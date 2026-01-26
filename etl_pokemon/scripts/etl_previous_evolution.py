#!/usr/bin/env python3
"""
ETL – Pokémon Move Inheritance from Previous Evolutions (Threaded Version)

OBJECTIF
--------
- Hériter les capacités des évolutions précédentes (ex: Reptincel → Salamèche)
- learn_level = -2
- learn_method = 'before_evolution'

RÈGLES MÉTIER
------------
- ✅ Traite toutes les formes : Base, Alola, Starter
- ❌ Exclut UNIQUEMENT les formes Mega
- ✅ Les Mega sont gérées par un autre script ETL dédié
- ✅ Gestion spéciale Alola : cherche l'évolution précédente dans les 2 variantes
  Exemple: Rattatac Alola hérite de Rattata Alola ET Rattata Base
- ✅ Upsert idempotent dans PokemonMove
- ✅ Appels PokeAPI threadés
- ✅ Évite les doublons : ne copie que les moves non possédés
"""

import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from core.db.session import SessionLocal
from core.models import Pokemon, Move, LearnMethod, PokemonMove

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
POKEAPI_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/{}"
REQUEST_DELAY = 0.05
MAX_RETRIES = 3
MAX_WORKERS = 10

# IDs des formes à traiter (exclut Mega uniquement)
BASE_FORM_ID = 1
ALOLA_FORM_ID = 3
STARTER_FORM_ID = 4
INCLUDED_FORM_IDS = [BASE_FORM_ID, ALOLA_FORM_ID, STARTER_FORM_ID]

# ---------------------------------------------------------------------
# Helpers – PokeAPI
# ---------------------------------------------------------------------
def get_species_data(name_or_id: str) -> dict | None:
    """Retrieve species data from PokeAPI with retries."""
    for _ in range(MAX_RETRIES):
        try:
            resp = requests.get(
                POKEAPI_SPECIES_URL.format(name_or_id),
                timeout=10
            )
            if resp.status_code == 200:
                time.sleep(REQUEST_DELAY)
                return resp.json()
            logger.warning(
                "HTTP %s while fetching species %s",
                resp.status_code,
                name_or_id
            )
        except requests.RequestException as exc:
            logger.warning(
                "Request failed for species %s: %s",
                name_or_id,
                exc
            )
        time.sleep(1)
    return None

def walk_chain_for_previous(
    chain: dict,
    target_name: str,
    previous_names: list[str]
) -> bool:
    """
    Walk evolution chain recursively and collect all previous evolutions.
    Returns True if target_name is found in current node or descendants.
    """
    if chain["species"]["name"] == target_name:
        return True

    for evo in chain.get("evolves_to", []):
        if walk_chain_for_previous(evo, target_name, previous_names):
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
    move_cache: dict[str, int],
    before_evo_lm_id: int,
) -> int:
    """
    Thread worker:
    - Fetch evolution chain
    - Find previous evolutions
    - Inherit their moves, sans doublons
    - Gère les formes Alola en cherchant les deux variantes (base et alola)
    """
    session: Session = SessionLocal()
    inherited_count = 0

    try:
        pokemon = session.get(Pokemon, pokemon_id)
        if not pokemon or not name_pokeapi:
            return 0

        # Cache moves déjà possédés pour éviter doublons
        existing_moves = {pm.move.name.lower() for pm in pokemon.moves}

        # Pour les formes Alola, extraire le nom de base pour PokeAPI
        # Ex: "rattata-alola" → chercher species "rattata"
        species_name = name_pokeapi.replace("-alola", "").replace("-starter", "")
        
        species_data = get_species_data(species_name)
        if not species_data or not species_data.get("evolution_chain"):
            return 0

        evo_chain_url = species_data["evolution_chain"]["url"]
        try:
            resp = requests.get(evo_chain_url, timeout=10)
            resp.raise_for_status()
            chain_data = resp.json()["chain"]
        except Exception as exc:
            logger.warning(
                "Cannot fetch evolution chain for %s: %s",
                species_name,
                exc
            )
            return 0

        previous_names: list[str] = []
        walk_chain_for_previous(chain_data, species_name, previous_names)
        if not previous_names:
            return 0

        # Héritage des moves des évolutions précédentes
        for prev_name in previous_names:
            # Pour les formes Alola/Starter, chercher AUSSI la forme correspondante
            # Ex: Si on traite "rattata-alola", chercher "rattata-alola" ET "rattata"
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
                if not base_pokemon:
                    continue

                for pm in base_pokemon.moves:
                    move_name = pm.move.name.lower()
                    if move_name in existing_moves:
                        continue  # Ignorer les doublons
                    move_id = move_cache.get(move_name)
                    if not move_id:
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
                            ]
                        )
                    )
                    session.execute(stmt)
                    inherited_count += 1
                    existing_moves.add(move_name)

        session.commit()
        if inherited_count:
            logger.info(
                "✔ %s inherited %d moves from previous evolutions",
                name_pokeapi,
                inherited_count
            )
        return inherited_count

    except Exception as exc:
        session.rollback()
        logger.error("💥 Error for %s: %s", name_pokeapi, exc)
        return 0

    finally:
        session.close()

# ---------------------------------------------------------------------
# Main ETL
# ---------------------------------------------------------------------
def inherit_previous_evolution_moves_threaded():
    """
    Main ETL entrypoint.
    Traite toutes les formes sauf Mega (Base, Alola, Starter)
    """
    session: Session = SessionLocal()
    try:
        # Cache des méthodes d'apprentissage
        learn_method_cache = {
            lm.name: lm.id
            for lm in session.execute(select(LearnMethod)).scalars()
        }
        before_evo_lm_id = learn_method_cache.get("before_evolution")
        if not before_evo_lm_id:
            raise RuntimeError("LearnMethod 'before_evolution' not found")

        # Cache des moves
        move_cache = {
            m.name.lower(): m.id
            for m in session.execute(select(Move)).scalars()
        }

        pokemons = (
            session.query(Pokemon.id, Pokemon.name_pokeapi, Pokemon.form_id)
            .filter(Pokemon.form_id.in_(INCLUDED_FORM_IDS))
            .all()
        )
    finally:
        session.close()

    logger.info(
        "➡ %d Pokémon to process (formes: Base, Alola, Starter)",
        len(pokemons)
    )

    total_inherited = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                process_pokemon_moves,
                pid,
                name,
                form_id,
                move_cache,
                before_evo_lm_id
            )
            for pid, name, form_id in pokemons
        ]
        for future in as_completed(futures):
            total_inherited += future.result() or 0

    logger.info(
        "✅ Previous evolution move inheritance completed: %d moves inherited",
        total_inherited
    )

# ---------------------------------------------------------------------
if __name__ == "__main__":
    inherit_previous_evolution_moves_threaded()
