"""
Tests for prediction routes
============================

Integration tests for ML prediction API endpoints.

Coverage target: 80%+
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from api_pokemon.routes.prediction_route import router
from api_pokemon.services import prediction_service


# Create a minimal FastAPI app for testing
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    """Create a test client for the prediction routes."""
    return TestClient(app)


# ============================================================
# 🔹 TESTS: POST /predict/best-move
# ============================================================

class TestPredictBestMove:
    """Tests for the best move prediction endpoint."""

    @patch('api_pokemon.routes.prediction_route.prediction_service.predict_best_move')
    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_success(self, mock_get_db, mock_predict, client):
        """Test successful prediction request."""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock prediction response
        mock_predict.return_value = {
            'pokemon_a_id': 1,
            'pokemon_a_name': 'Pikachu',
            'pokemon_b_id': 2,
            'pokemon_b_name': 'Dracaufeu',
            'recommended_move': 'Tonnerre',
            'win_probability': 0.85,
            'all_moves': [
                {
                    'move_name': 'Tonnerre',
                    'move_type': 'Électrik',
                    'move_power': 110,
                    'effective_power': 110.0,
                    'type_multiplier': 1.0,
                    'stab': 1.5,
                    'priority': 0,
                    'score': 165.0,
                    'win_probability': 0.85,
                    'predicted_winner': 'A'
                }
            ]
        }

        # Make request
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": 1,
                "pokemon_b_id": 2,
                "available_moves": ["Tonnerre", "Vive-Attaque"]
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert data['pokemon_a_id'] == 1
        assert data['pokemon_a_name'] == 'Pikachu'
        assert data['pokemon_b_id'] == 2
        assert data['pokemon_b_name'] == 'Dracaufeu'
        assert data['recommended_move'] == 'Tonnerre'
        assert data['win_probability'] == 0.85
        assert len(data['all_moves']) == 1

        # Verify service was called
        mock_predict.assert_called_once()

    @patch('api_pokemon.routes.prediction_route.prediction_service.predict_best_move')
    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_pokemon_not_found(self, mock_get_db, mock_predict, client):
        """Test prediction with non-existent Pokemon."""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock service to raise ValueError
        mock_predict.side_effect = ValueError("Pokemon A with ID 999 not found")

        # Make request
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": 999,
                "pokemon_b_id": 2,
                "available_moves": ["Tonnerre"]
            }
        )

        # Assertions
        assert response.status_code == 404
        assert "Pokemon A with ID 999 not found" in response.json()['detail']

    @patch('api_pokemon.routes.prediction_route.prediction_service.predict_best_move')
    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_invalid_moves(self, mock_get_db, mock_predict, client):
        """Test prediction with invalid move names."""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock service to raise ValueError
        mock_predict.side_effect = ValueError("No valid moves found for prediction")

        # Make request
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": 1,
                "pokemon_b_id": 2,
                "available_moves": ["NonExistentMove"]
            }
        )

        # Assertions
        assert response.status_code == 404
        assert "No valid moves found" in response.json()['detail']

    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_missing_pokemon_a_id(self, mock_get_db, client):
        """Test prediction without pokemon_a_id."""
        # Make request with missing field
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_b_id": 2,
                "available_moves": ["Tonnerre"]
            }
        )

        # Assertions
        assert response.status_code == 422  # Validation error

    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_missing_pokemon_b_id(self, mock_get_db, client):
        """Test prediction without pokemon_b_id."""
        # Make request with missing field
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": 1,
                "available_moves": ["Tonnerre"]
            }
        )

        # Assertions
        assert response.status_code == 422  # Validation error

    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_missing_moves(self, mock_get_db, client):
        """Test prediction without available_moves."""
        # Make request with missing field
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": 1,
                "pokemon_b_id": 2
            }
        )

        # Assertions
        assert response.status_code == 422  # Validation error

    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_empty_moves_list(self, mock_get_db, client):
        """Test prediction with empty moves list."""
        # Make request with empty moves
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": 1,
                "pokemon_b_id": 2,
                "available_moves": []
            }
        )

        # Assertions
        assert response.status_code == 422  # Validation error (min_items=1)

    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_invalid_pokemon_id_zero(self, mock_get_db, client):
        """Test prediction with pokemon_id = 0."""
        # Make request with invalid ID
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": 0,
                "pokemon_b_id": 2,
                "available_moves": ["Tonnerre"]
            }
        )

        # Assertions
        assert response.status_code == 422  # Validation error (gt=0)

    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_invalid_pokemon_id_negative(self, mock_get_db, client):
        """Test prediction with negative pokemon_id."""
        # Make request with negative ID
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": -1,
                "pokemon_b_id": 2,
                "available_moves": ["Tonnerre"]
            }
        )

        # Assertions
        assert response.status_code == 422  # Validation error

    @patch('api_pokemon.routes.prediction_route.prediction_service.predict_best_move')
    @patch('api_pokemon.routes.prediction_route.get_db')
    def test_predict_best_move_server_error(self, mock_get_db, mock_predict, client):
        """Test prediction with unexpected server error."""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock service to raise generic exception
        mock_predict.side_effect = Exception("Model inference error")

        # Make request
        response = client.post(
            "/predict/best-move",
            json={
                "pokemon_a_id": 1,
                "pokemon_b_id": 2,
                "available_moves": ["Tonnerre"]
            }
        )

        # Assertions
        assert response.status_code == 500
        assert "Prediction error" in response.json()['detail']


# ============================================================
# 🔹 TESTS: GET /predict/model-info
# ============================================================

class TestModelInfo:
    """Tests for the model info endpoint."""

    @patch('api_pokemon.routes.prediction_route.prediction_service.prediction_model')
    def test_get_model_info_success(self, mock_model_instance, client):
        """Test successful retrieval of model info."""
        # Mock model metadata
        mock_model_instance.metadata = {
            'model_type': 'XGBClassifier',
            'version': 'v1',
            'n_features': 133,
            'metrics': {
                'test_accuracy': 0.9424,
                'test_precision': 0.9456,
                'test_recall': 0.9389,
                'test_f1': 0.9422,
                'test_roc_auc': 0.9821
            },
            'trained_at': '2024-01-20T10:30:00',
            'hyperparameters': {
                'n_estimators': 100,
                'max_depth': 8,
                'learning_rate': 0.1
            }
        }

        # Make request
        response = client.get("/predict/model-info")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert data['model_type'] == 'XGBClassifier'
        assert data['version'] == 'v1'
        assert data['n_features'] == 133
        assert 'metrics' in data
        assert data['metrics']['test_accuracy'] == 0.9424
        assert 'trained_at' in data
        assert 'hyperparameters' in data

    @patch('api_pokemon.routes.prediction_route.prediction_service.prediction_model')
    def test_get_model_info_includes_all_fields(self, mock_model_instance, client):
        """Test that model info includes all required fields."""
        # Mock model metadata
        mock_model_instance.metadata = {
            'model_type': 'XGBClassifier',
            'version': 'v1',
            'n_features': 133,
            'metrics': {},
            'trained_at': '2024-01-20T10:30:00',
            'hyperparameters': {}
        }

        # Make request
        response = client.get("/predict/model-info")

        # Assertions
        assert response.status_code == 200
        data = response.json()

        # Check all required fields are present
        assert 'model_type' in data
        assert 'version' in data
        assert 'n_features' in data
        assert 'metrics' in data
        assert 'trained_at' in data
        assert 'hyperparameters' in data
