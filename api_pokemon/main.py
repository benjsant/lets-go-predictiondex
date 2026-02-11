"""FastAPI application entry point for the PredictionDex API."""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.responses import Response

from api_pokemon.middleware.security import verify_api_key
from api_pokemon.monitoring.metrics import get_metrics, metrics_middleware
from api_pokemon.routes import (
    moves_route,
    pokemon_route,
    prediction_route,
    type_route,
)

# Check if API Key is required (in production)
API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - preload ML model at startup."""
    print("[API] Startup: Preloading ML model...")
    from api_pokemon.services.prediction_service import prediction_model
    try:
        prediction_model.load()
        print("[API] ML model preloaded successfully")
    except Exception as e:
        print(f"[API] Warning: Failed to preload ML model: {e}")
        print("       Model will be loaded on first prediction request")
    yield
    # Cleanup on shutdown (if needed in the future)


app = FastAPI(
    title="Pokémon Let's Go PredictionDex API",
    description="""
## REST API for Pokémon Let's Go Pikachu / Eevee

### Features
- **Pokémon Database**: Complete Gen 1 data (151 Pokémon + forms)
- **Move Database**: All moves with stats and type effectiveness
- **ML Predictions**: Battle winner prediction (94.24% accuracy)
- **Monitoring**: Prometheus metrics + drift detection
- **Security**: API Key authentication

### Authentication
Most endpoints require an API Key in the `X-API-Key` header.

**Public endpoints** (no auth required):
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /docs` - This Swagger documentation
- `GET /redoc` - ReDoc documentation

### ML Model
- **Model**: XGBoost Classifier
- **Accuracy**: 94.24%
- **Features**: 133 (stats, types, moves, STAB, effectiveness)
- **Training**: 718,889 battles (3 scenarios)
- **Registry**: MLflow Model Registry

### Example Usage
```bash
# Get all Pokémon
curl -H "X-API-Key: YOUR_KEY" http://localhost:8080/pokemon/

# Predict best move
curl -X POST http://localhost:8080/predict/best-move \\
  -H "X-API-Key: YOUR_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "pokemon_a_id": 25,
    "pokemon_b_id": 1,
    "available_moves": ["Fatal-Foudre", "Vive-Attaque"]
  }'
```
    """,
    version="2.0.0",
    contact={
        "name": "PredictionDex Team",
        "url": "https://github.com/yourusername/lets-go-predictiondex",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
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


# Make Swagger UI and ReDoc accessible without API Key (for internal Docker network)
if API_KEY_REQUIRED:
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """Swagger UI - accessible without API Key from Docker network"""
        from fastapi.openapi.docs import get_swagger_ui_html
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
        )

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        """ReDoc - accessible without API Key from Docker network"""
        from fastapi.openapi.docs import get_redoc_html
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
        )

    @app.get("/openapi.json", include_in_schema=False)
    async def get_open_api_endpoint():
        """OpenAPI schema - accessible without API Key"""
        from fastapi.openapi.utils import get_openapi
        return get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )


# Protected routes requiring API Key (if API_KEY_REQUIRED=true)
dependencies = [Depends(verify_api_key)] if API_KEY_REQUIRED else []

app.include_router(pokemon_route.router, dependencies=dependencies)
app.include_router(moves_route.router, dependencies=dependencies)
app.include_router(type_route.router, dependencies=dependencies)
app.include_router(prediction_route.router, dependencies=dependencies)
