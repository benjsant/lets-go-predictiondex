# Dockerfile for Machine Learning Pipeline
# ----------------------------------------
# This container is responsible for running the machine learning pipeline,
# including dataset preparation, model training, evaluation, and optional
# hyperparameter tuning.
#
# It is typically executed as a batch-style container in a Docker Compose
# or CI/CD workflow.

# Base image
# ----------
# Use the official Python 3.11 slim image for a lightweight and consistent
# Python runtime.
FROM python:3.11-slim

# Working directory
# -----------------
# All ML-related code and artifacts are executed and stored under /app.
WORKDIR /app

# Environment configuration
# -------------------------
# PYTHONDONTWRITEBYTECODE prevents creation of .pyc files.
# PYTHONUNBUFFERED ensures immediate log output for container visibility.
# PYTHONPATH allows internal project modules to be imported correctly.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# System dependencies
# -------------------
# Install minimal system packages required to:
# - build Python packages with native extensions
# - enable PostgreSQL connectivity via libpq
#
# --no-install-recommends keeps the image lightweight.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Machine Learning dependencies
# -----------------------------
# Copy ML-specific requirements separately to leverage Docker layer caching.
COPY machine_learning/requirements.txt ./ml_requirements.txt
RUN pip install --no-cache-dir -r ml_requirements.txt

# Application source code
# -----------------------
# Copy machine learning logic, shared core utilities,
# and the ML container entrypoint script.
COPY machine_learning ./machine_learning
COPY core ./core
COPY docker/ml_entrypoint.py ./docker/ml_entrypoint.py

# Default command
# ---------------
# Execute the ML entrypoint script, which:
# - waits for the database to be ready,
# - configures the ML pipeline via environment variables,
# - runs training, evaluation, and/or dataset generation.
CMD ["python", "docker/ml_entrypoint.py"]
