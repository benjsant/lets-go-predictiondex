"""
Configuration centralisée pour le pipeline Machine Learning.

Ce module centralise tous les hyperparamètres, configurations de grilles de recherche,
et paramètres de pipeline pour éviter la duplication entre run_machine_learning.py
et train_model.py.

Validation: C10 (hyperparameter optimization)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any


# ================================================================
# SEED GLOBAL
# ================================================================
RANDOM_SEED = 42


# ================================================================
# HYPERPARAMÈTRES XGBOOST (CPU-OPTIMISÉS)
# ================================================================

@dataclass
class XGBoostConfig:
    """Configuration pour XGBoost optimisée pour CPU."""

    n_estimators: int = 100
    max_depth: int = 8
    learning_rate: float = 0.1
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    tree_method: str = 'hist'        # CPU-optimized histogram algorithm
    predictor: str = 'cpu_predictor'  # Explicit CPU predictor
    random_state: int = RANDOM_SEED
    n_jobs: int = -1                 # Use all CPU cores
    eval_metric: str = 'logloss'

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la config en dictionnaire pour XGBoost."""
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
# GRILLES DE RECHERCHE D'HYPERPARAMÈTRES
# ================================================================

@dataclass
class GridSearchConfigFast:
    """
    Grille de recherche rapide pour GridSearchCV.

    Configuration conservative pour entraînement rapide (CI/Docker).
    2×2×2×1×1 = 8 combinaisons (~5-10 min)
    """

    n_estimators: List[int] = field(default_factory=lambda: [100, 200])
    max_depth: List[int] = field(default_factory=lambda: [6, 8, 10])
    learning_rate: List[float] = field(default_factory=lambda: [0.05, 0.1])
    subsample: List[float] = field(default_factory=lambda: [0.8])
    colsample_bytree: List[float] = field(default_factory=lambda: [0.8])
    tree_method: List[str] = field(default_factory=lambda: ['hist'])

    def to_dict(self) -> Dict[str, List]:
        """Convertit en dictionnaire pour GridSearchCV."""
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
    Grille de recherche étendue pour GridSearchCV.

    Configuration exhaustive pour recherche approfondie (production).
    3×3×3×3×3×1 = 243 combinaisons (~2-4 heures)
    """

    n_estimators: List[int] = field(default_factory=lambda: [100, 200, 300])
    max_depth: List[int] = field(default_factory=lambda: [6, 8, 10])
    learning_rate: List[float] = field(default_factory=lambda: [0.05, 0.1, 0.2])
    subsample: List[float] = field(default_factory=lambda: [0.7, 0.8, 0.9])
    colsample_bytree: List[float] = field(default_factory=lambda: [0.7, 0.8, 0.9])
    tree_method: List[str] = field(default_factory=lambda: ['hist'])

    def to_dict(self) -> Dict[str, List]:
        """Convertit en dictionnaire pour GridSearchCV."""
        return {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'subsample': self.subsample,
            'colsample_bytree': self.colsample_bytree,
            'tree_method': self.tree_method,
        }


# ================================================================
# CONFIGURATION DATASET
# ================================================================

@dataclass
class DatasetConfig:
    """Configuration pour la génération de datasets."""

    version: str = 'v1'              # 'v1' ou 'v2'
    scenario_type: str = 'all'       # 'best_move', 'random_move', 'all_combinations', 'all'
    test_size: float = 0.2
    random_seed: int = RANDOM_SEED
    num_random_samples: int = 5      # Pour random_move scenario
    max_combinations: int = 20       # Pour all_combinations scenario


# ================================================================
# CONFIGURATION FEATURE ENGINEERING
# ================================================================

@dataclass
class FeatureEngineeringConfig:
    """Configuration pour le feature engineering."""

    use_derived_features: bool = True
    use_standard_scaling: bool = True

    # Features catégorielles à encoder (one-hot)
    categorical_features: List[str] = field(default_factory=lambda: [
        'a_type_1', 'a_type_2', 'b_type_1', 'b_type_2',
        'a_move_type', 'b_move_type'
    ])

    # Features numériques à normaliser
    numerical_features_to_scale: List[str] = field(default_factory=lambda: [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
        'a_move_power', 'b_move_power',
        'a_total_stats', 'b_total_stats',
        'speed_diff', 'hp_diff'
    ])

    # Features dérivées à créer
    derived_features: List[str] = field(default_factory=lambda: [
        'stat_ratio', 'type_advantage_diff',
        'effective_power_a', 'effective_power_b',
        'effective_power_diff', 'priority_advantage'
    ])

    # Colonnes ID et noms à ne pas inclure dans le modèle
    id_features: List[str] = field(default_factory=lambda: [
        'a_pokedex_number', 'b_pokedex_number',
        'a_pokemon_id', 'b_pokemon_id',
        'pokemon_a_name', 'pokemon_b_name',
        'a_move_id', 'b_move_id',
        'a_move_name', 'b_move_name'
    ])


# ================================================================
# CONFIGURATION PIPELINE COMPLÈTE
# ================================================================

@dataclass
class MLPipelineConfig:
    """Configuration complète du pipeline ML."""

    # Sous-configurations
    xgboost: XGBoostConfig = field(default_factory=XGBoostConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    features: FeatureEngineeringConfig = field(default_factory=FeatureEngineeringConfig)

    # Paramètres d'entraînement
    use_gridsearch: bool = False
    grid_type: str = 'fast'          # 'fast' ou 'extended'
    use_early_stopping: bool = True
    early_stopping_rounds: int = 10

    # MLflow
    use_mlflow: bool = True
    mlflow_experiment_name: str = "pokemon_battle_prediction"

    def get_grid_config(self) -> Dict[str, List]:
        """Retourne la grille de recherche selon le type."""
        if self.grid_type == 'extended':
            return GridSearchConfigExtended().to_dict()
        return GridSearchConfigFast().to_dict()


# ================================================================
# INSTANCES PAR DÉFAUT (pour import direct)
# ================================================================

# Configurations par défaut réutilisables
DEFAULT_XGBOOST_CONFIG = XGBoostConfig()
DEFAULT_DATASET_CONFIG = DatasetConfig()
DEFAULT_FEATURE_CONFIG = FeatureEngineeringConfig()
DEFAULT_PIPELINE_CONFIG = MLPipelineConfig()

# Grilles de recherche
XGBOOST_PARAM_GRID_FAST = GridSearchConfigFast().to_dict()
XGBOOST_PARAM_GRID_EXTENDED = GridSearchConfigExtended().to_dict()

# Hyperparamètres XGBoost en dict (backward compatibility)
XGBOOST_PARAMS = DEFAULT_XGBOOST_CONFIG.to_dict()
