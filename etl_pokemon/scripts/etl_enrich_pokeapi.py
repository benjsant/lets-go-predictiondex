"""
ETL – Pokémon Reference Data Enrichment from PokeAPI (Pokémon Let's Go)

This script enriches existing Pokémon records with reference data from PokeAPI:
- Base combat statistics (HP, Attack, Defense, etc.)
- Physical attributes (height, weight)
- Sprite URLs (starter-specific overrides)

Constraints:
- Never creates new Pokémon entities
- Only updates existing Pokémon
- Idempotent and re-runnable
- Threaded for I/O-bound API calls

Execution:
- Must run after DB initialization and CSV-based ingestion
- Competency Block: E1
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import requests
from sqlalchemy.orm import Session

from core.db.guards.pokemon_stats import upsert_pokemon_stats
from core.db.session import SessionLocal
from core.models import Form, Pokemon

# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
MAX_WORKERS = 10
REQUEST_DELAY = 0.05  # Delay between API requests to avoid rate-limiting

BASE_SPRITES = {
    "pikachu-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
    "eevee-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/133.png",
}

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{}"

# ---------------------------------------------------------------------
# PokeAPI Extraction
# ---------------------------------------------------------------------


def get_pokemon_data(name: str, retries: int = 3, delay: int = 2) -> dict | None:
    """Retrieve Pokémon data from PokeAPI."""
    url = POKEAPI_URL.format(name.lower())
    for _ in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                payload = resp.json()
                stats = {s["stat"]["name"]: s["base_stat"] for s in payload["stats"]}
                time.sleep(REQUEST_DELAY)
                return {
                    "hp": stats.get("hp"),
                    "attack": stats.get("attack"),
                    "defense": stats.get("defense"),
                    "sp_attack": stats.get("special-attack"),
                    "sp_defense": stats.get("special-defense"),
                    "speed": stats.get("speed"),
                    "height_m": Decimal(payload["height"]) / 10,
                    "weight_kg": Decimal(payload["weight"]) / 10,
                    "sprite_url": payload["sprites"]["front_default"],
                }
            logger.warning("%s: HTTP %s", name, resp.status_code)
        except requests.RequestException as exc:
            logger.warning("%s: %s", name, exc)
        time.sleep(delay)
    return None

# ---------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------


def process_pokemon(pokemon_id: int, starter_form_id: int) -> str | None:
    """Enrich a single Pokémon record using PokeAPI data."""
    session: Session = SessionLocal()
    try:
        pokemon = session.get(Pokemon, pokemon_id)
        if not pokemon or not pokemon.name_pokeapi:
            return None

        data = get_pokemon_data(pokemon.name_pokeapi)
        if not data:
            logger.error("❌ %s not retrieved", pokemon.name_pokeapi)
            return None

        # Update physical attributes
        pokemon.height_m = data["height_m"]
        pokemon.weight_kg = data["weight_kg"]

        # Sprite override for starter forms
        if pokemon.form_id == starter_form_id:
            key = pokemon.name_pokeapi.lower()
            pokemon.sprite_url = BASE_SPRITES.get(key, data["sprite_url"])
        else:
            pokemon.sprite_url = data["sprite_url"]

        # Upsert base stats
        upsert_pokemon_stats(
            session,
            pokemon_id=pokemon.id,
            hp=data["hp"],
            attack=data["attack"],
            defense=data["defense"],
            sp_attack=data["sp_attack"],
            sp_defense=data["sp_defense"],
            speed=data["speed"],
            auto_commit=False,
        )

        session.commit()
        logger.info("✔ %s enriched", pokemon.name_pokeapi)
        return pokemon.name_pokeapi

    except Exception as exc:
        session.rollback()
        logger.error("💥 Error %s: %s", pokemon_id, exc)
        return None
    finally:
        session.close()

# ---------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------


def main():
    """Execute PokeAPI enrichment for all Pokémon."""
    session: Session = SessionLocal()
    try:
        pokemon_ids = [p.id for p in session.query(Pokemon.id).all()]
        starter_form_id = session.query(Form.id).filter_by(name="starter").scalar()
        if starter_form_id is None:
            raise RuntimeError("Starter form not found in database")
    finally:
        session.close()

    logger.info("➡ %s Pokémon to enrich via PokeAPI", len(pokemon_ids))
    updated = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_pokemon, pid, starter_form_id) for pid in pokemon_ids]
        for future in as_completed(futures):
            if future.result():
                updated += 1

    logger.info("✅ PokeAPI enrichment completed: %s Pokémon enriched", updated)


# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()
