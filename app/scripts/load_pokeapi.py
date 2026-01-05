import time
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from app.db.session import SessionLocal
from app.models import Pokemon, PokemonStat

# ----------------------------------
# Config
# ----------------------------------
MAX_WORKERS = 10  # on peut augmenter pour la vitesse
BASE_SPRITES = {
    "pikachu-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
    "eevee-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/133.png",
}

# ----------------------------------
# PokéAPI
# ----------------------------------
def get_pokemon_data(name: str, retries=3, delay=2):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                p = resp.json()
                stats = {s["stat"]["name"]: s["base_stat"] for s in p["stats"]}
                time.sleep(0.05)  # petit délai pour ne pas spammer l'API
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
            else:
                print(f"⚠ {name}: HTTP {resp.status_code}")
        except requests.RequestException as e:
            print(f"⚠ {name}: {e}")
        time.sleep(delay)
    return None

# ----------------------------------
# Worker
# ----------------------------------
def process_pokemon(pokemon: Pokemon):
    if not pokemon.nom_pokeapi:
        return None

    data = get_pokemon_data(pokemon.nom_pokeapi)
    if not data:
        print(f"❌ {pokemon.nom_pokeapi} non récupéré")
        return None

    # Sprite override pour starters partenaires
    key = pokemon.nom_pokeapi.lower()
    if pokemon.is_starter and key in BASE_SPRITES:
        data["sprite_url"] = BASE_SPRITES[key]

    # Mise à jour Pokémon
    pokemon.height_m = data["height_m"]
    pokemon.weight_kg = data["weight_kg"]
    pokemon.sprite_url = data["sprite_url"]

    # Stats (1–1)
    stats = pokemon.stats or PokemonStat(pokemon_id=pokemon.id)
    stats.hp = data["hp"]
    stats.attack = data["attack"]
    stats.defense = data["defense"]
    stats.sp_attack = data["sp_attack"]
    stats.sp_defense = data["sp_defense"]
    stats.speed = data["speed"]

    return pokemon, stats

# ----------------------------------
# Main
# ----------------------------------
def main():
    session = SessionLocal()
    try:
        pokemons = session.query(Pokemon).all()
        print(f"➡ {len(pokemons)} Pokémon à enrichir via PokéAPI")

        updated = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(process_pokemon, p): p for p in pokemons}

            for future in as_completed(futures):
                result = future.result()
                if result is None:
                    continue

                pokemon, stats = result
                session.merge(pokemon)
                session.merge(stats)
                updated += 1
                print(f"✔ {pokemon.nom_pokeapi} enrichi")

        session.commit()  # ✅ commit final pour tout le batch
        print(f"✅ PokéAPI terminé : {updated} Pokémon enrichis")
    finally:
        session.close()

if __name__ == "__main__":
    main()
