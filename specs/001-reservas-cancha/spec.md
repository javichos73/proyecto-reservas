# Feature Specification: Sistema de Reservas para Cancha Sintética "Estrellas"

**Feature Branch**: `001-reservas-cancha`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "Sistema de reservas para la cancha de fútbol sintética 'Estrellas'. Entidades: Usuario, Reserva. Reglas de negocio: hora_fin > hora_inicio, no solapamiento en fecha/cancha, duración mínima 1 hora, aislamiento de reservas por usuario. Contrato REST y MCP con casos de error explícitos."

## Clarifications

### Session 2026-09-19
- Q: ¿Cuál es la granularidad y formato permitido para los minutos en los horarios de reserva? → A: Únicamente bloques de horas en punto enteras con minutos estrictamente ':00' (ej. 17:00 a 18:00 o 18:00 a 20:00). Minutos fraccionados (como 17:30 o 18:15) son inválidos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro y Autenticación de Usuarios (Priority: P1)

Como deportista o cliente del complejo deportivo, quiero registrar una cuenta con mi correo y contraseña e iniciar sesión para obtener acceso seguro y gestionar mis reservas.

**Why this priority**: Es la base del sistema y del aislamiento de seguridad; sin cuentas ni autenticación no se pueden atribuir reservas a usuarios de forma segura.

**Independent Test**: Puede probarse de forma aislada registrando un nuevo usuario con email y contraseña, verificando que no se exponga el hash y autenticándose para recibir un token de acceso válido.

**Acceptance Scenarios**:

1. **Given** un correo electrónico no registrado previamente y una contraseña válida, **When** el usuario solicita el registro de cuenta, **Then** el sistema crea el usuario y devuelve una confirmación con código HTTP 201 sin exponer la contraseña hasheada.
2. **Given** un correo electrónico que ya existe en el sistema, **When** un usuario intenta registrarse con ese mismo correo, **Then** el sistema rechaza la solicitud con código HTTP 400 indicando email duplicado.
3. **Given** credenciales correctas (email/username y contraseña), **When** el usuario solicita un token de acceso, **Then** el sistema emite un token JWT firmado y responde con código HTTP 200.
4. **Given** credenciales incorrectas, **When** el usuario intenta autenticarse, **Then** el sistema rechaza la solicitud con código HTTP 401.

---

### User Story 2 - Creación de Reserva con Validación de Solapamiento y Horarios (Priority: P1)

Como usuario autenticado, quiero reservar la cancha "Estrellas" indicando fecha, hora de inicio y hora de fin en horas en punto enteras para asegurar mi turno de juego sin conflictos con otros usuarios.

**Why this priority**: Constituye la funcionalidad nuclear del negocio (agendamiento de canchas deportivas).

**Independent Test**: Puede probarse creando reservas válidas asociadas al usuario autenticado y verificando que se rechacen reservas con horarios invertidos, duración menor a 1 hora, minutos fraccionados (distintos de :00) o solapadas en la misma fecha y cancha.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado y un horario disponible para la cancha en una fecha dada con duración $\ge 1$ hora, `hora_fin > hora_inicio` y minutos `:00`, **When** el usuario solicita crear la reserva, **Then** el sistema persiste la reserva asignada al `usuario_id` autenticado y responde con código HTTP 201.
2. **Given** una reserva existente de 18:00 a 19:00 en una fecha y cancha, **When** cualquier usuario intenta reservar de 18:00 a 20:00 en la misma fecha y cancha, **Then** el sistema rechaza la solicitud con código HTTP 400 por solapamiento de horario.
3. **Given** una reserva existente de 18:00 a 19:00, **When** un usuario solicita una reserva de 19:00 a 20:00 en la misma fecha y cancha, **Then** el sistema acepta la reserva con código HTTP 201 (los horarios contiguos no se solapan).
4. **Given** una solicitud de reserva con `hora_fin <= hora_inicio` o duración menor a 60 minutos, **When** el usuario intenta crear la reserva, **Then** el sistema rechaza la solicitud con código HTTP 400.
5. **Given** una solicitud de reserva con minutos fraccionados (ej. `17:30`, `18:15`), **When** el usuario intenta crear la reserva, **Then** el sistema rechaza la solicitud con código HTTP 400 indicando que únicamente se permiten horas en punto (`:00`).

---

### User Story 3 - Consulta de Reservas Privadas del Usuario (Priority: P2)

