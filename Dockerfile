# Use official Python slim image
FROM python:3.11-slim AS base


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
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the full application code - adjust as necessary
COPY . .

# Create a non‑root user with full privileges for running the app
RUN useradd -u 0 -o -m -s /bin/bash appuser
USER appuser

# Expose the port
EXPOSE 8080

# Run the application using Gunicorn: adjusted module path
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "vstabletop.main.app:app", "--workers", "2", "--timeout", "120"]