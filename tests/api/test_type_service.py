"""
Tests for type service
======================

Unit tests for Type service layer.

Coverage target: 80%+
"""

import pytest

from api_pokemon.services.type_service import (
    normalize,
    find_type_by_name,
    list_types,
    get_type_affinities,
    get_type_affinities_by_name,
    list_pokemon_by_type,
    list_pokemon_by_type_name,
)


# ============================================================
# 🔹 TESTS: Text Normalization
# ============================================================

class TestNormalize:
    """Tests for text normalization utility."""

    def test_normalize_lowercase(self):
        """Test that text is converted to lowercase."""
        assert normalize("HELLO") == "hello"
        assert normalize("Normal") == "normal"

    def test_normalize_removes_accents(self):
        """Test that accents are removed."""
        assert normalize("Ténèbres") == "tenebres"
        assert normalize("Fée") == "fee"
        assert normalize("Électrik") == "electrik"

    def test_normalize_combined(self):
        """Test lowercase + accent removal combined."""
        assert normalize("ÉLECTRIK") == "electrik"
        assert normalize("Fée") == "fee"

    def test_normalize_empty_string(self):
        """Test empty string."""
        assert normalize("") == ""


# ============================================================
# 🔹 TESTS: Find Type by Name
# ============================================================

class TestFindTypeByName:
    """Tests for finding type by name with tolerant matching."""

    def test_find_type_exact_match(self, db_session, sample_types):
        """Test exact name match."""
        type_obj = find_type_by_name(db_session, "Feu")

        assert type_obj is not None
        assert type_obj.name == "Feu"

    def test_find_type_case_insensitive(self, db_session, sample_types):
        """Test case-insensitive matching."""
        type_obj = find_type_by_name(db_session, "FEU")

        assert type_obj is not None
        assert type_obj.name == "Feu"

    def test_find_type_accent_insensitive(self, db_session, sample_types):
        """Test accent-insensitive matching."""
        type_obj = find_type_by_name(db_session, "Electrik")

        assert type_obj is not None
        assert type_obj.name == "Électrik"

    def test_find_type_prefix_match(self, db_session, sample_types):
        """Test prefix-based matching."""
        type_obj = find_type_by_name(db_session, "Fe")

        assert type_obj is not None
        assert type_obj.name == "Feu"

    def test_find_type_not_found(self, db_session, sample_types):
        """Test with non-existent type."""
        type_obj = find_type_by_name(db_session, "NonExistentType")
        assert type_obj is None


# ============================================================
# 🔹 TESTS: List Types
# ============================================================

class TestListTypes:
    """Tests for listing all types."""

    def test_list_types_returns_all(self, db_session, sample_types):
        """Test that list_types returns all types."""
        result = list_types(db_session)

        assert len(result) == 8  # All sample types
        type_names = [t.name for t in result]
        assert "Feu" in type_names
        assert "Eau" in type_names
        assert "Électrik" in type_names

    def test_list_types_ordered_by_id(self, db_session, sample_types):
        """Test that types are ordered by ID."""
        result = list_types(db_session)

        for i in range(len(result) - 1):
            assert result[i].id < result[i + 1].id

    def test_list_types_empty_database(self, db_session):
        """Test list_types with empty database."""
        result = list_types(db_session)
        assert result == []


# ============================================================
# 🔹 TESTS: Get Type Affinities
# ============================================================

class TestGetTypeAffinities:
    """Tests for retrieving type effectiveness relationships."""

    def test_get_all_affinities(self, db_session, sample_type_effectiveness):
        """Test retrieving all type affinities."""
        result = get_type_affinities(db_session)

        assert len(result) == 8  # All sample effectiveness records

    def test_get_affinities_filter_by_attacking_type(
        self,
        db_session,
        sample_type_effectiveness
    ):
        """Test filtering by attacking type."""
        # Feu (id=3) attacking
        result = get_type_affinities(db_session, attacking_type_id=3)

        assert len(result) >= 1
        for affinity in result:
            assert affinity.attacking_type_id == 3

    def test_get_affinities_filter_by_defending_type(
        self,
        db_session,
        sample_type_effectiveness
    ):
        """Test filtering by defending type."""
        # Eau (id=5) defending
        result = get_type_affinities(db_session, defending_type_id=5)

        assert len(result) >= 1
        for affinity in result:
            assert affinity.defending_type_id == 5

    def test_get_affinities_filter_both_types(
        self,
        db_session,
        sample_type_effectiveness
    ):
        """Test filtering by both attacking and defending types."""
        # Feu (3) vs Plante (4)
        result = get_type_affinities(
            db_session,
            attacking_type_id=3,
            defending_type_id=4
        )

        assert len(result) == 1
        assert result[0].attacking_type_id == 3
        assert result[0].defending_type_id == 4
        assert result[0].multiplier == 2.0

    def test_get_affinities_no_match(self, db_session, sample_type_effectiveness):
        """Test when no affinities match the filter."""
        result = get_type_affinities(db_session, attacking_type_id=999)
        assert result == []


# ============================================================
# 🔹 TESTS: Get Type Affinities by Name
# ============================================================

