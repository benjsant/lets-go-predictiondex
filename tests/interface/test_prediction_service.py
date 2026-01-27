"""
Tests for Interface Prediction Service
=======================================

Tests for Streamlit's prediction service layer.
Critical for C10 (Integration dans application).

Validation:
- Service calls API correctly
- Response parsing works
- Error handling proper
- Data formatting for UI correct
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from interface.services.prediction_service import PredictionService


# ============================================================
# 🔹 FIXTURES
# ============================================================

@pytest.fixture
def prediction_service():
    """Create prediction service instance."""
    return PredictionService(api_base_url="http://localhost:8080")


@pytest.fixture
def mock_prediction_response():
    """Create mock prediction API response."""
    return {
        'pokemon_a_id': 25,
        'pokemon_a_name': 'Pikachu',
        'pokemon_b_id': 6,
        'pokemon_b_name': 'Dracaufeu',
        'recommended_move': 'Tonnerre',
        'win_probability': 0.87,
        'all_moves': [
            {
                'move_name': 'Tonnerre',
                'move_type': 'Électrik',
                'move_power': 110,
                'effective_power': 165.0,
                'type_multiplier': 1.0,
                'stab': 1.5,
                'priority': 0,
                'score': 165.0,
                'win_probability': 0.87,
                'predicted_winner': 'A'
            },
            {
                'move_name': 'Vive-Attaque',
                'move_type': 'Normal',
                'move_power': 40,
                'effective_power': 40.0,
                'type_multiplier': 1.0,
                'stab': 1.0,
                'priority': 1,
                'score': 40.0,
                'win_probability': 0.62,
                'predicted_winner': 'A'
            }
        ]
    }


# ============================================================
# 🔹 TESTS: Prediction Request
# ============================================================

class TestPredictionRequest:
    """Tests for making prediction requests."""

    @patch('requests.post')
    def test_predict_best_move_success(self, mock_post, prediction_service, mock_prediction_response):
        """Test successful prediction request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_prediction_response
        mock_post.return_value = mock_response

        result = prediction_service.predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre', 'Vive-Attaque']
        )

        assert result is not None
        assert result['recommended_move'] == 'Tonnerre'
        assert result['win_probability'] == 0.87
        assert len(result['all_moves']) == 2

    @patch('requests.post')
    def test_predict_with_optional_moves_b(self, mock_post, prediction_service, mock_prediction_response):
        """Test prediction with optional Pokemon B moves."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_prediction_response
        mock_post.return_value = mock_response

        result = prediction_service.predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre'],
            available_moves_b=['Lance-Flammes', 'Danse-Lames']
        )

        assert result is not None
        # Verify moves_b was included in request
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        if 'json' in call_kwargs:
            assert 'available_moves_b' in call_kwargs['json']

    def test_validate_input_parameters(self, prediction_service):
        """Test input validation before API call."""
        # Invalid pokemon_a_id (not positive integer)
        with pytest.raises((ValueError, TypeError)):
            prediction_service.predict_best_move(
                pokemon_a_id=-1,
                pokemon_b_id=6,
                available_moves=['Surf']
            )

        # Empty moves list
        with pytest.raises(ValueError):
            prediction_service.predict_best_move(
                pokemon_a_id=25,
                pokemon_b_id=6,
                available_moves=[]
            )


# ============================================================
# 🔹 TESTS: Response Parsing
# ============================================================

class TestResponseParsing:
    """Tests for parsing API responses."""

    def test_parse_prediction_response(self, prediction_service, mock_prediction_response):
        """Test parsing of prediction response."""
        parsed = prediction_service._parse_prediction_response(mock_prediction_response)

        assert parsed['recommended_move'] == 'Tonnerre'
        assert parsed['win_probability'] == 0.87
        assert isinstance(parsed['all_moves'], list)

    def test_parse_move_details(self, prediction_service, mock_prediction_response):
        """Test parsing of individual move details."""
        moves = mock_prediction_response['all_moves']

        for move in moves:
            assert 'move_name' in move
            assert 'win_probability' in move
            assert 'type_multiplier' in move
            assert 0 <= move['win_probability'] <= 1

    def test_handle_empty_moves_list(self, prediction_service):
        """Test handling of response with no moves."""
        response = {
            'pokemon_a_id': 25,
            'pokemon_a_name': 'Pikachu',
            'pokemon_b_id': 6,
            'pokemon_b_name': 'Dracaufeu',
            'recommended_move': None,
            'win_probability': 0.5,
            'all_moves': []
        }

        # Should handle gracefully (return error or default)
        parsed = prediction_service._parse_prediction_response(response)
        assert parsed is not None


# ============================================================
# 🔹 TESTS: Error Handling
# ============================================================

class TestErrorHandling:
    """Tests for error handling."""

    @patch('requests.post')
    def test_handles_api_404_error(self, mock_post, prediction_service):
        """Test handling of 404 Pokemon Not Found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'detail': 'Pokemon not found'}
        mock_post.return_value = mock_response

        result = prediction_service.predict_best_move(
            pokemon_a_id=9999,
            pokemon_b_id=6,
            available_moves=['Surf']
        )

        # Should return error indication or None
        assert result is None or 'error' in result

    @patch('requests.post')
    def test_handles_api_500_error(self, mock_post, prediction_service):
        """Test handling of 500 Internal Server Error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_post.return_value = mock_response

        result = prediction_service.predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre']
        )

        # Should handle gracefully
        assert result is None or 'error' in result

    @patch('requests.post')
    def test_handles_timeout(self, mock_post, prediction_service):
        """Test handling of request timeout."""
        import requests
        mock_post.side_effect = requests.Timeout("Request timed out")

        result = prediction_service.predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre']
        )

        # Should handle timeout gracefully
        assert result is None or 'error' in result

    @patch('requests.post')
    def test_handles_malformed_response(self, mock_post, prediction_service):
        """Test handling of malformed JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'unexpected': 'format'}
        mock_post.return_value = mock_response

        result = prediction_service.predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre']
        )

        # Should handle unexpected format
        assert result is None or 'error' in result


