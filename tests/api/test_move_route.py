"""
Tests for move routes
======================

Integration tests for Move API endpoints.

Coverage target: 80%+
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from api_pokemon.routes.moves_route import router


# Create a minimal FastAPI app for testing
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    """Create a test client for the move routes."""
    with TestClient(app) as c:
        yield c


# ============================================================
# TESTS: GET /moves/
# ============================================================

class TestListMoves:
    """Tests for listing all moves."""

    @patch('api_pokemon.routes.moves_route.list_moves')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_list_moves_success(self, mock_get_db, mock_list_moves, client):
        """Test successful retrieval of moves list."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock Move objects
        mock_type = Mock()
        mock_type.id = 3
        mock_type.name = "Feu"

        mock_category = Mock()
        mock_category.name = "spécial"

        mock_move = Mock()
        mock_move.id = 1
        mock_move.name = "Lance-Flammes"
        mock_move.category = mock_category
        mock_move.power = 90
        mock_move.accuracy = 100
        mock_move.description = "Une gerbe de flammes intense."
        mock_move.type = mock_type

        mock_list_moves.return_value = [mock_move]

        # Make request
        response = client.get("/moves/")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]['id'] == 1
        assert data[0]['name'] == "Lance-Flammes"
        assert data[0]['power'] == 90
        assert data[0]['description'] == "Une gerbe de flammes intense."

    @patch('api_pokemon.routes.moves_route.list_moves')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_list_moves_empty(self, mock_get_db, mock_list_moves, client):
        """Test listing moves when database is empty."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock empty list
        mock_list_moves.return_value = []

        # Make request
        response = client.get("/moves/")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data == []


# ============================================================
# TESTS: GET /moves/search
# ============================================================

class TestSearchMoves:
    """Tests for searching moves by name."""

    @patch('api_pokemon.routes.moves_route.search_moves_by_name')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_search_moves_success(self, mock_get_db, mock_search, client):
        """Test successful move search."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock Move objects
        mock_type = Mock()
        mock_type.id = 5
        mock_type.name = "Eau"

        mock_category = Mock()
        mock_category.name = "spécial"

        mock_move = Mock()
        mock_move.id = 2
        mock_move.name = "Surf"
        mock_move.category = mock_category
        mock_move.power = 90
        mock_move.accuracy = 100
        mock_move.description = "Une énorme vague."
        mock_move.type = mock_type

        mock_search.return_value = [mock_move]

        # Make request
        response = client.get("/moves/search?name=Surf")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]['name'] == "Surf"

        # Verify service was called
        mock_search.assert_called_once()

    @patch('api_pokemon.routes.moves_route.search_moves_by_name')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_search_moves_no_results(self, mock_get_db, mock_search, client):
        """Test search with no matching moves."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock empty results
        mock_search.return_value = []

        # Make request
        response = client.get("/moves/search?name=NonExistent")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @patch('api_pokemon.routes.moves_route.get_db')
    def test_search_moves_missing_name(self, mock_get_db, client):
        """Test search without name parameter."""
        # Make request without name
        response = client.get("/moves/search")

        # Assertions
        assert response.status_code == 422 # Validation error


# ============================================================
# TESTS: GET /moves/by-type/{type_name}
# ============================================================

class TestListMovesByType:
    """Tests for listing moves by type."""

    @patch('api_pokemon.routes.moves_route.list_moves_by_type')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_list_moves_by_type_success(self, mock_get_db, mock_list, client):
        """Test successful retrieval of moves by type."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock Move objects
        mock_type = Mock()
        mock_type.id = 3
        mock_type.name = "Feu"

        mock_category = Mock()
        mock_category.name = "spécial"

        mock_move = Mock()
        mock_move.id = 1
        mock_move.name = "Lance-Flammes"
        mock_move.category = mock_category
        mock_move.power = 90
        mock_move.accuracy = 100
        mock_move.description = "Une gerbe de flammes intense."
        mock_move.type = mock_type

        mock_list.return_value = [
            {
                'move': mock_move,
                'learn_method': None,
                'learn_level': None
            }
        ]

        # Make request
        response = client.get("/moves/by-type/feu")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]['name'] == "Lance-Flammes"
        assert data[0]['learn_method'] is None
        assert data[0]['learn_level'] is None

    @patch('api_pokemon.routes.moves_route.list_moves_by_type')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_list_moves_by_type_with_pokemon_filter(self, mock_get_db, mock_list, client):
        """Test listing moves by type with Pokemon filter."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock Move with learn info
        mock_type = Mock()
        mock_type.id = 6
        mock_type.name = "Électrik"

        mock_category = Mock()
        mock_category.name = "spécial"

        mock_move = Mock()
        mock_move.id = 5
        mock_move.name = "Tonnerre"
        mock_move.category = mock_category
        mock_move.power = 110
        mock_move.accuracy = 70
        mock_move.description = "Une puissante décharge."
        mock_move.type = mock_type

        mock_list.return_value = [
            {
                'move': mock_move,
                'learn_method': 'level_up',
                'learn_level': 30
            }
        ]

        # Make request with pokemon_id
        response = client.get("/moves/by-type/electrik?pokemon_id=1")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]['learn_method'] == 'level_up'
        assert data[0]['learn_level'] == 30

    @patch('api_pokemon.routes.moves_route.list_moves_by_type')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_list_moves_by_type_empty(self, mock_get_db, mock_list, client):
        """Test listing moves by type with no results."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock empty list
        mock_list.return_value = []

        # Make request
        response = client.get("/moves/by-type/nonexistent")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data == []


