"""
Prometheus Metrics Collection
=============================

Collects and exposes metrics for API and ML model monitoring.

Metrics collected:
- API request count, latency, errors
- Model prediction count, latency, confidence
- Resource usage
"""

import time
from typing import Callable

import psutil
from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

# ============================================================================
# API Metrics
# ============================================================================

# Request metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

api_errors_total = Counter(
    'api_errors_total',
    'Total number of API errors',
    ['method', 'endpoint', 'error_type']
)

# ============================================================================
# Model Metrics
# ============================================================================

model_predictions_total = Counter(
    'model_predictions_total',
    'Total number of model predictions',
    ['model_version']
)

model_prediction_duration_seconds = Histogram(
    'model_prediction_duration_seconds',
    'Model prediction duration in seconds',
    ['model_version'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

model_confidence_score = Histogram(
    'model_confidence_score',
    'Distribution of model prediction confidence scores (0-1)',
    ['model_version'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
)

model_win_probability = Histogram(
    'model_win_probability',
    'Distribution of win probabilities',
    ['model_version'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# ============================================================================
# System Metrics
# ============================================================================

system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'Current CPU usage in percent'
)

system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'Current memory usage in bytes'
)

system_memory_available = Gauge(
    'system_memory_available_bytes',
    'Available memory in bytes'
)


# ============================================================================
# Tracking Functions
# ============================================================================

def track_prediction(model_version: str, duration: float, confidence: float, win_prob: float):
    """
    Track a model prediction.

    Args:
        model_version: Version of the model (e.g., 'v2')
        duration: Prediction duration in seconds
        confidence: Confidence score (0-1)
        win_prob: Win probability (0-1)
    """
    model_predictions_total.labels(model_version=model_version).inc()
    model_prediction_duration_seconds.labels(model_version=model_version).observe(duration)
    model_confidence_score.labels(model_version=model_version).observe(confidence)
    model_win_probability.labels(model_version=model_version).observe(win_prob)


def track_request(method: str, endpoint: str, status: int, duration: float):
    """
    Track an API request.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        status: HTTP status code
        duration: Request duration in seconds
    """
    api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    api_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def track_error(method: str, endpoint: str, error_type: str):
    """
    Track an API error.

    Args:
        method: HTTP method
        endpoint: API endpoint path
        error_type: Type of error (e.g., 'ValidationError', 'DatabaseError')
    """
    api_errors_total.labels(method=method, endpoint=endpoint, error_type=error_type).inc()


def update_system_metrics():
    """Update system resource metrics."""
    system_cpu_usage.set(psutil.cpu_percent(interval=0.1))

    memory = psutil.virtual_memory()
    system_memory_usage.set(memory.used)
    system_memory_available.set(memory.available)


# ============================================================================
# Middleware
# ============================================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically track API requests and errors.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track metrics.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response from handler
        """
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        # Track request
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Track successful request
            track_request(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                duration=duration
            )

            # Update system metrics periodically
            update_system_metrics()

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Track error
            track_error(
                method=request.method,
                endpoint=request.url.path,
                error_type=type(e).__name__
            )

            # Also track as failed request
            track_request(
                method=request.method,
                endpoint=request.url.path,
                status=500,
                duration=duration
            )

            raise


def metrics_middleware(app):
    """
    Add Prometheus middleware to FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(PrometheusMiddleware)


# ============================================================================
# Metrics Endpoint
# ============================================================================

def get_metrics() -> Response:
    """
    Generate Prometheus metrics response.

    Returns:
        Response with Prometheus metrics in text format
    """
    # Update system metrics before generating response
    update_system_metrics()

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
