# Tasks: Sistema de Reservas para Cancha Sintética "Estrellas"

**Branch**: `001-reservas-cancha` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency management, and configuration loading.

- [X] T001 Configure project dependencies in `pyproject.toml` (`fastapi`, `uvicorn[standard]`, `sqlalchemy>=2.0`, `pyjwt`, `passlib[bcrypt]`, `bcrypt<4.1>`, `pydantic-settings`, `email-validator`, `python-multipart`, `mcp[cli]<2`, `pytest`, `pytest-cov`, `httpx`).
- [X] T002 [P] Create environment variables template in `.env.example` and configuration loader in `app/config.py` using `pydantic-settings`.
- [X] T003 [P] Configure structured logging in `app/logging_config.py`.

---

## Phase 2: Foundational (Core DB, Base Repositories & Utilities)

**Purpose**: Core infrastructure and pure utilities that MUST be complete before user stories can be implemented.

**⚠️ CRITICAL**: Foundational components required across all domain entities and testing fixtures.

- [X] T004 Setup SQLAlchemy 2.0 database engine, SessionLocal, and DeclarativeBase in `app/database.py`.
- [X] T005 [P] Create base repository protocols and domain interfaces in `app/repositories/base.py`.
- [X] T006 [P] Implement pure time validation and parsing utilities in `app/utils/time_utils.py` (enforcing strict `:00` minutes `pattern="^([01]\d|2[0-3]):00$"`, temporal ordering `hora_fin > hora_inicio`, and duration $\ge 1$ hour).
- [X] T007 [P] Unit tests for pure time utilities in `tests/unit/test_time_utils.py` (validating `:00` constraint, rejected fractional minutes, and durations).
- [X] T008 [P] Setup global pytest fixtures, in-memory SQLite database, and HTTP TestClient in `tests/conftest.py`.

**Checkpoint**: Foundation ready - User Story implementation can proceed in order.

---

## Phase 3: User Story 1 - Registro y Autenticación de Usuarios (Priority: P1) 🎯 MVP Part 1

**Goal**: Permitir el registro de usuarios con email único y contraseña cifrada con bcrypt (`bcrypt<4.1`), y autenticación mediante OAuth2 Password Flow con tokens JWT (HS256).

**Independent Test**: Registrar un usuario en `/usuarios/`, verificar que no expone el hash de contraseña, y autenticarse en `/usuarios/token` para obtener un JWT válido.

### Tests for User Story 1

- [X] T009 [P] [US1] Unit tests for AuthService in `tests/unit/test_auth_service.py` (verifying bcrypt hashing, password verification, JWT generation with HS256, and duplicate email detection).
- [X] T010 [P] [US1] Integration tests for authentication endpoints in `tests/integration/test_auth_endpoints.py` (verifying HTTP 201 on register, HTTP 400 on duplicate email, HTTP 200 on valid token request, and HTTP 401 on invalid credentials).

### Implementation for User Story 1

- [X] T011 [P] [US1] Create Usuario SQLAlchemy model in `app/models/usuario.py` (`id: int`, `email: str` unique indexed, `password_hash: str`, `creado_en: datetime`).
- [X] T012 [P] [US1] Create Usuario Pydantic schemas in `app/schemas/usuario.py` (`UsuarioCreate`, `UsuarioResponse`, `TokenResponse`, `TokenData`).
- [X] T013 [US1] Implement UsuarioRepository in `app/repositories/usuario_repository.py` (methods: `get_by_email`, `get_by_id`, `create`).
- [X] T014 [US1] Implement AuthService in `app/services/auth_service.py` (methods: `crear_usuario`, `autenticar_usuario`, `crear_access_token`, `verificar_token`).
- [X] T015 [US1] Implement FastAPI dependencies (`get_db`, `get_current_user`) in `app/dependencies.py` to extract `usuario_id` securely from JWT.
- [X] T016 [US1] Implement auth router in `app/routers/auth.py` (`POST /usuarios/`, `POST /usuarios/token`) and register in `app/main.py`.

**Checkpoint**: User Story 1 functional - Users can register and obtain JWT authentication tokens.

---

## Phase 4: User Story 2 - Creación de Reserva con Validación de Solapamiento y Horarios (Priority: P1) 🎯 MVP Part 2

**Goal**: Permitir a usuarios autenticados reservar la cancha "Estrellas" con validación estricta de solapamientos, horas en punto exactas (`:00`), duración mínima $\ge 1$ hora y `hora_fin > hora_inicio`.

**Independent Test**: Crear reservas válidas con JWT autenticado y verificar que se rechacen intentos de solapamiento en misma fecha/cancha (HTTP 400), minutos fraccionados (HTTP 400) y horarios invertidos (HTTP 400).

### Tests for User Story 2

