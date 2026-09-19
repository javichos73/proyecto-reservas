from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


class UsuarioRepository:
    def get_by_id(self, user_id: int, db: Session) -> Optional[Usuario]:
        return db.scalar(select(Usuario).where(Usuario.id == user_id))

    def get_by_email(self, email: str, db: Session) -> Optional[Usuario]:
        return db.scalar(select(Usuario).where(Usuario.email == email))

    def create(self, email: str, password_hash: str, db: Session) -> Usuario:
        usuario = Usuario(email=email, password_hash=password_hash)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario


usuario_repository = UsuarioRepository()
