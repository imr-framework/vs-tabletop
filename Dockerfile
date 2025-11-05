# Use official Python slim image
FROM python:3.11-slim AS base

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
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the full application code
COPY . .

# Create a non‑root user for running the app
RUN useradd --create-home appuser
USER appuser

# Expose the port
EXPOSE 8080

# Run the application using Gunicorn: adjusted module path
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "vstabletop.main.app:app", "--workers", "2", "--timeout", "120"]