Como usuario autenticado, quiero listar mis reservas activas para consultar mis horarios programados sin ver las reservas personales de otros usuarios.

**Why this priority**: Permite al usuario hacer seguimiento de sus turnos programados manteniendo la privacidad de la información.

**Independent Test**: Puede probarse creando reservas con dos usuarios distintos (`Usuario A` y `Usuario B`) y verificando que la consulta de `Usuario A` devuelve únicamente sus reservas con paginación (`skip`, `limit`).

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con reservas existentes, **When** solicita el listado de sus reservas, **Then** el sistema devuelve una lista paginada (código HTTP 200) que contiene únicamente las reservas pertenecientes a su `usuario_id`.
2. **Given** una solicitud de listado sin token JWT o con token inválido, **When** se envía la petición, **Then** el sistema responde con código HTTP 401.

---

### User Story 4 - Cancelación de Reserva Propia (Priority: P2)

Como usuario autenticado, quiero cancelar una de mis reservas existentes cuando no pueda asistir para liberar el turno.

**Why this priority**: Permite la gestión del ciclo de vida de las reservas y asegura la liberación de espacios.

**Independent Test**: Puede probarse intentando cancelar una reserva propia (éxito 204), intentando cancelar una reserva ajena (error 403) y cancelando un id inexistente (error 404).

**Acceptance Scenarios**:

1. **Given** un usuario autenticado que es propietario de una reserva con id existente, **When** solicita cancelar dicha reserva, **Then** el sistema elimina o cancela la reserva y responde con código HTTP 204 (No Content).
2. **Given** un usuario autenticado que intenta cancelar una reserva perteneciente a otro usuario, **When** envía la solicitud de cancelación, **Then** el sistema deniega la acción con código HTTP 403 (Prohibido).
3. **Given** un usuario autenticado que intenta cancelar un identificador de reserva que no existe en la base de datos, **When** envía la solicitud, **Then** el sistema responde con código HTTP 404 (No encontrado).

---

### User Story 5 - Interacción y Operaciones mediante Model Context Protocol (MCP) (Priority: P3)

Como agente de IA o asistente inteligente en representación del usuario autenticado, quiero interactuar con el sistema a través de herramientas MCP (`crear_reserva`, `listar_reservas`, `cancelar_reserva`) para asistir en la gestión conversacional de reservas.

**Why this priority**: Extiende el acceso y la automatización inteligente del sistema mediante el estándar MCP.

**Independent Test**: Puede probarse invocando las tools MCP con la identidad resuelta del usuario y verificando respuestas exitosas y respuestas estructuradas de error `{"error": "..."}` sin interrumpir la sesión.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en sesión MCP, **When** el agente ejecuta la tool `crear_reserva` con parámetros válidos en horas en punto, **Then** la tool delega la lógica al servicio correspondiente y devuelve los datos de la reserva creada.
2. **Given** un conflicto de horario, minutos fraccionados o parámetros inválidos en una tool MCP, **When** se invoca `crear_reserva`, **Then** la tool devuelve un JSON estructurado con `{"error": "<mensaje explicativo>"}`.
3. **Given** una solicitud para cancelar una reserva vía MCP, **When** se invoca `cancelar_reserva`, **Then** se valida la propiedad del usuario y se solicita confirmación antes de la eliminación efectiva.

---

### Edge Cases

