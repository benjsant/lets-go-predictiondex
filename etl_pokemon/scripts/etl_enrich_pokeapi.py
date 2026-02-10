"""
ETL – Pokémon Reference Data Enrichment from PokeAPI (Pokémon Let's Go)

This script enriches existing Pokémon records with reference data fetched
from the PokeAPI:
- Base combat statistics (HP, Attack, Defense, etc.)
- Physical attributes (height, weight)
- Sprite URLs (with overrides for starter Pokémon)

Constraints:
- Never creates new Pokémon entities
- Only updates existing Pokémon
- Idempotent and re-runnable
- Threaded for I/O-bound API calls

Execution:
- Must be executed after database initialization and CSV ingestion
- Competency Block: E1
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from typing import Optional

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
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------
MAX_WORKERS = 10
REQUEST_DELAY = 0.05  # Delay between API requests to reduce rate-limiting
REQUEST_TIMEOUT = 10
RETRY_DELAY = 2
MAX_RETRIES = 3

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{}"

BASE_SPRITES = {
    "pikachu-starter": (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        "sprites/pokemon/25.png"
    ),
    "eevee-starter": (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        "sprites/pokemon/133.png"
    ),
}

# ---------------------------------------------------------------------
# PokeAPI extraction
# ---------------------------------------------------------------------


def get_pokemon_data(name: str) -> Optional[dict]:
    """
    Retrieve and normalize Pokémon reference data from PokeAPI.

    Args:
        name: Pokémon name as referenced by PokeAPI.

    Returns:
        A dictionary containing base stats, physical attributes and sprite URL,
        or None if the data could not be retrieved after retries.
    """
    url = POKEAPI_URL.format(name.lower())

    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                payload = response.json()
                stats = {
                    stat["stat"]["name"]: stat["base_stat"]
                    for stat in payload["stats"]
                }

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

            LOGGER.warning("%s: HTTP %s", name, response.status_code)

        except requests.RequestException as exc:
            LOGGER.warning("%s: request failed (%s)", name, exc)

        time.sleep(RETRY_DELAY)

    return None

# ---------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------


def process_pokemon(pokemon_id: int, starter_form_id: int) -> Optional[str]:
    """
    Enrich a single Pokémon record using data from PokeAPI.

    Args:
        pokemon_id: Primary key of the Pokémon to enrich.
        starter_form_id: Database ID corresponding to the starter form.

    Returns:
        The Pokémon PokeAPI name if enrichment succeeded, otherwise None.
    """
    session: Session = SessionLocal()

    try:
        pokemon = session.get(Pokemon, pokemon_id)
        if pokemon is None or not pokemon.name_pokeapi:
            return None

        data = get_pokemon_data(pokemon.name_pokeapi)
        if data is None:
            LOGGER.error("❌ Failed to retrieve %s", pokemon.name_pokeapi)
            return None

        # Update physical attributes
        pokemon.height_m = data["height_m"]
        pokemon.weight_kg = data["weight_kg"]

        # Sprite override for starter forms
        if pokemon.form_id == starter_form_id:
            sprite_key = pokemon.name_pokeapi.lower()
            pokemon.sprite_url = BASE_SPRITES.get(
                sprite_key,
                data["sprite_url"],
            )
        else:
            pokemon.sprite_url = data["sprite_url"]

        # Upsert base combat stats
        upsert_pokemon_stats(
            session=session,
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
        LOGGER.info("✔ %s enriched", pokemon.name_pokeapi)
        return pokemon.name_pokeapi

    except Exception as exc:  # pylint: disable=broad-except
        session.rollback()
        LOGGER.error("💥 Error while processing Pokémon %s: %s", pokemon_id, exc)
        return None

    finally:
        session.close()

# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------


def main() -> None:
    """
    Execute the PokeAPI enrichment process for all Pokémon in the database.
    """
    session: Session = SessionLocal()
    try:
        pokemon_ids = [row.id for row in session.query(Pokemon.id).all()]
        starter_form_id = (
            session.query(Form.id)
            .filter_by(name="starter")
            .scalar()
        )

        if starter_form_id is None:
            raise RuntimeError("Starter form not found in database")

    finally:
        session.close()

    LOGGER.info("➡ %s Pokémon to enrich via PokeAPI", len(pokemon_ids))

    updated = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = (
            executor.submit(process_pokemon, pid, starter_form_id)
            for pid in pokemon_ids
        )

        for future in as_completed(futures):
            if future.result() is not None:
                updated += 1

    LOGGER.info("✅ PokeAPI enrichment completed: %s Pokémon enriched", updated)


if __name__ == "__main__":
    main()
