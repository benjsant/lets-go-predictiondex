"""
ETL – Pokémon Move Inheritance from Previous Evolutions (Threaded Version)

This ETL script inherits moves from previous evolutions:
- Example: Charmeleon inherits moves from Charmander
- learn_level is set to -2
- learn_method is 'before_evolution'

Business rules:
- Process Base, Alola and Starter forms
- Exclude Mega forms only (handled by a dedicated ETL)
- Alola forms inherit from both Base and Alola previous evolutions
- Idempotent upsert into PokemonMove
- Avoid duplicates (only missing moves are copied)
- Threaded PokeAPI calls
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

import requests
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from core.db.session import SessionLocal
from core.models import LearnMethod, Move, Pokemon, PokemonMove

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
POKEAPI_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/{}"
REQUEST_DELAY = 0.05
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
MAX_WORKERS = 10

# Form IDs (exclude Mega only)
BASE_FORM_ID = 1
ALOLA_FORM_ID = 3
STARTER_FORM_ID = 4

INCLUDED_FORM_IDS = [
    BASE_FORM_ID,
    ALOLA_FORM_ID,
    STARTER_FORM_ID,
]

# ---------------------------------------------------------------------
# Helpers – PokeAPI
# ---------------------------------------------------------------------


def get_species_data(name_or_id: str) -> Optional[dict]:
    """
    Retrieve Pokémon species data from PokeAPI with retries.

    Args:
        name_or_id: Pokémon species name or ID.

    Returns:
        Parsed JSON response or None if retrieval fails.
    """
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(
                POKEAPI_SPECIES_URL.format(name_or_id),
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 200:
                time.sleep(REQUEST_DELAY)
                return response.json()

            LOGGER.warning(
                "HTTP %s while fetching species %s",
                response.status_code,
                name_or_id,
            )

        except requests.RequestException as exc:
            LOGGER.warning(
                "Request failed for species %s: %s",
                name_or_id,
                exc,
            )

        time.sleep(1)

    return None


def walk_chain_for_previous(
    chain: dict,
    target_name: str,
    previous_names: List[str],
) -> bool:
    """
    Walk the evolution chain recursively to collect previous evolutions.

    Args:
        chain: Current evolution chain node.
        target_name: Pokémon name to locate.
        previous_names: List populated with previous evolution names.

    Returns:
        True if target_name is found in this branch, False otherwise.
    """
    if chain["species"]["name"] == target_name:
        return True

    for evolution in chain.get("evolves_to", []):
        if walk_chain_for_previous(evolution, target_name, previous_names):
            previous_names.append(chain["species"]["name"])
            return True

    return False

# ---------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------


def process_pokemon_moves(
    pokemon_id: int,
    name_pokeapi: str,
    form_id: int,
    move_cache: Dict[str, int],
    before_evo_lm_id: int,
) -> int:
    """
    Thread worker to inherit moves from previous evolutions.

    Steps:
    - Fetch evolution chain
    - Identify previous evolutions
    - Inherit missing moves only
    - Handle Base / Alola / Starter forms properly

    Args:
        pokemon_id: Pokémon database ID.
        name_pokeapi: Pokémon PokeAPI name.
        form_id: Pokémon form ID.
        move_cache: Cached mapping of move name → move ID.
        before_evo_lm_id: LearnMethod ID for 'before_evolution'.

    Returns:
        Number of inherited moves.
    """
    session: Session = SessionLocal()
    inherited_count = 0

    try:
        pokemon = session.get(Pokemon, pokemon_id)
        if pokemon is None or not name_pokeapi:
            return 0

        existing_moves = {
            pokemon_move.move.name.lower()
            for pokemon_move in pokemon.moves
        }

        # Normalize species name for PokeAPI
        species_name = (
            name_pokeapi
            .replace("-alola", "")
            .replace("-starter", "")
        )

        species_data = get_species_data(species_name)
        if not species_data or not species_data.get("evolution_chain"):
            return 0

        try:
            response = requests.get(
                species_data["evolution_chain"]["url"],
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            chain_data = response.json()["chain"]
        except requests.RequestException as exc:
            LOGGER.warning(
                "Cannot fetch evolution chain for %s: %s",
                species_name,
                exc,
            )
            return 0

        previous_names: List[str] = []
        walk_chain_for_previous(chain_data, species_name, previous_names)

        if not previous_names:
            return 0

        for prev_name in previous_names:
            candidates = [prev_name]

            if form_id == ALOLA_FORM_ID:
                candidates.append(f"{prev_name}-alola")
            elif form_id == STARTER_FORM_ID:
                candidates.append(f"{prev_name}-starter")

            for candidate_name in candidates:
                base_pokemon = (
                    session.query(Pokemon)
                    .filter(Pokemon.name_pokeapi == candidate_name)
                    .first()
                )
                if base_pokemon is None:
                    continue

                for pokemon_move in base_pokemon.moves:
                    move_name = pokemon_move.move.name.lower()
                    if move_name in existing_moves:
                        continue

                    move_id = move_cache.get(move_name)
                    if move_id is None:
                        continue

                    stmt = (
                        insert(PokemonMove)
                        .values(
                            pokemon_id=pokemon.id,
                            move_id=move_id,
                            learn_method_id=before_evo_lm_id,
                            learn_level=-2,
                        )
                        .on_conflict_do_nothing(
                            index_elements=[
                                "pokemon_id",
                                "move_id",
                                "learn_method_id",
                            ],
                        )
                    )

                    session.execute(stmt)
                    inherited_count += 1
                    existing_moves.add(move_name)

        session.commit()

        if inherited_count:
            LOGGER.info(
                " %s inherited %d moves from previous evolutions",
                name_pokeapi,
                inherited_count,
            )

        return inherited_count

    except Exception as exc: # pylint: disable=broad-except
        session.rollback()
        LOGGER.error(" Error for %s: %s", name_pokeapi, exc)
        return 0

    finally:
        session.close()

# ---------------------------------------------------------------------
# Main ETL
# ---------------------------------------------------------------------


def inherit_previous_evolution_moves_threaded() -> None:
    """
    Main ETL entry point.

    Processes all Base, Alola and Starter Pokémon
    and inherits moves from previous evolutions.
    """
    session: Session = SessionLocal()

    try:
        learn_method_cache = {
            lm.name: lm.id
            for lm in session.execute(select(LearnMethod)).scalars()
        }
        before_evo_lm_id = learn_method_cache.get("before_evolution")
        if before_evo_lm_id is None:
            raise RuntimeError("LearnMethod 'before_evolution' not found")

        move_cache = {
            move.name.lower(): move.id
            for move in session.execute(select(Move)).scalars()
        }

        pokemons = (
            session.query(
                Pokemon.id,
                Pokemon.name_pokeapi,
                Pokemon.form_id,
            )
            .filter(Pokemon.form_id.in_(INCLUDED_FORM_IDS))
            .all()
        )

    finally:
        session.close()

    LOGGER.info(
        " %d Pokémon to process (Base, Alola, Starter forms)",
        len(pokemons),
    )

    total_inherited = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = (
            executor.submit(
                process_pokemon_moves,
                pokemon_id,
                name,
                form_id,
                move_cache,
                before_evo_lm_id,
            )
            for pokemon_id, name, form_id in pokemons
        )

        for future in as_completed(futures):
            total_inherited += future.result() or 0

    LOGGER.info(
        "Previous evolution move inheritance completed: %d moves inherited",
        total_inherited,
    )


if __name__ == "__main__":
    inherit_previous_evolution_moves_threaded()
