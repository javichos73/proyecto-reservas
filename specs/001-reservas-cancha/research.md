# Research Document: Sistema de Reservas para Cancha Sintética "Estrellas"

**Branch**: `001-reservas-cancha` | **Date**: 2026-09-19 | **Feature**: [spec.md](./spec.md)

## 1. Technical Stack & Dependencies

### Decision: Python 3.11+ con FastAPI & Pydantic v2
- **Rationale**: FastAPI proporciona alto rendimiento asíncrono, generación automática de documentación OpenAPI y tipado fuerte con Pydantic v2.
- **Alternatives considered**: Flask (menor soporte nativo para async/OpenAPI), Django/DRF (demasiado pesado para microservicio con MCP integrado).

### Decision: SQLAlchemy 2.0 con SQLite en desarrollo
- **Rationale**: SQLAlchemy 2.0 ofrece sintaxis tipada (`Mapped`, `mapped_column`, `select`) y separación limpia entre ORM y modelos relacionales. SQLite cumple con el Artículo III de la Constitución para entornos de desarrollo y pruebas.
- **Alternatives considered**: Raw SQLite (falta de abstracción y migraciones), Tortoise ORM (menor adopción y ecosistema que SQLAlchemy).

### Decision: Seguridad con `passlib[bcrypt]` (`bcrypt<4.1`) y `pyjwt` (HS256)
- **Rationale**: Requisito constitucional innegociable (Artículo IV). Fijar `bcrypt<4.1` evita incompatibilidades conocidas entre versiones recientes de passlib y bcrypt. JWT firmado con algoritmo HS256 y expiración configurable vía `pydantic-settings`.
- **Alternatives considered**: Argon2 (no especificado en constitución), OAuth externo (requiere conexión de terceros, innecesario para MVP local).

### Decision: FastMCP (`mcp[cli]<2`) montado sobre FastAPI (streamable-http y stdio)
- **Rationale**: Cumple el Artículo VI de la Constitución. Permite exponer herramientas estandarizadas reutilizando directamente `services/` sin duplicar lógica y manejando respuestas de error bajo formato `{"error": "..."}`.
- **Alternatives considered**: MCP en proceso separado (mayor complejidad de despliegue y compartición de estado).

---

## 2. Layered Architecture & Dependency Inversion (DIP)

### Decision: Inyección de Repositorios en Servicios vía Default Parameters
- **Rationale**: Cumple el Artículo II.3 de la Constitución. Cada función de servicio recibe su repositorio con valor por defecto (`def crear_reserva(..., repo: ReservaRepositoryInterface = reserva_repository)`). Esto permite inyectar un `RepositorioFalso` en pruebas unitarias eliminando cualquier necesidad de `unittest.mock` (Artículo VII.1).
- **Alternatives considered**: Inyección de dependencias pesada (injector, dependency-injector) - descartada por sobreingeniería; `unittest.mock` - explícitamente prohibido en `services/` por la Constitución.

### Decision: Aislamiento estricto de capas
- **Routers**: Manejan HTTP (request/response, status codes, translation de excepciones a HTTP). Cero lógica de negocio.
- **Services**: Contienen toda la lógica de negocio y validaciones de solapamiento/horarios. Cero imports de SQLAlchemy o Session.
- **Repositories**: Única capa que interactúa con SQLAlchemy `Session`. Retornan entidades de dominio o diccionarios limpios.
- **Utils**: Funciones puras de validación de horas (ej. `es_hora_en_punto`, `calcular_duracion_horas`).

---

## 3. Business Rule Validation Strategy

### Decision: Validación de Solapamiento en Dos Fases
1. **Fase 1 (Pre-condiciones en memoria/servicio)**:
   - Validar que minutos sean `:00` (`hora_inicio.endswith(":00")` y `hora_fin.endswith(":00")`).
   - Validar que `hora_fin > hora_inicio`.
   - Validar duración $\ge 1$ hora.
2. **Fase 2 (Verificación de conflictos con persistencia vía Repositorio)**:
   - Consultar si existe alguna reserva activa en la misma `cancha` y `fecha` tal que:
     `reserva.hora_inicio < nueva_hora_fin AND reserva.hora_fin > nueva_hora_inicio`.
   - Si existe conflicto, lanzar excepción de dominio `SolapamientoError` (mapeada a HTTP 400 en Router / `{"error": "..."}` en MCP).
- **Rationale**: La fórmula matemática `inicio_A < fin_B AND fin_A > inicio_B` maneja con precisión intervalos abiertos/cerrados para que horarios contiguos (ej. 18:00-19:00 y 19:00-20:00) NO se solapen.
