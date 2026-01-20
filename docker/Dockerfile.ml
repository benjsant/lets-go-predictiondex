FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install ML dependencies
COPY machine_learning/requirements.txt ./ml_requirements.txt
RUN pip install --no-cache-dir -r ml_requirements.txt

# Copy application code
COPY machine_learning ./machine_learning
COPY core ./core
COPY docker/ml_entrypoint.py ./docker/ml_entrypoint.py

CMD ["python", "docker/ml_entrypoint.py"]
