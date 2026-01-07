from app.db.session import SessionLocal
from app.models import Pokemon, PokemonSpecies
from app.db.guards.pokemon_move import upsert_pokemon_move


def inherit_mega_moves():
    session = SessionLocal()
    try:
        megas = session.query(Pokemon).filter(
            Pokemon.form_name == "mega"
        ).all()

        inherited_count = 0

        for mega in megas:
            species = session.get(PokemonSpecies, mega.species_id)
            if not species:
                print(f"[WARN] Aucun species pour {mega.nom_pokepedia}")
                continue

            base = (
                session.query(Pokemon)
                .join(PokemonSpecies)
                .filter(
                    Pokemon.form_name == "base",
                    PokemonSpecies.pokedex_number == species.pokedex_number,
                )
                .one_or_none()
            )

            if not base:
                print(
                    f"[WARN] Aucun Pokémon de base pour {mega.nom_pokepedia} "
                    f"(pokedex={species.pokedex_number})"
                )
                continue

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
        print(
            f"[INFO] Héritage des Méga-Pokémon terminé "
            f"({inherited_count} moves hérités)"
        )

    finally:
        session.close()


if __name__ == "__main__":
    inherit_mega_moves()
