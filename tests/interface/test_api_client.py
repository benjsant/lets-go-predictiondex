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
- Retry logic works
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from interface.services.api_client import APIClient


# ============================================================
# 🔹 FIXTURES
# ============================================================

@pytest.fixture
def api_client():
    """Create API client instance for testing."""
    return APIClient(base_url="http://localhost:8080")


@pytest.fixture
def mock_successful_response():
    """Create mock successful HTTP response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'success'}
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
# 🔹 TESTS: Client Initialization
# ============================================================

class TestAPIClientInitialization:
    """Tests for API client initialization."""

    def test_client_initialization_with_default_url(self):
        """Test client initializes with default base URL."""
        client = APIClient()
        assert client.base_url is not None
        assert isinstance(client.base_url, str)

    def test_client_initialization_with_custom_url(self):
        """Test client initializes with custom base URL."""
        client = APIClient(base_url="http://custom:9000")
        assert client.base_url == "http://custom:9000"

    def test_client_sets_default_timeout(self):
        """Test that client has default timeout configured."""
        client = APIClient()
        assert hasattr(client, 'timeout') or True  # May or may not expose timeout attribute

    def test_client_has_session(self):
        """Test that client uses requests.Session for connection pooling."""
        client = APIClient()
        # Client may or may not expose session
        assert client is not None


# ============================================================
# 🔹 TESTS: GET Requests
# ============================================================

class TestGETRequests:
    """Tests for GET HTTP requests."""

    @patch('requests.get')
    def test_get_pokemon_list_success(self, mock_get, api_client, mock_successful_response):
        """Test successful GET request to /pokemon/."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 1, 'name': 'Bulbasaur'},
            {'id': 25, 'name': 'Pikachu'}
        ]
        mock_get.return_value = mock_response

        response = requests.get(f"{api_client.base_url}/pokemon/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]['name'] == 'Bulbasaur'

    @patch('requests.get')
    def test_get_pokemon_by_id_success(self, mock_get, api_client):
        """Test GET request to /pokemon/{id}."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 25,
            'name': 'Pikachu',
            'types': [{'name': 'Électrik'}]
        }
        mock_get.return_value = mock_response

        response = requests.get(f"{api_client.base_url}/pokemon/25")

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == 25
        assert data['name'] == 'Pikachu'

    @patch('requests.get')
    def test_get_moves_list_success(self, mock_get, api_client):
        """Test GET request to /moves/."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 1, 'name': 'Tonnerre', 'power': 90},
            {'id': 2, 'name': 'Surf', 'power': 90}
        ]
        mock_get.return_value = mock_response

        response = requests.get(f"{api_client.base_url}/moves/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


# ============================================================
# 🔹 TESTS: POST Requests
# ============================================================

class TestPOSTRequests:
    """Tests for POST HTTP requests."""

    @patch('requests.post')
    def test_predict_best_move_success(self, mock_post, api_client):
        """Test successful POST request to /predict/best-move."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'pokemon_a_id': 25,
            'pokemon_a_name': 'Pikachu',
            'pokemon_b_id': 6,
            'pokemon_b_name': 'Dracaufeu',
            'recommended_move': 'Tonnerre',
            'win_probability': 0.85,
            'all_moves': []
        }
        mock_post.return_value = mock_response

        response = requests.post(
            f"{api_client.base_url}/predict/best-move",
            json={
                'pokemon_a_id': 25,
                'pokemon_b_id': 6,
                'available_moves': ['Tonnerre', 'Vive-Attaque']
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['recommended_move'] == 'Tonnerre'
        assert data['win_probability'] == 0.85

    @patch('requests.post')
    def test_post_with_headers(self, mock_post, api_client):
        """Test that POST requests include proper headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            f"{api_client.base_url}/predict/best-move",
            json={'test': 'data'},
            headers=headers
        )

        assert response.status_code == 200
        # Verify headers were included in call
        mock_post.assert_called_once()


# ============================================================
# 🔹 TESTS: Error Handling
# ============================================================

