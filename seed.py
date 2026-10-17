"""Script de inicialización y datos semilla (seed) para la base de datos.
Idempotente: Puede ejecutarse múltiples veces sin duplicar datos ni fallar.
"""

import sys
from app.database import Base, SessionLocal, engine
from app.models import Reserva, Usuario  # noqa: F401 - Asegura registro de modelos
from app.repositories.reserva_repository import reserva_repository
from app.repositories.usuario_repository import usuario_repository
from app.services.auth_service import EmailDuplicadoError, registrar_usuario
from app.services.reserva_service import SolapamientoError, crear_reserva

DEMO_EMAIL = "demo@estrellas.ec"
DEMO_PASSWORD = "estrellas123"

# 20 reservas reales distribuidas entre las 4 canchas del complejo
RESERVAS_SEMILLA = [
    # Cancha Estrellas 1 (Fútbol 7) - 5 reservas
    {
        "cancha": "Cancha Estrellas 1 (Fútbol 7)",
        "fecha": "2026-10-20",
        "hora_inicio": "16:00",
        "hora_fin": "17:00",
    },
    {
        "cancha": "Cancha Estrellas 1 (Fútbol 7)",
        "fecha": "2026-10-22",
        "hora_inicio": "18:00",
        "hora_fin": "19:00",
    },
    {
        "cancha": "Cancha Estrellas 1 (Fútbol 7)",
        "fecha": "2026-10-25",
        "hora_inicio": "19:00",
        "hora_fin": "21:00",
    },
    {
        "cancha": "Cancha Estrellas 1 (Fútbol 7)",
        "fecha": "2026-11-03",
        "hora_inicio": "17:00",
        "hora_fin": "18:00",
    },
    {
        "cancha": "Cancha Estrellas 1 (Fútbol 7)",
        "fecha": "2026-11-10",
        "hora_inicio": "20:00",
        "hora_fin": "22:00",
    },
    # Cancha Estrellas 2 (Fútbol 5) - 5 reservas
    {
        "cancha": "Cancha Estrellas 2 (Fútbol 5)",
        "fecha": "2026-10-21",
        "hora_inicio": "17:00",
        "hora_fin": "18:00",
    },
    {
        "cancha": "Cancha Estrellas 2 (Fútbol 5)",
        "fecha": "2026-10-24",
        "hora_inicio": "19:00",
        "hora_fin": "20:00",
    },
    {
        "cancha": "Cancha Estrellas 2 (Fútbol 5)",
        "fecha": "2026-10-28",
        "hora_inicio": "20:00",
        "hora_fin": "21:00",
    },
    {
        "cancha": "Cancha Estrellas 2 (Fútbol 5)",
        "fecha": "2026-11-05",
        "hora_inicio": "18:00",
        "hora_fin": "20:00",
    },
    {
        "cancha": "Cancha Estrellas 2 (Fútbol 5)",
        "fecha": "2026-11-12",
        "hora_inicio": "16:00",
        "hora_fin": "17:00",
    },
    # Cancha Estrellas 3 (Fútbol 8 Techada) - 5 reservas
    {
        "cancha": "Cancha Estrellas 3 (Fútbol 8 Techada)",
        "fecha": "2026-10-23",
        "hora_inicio": "18:00",
        "hora_fin": "19:00",
    },
    {
        "cancha": "Cancha Estrellas 3 (Fútbol 8 Techada)",
        "fecha": "2026-10-26",
        "hora_inicio": "19:00",
        "hora_fin": "21:00",
    },
    {
        "cancha": "Cancha Estrellas 3 (Fútbol 8 Techada)",
        "fecha": "2026-10-30",
        "hora_inicio": "21:00",
        "hora_fin": "22:00",
    },
    {
        "cancha": "Cancha Estrellas 3 (Fútbol 8 Techada)",
        "fecha": "2026-11-07",
        "hora_inicio": "17:00",
        "hora_fin": "19:00",
    },
    {
        "cancha": "Cancha Estrellas 3 (Fútbol 8 Techada)",
        "fecha": "2026-11-15",
        "hora_inicio": "19:00",
        "hora_fin": "20:00",
    },
    # Cancha Estrellas VIP (Fútbol 11) - 5 reservas
    {
        "cancha": "Cancha Estrellas VIP (Fútbol 11)",
        "fecha": "2026-10-27",
        "hora_inicio": "18:00",
        "hora_fin": "20:00",
    },
    {
        "cancha": "Cancha Estrellas VIP (Fútbol 11)",
        "fecha": "2026-10-31",
        "hora_inicio": "20:00",
        "hora_fin": "22:00",
    },
    {
        "cancha": "Cancha Estrellas VIP (Fútbol 11)",
        "fecha": "2026-11-08",
        "hora_inicio": "19:00",
        "hora_fin": "21:00",
    },
    {
        "cancha": "Cancha Estrellas VIP (Fútbol 11)",
        "fecha": "2026-11-18",
        "hora_inicio": "17:00",
        "hora_fin": "19:00",
    },
    {
        "cancha": "Cancha Estrellas VIP (Fútbol 11)",
        "fecha": "2026-11-22",
        "hora_inicio": "20:00",
        "hora_fin": "22:00",
    },
]


