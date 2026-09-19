from fastapi import FastAPI
from app.config import settings
from app.logging_config import setup_logging
from app.routers import auth, reservas

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para Sistema de Reservas de Cancha Sintética 'Estrellas'",
)

app.include_router(auth.router)
app.include_router(reservas.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
