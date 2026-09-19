from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReservaCreate(BaseModel):
    cancha: str = Field(default="Cancha Estrellas", min_length=1, max_length=100)
    fecha: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Fecha en formato YYYY-MM-DD",
        examples=["2026-09-25"],
    )
    hora_inicio: str = Field(
        ...,
        pattern=r"^([01]\d|2[0-3]):00$",
        description="Hora de inicio en formato HH:00 (horas en punto)",
        examples=["18:00"],
    )
    hora_fin: str = Field(
        ...,
        pattern=r"^([01]\d|2[0-3]):00$",
        description="Hora de fin en formato HH:00 (horas en punto)",
        examples=["19:00"],
    )


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cancha: str
    fecha: str
    hora_inicio: str
    hora_fin: str
    usuario_id: int
    creado_en: datetime
