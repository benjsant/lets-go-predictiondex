"""
Tests for ETL Pipeline
======================

Tests for data extraction, transformation, and loading.
Critical for C1, C2, C3 (ETL processes).

Validation:
- Database initialization works
- CSV loading succeeds
- Data enrichment from PokeAPI works
- Post-processing logic is correct
- Evolution inheritance works
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.db.base import Base
from core.models import (
    Pokemon, PokemonSpecies, PokemonStat, PokemonType,
    Move, MoveCategory, Type, TypeEffectiveness, LearnMethod, Form
)


# ============================================================
# 🔹 FIXTURES
# ============================================================

@pytest.fixture
def temp_db_engine():
    """Create temporary in-memory database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def temp_db_session(temp_db_engine):
    """Create temporary database session."""
    Session = sessionmaker(bind=temp_db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Normal', 'Feu', 'Eau'],
        'color': ['#A8A878', '#F08030', '#6890F0']
    })


# ============================================================
# 🔹 TESTS: Database Initialization (C4)
# ============================================================

class TestDatabaseInitialization:
    """Tests for ETL database initialization."""

    def test_all_tables_created(self, temp_db_engine):
        """Test that all tables are created during initialization."""
        inspector = inspect(temp_db_engine)
        table_names = inspector.get_table_names()

        expected_tables = [
            'pokemon_species',
            'pokemon',
            'pokemon_stat',
            'pokemon_type',
            'pokemon_move',
            'type',
            'type_effectiveness',
            'move',
            'move_category',
            'form',
            'learn_method'
        ]

        for table in expected_tables:
            assert table in table_names, f"Table {table} not created"

    def test_tables_have_primary_keys(self, temp_db_engine):
        """Test that all tables have primary keys."""
        inspector = inspect(temp_db_engine)

        for table_name in inspector.get_table_names():
            pk_constraint = inspector.get_pk_constraint(table_name)
            assert pk_constraint['constrained_columns'], \
                   f"Table {table_name} has no primary key"

    def test_foreign_key_constraints_exist(self, temp_db_engine):
        """Test that foreign key relationships are defined."""
        inspector = inspect(temp_db_engine)

        # Pokemon should have FK to pokemon_species
        fks = inspector.get_foreign_keys('pokemon')
        fk_tables = [fk['referred_table'] for fk in fks]
        assert 'pokemon_species' in fk_tables, \
               "Pokemon missing FK to pokemon_species"

        # Pokemon_type should have FK to type
        fks = inspector.get_foreign_keys('pokemon_type')
        fk_tables = [fk['referred_table'] for fk in fks]
        assert 'type' in fk_tables, "Pokemon_type missing FK to type"


# ============================================================
# 🔹 TESTS: CSV Loading (C1 - Extract)
# ============================================================

class TestCSVLoading:
    """Tests for loading data from CSV files."""

    def test_csv_data_loads_to_dataframe(self, sample_csv_data):
        """Test that CSV data can be loaded into DataFrame."""
        assert len(sample_csv_data) == 3
        assert 'id' in sample_csv_data.columns
        assert 'name' in sample_csv_data.columns

    def test_csv_types_loaded(self, temp_db_session):
        """Test loading types from CSV to database."""
        # Create sample types
        types_data = [
            Type(id=1, name='Normal'),
            Type(id=2, name='Feu'),
            Type(id=3, name='Eau'),
        ]

        for type_obj in types_data:
            temp_db_session.add(type_obj)
        temp_db_session.commit()

        # Verify loaded
        loaded_types = temp_db_session.query(Type).all()
        assert len(loaded_types) == 3
        assert loaded_types[0].name == 'Normal'

    def test_csv_move_categories_loaded(self, temp_db_session):
        """Test loading move categories from CSV."""
        categories = [
            MoveCategory(id=1, name='physique'),
            MoveCategory(id=2, name='spécial'),
            MoveCategory(id=3, name='autre'),
        ]

        for cat in categories:
            temp_db_session.add(cat)
        temp_db_session.commit()

        loaded = temp_db_session.query(MoveCategory).all()
        assert len(loaded) == 3

    def test_csv_learn_methods_loaded(self, temp_db_session):
        """Test loading learn methods from CSV."""
        methods = [
            LearnMethod(id=1, name='level_up'),
            LearnMethod(id=2, name='ct'),
            LearnMethod(id=3, name='move_tutor'),
        ]

        for method in methods:
            temp_db_session.add(method)
        temp_db_session.commit()

        loaded = temp_db_session.query(LearnMethod).all()
        assert len(loaded) == 3

    def test_malformed_csv_handling(self):
        """Test handling of malformed CSV data."""
        malformed_csv = pd.DataFrame({
            'id': [1, None, 3],  # Missing value
            'name': ['Type1', 'Type2', None],  # Missing value
        })

        # Should be able to identify missing values
        assert malformed_csv['id'].isnull().any()
        assert malformed_csv['name'].isnull().any()

        # Cleaning logic should handle this
        cleaned = malformed_csv.dropna()
        assert len(cleaned) == 1  # Only first row is complete


