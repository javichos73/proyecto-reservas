from typing import Any
from app.database import SessionLocal
from app.services.reserva_service import (
    AccesoDenegadoError,
    HorarioInvalidoError,
    ReservaNoEncontradaError,
    SolapamientoError,
    cancelar_reserva as service_cancelar_reserva,
    crear_reserva as service_crear_reserva,
    listar_reservas as service_listar_reservas,
)


def mcp_crear_reserva(
    cancha: str = "Cancha Estrellas",
    fecha: str = "",
    hora_inicio: str = "",
    hora_fin: str = "",
    usuario_id: int = 1,
) -> dict[str, Any]:
    """
    Herramienta MCP para crear una reserva en la cancha sintética.
    Reutiliza directamente reserva_service.
    """
    db = SessionLocal()
    try:
        reserva = service_crear_reserva(
            cancha=cancha,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            usuario_id=usuario_id,
            db=db,
        )
        return {
            "id": reserva.id,
            "cancha": reserva.cancha,
            "fecha": reserva.fecha,
            "hora_inicio": reserva.hora_inicio,
            "hora_fin": reserva.hora_fin,
            "usuario_id": reserva.usuario_id,
        }
    except (HorarioInvalidoError, SolapamientoError) as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error inesperado al crear la reserva: {str(e)}"}
    finally:
        db.close()


def mcp_listar_reservas(
    usuario_id: int = 1,
    skip: int = 0,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Herramienta MCP para listar las reservas del usuario autenticado.
    """
    db = SessionLocal()
    try:
        reservas = service_listar_reservas(
            usuario_id=usuario_id,
            skip=skip,
            limit=limit,
            db=db,
        )
        return [
            {
                "id": r.id,
                "cancha": r.cancha,
                "fecha": r.fecha,
                "hora_inicio": r.hora_inicio,
                "hora_fin": r.hora_fin,
            }
            for r in reservas
        ]
    finally:
        db.close()


def mcp_cancelar_reserva(
    reserva_id: int,
    usuario_id: int = 1,
    confirmar: bool = True,
) -> dict[str, Any]:
    """
    Herramienta MCP para cancelar una reserva existente con confirmación explícita.
    """
    if not confirmar:
        return {
            "error": "Se requiere confirmación explícita para cancelar la reserva."
        }

    db = SessionLocal()
    try:
        service_cancelar_reserva(
            reserva_id=reserva_id,
            usuario_id=usuario_id,
            db=db,
        )
        return {"mensaje": f"Reserva {reserva_id} cancelada exitosamente"}
    except (AccesoDenegadoError, ReservaNoEncontradaError) as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error inesperado al cancelar la reserva: {str(e)}"}
    finally:
        db.close()