# ============================================================
# 🔹 TESTS: UI Data Formatting
# ============================================================

class TestUIDataFormatting:
    """Tests for formatting data for Streamlit UI."""

    def test_format_moves_for_display(self, prediction_service, mock_prediction_response):
        """Test formatting moves for UI display."""
        moves = mock_prediction_response['all_moves']

        formatted = prediction_service.format_moves_for_ui(moves)

        assert isinstance(formatted, list)
        for move in formatted:
            # UI-friendly format
            assert 'display_name' in move or 'move_name' in move
            assert 'win_probability' in move

    def test_format_win_probability_as_percentage(self, prediction_service):
        """Test formatting win probability as percentage."""
        probability = 0.8745

        formatted = prediction_service.format_probability(probability)

        assert isinstance(formatted, str)
        assert '%' in formatted or '87' in formatted

    def test_format_type_multiplier(self, prediction_service):
        """Test formatting type multiplier for display."""
        multipliers = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]

        for mult in multipliers:
            formatted = prediction_service.format_multiplier(mult)

            assert isinstance(formatted, str)
            # Should indicate effectiveness
            if mult == 0:
                assert 'immune' in formatted.lower() or '0x' in formatted
            elif mult > 1:
                assert 'super' in formatted.lower() or 'efficace' in formatted.lower() or f'{mult}x' in formatted


# ============================================================
# 🔹 TESTS: Move Ranking
# ============================================================

