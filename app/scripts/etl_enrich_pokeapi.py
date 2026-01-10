#app/scripts/etl_enrich_pokeapi.py
import time
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from app.db.session import SessionLocal
from app.models import Pokemon, PokemonStat
from app.db.guards.pokemon import upsert_pokemon

# ----------------------------------
# Config
# ----------------------------------
MAX_WORKERS = 10
REQUEST_DELAY = 0.05

BASE_SPRITES = {
    "pikachu-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
    "eevee-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/133.png",
}

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{}"

# ----------------------------------
# PokéAPI
# ----------------------------------
def get_pokemon_data(name: str, retries: int = 3, delay: int = 2):
    """Récupère stats, taille, poids et sprite depuis PokéAPI"""
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

# ----------------------------------
# Worker
# ----------------------------------
def process_pokemon(pokemon_id: int):
    session = SessionLocal()

    try:
        pokemon = session.get(Pokemon, pokemon_id)
        if not pokemon or not pokemon.nom_pokeapi:
            return None

        data = get_pokemon_data(pokemon.nom_pokeapi)
        if not data:
            print(f"❌ {pokemon.nom_pokeapi} non récupéré")
            return None

        # -------------------------
        # Pokémon (structure)
        # -------------------------
        poke = upsert_pokemon(
            session,
            species_id=pokemon.species_id,
            form_name=pokemon.form_name,
            nom_pokeapi=pokemon.nom_pokeapi,
            nom_pokepedia=pokemon.nom_pokepedia,
            is_mega=pokemon.is_mega,
            is_alola=pokemon.is_alola,
            is_starter=pokemon.is_starter,
        )

        # -------------------------
        # Enrichissement dimensions
        # -------------------------
        poke.height_m = data["height_m"]
        poke.weight_kg = data["weight_kg"]

        # Sprite (override pour starters partenaires)
        key = poke.nom_pokeapi.lower()
        if poke.is_starter and key in BASE_SPRITES:
            poke.sprite_url = BASE_SPRITES[key]
        else:
            poke.sprite_url = data["sprite_url"]

        # -------------------------
        # Stats (1–1)
        # -------------------------
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
        print(f"✔ {poke.nom_pokeapi} enrichi")

        return poke.nom_pokeapi

    except Exception as exc:
        session.rollback()
        print(f"💥 Erreur {pokemon_id}: {exc}")
        return None

    finally:
        session.close()

# ----------------------------------
# Main
# ----------------------------------
def main():
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
