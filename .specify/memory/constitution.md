<!--
Sync Impact Report:
- Version change: Unratified / Template Draft -> 1.0.0 (Initial Ratification)
- Added principles:
  - I. Arquitectura en capas
  - II. SOLID aplicado
  - III. Persistencia
  - IV. Seguridad (No Negociable)
  - V. Diseño de Endpoints REST
  - VI. Model Context Protocol (MCP)
  - VII. Testing y Cobertura
- Governance: Added precedence, compliance review expectations, and amendment rules.
- Follow-up TODOs: None
-->

# Sistema de Reservas de Cancha Sintética Constitution

## Core Principles

### I. Arquitectura en Capas
1. `routers/` reciben las peticiones HTTP, delegan al service correspondiente y traducen excepciones a códigos HTTP. Un router NUNCA valida reglas de negocio (ej. solapamiento de horarios) — esa lógica vive exclusivamente en `services/`.
2. `services/` contienen toda la lógica de negocio. Un service NUNCA importa SQLAlchemy, `Session`, ni detalles de persistencia directamente.
3. `repositories/` son la única capa autorizada para interactuar con la base de datos. Devuelven estructuras simples (dict o entidades de dominio), nunca exponen objetos de sesión ni consultas ORM crudas.
4. `utils/` contiene funciones puras sin dependencias cruzadas de capas.
5. `mcp/tools/` NUNCA reimplementan reglas de negocio. Si una tool MCP y un router hacen la misma acción, ambos llaman a la misma función en `services/`.

### II. SOLID Aplicado
1. **SRP (Single Responsibility Principle)**: Cada función de `services/` tiene una sola responsabilidad (ej. validación de solapamiento separada de la orquestación de creación).
2. **OCP (Open/Closed Principle)**: Nuevas canchas o tipos de reserva se configuran vía constantes/enums, sin reescribir la lógica existente.
3. **DIP (Dependency Inversion Principle)**: Todo service recibe su repositorio como parámetro con valor por defecto (`def crear_reserva(..., repo=reservas_repository)`). Innegociable para permitir testing sin `unittest.mock`.

### III. Persistencia
1. SQLAlchemy 2.0 como ORM, SQLite en desarrollo.
2. Todo modelo de datos de usuario incluye `usuario_id` como clave foránea (FK). Ninguna consulta de reservas puede omitir el filtro por `usuario_id` cuando sea consulta privada del usuario.

### IV. Seguridad (No Negociable)
1. Contraseñas hasheadas con `passlib[bcrypt]` (fijando `bcrypt<4.1`).
2. Autenticación con OAuth2 password flow y tokens JWT firmados con HS256.
3. Secretos (`SECRET_KEY`, `DATABASE_URL`) viven únicamente en `.env`. Se versiona `.env.example` con la plantilla de variables requeridas.
4. Autorización: El `usuario_id` para crear, listar o cancelar reservas SIEMPRE se extrae del JWT (`get_current_user`), NUNCA de parámetros de la URL, query params o el cuerpo JSON.

### V. Diseño de Endpoints REST
1. Códigos de respuesta estándar: `POST` crea (`201`), `GET` lista (`200`), `DELETE` cancela/elimina (`204`).
2. Errores esperados:
   - Autenticación requerida: `401`
   - Regla de negocio violada o solapamiento: `400`
   - No dueño al cancelar: `403`
   - Recurso no encontrado: `404`
   - Validación Pydantic: `422`
   - Error interno no controlado: `500`

### VI. Model Context Protocol (MCP)
1. Toda tool MCP reutiliza directamente funciones de `services/`.
2. Las descripciones de las tools son específicas, claras y accionables.
3. Errores de negocio en MCP se devuelven como `{"error": "..."}`, nunca rompiendo la sesión del cliente.
4. La identidad del usuario en MCP se resuelve desde el token JWT en transporte streamable-http (con fallback documentado si corre en stdio).
5. Cancelar una reserva mediante MCP exige confirmación del servidor.

### VII. Testing y Cobertura
1. Prohibido usar `unittest.mock` en los tests de `services/`. Se utiliza un `RepositorioFalso` inyectado por parámetro (DIP).
2. Cada regla de negocio de `spec.md` tiene al menos un test unitario dedicado.
3. Cobertura obligatoria: $\ge 90\%$ en `services/` y $\ge 70\%$ global (`pytest --cov=app --cov-report=term-missing`). Se excluyen `main.py`, `mcp/server.py` y `logging_config.py` en `pyproject.toml`.
4. Al menos un test de integración contra base de datos real (SQLite).

## Governance

1. **Supremacía Constitucional**: Esta constitución tiene prioridad sobre cualquier propuesta del agente o convención externa. Cualquier desviación debe ser señalada explícitamente y esperar confirmación del usuario.
2. **Proceso de Enmienda**: Toda modificación requiere actualizar este documento, justificar el cambio de versión semántica (MAJOR para cambios incompatibles/eliminaciones, MINOR para adición de artículos, PATCH para aclaraciones) y documentar el impacto.
3. **Revisión de Cumplimiento**: Cada especificación (`spec.md`), plan (`plan.md`), lista de tareas (`tasks.md`) y PR/revisión debe verificar el cumplimiento estricto de estos artículos.

**Version**: 1.0.0 | **Ratified**: 2026-09-19 | **Last Amended**: 2026-09-19
