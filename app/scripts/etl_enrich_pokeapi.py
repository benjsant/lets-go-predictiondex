"""
ETL – Pokémon Reference Data Enrichment from PokeAPI (Pokémon Let's Go)

Overview
--------
This script enriches an existing Pokémon reference database using data
retrieved from the public PokeAPI.

It complements previously ingested CSV-based reference data by adding:
- base combat statistics (HP, Attack, Defense, etc.)
- physical attributes (height, weight)
- sprite URLs

Important Constraints
---------------------
- This script DOES NOT create new Pokémon entities.
- Only Pokémon records already present in the database are enriched.
- CSV ingestion remains the authoritative source of Pokémon identity data.

This separation guarantees:
- deterministic and reproducible ingestion (CSV-based)
- optional enrichment from external APIs
- isolation of failures related to third-party services

Competency Scope (E1)
---------------------
This script is part of competency block E1 and demonstrates:
- extraction from an external REST API
- controlled data transformation
- enrichment of relational database records
- transactional consistency
- basic parallelism for I/O-bound tasks

The use of local multithreading is intentional and limited.
No orchestration framework, message queue, or scheduler is required
for E1 validation.

Execution Context
-----------------
This script must be executed after:
- database schema initialization
- CSV-based data loading

It can be re-executed safely without creating duplicate records.

Usage
-----
python app/scripts/etl_enrich_pokeapi.py
"""

import time
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from app.db.session import SessionLocal
from app.models import Pokemon, PokemonStat
from app.db.guards.pokemon import upsert_pokemon


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

MAX_WORKERS = 10
REQUEST_DELAY = 0.05

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

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{}"


# ---------------------------------------------------------------------
# API Extraction
# ---------------------------------------------------------------------
def get_pokemon_data(name: str, retries: int = 3, delay: int = 2):
    """
    Retrieve Pokémon data from PokeAPI.

    This function queries the PokeAPI for a given Pokémon name and extracts
    a subset of useful attributes used for enrichment.

    Parameters
    ----------
    name : str
        Pokémon identifier used by PokeAPI.
    retries : int, optional
        Number of retry attempts in case of request failure.
    delay : int, optional
        Delay (in seconds) between retry attempts.

    Returns
    -------
    dict | None
        A dictionary containing base stats, physical attributes, and sprite URL,
        or None if the data could not be retrieved.
    """
    url = POKEAPI_URL.format(name.lower())

    for _ in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                payload = resp.json()

                stats = {
                    s["stat"]["name"]: s["base_stat"]
                    for s in payload["stats"]
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

            print(f"⚠ {name}: HTTP {resp.status_code}")

        except requests.RequestException as exc:
            print(f"⚠ {name}: {exc}")

        time.sleep(delay)

    return None


# ---------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------
def process_pokemon(pokemon_id: int):
    """
    Enrich a single Pokémon record using PokeAPI data.

    This function:
    - retrieves an existing Pokémon entity
    - fetches enrichment data from PokeAPI
    - updates physical attributes and sprite
    - upserts the associated base statistics

    A dedicated database session is created for isolation and
    transactional safety.

    Parameters
    ----------
    pokemon_id : int
        Primary key of the Pokémon record to enrich.

    Returns
    -------
    str | None
        Pokémon PokeAPI name if enrichment succeeded, otherwise None.
    """
    session = SessionLocal()

    try:
        pokemon = session.get(Pokemon, pokemon_id)
        if not pokemon or not pokemon.name_pokeapi:
            return None

        data = get_pokemon_data(pokemon.name_pokeapi)
        if not data:
            print(f"❌ {pokemon.name_pokeapi} non récupéré")
            return None

        poke = upsert_pokemon(
            session,
            species_id=pokemon.species_id,
            form_name=pokemon.form_name,
            name_pokeapi=pokemon.name_pokeapi,
            name_pokepedia=pokemon.name_pokepedia,
            is_mega=pokemon.is_mega,
            is_alola=pokemon.is_alola,
            is_starter=pokemon.is_starter,
        )

        poke.height_m = data["height_m"]
        poke.weight_kg = data["weight_kg"]

        key = poke.name_pokeapi.lower()
        if poke.is_starter and key in BASE_SPRITES:
            poke.sprite_url = BASE_SPRITES[key]
        else:
            poke.sprite_url = data["sprite_url"]

        stats = (
            session.query(PokemonStat)
            .filter(PokemonStat.pokemon_id == poke.id)
            .one_or_none()
        )

        if not stats:
            stats = PokemonStat(pokemon_id=poke.id)
            session.add(stats)

        stats.hp = data["hp"]
        stats.attack = data["attack"]
        stats.defense = data["defense"]
        stats.sp_attack = data["sp_attack"]
        stats.sp_defense = data["sp_defense"]
        stats.speed = data["speed"]

        session.commit()
        print(f"✔ {poke.name_pokeapi} enrichi")

        return poke.name_pokeapi

    except Exception as exc:
        session.rollback()
        print(f"💥 Erreur {pokemon_id}: {exc}")
        return None

    finally:
        session.close()


# ---------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------
def main():
    """
    Execute the PokeAPI enrichment pipeline.

    This function:
    - retrieves all Pokémon IDs from the database
    - processes them in parallel using a thread pool
    - aggregates enrichment results

    Failures affecting individual Pokémon do not interrupt
    the global execution.
    """
    session = SessionLocal()
    try:
        pokemon_ids = [p.id for p in session.query(Pokemon.id).all()]
    finally:
        session.close()

    print(f"➡ {len(pokemon_ids)} Pokémon à enrichir via PokéAPI")

    updated = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_pokemon, pid)
            for pid in pokemon_ids
        ]

        for future in as_completed(futures):
            if future.result():
                updated += 1

    print(f"✅ PokéAPI terminé : {updated} Pokémon enrichis")


if __name__ == "__main__":
    main()
