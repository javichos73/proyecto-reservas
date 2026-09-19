from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.repositories.usuario_repository import usuario_repository
from app.services.auth_service import TokenInvalidoError, verificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    """
    Extrae y valida el token JWT del header Authorization Bearer.
    Devuelve la entidad Usuario correspondiente al usuario_id del token.
    Lanza HTTP 401 si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de acceso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verificar_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (TokenInvalidoError, ValueError):
        raise credentials_exception

    usuario = usuario_repository.get_by_id(user_id, db)
    if usuario is None:
        raise credentials_exception
    return usuario
