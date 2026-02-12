"""
Global constants for the Machine Learning pipeline.

This module centralizes all constants shared between different
ML pipeline modules (dataset, training, evaluation).
"""

import os
from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports" / "ml"


def get_data_dir(version: str = 'v1') -> Path:
    """
    Return the data directory according to the dataset version.

    Args:
        version: 'v1' for battle_winner, 'v2' for battle_winner_v2

    Returns:
        Path: Path to the data directory
    """
    suffix = '' if version == 'v1' else '_v2'
    return PROJECT_ROOT / "data" / "ml" / f"battle_winner{suffix}"


def get_raw_dir(version: str = 'v1') -> Path:
    """Return the raw directory according to the version."""
    return get_data_dir(version) / "raw"


def get_processed_dir(version: str = 'v1') -> Path:
    """Return the processed directory according to the version."""
    return get_data_dir(version) / "processed"


def get_features_dir(version: str = 'v1') -> Path:
    """Return the features directory according to the version."""
    return get_data_dir(version) / "features"


# Database configuration
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")


def get_db_connection_string() -> str:
    """
    Build the PostgreSQL connection string.

    Returns:
        str: Connection string in format postgresql://user:pass@host:port/db
    """
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Scenario types (Dataset V2)
SCENARIO_TYPES = {
    'best_move': 'Best move strategy for both Pokemon',
    'random_move': 'Random move selection',
    'all_combinations': 'All possible move combinations',
    'all': 'All scenarios combined'
}


# Allowed damage types
ALLOWED_DAMAGE_TYPES = {
    'physical', 'special', 'status'
}


# Evaluation metrics
DEFAULT_METRICS = [
    'accuracy',
    'precision',
    'recall',
    'f1',
    'roc_auc'
]


# Feature columns

# Pokemon stats columns
POKEMON_STAT_COLUMNS = [
    'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed'
]

# Type columns
TYPE_COLUMNS = ['type_1', 'type_2']

# Move columns
MOVE_COLUMNS = ['move_id', 'move_type', 'move_power', 'move_priority', 'move_stab', 'move_type_mult']

# ID columns (to exclude from training)
ID_COLUMNS = [
    'a_pokedex_number', 'b_pokedex_number',
    'a_pokemon_id', 'b_pokemon_id',
    'a_move_id', 'b_move_id'
]


# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
MLFLOW_EXPERIMENT_NAME = "pokemon_battle_prediction"
MLFLOW_MODEL_NAME = "battle_winner_predictor"


# Early stopping
EARLY_STOPPING_ROUNDS = 10
VALIDATION_SPLIT = 0.2


# Default values
DEFAULT_TEST_SIZE = 0.2
DEFAULT_NUM_RANDOM_SAMPLES = 5
DEFAULT_MAX_COMBINATIONS = 20
