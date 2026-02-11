"""
Tests for Streamlit API Client
===============================

Tests for interface's API client service.
Critical for C10 (Integration API dans application).

Validation:
- HTTP requests to API work
- Error handling (timeouts, 404, 500)
- Authentication headers sent
- Response parsing correct
"""

import pytest
import requests
from unittest.mock import Mock, patch
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from interface.services.api_client import (
    _get,
    _post,
    _get_headers,
    get_all_pokemon,
    get_pokemon_by_id,
    get_pokemon_weaknesses,
    search_pokemon,
    get_all_moves,
    get_move_by_id,
    get_moves_by_type,
    search_moves,
    get_all_types,
    get_type_affinities,
    get_type_affinities_by_name,
    predict_best_move,
    get_model_info,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def mock_successful_response():
    """Create mock successful HTTP response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'success'}
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture
def mock_error_response():
    """Create mock error HTTP response."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'
    mock_response.raise_for_status.side_effect = requests.HTTPError("500 Error")
    return mock_response


# ============================================================
# TESTS: Headers & Authentication
# ============================================================

class TestHeaders:
    """Tests for API headers construction."""

    @patch('interface.services.api_client.API_KEY', 'test_key_123')
    def test_headers_include_api_key(self):
        """Test that headers include API key when configured."""
        headers = _get_headers()
        assert headers.get("X-API-Key") == "test_key_123"

    @patch('interface.services.api_client.API_KEY', None)
    def test_headers_empty_without_api_key(self):
        """Test that headers are empty when no API key."""
        headers = _get_headers()
        assert "X-API-Key" not in headers

    @patch('interface.services.api_client.API_KEY', '')
    def test_headers_empty_with_blank_api_key(self):
        """Test that headers are empty with blank API key."""
        headers = _get_headers()
        assert "X-API-Key" not in headers


# ============================================================
# TESTS: GET Requests
# ============================================================

class TestGETRequests:
    """Tests for _get helper and GET endpoints."""

    @patch('interface.services.api_client.requests.get')
    def test_get_returns_json_on_success(self, mock_get):
        """Test _get returns parsed JSON on success."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'id': 1, 'name': 'Bulbizarre'}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = _get("/pokemon/")

        assert result == [{'id': 1, 'name': 'Bulbizarre'}]

    @patch('interface.services.api_client.requests.get')
    def test_get_returns_none_on_error(self, mock_get):
        """Test _get returns None on request error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = _get("/pokemon/")

        assert result is None

    @patch('interface.services.api_client.requests.get')
    def test_get_returns_none_on_timeout(self, mock_get):
        """Test _get returns None on timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        result = _get("/pokemon/")

        assert result is None

    @patch('interface.services.api_client.requests.get')
    def test_get_returns_none_on_http_error(self, mock_get):
        """Test _get returns None on HTTP error status."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_response

        result = _get("/pokemon/9999")

        assert result is None


# ============================================================
# TESTS: POST Requests
# ============================================================

class TestPOSTRequests:
    """Tests for _post helper."""

    @patch('interface.services.api_client.requests.post')
    def test_post_returns_json_on_success(self, mock_post):
        """Test _post returns parsed JSON on success."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'recommended_move': 'Tonnerre'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = _post("/predict/best-move", {"pokemon_a_id": 25, "pokemon_b_id": 6})

        assert result == {'recommended_move': 'Tonnerre'}

    @patch('interface.services.api_client.requests.post')
    def test_post_returns_none_on_error(self, mock_post):
        """Test _post returns None on request error."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = _post("/predict/best-move", {})

        assert result is None

    @patch('interface.services.api_client.requests.post')
    def test_post_returns_none_on_timeout(self, mock_post):
        """Test _post returns None on timeout."""
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

        result = _post("/predict/best-move", {})

        assert result is None


# ============================================================
# TESTS: Pokemon Endpoints
# ============================================================

class TestPokemonEndpoints:
    """Tests for Pokemon API endpoint wrappers."""

    @patch('interface.services.api_client._get')
    def test_get_all_pokemon(self, mock_get):
        """Test get_all_pokemon calls correct endpoint."""
        mock_get.return_value = [{'id': 1}, {'id': 25}]

        result = get_all_pokemon()

        mock_get.assert_called_once_with("/pokemon/")
        assert len(result) == 2

    @patch('interface.services.api_client._get')
    def test_get_pokemon_by_id(self, mock_get):
        """Test get_pokemon_by_id calls correct endpoint."""
        mock_get.return_value = {'id': 25, 'name': 'Pikachu'}

        result = get_pokemon_by_id(25)

        mock_get.assert_called_once_with("/pokemon/25")
        assert result['id'] == 25

    @patch('interface.services.api_client._get')
    def test_get_pokemon_weaknesses(self, mock_get):
        """Test get_pokemon_weaknesses calls correct endpoint."""
        mock_get.return_value = [{'attacking_type': 'Sol', 'multiplier': '2.0'}]

        result = get_pokemon_weaknesses(25)

        mock_get.assert_called_once_with("/pokemon/25/weaknesses")

    @patch('interface.services.api_client._get')
    def test_search_pokemon(self, mock_get):
        """Test search_pokemon calls correct endpoint."""
        mock_get.return_value = [{'id': 25, 'name': 'Pikachu'}]

        result = search_pokemon("Pikachu")

        mock_get.assert_called_once_with("/pokemon/search?name=Pikachu")


# ============================================================
# TESTS: Moves Endpoints
# ============================================================

class TestMovesEndpoints:
    """Tests for Moves API endpoint wrappers."""

    @patch('interface.services.api_client._get')
    def test_get_all_moves(self, mock_get):
        """Test get_all_moves calls correct endpoint."""
        mock_get.return_value = [{'id': 1, 'name': 'Tonnerre'}]

        result = get_all_moves()

        mock_get.assert_called_once_with("/moves/")

    @patch('interface.services.api_client._get')
    def test_get_move_by_id(self, mock_get):
        """Test get_move_by_id calls correct endpoint."""
        mock_get.return_value = {'id': 1, 'name': 'Tonnerre'}

        result = get_move_by_id(1)

        mock_get.assert_called_once_with("/moves/id/1")

    @patch('interface.services.api_client._get')
    def test_get_moves_by_type(self, mock_get):
        """Test get_moves_by_type calls correct endpoint."""
        mock_get.return_value = [{'id': 1, 'name': 'Tonnerre'}]

        result = get_moves_by_type("electrik")

        mock_get.assert_called_once_with("/moves/by-type/electrik")


# ============================================================
# TESTS: Types Endpoints
# ============================================================

class TestTypesEndpoints:
    """Tests for Types API endpoint wrappers."""

    @patch('interface.services.api_client._get')
    def test_get_all_types(self, mock_get):
        """Test get_all_types calls correct endpoint."""
        mock_get.return_value = [{'id': 1, 'name': 'Normal'}]

        result = get_all_types()

        mock_get.assert_called_once_with("/types/")

    @patch('interface.services.api_client._get')
    def test_get_type_affinities(self, mock_get):
        """Test get_type_affinities calls correct endpoint."""
        mock_get.return_value = [{'attacking_type_id': 1, 'defending_type_id': 2}]

        result = get_type_affinities()

        mock_get.assert_called_once_with("/types/affinities")

    @patch('interface.services.api_client._get')
    def test_get_type_affinities_by_name(self, mock_get):
        """Test get_type_affinities_by_name uses correct query params."""
        mock_get.return_value = [{'multiplier': '2.0'}]

        result = get_type_affinities_by_name("feu", "plante")

        mock_get.assert_called_once_with(
            "/types/affinities/by-name?attacking=feu&defending=plante"
        )


# ============================================================
# TESTS: Prediction Endpoints
# ============================================================

class TestPredictionEndpoints:
    """Tests for Prediction API endpoint wrappers."""

    @patch('interface.services.api_client._post')
    def test_predict_best_move(self, mock_post):
        """Test predict_best_move sends correct payload."""
        mock_post.return_value = {'recommended_move': 'Tonnerre', 'win_probability': 0.85}

        result = predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre', 'Vive-Attaque']
        )

        mock_post.assert_called_once_with(
            "/predict/best-move",
            {
                'pokemon_a_id': 25,
                'pokemon_b_id': 6,
                'available_moves': ['Tonnerre', 'Vive-Attaque'],
            }
        )
        assert result['recommended_move'] == 'Tonnerre'

    @patch('interface.services.api_client._post')
    def test_predict_best_move_with_moves_b(self, mock_post):
        """Test predict_best_move includes optional moves_b."""
        mock_post.return_value = {'recommended_move': 'Tonnerre'}

        result = predict_best_move(
            pokemon_a_id=25,
            pokemon_b_id=6,
            available_moves=['Tonnerre'],
            available_moves_b=['Lance-Flammes']
        )

        call_args = mock_post.call_args
        payload = call_args[0][1]
        assert 'available_moves_b' in payload
        assert payload['available_moves_b'] == ['Lance-Flammes']

    @patch('interface.services.api_client._get')
    def test_get_model_info(self, mock_get):
        """Test get_model_info calls correct endpoint."""
        mock_get.return_value = {'model_type': 'XGBClassifier', 'version': 'v2'}

        result = get_model_info()

        mock_get.assert_called_once_with("/predict/model-info")
        assert result['model_type'] == 'XGBClassifier'


# ============================================================
# TESTS: Integration Workflow
# ============================================================

class TestIntegrationWorkflow:
    """Integration tests for API client workflow."""

    @patch('interface.services.api_client._post')
    @patch('interface.services.api_client._get')
    def test_full_prediction_workflow(self, mock_get, mock_post):
        """Test complete workflow: get Pokemon -> predict."""
        mock_get.side_effect = [
            {'id': 25, 'name': 'Pikachu', 'moves': [{'name': 'Tonnerre'}]},
            {'id': 6, 'name': 'Dracaufeu'},
        ]
        mock_post.return_value = {
            'recommended_move': 'Tonnerre',
            'win_probability': 0.85,
            'all_moves': []
        }

        pokemon_a = get_pokemon_by_id(25)
        pokemon_b = get_pokemon_by_id(6)
        prediction = predict_best_move(25, 6, ['Tonnerre'])

        assert pokemon_a['id'] == 25
        assert pokemon_b['id'] == 6
        assert prediction['recommended_move'] == 'Tonnerre'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
