from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import jwt
from passlib.context import CryptContext

from app.config import settings
from app.repositories.usuario_repository import usuario_repository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class EmailDuplicadoError(Exception):
    pass


class CredencialesInvalidasError(Exception):
    pass


class TokenInvalidoError(Exception):
    pass


def hash_password(password: str) -> str:
    """Genera un hash seguro de la contraseña usando bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)


def crear_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Crea y firma un token JWT usando el algoritmo HS256."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verificar_token(token: str) -> dict[str, Any]:
    """Decodifica y valida un token JWT. Lanza TokenInvalidoError si es inválido o expiró."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError as e:
        raise TokenInvalidoError(f"Token no válido o expirado: {str(e)}") from e


def registrar_usuario(
    email: str,
    password: str,
    db: Any = None,
    repo: Any = usuario_repository,
) -> Any:
    """
    Registra un nuevo usuario en el sistema.
    Lanza EmailDuplicadoError si el email ya existe.
    """
    existente = repo.get_by_email(email, db)
    if existente:
        raise EmailDuplicadoError(f"El email '{email}' ya se encuentra registrado.")

    password_hash = hash_password(password)
    return repo.create(email, password_hash, db)


def autenticar_usuario(
    email: str,
    password: str,
    db: Any = None,
    repo: Any = usuario_repository,
) -> Any:
    """
    Autentica un usuario con email y contraseña.
    Lanza CredencialesInvalidasError si la autenticación falla.
    """
    usuario = repo.get_by_email(email, db)
    if not usuario:
        raise CredencialesInvalidasError("Credenciales de acceso inválidas.")

    if not verify_password(password, usuario.password_hash):
        raise CredencialesInvalidasError("Credenciales de acceso inválidas.")

    return usuario
