import csv
from decimal import Decimal

# ⚠️ OBLIGATOIRE : force l’enregistrement de TOUS les models
import app.models  # noqa: F401

from app.db.session import SessionLocal
from app.models import (
    Pokemon,
    PokemonSpecies,
    Type,
    Move,
    PokemonType,
    TypeEffectiveness,
)

DATA_PATH = "data/csv"

# ======================================================
# Helpers
# ======================================================

def normalize_bool(value):
    return str(value).strip().lower() in ("1", "true", "yes", "oui")


def normalize_int(value):
    return int(value) if value not in ("", None) else None


def normalize_key(value: str) -> str:
    return value.strip().lower()


# ======================================================
# Load TYPES (depuis liste_pokemon.csv)
# ======================================================

def load_types(session):
    print("➡ Loading types...")

    types_seen = {}

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col in ("type_1", "type_2"):
                name = row.get(col)
                if name:
                    key = normalize_key(name)
                    if key not in types_seen:
                        types_seen[key] = Type(name=name.strip())

    session.add_all(types_seen.values())
    session.commit()

    print(f"✔ {len(types_seen)} types inserted")


# ======================================================
# Load MOVES
# ======================================================

def load_moves(session):
    print("➡ Loading moves...")

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(Type).all()
    }

    with open(f"{DATA_PATH}/liste_capacite_lets_go.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            move = Move(
                name=row["nom_français"].strip(),
                power=normalize_int(row.get("puissance")),
                accuracy=normalize_int(row.get("précision")),
                category=row["classe"].strip(),
                damage_type=row.get("type_degats") or None,
                description=row.get("description"),
                type_id=type_map[normalize_key(row["type"])],
            )
            session.merge(move)

    session.commit()
    print("✔ Moves inserted")


# ======================================================
# Load POKEMON SPECIES
# ======================================================

def load_pokemon_species(session):
    print("➡ Loading pokemon species...")

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            species = PokemonSpecies(
                id=int(row["id"]),
                pokedex_number=int(row["num_pokedex"]),
                name_fr=row["nom_fr"].strip(),
                name_en=row.get("nom_eng"),
            )
            session.merge(species)

    session.commit()
    print("✔ Pokemon species inserted")


# ======================================================
# Load POKEMON (formes)
# ======================================================

def load_pokemon(session):
    print("➡ Loading pokemon forms...")

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pokemon = Pokemon(
                id=int(row["id"]),
                species_id=int(row["id"]),  # 1 forme = 1 espèce (LGPE)

                nom_pokeapi=row.get("nom_pokeapi"),
                nom_pokepedia=row.get("nom_pokepedia"),
                form_name="base",

                is_alola=normalize_bool(row.get("alola")),
                is_mega=normalize_bool(row.get("mega")),
                is_starter=normalize_bool(row.get("starter")),

                height_m=Decimal("0.00"),
                weight_kg=Decimal("0.00"),
                sprite_url=None,
            )
            session.merge(pokemon)

    session.commit()
    print("✔ Pokemon forms inserted")


# ======================================================
# Load POKEMON ↔ TYPES
# ======================================================

def load_pokemon_types(session):
    print("➡ Loading pokemon types...")

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(Type).all()
    }

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pokemon_id = int(row["id"])

            if row.get("type_1"):
                session.merge(
                    PokemonType(
                        pokemon_id=pokemon_id,
                        type_id=type_map[normalize_key(row["type_1"])],
                        slot=1,
                    )
                )

            if row.get("type_2"):
                session.merge(
                    PokemonType(
                        pokemon_id=pokemon_id,
                        type_id=type_map[normalize_key(row["type_2"])],
                        slot=2,
                    )
                )

    session.commit()
    print("✔ Pokemon types inserted")


# ======================================================
# Load TYPE EFFECTIVENESS
# ======================================================

def load_type_effectiveness(session):
    print("➡ Loading type effectiveness...")

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(Type).all()
    }

    with open(f"{DATA_PATH}/table_type.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            te = TypeEffectiveness(
                attacking_type_id=type_map[normalize_key(row["type_attaquant"])],
                defending_type_id=type_map[normalize_key(row["type_defenseur"])],
                multiplier=Decimal(row["multiplicateur"]),
            )
            session.merge(te)

    session.commit()
    print("✔ Type effectiveness inserted")


# ======================================================
# MAIN
# ======================================================

def main():
    session = SessionLocal()
    try:
        load_types(session)
        load_moves(session)
        load_pokemon_species(session)
        load_pokemon(session)
        load_pokemon_types(session)
        load_type_effectiveness(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
