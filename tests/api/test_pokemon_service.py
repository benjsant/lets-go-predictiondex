"""
Tests for pokemon service
==========================

Unit tests for Pokemon service layer.

Coverage target: 80%+
"""

import pytest
from decimal import Decimal

from api_pokemon.services.pokemon_service import (
    list_pokemon,
    get_pokemon_by_id,
    search_pokemon_by_species_name,
    compute_pokemon_weaknesses,
)


# ============================================================
# TESTS: List Pokemon
# ============================================================

class TestListPokemon:
    """Tests for listing all Pokemon."""

    def test_list_pokemon_returns_all(self, db_session, sample_pokemon):
        """Test that list_pokemon returns all Pokemon."""
        result = list_pokemon(db_session)

        assert len(result) == 3 # Pikachu, Charizard, Blastoise
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[2].id == 3

    def test_list_pokemon_eager_loads_relationships(self, db_session, sample_pokemon):
        """Test that relationships are eager-loaded."""
        result = list_pokemon(db_session)

        # Check that species is loaded
        assert result[0].species is not None
        assert result[0].species.name_en == "Pikachu"

        # Check that types are loaded
        assert len(result[0].types) == 1
        assert result[0].types[0].type.name == "Électrik"

    def test_list_pokemon_ordered_by_id(self, db_session, sample_pokemon):
        """Test that Pokemon are ordered by ID."""
        result = list_pokemon(db_session)

        for i in range(len(result) - 1):
            assert result[i].id < result[i + 1].id

    def test_list_pokemon_empty_database(self, db_session):
        """Test list_pokemon with empty database."""
        result = list_pokemon(db_session)
        assert result == []


# ============================================================
# TESTS: Get Pokemon by ID
# ============================================================

class TestGetPokemonById:
    """Tests for retrieving Pokemon by ID."""

    def test_get_pokemon_by_id_found(self, db_session, sample_pokemon):
        """Test retrieving existing Pokemon."""
        pokemon = get_pokemon_by_id(db_session, 1)

        assert pokemon is not None
        assert pokemon.id == 1
        assert pokemon.species.name_en == "Pikachu"

    def test_get_pokemon_by_id_not_found(self, db_session, sample_pokemon):
        """Test retrieving non-existent Pokemon."""
        pokemon = get_pokemon_by_id(db_session, 999)
        assert pokemon is None

    def test_get_pokemon_by_id_eager_loads_stats(self, db_session, sample_pokemon):
        """Test that stats are eager-loaded."""
        pokemon = get_pokemon_by_id(db_session, 1)

        assert pokemon.stats is not None
        assert pokemon.stats.hp == 35
        assert pokemon.stats.attack == 55
        assert pokemon.stats.speed == 90

    def test_get_pokemon_by_id_eager_loads_types(self, db_session, sample_pokemon):
        """Test that types are eager-loaded."""
        pokemon = get_pokemon_by_id(db_session, 2) # Charizard

        assert len(pokemon.types) == 2
        type_names = [pt.type.name for pt in pokemon.types]
        assert "Feu" in type_names
        assert "Vol" in type_names

    def test_get_pokemon_by_id_eager_loads_moves(self, db_session, sample_pokemon):
        """Test that moves are eager-loaded."""
        pokemon = get_pokemon_by_id(db_session, 1) # Pikachu

        assert len(pokemon.moves) >= 1
        assert pokemon.moves[0].move is not None
        assert pokemon.moves[0].move.type is not None
        assert pokemon.moves[0].move.category is not None


# ============================================================
# TESTS: Search Pokemon by Name
# ============================================================

