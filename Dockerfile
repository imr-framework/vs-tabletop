# syntax=docker/dockerfile:1.7

# Use official Python slim image (override via --build-arg PYTHON_VERSION=...)
ARG PYTHON_VERSION=3.10.20
FROM python:${PYTHON_VERSION}-slim AS base


# Create the directory if it doesn't exist
RUN mkdir -p /app/flask_session

## Grant write permissions to the directory for all users (or a specific group)
##RUN chmod 775 /app/flask_session
RUN chmod 777 /app/flask_session 

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

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

# Create a non‑root user with full privileges for running the app
RUN useradd -u 0 -o -m -s /bin/bash appuser
USER appuser

# Expose the port
EXPOSE 8080

# Run with threaded workers + simple-websocket compatible Socket.IO mode.
CMD ["gunicorn", "--worker-class", "gthread", "--threads", "8", "-w", "1", "--bind", "0.0.0.0:8080", "vstabletop.main.app:app", "--timeout", "120"]