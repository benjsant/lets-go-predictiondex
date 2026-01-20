#app/api/main.py
from fastapi import FastAPI

from app.api.routes import (
    pokemon_route,
    moves_route,
)

app = FastAPI(title="Pokémon Let's Go API")

app.include_router(pokemon_route.router, prefix="/pokemon", tags=["Pokemon"])
app.include_router(moves_route.router, prefix="/moves", tags=["Moves"])

