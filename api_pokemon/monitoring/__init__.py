"""
Monitoring Module
================

Provides Prometheus metrics collection and Evidently data drift monitoring.
"""

from .metrics import (
    metrics_middleware,
    track_error,
    track_prediction,
    track_request,
)

__all__ = [
    "track_prediction",
    "track_request",
    "track_error",
    "metrics_middleware",
]
