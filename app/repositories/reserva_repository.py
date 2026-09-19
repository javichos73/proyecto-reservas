from typing import Optional
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.reserva import Reserva


class ReservaRepository:
    def get_by_id(self, reserva_id: int, db: Session) -> Optional[Reserva]:
        return db.scalar(select(Reserva).where(Reserva.id == reserva_id))

    def buscar_solapamientos(
        self, cancha: str, fecha: str, hora_inicio: str, hora_fin: str, db: Session
    ) -> list[Reserva]:
        """
        Busca reservas que se solapen en fecha y cancha:
        reserva.hora_inicio < hora_fin_solicitada AND reserva.hora_fin > hora_inicio_solicitada
        """
        stmt = select(Reserva).where(
            and_(
                Reserva.cancha == cancha,
                Reserva.fecha == fecha,
                Reserva.hora_inicio < hora_fin,
                Reserva.hora_fin > hora_inicio,
            )
        )
        return list(db.scalars(stmt).all())

    def crear_reserva(
        self,
        cancha: str,
        fecha: str,
        hora_inicio: str,
        hora_fin: str,
        usuario_id: int,
        db: Session,
    ) -> Reserva:
        reserva = Reserva(
            cancha=cancha,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            usuario_id=usuario_id,
        )
        db.add(reserva)
        db.commit()
        db.refresh(reserva)
        return reserva

    def listar_por_usuario(
        self, usuario_id: int, skip: int, limit: int, db: Session
    ) -> list[Reserva]:
        stmt = (
            select(Reserva)
            .where(Reserva.usuario_id == usuario_id)
            .offset(skip)
            .limit(limit)
            .order_by(Reserva.fecha.asc(), Reserva.hora_inicio.asc())
        )
        return list(db.scalars(stmt).all())

    def eliminar_reserva(self, reserva_id: int, db: Session) -> bool:
        reserva = self.get_by_id(reserva_id, db)
        if not reserva:
            return False
        db.delete(reserva)
        db.commit()
        return True


reserva_repository = ReservaRepository()
