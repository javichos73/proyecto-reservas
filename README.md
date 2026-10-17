# Sistema de Reservas - Cancha Sintética "Estrellas"

Backend en FastAPI para la gestión de reservas de canchas de fútbol sintéticas, diseñado con arquitectura en capas (Clean Architecture / SOLID) y preparado para ser consumido por la aplicación móvil Flutter.

---

## 🚀 Inicio Rápido con Docker

La forma más sencilla de levantar el backend completo con la base de datos y los datos semilla listos para usar:

```bash
docker compose up --build
```
*(o con `docker-compose up --build` según tu versión de Docker)*

El contenedor ejecutará automáticamente `python seed.py` para crear las tablas y las 20 reservas semilla, y luego iniciará Uvicorn en el puerto `8000`.

- **API Base:** `http://localhost:8000`
- **Documentación Interactiva (Swagger):** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`
- **Servidor FastMCP (SSE):** `http://localhost:8000/mcp`

---

## 💻 Ejecución Local

Si prefieres ejecutar el backend directamente en tu entorno local:

### 1. Activar el entorno virtual e instalar dependencias

```bash
# Crear y activar venv si no existe
python3.11 -m venv .venv
source .venv/bin/activate

# Instalar dependencias del proyecto
pip install -e .
```

### 2. Configurar variables de entorno (opcional)

Puedes copiar la plantilla `.env.example` a `.env`:

```bash
cp .env.example .env
```

*(Si no se define `.env`, la aplicación utilizará los valores por defecto configurados en `app/config.py`)*.

### 3. Ejecutar el script semilla e iniciar el servidor

```bash
python seed.py && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 👤 Credenciales del Usuario Semilla (Demo)

El script `seed.py` inicializa la base de datos SQLite y precarga de forma idempotente un usuario de pruebas con **20 reservas reales**:

- **Email:** `demo@estrellas.ec`
- **Contraseña:** `estrellas123`
- **Reservas precargadas:** 20 reservas reales distribuidas equitativamente entre las 4 canchas del complejo:
  * `Cancha Estrellas 1 (Fútbol 7)` (5 reservas)
  * `Cancha Estrellas 2 (Fútbol 5)` (5 reservas)
  * `Cancha Estrellas 3 (Fútbol 8 Techada)` (5 reservas)
  * `Cancha Estrellas VIP (Fútbol 11)` (5 reservas)
- **Fechas:** Variadas entre octubre y noviembre de 2026 en formato `YYYY-MM-DD`.
- **Horarios:** Bloques de 1 y 2 horas en punto (`:00`, ej. `16:00` a `17:00`, `18:00` a `20:00`, etc.), sin solapamientos.

---

## 📡 Endpoints Principales

| Método | Endpoint | Descripción | Requiere Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/health` | Chequeo de salud del servicio y conexión a BD (`{"status": "ok", "db": "ok"}`) | No |
| `POST` | `/usuarios/` | Registro de nuevo usuario (`email`, `password`) | No |
| `POST` | `/usuarios/token` | Login OAuth2 (Password Flow) para obtener JWT | No |
| `GET` | `/reservas/` | Lista las reservas del usuario autenticado (paginadas) | Sí |
| `POST` | `/reservas/` | Crea una nueva reserva (valida solapamiento y reglas de negocio) | Sí |
| `DELETE` | `/reservas/{id}` | Cancela y elimina una reserva propia del usuario | Sí |
| `GET` | `/mcp/sse` | Transporte SSE del servidor FastMCP | Depende de config |

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite completa de pruebas unitarias, de integración y MCP con reporte de cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```
