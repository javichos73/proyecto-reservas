FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip

# Copiar configuración e instalar dependencias declaradas en pyproject.toml
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

# Copiar el código del proyecto
COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
