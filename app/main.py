from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.logging_config import setup_logging
from app.models import Reserva, Usuario  # noqa: F401
from app.routers import auth, reservas

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Asegurar creación de tablas al inicio si no existen
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para Sistema de Reservas de Cancha Sintética 'Estrellas'",
    lifespan=lifespan,
)

# Garantizar creación de tablas antes de incluir routers
Base.metadata.create_all(bind=engine)

# Configurar CORSMiddleware permitiendo todos los orígenes (*), métodos y headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reservas.router)

# Montaje de FastMCP en /mcp si expone una app ASGI
try:
    from app.mcp.server import mcp, mcp_app

    if mcp_app is not None:
        app.mount("/mcp", mcp_app)
    elif hasattr(mcp, "sse_app"):
        app.mount("/mcp", mcp.sse_app(mount_path="/mcp"))
except Exception:
    pass


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status}

