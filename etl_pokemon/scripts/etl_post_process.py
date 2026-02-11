"""ETL post-processing phase for Pokemon data."""

from core.db.guards.pokemon_move import upsert_pokemon_move
from core.db.session import SessionLocal
from core.models import Form, Pokemon, PokemonSpecies


def inherit_mega_moves():
    """Copy move learnsets from base Pokemon to their Mega forms."""
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
