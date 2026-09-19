from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.reserva import ReservaCreate, ReservaResponse
from app.services.reserva_service import (
    AccesoDenegadoError,
    HorarioInvalidoError,
    ReservaNoEncontradaError,
    SolapamientoError,
    cancelar_reserva,
    crear_reserva,
    listar_reservas,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post(
    "/",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva reserva",
)
def crear(
    reserva_in: ReservaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        reserva = crear_reserva(
            cancha=reserva_in.cancha,
            fecha=reserva_in.fecha,
            hora_inicio=reserva_in.hora_inicio,
            hora_fin=reserva_in.hora_fin,
            usuario_id=current_user.id,
            db=db,
        )
        return reserva
    except (HorarioInvalidoError, SolapamientoError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/",
    response_model=list[ReservaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar reservas privadas del usuario autenticado",
)
def listar(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return listar_reservas(
        usuario_id=current_user.id,
        skip=skip,
        limit=limit,
        db=db,
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar una reserva propia",
)
def cancelar(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        cancelar_reserva(
            reserva_id=id,
            usuario_id=current_user.id,
            db=db,
        )
        return None
    except AccesoDenegadoError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ReservaNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