def seed_database() -> None:
    """Inicializa tablas y carga datos de demostración de manera idempotente."""
    print("--- [SEED] Inicializando base de datos ---")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas verificadas/creadas correctamente en SQLite.")

    with SessionLocal() as db:
        # 1. Obtener o crear usuario demo
        usuario = usuario_repository.get_by_email(DEMO_EMAIL, db)
        if not usuario:
            try:
                usuario = registrar_usuario(
                    email=DEMO_EMAIL,
                    password=DEMO_PASSWORD,
                    db=db,
                )
                print(f"✓ Usuario de demostración creado: {DEMO_EMAIL} (ID: {usuario.id})")
            except EmailDuplicadoError:
                usuario = usuario_repository.get_by_email(DEMO_EMAIL, db)
        else:
            print(f"✓ Usuario de demostración existente: {DEMO_EMAIL} (ID: {usuario.id})")

        # 2. Verificar reservas existentes
        reservas_existentes = reserva_repository.listar_por_usuario(
            usuario_id=usuario.id, skip=0, limit=100, db=db
        )
        total_existentes = len(reservas_existentes)
        print(f"✓ Reservas actuales registradas para {DEMO_EMAIL}: {total_existentes}")

        # 3. Si tiene menos de 20 reservas, crear las 20 reservas reales
        if total_existentes < 20:
            print(f"Insertando reservas semilla (meta: 20 reservas)...")
            creadas = 0
            for item in RESERVAS_SEMILLA:
                # Comprobar si ya existe solapamiento en la base de datos
                solapadas = reserva_repository.buscar_solapamientos(
                    cancha=item["cancha"],
                    fecha=item["fecha"],
                    hora_inicio=item["hora_inicio"],
                    hora_fin=item["hora_fin"],
                    db=db,
                )
                if solapadas:
                    continue

                try:
                    crear_reserva(
                        cancha=item["cancha"],
                        fecha=item["fecha"],
                        hora_inicio=item["hora_inicio"],
                        hora_fin=item["hora_fin"],
                        usuario_id=usuario.id,
                        db=db,
                    )
                    creadas += 1
                except SolapamientoError:
                    continue

            reservas_finales = reserva_repository.listar_por_usuario(
                usuario_id=usuario.id, skip=0, limit=100, db=db
            )
            print(
                f"✓ Proceso completado: se agregaron {creadas} reservas nuevas. "
                f"Total reservas del usuario: {len(reservas_finales)}."
            )
        else:
            print(
                f"✓ El usuario {DEMO_EMAIL} ya posee {total_existentes} reservas. "
                f"No se agregaron reservas duplicadas (idempotencia garantizada)."
            )


if __name__ == "__main__":
    seed_database()
