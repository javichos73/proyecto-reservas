from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.reserva import Reserva


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relación con reservas
    reservas: Mapped[list["Reserva"]] = relationship(
        "Reserva", back_populates="usuario", cascade="all, delete-orphan"
    )
