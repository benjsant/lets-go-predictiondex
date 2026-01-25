# app/main.py

from fastapi import FastAPI
from fastapi.responses import Response

from api_pokemon.routes import (
    pokemon_route,
    moves_route,
    type_route,
    prediction_route,
)
from api_pokemon.monitoring.metrics import metrics_middleware, get_metrics

app = FastAPI(
    title="Pokémon Let's Go API",
    description="REST API for Pokémon Let's Go Pikachu / Eevee with ML-powered battle predictions",
    version="1.1.0",
)

# Add Prometheus metrics middleware
metrics_middleware(app)

@app.get("/health", tags=["health"])
def healthcheck():
    return {"status": "healthy"}

@app.get("/metrics", tags=["monitoring"])
def metrics() -> Response:
    """
    Prometheus metrics endpoint.
    
    Exposes metrics for:
    - API request count, latency, errors
    - Model prediction count, latency, confidence
    - System resource usage
    """
    return get_metrics()

app.include_router(pokemon_route.router)
app.include_router(moves_route.router)
app.include_router(type_route.router)
app.include_router(prediction_route.router)
