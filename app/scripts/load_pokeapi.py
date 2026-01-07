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
BASE_SPRITES = {
    "pikachu-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
    "eevee-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/133.png",
}

# ----------------------------------
# PokéAPI
# ----------------------------------
def get_pokemon_data(name: str, retries=3, delay=2):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    for _ in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                p = resp.json()
                stats = {s["stat"]["name"]: s["base_stat"] for s in p["stats"]}
                time.sleep(0.05)
                return {
                    "hp": stats.get("hp"),
                    "attack": stats.get("attack"),
                    "defense": stats.get("defense"),
                    "sp_attack": stats.get("special-attack"),
                    "sp_defense": stats.get("special-defense"),
                    "speed": stats.get("speed"),
                    "height_m": Decimal(p["height"]) / 10,
                    "weight_kg": Decimal(p["weight"]) / 10,
                    "sprite_url": p["sprites"]["front_default"],
                }
        except requests.RequestException as e:
            print(f"⚠ {name}: {e}")
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

        # Sprite override pour starters partenaires
        key = pokemon.nom_pokeapi.lower()
        if pokemon.is_starter and key in BASE_SPRITES:
            data["sprite_url"] = BASE_SPRITES[key]

        # 🔒 Pokémon via guard
        upsert_pokemon(
            session,
            species_id=pokemon.species_id,
            form_name=pokemon.form_name,
            nom_pokeapi=pokemon.nom_pokeapi,
            nom_pokepedia=pokemon.nom_pokepedia,
            is_mega=pokemon.is_mega,
            is_alola=pokemon.is_alola,
            is_starter=pokemon.is_starter,
            height_m=data["height_m"],
            weight_kg=data["weight_kg"],
            sprite_url=data["sprite_url"],
        )

        # 🔒 Stats (upsert simple, 1–1)
        stats = session.query(PokemonStat).filter(
            PokemonStat.pokemon_id == pokemon.id
        ).one_or_none()

        if not stats:
            stats = PokemonStat(pokemon_id=pokemon.id)
            session.add(stats)

        stats.hp = data["hp"]
        stats.attack = data["attack"]
        stats.defense = data["defense"]
        stats.sp_attack = data["sp_attack"]
        stats.sp_defense = data["sp_defense"]
        stats.speed = data["speed"]

        session.commit()
        print(f"✔ {pokemon.nom_pokeapi} enrichi")
        return pokemon.nom_pokeapi

    finally:
        session.close()

# ----------------------------------
# Main
# ----------------------------------
def main():
    session = SessionLocal()
    try:
        pokemon_ids = [
            p.id for p in session.query(Pokemon.id).all()
        ]
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
