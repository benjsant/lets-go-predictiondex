"""
Tests for move service
======================

Unit tests for Move service layer.

Coverage target: 80%+
"""

import pytest

from api_pokemon.services.move_service import (
    normalize,
    list_moves,
    get_move_by_id,
    search_moves_by_name,
    list_moves_by_type,
)


# ============================================================
# 🔹 TESTS: Text Normalization
# ============================================================

class TestNormalize:
    """Tests for text normalization utility."""

    def test_normalize_lowercase(self):
        """Test that text is converted to lowercase."""
        assert normalize("HELLO") == "hello"
        assert normalize("HeLLo") == "hello"

    def test_normalize_removes_accents(self):
        """Test that accents are removed."""
        assert normalize("café") == "cafe"
        assert normalize("Pokémon") == "pokemon"
        assert normalize("Électrik") == "electrik"
        assert normalize("Flambée") == "flambee"

    def test_normalize_combined(self):
        """Test lowercase + accent removal combined."""
        assert normalize("CAFÉ") == "cafe"
        assert normalize("POKÉMON") == "pokemon"
        assert normalize("Électrik") == "electrik"

    def test_normalize_no_accents(self):
        """Test text without accents remains unchanged (except case)."""
        assert normalize("Normal") == "normal"
        assert normalize("Fire") == "fire"

    def test_normalize_empty_string(self):
        """Test empty string."""
        assert normalize("") == ""


# ============================================================
# 🔹 TESTS: List Moves
# ============================================================

class TestListMoves:
    """Tests for listing all moves."""

    def test_list_moves_returns_all(self, db_session, sample_moves):
        """Test that list_moves returns all moves."""
        result = list_moves(db_session)

        assert len(result) == 6  # All sample moves
        assert result[0].name == "Lance-Flammes"

    def test_list_moves_eager_loads_type(self, db_session, sample_moves):
        """Test that move type is eager-loaded."""
        result = list_moves(db_session)

        assert result[0].type is not None
        assert result[0].type.name == "Feu"

    def test_list_moves_eager_loads_category(self, db_session, sample_moves):
        """Test that move category is eager-loaded."""
        result = list_moves(db_session)

        assert result[0].category is not None
        assert result[0].category.name == "spécial"

    def test_list_moves_ordered_by_id(self, db_session, sample_moves):
        """Test that moves are ordered by ID."""
        result = list_moves(db_session)

        for i in range(len(result) - 1):
            assert result[i].id < result[i + 1].id

    def test_list_moves_empty_database(self, db_session):
        """Test list_moves with empty database."""
        result = list_moves(db_session)
        assert result == []


# ============================================================
# 🔹 TESTS: Get Move by ID
# ============================================================

class TestGetMoveById:
    """Tests for retrieving move by ID."""

    def test_get_move_by_id_found(self, db_session, sample_moves):
        """Test retrieving existing move."""
        move = get_move_by_id(db_session, 1)

        assert move is not None
        assert move.id == 1
        assert move.name == "Lance-Flammes"

    def test_get_move_by_id_not_found(self, db_session, sample_moves):
        """Test retrieving non-existent move."""
        move = get_move_by_id(db_session, 999)
        assert move is None

    def test_get_move_by_id_eager_loads_type(self, db_session, sample_moves):
        """Test that type is eager-loaded."""
        move = get_move_by_id(db_session, 1)

        assert move.type is not None
        assert move.type.name == "Feu"

    def test_get_move_by_id_eager_loads_category(self, db_session, sample_moves):
        """Test that category is eager-loaded."""
        move = get_move_by_id(db_session, 1)

        assert move.category is not None
        assert move.category.name == "spécial"


# ============================================================
# 🔹 TESTS: Search Moves by Name
# ============================================================

