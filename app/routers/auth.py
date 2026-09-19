from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import TokenResponse, UsuarioCreate, UsuarioResponse
from app.services.auth_service import (
    CredencialesInvalidasError,
    EmailDuplicadoError,
    autenticar_usuario,
    crear_access_token,
    registrar_usuario,
)

router = APIRouter(prefix="/usuarios", tags=["Autenticación"])


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de nuevo usuario",
)
def registrar(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
):
    try:
        usuario = registrar_usuario(
            email=usuario_in.email,
            password=usuario_in.password,
            db=db,
        )
        return usuario
    except EmailDuplicadoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtención de token JWT mediante OAuth2 Password Flow",
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        usuario = autenticar_usuario(
            email=form_data.username,
            password=form_data.password,
            db=db,
        )
        access_token = crear_access_token(
            data={"sub": str(usuario.id), "email": usuario.email}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except CredencialesInvalidasError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
