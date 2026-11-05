# Multi-stage build para backend de SistemaTriaje

# Stage 1: Base con dependencias del sistema
FROM python:3.12-slim as base

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema para WeasyPrint y PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    # Dependencias de WeasyPrint
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Builder - instalar dependencias de Python
FROM base as builder

WORKDIR /build

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias en un virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Stage 3: Runtime
FROM base as runtime

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar virtualenv desde builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Establecer working directory
WORKDIR /app

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
