# Dockerfile
# Multi-stage build for Django — development, builder, production.

# ---- Stage 1: Base ----
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# ---- Stage 2: Development ----
FROM base AS development
ENV DJANGO_SETTINGS_MODULE=config.settings
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ---- Stage 3: Builder ----
FROM base AS builder
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput || true

# ---- Stage 4: Production ----
FROM python:3.12-slim AS production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
WORKDIR /app

# Security: non-root user
RUN addgroup --system --gid 1001 django \
    && adduser --system --uid 1001 --gid 1001 django

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=django:django /app /app
COPY --from=builder --chown=django:django /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder --chown=django:django /usr/local/bin /usr/local/bin

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

USER django
EXPOSE 8000

# Gunicorn for production (more workers, proper signal handling)
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "30", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
