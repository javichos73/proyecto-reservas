# Quickstart & Verification Guide: Sistema de Reservas

**Feature**: Sistema de Reservas para Cancha Sintética "Estrellas" (`001-reservas-cancha`)
**Artifacts**: [spec.md](./spec.md) | [data-model.md](./data-model.md) | [contracts/openapi.yaml](./contracts/openapi.yaml)

---

## 1. Prerequisites & Environment Setup

```bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias del proyecto
pip install fastapi "uvicorn[standard]" "sqlalchemy>=2.0" pyjwt "passlib[bcrypt]" "bcrypt<4.1" pydantic-settings email-validator python-multipart "mcp[cli]<2" pytest pytest-cov httpx

# 3. Configurar variables de entorno iniciales
cp .env.example .env
```

---

## 2. Running Automated Tests & Coverage Gate

Validación de cumplimiento estricto con el Artículo VII de la Constitución ($\ge 90\%$ en `services/` y $\ge 70\%$ global):

```bash
# Ejecutar suite de pruebas con reporte de cobertura
pytest --cov=app --cov-report=term-missing
```

**Resultados esperados**:
- 0 errores, 0 fallos.
- Cobertura en `app/services/` $\ge 90\%$.
- Cobertura global $\ge 70\%$.

---

## 3. Manual / End-to-End API Verification Scenario

### Paso 1: Iniciar el servidor
```bash
uvicorn app.main:app --reload --port 8000
```

### Paso 2: Registrar un nuevo usuario
```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"email": "jugador@ejemplo.com", "password": "password123"}'
# Esperado: HTTP 201 {"id": 1, "email": "jugador@ejemplo.com", ...}
```

### Paso 3: Obtener Token JWT
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/usuarios/token \
  -F "username=jugador@ejemplo.com" \
  -F "password=password123" | jq -r .access_token)
```

### Paso 4: Crear una reserva válida
```bash
curl -X POST http://localhost:8000/reservas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cancha": "Cancha Estrellas", "fecha": "2026-09-25", "hora_inicio": "18:00", "hora_fin": "19:00"}'
# Esperado: HTTP 201 {"id": 1, "cancha": "Cancha Estrellas", "hora_inicio": "18:00", ...}
```

### Paso 5: Probar rechazo de solapamiento (Misma fecha/cancha)
```bash
curl -X POST http://localhost:8000/reservas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cancha": "Cancha Estrellas", "fecha": "2026-09-25", "hora_inicio": "18:00", "hora_fin": "20:00"}'
# Esperado: HTTP 400 {"detail": "..."}
```

### Paso 6: Probar rechazo de minutos fraccionados
```bash
curl -X POST http://localhost:8000/reservas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cancha": "Cancha Estrellas", "fecha": "2026-09-25", "hora_inicio": "18:30", "hora_fin": "19:30"}'
# Esperado: HTTP 400 o 422
```

### Paso 7: Listar reservas privadas
```bash
curl -X GET http://localhost:8000/reservas/ \
  -H "Authorization: Bearer $TOKEN"
# Esperado: HTTP 200 con array conteniendo la reserva creada
```

### Paso 8: Cancelar reserva propia
```bash
curl -X DELETE http://localhost:8000/reservas/1 \
  -H "Authorization: Bearer $TOKEN"
# Esperado: HTTP 204 No Content
```
