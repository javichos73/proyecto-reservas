from app.mcp.tools.reserva_tools import (
    mcp_cancelar_reserva,
    mcp_crear_reserva,
    mcp_listar_reservas,
)
from app.models.usuario import Usuario
from app.services.auth_service import hash_password


def create_db_user(db_session, email="mcp_user@test.com") -> int:
    user = Usuario(email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user.id


def test_mcp_crear_reserva_exitosa(db_session, monkeypatch):
    monkeypatch.setattr(
        "app.mcp.tools.reserva_tools.SessionLocal", lambda: db_session
    )

    user_id = create_db_user(db_session, "mcp1@test.com")

    res = mcp_crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-30",
        hora_inicio="18:00",
        hora_fin="19:00",
        usuario_id=user_id,
    )
    assert "id" in res
    assert res["hora_inicio"] == "18:00"
    assert "error" not in res


def test_mcp_crear_reserva_solapamiento_retorna_error(db_session, monkeypatch):
    monkeypatch.setattr(
        "app.mcp.tools.reserva_tools.SessionLocal", lambda: db_session
    )

    user1_id = create_db_user(db_session, "mcp_solap1@test.com")
    user2_id = create_db_user(db_session, "mcp_solap2@test.com")

    # Primera reserva 18:00 a 20:00
    r1 = mcp_crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-30",
        hora_inicio="18:00",
        hora_fin="20:00",
        usuario_id=user1_id,
    )
    assert "error" not in r1

    # Segunda reserva solapada 19:00 a 21:00
    r2 = mcp_crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-30",
        hora_inicio="19:00",
        hora_fin="21:00",
        usuario_id=user2_id,
    )
    assert "error" in r2
    assert "conflicto de horario" in r2["error"]


def test_mcp_crear_reserva_minutos_fraccionados_error(db_session, monkeypatch):
    monkeypatch.setattr(
        "app.mcp.tools.reserva_tools.SessionLocal", lambda: db_session
    )
    user_id = create_db_user(db_session, "mcp_frac@test.com")

    res = mcp_crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-30",
        hora_inicio="18:30",
        hora_fin="19:30",
        usuario_id=user_id,
    )
    assert "error" in res
    assert "minutos :00" in res["error"]


def test_mcp_listar_reservas(db_session, monkeypatch):
    monkeypatch.setattr(
        "app.mcp.tools.reserva_tools.SessionLocal", lambda: db_session
    )
    user_id = create_db_user(db_session, "mcp_list@test.com")

    mcp_crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-30",
        hora_inicio="10:00",
        hora_fin="11:00",
        usuario_id=user_id,
    )
    mcp_crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-30",
        hora_inicio="12:00",
        hora_fin="13:00",
        usuario_id=user_id,
    )

    lista = mcp_listar_reservas(usuario_id=user_id)
    assert len(lista) == 2


def test_mcp_cancelar_reserva_flujo(db_session, monkeypatch):
    monkeypatch.setattr(
        "app.mcp.tools.reserva_tools.SessionLocal", lambda: db_session
    )
    user_owner_id = create_db_user(db_session, "mcp_owner@test.com")
    user_other_id = create_db_user(db_session, "mcp_other@test.com")

    res = mcp_crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-30",
        hora_inicio="15:00",
        hora_fin="16:00",
        usuario_id=user_owner_id,
    )
    reserva_id = res["id"]

    # Sin confirmación
    res_no_conf = mcp_cancelar_reserva(
        reserva_id=reserva_id, usuario_id=user_owner_id, confirmar=False
    )
    assert "error" in res_no_conf

    # Cancelación por otro usuario (error)
    res_other = mcp_cancelar_reserva(
        reserva_id=reserva_id, usuario_id=user_other_id, confirmar=True
    )
    assert "error" in res_other
    assert "No tiene permiso" in res_other["error"]

    # Cancelación válida
    res_ok = mcp_cancelar_reserva(
        reserva_id=reserva_id, usuario_id=user_owner_id, confirmar=True
    )
    assert "mensaje" in res_ok
    assert "cancelada exitosamente" in res_ok["mensaje"]
