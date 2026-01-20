# app/main.py

from fastapi import FastAPI

from api_pokemon.routes import (
    pokemon_route,
    moves_route,
    type_route,
)

app = FastAPI(
    title="Pokémon Let's Go API",
    description="REST API for Pokémon Let's Go Pikachu / Eevee",
    version="1.0.0",
)

@app.get("/health", tags=["health"])
def healthcheck():
    return {"status": "ok"}

app.include_router(pokemon_route.router)
app.include_router(moves_route.router)
app.include_router(type_route.router)
