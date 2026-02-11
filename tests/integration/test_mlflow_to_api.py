"""
Integration Tests - MLflow Registry to API
==========================================

Tests end-to-end workflow:
1. Train model → Register in MLflow
2. API loads model from registry
3. Make predictions with loaded model
4. Test fallback to local files
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import joblib

# Import project modules
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from machine_learning.mlflow_integration import MLflowTracker, load_model_from_registry
from api_pokemon.services.model_loader import PredictionModel


@pytest.fixture
def temp_models_dir():
    """Create temporary models directory."""
    temp_dir = tempfile.mkdtemp()
    models_dir = Path(temp_dir) / "models"
    models_dir.mkdir(exist_ok=True)
    yield models_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_trained_model():
    """Create and train a sample model."""
    X = np.random.rand(100, 10)
    y = np.random.randint(0, 2, 100)
 
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
 
    return model, X, y


@pytest.fixture
def sample_scalers():
    """Create sample scalers."""
    scaler = StandardScaler()
    scaler.fit(np.random.rand(100, 10))
 
    return {
        'stat_scaler': scaler,
        'feature_scaler': scaler
    }


@pytest.fixture
def sample_feature_columns():
    """Create sample feature columns."""
    return [f'feature_{i}' for i in range(10)]


class TestMLflowToAPIIntegration:
    """Test integration between MLflow Registry and API."""
 
    @patch('api_pokemon.services.model_loader.load_model_from_registry')
    @patch.dict('os.environ', {'USE_MLFLOW_REGISTRY': 'true'})
    def test_api_loads_from_registry(self, mock_load_registry, sample_trained_model, sample_scalers, sample_feature_columns):
        """Test API successfully loads model from MLflow Registry."""
        model, X, y = sample_trained_model
 
        # Mock registry loading
        mock_load_registry.return_value = {
            'model': model,
            'scalers': sample_scalers,
            'metadata': {'feature_columns': sample_feature_columns},
            'version': '5',
            'stage': 'Production',
            'run_id': 'test_run_123'
        }
 
        # Create fresh PredictionModel instance
        pred_model = PredictionModel()
        pred_model._model = None # Reset singleton
        pred_model._scalers = None
        pred_model._metadata = None
 
        # Load model
        pred_model.load()
 
        # Verify loading
        assert pred_model.model is not None
        assert pred_model.scalers is not None
        assert pred_model.metadata is not None
 
        # Verify registry was called
        mock_load_registry.assert_called_once()
        # Check that it was called with correct parameters (either positional or keyword)
        call_kwargs = mock_load_registry.call_args.kwargs if mock_load_registry.call_args.kwargs else {}
        assert call_kwargs.get('model_name') == 'battle_winner_predictor' or \
               'battle_winner_predictor' in str(mock_load_registry.call_args)
 
    @patch('api_pokemon.services.model_loader.load_model_from_registry')
    @patch('api_pokemon.services.model_loader.joblib')
    @patch('builtins.open', create=True)
    @patch.dict('os.environ', {'USE_MLFLOW_REGISTRY': 'true'})
    def test_api_fallback_to_local_files(
        self, mock_open, mock_joblib, mock_load_registry, 
        sample_trained_model, sample_scalers, sample_feature_columns, temp_models_dir
    ):
        """Test API falls back to local files when registry fails."""
        model, X, y = sample_trained_model
 
        # Mock registry failure
        mock_load_registry.return_value = None
 
        # Mock local file loading
        mock_joblib.load.return_value = model
 
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
 
        # Mock pickle loads
        with patch('pickle.load') as mock_pickle_load:
            mock_pickle_load.side_effect = [sample_scalers, {'feature_columns': sample_feature_columns}]
 
            # Create fresh instance
            pred_model = PredictionModel()
            pred_model._model = None
            pred_model._scalers = None
            pred_model._metadata = None
 
            # Mock the file existence check
            with patch('pathlib.Path.exists', return_value=True):
                # Load model (should fallback to local)
                pred_model.load()
 
            # Verify registry was tried first
            mock_load_registry.assert_called_once()
 
            # Verify local loading was attempted
            assert mock_joblib.load.called or mock_open.called
 
    @patch.dict('os.environ', {'USE_MLFLOW_REGISTRY': 'false'})
    @patch('api_pokemon.services.model_loader.joblib')
    @patch('builtins.open', create=True)
    def test_api_loads_local_when_registry_disabled(
        self, mock_open, mock_joblib, sample_trained_model, sample_scalers, sample_feature_columns
    ):
        """Test API loads from local files when registry is disabled."""
        model, X, y = sample_trained_model
 
        # Mock local file loading
        mock_joblib.load.return_value = model
 
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
 
        with patch('pickle.load') as mock_pickle_load:
            mock_pickle_load.side_effect = [sample_scalers, {'feature_columns': sample_feature_columns}]
 
            # Create fresh instance
            pred_model = PredictionModel()
            pred_model._model = None
            pred_model._scalers = None
            pred_model._metadata = None
 
            with patch('pathlib.Path.exists', return_value=True):
                pred_model.load()
 
            # Verify model loaded
            assert pred_model.model is not None


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
 
    @patch('machine_learning.mlflow_integration.MlflowClient')
    @patch('machine_learning.mlflow_integration.mlflow')
    @patch('api_pokemon.services.model_loader.load_model_from_registry')
    def test_train_register_load_predict(
        self, mock_api_load_registry, mock_mlflow, mock_client,
        sample_trained_model, sample_scalers, sample_feature_columns
    ):
        """Test complete workflow: train → register → API load → predict."""
        model, X_train, y_train = sample_trained_model
 
        # --- STEP 1: Train and register model ---
        mock_run = Mock()
        mock_run.info.run_id = "e2e_run_123"
        mock_mlflow.active_run.return_value = mock_run
 
        mock_registered_model = Mock()
        mock_registered_model.version = "7"
        mock_mlflow.register_model.return_value = mock_registered_model
 
        mock_version = Mock()
        mock_version.version = "7"
        mock_version.current_stage = "Production"
        mock_version.run_id = "e2e_run_123"
 
        mock_client_instance = Mock()
        mock_client_instance.get_latest_versions.return_value = [mock_version]
 
        mock_client.return_value = mock_client_instance
 
        # Train and register
        tracker = MLflowTracker(experiment_name="e2e_test")
        with tracker.start_run(run_name="e2e_train"):
            tracker.log_params({'n_estimators': 10})
            tracker.log_metrics({
                'train_accuracy': 0.92,
                'test_accuracy': 0.87,
                'test_f1': 0.86
            })
            tracker.log_model(
                model=model,
                artifact_path="model",
                model_type="sklearn",
                scalers=sample_scalers,
                metadata={'feature_columns': sample_feature_columns}
            )
 
            version = tracker.register_model(
                model_name="battle_winner_predictor",
                description="E2E test model"
            )
 
            assert version == "7"
 
            # Promote to Production
            promoted = tracker.promote_to_production("battle_winner_predictor", version)
            assert promoted is True
 
        # --- STEP 2: API loads from registry ---
        mock_api_load_registry.return_value = {
            'model': model,
            'scalers': sample_scalers,
            'metadata': {'feature_columns': sample_feature_columns},
            'version': '7',
            'stage': 'Production',
            'run_id': 'e2e_run_123'
        }
 
        pred_model = PredictionModel()
        pred_model._model = None
        pred_model._scalers = None
        pred_model._metadata = None
 
        with patch.dict('os.environ', {'USE_MLFLOW_REGISTRY': 'true'}):
            pred_model.load()
 
        assert pred_model.model is not None
        assert pred_model.scalers is not None
 
        # --- STEP 3: Make predictions ---
        X_test = X_train[:5] # Use subset for prediction
        predictions = pred_model.model.predict(X_test)
 
        assert predictions is not None
        assert len(predictions) == 5
        assert all(p in [0, 1] for p in predictions) # Binary classification
 
    @patch('machine_learning.mlflow_integration.MlflowClient')
    @patch('machine_learning.mlflow_integration.mlflow')
    def test_multiple_versions_comparison(
        self, mock_mlflow, mock_client, sample_trained_model, sample_scalers
    ):
        """Test registering and comparing multiple model versions."""
        model, X, y = sample_trained_model
 
        # Setup mocks for multiple versions
        mock_run = Mock()
        mock_run.info.run_id = "multi_v_run"
        mock_mlflow.active_run.return_value = mock_run
 
        mock_client_instance = Mock()
 
        # Create 3 versions
        versions = []
        for i in range(1, 4):
            mock_v = Mock()
            mock_v.version = str(i)
            mock_v.current_stage = "Production" if i == 3 else "Archived"
            mock_v.run_id = f"run_{i}"
            mock_v.creation_timestamp = 1700000000000 + (i * 10000000)
            versions.append(mock_v)
 
        mock_client_instance.search_model_versions.return_value = list(reversed(versions))
 
        # Mock metrics for each version
        def get_run_side_effect(run_id):
            metrics_map = {
                'run_1': {'test_accuracy': 0.82, 'test_f1': 0.81},
                'run_2': {'test_accuracy': 0.85, 'test_f1': 0.84},
                'run_3': {'test_accuracy': 0.88, 'test_f1': 0.87}
            }
            return Mock(data=Mock(metrics=metrics_map.get(run_id, {})))
 
        mock_client_instance.get_run.side_effect = get_run_side_effect
        mock_client.return_value = mock_client_instance
 
        # Compare versions
        tracker = MLflowTracker(experiment_name="multi_version_test")
        df = tracker.compare_models(model_name="battle_winner_predictor")
 
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
 
        # Verify metrics progression
        assert df.iloc[0]['version'] == "3" # Latest version first
        assert df.iloc[0]['test_accuracy'] == 0.88
        assert df.iloc[2]['version'] == "1"
        assert df.iloc[2]['test_accuracy'] == 0.82


class TestRollbackScenario:
    """Test model rollback scenario."""
 
    @patch('machine_learning.mlflow_integration.MlflowClient')
    @patch('api_pokemon.services.model_loader.load_model_from_registry')
    def test_rollback_to_previous_version(
        self, mock_api_load_registry, mock_client, sample_trained_model, sample_scalers
    ):
        """Test rolling back from bad version to previous good version."""
        model_good, X, y = sample_trained_model
 
        # Create a "bad" model (for demonstration)
        model_bad = RandomForestClassifier(n_estimators=5, random_state=999)
        model_bad.fit(X[:50], y[:50]) # Trained on less data
 
        # Setup mocks
        mock_client_instance = Mock()
 
        # Version 2 (good, previously in Production)
        mock_v2 = Mock()
        mock_v2.version = "2"
        mock_v2.current_stage = "Archived"
 
        # Version 3 (bad, currently in Production)
        mock_v3 = Mock()
        mock_v3.version = "3"
        mock_v3.current_stage = "Production"
 
        mock_client_instance.get_latest_versions.side_effect = [
            [mock_v3], # First call: get current Production
            [mock_v2] # After rollback: get new Production
        ]
 
        mock_client.return_value = mock_client_instance
 
        # --- STEP 1: API loads bad model (v3) ---
        mock_api_load_registry.return_value = {
            'model': model_bad,
            'scalers': sample_scalers,
            'metadata': {},
            'version': '3',
            'stage': 'Production'
        }
 
        pred_model = PredictionModel()
        pred_model._model = None
 
        with patch.dict('os.environ', {'USE_MLFLOW_REGISTRY': 'true'}):
            pred_model.load()
 
        # Make prediction with bad model
        pred_bad = pred_model.model.predict(X[:5])
 
        # --- STEP 2: Rollback to v2 ---
        tracker = MLflowTracker(experiment_name="rollback_test")
        result = tracker.promote_to_production("battle_winner_predictor", version="2")
        assert result is True
 
        # --- STEP 3: API reloads good model (v2) ---
        mock_api_load_registry.return_value = {
            'model': model_good,
            'scalers': sample_scalers,
            'metadata': {},
            'version': '2',
            'stage': 'Production'
        }
 
        # Force reload
        pred_model._model = None
        pred_model.load()
 
        # Make prediction with good model
        pred_good = pred_model.model.predict(X[:5])
 
        # Verify both predictions work (models are different but functional)
        assert len(pred_bad) == 5
        assert len(pred_good) == 5


class TestConcurrentAccess:
    """Test concurrent access scenarios."""
 
    @patch('api_pokemon.services.model_loader.load_model_from_registry')
    def test_multiple_api_instances_load_same_model(
        self, mock_load_registry, sample_trained_model, sample_scalers
    ):
        """Test multiple API instances loading same model from registry."""
        model, X, y = sample_trained_model
 
        # Mock registry loading
        mock_load_registry.return_value = {
            'model': model,
            'scalers': sample_scalers,
            'metadata': {},
            'version': '8',
            'stage': 'Production'
        }
 
        # Simulate 3 API instances
        instances = []
        for i in range(3):
            pred_model = PredictionModel()
            pred_model._model = None
            pred_model._scalers = None
 
            with patch.dict('os.environ', {'USE_MLFLOW_REGISTRY': 'true'}):
                pred_model.load()
 
            instances.append(pred_model)
 
        # Verify all instances loaded successfully
        for instance in instances:
            assert instance.model is not None
            predictions = instance.model.predict(X[:5])
            assert len(predictions) == 5
 
        # Verify registry was called for each instance
        assert mock_load_registry.call_count == 3


class TestErrorHandling:
    """Test error handling in integration scenarios."""
 
    @patch('api_pokemon.services.model_loader.load_model_from_registry')
    @patch('api_pokemon.services.model_loader.joblib')
    def test_registry_timeout_fallback(self, mock_joblib, mock_load_registry, sample_trained_model, sample_scalers):
        """Test fallback when registry times out."""
        model, X, y = sample_trained_model
 
        # Mock registry timeout
        mock_load_registry.side_effect = TimeoutError("MLflow server timeout")
 
        # Mock local loading succeeds
        mock_joblib.load.return_value = model
 
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
 
            with patch('pickle.load') as mock_pickle_load:
                mock_pickle_load.side_effect = [sample_scalers, {}]
 
                pred_model = PredictionModel()
                pred_model._model = None
                pred_model._scalers = None
 
                with patch('pathlib.Path.exists', return_value=True):
                    # Should not raise exception, should fallback
                    try:
                        pred_model.load()
                    except TimeoutError:
                        pytest.fail("Should have fallen back to local files")
 
    @patch('api_pokemon.services.model_loader.load_model_from_registry')
    @patch('pathlib.Path.exists')
    def test_no_model_available_error(self, mock_exists, mock_load_registry):
        """Test error when no model available (registry and local)."""
        # Mock registry failure
        mock_load_registry.return_value = None
 
        # Mock local files don't exist
        mock_exists.return_value = False
 
        pred_model = PredictionModel()
        pred_model._model = None
 
        with patch.dict('os.environ', {'USE_MLFLOW_REGISTRY': 'true'}):
            with pytest.raises(FileNotFoundError):
                pred_model.load()


@pytest.mark.integration
class TestRealMLflowServer:
    """Integration tests with real MLflow server (requires running server)."""
 
    @pytest.mark.skipif(
        True, # Skip by default, enable manually for real server tests
        reason="Requires running MLflow server"
    )
    def test_real_mlflow_server_integration(self, sample_trained_model, sample_scalers):
        """Test with real MLflow server (manual test)."""
        import mlflow
        model, X, y = sample_trained_model
 
        # Connect to MLflow server (Docker service)
        mlflow.set_tracking_uri("http://mlflow:5001")
 
        tracker = MLflowTracker(experiment_name="real_server_integration_test")
 
        with tracker.start_run(run_name="real_integration"):
            tracker.log_params({'test': 'real_server'})
            tracker.log_metrics({'test_accuracy': 0.85})
            tracker.log_model(model, scalers=sample_scalers, metadata={'test': True})
 
            version = tracker.register_model(model_name="test_integration_model")
            assert version is not None
 
            # Promote
            promoted = tracker.promote_to_production("test_integration_model", version)
            assert promoted is True
 
        # Load from registry
        bundle = load_model_from_registry(
            model_name="test_integration_model",
            stage="Production"
        )
 
        assert bundle is not None
        assert bundle['model'] is not None
        assert bundle['scalers'] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-k", "not TestRealMLflowServer"])
