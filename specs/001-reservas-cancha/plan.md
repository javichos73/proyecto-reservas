# Implementation Plan: Sistema de Reservas para Cancha Sintética "Estrellas"

**Branch**: `001-reservas-cancha` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-reservas-cancha/spec.md`

## Summary

Implementar un sistema modular en capas para la gestión y reserva de turnos en la cancha sintética "Estrellas". El sistema incluye autenticación segura mediante OAuth2 Password Flow con JWT (HS256) y contraseñas cifradas con `passlib[bcrypt]` (`bcrypt<4.1`), persistencia relacional con SQLAlchemy 2.0 sobre SQLite, validación estricta de reglas de negocio (solapamiento temporal, intervalos de horas en punto y duración mínima) aislada en la capa de servicios con inversión de dependencias (DIP), exposición de endpoints REST con códigos de estado semánticos e integración nativa de herramientas FastMCP.

---

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, uvicorn[standard], SQLAlchemy>=2.0, pyjwt, passlib[bcrypt], bcrypt<4.1, pydantic-settings, email-validator, python-multipart, mcp[cli]<2, pytest, pytest-cov, httpx

**Storage**: SQLite en desarrollo y pruebas vía SQLAlchemy 2.0 ORM

**Testing**: pytest, pytest-cov, httpx (FastAPI TestClient), Repositorios Falsos en memoria (sin `unittest.mock` en servicios)

**Target Platform**: Linux Server / Multiplataforma

**Project Type**: Web Service (REST API) + Model Context Protocol (FastMCP)

**Performance Goals**: Latencia p95 < 50ms en operaciones de consulta y validación de reservas; ejecución de tools MCP < 100ms

**Constraints**:
- Cumplimiento innegociable de la Constitución v1.0.0.
- Cobertura $\ge 90\%$ en `app/services/` y $\ge 70\%$ global en `pytest --cov=app`.
- Inversión de Dependencias (DIP) obligatoria en servicios para testing unitario puro.

**Scale/Scope**: Microservicio monolítico modular bajo paquete `app/` compuesto por 2 entidades clave (`Usuario`, `Reserva`), 5 endpoints REST y 3 herramientas MCP.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artículo | Regla Constitucional | Estado | Justificación / Mecanismo de Cumplimiento |
|----------|----------------------|--------|-------------------------------------------|
| **I. Arquitectura en capas** | `routers/` delegan a `services/`, `services/` no importan SQLAlchemy/Session, `repositories/` única capa DB. | **PASSED** | Estructura de paquetes estricta: `routers/` -> `services/` -> `repositories/` -> `models/`. |
| **II. SOLID aplicado** | SRP en servicios, OCP en modelos/canchas, DIP con `repo=default_repo`. | **PASSED** | Parámetros por defecto `repo=reserva_repository` en todas las funciones de servicio. |
| **III. Persistencia** | SQLAlchemy 2.0, SQLite, FK `usuario_id` y filtrado obligatorio. | **PASSED** | Modelos con `mapped_column`, FK explícita y queries con filtro `usuario_id`. |
| **IV. Seguridad** | `passlib[bcrypt]` (`bcrypt<4.1`), JWT HS256, secretos en `.env`, `usuario_id` del JWT. | **PASSED** | Configuración centralizada en `app/config.py`, dependencia `get_current_user`. |
| **V. Endpoints REST** | Códigos 201, 200, 204, 400, 401, 403, 404, 422, 500. | **PASSED** | Mapeo exacto documentado en `contracts/openapi.yaml`. |
| **VI. MCP** | Reutilización de services, formato `{"error": "..."}`, confirmación de servidor. | **PASSED** | FastMCP en `app/mcp/server.py` llamando directamente a `services/`. |
| **VII. Testing** | Prohibido `unittest.mock` en services, $\ge 90\%$ cov services, $\ge 70\%$ global, test SQLite real. | **PASSED** | Fixtures con `RepositorioFalso`, configuración `pytest --cov` y tests de integración dedicados. |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-reservas-cancha/
├── spec.md              # Feature specification
├── plan.md              # This file (Implementation Plan)
├── research.md          # Technical research and architecture decisions
├── data-model.md        # Relational schema and DTO specifications
├── quickstart.md        # Verification and running guide
├── contracts/
│   ├── openapi.yaml     # REST API OpenAPI 3.1 specification
│   └── mcp_tools.json   # MCP Tools schema definition
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── config.py                 # Settings vía pydantic-settings (.env)
├── database.py               # Engine SQLAlchemy 2.0, SessionLocal, Base
├── dependencies.py           # get_db, get_current_user (JWT OAuth2)
├── main.py                   # FastAPI app, routers registration, MCP mount
├── logging_config.py         # Configuración de logging estructurado
├── models/
│   ├── __init__.py
│   ├── usuario.py            # Modelo SQLAlchemy Usuario
│   └── reserva.py            # Modelo SQLAlchemy Reserva
├── schemas/
│   ├── __init__.py
│   ├── usuario.py            # Pydantic schemas: UsuarioCreate, UsuarioResponse, Token
│   └── reserva.py            # Pydantic schemas: ReservaCreate, ReservaResponse
├── repositories/
│   ├── __init__.py
│   ├── base.py               # Protocolos e interfaces de repositorio
│   ├── usuario_repository.py # Acceso a BD para Usuario (SQLAlchemy)
│   └── reserva_repository.py # Acceso a BD para Reserva (SQLAlchemy)
├── services/
│   ├── __init__.py
│   ├── auth_service.py       # Hashing passlib, emisión/validación JWT
│   └── reserva_service.py    # Lógica de solapamiento, DIP con repo inyectable
├── routers/
│   ├── __init__.py
│   ├── auth.py               # /usuarios/ y /usuarios/token
│   └── reservas.py           # /reservas/ (POST, GET, DELETE)
├── utils/
│   ├── __init__.py
│   └── time_utils.py         # Funciones puras de validación de horas y formato
└── mcp/
    ├── __init__.py
    ├── server.py             # Servidor FastMCP integrado
    └── tools/
        ├── __init__.py
        └── reserva_tools.py  # Herramientas MCP conectadas a services/

tests/
├── __init__.py
├── conftest.py               # Fixtures globales, BD SQLite test, client HTTP
├── unit/
│   ├── __init__.py
│   ├── test_auth_service.py    # Tests unitarios auth
│   ├── test_reserva_service.py # Tests unitarios reserva usando RepositorioFalso
│   └── test_time_utils.py      # Tests unitarios utilidades de tiempo
├── integration/
│   ├── __init__.py
│   ├── test_db_repositories.py # Pruebas contra SQLite real
│   ├── test_auth_endpoints.py  # Pruebas HTTP endpoints /usuarios
│   └── test_reserva_endpoints.py # Pruebas HTTP endpoints /reservas
└── mcp/
    ├── __init__.py
    └── test_mcp_tools.py       # Pruebas de invocación de tools FastMCP
```

**Structure Decision**: Monoproyecto modular en capas bajo `app/` con separación rigurosa entre adaptadores (routers, MCP tools), núcleo de dominio/negocio (services), persistencia (repositories, models) y suite de pruebas (`tests/`).

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *Ninguna* | Cumple al 100% las restricciones de la Constitución sin excepciones. | N/A |
