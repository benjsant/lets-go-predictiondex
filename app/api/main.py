"""
Pokémon Let's Go API - Application entry point
==============================================

This module defines the FastAPI application instance and registers
all API routers.

It serves as the main entry point of the Pokémon Let's Go API and
is responsible for:
- Initializing the FastAPI application
- Setting global API metadata (title, description, etc.)
- Registering all route modules with their respective prefixes and tags

The actual business logic and database access are handled in dedicated
service and model layers.
"""

from fastapi import FastAPI

from app.api.routes import (
    pokemon_route,
    moves_route,
)

app = FastAPI(title="Pokémon Let's Go API")

app.include_router(
    pokemon_route.router,
    prefix="/pokemon",
    tags=["Pokemon"],
)

app.include_router(
    moves_route.router,
    prefix="/moves",
    tags=["Moves"],
)
