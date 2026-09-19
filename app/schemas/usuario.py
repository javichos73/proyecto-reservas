from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Contraseña mínimo 6 caracteres")


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    creado_en: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None