- **Horarios con minutos fraccionados**: Intentos de reserva con minutos distintos de :00 (ej. 17:30, 18:15, 19:45) deben ser rechazados con código HTTP 400.
- **Reservas en el límite de medianoche**: Las reservas deben estar contenidas dentro del mismo día calendario (fecha); horarios que crucen la medianoche deben ser rechazados según formato de fecha única.
- **Reservas contiguas exactas**: Una reserva que termina exactamente a la misma hora en que otra inicia (ej. 18:00 - 19:00 y 19:00 - 20:00) NO constituye solapamiento y debe permitirse.
- **Intentos de inyección o suplantación de `usuario_id`**: El parámetro `usuario_id` no se aceptará nunca en el body o query params; se resolverá exclusivamente desde el token JWT.
- **Formato de horas y fechas inválido**: Solicitudes con fechas u horas mal formadas deben ser rechazadas con error de validación HTTP 422.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir el registro de usuarios con email único y contraseña segura, almacenando la contraseña hasheada y sin exponerla jamás en respuestas.
- **FR-002**: El sistema DEBE autenticar usuarios mediante OAuth2 Password Flow emitiendo tokens JWT firmados con HS256.
- **FR-003**: El sistema DEBE requerir autenticación JWT obligatoria en todas las operaciones sobre reservas (`crear`, `listar`, `cancelar`).
- **FR-004**: El sistema DEBE validar que la `hora_fin` sea estrictamente posterior a la `hora_inicio`.
- **FR-005**: El sistema DEBE validar que la duración mínima entre `hora_inicio` y `hora_fin` sea de al menos 1 hora (60 minutos).
- **FR-006**: El sistema DEBE verificar y prevenir cualquier solapamiento de horario para la misma cancha y fecha con cualquier otra reserva existente en la base de datos.
- **FR-007**: El sistema DEBE asociar automáticamente toda reserva creada al `usuario_id` extraído del token JWT verificado.
- **FR-008**: El sistema DEBE filtrar las consultas de listado de reservas para que cada usuario únicamente pueda visualizar sus propias reservas.
- **FR-009**: El sistema DEBE soportar paginación en el listado de reservas mediante parámetros `skip` (por defecto 0) y `limit` (por defecto 20).
- **FR-010**: El sistema DEBE verificar la propiedad de una reserva antes de cancelar, devolviendo HTTP 403 si un usuario intenta cancelar una reserva de otro usuario y HTTP 404 si la reserva no existe.
- **FR-011**: El sistema DEBE exponer herramientas MCP (`crear_reserva`, `listar_reservas`, `cancelar_reserva`) que reutilicen directamente la capa de servicios sin duplicar lógica de negocio.
- **FR-012**: Las herramientas MCP DEBEN retornar errores controlados bajo el formato `{"error": "..."}` ante violaciones de reglas de negocio sin interrumpir la conexión del cliente.
- **FR-013**: El sistema DEBE exigir que los horarios de `hora_inicio` y `hora_fin` sean exclusivamente horas en punto enteras con minutos estrictamente `:00` (formato `HH:00`), rechazando cualquier reserva con minutos fraccionados (ej. 17:30, 18:15) con error HTTP 400.

### Key Entities

- **Usuario**: Representa a la persona registrada en el sistema.
  - Atributos clave: `id`, `email` (único, formato correo), `password_hash` (cadena hasheada, privada), `creado_en`.
- **Reserva**: Representa la asignación y bloqueo de horario para la cancha sintética.
  - Atributos clave: `id`, `cancha` (cadena de texto, ej. "Cancha Estrellas"), `fecha` (formato YYYY-MM-DD), `hora_inicio` (formato HH:00), `hora_fin` (formato HH:00), `usuario_id` (clave foránea que relaciona la reserva con su creador).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las solicitudes de reserva con solapamiento de horario en la misma cancha y fecha son bloqueadas y rechazadas con código HTTP 400.
- **SC-002**: El 100% de los intentos de crear reservas con duración menor a 1 hora, `hora_fin <= hora_inicio` o minutos fraccionados distintos de `:00` son rechazados con código HTTP 400.
- **SC-003**: Cero fugas de información de reservas ajenas: en el 100% de las pruebas de listado privado, un usuario solo puede ver sus propios registros.
- **SC-004**: Cero operaciones no autorizadas de cancelación: el 100% de intentos de cancelación de reservas ajenas son rechazados con código HTTP 403.
- **SC-005**: Cobertura de pruebas unitarias $\ge 90\%$ en la capa de servicios y $\ge 70\%$ en cobertura global del proyecto.
- **SC-006**: 100% de los casos de prueba obligatorios definidos en la constitución y especificación cuentan con tests automatizados dedicados sin uso de `unittest.mock` en la capa de servicios.

## Assumptions

- Se asume el nombre de cancha por defecto "Cancha Estrellas" para la fase inicial, permitiendo la extensión futura a múltiples canchas vía configuración/enums según el principio OCP.
- Las reservas se realizan en bloques horarios dentro de un mismo día (la fecha rige tanto el inicio como el fin de la reserva).
- El formato de hora se maneja exclusivamente en bloques de horas en punto enteras (los minutos deben ser estrictamente `:00`).
- En caso de consultas MCP vía transporte `streamable-http`, la identidad del usuario se suministra en el contexto de autenticación de la sesión HTTP; en `stdio` se utiliza un fallback configurable documentado para pruebas y desarrollo.