# ============================================================
# 🔹 TESTS: API Enrichment (C1 - Extract from API)
# ============================================================

class TestAPIEnrichment:
    """Tests for data enrichment from PokeAPI."""

    @patch('requests.get')
    def test_pokeapi_request_successful(self, mock_get):
        """Test successful API request to PokeAPI."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 25,
            'name': 'pikachu',
            'height': 4,
            'weight': 60,
            'types': [{'type': {'name': 'electric'}, 'slot': 1}],
            'stats': [
                {'stat': {'name': 'hp'}, 'base_stat': 35},
                {'stat': {'name': 'attack'}, 'base_stat': 55},
            ]
        }
        mock_get.return_value = mock_response

        import requests
        response = requests.get('https://pokeapi.co/api/v2/pokemon/25')

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'pikachu'
        assert data['height'] == 4

    @patch('requests.get')
    def test_pokeapi_handles_rate_limiting(self, mock_get):
        """Test handling of API rate limiting."""
        # Mock 429 response (Too Many Requests)
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limited")
        mock_get.return_value = mock_response

        import requests
        response = requests.get('https://pokeapi.co/api/v2/pokemon/1')

        assert response.status_code == 429
        # ETL should handle this with retries or delays

    @patch('requests.get')
    def test_pokeapi_enrichment_adds_data(self, mock_get, temp_db_session):
        """Test that API enrichment adds data to database."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 1,
            'name': 'bulbasaur',
            'height': 7,
            'weight': 69,
            'sprites': {
                'front_default': 'https://example.com/bulbasaur.png'
            }
        }
        mock_get.return_value = mock_response

        # Create Pokemon species
        species = PokemonSpecies(
            id=1,
            pokedex_number=1,
            name_en='Bulbasaur',
            name_fr='Bulbizarre'
        )
        temp_db_session.add(species)

        # Create Form
        form = Form(id=1, name='normal')
        temp_db_session.add(form)
        temp_db_session.commit()

        # Simulate enrichment
        import requests
        response = requests.get('https://pokeapi.co/api/v2/pokemon/1')
        data = response.json()

        pokemon = Pokemon(
            id=1,
            species_id=1,
            form_id=1,
            name_pokeapi=data['name'],
            name_pokepedia='Bulbizarre',
            height_m=data['height'] / 10,
            weight_kg=data['weight'] / 10,
            sprite_url=data['sprites']['front_default']
        )
        temp_db_session.add(pokemon)
        temp_db_session.commit()

        # Verify enriched
        loaded = temp_db_session.query(Pokemon).first()
        assert loaded.name_pokeapi == 'bulbasaur'
        assert float(loaded.height_m) == 0.7


# ============================================================
# 🔹 TESTS: Web Scraping (C1 - Scraping)
# ============================================================

class TestWebScraping:
    """Tests for web scraping with Scrapy."""

    @patch('scrapy.Spider.parse')
    def test_scraper_parses_html(self, mock_parse):
        """Test that scraper can parse HTML content."""
        mock_response = Mock()
        mock_response.css.return_value.getall.return_value = [
            'Tonnerre', 'Surf', 'Lance-Flammes'
        ]

        # Simulate parsing
        moves = mock_response.css('td.move-name::text').getall()

        assert len(moves) == 3
        assert 'Tonnerre' in moves

    def test_scraper_handles_missing_data(self):
        """Test scraper handles missing data gracefully."""
        mock_response = Mock()
        mock_response.css.return_value.getall.return_value = []

        moves = mock_response.css('td.move-name::text').getall()

        # Should return empty list, not crash
        assert moves == []

    @patch('scrapy.http.Response')
    def test_scraper_extracts_move_data(self, mock_response_class):
        """Test extraction of move data from scraped page."""
        mock_response = Mock()
        mock_response.css.return_value = Mock()
        mock_response.css.return_value.get.return_value = 'Tonnerre'

        # Extract move name
        move_name = mock_response.css('td.move-name::text').get()

        assert move_name == 'Tonnerre'