# ============================================================
# TESTS: GET /moves/id/{move_id}
# ============================================================

class TestGetMoveById:
    """Tests for retrieving move by ID."""

    @patch('api_pokemon.routes.moves_route.get_move_by_id')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_get_move_by_id_success(self, mock_get_db, mock_get_move, client):
        """Test successful retrieval of move by ID."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock Move object
        mock_type = Mock()
        mock_type.id = 5
        mock_type.name = "Eau"

        mock_category = Mock()
        mock_category.name = "spécial"

        mock_move = Mock()
        mock_move.id = 2
        mock_move.name = "Surf"
        mock_move.category = mock_category
        mock_move.power = 90
        mock_move.accuracy = 100
        mock_move.description = "Une énorme vague."
        mock_move.damage_type = "offensif"
        mock_move.type = mock_type

        mock_get_move.return_value = mock_move

        # Make request
        response = client.get("/moves/id/2")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert data['id'] == 2
        assert data['name'] == "Surf"
        assert data['description'] == "Une énorme vague."
        assert data['damage_type'] == "offensif"

    @patch('api_pokemon.routes.moves_route.get_move_by_id')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_get_move_by_id_not_found(self, mock_get_db, mock_get_move, client):
        """Test retrieval of non-existent move."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock service returns None
        mock_get_move.return_value = None

        # Make request
        response = client.get("/moves/id/999")

        # Assertions
        assert response.status_code == 404
        assert "Move not found" in response.json()['detail']

    @patch('api_pokemon.routes.moves_route.get_move_by_id')
    @patch('api_pokemon.routes.moves_route.get_db')
    def test_get_move_by_id_includes_all_fields(self, mock_get_db, mock_get_move, client):
        """Test that move detail includes all expected fields."""
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock complete Move object
        mock_type = Mock()
        mock_type.id = 1
        mock_type.name = "Normal"

        mock_category = Mock()
        mock_category.name = "physique"

        mock_move = Mock()
        mock_move.id = 4
        mock_move.name = "Vive-Attaque"
        mock_move.category = mock_category
        mock_move.power = 40
        mock_move.accuracy = 100
        mock_move.description = "Attaque rapide."
        mock_move.damage_type = "offensif"
        mock_move.type = mock_type

        mock_get_move.return_value = mock_move

        # Make request
        response = client.get("/moves/id/4")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        # Verify all expected fields are present
        assert 'id' in data
        assert 'name' in data
        assert 'category' in data
        assert 'type' in data
        assert 'power' in data
        assert 'accuracy' in data
        assert 'description' in data
        assert 'damage_type' in data
