from app.db.session import SessionLocal
from app.models import Pokemon, PokemonMove, PokemonSpecies

def inherit_mega_moves():
    session = SessionLocal()
    try:
        # 🔹 Tous les Méga-Pokémon
        megas = session.query(Pokemon).filter(Pokemon.form_name == "mega").all()

        inherited_count = 0

        for mega in megas:
            # 🔹 Récupérer le pokedex_number via species_id
            species = session.query(PokemonSpecies).filter(
                PokemonSpecies.id == mega.species_id
            ).first()

            if not species:
                print(f"[WARN] Aucun species trouvé pour méga {mega.nom_pokepedia}")
                continue

            # 🔹 Chercher le Pokémon base correspondant au même pokedex_number
            base = session.query(Pokemon).join(PokemonSpecies, Pokemon.species_id == PokemonSpecies.id).filter(
                Pokemon.form_name == "base",
                PokemonSpecies.pokedex_number == species.pokedex_number
            ).first()

            if not base:
                print(f"[WARN] Aucun Pokémon de base trouvé pour {mega.nom_pokepedia} (pokedex_number={species.pokedex_number})")
                continue

            # 🔹 Tous les moves du Pokémon de base
            for bm in base.moves:
                # Vérifier si le move existe déjà pour la Méga
                exists = session.query(PokemonMove).filter(
                    PokemonMove.pokemon_id == mega.id,
                    PokemonMove.move_id == bm.move_id,
                    PokemonMove.learn_method_id == bm.learn_method_id,
                    PokemonMove.learn_level == bm.learn_level,
                ).first()

                if exists:
                    continue

                # 🔹 Ajouter le move à la Méga
                session.add(PokemonMove(
                    pokemon_id=mega.id,
                    move_id=bm.move_id,
                    learn_method_id=bm.learn_method_id,
                    learn_level=bm.learn_level,
                ))
                inherited_count += 1
                print(f"[INFO] Move hérité pour Méga {mega.nom_pokepedia}: {bm.move.name} "
                      f"(méthode={bm.learn_method.name}, level={bm.learn_level})")

        session.commit()
        print(f"[INFO] Héritage des Méga-Pokémon terminé ({inherited_count} moves hérités)")

    finally:
        session.close()


if __name__ == "__main__":
    inherit_mega_moves()