- [X] T017 [P] [US2] Unit tests for ReservaService creation in `tests/unit/test_reserva_service.py` using `RepositorioFalso` (strictly NO `unittest.mock` per Constitution Art. VII) covering: valid creation, overlapping schedules on same date/court, contiguous exact slots (18:00-19:00 and 19:00-20:00 allowed), `hora_fin <= hora_inicio`, duration < 1h, and fractional minutes (e.g. 18:30).
- [X] T018 [P] [US2] Integration tests for reservation creation endpoint in `tests/integration/test_reserva_endpoints.py` (`POST /reservas/` testing HTTP 201, HTTP 400 overlap, HTTP 400 invalid times, HTTP 401 unauthenticated, HTTP 422 malformed).

### Implementation for User Story 2

- [X] T019 [P] [US2] Create Reserva SQLAlchemy model in `app/models/reserva.py` (`id: int`, `cancha: str`, `fecha: str`, `hora_inicio: str`, `hora_fin: str`, `usuario_id: int` FK, `creado_en: datetime`).
- [X] T020 [P] [US2] Create Reserva Pydantic schemas in `app/schemas/reserva.py` (`ReservaCreate` with regex pattern `^([01]\d|2[0-3]):00$`, `ReservaResponse`).
- [X] T021 [US2] Implement ReservaRepository in `app/repositories/reserva_repository.py` (method: `buscar_solapamientos(cancha, fecha, hora_inicio, hora_fin)`, `crear_reserva`).
- [X] T022 [US2] Implement `crear_reserva` in `app/services/reserva_service.py` with Dependency Inversion (`repo=reserva_repository` default param) performing two-phase validation: time constraints + overlap verification.
- [X] T023 [US2] Implement POST `/reservas/` endpoint in `app/routers/reservas.py` delegating to `reserva_service` and mapping domain exceptions to HTTP status codes.

**Checkpoint**: Core MVP functional - Users can authenticate and book non-overlapping court slots.

---

## Phase 5: User Story 3 - Consulta de Reservas Privadas del Usuario (Priority: P2)

**Goal**: Permitir a usuarios autenticados consultar el listado paginado (`skip`, `limit`) exclusivamente de sus propias reservas.

**Independent Test**: Crear reservas con dos usuarios distintos y verificar que `GET /reservas/` devuelve únicamente las reservas del usuario autenticado en el token JWT.

### Tests for User Story 3

- [X] T024 [P] [US3] Unit tests for ReservaService listing in `tests/unit/test_reserva_service.py` using `RepositorioFalso` (validating pagination and strict filtering by `usuario_id`).
- [X] T025 [P] [US3] Integration tests for listing endpoint in `tests/integration/test_reserva_endpoints.py` (`GET /reservas/` verifying user privacy isolation, pagination parameters, and HTTP 401 when unauthenticated).

### Implementation for User Story 3

- [X] T026 [US3] Implement `listar_por_usuario(usuario_id, skip, limit)` in `app/repositories/reserva_repository.py`.
- [X] T027 [US3] Implement `listar_reservas(usuario_id, skip=0, limit=20, repo=reserva_repository)` with DIP in `app/services/reserva_service.py`.
- [X] T028 [US3] Implement GET `/reservas/` endpoint in `app/routers/reservas.py` extracting `usuario_id` via `get_current_user`.

**Checkpoint**: User Stories 1, 2, and 3 functional - Private listing verified.

---

## Phase 6: User Story 4 - Cancelación de Reserva Propia (Priority: P2)

**Goal**: Permitir a usuarios autenticados cancelar una reserva propia devolviendo HTTP 204, impidiendo la cancelación de reservas ajenas (HTTP 403) o inexistentes (HTTP 404).

**Independent Test**: Cancelar una reserva propia (HTTP 204), intentar cancelar una reserva ajena con otro usuario (HTTP 403) e intentar cancelar un ID que no existe (HTTP 404).

### Tests for User Story 4

- [X] T029 [P] [US4] Unit tests for ReservaService cancellation in `tests/unit/test_reserva_service.py` using `RepositorioFalso` (testing successful deletion, unauthorized cancellation error for different user, and not found error).
- [X] T030 [P] [US4] Integration tests for cancellation endpoint in `tests/integration/test_reserva_endpoints.py` (`DELETE /reservas/{id}` validating HTTP 204, HTTP 403, HTTP 404, and HTTP 401).

### Implementation for User Story 4

- [X] T031 [US4] Implement `eliminar_reserva(reserva_id)` and `get_by_id(reserva_id)` in `app/repositories/reserva_repository.py`.
- [X] T032 [US4] Implement `cancelar_reserva(reserva_id, usuario_id, repo=reserva_repository)` with DIP in `app/services/reserva_service.py` validating ownership.
- [X] T033 [US4] Implement DELETE `/reservas/{id}` endpoint in `app/routers/reservas.py` mapping domain errors to HTTP 403/404/204.

**Checkpoint**: Full REST API lifecycle complete and verified.

---

## Phase 7: User Story 5 - Interacción y Operaciones mediante Model Context Protocol (MCP) (Priority: P3)