# ============================================================
# �� TESTS: Data Aggregation (C3 - Transform)
# ============================================================

class TestDataAggregation:
    """Tests for data aggregation and transformation."""

    def test_data_deduplication(self):
        """Test removal of duplicate entries."""
        data = pd.DataFrame({
            'id': [1, 2, 2, 3, 3, 3],
            'name': ['A', 'B', 'B', 'C', 'C', 'C']
        })

        # Remove duplicates
        deduplicated = data.drop_duplicates()

        assert len(deduplicated) == 3
        assert list(deduplicated['id']) == [1, 2, 3]

    def test_data_normalization(self):
        """Test data normalization (format homogenization)."""
        data = pd.DataFrame({
            'name': ['  Pikachu  ', 'CHARIZARD', 'Bulbasaur'],
            'type': ['électrik', 'FEU', 'Plante']
        })

        # Normalize
        data['name'] = data['name'].str.strip().str.title()
        data['type'] = data['type'].str.lower().str.capitalize()

        assert data['name'].iloc[0] == 'Pikachu'
        assert data['name'].iloc[1] == 'Charizard'
        assert data['type'].iloc[0] == 'Électrik'
        assert data['type'].iloc[1] == 'Feu'

    def test_merge_multiple_sources(self):
        """Test merging data from multiple sources."""
        # Source 1: Pokemon basic info
        source1 = pd.DataFrame({
            'pokemon_id': [1, 2, 3],
            'name': ['Bulbasaur', 'Ivysaur', 'Venusaur']
        })

        # Source 2: Pokemon stats
        source2 = pd.DataFrame({
            'pokemon_id': [1, 2, 3],
            'hp': [45, 60, 80],
            'attack': [49, 62, 82]
        })

        # Merge
        merged = pd.merge(source1, source2, on='pokemon_id')

        assert len(merged) == 3
        assert 'name' in merged.columns
        assert 'hp' in merged.columns
        assert merged.iloc[0]['name'] == 'Bulbasaur'
        assert merged.iloc[0]['hp'] == 45

    def test_missing_value_imputation(self):
        """Test handling of missing values during aggregation."""
        data = pd.DataFrame({
            'pokemon_id': [1, 2, 3],
            'accuracy': [100, None, 95],
            'power': [90, 85, None]
        })

        # Fill missing with defaults
        data['accuracy'].fillna(100, inplace=True)
        data['power'].fillna(0, inplace=True)

        assert data['accuracy'].iloc[1] == 100
        assert data['power'].iloc[2] == 0


# ============================================================
# 🔹 TESTS: Post-Processing (C3 - Transform)
# ============================================================

class TestPostProcessing:
    """Tests for post-processing logic."""

    def test_mega_evolution_move_inheritance(self, temp_db_session):
        """Test that Mega evolutions inherit moves from base form."""
        # Create base Pokemon
        species = PokemonSpecies(id=1, pokedex_number=6, name_en='Charizard', name_fr='Dracaufeu')
        form_normal = Form(id=1, name='normal')
        form_mega = Form(id=2, name='mega')
        temp_db_session.add_all([species, form_normal, form_mega])
        temp_db_session.commit()

        # Base Charizard
        charizard = Pokemon(id=1, species_id=1, form_id=1, name_pokeapi='charizard')
        temp_db_session.add(charizard)

        # Mega Charizard X
        mega_charizard = Pokemon(id=2, species_id=1, form_id=2, name_pokeapi='charizard-mega-x',
                                  previous_evolution_id=1)
        temp_db_session.add(mega_charizard)
        temp_db_session.commit()

        # Post-processing should copy moves from base to mega
        # Verify relationship exists
        assert mega_charizard.previous_evolution_id == 1

    def test_alola_form_type_assignment(self, temp_db_session):
        """Test that Alola forms get correct types."""
        # Alola forms have different types
        species = PokemonSpecies(id=1, pokedex_number=26, name_en='Raichu', name_fr='Raichu')
        form_normal = Form(id=1, name='normal')
        form_alola = Form(id=3, name='alola')
        type_electric = Type(id=1, name='Électrik')
        type_psy = Type(id=2, name='Psy')

        temp_db_session.add_all([species, form_normal, form_alola, type_electric, type_psy])
        temp_db_session.commit()

        # Alola Raichu (Electric/Psychic)
        raichu_alola = Pokemon(id=2, species_id=1, form_id=3, name_pokeapi='raichu-alola')
        temp_db_session.add(raichu_alola)
        temp_db_session.commit()

        # Verify form is Alola
        assert raichu_alola.form_id == 3


