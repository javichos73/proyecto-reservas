from datetime import datetime, timezone
from typing import Optional
import pytest

from app.services.reserva_service import (
    AccesoDenegadoError,
    HorarioInvalidoError,
    ReservaNoEncontradaError,
    SolapamientoError,
    cancelar_reserva,
    crear_reserva,
    listar_reservas,
)
from app.utils.time_utils import hay_solapamiento


class FakeReserva:
    def __init__(
        self,
        id: int,
        cancha: str,
        fecha: str,
        hora_inicio: str,
        hora_fin: str,
        usuario_id: int,
    ):
        self.id = id
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.usuario_id = usuario_id
        self.creado_en = datetime.now(timezone.utc)


class RepositorioFalsoReserva:
    def __init__(self):
        self.reservas: dict[int, FakeReserva] = {}
        self.next_id = 1

    def get_by_id(self, reserva_id: int, db=None) -> Optional[FakeReserva]:
        return self.reservas.get(reserva_id)

    def buscar_solapamientos(
        self, cancha: str, fecha: str, hora_inicio: str, hora_fin: str, db=None
    ) -> list[FakeReserva]:
        solapadas = []
        for r in self.reservas.values():
            if r.cancha == cancha and r.fecha == fecha:
                if hay_solapamiento(r.hora_inicio, r.hora_fin, hora_inicio, hora_fin):
                    solapadas.append(r)
        return solapadas

    def crear_reserva(
        self,
        cancha: str,
        fecha: str,
        hora_inicio: str,
        hora_fin: str,
        usuario_id: int,
        db=None,
    ) -> FakeReserva:
        reserva = FakeReserva(
            self.next_id, cancha, fecha, hora_inicio, hora_fin, usuario_id
        )
        self.reservas[self.next_id] = reserva
        self.next_id += 1
        return reserva

    def listar_por_usuario(
        self, usuario_id: int, skip: int = 0, limit: int = 20, db=None
    ) -> list[FakeReserva]:
        user_reservas = [
            r for r in self.reservas.values() if r.usuario_id == usuario_id
        ]
        user_reservas.sort(key=lambda r: (r.fecha, r.hora_inicio))
        return user_reservas[skip : skip + limit]

    def eliminar_reserva(self, reserva_id: int, db=None) -> bool:
        if reserva_id in self.reservas:
            del self.reservas[reserva_id]
            return True
        return False


# --- Tests de Creación ---


def test_crear_reserva_exitosa():
    repo = RepositorioFalsoReserva()
    reserva = crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-25",
        hora_inicio="18:00",
        hora_fin="19:00",
        usuario_id=1,
        repo=repo,
    )
    assert reserva.id == 1
    assert reserva.cancha == "Cancha Estrellas"
    assert reserva.hora_inicio == "18:00"
    assert reserva.hora_fin == "19:00"


def test_crear_reserva_horario_invertido_o_igual():
    repo = RepositorioFalsoReserva()
    with pytest.raises(HorarioInvalidoError, match="estrictamente posterior"):
        crear_reserva(
            cancha="Cancha Estrellas",
            fecha="2026-09-25",
            hora_inicio="19:00",
            hora_fin="18:00",
            usuario_id=1,
            repo=repo,
        )

    with pytest.raises(HorarioInvalidoError, match="estrictamente posterior"):
        crear_reserva(
            cancha="Cancha Estrellas",
            fecha="2026-09-25",
            hora_inicio="18:00",
            hora_fin="18:00",
            usuario_id=1,
            repo=repo,
        )


def test_crear_reserva_minutos_fraccionados():
    repo = RepositorioFalsoReserva()
    with pytest.raises(HorarioInvalidoError, match="minutos :00"):
        crear_reserva(
            cancha="Cancha Estrellas",
            fecha="2026-09-25",
            hora_inicio="18:30",
            hora_fin="19:30",
            usuario_id=1,
            repo=repo,
        )


def test_crear_reserva_solapamiento():
    repo = RepositorioFalsoReserva()
    # Crear primera reserva 18:00 a 20:00
    crear_reserva("Cancha Estrellas", "2026-09-25", "18:00", "20:00", 1, repo=repo)

    # Intento de solapamiento parcial por otro usuario 19:00 a 21:00
    with pytest.raises(SolapamientoError, match="conflicto de horario"):
        crear_reserva(
            "Cancha Estrellas", "2026-09-25", "19:00", "21:00", 2, repo=repo
        )

    # Intento de solapamiento contenido 18:00 a 19:00
    with pytest.raises(SolapamientoError, match="conflicto de horario"):
        crear_reserva(
            "Cancha Estrellas", "2026-09-25", "18:00", "19:00", 3, repo=repo
        )


