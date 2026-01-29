"""
Tests for MLflow integration module
Validates C13 (MLOps) - Experiment tracking
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import mlflow
from machine_learning.mlflow_integration import MLflowTracker, get_mlflow_tracker


class TestMLflowTracker:
    """Test MLflowTracker class"""
    
    def test_tracker_initialization(self):
        """Test tracker initializes correctly"""
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=None):
                with patch('mlflow.create_experiment', return_value='1'):
                    tracker = MLflowTracker(experiment_name="test_exp")
                    assert tracker.experiment_name == "test_exp"
    
    def test_tracker_with_existing_experiment(self):
        """Test tracker with existing experiment"""
        mock_exp = Mock()
        mock_exp.experiment_id = '42'
        
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=mock_exp):
                with patch('mlflow.set_experiment'):
                    tracker = MLflowTracker(experiment_name="existing")
                    assert tracker.experiment_id == '42'
    
    def test_tracker_auto_detection_docker(self):
        """Test auto-detection of Docker environment"""
        with patch('socket.create_connection'):
            with patch('mlflow.set_tracking_uri') as mock_set_uri:
                with patch('mlflow.get_experiment_by_name', return_value=None):
                    with patch('mlflow.create_experiment', return_value='1'):
                        tracker = MLflowTracker(experiment_name="test")
                        # Should detect mlflow:5000 in Docker
                        mock_set_uri.assert_called_once()
    
    def test_tracker_graceful_fallback(self):
        """Test graceful fallback when MLflow unavailable"""
        with patch('mlflow.set_tracking_uri', side_effect=Exception("Connection failed")):
            tracker = MLflowTracker(experiment_name="test")
            assert tracker.experiment_name is None
    
    def test_log_params(self):
        """Test logging parameters"""
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=None):
                with patch('mlflow.create_experiment', return_value='1'):
                    with patch('mlflow.log_params') as mock_log:
                        tracker = MLflowTracker(experiment_name="test")
                        params = {'n_estimators': 100, 'max_depth': 8}
                        tracker.log_params(params)
                        mock_log.assert_called_once_with(params)
    
    def test_log_metrics(self):
        """Test logging metrics"""
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=None):
                with patch('mlflow.create_experiment', return_value='1'):
                    with patch('mlflow.log_metrics') as mock_log:
                        tracker = MLflowTracker(experiment_name="test")
                        metrics = {'accuracy': 0.95, 'f1': 0.92}
                        tracker.log_metrics(metrics)
                        mock_log.assert_called_once_with(metrics, step=None)
    
    def test_log_model_xgboost(self):
        """Test logging XGBoost model"""
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=None):
                with patch('mlflow.create_experiment', return_value='1'):
                    with patch('mlflow.xgboost.log_model') as mock_log:
                        tracker = MLflowTracker(experiment_name="test")
                        mock_model = Mock()
                        tracker.log_model(mock_model, "model", "xgboost")
                        mock_log.assert_called_once()
    
    def test_log_model_sklearn(self):
        """Test logging sklearn model"""
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=None):
                with patch('mlflow.create_experiment', return_value='1'):
                    with patch('mlflow.sklearn.log_model') as mock_log:
                        tracker = MLflowTracker(experiment_name="test")
                        mock_model = Mock()
                        tracker.log_model(mock_model, "model", "sklearn")
                        mock_log.assert_called_once()
    
    def test_log_dataset_info(self):
        """Test logging dataset information"""
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=None):
                with patch('mlflow.create_experiment', return_value='1'):
                    with patch('mlflow.log_params') as mock_log:
                        tracker = MLflowTracker(experiment_name="test")
                        dataset_info = {
                            'train_samples': 1000,
                            'test_samples': 250,
                            'num_features': 45
                        }
                        tracker.log_dataset_info(dataset_info)
                        mock_log.assert_called_once()
    
    def test_start_run(self):
        """Test starting a run"""
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=None):
                with patch('mlflow.create_experiment', return_value='1'):
                    with patch('mlflow.start_run') as mock_start:
                        tracker = MLflowTracker(experiment_name="test")
                        tracker.start_run(run_name="test_run")
                        mock_start.assert_called_once()
    
    def test_set_tags(self):
        """Test setting tags"""
        with patch('mlflow.set_tracking_uri'):
            with patch('mlflow.get_experiment_by_name', return_value=None):
                with patch('mlflow.create_experiment', return_value='1'):
                    with patch('mlflow.set_tags') as mock_tags:
                        tracker = MLflowTracker(experiment_name="test")
                        tags = {'version': 'v2', 'model_type': 'xgboost'}
                        tracker.set_tags(tags)
                        mock_tags.assert_called_once_with(tags)


def test_get_mlflow_tracker():
    """Test helper function to get tracker"""
    with patch('mlflow.set_tracking_uri'):
        with patch('mlflow.get_experiment_by_name', return_value=None):
            with patch('mlflow.create_experiment', return_value='1'):
                tracker = get_mlflow_tracker("test_experiment")
                assert isinstance(tracker, MLflowTracker)
                assert tracker.experiment_name == "test_experiment"
