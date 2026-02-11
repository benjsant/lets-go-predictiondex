"""
Pytest configuration and shared fixtures
=========================================

This module provides fixtures for testing the Pokemon API.
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.db.base import Base
from core.models import (
    Pokemon, PokemonSpecies, PokemonStat, PokemonType,
    Move, MoveCategory, Type, TypeEffectiveness, PokemonMove, LearnMethod, Form
)


# Test database URL (use in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def sample_types(db_session: Session):
    """Create sample types for testing."""
    types = [
        Type(id=1, name="Normal"),
        Type(id=2, name="Combat"),
        Type(id=3, name="Feu"),
        Type(id=4, name="Plante"),
        Type(id=5, name="Eau"),
        Type(id=6, name="Électrik"),
        Type(id=7, name="Vol"),
        Type(id=8, name="Psy"),
    ]

    for t in types:
        db_session.add(t)

    db_session.commit()

    return types


@pytest.fixture(scope="function")
def sample_type_effectiveness(db_session: Session, sample_types):
    """Create sample type effectiveness relationships."""
    effectiveness = [
        # Feu (3) vs Plante (4) = 2x
        TypeEffectiveness(attacking_type_id=3, defending_type_id=4, multiplier=2.0),
        # Eau (5) vs Feu (3) = 2x
        TypeEffectiveness(attacking_type_id=5, defending_type_id=3, multiplier=2.0),
        # Feu (3) vs Eau (5) = 0.5x
        TypeEffectiveness(attacking_type_id=3, defending_type_id=5, multiplier=0.5),
        # Plante (4) vs Eau (5) = 2x
        TypeEffectiveness(attacking_type_id=4, defending_type_id=5, multiplier=2.0),
        # Électrik (6) vs Eau (5) = 2x
        TypeEffectiveness(attacking_type_id=6, defending_type_id=5, multiplier=2.0),
        # Électrik (6) vs Plante (4) = 0.5x
        TypeEffectiveness(attacking_type_id=6, defending_type_id=4, multiplier=0.5),
        # Vol (7) vs Plante (4) = 2x
        TypeEffectiveness(attacking_type_id=7, defending_type_id=4, multiplier=2.0),
        # Psy (8) vs Combat (2) = 2x
        TypeEffectiveness(attacking_type_id=8, defending_type_id=2, multiplier=2.0),
    ]

    for eff in effectiveness:
        db_session.add(eff)

    db_session.commit()

    return effectiveness


@pytest.fixture(scope="function")
def sample_move_categories(db_session: Session):
    """Create sample move categories."""
    categories = [
        MoveCategory(id=1, name="physique"),
        MoveCategory(id=2, name="spécial"),
        MoveCategory(id=3, name="autre"),
    ]

    for cat in categories:
        db_session.add(cat)

    db_session.commit()

    return categories


@pytest.fixture(scope="function")
def sample_moves(db_session: Session, sample_types, sample_move_categories):
    """Create sample moves for testing."""
    moves = [
        Move(
            id=1,
            name="Lance-Flammes",
            type_id=3, # Feu
            category_id=2, # spécial
            power=90,
            accuracy=100,
            priority=0,
            damage_type="offensif",
            description="Une gerbe de flammes intense."
        ),
        Move(
            id=2,
            name="Surf",
            type_id=5, # Eau
            category_id=2, # spécial
            power=90,
            accuracy=100,
            priority=0,
            damage_type="offensif",
            description="Une énorme vague."
        ),
        Move(
            id=3,
            name="Tranche-Herbe",
            type_id=4, # Plante
            category_id=1, # physique
            power=55,
            accuracy=95,
            priority=0,
            damage_type="offensif",
            description="Attaque avec une lame d'herbe."
        ),
        Move(
            id=4,
            name="Vive-Attaque",
            type_id=1, # Normal
            category_id=1, # physique
            power=40,
            accuracy=100,
            priority=1,
            damage_type="offensif",
            description="Attaque rapide prioritaire."
        ),
        Move(
            id=5,
            name="Tonnerre",
            type_id=6, # Électrik
            category_id=2, # spécial
            power=110,
            accuracy=70,
            priority=0,
            damage_type="offensif",
            description="Une puissante décharge électrique."
        ),
        Move(
            id=6,
            name="Abri",
            type_id=1, # Normal
            category_id=3, # autre
            power=None,
            accuracy=None,
            priority=4,
            damage_type="protection",
            description="Protection totale."
        ),
    ]

    for move in moves:
        db_session.add(move)

    db_session.commit()

    return moves


@pytest.fixture(scope="function")
def sample_forms(db_session: Session):
    """Create sample Pokemon forms."""
    forms = [
        Form(id=1, name="normal"),
        Form(id=2, name="mega"),
        Form(id=3, name="alola"),
    ]

    for form in forms:
        db_session.add(form)

    db_session.commit()

    return forms


@pytest.fixture(scope="function")
def sample_learn_methods(db_session: Session):
    """Create sample learn methods."""
    methods = [
        LearnMethod(id=1, name="level_up"),
        LearnMethod(id=2, name="ct"),
        LearnMethod(id=3, name="move_tutor"),
    ]

    for method in methods:
        db_session.add(method)

    db_session.commit()

    return methods


@pytest.fixture(scope="function")
def sample_species(db_session: Session):
    """Create sample Pokemon species."""
    species = [
        PokemonSpecies(
            id=1,
            pokedex_number=25,
            name_en="Pikachu",
            name_fr="Pikachu"
        ),
        PokemonSpecies(
            id=2,
            pokedex_number=6,
            name_en="Charizard",
            name_fr="Dracaufeu"
        ),
        PokemonSpecies(
            id=3,
            pokedex_number=9,
            name_en="Blastoise",
            name_fr="Tortank"
        ),
    ]

    for spec in species:
        db_session.add(spec)

    db_session.commit()

    return species


@pytest.fixture(scope="function")
def sample_pokemon(
    db_session: Session,
    sample_species,
    sample_types,
    sample_moves,
    sample_forms,
    sample_learn_methods
):
    """Create sample Pokemon with stats, types, and moves."""
    # Pikachu (Électrik)
    pikachu = Pokemon(
        id=1,
        species_id=1,
        form_id=1, # normal
        name_pokeapi="pikachu",
        name_pokepedia="Pikachu",
        height_m=0.4,
        weight_kg=6.0
    )
    pikachu_stats = PokemonStat(
        pokemon_id=1,
        hp=35,
        attack=55,
        defense=40,
        sp_attack=50,
        sp_defense=50,
        speed=90
    )
    pikachu.stats = pikachu_stats

    # Add types
    pikachu_type = PokemonType(pokemon_id=1, type_id=6, slot=1) # Électrik

    # Add moves
    pikachu_move1 = PokemonMove(
        pokemon_id=1,
        move_id=5, # Tonnerre
        learn_method_id=1, # level_up
        learn_level=30
    )
    pikachu_move2 = PokemonMove(
        pokemon_id=1,
        move_id=4, # Vive-Attaque
        learn_method_id=1, # level_up
        learn_level=5
    )

    db_session.add(pikachu)
    db_session.add(pikachu_stats)
    db_session.add(pikachu_type)
    db_session.add(pikachu_move1)
    db_session.add(pikachu_move2)

    # Dracaufeu (Feu/Vol)
    charizard = Pokemon(
        id=2,
        species_id=2,
        form_id=1, # normal
        name_pokeapi="charizard",
        name_pokepedia="Dracaufeu",
        height_m=1.7,
        weight_kg=90.5
    )
    charizard_stats = PokemonStat(
        pokemon_id=2,
        hp=78,
        attack=84,
        defense=78,
        sp_attack=109,
        sp_defense=85,
        speed=100
    )
    charizard.stats = charizard_stats

    # Add types
    charizard_type1 = PokemonType(pokemon_id=2, type_id=3, slot=1) # Feu
    charizard_type2 = PokemonType(pokemon_id=2, type_id=7, slot=2) # Vol

    # Add moves
    charizard_move = PokemonMove(
        pokemon_id=2,
        move_id=1, # Lance-Flammes
        learn_method_id=1, # level_up
        learn_level=40
    )

    db_session.add(charizard)
    db_session.add(charizard_stats)
    db_session.add(charizard_type1)
    db_session.add(charizard_type2)
    db_session.add(charizard_move)

    # Tortank (Eau)
    blastoise = Pokemon(
        id=3,
        species_id=3,
        form_id=1, # normal
        name_pokeapi="blastoise",
        name_pokepedia="Tortank",
        height_m=1.6,
        weight_kg=85.5
    )
    blastoise_stats = PokemonStat(
        pokemon_id=3,
        hp=79,
        attack=83,
        defense=100,
        sp_attack=85,
        sp_defense=105,
        speed=78
    )
    blastoise.stats = blastoise_stats

    # Add types
    blastoise_type = PokemonType(pokemon_id=3, type_id=5, slot=1) # Eau

    # Add moves
    blastoise_move = PokemonMove(
        pokemon_id=3,
        move_id=2, # Surf
        learn_method_id=1, # level_up
        learn_level=45
    )

    db_session.add(blastoise)
    db_session.add(blastoise_stats)
    db_session.add(blastoise_type)
    db_session.add(blastoise_move)

    db_session.commit()

    # Refresh to load relationships
    db_session.refresh(pikachu)
    db_session.refresh(charizard)
    db_session.refresh(blastoise)

    return {
        'pikachu': pikachu,
        'charizard': charizard,
        'blastoise': blastoise
    }