**Goal**: Exponer herramientas FastMCP (`crear_reserva`, `listar_reservas`, `cancelar_reserva`) sobre streamable-http/stdio, reutilizando directamente `services/` y devolviendo errores formateados como `{"error": "..."}`.

**Independent Test**: Invocar las tools MCP y verificar creación exitosa de reservas, listado paginado, confirmación de cancelación y retorno de respuestas de error `{"error": "..."}` sin romper la sesión.

### Tests for User Story 5

- [X] T034 [P] [US5] Unit and integration tests for FastMCP tools in `tests/mcp/test_mcp_tools.py` (testing `crear_reserva`, `listar_reservas`, `cancelar_reserva`, formatted error handling, and user resolution).

### Implementation for User Story 5

- [X] T035 [US5] Implement FastMCP server setup and streamable-http ASGI mount in `app/mcp/server.py` and attach to FastAPI in `app/main.py`.
- [X] T036 [US5] Implement FastMCP tools in `app/mcp/tools/reserva_tools.py` directly invoking `app/services/reserva_service.py` and handling exceptions as `{"error": str(e)}`.

**Checkpoint**: MCP protocol integration complete.

---

## Phase 8: Polish, Integration & Mandatory Coverage Gate

**Purpose**: Verificación de persistencia real SQLite, ejecución E2E y cumplimiento estricto de la Constitución.

- [X] T037 [P] Integration tests against real SQLite database in `tests/integration/test_db_repositories.py` (verifying SQLAlchemy 2.0 transactions and constraint enforcement).
- [X] T038 Execute end-to-end verification scenario scripts per `specs/001-reservas-cancha/quickstart.md`.
- [X] T039 Mandatory Constitution Coverage Gate: Execute `pytest --cov=app --cov-report=term-missing` and enforce coverage thresholds ($\ge 90\%$ in `app/services/` and $\ge 70\%$ global, excluding `main.py`, `mcp/server.py`, `logging_config.py` in `pyproject.toml`).

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Can start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 - Blocks all User Stories.
- **Phase 3 (US1 - Auth)**: Depends on Phase 2 - MVP Part 1.
- **Phase 4 (US2 - Crear Reserva)**: Depends on Phase 3 (needs user auth context) - MVP Part 2.
- **Phase 5 (US3 - Listar Reservas)**: Depends on Phase 4 (needs existing reservation logic).
- **Phase 6 (US4 - Cancelar Reserva)**: Depends on Phase 4 and Phase 5.
- **Phase 7 (US5 - MCP)**: Depends on Phase 4, Phase 5, Phase 6 (reusable services).
- **Phase 8 (Polish & Coverage Gate)**: Depends on all user stories being completed.

### Layer-by-Layer Dependency Flow within Stories
1. **Tests (TDD)**: Written first (`tests/unit/`, `tests/integration/`).
2. **Models & Schemas**: `app/models/`, `app/schemas/`.
3. **Repositories**: `app/repositories/`.
4. **Services (DIP)**: `app/services/` (receiving repository by parameter).
5. **Adapters**: `app/routers/`, `app/mcp/tools/`.

---

## Parallel Opportunities

```bash
# Phase 1 Parallel Setup:
Task T002: "Create .env.example and app/config.py"
Task T003: "Configure structured logging in app/logging_config.py"

# Phase 2 Parallel Foundational:
Task T005: "Create base repository protocols in app/repositories/base.py"
Task T006: "Implement pure time utilities in app/utils/time_utils.py"
Task T007: "Unit tests for time utilities in tests/unit/test_time_utils.py"
Task T008: "Setup global pytest fixtures in tests/conftest.py"

# Phase 3 Parallel Tests & Models:
Task T009: "Unit tests for AuthService in tests/unit/test_auth_service.py"
Task T010: "Integration tests for auth endpoints in tests/integration/test_auth_endpoints.py"
Task T011: "Create Usuario model in app/models/usuario.py"
Task T012: "Create Usuario schemas in app/schemas/usuario.py"

# Phase 4 Parallel Tests & Models:
Task T017: "Unit tests for ReservaService in tests/unit/test_reserva_service.py"
Task T018: "Integration tests for reservation endpoint in tests/integration/test_reserva_endpoints.py"
Task T019: "Create Reserva model in app/models/reserva.py"
Task T020: "Create Reserva schemas in app/schemas/reserva.py"
```

---

## Implementation Strategy

### MVP Scope (Phases 1-4)
1. Complete Setup + Foundational (Phases 1-2).
2. Complete US1 (User Registration & JWT Auth).
3. Complete US2 (Court Reservation Creation with Schedule & Overlap Validation).
4. **MVP Validation Checkpoint**: Verify with automated test suite and manual verification.

### Incremental Delivery (Phases 5-8)
1. Add US3 (Private Listing) → Validate.
2. Add US4 (Cancellation) → Validate.
3. Add US5 (FastMCP Tools) → Validate.
4. Run Phase 8 Polish & Mandatory Coverage Gate ($\ge 90\%$ services, $\ge 70\%$ global).
