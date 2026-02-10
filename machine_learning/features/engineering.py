"""
Feature engineering class for Pokemon battle prediction.

This module provides a reusable class that encapsulates all feature engineering
logic, eliminating code duplication between training scripts.

Validation: C12 (preprocessing pipeline tests)
"""

from typing import Tuple, Dict, List
import pandas as pd
from sklearn.preprocessing import StandardScaler

from machine_learning.config import FeatureEngineeringConfig


class PokemonFeatureEngineer:
    """
    Feature engineering pipeline for Pokemon battle data.

    This class handles:
    1. One-hot encoding of categorical features (types)
    2. Removal of ID and categorical columns
    3. Normalization of numerical features
    4. Creation of derived features (ratios, advantages, etc.)
    5. Normalization of derived features

    Attributes:
        config: Feature engineering configuration
        scaler: StandardScaler for numerical features
        scaler_derived: StandardScaler for derived features
        feature_columns: List of final feature column names
    """

    def __init__(self, config: FeatureEngineeringConfig = None):
        """
        Initialize the feature engineer.

        Args:
            config: Feature engineering configuration. If None, uses default.
        """
        self.config = config or FeatureEngineeringConfig()
        self.scaler = StandardScaler()
        self.scaler_derived = StandardScaler()
        self.feature_columns = []

    def fit_transform(
        self,
        df_train: pd.DataFrame,
        df_test: pd.DataFrame,
        verbose: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Dict, List[str]]:
        """
        Fit the feature engineering pipeline and transform train/test data.

        This is the main method that applies all feature engineering steps
        in the correct order. It should be called during training.

        Args:
            df_train: Training dataframe with 'winner' column
            df_test: Test dataframe with 'winner' column
            verbose: Whether to print progress information

        Returns:
            Tuple containing:
            - X_train_encoded: Transformed training features
            - X_test_encoded: Transformed test features
            - y_train: Training labels
            - y_test: Test labels
            - scalers: Dictionary with both scalers
            - feature_columns: List of final feature names

        Example:
            >>> engineer = PokemonFeatureEngineer()
            >>> X_train, X_test, y_train, y_test, scalers, features = engineer.fit_transform(
            ...     df_train, df_test
            ... )
        """
        if verbose:
            print("\n" + "=" * 80)
            print("FEATURE ENGINEERING PIPELINE")
            print("=" * 80)

        # Separate target
        y_train = df_train['winner']
        y_test = df_test['winner']

        X_train = df_train.drop(columns=['winner']).copy()
        X_test = df_test.drop(columns=['winner']).copy()

        # Step 1: One-hot encode categorical features
        X_train, X_test = self._encode_categorical(X_train, X_test, verbose)

        # Step 2: Remove categorical columns and IDs
        X_train, X_test = self._drop_unnecessary_columns(X_train, X_test, verbose)

        # Step 3: Normalize numerical features
        X_train, X_test = self._normalize_numerical(X_train, X_test, df_train, df_test, verbose)

        # Step 4: Create derived features (using original values from df_train/df_test)
        X_train, X_test = self._create_derived_features(X_train, X_test, df_train, df_test, verbose)

        # Step 5: Normalize derived features
        X_train, X_test = self._normalize_derived_features(X_train, X_test, verbose)

        # Store feature columns
        self.feature_columns = X_train.columns.tolist()

        if verbose:
            print(f"\n✅ Final feature count: {len(self.feature_columns)}")

        scalers = {
            'standard_scaler': self.scaler,
            'standard_scaler_new_features': self.scaler_derived
        }

        return X_train, X_test, y_train, y_test, scalers, self.feature_columns

    def transform(
        self,
        df: pd.DataFrame,
        verbose: bool = False
    ) -> pd.DataFrame:
        """
        Transform new data using fitted scalers (for inference).

        This method should be called on new data during inference/prediction.
        It assumes fit_transform() was called first during training.

        Args:
            df: DataFrame to transform (without 'winner' column)
            verbose: Whether to print progress information

        Returns:
            Transformed features as DataFrame

        Raises:
            ValueError: If scalers have not been fitted yet
        """
        if not hasattr(self.scaler, 'mean_'):
            raise ValueError("Scalers not fitted. Call fit_transform() first during training.")

        X = df.copy()

        # Apply same transformations (without fitting)
        X = self._encode_categorical_inference(X, verbose)
        X = self._drop_unnecessary_columns_inference(X, verbose)
        X = self._normalize_numerical_inference(X, df, verbose)
        X = self._create_derived_features_inference(X, df, verbose)
        X = self._normalize_derived_features_inference(X, verbose)

        # Ensure same columns as training
        missing_cols = set(self.feature_columns) - set(X.columns)
        for col in missing_cols:
            X[col] = 0

        X = X[self.feature_columns]

        return X

    # ========================================================================
    # PRIVATE METHODS - TRAINING (FIT_TRANSFORM)
    # ========================================================================

    def _encode_categorical(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        verbose: bool
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """One-hot encode categorical features."""
        if verbose:
            print("\n1️⃣ One-hot encoding categorical features...")

        for feature in self.config.categorical_features:
            if feature in X_train.columns:
                train_dummies = pd.get_dummies(X_train[feature], prefix=feature, drop_first=False)
                test_dummies = pd.get_dummies(X_test[feature], prefix=feature, drop_first=False)

                # Align columns
                train_dummies, test_dummies = train_dummies.align(
                    test_dummies, join='left', axis=1, fill_value=0
                )

                X_train = pd.concat([X_train, train_dummies], axis=1)
                X_test = pd.concat([X_test, test_dummies], axis=1)

        if verbose:
            print(f"   After encoding: {X_train.shape[1]} columns")

        return X_train, X_test

    def _drop_unnecessary_columns(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        verbose: bool
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Remove categorical columns, IDs, and scenario_type."""
        columns_to_drop = self.config.categorical_features + self.config.id_features

        # Also remove scenario_type if present
        if 'scenario_type' in X_train.columns:
            columns_to_drop.append('scenario_type')

        # Only drop columns that exist
        columns_to_drop = [col for col in columns_to_drop if col in X_train.columns]

        X_train = X_train.drop(columns=columns_to_drop)
        X_test = X_test.drop(columns=columns_to_drop)

        if verbose:
            print(f"   After dropping categorical/IDs: {X_train.shape[1]} columns")

        return X_train, X_test

    def _normalize_numerical(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        df_train: pd.DataFrame,
        df_test: pd.DataFrame,
        verbose: bool
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Normalize numerical features using StandardScaler."""
        if verbose:
            print("\n2️⃣ Normalizing numerical features...")

        features_to_scale = [f for f in self.config.numerical_features_to_scale if f in X_train.columns]

        self.scaler.fit(X_train[features_to_scale])
        X_train[features_to_scale] = self.scaler.transform(X_train[features_to_scale])
        X_test[features_to_scale] = self.scaler.transform(X_test[features_to_scale])

        if verbose:
            print(f"   {len(features_to_scale)} features normalized")

        return X_train, X_test

    def _create_derived_features(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        df_train: pd.DataFrame,
        df_test: pd.DataFrame,
        verbose: bool
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Create derived features using original (non-normalized) values."""
        if verbose:
            print("\n3️⃣ Creating derived features...")

        # Stat ratio
        X_train['stat_ratio'] = df_train['a_total_stats'] / (df_train['b_total_stats'] + 1)
        X_test['stat_ratio'] = df_test['a_total_stats'] / (df_test['b_total_stats'] + 1)

        # Type advantage difference
        X_train['type_advantage_diff'] = df_train['a_move_type_mult'] - df_train['b_move_type_mult']
        X_test['type_advantage_diff'] = df_test['a_move_type_mult'] - df_test['b_move_type_mult']

        # Effective power A
        X_train['effective_power_a'] = (
            df_train['a_move_power'] * df_train['a_move_stab'] * df_train['a_move_type_mult']
        )
        X_test['effective_power_a'] = (
            df_test['a_move_power'] * df_test['a_move_stab'] * df_test['a_move_type_mult']
        )

        # Effective power B
        X_train['effective_power_b'] = (
            df_train['b_move_power'] * df_train['b_move_stab'] * df_train['b_move_type_mult']
        )
        X_test['effective_power_b'] = (
            df_test['b_move_power'] * df_test['b_move_stab'] * df_test['b_move_type_mult']
        )

        # Effective power difference
        X_train['effective_power_diff'] = (
            X_train['effective_power_a'] - X_train['effective_power_b']
        )
        X_test['effective_power_diff'] = (
            X_test['effective_power_a'] - X_test['effective_power_b']
        )

        # Priority advantage
        X_train['priority_advantage'] = df_train['a_move_priority'] - df_train['b_move_priority']
        X_test['priority_advantage'] = df_test['a_move_priority'] - df_test['b_move_priority']

        if verbose:
            print(f"   Created {len(self.config.derived_features)} derived features")
            print(f"   After derived features: {X_train.shape[1]} columns")

        return X_train, X_test

    def _normalize_derived_features(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        verbose: bool
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Normalize derived features using a second StandardScaler."""
        if verbose:
            print("\n4️⃣ Normalizing derived features...")

        self.scaler_derived.fit(X_train[self.config.derived_features])
        X_train[self.config.derived_features] = self.scaler_derived.transform(
            X_train[self.config.derived_features]
        )
        X_test[self.config.derived_features] = self.scaler_derived.transform(
            X_test[self.config.derived_features]
        )

        if verbose:
            print(f"   {len(self.config.derived_features)} derived features normalized")

        return X_train, X_test

    # ========================================================================
    # PRIVATE METHODS - INFERENCE (TRANSFORM)
    # ========================================================================

    def _encode_categorical_inference(self, X: pd.DataFrame, verbose: bool) -> pd.DataFrame:
        """One-hot encode categorical features for inference."""
        for feature in self.config.categorical_features:
            if feature in X.columns:
                dummies = pd.get_dummies(X[feature], prefix=feature, drop_first=False)
                X = pd.concat([X, dummies], axis=1)
        return X

    def _drop_unnecessary_columns_inference(self, X: pd.DataFrame, verbose: bool) -> pd.DataFrame:
        """Remove unnecessary columns for inference."""
        columns_to_drop = self.config.categorical_features + self.config.id_features
        if 'scenario_type' in X.columns:
            columns_to_drop.append('scenario_type')
        columns_to_drop = [col for col in columns_to_drop if col in X.columns]
        return X.drop(columns=columns_to_drop)

    def _normalize_numerical_inference(
        self,
        X: pd.DataFrame,
        df_original: pd.DataFrame,
        verbose: bool
    ) -> pd.DataFrame:
        """Normalize numerical features for inference using fitted scaler."""
        features_to_scale = [f for f in self.config.numerical_features_to_scale if f in X.columns]
        X[features_to_scale] = self.scaler.transform(X[features_to_scale])
        return X

    def _create_derived_features_inference(
        self,
        X: pd.DataFrame,
        df_original: pd.DataFrame,
        verbose: bool
    ) -> pd.DataFrame:
        """Create derived features for inference."""
        X['stat_ratio'] = df_original['a_total_stats'] / (df_original['b_total_stats'] + 1)
        X['type_advantage_diff'] = df_original['a_move_type_mult'] - df_original['b_move_type_mult']
        X['effective_power_a'] = (
            df_original['a_move_power'] * df_original['a_move_stab'] * df_original['a_move_type_mult']
        )
        X['effective_power_b'] = (
            df_original['b_move_power'] * df_original['b_move_stab'] * df_original['b_move_type_mult']
        )
        X['effective_power_diff'] = X['effective_power_a'] - X['effective_power_b']
        X['priority_advantage'] = df_original['a_move_priority'] - df_original['b_move_priority']
        return X

    def _normalize_derived_features_inference(
        self,
        X: pd.DataFrame,
        verbose: bool
    ) -> pd.DataFrame:
        """Normalize derived features for inference using fitted scaler."""
        X[self.config.derived_features] = self.scaler_derived.transform(X[self.config.derived_features])
        return X
