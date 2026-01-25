"""
Monitoring Module
================

Provides Prometheus metrics collection and Evidently data drift monitoring.
"""

from .metrics import (
    track_prediction,
    track_request,
    track_error,
    metrics_middleware,
)

__all__ = [
    "track_prediction",
    "track_request",
    "track_error",
    "metrics_middleware",
]