def test_crear_reserva_contigua_permitida():
    repo = RepositorioFalsoReserva()
    # Reserva 1: 18:00 - 19:00
    r1 = crear_reserva(
        "Cancha Estrellas", "2026-09-25", "18:00", "19:00", 1, repo=repo
    )
    # Reserva 2 contigua: 19:00 - 20:00 (permitida)
    r2 = crear_reserva(
        "Cancha Estrellas", "2026-09-25", "19:00", "20:00", 2, repo=repo
    )
    # Reserva 3 contigua anterior: 17:00 - 18:00 (permitida)
    r3 = crear_reserva(
        "Cancha Estrellas", "2026-09-25", "17:00", "18:00", 3, repo=repo
    )

    assert r1.id == 1
    assert r2.id == 2
    assert r3.id == 3


def test_crear_reserva_otra_cancha_u_otra_fecha():
    repo = RepositorioFalsoReserva()
    crear_reserva("Cancha Estrellas", "2026-09-25", "18:00", "20:00", 1, repo=repo)

    # Misma hora pero otra fecha
    r_otra_fecha = crear_reserva(
        "Cancha Estrellas", "2026-09-26", "18:00", "20:00", 2, repo=repo
    )
    # Misma hora y fecha pero otra cancha
    r_otra_cancha = crear_reserva(
        "Cancha Galaxia", "2026-09-25", "18:00", "20:00", 3, repo=repo
    )

    assert r_otra_fecha.id == 2
    assert r_otra_cancha.id == 3


# --- Tests de Listado ---


def test_listar_reservas_usuario_aislamiento():
    repo = RepositorioFalsoReserva()
    crear_reserva("Cancha Estrellas", "2026-09-25", "10:00", "11:00", 1, repo=repo)
    crear_reserva("Cancha Estrellas", "2026-09-25", "12:00", "13:00", 1, repo=repo)
    crear_reserva("Cancha Estrellas", "2026-09-25", "14:00", "15:00", 2, repo=repo)

    reservas_user1 = listar_reservas(usuario_id=1, repo=repo)
    assert len(reservas_user1) == 2
    assert all(r.usuario_id == 1 for r in reservas_user1)

    reservas_user2 = listar_reservas(usuario_id=2, repo=repo)
    assert len(reservas_user2) == 1
    assert reservas_user2[0].usuario_id == 2


def test_listar_reservas_paginacion():
    repo = RepositorioFalsoReserva()
    crear_reserva("Cancha Estrellas", "2026-09-25", "10:00", "11:00", 1, repo=repo)
    crear_reserva("Cancha Estrellas", "2026-09-25", "12:00", "13:00", 1, repo=repo)
    crear_reserva("Cancha Estrellas", "2026-09-25", "14:00", "15:00", 1, repo=repo)

    page1 = listar_reservas(usuario_id=1, skip=0, limit=2, repo=repo)
    assert len(page1) == 2
    assert page1[0].hora_inicio == "10:00"

    page2 = listar_reservas(usuario_id=1, skip=2, limit=2, repo=repo)
    assert len(page2) == 1
    assert page2[0].hora_inicio == "14:00"


# --- Tests de Cancelación ---


def test_cancelar_reserva_propia_exitosa():
    repo = RepositorioFalsoReserva()
    r = crear_reserva(
        "Cancha Estrellas", "2026-09-25", "18:00", "19:00", 1, repo=repo
    )

    resultado = cancelar_reserva(reserva_id=r.id, usuario_id=1, repo=repo)
    assert resultado is True
    assert repo.get_by_id(r.id) is None


def test_cancelar_reserva_ajena_acceso_denegado():
    repo = RepositorioFalsoReserva()
    r = crear_reserva(
        "Cancha Estrellas", "2026-09-25", "18:00", "19:00", 1, repo=repo
    )

    with pytest.raises(AccesoDenegadoError, match="No tiene permiso"):
        cancelar_reserva(reserva_id=r.id, usuario_id=2, repo=repo)


def test_cancelar_reserva_inexistente():
    repo = RepositorioFalsoReserva()
    with pytest.raises(ReservaNoEncontradaError, match="no fue encontrada"):
        cancelar_reserva(reserva_id=999, usuario_id=1, repo=repo)
