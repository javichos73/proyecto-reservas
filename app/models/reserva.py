from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reserva(Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cancha: Mapped[str] = mapped_column(
        String(100), default="Cancha Estrellas", index=True, nullable=False
    )
    fecha: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    hora_inicio: Mapped[str] = mapped_column(String(5), nullable=False)
    hora_fin: Mapped[str] = mapped_column(String(5), nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), index=True, nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relación inversa con Usuario
    usuario = relationship("Usuario", back_populates="reservas")
