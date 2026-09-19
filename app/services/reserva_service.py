from typing import Any
from app.repositories.reserva_repository import reserva_repository
from app.utils.time_utils import validar_reglas_horario


class HorarioInvalidoError(Exception):
    pass


class SolapamientoError(Exception):
    pass


class ReservaNoEncontradaError(Exception):
    pass


class AccesoDenegadoError(Exception):
    pass


def crear_reserva(
    cancha: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    usuario_id: int,
    db: Any = None,
    repo: Any = reserva_repository,
) -> Any:
    """
    Crea una nueva reserva validando reglas de tiempo y solapamiento.
    Inyección de dependencias (DIP) mediante repo=reserva_repository por defecto.
    """
    try:
        validar_reglas_horario(hora_inicio, hora_fin)
    except ValueError as e:
        raise HorarioInvalidoError(str(e)) from e

    solapadas = repo.buscar_solapamientos(cancha, fecha, hora_inicio, hora_fin, db)
    if solapadas:
        raise SolapamientoError(
            f"Existe un conflicto de horario con otra reserva en la cancha '{cancha}' para la fecha {fecha}."
        )

    return repo.crear_reserva(cancha, fecha, hora_inicio, hora_fin, usuario_id, db)


def listar_reservas(
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Any = None,
    repo: Any = reserva_repository,
) -> list[Any]:
    """
    Lista las reservas privadas del usuario autenticado con paginación.
    """
    return repo.listar_por_usuario(usuario_id, skip=skip, limit=limit, db=db)


def cancelar_reserva(
    reserva_id: int,
    usuario_id: int,
    db: Any = None,
    repo: Any = reserva_repository,
) -> bool:
    """
    Cancela una reserva propia del usuario autenticado.
    Lanza ReservaNoEncontradaError si no existe o AccesoDenegadoError si no es el dueño.
    """
    reserva = repo.get_by_id(reserva_id, db)
    if not reserva:
        raise ReservaNoEncontradaError(
            f"La reserva con id {reserva_id} no fue encontrada."
        )

    if reserva.usuario_id != usuario_id:
        raise AccesoDenegadoError(
            "No tiene permiso para cancelar una reserva que no le pertenece."
        )

    return repo.eliminar_reserva(reserva_id, db)