class TestGetTypeAffinitiesByName:
    """Tests for retrieving type effectiveness by name."""

    def test_get_affinities_by_attacking_type_name(
        self,
        db_session,
        sample_types,
        sample_type_effectiveness
    ):
        """Test filtering by attacking type name."""
        result = get_type_affinities_by_name(db_session, attacking_type_name="Feu")

        assert len(result) >= 1
        # All results should have Feu (id=3) as attacking type
        for affinity in result:
            assert affinity.attacking_type_id == 3

    def test_get_affinities_by_defending_type_name(
        self,
        db_session,
        sample_types,
        sample_type_effectiveness
    ):
        """Test filtering by defending type name."""
        result = get_type_affinities_by_name(db_session, defending_type_name="Eau")

        assert len(result) >= 1
        # All results should have Eau (id=5) as defending type
        for affinity in result:
            assert affinity.defending_type_id == 5

    def test_get_affinities_by_both_type_names(
        self,
        db_session,
        sample_types,
        sample_type_effectiveness
    ):
        """Test filtering by both type names."""
        result = get_type_affinities_by_name(
            db_session,
            attacking_type_name="Feu",
            defending_type_name="Plante"
        )

        assert len(result) == 1
        assert result[0].attacking_type_id == 3  # Feu
        assert result[0].defending_type_id == 4  # Plante
        assert result[0].multiplier == 2.0

    def test_get_affinities_case_insensitive(
        self,
        db_session,
        sample_types,
        sample_type_effectiveness
    ):
        """Test case-insensitive type name matching."""
        result = get_type_affinities_by_name(
            db_session,
            attacking_type_name="FEU"
        )

        assert len(result) >= 1

    def test_get_affinities_accent_insensitive(
        self,
        db_session,
        sample_types,
        sample_type_effectiveness
    ):
        """Test accent-insensitive type name matching."""
        result = get_type_affinities_by_name(
            db_session,
            attacking_type_name="Electrik"  # Without accent
        )

        assert len(result) >= 1

    def test_get_affinities_nonexistent_type_name(
        self,
        db_session,
        sample_types,
        sample_type_effectiveness
    ):
        """Test with non-existent type name."""
        result = get_type_affinities_by_name(
            db_session,
            attacking_type_name="NonExistent"
        )

        # Should return all affinities (no filter applied)
        assert len(result) >= 1


# ============================================================
# 🔹 TESTS: List Pokemon by Type
# ============================================================

class TestListPokemonByType:
    """Tests for listing Pokemon by type."""

    def test_list_pokemon_by_type_id(self, db_session, sample_pokemon):
        """Test listing Pokemon by type ID."""
        # Électrik type (id=6) - Pikachu
        result = list_pokemon_by_type(db_session, type_id=6)

        assert len(result) == 1
        assert result[0].species.name_en == "Pikachu"

    def test_list_pokemon_by_type_dual_type(self, db_session, sample_pokemon):
        """Test listing Pokemon that have type in slot 2."""
        # Vol type (id=7) - Charizard (Feu/Vol)
        result = list_pokemon_by_type(db_session, type_id=7)

        assert len(result) == 1
        assert result[0].species.name_en == "Charizard"

    def test_list_pokemon_by_type_multiple_pokemon(self, db_session, sample_pokemon):
        """Test type shared by multiple Pokemon."""
        # If we had multiple Water-type Pokemon, they would all be returned
        result = list_pokemon_by_type(db_session, type_id=5)  # Eau

        assert len(result) >= 1  # At least Blastoise

    def test_list_pokemon_by_type_no_match(self, db_session, sample_pokemon):
        """Test type with no Pokemon."""
        result = list_pokemon_by_type(db_session, type_id=999)
        assert result == []

    def test_list_pokemon_by_type_eager_loads_relationships(
        self,
        db_session,
        sample_pokemon
    ):
        """Test that relationships are eager-loaded."""
        result = list_pokemon_by_type(db_session, type_id=6)

        assert result[0].species is not None
        assert result[0].types is not None
        assert len(result[0].types) >= 1

    def test_list_pokemon_by_type_ordered_by_id(self, db_session, sample_pokemon):
        """Test that Pokemon are ordered by ID."""
        result = list_pokemon_by_type(db_session, type_id=6)

        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i].id < result[i + 1].id


# ============================================================
# 🔹 TESTS: List Pokemon by Type Name
# ============================================================

class TestListPokemonByTypeName:
    """Tests for listing Pokemon by type name."""

    def test_list_pokemon_by_type_name(self, db_session, sample_pokemon, sample_types):
        """Test listing Pokemon by type name."""
        result = list_pokemon_by_type_name(db_session, "Électrik")

        assert len(result) == 1
        assert result[0].species.name_en == "Pikachu"

    def test_list_pokemon_by_type_name_case_insensitive(
        self,
        db_session,
        sample_pokemon,
        sample_types
    ):
        """Test case-insensitive type name matching."""
        result = list_pokemon_by_type_name(db_session, "ÉLECTRIK")

        assert len(result) == 1

    def test_list_pokemon_by_type_name_accent_insensitive(
        self,
        db_session,
        sample_pokemon,
        sample_types
    ):
        """Test accent-insensitive type name matching."""
        result = list_pokemon_by_type_name(db_session, "Electrik")

        assert len(result) == 1

    def test_list_pokemon_by_type_name_prefix_match(
        self,
        db_session,
        sample_pokemon,
        sample_types
    ):
        """Test prefix-based type name matching."""
        result = list_pokemon_by_type_name(db_session, "Ele")

        assert len(result) >= 1

    def test_list_pokemon_by_type_name_nonexistent_type(
        self,
        db_session,
        sample_pokemon,
        sample_types
    ):
        """Test with non-existent type name."""
        result = list_pokemon_by_type_name(db_session, "NonExistent")
        assert result == []
