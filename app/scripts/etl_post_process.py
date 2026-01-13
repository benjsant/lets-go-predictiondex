# app/scripts/etl_post_process.py

"""
ETL - Post-processing phase for Pokémon data (Pokémon Let's Go)

This script performs post-load transformations that cannot be
handled during the initial CSV or API ingestion phases.

Context:
Some Pokémon forms (e.g. Mega evolutions) do not have their own
distinct learnsets in the data sources used for E1. However, from
a business and gameplay perspective, Mega Pokémon inherit the moves
of their base form.

ETL responsibilities:
- Identify Mega Pokémon forms already persisted in the database
- Resolve their corresponding base Pokémon using Pokédex number
- Copy (inherit) move learnsets from base form to Mega form
- Ensure idempotent insertion using guarded upserts
- Preserve referential integrity and learning metadata

This script belongs to the "Transform" phase of the ETL pipeline
and must be executed after:
- Pokémon species are loaded
- Pokémon forms are loaded
- Pokémon ↔ moves associations are populated

Competency block:
- E1: Advanced data transformation and normalization logic
"""

from app.db.session import SessionLocal
from app.models import Pokemon, PokemonSpecies, Form
from app.db.guards.pokemon_move import upsert_pokemon_move


def inherit_mega_moves():
    """
    Inherit move learnsets from base Pokémon to Mega Pokémon forms.

    Business rule:
    - A Mega Pokémon shares the same learnable moves as its base form
    - The base form is identified using the Pokédex number
    - Only Pokémon with form_name == "mega" are processed

    Processing steps:
    1. Retrieve form IDs dynamically
    2. Retrieve all Mega Pokémon forms
    3. Resolve their Pokémon species
    4. Find the corresponding base Pokémon by pokedex_number
    5. Copy each move association from base to Mega
    6. Use guarded upsert to avoid duplicates

    Side effects:
    - Inserts rows into pokemon_move table if missing
    - Does not delete or override existing data

    Returns:
        None
    """
    session = SessionLocal()
    try:
        # Retrieve form IDs dynamically
        forms = {f.name: f.id for f in session.query(Form).all()}
        base_form_id = forms.get("base")
        mega_form_id = forms.get("mega")

        if base_form_id is None or mega_form_id is None:
            print("[ERROR] Base or Mega form not found in database")
            return

        # Get all Mega Pokémon
        megas = session.query(Pokemon).filter(Pokemon.form_id == mega_form_id).all()
        inherited_count = 0

        for mega in megas:
            species = session.get(PokemonSpecies, mega.species_id)
            if not species:
                print(f"[WARN] No species found for {mega.name_pokepedia}")
                continue

            # Find the base Pokémon by pokedex_number
            base = (
                session.query(Pokemon)
                .join(PokemonSpecies)
                .filter(
                    Pokemon.form_id == base_form_id,
                    PokemonSpecies.pokedex_number == species.pokedex_number,
                )
                .one_or_none()
            )

            if not base:
                print(
                    f"[WARN] No base Pokémon found for {mega.name_pokepedia} "
                    f"(pokedex={species.pokedex_number})"
                )
                continue

            # Copy moves from base to Mega
            for bm in base.moves:
                _, created = upsert_pokemon_move(
                    session,
                    pokemon_id=mega.id,
                    move_id=bm.move_id,
                    learn_method_id=bm.learn_method_id,
                    learn_level=bm.learn_level,
                )
                if created:
                    inherited_count += 1

        session.commit()
        print(f"[INFO] Mega Pokémon move inheritance completed ({inherited_count} moves inherited)")

    finally:
        session.close()


if __name__ == "__main__":
    inherit_mega_moves()
