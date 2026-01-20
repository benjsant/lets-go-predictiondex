# app/scripts/build_dataset_V2.py

"""
Build ML dataset with Pokémon, offensive moves and simulated damage
------------------------------------------------------------------
- Pokémon stats & types
- Offensive moves only (physical / special)
- Variable attacker & defender levels
- STAB, accuracy, type effectiveness
- Export Parquet for ML training

C3 – Data aggregation & normalization
"""

from pathlib import Path
import pandas as pd

from extraction_pokemon.db.session import SessionLocal
from extraction_pokemon.models import (
    Pokemon,
    PokemonType,
    PokemonStat,
    PokemonSpecies,
    PokemonMove,
    Move,
    Type,
)

# ----------------------------------
# Config
# ----------------------------------
OUTPUT_PATH = Path("data/datasets")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_PATH / "pokemon_damage_ml.parquet"

ATTACKER_LEVELS = [50, 60, 70, 75]
DEFENDER_LEVELS = [50, 60, 70, 75]

# ----------------------------------
# Type chart (simplifié)
# ----------------------------------
TYPE_CHART = {
    ("fire", "grass"): 2.0,
    ("fire", "water"): 0.5,
    ("electric", "water"): 2.0,
    ("electric", "electric"): 0.5,
    ("water", "fire"): 2.0,
    ("grass", "water"): 2.0,
}

def type_multiplier(move_type, def_type1, def_type2):
    m1 = TYPE_CHART.get((move_type, def_type1), 1.0)
    m2 = TYPE_CHART.get((move_type, def_type2), 1.0)
    return m1 * m2

def compute_damage(level, power, atk, defense, stab, type_mult):
    """Formule simplifiée Pokémon"""
    base = ((2 * level / 5 + 2) * power * (atk / defense)) / 50 + 2
    return base * stab * type_mult

# ----------------------------------
# Main
# ----------------------------------
def build_dataset():
    session = SessionLocal()
    try:
        # ----------------------------------
        # 1️⃣ Pokémon stats & types
        # ----------------------------------
        query = (
            session.query(
                Pokemon.id.label("pokemon_id"),
                PokemonSpecies.name_en,
                PokemonStat.attack,
                PokemonStat.defense,
                PokemonStat.sp_attack,
                PokemonStat.sp_defense,
                PokemonType.slot,
                Type.name.label("type_name"),
            )
            .join(Pokemon.species)
            .join(Pokemon.stats)
            .join(Pokemon.types)
            .join(Type)
        )

        df = pd.DataFrame(query.all())
        df = df.dropna()

        types = (
            df.pivot_table(
                index="pokemon_id",
                columns="slot",
                values="type_name",
                aggfunc="first",
            )
            .rename(columns={1: "primary_type", 2: "secondary_type"})
        )

        stats_cols = [
            "pokemon_id",
            "name_en",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
        ]

        df_pokemon = (
            df[stats_cols]
            .drop_duplicates("pokemon_id")
            .set_index("pokemon_id")
            .join(types)
            .reset_index()
        )

        df_pokemon["secondary_type"] = df_pokemon["secondary_type"].fillna("none")

        # ----------------------------------
        # 2️⃣ Offensive moves
        # ----------------------------------
        moves_query = (
            session.query(
                PokemonMove.pokemon_id,
                Move.name.label("move_name"),
                Move.type.label("move_type"),
                Move.category,
                Move.power,
                Move.accuracy,
                PokemonMove.learn_method,
            )
            .join(PokemonMove.move)
            .filter(Move.category.in_(["physical", "special"]))
        )

        moves_df = pd.DataFrame(moves_query.all()).dropna(subset=["power"])

        # ----------------------------------
        # 3️⃣ Dataset generation
        # ----------------------------------
        rows = []

        for atk_lvl in ATTACKER_LEVELS:
            for def_lvl in DEFENDER_LEVELS:
                for _, attacker in df_pokemon.iterrows():
                    attacker_moves = moves_df[moves_df["pokemon_id"] == attacker["pokemon_id"]]

                    for _, move in attacker_moves.iterrows():
                        for _, defender in df_pokemon.iterrows():

                            stab = 1.5 if move["move_type"] in [
                                attacker["primary_type"],
                                attacker["secondary_type"],
                            ] else 1.0

                            t_mult = type_multiplier(
                                move["move_type"],
                                defender["primary_type"],
                                defender["secondary_type"],
                            )

                            if move["category"] == "physical":
                                atk = attacker["attack"]
                                defense = defender["defense"]
                            else:
                                atk = attacker["sp_attack"]
                                defense = defender["sp_defense"]

                            damage = compute_damage(
                                atk_lvl,
                                move["power"],
                                atk,
                                defense,
                                stab,
                                t_mult,
                            )

                            expected_damage = damage * (move["accuracy"] / 100)

                            rows.append({
                                "attacker_id": attacker["pokemon_id"],
                                "defender_id": defender["pokemon_id"],
                                "attacker_level": atk_lvl,
                                "defender_level": def_lvl,
                                "move_name": move["move_name"],
                                "move_type": move["move_type"],
                                "move_category": move["category"],
                                "move_power": move["power"],
                                "move_accuracy": move["accuracy"],
                                "learn_method": move["learn_method"],
                                "attacker_attack": attacker["attack"],
                                "attacker_sp_attack": attacker["sp_attack"],
                                "defender_defense": defender["defense"],
                                "defender_sp_defense": defender["sp_defense"],
                                "stab": stab,
                                "type_multiplier": t_mult,
                                "expected_damage": expected_damage,
                            })

        df_ml = pd.DataFrame(rows)

        # ----------------------------------
        # 4️⃣ Export
        # ----------------------------------
        df_ml.to_parquet(OUTPUT_FILE, index=False)

        print("✅ Dataset ML généré")
        print(f"➡ Fichier : {OUTPUT_FILE}")
        print(f"➡ Lignes : {len(df_ml)}")

    finally:
        session.close()


if __name__ == "__main__":
    build_dataset()