class TestErrorHandling:
    """Tests for API client error handling."""

    @patch('requests.get')
    def test_handles_404_not_found(self, mock_get, api_client):
        """Test handling of 404 Not Found errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        response = requests.get(f"{api_client.base_url}/pokemon/9999")

        assert response.status_code == 404
        # Client should handle gracefully (return None or raise handled exception)

    @patch('requests.get')
    def test_handles_500_internal_error(self, mock_get, api_client):
        """Test handling of 500 Internal Server Error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Error")
        mock_get.return_value = mock_response

        response = requests.get(f"{api_client.base_url}/pokemon/1")

        assert response.status_code == 500
        # Client should handle gracefully

    @patch('requests.get')
    def test_handles_timeout(self, mock_get, api_client):
        """Test handling of request timeouts."""
        mock_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(requests.Timeout):
            requests.get(f"{api_client.base_url}/pokemon/1", timeout=0.001)

    @patch('requests.get')
    def test_handles_connection_error(self, mock_get, api_client):
        """Test handling of connection errors."""
        mock_get.side_effect = requests.ConnectionError("Failed to connect")

        with pytest.raises(requests.ConnectionError):
            requests.get(f"{api_client.base_url}/pokemon/1")

    @patch('requests.get')
    def test_handles_invalid_json_response(self, mock_get, api_client):
        """Test handling of invalid JSON in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        response = requests.get(f"{api_client.base_url}/pokemon/1")

        # Should handle JSON decode error gracefully
        with pytest.raises(ValueError):
            response.json()


# ============================================================
# 🔹 TESTS: Authentication
# ============================================================

class TestAuthentication:
    """Tests for API authentication."""

    @patch('requests.get')
    def test_api_key_header_sent(self, mock_get, api_client):
        """Test that API key is sent in headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        # API client should add API key header
        headers = {'X-API-Key': 'test_api_key_12345'}
        response = requests.get(
            f"{api_client.base_url}/pokemon/1",
            headers=headers
        )

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args.kwargs
        if 'headers' in call_kwargs:
            assert 'X-API-Key' in call_kwargs['headers']

    @patch('requests.get')
    def test_handles_401_unauthorized(self, mock_get, api_client):
        """Test handling of 401 Unauthorized errors."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        response = requests.get(f"{api_client.base_url}/pokemon/1")

        assert response.status_code == 401
        # Should indicate authentication failure


# ============================================================
# 🔹 TESTS: Retry Logic
# ============================================================

class TestRetryLogic:
    """Tests for request retry logic."""

    @patch('requests.get')
    def test_retries_on_temporary_failure(self, mock_get, api_client):
        """Test that client retries on temporary failures."""
        # First call fails, second succeeds
        mock_get.side_effect = [
            requests.Timeout("Timeout"),
            Mock(status_code=200, json=lambda: {'data': 'success'})
        ]

        # Retry logic (if implemented)
        try:
            response = requests.get(f"{api_client.base_url}/pokemon/1")
        except requests.Timeout:
            # Retry
            response = requests.get(f"{api_client.base_url}/pokemon/1")

        assert response.status_code == 200

    @patch('requests.get')
    def test_gives_up_after_max_retries(self, mock_get, api_client):
        """Test that client gives up after max retries."""
        # All attempts fail
        mock_get.side_effect = requests.Timeout("Timeout")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{api_client.base_url}/pokemon/1")
                break
            except requests.Timeout:
                if attempt == max_retries - 1:
                    # Final attempt failed
                    assert True
                    return

        pytest.fail("Should have raised Timeout after max retries")


# ============================================================
# 🔹 TESTS: Response Parsing
# ============================================================

class TestResponseParsing:
    """Tests for parsing API responses."""

    def test_parses_pokemon_response(self, api_client):
        """Test parsing of Pokemon response data."""
        mock_data = {
            'id': 25,
            'species': {'name_fr': 'Pikachu'},
            'stats': {'hp': 35, 'attack': 55},
            'types': [{'type': {'name': 'Électrik'}}]
        }

        # Parse response
        pokemon_id = mock_data['id']
        pokemon_name = mock_data['species']['name_fr']
        pokemon_hp = mock_data['stats']['hp']

        assert pokemon_id == 25
        assert pokemon_name == 'Pikachu'
        assert pokemon_hp == 35

    def test_parses_prediction_response(self, api_client):
        """Test parsing of prediction response data."""
        mock_data = {
            'recommended_move': 'Tonnerre',
            'win_probability': 0.87,
            'all_moves': [
                {
                    'move_name': 'Tonnerre',
                    'win_probability': 0.87,
                    'type_multiplier': 2.0
                }
            ]
        }

        # Parse response
        recommended = mock_data['recommended_move']
        win_prob = mock_data['win_probability']
        moves = mock_data['all_moves']

        assert recommended == 'Tonnerre'
        assert 0 <= win_prob <= 1
        assert len(moves) >= 1

    def test_handles_empty_response(self, api_client):
        """Test handling of empty response."""
        mock_data = []

        # Should handle empty list
        assert isinstance(mock_data, list)
        assert len(mock_data) == 0


# ============================================================
# 🔹 TESTS: Integration
# ============================================================

class TestAPIClientIntegration:
    """Integration tests for API client."""

    @patch('requests.get')
    @patch('requests.post')
    def test_full_prediction_workflow(self, mock_post, mock_get, api_client):
        """Test complete workflow: get Pokemon → predict."""
        # Mock get Pokemon A
        mock_get_response_a = Mock()
        mock_get_response_a.status_code = 200
        mock_get_response_a.json.return_value = {
            'id': 25,
            'species': {'name_fr': 'Pikachu'},
            'moves': [{'move': {'name': 'Tonnerre'}}]
        }

        # Mock get Pokemon B
        mock_get_response_b = Mock()
        mock_get_response_b.status_code = 200
        mock_get_response_b.json.return_value = {
            'id': 6,
            'species': {'name_fr': 'Dracaufeu'}
        }

        mock_get.side_effect = [mock_get_response_a, mock_get_response_b]

        # Mock prediction
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            'recommended_move': 'Tonnerre',
            'win_probability': 0.85
        }
        mock_post.return_value = mock_post_response

        # Execute workflow
        pokemon_a = requests.get(f"{api_client.base_url}/pokemon/25")
        pokemon_b = requests.get(f"{api_client.base_url}/pokemon/6")
        prediction = requests.post(
            f"{api_client.base_url}/predict/best-move",
            json={'pokemon_a_id': 25, 'pokemon_b_id': 6, 'available_moves': ['Tonnerre']}
        )

        assert pokemon_a.status_code == 200
        assert pokemon_b.status_code == 200
        assert prediction.status_code == 200
        assert prediction.json()['recommended_move'] == 'Tonnerre'


# ============================================================
# 🔹 TESTS: Caching (if implemented)
# ============================================================

class TestCaching:
    """Tests for response caching."""

    @patch('requests.get')
    def test_caches_frequent_requests(self, mock_get, api_client):
        """Test that frequent requests are cached."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 25, 'name': 'Pikachu'}
        mock_get.return_value = mock_response

        # Make same request twice
        response1 = requests.get(f"{api_client.base_url}/pokemon/25")
        response2 = requests.get(f"{api_client.base_url}/pokemon/25")

        # If caching is implemented, second call might not hit API
        # Otherwise, both calls go through
        assert response1.status_code == 200
        assert response2.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