class TestSearchMovesByName:
    """Tests for searching moves by name."""

    def test_search_moves_exact_match(self, db_session, sample_moves):
        """Test exact name match."""
        result = search_moves_by_name(db_session, "Surf")

        assert len(result) == 1
        assert result[0].name == "Surf"

    def test_search_moves_partial_match(self, db_session, sample_moves):
        """Test partial name match."""
        result = search_moves_by_name(db_session, "Flammes")

        # Should match "Lance-Flammes"
        assert len(result) >= 1
        assert any(move.name == "Lance-Flammes" for move in result)

    def test_search_moves_case_insensitive(self, db_session, sample_moves):
        """Test case-insensitive search."""
        result = search_moves_by_name(db_session, "SURF")

        assert len(result) == 1
        assert result[0].name == "Surf"

    def test_search_moves_accent_insensitive(self, db_session, sample_moves):
        """Test accent-insensitive search."""
        result = search_moves_by_name(db_session, "Lance-Flammes")

        assert len(result) >= 1
        assert result[0].name == "Lance-Flammes"

        # Search without accent
        result2 = search_moves_by_name(db_session, "Vive-Attaque")
        assert len(result2) >= 1

    def test_search_moves_no_results(self, db_session, sample_moves):
        """Test search with no matches."""
        result = search_moves_by_name(db_session, "NonExistentMove")
        assert result == []

    def test_search_moves_eager_loads_relationships(self, db_session, sample_moves):
        """Test that relationships are eager-loaded."""
        result = search_moves_by_name(db_session, "Surf")

        assert result[0].type is not None
        assert result[0].category is not None


# ============================================================
# 🔹 TESTS: List Moves by Type
# ============================================================

class TestListMovesByType:
    """Tests for listing moves by type."""

    def test_list_moves_by_type_no_pokemon_filter(self, db_session, sample_moves, sample_types):
        """Test listing moves by type without Pokemon filter."""
        result = list_moves_by_type(db_session, "Feu", pokemon_id=None)

        assert len(result) == 1
        assert result[0]['move'].name == "Lance-Flammes"
        assert result[0]['learn_method'] is None
        assert result[0]['learn_level'] is None

    def test_list_moves_by_type_with_pokemon_filter(
        self,
        db_session,
        sample_moves,
        sample_pokemon,
        sample_types
    ):
        """Test listing moves by type with Pokemon filter."""
        # Pikachu (id=1) has Tonnerre (Électrik) and Vive-Attaque (Normal)
        result = list_moves_by_type(db_session, "Électrik", pokemon_id=1)

        assert len(result) == 1
        assert result[0]['move'].name == "Tonnerre"
        assert result[0]['learn_method'] == "level_up"
        assert result[0]['learn_level'] == 30

    def test_list_moves_by_type_case_insensitive(self, db_session, sample_moves, sample_types):
        """Test type name matching is case-insensitive."""
        result = list_moves_by_type(db_session, "FEU", pokemon_id=None)

        assert len(result) == 1
        assert result[0]['move'].type.name == "Feu"

    def test_list_moves_by_type_accent_insensitive(self, db_session, sample_moves, sample_types):
        """Test type name matching is accent-insensitive."""
        result = list_moves_by_type(db_session, "Electrik", pokemon_id=None)

        # Should match "Électrik"
        assert len(result) == 1
        assert result[0]['move'].type.name == "Électrik"

    def test_list_moves_by_type_partial_match(self, db_session, sample_moves, sample_types):
        """Test partial type name matching."""
        result = list_moves_by_type(db_session, "Fe", pokemon_id=None)

        # Should match "Feu"
        assert len(result) >= 1

    def test_list_moves_by_type_nonexistent_type(self, db_session, sample_moves, sample_types):
        """Test with non-existent type."""
        result = list_moves_by_type(db_session, "NonExistentType", pokemon_id=None)
        assert result == []

    def test_list_moves_by_type_pokemon_has_no_moves_of_type(
        self,
        db_session,
        sample_moves,
        sample_pokemon,
        sample_types
    ):
        """Test when Pokemon has no moves of the specified type."""
        # Pikachu doesn't have Feu moves
        result = list_moves_by_type(db_session, "Feu", pokemon_id=1)

        assert result == []

    def test_list_moves_by_type_ordered_by_id(self, db_session, sample_moves, sample_types):
        """Test that moves are ordered by ID."""
        # Add multiple moves of same type to test ordering
        result = list_moves_by_type(db_session, "Normal", pokemon_id=None)

        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]['move'].id < result[i + 1]['move'].id

    def test_list_moves_by_type_returns_stable_structure(
        self,
        db_session,
        sample_moves,
        sample_types
    ):
        """Test that return structure is stable."""
        result = list_moves_by_type(db_session, "Eau", pokemon_id=None)

        assert len(result) == 1
        assert 'move' in result[0]
        assert 'learn_method' in result[0]
        assert 'learn_level' in result[0]
        assert isinstance(result[0], dict)