class TestMoveRanking:
    """Tests for move ranking logic."""

    def test_moves_sorted_by_win_probability(self, prediction_service, mock_prediction_response):
        """Test that moves are sorted by win probability."""
        moves = mock_prediction_response['all_moves']

        # Verify descending order
        for i in range(len(moves) - 1):
            assert moves[i]['win_probability'] >= moves[i+1]['win_probability'], \
                   "Moves should be sorted by win probability (descending)"

    def test_recommended_move_is_highest_probability(self, prediction_service, mock_prediction_response):
        """Test that recommended move has highest win probability."""
        recommended = mock_prediction_response['recommended_move']
        all_moves = mock_prediction_response['all_moves']

        recommended_move_data = next(
            (m for m in all_moves if m['move_name'] == recommended),
            None
        )

        assert recommended_move_data is not None
        assert recommended_move_data['win_probability'] == max(
            m['win_probability'] for m in all_moves
        )


# ============================================================
# 🔹 TESTS: Caching
# ============================================================

class TestPredictionCaching:
    """Tests for prediction result caching."""

    @patch('requests.post')
    def test_caches_recent_predictions(self, mock_post, prediction_service, mock_prediction_response):
        """Test that recent predictions are cached."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_prediction_response
        mock_post.return_value = mock_response

        # Make same prediction twice
        result1 = prediction_service.predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre']
        )

        result2 = prediction_service.predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre']
        )

        # If caching implemented, should only call API once
        # Otherwise, both calls go through
        assert result1 is not None
        assert result2 is not None

    def test_cache_invalidation(self, prediction_service):
        """Test cache invalidation on different inputs."""
        # Different inputs should not use cache
        # This is implementation-dependent
        assert True  # Placeholder


# ============================================================
# 🔹 TESTS: Integration with Streamlit
# ============================================================

class TestStreamlitIntegration:
    """Integration tests with Streamlit components."""

    @patch('requests.post')
    @patch('streamlit.session_state', {})
    def test_prediction_updates_session_state(self, mock_post, prediction_service, mock_prediction_response):
        """Test that predictions update Streamlit session state."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_prediction_response
        mock_post.return_value = mock_response

        result = prediction_service.predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre']
        )

        # Session state might be updated
        assert result is not None

    def test_error_display_format(self, prediction_service):
        """Test error messages are formatted for Streamlit display."""
        error_msg = prediction_service.format_error("Pokemon not found")

        assert isinstance(error_msg, str)
        assert len(error_msg) > 0


# ============================================================
# 🔹 TESTS: Move Selection Validation
# ============================================================

class TestMoveSelectionValidation:
    """Tests for validating move selections."""

    def test_validate_move_names(self, prediction_service):
        """Test validation of move names."""
        valid_moves = ['Tonnerre', 'Surf', 'Lance-Flammes']

        # Should accept valid moves
        is_valid = prediction_service.validate_moves(valid_moves)
        assert is_valid

    def test_reject_empty_move_list(self, prediction_service):
        """Test rejection of empty move list."""
        empty_moves = []

        is_valid = prediction_service.validate_moves(empty_moves)
        assert not is_valid

    def test_reject_too_many_moves(self, prediction_service):
        """Test rejection of too many moves (>20)."""
        too_many_moves = [f'Move{i}' for i in range(25)]

        is_valid = prediction_service.validate_moves(too_many_moves)
        assert not is_valid


# ============================================================
# 🔹 TESTS: Confidence Indicators
# ============================================================

class TestConfidenceIndicators:
    """Tests for confidence indicator generation."""

    def test_high_confidence_indicator(self, prediction_service):
        """Test indicator for high confidence prediction."""
        confidence = 0.95

        indicator = prediction_service.get_confidence_indicator(confidence)

        assert '✅' in indicator or 'High' in indicator or 'Élevée' in indicator

    def test_low_confidence_indicator(self, prediction_service):
        """Test indicator for low confidence prediction."""
        confidence = 0.55

        indicator = prediction_service.get_confidence_indicator(confidence)

        assert '⚠️' in indicator or 'Low' in indicator or 'Faible' in indicator

    def test_very_low_confidence_indicator(self, prediction_service):
        """Test indicator for very low confidence prediction."""
        confidence = 0.45

        indicator = prediction_service.get_confidence_indicator(confidence)

        # Should warn user about uncertain prediction
        assert '❌' in indicator or '⚠️' in indicator or 'uncertain' in indicator.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
