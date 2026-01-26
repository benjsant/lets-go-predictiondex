# app/main.py

from fastapi import FastAPI, Depends
from fastapi.responses import Response
import os

from api_pokemon.routes import (
    pokemon_route,
    moves_route,
    type_route,
    prediction_route,
)
from api_pokemon.monitoring.metrics import metrics_middleware, get_metrics
from api_pokemon.middleware.security import verify_api_key

# Vérifier si l'API Key est requise (en production)
API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "true").lower() == "true"

app = FastAPI(
    title="Pokémon Let's Go API",
    description="REST API for Pokémon Let's Go Pikachu / Eevee with ML-powered battle predictions - Secured with API Key",
    version="2.0.0",
)

# Add Prometheus metrics middleware
metrics_middleware(app)

@app.get("/health", tags=["health"])
def healthcheck():
    """Health check endpoint - no authentication required"""
    return {"status": "healthy"}

@app.get("/metrics", tags=["monitoring"])
def metrics() -> Response:
    """
    Prometheus metrics endpoint - no authentication required for monitoring.
    
    Exposes metrics for:
    - API request count, latency, errors
    - Model prediction count, latency, confidence
    - System resource usage
    """
    return get_metrics()

# Routes protégées par API Key (si API_KEY_REQUIRED=true)
dependencies = [Depends(verify_api_key)] if API_KEY_REQUIRED else []

app.include_router(pokemon_route.router, dependencies=dependencies)
app.include_router(moves_route.router, dependencies=dependencies)
app.include_router(type_route.router, dependencies=dependencies)
app.include_router(prediction_route.router, dependencies=dependencies)
