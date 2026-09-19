import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.database import Base
from app.repositories.reserva_repository import reserva_repository
from app.repositories.usuario_repository import usuario_repository


@pytest.fixture
def real_sqlite_session():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_real_sqlite_usuario_y_reserva_repositorios(real_sqlite_session):
    # 1. Crear usuario en SQLite real
    user = usuario_repository.create(
        email="real_db@test.com", password_hash="hash123", db=real_sqlite_session
    )
    assert user.id is not None

    user_found = usuario_repository.get_by_email(
        "real_db@test.com", db=real_sqlite_session
    )
    assert user_found is not None
    assert user_found.id == user.id

    # 2. Crear reserva en SQLite real
    reserva = reserva_repository.crear_reserva(
        cancha="Cancha Estrellas",
        fecha="2026-09-28",
        hora_inicio="18:00",
        hora_fin="19:00",
        usuario_id=user.id,
        db=real_sqlite_session,
    )
    assert reserva.id is not None

    # 3. Buscar solapamientos
    solapadas = reserva_repository.buscar_solapamientos(
        cancha="Cancha Estrellas",
        fecha="2026-09-28",
        hora_inicio="18:00",
        hora_fin="20:00",
        db=real_sqlite_session,
    )
    assert len(solapadas) == 1

    # 4. Listar por usuario
    lista = reserva_repository.listar_por_usuario(
        usuario_id=user.id, skip=0, limit=10, db=real_sqlite_session
    )
    assert len(lista) == 1

    # 5. Eliminar reserva
    eliminado = reserva_repository.eliminar_reserva(
        reserva_id=reserva.id, db=real_sqlite_session
    )
    assert eliminado is True
    assert (
        reserva_repository.get_by_id(reserva.id, db=real_sqlite_session) is None
    )