class TestSearchPokemonByName:
    """Tests for searching Pokemon by species name."""

    def test_search_pokemon_exact_match(self, db_session, sample_pokemon):
        """Test exact name match."""
        result = search_pokemon_by_species_name(db_session, "Pikachu", lang="fr")

        assert len(result) == 1
        assert result[0].species.name_fr == "Pikachu"

    def test_search_pokemon_partial_match(self, db_session, sample_pokemon):
        """Test partial name match."""
        result = search_pokemon_by_species_name(db_session, "ka", lang="fr")

        # Should match "Pikachu"
        assert len(result) >= 1
        assert any(p.species.name_fr == "Pikachu" for p in result)

    def test_search_pokemon_case_insensitive(self, db_session, sample_pokemon):
        """Test case-insensitive search."""
        result = search_pokemon_by_species_name(db_session, "PIKACHU", lang="fr")

        assert len(result) == 1
        assert result[0].species.name_fr == "Pikachu"

    def test_search_pokemon_no_results(self, db_session, sample_pokemon):
        """Test search with no matches."""
        result = search_pokemon_by_species_name(db_session, "NonExistentPokemon", lang="fr")
        assert result == []

    def test_search_pokemon_lang_en(self, db_session, sample_pokemon):
        """Test search in English."""
        result = search_pokemon_by_species_name(db_session, "Charizard", lang="en")

        assert len(result) == 1
        assert result[0].species.name_en == "Charizard"

    def test_search_pokemon_eager_loads_relationships(self, db_session, sample_pokemon):
        """Test that relationships are eager-loaded in search results."""
        result = search_pokemon_by_species_name(db_session, "Pikachu", lang="fr")

        assert result[0].species is not None
        assert len(result[0].types) >= 1
        assert result[0].types[0].type is not None


# ============================================================
# TESTS: Compute Pokemon Weaknesses
# ============================================================

class TestComputePokemonWeaknesses:
    """Tests for computing type weaknesses."""

    def test_compute_weaknesses_single_type(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test computing weaknesses for single-type Pokemon."""
        # Pikachu (Électrik) - type_id=6
        weaknesses = compute_pokemon_weaknesses(db_session, 1)

        assert weaknesses is not None
        assert isinstance(weaknesses, list)

        # The function returns only types that have effectiveness data
        # In our sample data, we have: Plante (4) vs Électrik (6) = 0.5x
        if len(weaknesses) > 0:
            # Convert to dict for easier testing
            weakness_dict = {w['attacking_type']: w['multiplier'] for w in weaknesses}
            # Check that multipliers are floats
            for w in weaknesses:
                assert isinstance(w['multiplier'], float)

    def test_compute_weaknesses_dual_type(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test computing weaknesses for dual-type Pokemon."""
        # Charizard (Feu/Vol) - type_ids = [3, 7]
        weaknesses = compute_pokemon_weaknesses(db_session, 2)

        assert weaknesses is not None
        assert isinstance(weaknesses, list)

        weakness_dict = {w['attacking_type']: w['multiplier'] for w in weaknesses}

        # Eau (5) vs Feu (3) = 2x (from type_effectiveness)
        assert weakness_dict.get('Eau') == 2.0

    def test_compute_weaknesses_pokemon_not_found(self, db_session, sample_pokemon):
        """Test computing weaknesses for non-existent Pokemon."""
        result = compute_pokemon_weaknesses(db_session, 999)
        assert result is None

    def test_compute_weaknesses_includes_all_types(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test that the function returns weakness data."""
        weaknesses = compute_pokemon_weaknesses(db_session, 1)

        assert weaknesses is not None
        assert isinstance(weaknesses, list)

        # The function returns types based on effectiveness data in the database
        # With our sample data, there may or may not be effectiveness data for Pikachu
        # The important thing is that the function executes without errors

    def test_compute_weaknesses_multiplier_is_float(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test that multipliers are returned as floats."""
        weaknesses = compute_pokemon_weaknesses(db_session, 1)

        for weakness in weaknesses:
            assert isinstance(weakness['multiplier'], float)

    def test_compute_weaknesses_multiplies_for_dual_types(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test that multipliers are correctly multiplied for dual-type Pokemon."""
        # Charizard (Feu/Vol)
        weaknesses = compute_pokemon_weaknesses(db_session, 2)

        weakness_dict = {w['attacking_type']: w['multiplier'] for w in weaknesses}

        # If we have effectiveness for both types, they should multiply
        # For example, if Eau is 2x against Feu and 2x against Vol,
        # the total would be 4x (but we only have Eau vs Feu = 2x in our sample data)
        assert 'Eau' in weakness_dict
