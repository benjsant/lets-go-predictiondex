FROM python:3.11-slim

# ----------------------------
# System
# ----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ----------------------------
# System deps
# ----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Python deps
# ----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Project
# ----------------------------
COPY . .

# ----------------------------
# Default (override in compose)
# ----------------------------
CMD ["bash"]