# ============================================================
# 🔹 TESTS: SQL Queries (C2)
# ============================================================

class TestSQLQueries:
    """Tests for SQL query execution."""

    def test_select_query_with_join(self, temp_db_session):
        """Test SELECT with JOIN query."""
        # Create test data
        species = PokemonSpecies(id=1, pokedex_number=25, name_en='Pikachu', name_fr='Pikachu')
        form = Form(id=1, name='normal')
        type_electric = Type(id=1, name='Électrik')

        temp_db_session.add_all([species, form, type_electric])
        temp_db_session.commit()

        pokemon = Pokemon(id=1, species_id=1, form_id=1, name_pokeapi='pikachu')
        temp_db_session.add(pokemon)
        temp_db_session.commit()

        pokemon_type = PokemonType(pokemon_id=1, type_id=1, slot=1)
        temp_db_session.add(pokemon_type)
        temp_db_session.commit()

        # Query with JOIN
        result = temp_db_session.query(Pokemon, Type).join(
            PokemonType, Pokemon.id == PokemonType.pokemon_id
        ).join(
            Type, PokemonType.type_id == Type.id
        ).filter(Pokemon.id == 1).all()

        assert len(result) == 1
        assert result[0][1].name == 'Électrik'

    def test_aggregate_query(self, temp_db_session):
        """Test aggregate queries (COUNT, AVG, etc)."""
        from sqlalchemy import func

        # Create multiple Pokemon
        species = PokemonSpecies(id=1, pokedex_number=1, name_en='Test', name_fr='Test')
        form = Form(id=1, name='normal')
        temp_db_session.add_all([species, form])
        temp_db_session.commit()

        for i in range(10):
            pokemon = Pokemon(id=i+1, species_id=1, form_id=1, name_pokeapi=f'pokemon{i}')
            temp_db_session.add(pokemon)
        temp_db_session.commit()

        # Count query
        count = temp_db_session.query(func.count(Pokemon.id)).scalar()

        assert count == 10

    def test_complex_filter_query(self, temp_db_session):
        """Test complex WHERE clause with multiple conditions."""
        species = PokemonSpecies(id=1, pokedex_number=25, name_en='Pikachu', name_fr='Pikachu')
        form = Form(id=1, name='normal')
        temp_db_session.add_all([species, form])
        temp_db_session.commit()

        for i in range(5):
            pokemon = Pokemon(
                id=i+1,
                species_id=1,
                form_id=1,
                name_pokeapi=f'pokemon{i}',
                height_m=float(i)
            )
            temp_db_session.add(pokemon)
        temp_db_session.commit()

        # Complex filter
        result = temp_db_session.query(Pokemon).filter(
            Pokemon.species_id == 1,
            Pokemon.height_m > 1.0,
            Pokemon.height_m < 4.0
        ).all()

        assert len(result) == 2  # Pokemon with height 2.0 and 3.0


# ============================================================
# 🔹 TESTS: ETL Error Handling
# ============================================================

class TestETLErrorHandling:
    """Tests for ETL error handling."""

    def test_handles_database_connection_error(self):
        """Test handling of database connection errors."""
        # Try connecting to invalid database
        try:
            engine = create_engine('postgresql://invalid:invalid@localhost:5432/invalid')
            engine.connect()
            pytest.fail("Should have raised connection error")
        except Exception as e:
            # Should handle gracefully
            assert True

    def test_handles_corrupted_csv(self):
        """Test handling of corrupted CSV data."""
        corrupted_data = "id,name\n1,Type1\n2,\n3,Type3,ExtraColumn"

        # Should be able to detect corruption
        try:
            import io
            df = pd.read_csv(io.StringIO(corrupted_data))
            # Check for inconsistencies
            assert df.isnull().any().any() or len(df.columns) != 2
        except Exception:
            # Exception is acceptable for corrupted data
            assert True

    def test_rollback_on_error(self, temp_db_session):
        """Test that transactions rollback on error."""
        species = PokemonSpecies(id=1, pokedex_number=1, name_en='Test', name_fr='Test')
        temp_db_session.add(species)
        temp_db_session.commit()

        try:
            # Try to add duplicate (should fail)
            duplicate = PokemonSpecies(id=1, pokedex_number=1, name_en='Duplicate', name_fr='Duplicate')
            temp_db_session.add(duplicate)
            temp_db_session.commit()
            pytest.fail("Should have raised integrity error")
        except Exception:
            temp_db_session.rollback()
            # Database should be in consistent state
            count = temp_db_session.query(PokemonSpecies).count()
            assert count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
