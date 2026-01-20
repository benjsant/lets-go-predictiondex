# app/scripts/build_dataset.py

"""
Build final ML dataset from PostgreSQL
--------------------------------------
- Aggregate data from multiple tables
- Clean corrupted / incomplete entries
- Normalize formats
- Export final dataset as Parquet

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
    Type,
)

# ----------------------------------
# Config
# ----------------------------------
OUTPUT_PATH = Path("data/datasets")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_PATH / "pokemon_dataset.parquet"


# ----------------------------------
# Main aggregation logic
# ----------------------------------
def build_dataset():
    session = SessionLocal()
    try:
        # -------------------------
        # SQL extraction
        # -------------------------
        query = (
            session.query(
                Pokemon.id.label("pokemon_id"),
                PokemonSpecies.pokedex_number,
                PokemonSpecies.name_fr,
                PokemonSpecies.name_en,
                Pokemon.height_m,
                Pokemon.weight_kg,
                Pokemon.is_mega,
                Pokemon.is_alola,
                Pokemon.is_starter,
                PokemonStat.hp,
                PokemonStat.attack,
                PokemonStat.defense,
                PokemonStat.sp_attack,
                PokemonStat.sp_defense,
                PokemonStat.speed,
                PokemonType.slot,
                Type.name.label("type_name"),
            )
            .join(Pokemon.species)
            .join(Pokemon.stats)
            .join(Pokemon.types)
            .join(Type)
        )

        rows = query.all()
        df = pd.DataFrame(rows)

        # -------------------------
        # Cleaning rules
        # -------------------------

        # 1️⃣ Remove corrupted entries
        df = df.dropna(subset=[
            "hp",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "speed",
            "type_name",
        ])

        # -------------------------
        # Normalize types (primary / secondary)
        # -------------------------
        types_pivot = (
            df.pivot_table(
                index="pokemon_id",
                columns="slot",
                values="type_name",
                aggfunc="first"
            )
            .rename(columns={
                1: "primary_type",
                2: "secondary_type",
            })
        )

        # -------------------------
        # Keep one row per Pokémon
        # -------------------------
        base_cols = [
            "pokemon_id",
            "pokedex_number",
            "name_fr",
            "name_en",
            "height_m",
            "weight_kg",
            "is_mega",
            "is_alola",
            "is_starter",
            "hp",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "speed",
        ]

        df_base = (
            df[base_cols]
            .drop_duplicates(subset=["pokemon_id"])
            .set_index("pokemon_id")
        )

        final_df = df_base.join(types_pivot)

        # -------------------------
        # Final formatting
        # -------------------------
        final_df = final_df.reset_index(drop=True)

        final_df["secondary_type"] = final_df["secondary_type"].fillna("none")

        # -------------------------
        # Export
        # -------------------------
        final_df.to_parquet(OUTPUT_FILE, index=False)

        print(f"✅ Dataset generated: {OUTPUT_FILE}")
        print(f"➡ Rows: {len(final_df)}")

    finally:
        session.close()


# ----------------------------------
# Entry point
# ----------------------------------
if __name__ == "__main__":
    build_dataset()
