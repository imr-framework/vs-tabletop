# syntax=docker/dockerfile:1.7

# Use official Python slim image (override via --build-arg PYTHON_VERSION=...)
ARG PYTHON_VERSION=3.10.20
FROM python:${PYTHON_VERSION}-slim AS base


# Create runtime session directory.
RUN mkdir -p /tmp/flask_session

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    SESSION_FILE_DIR=/tmp/flask_session

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt gunicorn

# Copy the full application code - adjust as necessary
COPY . .

RUN chmod +x /app/scripts/docker_entrypoint.sh

# Create an unprivileged runtime user.
RUN groupadd -r appuser && useradd -r -g appuser -m -s /bin/bash appuser \
 && chown -R appuser:appuser /app /tmp/flask_session
USER appuser

# Expose the port
EXPOSE 8080

ENTRYPOINT ["/app/scripts/docker_entrypoint.sh"]

# Run with threaded workers + simple-websocket compatible Socket.IO mode.
CMD ["gunicorn", "--worker-class", "gthread", "--threads", "8", "-w", "1", "--bind", "0.0.0.0:8080", "vstabletop.main.app:app", "--timeout", "120"]