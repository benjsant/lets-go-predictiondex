#!/usr/bin/env python3
"""
MLflow Integration for Machine Learning Pipeline
================================================

This module provides MLflow tracking integration for the ML pipeline,
automatically logging experiments, parameters, metrics, and models.

Features:
- Automatic experiment tracking
- Hyperparameter logging
- Metrics logging (accuracy, precision, recall, F1, AUC)
- Model artifact logging
- Dataset metadata logging
- Comparison between runs

Usage:
    from machine_learning.mlflow_integration import MLflowTracker
    
    tracker = MLflowTracker(experiment_name="battle_winner_v2")
    
    with tracker.start_run(run_name="xgboost_training"):
        tracker.log_params(hyperparams)
        tracker.log_metrics(metrics)
        tracker.log_model(model, "model")
"""

import os
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class MLflowTracker:
    """MLflow experiment tracking wrapper."""
    
    def __init__(
        self, 
        experiment_name: str = "pokemon_battle_winner",
        tracking_uri: Optional[str] = None
    ):
        """
        Initialize MLflow tracker.
        
        Args:
            experiment_name: Name of the MLflow experiment
            tracking_uri: MLflow tracking server URI (default: http://mlflow:5000)
        """
        # Check if MLflow tracking is explicitly disabled
        if os.getenv("DISABLE_MLFLOW_TRACKING", "false").lower() == "true":
            print("ℹ️  MLflow tracking disabled via DISABLE_MLFLOW_TRACKING environment variable")
            self.experiment_name = None
            self.experiment_id = None
            return
        
        # Set tracking URI (default to mlflow:5000 for Docker, localhost for local dev)
        if tracking_uri is None:
            # Check if running in Docker (MLFLOW_TRACKING_URI env var)
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
            if tracking_uri is None:
                # Fallback: check if we can reach mlflow service (Docker)
                import socket
                import time
                mlflow_available = False
                
                # Retry MLflow connection up to 30 seconds
                for attempt in range(10):
                    try:
                        socket.create_connection(("mlflow", 5000), timeout=3)
                        tracking_uri = "http://mlflow:5000"
                        mlflow_available = True
                        print(f"✅ MLflow detected at mlflow:5000 (attempt {attempt + 1})")
                        break
                    except (socket.error, socket.timeout):
                        if attempt < 9:
                            print(f"⏳ Waiting for MLflow... (attempt {attempt + 1}/10)")
                            time.sleep(3)
                        else:
                            # Fallback to localhost for local dev
                            tracking_uri = "http://localhost:5000"
                            print("⚠️ MLflow not detected, trying localhost:5000")
        
        mlflow.set_tracking_uri(tracking_uri)
        
        # Set or create experiment
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                print(f"✅ Created new experiment: {experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                print(f"✅ Using existing experiment: {experiment_name} (ID: {experiment_id})")
            
            mlflow.set_experiment(experiment_name)
            self.experiment_name = experiment_name
            self.experiment_id = experiment_id
            
        except Exception as e:
            print(f"⚠️ MLflow connection error: {e}")
            print(f"⚠️ Continuing without MLflow tracking...")
            self.experiment_name = None
            self.experiment_id = None
    
    def start_run(self, run_name: Optional[str] = None, nested: bool = False):
        """
        Start a new MLflow run.
        
        Args:
            run_name: Optional name for the run
            nested: Whether this is a nested run
        
        Returns:
            MLflow run context manager
        """
        if self.experiment_name is None:
            # Dummy context manager if MLflow unavailable
            class DummyContext:
                def __enter__(self): return self
                def __exit__(self, *args): pass
            return DummyContext()
        
        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return mlflow.start_run(run_name=run_name, nested=nested)
    
    def log_params(self, params: Dict[str, Any]):
        """
        Log hyperparameters.
        
        Args:
            params: Dictionary of parameters
        """
        if self.experiment_name is None:
            return
        
        try:
            # Flatten nested dicts and convert to string if needed
            flat_params = {}
            for key, value in params.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flat_params[f"{key}_{sub_key}"] = str(sub_value)
                else:
                    flat_params[key] = value
            
            mlflow.log_params(flat_params)
            print(f"✅ Logged {len(flat_params)} parameters")
        except Exception as e:
            print(f"⚠️ Error logging params: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log metrics.
        
        Args:
            metrics: Dictionary of metrics
            step: Optional step number for tracking over time
        """
        if self.experiment_name is None:
            return
        
        try:
            mlflow.log_metrics(metrics, step=step)
            print(f"✅ Logged {len(metrics)} metrics")
        except Exception as e:
            print(f"⚠️ Error logging metrics: {e}")
    
    def log_model(
        self, 
        model: Any, 
        artifact_path: str = "model",
        model_type: str = "sklearn"
    ):
        """
        Log model artifact.
        
        Args:
            model: Trained model object
            artifact_path: Path within MLflow artifacts
            model_type: Type of model ('sklearn', 'xgboost')
        """
        if self.experiment_name is None:
            return
        
        try:
            if model_type == "xgboost":
                mlflow.xgboost.log_model(model, artifact_path)
            else:
                mlflow.sklearn.log_model(model, artifact_path)
            
            print(f"✅ Logged {model_type} model to: {artifact_path}")
        except Exception as e:
            print(f"⚠️ Error logging model: {e}")
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """
        Log a file or directory as an artifact.
        
        Args:
            local_path: Local file or directory path
            artifact_path: Optional subdirectory in artifacts
        """
        if self.experiment_name is None:
            return
        
        try:
            mlflow.log_artifact(local_path, artifact_path)
            print(f"✅ Logged artifact: {local_path}")
        except Exception as e:
            print(f"⚠️ Error logging artifact: {e}")
    
    def log_dataset_info(self, dataset_info: Dict[str, Any]):
        """
        Log dataset metadata.
        
        Args:
            dataset_info: Dictionary with dataset information
        """
        if self.experiment_name is None:
            return
        
        try:
            # Log as tags for easy filtering
            mlflow.set_tags({
                f"dataset_{key}": str(value)
                for key, value in dataset_info.items()
            })
            print(f"✅ Logged dataset metadata")
        except Exception as e:
            print(f"⚠️ Error logging dataset info: {e}")
    
    def set_tags(self, tags: Dict[str, str]):
        """
        Set tags for the current run.
        
        Args:
            tags: Dictionary of tags
        """
        if self.experiment_name is None:
            return
        
        try:
            mlflow.set_tags(tags)
            print(f"✅ Set {len(tags)} tags")
        except Exception as e:
            print(f"⚠️ Error setting tags: {e}")


def get_mlflow_tracker(
    experiment_name: str = "pokemon_battle_winner",
    tracking_uri: Optional[str] = None
) -> MLflowTracker:
    """
    Get or create MLflow tracker instance.
    
    Args:
        experiment_name: Name of the experiment
        tracking_uri: MLflow tracking server URI
    
    Returns:
        MLflowTracker instance
    """
    return MLflowTracker(experiment_name, tracking_uri)
