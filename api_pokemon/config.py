"""
API Pokemon Configuration
==========================

Centralized configuration for the Pokemon API service.
Contains paths, environment variables, and constants.
"""

import os
from pathlib import Path

# ================================================================
# PROJECT PATHS
# ================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

# ================================================================
# MLFLOW CONFIGURATION
# ================================================================

# MLflow Model Registry settings
USE_MLFLOW_REGISTRY = os.getenv('USE_MLFLOW_REGISTRY', 'true').lower() == 'true'
MLFLOW_MODEL_NAME = os.getenv('MLFLOW_MODEL_NAME', 'battle_winner_predictor')
MLFLOW_MODEL_STAGE = os.getenv('MLFLOW_MODEL_STAGE', 'Production')
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5001')

# ================================================================
# MODEL CONFIGURATION
# ================================================================

# Default model version to load if MLflow is unavailable
DEFAULT_MODEL_VERSION = os.getenv('MODEL_VERSION', 'v2')

# Feature columns that the model expects
# Note: These should match the feature engineering output
EXPECTED_FEATURE_COLUMNS = [
    # Will be populated from metadata when model is loaded
]

# ================================================================
# PREDICTION THRESHOLDS
# ================================================================

# Minimum confidence threshold for predictions
MIN_PREDICTION_CONFIDENCE = float(os.getenv('MIN_PREDICTION_CONFIDENCE', '0.5'))

# Threshold for "uncertain" predictions
UNCERTAINTY_THRESHOLD = float(os.getenv('UNCERTAINTY_THRESHOLD', '0.6'))

# ================================================================
# FEATURE ENGINEERING CONSTANTS
# ================================================================

# Categorical features to encode
CATEGORICAL_FEATURES = [
    'a_type_1', 'a_type_2', 'b_type_1', 'b_type_2',
    'a_move_type', 'b_move_type'
]

# Numerical features to scale
NUMERICAL_FEATURES_TO_SCALE = [
    'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
    'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
    'a_move_power', 'b_move_power',
    'a_total_stats', 'b_total_stats',
    'speed_diff', 'hp_diff'
]

# Derived features to create
DERIVED_FEATURES = [
    'stat_ratio', 'type_advantage_diff',
    'effective_power_a', 'effective_power_b',
    'effective_power_diff', 'priority_advantage'
]

# ================================================================
# API CONFIGURATION
# ================================================================

# API key for authentication
API_KEY = os.getenv('API_KEY', 'default_key')

# Rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', '60')) # seconds

# ================================================================
# LOGGING CONFIGURATION
# ================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
