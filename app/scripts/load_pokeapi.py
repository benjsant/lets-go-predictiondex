# app/scripts/pokeapi_load_parallel.py

import csv
import time
from decimal import Decimal
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.db.session import SessionLocal
from app.models import Pokemon, PokemonStat

CSV_PATH = "data/csv/liste_pokemon.csv"
MAX_WORKERS = 5
BATCH_COMMIT = 50  # Commit tous les N Pokémon

# Pokémon de base pour les sprites manquants
BASE_SPRITES = {
    "pikachu-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
    "eevee-starter": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/133.png"
}

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def normalize_bool(value):
    return str(value).strip().lower() in ("1", "true", "yes", "oui")

def get_pokemon_data(name: str, retries=3, delay=2):
    """Récupère les données d’un Pokémon depuis PokéAPI avec retry."""
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                p = resp.json()
                stats = {s['stat']['name']: s['base_stat'] for s in p['stats']}
                time.sleep(0.1)  # pause courte pour ne pas saturer l'API
                return {
                    "name_eng": p['name'],
                    "hp": stats.get("hp"),
                    "attack": stats.get("attack"),
                    "defense": stats.get("defense"),
                    "sp_attack": stats.get("special-attack"),
                    "sp_defense": stats.get("special-defense"),
                    "speed": stats.get("speed"),
                    "height_m": Decimal(p['height']) / 10,
                    "weight_kg": Decimal(p['weight']) / 10,
                    "sprite_url": p['sprites']['front_default']
                }
            else:
                print(f"⚠ {name}: HTTP {resp.status_code}")
        except requests.RequestException as e:
            print(f"⚠ {name}: {e}")
        time.sleep(delay)
    return None

def process_pokemon(row):
    """Traitement d’un Pokémon pour mise à jour ou création BDD."""
    poke_id = int(row["id"])
    pokeapi_name = row.get("nom_pokeapi") or row.get("nom_eng") or row.get("nom_fr")
    data = get_pokemon_data(pokeapi_name)

    # Gestion des sprites manquants pour starters partenaires
    key = (row.get("nom_pokeapi") or "").lower()
    if data and (not data["sprite_url"] or key in BASE_SPRITES):
        data["sprite_url"] = BASE_SPRITES.get(key, data["sprite_url"])

    return poke_id, data, row

# -------------------------------------------------
# Main
# -------------------------------------------------
def main():
    session = SessionLocal()
    updated_count = 0
    try:
        with open(CSV_PATH, encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_row = {executor.submit(process_pokemon, row): row for row in reader}
            batch_count = 0

            for future in as_completed(future_to_row):
                poke_id, data, row = future.result()
                if not data:
                    print(f"❌ {row['nom_fr']} non mis à jour.")
                    continue

                poke = session.query(Pokemon).filter_by(id=poke_id).first()
                if not poke:
                    # Création si absent
                    poke = Pokemon(
                        id=poke_id,
                        name_fr=row["nom_fr"],
                        name_en=row.get("nom_eng"),
                        height_m=data["height_m"],
                        weight_kg=data["weight_kg"],
                        sprite_url=data["sprite_url"]
                    )
                else:
                    # Update seulement si vide ou starter
                    poke.height_m = poke.height_m or data["height_m"]
                    poke.weight_kg = poke.weight_kg or data["weight_kg"]
                    if poke.sprite_url is None or (row.get("nom_pokeapi") or "").lower() in BASE_SPRITES:
                        poke.sprite_url = data["sprite_url"]

                session.merge(poke)

                # Stats
                stats = poke.stats or PokemonStat(pokemon_id=poke.id)
                stats.hp = data["hp"]
                stats.attack = data["attack"]
                stats.defense = data["defense"]
                stats.sp_attack = data["sp_attack"]
                stats.sp_defense = data["sp_defense"]
                stats.speed = data["speed"]
                session.merge(stats)

                updated_count += 1
                batch_count += 1
                print(f"✔ {poke.name_fr} ({poke.name_en}) mis à jour.")

                # Commit par batch
                if batch_count >= BATCH_COMMIT:
                    session.commit()
                    batch_count = 0

        session.commit()
        print(f"✅ Mise à jour PokéAPI terminée. {updated_count} Pokémon mis à jour ou ajoutés.")

    finally:
        session.close()

if __name__ == "__main__":
    main()
