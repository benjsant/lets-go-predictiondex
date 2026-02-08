"""
Centralized configuration for the Machine Learning pipeline.

This module centralizes all hyperparameters, grid search configurations,
and pipeline parameters to avoid duplication between run_machine_learning.py
and train_model.py.

Validation: C10 (hyperparameter optimization)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any

# Import platform configuration for Windows/Linux detection
try:
    from machine_learning.platform_config import SAFE_N_JOBS, SAFE_GRIDSEARCH_N_JOBS
except ImportError:
    # Fallback if platform_config not available
    import multiprocessing
    SAFE_N_JOBS = -1
    SAFE_GRIDSEARCH_N_JOBS = max(1, multiprocessing.cpu_count() // 2)


# ================================================================
# GLOBAL SEED
# ================================================================
RANDOM_SEED = 42


# ================================================================
# XGBOOST HYPERPARAMETERS (CPU-OPTIMIZED)
# ================================================================

@dataclass
class XGBoostConfig:
    """
    CPU-optimized configuration for XGBoost.

    n_jobs is automatically adjusted according to the platform:
    - Linux: -1 (all cores)
    - Windows: 50% of cores (to avoid memory saturation)
    """

    n_estimators: int = 100
    max_depth: int = 8
    learning_rate: float = 0.1
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    tree_method: str = 'hist'        # CPU-optimized histogram algorithm
    predictor: str = 'cpu_predictor'  # Explicit CPU predictor
    random_state: int = RANDOM_SEED
    n_jobs: int = SAFE_N_JOBS        # Auto-adjusted according to platform (Windows/Linux)
    eval_metric: str = 'logloss'

    def to_dict(self) -> Dict[str, Any]:
        """Convert the config to a dictionary for XGBoost."""
        return {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'subsample': self.subsample,
            'colsample_bytree': self.colsample_bytree,
            'tree_method': self.tree_method,
            'predictor': self.predictor,
            'random_state': self.random_state,
            'n_jobs': self.n_jobs,
            'eval_metric': self.eval_metric,
        }


# ================================================================
# HYPERPARAMETER SEARCH GRIDS
# ================================================================

@dataclass
class GridSearchConfigFast:
    """
    Fast search grid for GridSearchCV.

    Conservative configuration for fast training (CI/Docker).
    2×2×2×1×1 = 8 combinations (~5-10 min)
    """

    n_estimators: List[int] = field(default_factory=lambda: [100, 200])
    max_depth: List[int] = field(default_factory=lambda: [6, 8, 10])
    learning_rate: List[float] = field(default_factory=lambda: [0.05, 0.1])
    subsample: List[float] = field(default_factory=lambda: [0.8])
    colsample_bytree: List[float] = field(default_factory=lambda: [0.8])
    tree_method: List[str] = field(default_factory=lambda: ['hist'])

    def to_dict(self) -> Dict[str, List]:
        """Convert to dictionary for GridSearchCV."""
        return {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'subsample': self.subsample,
            'colsample_bytree': self.colsample_bytree,
            'tree_method': self.tree_method,
        }


@dataclass
class GridSearchConfigExtended:
    """
    Extended search grid for GridSearchCV.

    Exhaustive configuration for in-depth search (production).
    3×3×3×3×3×1 = 243 combinations (~2-4 hours)
    """

    n_estimators: List[int] = field(default_factory=lambda: [100, 200, 300])
    max_depth: List[int] = field(default_factory=lambda: [6, 8, 10])
    learning_rate: List[float] = field(default_factory=lambda: [0.05, 0.1, 0.2])
    subsample: List[float] = field(default_factory=lambda: [0.7, 0.8, 0.9])
    colsample_bytree: List[float] = field(default_factory=lambda: [0.7, 0.8, 0.9])
    tree_method: List[str] = field(default_factory=lambda: ['hist'])

    def to_dict(self) -> Dict[str, List]:
        """Convert to dictionary for GridSearchCV."""
        return {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'subsample': self.subsample,
            'colsample_bytree': self.colsample_bytree,
            'tree_method': self.tree_method,
        }


# ================================================================
# DATASET CONFIGURATION
# ================================================================

@dataclass
class DatasetConfig:
    """Configuration for dataset generation."""

    version: str = 'v1'              # 'v1' or 'v2'
    scenario_type: str = 'all'       # 'best_move', 'random_move', 'all_combinations', 'all'
    test_size: float = 0.2
    random_seed: int = RANDOM_SEED
    num_random_samples: int = 5      # For random_move scenario
    max_combinations: int = 20       # For all_combinations scenario


# ================================================================
# FEATURE ENGINEERING CONFIGURATION
# ================================================================

@dataclass
class FeatureEngineeringConfig:
    """Configuration for feature engineering."""

    use_derived_features: bool = True
    use_standard_scaling: bool = True

    # Categorical features to encode (one-hot)
    categorical_features: List[str] = field(default_factory=lambda: [
        'a_type_1', 'a_type_2', 'b_type_1', 'b_type_2',
        'a_move_type', 'b_move_type'
    ])

    # Numerical features to normalize
    numerical_features_to_scale: List[str] = field(default_factory=lambda: [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
        'a_move_power', 'b_move_power',
        'a_total_stats', 'b_total_stats',
        'speed_diff', 'hp_diff'
    ])

    # Derived features to create
    derived_features: List[str] = field(default_factory=lambda: [
        'stat_ratio', 'type_advantage_diff',
        'effective_power_a', 'effective_power_b',
        'effective_power_diff', 'priority_advantage'
    ])

    # ID and name columns not to include in the model
    id_features: List[str] = field(default_factory=lambda: [
        'a_pokedex_number', 'b_pokedex_number',
        'a_pokemon_id', 'b_pokemon_id',
        'pokemon_a_name', 'pokemon_b_name',
        'a_move_id', 'b_move_id',
        'a_move_name', 'b_move_name'
    ])


# ================================================================
# COMPLETE PIPELINE CONFIGURATION
# ================================================================

@dataclass
class MLPipelineConfig:
    """Complete ML pipeline configuration."""

    # Sub-configurations
    xgboost: XGBoostConfig = field(default_factory=XGBoostConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    features: FeatureEngineeringConfig = field(default_factory=FeatureEngineeringConfig)

    # Training parameters
    use_gridsearch: bool = False
    grid_type: str = 'fast'          # 'fast' or 'extended'
    use_early_stopping: bool = True
    early_stopping_rounds: int = 10

    # MLflow
    use_mlflow: bool = True
    mlflow_experiment_name: str = "pokemon_battle_prediction"

    def get_grid_config(self) -> Dict[str, List]:
        """Return the search grid according to the type."""
        if self.grid_type == 'extended':
            return GridSearchConfigExtended().to_dict()
        return GridSearchConfigFast().to_dict()


# ================================================================
# DEFAULT INSTANCES (for direct import)
# ================================================================

# Reusable default configurations
DEFAULT_XGBOOST_CONFIG = XGBoostConfig()
DEFAULT_DATASET_CONFIG = DatasetConfig()
DEFAULT_FEATURE_CONFIG = FeatureEngineeringConfig()
DEFAULT_PIPELINE_CONFIG = MLPipelineConfig()

# Search grids
XGBOOST_PARAM_GRID_FAST = GridSearchConfigFast().to_dict()
XGBOOST_PARAM_GRID_EXTENDED = GridSearchConfigExtended().to_dict()

# XGBoost hyperparameters as dict (backward compatibility)
XGBOOST_PARAMS = DEFAULT_XGBOOST_CONFIG.to_dict()

# Exported for external use
__all__ = [
    'SAFE_N_JOBS',
    'SAFE_GRIDSEARCH_N_JOBS',
    'RANDOM_SEED',
    'XGBOOST_PARAMS',
    'XGBOOST_PARAM_GRID_FAST',
    'XGBOOST_PARAM_GRID_EXTENDED',
]
