from typing import Any
from mcp.server.fastmcp import FastMCP
from app.mcp.tools.reserva_tools import (
    mcp_cancelar_reserva,
    mcp_crear_reserva,
    mcp_listar_reservas,
)

# Se inicializa solo con el nombre posicional
mcp = FastMCP("reservas-cancha-sintetica")
mcp_server = mcp  # Alias de compatibilidad


@mcp.tool(
    name="crear_reserva",
    description="Crea una nueva reserva en la cancha sintética para el usuario autenticado, validando disponibilidad y reglas de negocio.",
)
def tool_crear_reserva(
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    cancha: str = "Cancha Estrellas",
    usuario_id: int = 1,
) -> dict[str, Any]:
    return mcp_crear_reserva(
        cancha=cancha,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        usuario_id=usuario_id,
    )


@mcp.tool(
    name="listar_reservas",
    description="Obtiene la lista paginada de reservas pertenecientes al usuario autenticado.",
)
def tool_listar_reservas(
    usuario_id: int = 1,
    skip: int = 0,
    limit: int = 20,
) -> list[dict[str, Any]]:
    return mcp_listar_reservas(usuario_id=usuario_id, skip=skip, limit=limit)


@mcp.tool(
    name="cancelar_reserva",
    description="Cancela y elimina una reserva existente verificando que pertenezca al usuario autenticado y con confirmación explícita.",
)
def tool_cancelar_reserva(
    reserva_id: int,
    usuario_id: int = 1,
    confirmar: bool = True,
) -> dict[str, Any]:
    return mcp_cancelar_reserva(
        reserva_id=reserva_id, usuario_id=usuario_id, confirmar=confirmar
    )

if __name__ == "__main__":
    mcp.run()