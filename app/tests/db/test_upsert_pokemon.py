#app/tests/db/test_upsert_pokemon.py
from app.db.guards.pokemon import upsert_pokemon

def test_upsert_pokemon_idempotent(db_session):
    p1 = upsert_pokemon(
        db_session,
        species_id=1,
        form_name="Base",
        name_pokeapi="pikachu",
        name_pokepedia="Pikachu",
        is_mega=False,
        is_alola=False,
        is_starter=True,
        height_m=0.4,
        weight_kg=6.0,
        sprite_url="url",
    )

    p2 = upsert_pokemon(
        db_session,
        species_id=1,
        form_name="Base",
        name_pokeapi="pikachu",
        name_pokepedia="Pikachu",
        is_mega=False,
        is_alola=False,
        is_starter=True,
        height_m=0.4,
        weight_kg=6.0,
        sprite_url="url",
    )

    assert p1.id == p2.id
