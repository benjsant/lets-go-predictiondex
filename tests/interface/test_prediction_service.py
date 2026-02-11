"""
Tests for Interface Prediction Service
=======================================

Tests for Streamlit's prediction service layer.
Critical for C10 (Integration dans application).

Validation:
- Mock prediction logic works
- Score calculation correct
- Output format valid
- Edge cases handled
"""

import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from interface.services.prediction_service import predict_battle_mock
from interface.formatters.ui.pokemon_ui import PokemonSelectItem
from interface.formatters.ui.move_ui import MoveSelectItem


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def pokemon_a():
    """Create Pokemon A (Pikachu) for testing."""
    return PokemonSelectItem(
        id=25,
        name="Pikachu",
        sprite_url="https://example.com/pikachu.png",
        types=["electrik"],
        total_stats=320,
    )


@pytest.fixture
def pokemon_b():
    """Create Pokemon B (Dracaufeu) for testing."""
    return PokemonSelectItem(
        id=6,
        name="Dracaufeu",
        sprite_url="https://example.com/dracaufeu.png",
        types=["feu", "vol"],
        total_stats=534,
    )


@pytest.fixture
def moves_a():
    """Create moves list for Pokemon A."""
    return [
        MoveSelectItem(name="Tonnerre", label="Tonnerre (90)", type="electrik", power=90, category="special"),
        MoveSelectItem(name="Vive-Attaque", label="Vive-Attaque (40)", type="normal", power=40, category="physical"),
    ]


@pytest.fixture
def moves_b():
    """Create moves list for Pokemon B."""
    return [
        MoveSelectItem(name="Lance-Flammes", label="Lance-Flammes (90)", type="feu", power=90, category="special"),
        MoveSelectItem(name="Cru-Ailes", label="Cru-Ailes (60)", type="vol", power=60, category="physical"),
    ]


# ============================================================
# TESTS: Prediction Output Format
# ============================================================

class TestPredictionOutput:
    """Tests for prediction output structure."""

    def test_returns_dict(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that prediction returns a dictionary."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        assert isinstance(result, dict)

    def test_contains_winner(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that result contains winner field."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        assert 'winner' in result
        assert result['winner'] in [pokemon_a.name, pokemon_b.name]

    def test_contains_message(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that result contains message field."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        assert 'message' in result
        assert isinstance(result['message'], str)
        assert len(result['message']) > 0

    def test_contains_probabilities(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that result contains probabilities for both Pokemon."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        assert 'probabilities' in result
        probs = result['probabilities']
        assert pokemon_a.name in probs
        assert pokemon_b.name in probs

    def test_probabilities_sum_to_one(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that probabilities sum to approximately 1."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        probs = result['probabilities']
        total = sum(probs.values())
        assert abs(total - 1.0) < 0.05 # rounding tolerance

    def test_contains_debug_info(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that result contains debug information."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        assert 'debug' in result
        assert 'pokemon_1_score' in result['debug']
        assert 'pokemon_2_score' in result['debug']


# ============================================================
# TESTS: Score Calculation
# ============================================================

class TestScoreCalculation:
    """Tests for score calculation logic."""

    def test_higher_stats_pokemon_tends_to_win(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that Pokemon with higher stats wins more often."""
        wins_b = 0
        trials = 100

        for _ in range(trials):
            result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)
            if result['winner'] == pokemon_b.name:
                wins_b += 1

        # Dracaufeu (534 stats) should win more than Pikachu (320 stats)
        assert wins_b > trials * 0.5, "Higher stats Pokemon should win more often"

    def test_scores_are_positive(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that calculated scores are positive."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        assert result['debug']['pokemon_1_score'] > 0
        assert result['debug']['pokemon_2_score'] > 0

    def test_probabilities_in_valid_range(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that probabilities are between 0 and 1."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        for name, prob in result['probabilities'].items():
            assert 0.0 <= prob <= 1.0, f"Probability for {name} should be between 0 and 1"


# ============================================================
# TESTS: Edge Cases
# ============================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_zero_power_moves(self, pokemon_a, pokemon_b):
        """Test with moves that have zero power."""
        zero_moves = [
            MoveSelectItem(name="Rugissement", label="Rugissement", type="normal", power=0, category="autre"),
        ]

        result = predict_battle_mock(pokemon_a, zero_moves, pokemon_b, zero_moves)

        assert 'winner' in result
        assert result['winner'] in [pokemon_a.name, pokemon_b.name]

    def test_none_power_moves(self, pokemon_a, pokemon_b):
        """Test with moves that have None power (status moves)."""
        none_moves = [
            MoveSelectItem(name="Toxik", label="Toxik", type="poison", power=None, category="autre"),
        ]

        result = predict_battle_mock(pokemon_a, none_moves, pokemon_b, none_moves)

        assert 'winner' in result

    def test_none_total_stats(self, pokemon_b, moves_a, moves_b):
        """Test with Pokemon that has None total_stats."""
        pokemon_no_stats = PokemonSelectItem(
            id=1,
            name="Bulbizarre",
            types=["plante"],
            total_stats=None,
        )

        result = predict_battle_mock(pokemon_no_stats, moves_a, pokemon_b, moves_b)

        assert 'winner' in result # Should fallback to 300

    def test_message_contains_winner_name(self, pokemon_a, pokemon_b, moves_a, moves_b):
        """Test that message mentions the winner."""
        result = predict_battle_mock(pokemon_a, moves_a, pokemon_b, moves_b)

        assert result['winner'] in result['message']


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
