"""
Tests for prediction service
=============================

Unit tests for ML prediction service layer.

Coverage target: 85%+ (CRITICAL - 547 LOC)
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from api_pokemon.services import prediction_service
from api_pokemon.services.prediction_service import (
    PredictionModel,
    get_pokemon_with_details,
    get_type_multiplier,
    load_type_effectiveness,
    calculate_effective_power,
    select_best_move_for_matchup,
    prepare_features_for_prediction,
    apply_feature_engineering,
    predict_best_move,
)


# ============================================================
# 🔹 TESTS: PredictionModel Singleton
# ============================================================

class TestPredictionModel:
    """Tests for PredictionModel singleton."""

    def test_singleton_pattern(self):
        """Test that PredictionModel is a singleton."""
        instance1 = PredictionModel()
        instance2 = PredictionModel()
        assert instance1 is instance2

    @patch('builtins.open')
    @patch('pickle.load')
    def test_load_model_artifacts(self, mock_pickle_load, mock_open):
        """Test loading model artifacts from disk."""
        # Reset singleton
        PredictionModel._instance = None
        PredictionModel._model = None
        PredictionModel._scalers = None
        PredictionModel._metadata = None

        # Mock model artifacts
        mock_model = Mock()
        mock_scalers = {'standard_scaler': Mock(), 'standard_scaler_new_features': Mock()}
        mock_metadata = {
            'model_type': 'XGBClassifier',
            'version': 'v1',
            'n_features': 133,
            'feature_columns': ['feature1', 'feature2']
        }

        mock_pickle_load.side_effect = [mock_model, mock_scalers, mock_metadata]

        instance = PredictionModel()
        instance.load()

        assert instance._model == mock_model
        assert instance._scalers == mock_scalers
        assert instance._metadata == mock_metadata
        assert mock_open.call_count == 3

    def test_model_property_lazy_loading(self):
        """Test that model property triggers lazy loading."""
        # Reset singleton
        PredictionModel._instance = None
        PredictionModel._model = None

        instance = PredictionModel()

        with patch.object(instance, 'load') as mock_load:
            # Access model property (should trigger load)
            _ = instance.model
            mock_load.assert_called_once()

    def test_scalers_property_lazy_loading(self):
        """Test that scalers property triggers lazy loading."""
        # Reset singleton
        PredictionModel._instance = None
        PredictionModel._scalers = None

        instance = PredictionModel()

        with patch.object(instance, 'load') as mock_load:
            _ = instance.scalers
            mock_load.assert_called_once()

    def test_metadata_property_lazy_loading(self):
        """Test that metadata property triggers lazy loading."""
        # Reset singleton
        PredictionModel._instance = None
        PredictionModel._metadata = None

        instance = PredictionModel()

        with patch.object(instance, 'load') as mock_load:
            _ = instance.metadata
            mock_load.assert_called_once()


# ============================================================
# 🔹 TESTS: Database Queries
# ============================================================

class TestDatabaseQueries:
    """Tests for database query functions."""

    def test_get_pokemon_with_details_found(self, db_session, sample_pokemon):
        """Test retrieving a Pokemon with all relationships."""
        pikachu = get_pokemon_with_details(db_session, 1)

        assert pikachu is not None
        assert pikachu.id == 1
        assert pikachu.species.name_en == "Pikachu"
        assert pikachu.stats.hp == 35
        assert len(pikachu.types) == 1
        assert pikachu.types[0].type.name == "Électrik"
        assert len(pikachu.moves) >= 1

    def test_get_pokemon_with_details_not_found(self, db_session, sample_pokemon):
        """Test retrieving a non-existent Pokemon."""
        result = get_pokemon_with_details(db_session, 999)
        assert result is None

    def test_load_type_effectiveness(self, db_session, sample_type_effectiveness):
        """Test loading type effectiveness chart."""
        type_eff = load_type_effectiveness(db_session)

        assert isinstance(type_eff, dict)
        # Feu (3) vs Plante (4) = 2x
        assert type_eff[(3, 4)] == 2.0
        # Eau (5) vs Feu (3) = 2x
        assert type_eff[(5, 3)] == 2.0
        # Non-existent combination defaults to 1.0
        assert type_eff[(99, 99)] == 1.0


# ============================================================
# 🔹 TESTS: Type Effectiveness Calculation
# ============================================================

class TestTypeMultiplier:
    """Tests for type effectiveness multiplier calculation."""

    def test_neutral_effectiveness(self):
        """Test neutral type matchup (1x)."""
        type_eff = {(1, 1): 1.0}
        multiplier = get_type_multiplier(1, [1], type_eff)
        assert multiplier == 1.0

    def test_super_effective_single_type(self):
        """Test super effective against single type (2x)."""
        type_eff = {(3, 4): 2.0}  # Feu vs Plante
        multiplier = get_type_multiplier(3, [4], type_eff)
        assert multiplier == 2.0

    def test_not_very_effective(self):
        """Test not very effective (0.5x)."""
        type_eff = {(3, 5): 0.5}  # Feu vs Eau
        multiplier = get_type_multiplier(3, [5], type_eff)
        assert multiplier == 0.5

    def test_super_effective_dual_type(self):
        """Test super effective against dual type (4x)."""
        type_eff = {
            (5, 3): 2.0,  # Eau vs Feu
            (5, 7): 2.0,  # Eau vs Vol
        }
        # Eau vs Feu/Vol = 2x × 2x = 4x
        multiplier = get_type_multiplier(5, [3, 7], type_eff)
        assert multiplier == 4.0

    def test_quarter_effective_dual_type(self):
        """Test double resistance (0.25x)."""
        type_eff = {
            (6, 4): 0.5,  # Électrik vs Plante
            (6, 3): 0.5,  # Électrik vs Feu (hypothetical)
        }
        # Électrik vs Plante/Feu = 0.5 × 0.5 = 0.25x
        multiplier = get_type_multiplier(6, [4, 3], type_eff)
        assert multiplier == 0.25

    def test_missing_type_defaults_to_neutral(self):
        """Test missing type effectiveness defaults to 1.0."""
        type_eff = {}
        multiplier = get_type_multiplier(1, [2], type_eff)
        assert multiplier == 1.0


# ============================================================
# 🔹 TESTS: Move Power Calculation
# ============================================================

class TestEffectivePowerCalculation:
    """Tests for effective power calculation based on damage_type."""

    def test_standard_offensive_move(self):
        """Test standard offensive move (no multiplier)."""
        move = Mock()
        move.power = 100
        move.damage_type = "offensif"

        power = calculate_effective_power(move)
        assert power == 100

    def test_multi_hit_move(self):
        """Test multi-hit move (3x power)."""
        move = Mock()
        move.power = 25
        move.damage_type = "multi_coups"

        power = calculate_effective_power(move)
        assert power == 75  # 25 × 3

    def test_double_damage_move(self):
        """Test double damage move (2x power)."""
        move = Mock()
        move.power = 50
        move.damage_type = "double_degats"

        power = calculate_effective_power(move)
        assert power == 100  # 50 × 2

    def test_two_turn_move(self):
        """Test two-turn move (0.5x power)."""
        move = Mock()
        move.power = 120
        move.damage_type = "deux_tours"

        power = calculate_effective_power(move)
        assert power == 60  # 120 / 2

    def test_move_without_power(self):
        """Test status move (no power)."""
        move = Mock()
        move.power = None
        move.damage_type = "protection"

        power = calculate_effective_power(move)
        assert power == 0

    def test_move_without_damage_type(self):
        """Test move without damage_type defaults to offensif."""
        move = Mock()
        move.power = 80
        move.damage_type = None

        power = calculate_effective_power(move)
        assert power == 80


# ============================================================
# 🔹 TESTS: Move Selection
# ============================================================

class TestMoveSelection:
    """Tests for selecting the best move in a matchup."""

    def test_select_best_move_for_matchup(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test selecting the best move for a matchup."""
        type_eff = load_type_effectiveness(db_session)

        # Pikachu (Électrik) vs Blastoise (Eau)
        pikachu = get_pokemon_with_details(db_session, 1)
        blastoise = get_pokemon_with_details(db_session, 3)

        # Pikachu has: Tonnerre (Électrik, 110 power) and Vive-Attaque (Normal, 40 power)
        best_move = select_best_move_for_matchup(
            pikachu,
            blastoise,
            ['Tonnerre', 'Vive-Attaque'],
            type_eff,
            db_session
        )

        assert best_move is not None
        # Tonnerre should be selected (super effective + higher power)
        assert best_move['move_name'] == 'Tonnerre'
        assert best_move['type_multiplier'] == 2.0  # Électrik vs Eau
        assert best_move['stab'] == 1.5  # STAB for Pikachu

    def test_select_best_move_with_stab(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test that STAB is correctly applied."""
        type_eff = load_type_effectiveness(db_session)

        charizard = get_pokemon_with_details(db_session, 2)
        blastoise = get_pokemon_with_details(db_session, 3)

        # Charizard (Feu/Vol) uses Lance-Flammes (Feu)
        best_move = select_best_move_for_matchup(
            charizard,
            blastoise,
            ['Lance-Flammes'],
            type_eff,
            db_session
        )

        assert best_move is not None
        assert best_move['stab'] == 1.5  # Feu move on Feu-type Pokemon

    def test_select_best_move_no_valid_moves(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test when no valid offensive moves are available."""
        type_eff = load_type_effectiveness(db_session)

        pikachu = get_pokemon_with_details(db_session, 1)
        blastoise = get_pokemon_with_details(db_session, 3)

        # No valid move names
        best_move = select_best_move_for_matchup(
            pikachu,
            blastoise,
            ['NonExistentMove'],
            type_eff,
            db_session
        )

        assert best_move is None

    def test_select_best_move_filters_status_moves(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test that status moves are filtered out."""
        type_eff = load_type_effectiveness(db_session)

        pikachu = get_pokemon_with_details(db_session, 1)
        blastoise = get_pokemon_with_details(db_session, 3)

        # Abri is a status move (category: autre)
        best_move = select_best_move_for_matchup(
            pikachu,
            blastoise,
            ['Abri'],
            type_eff,
            db_session
        )

        # Status moves should be filtered
        assert best_move is None


# ============================================================
# 🔹 TESTS: Feature Preparation
# ============================================================

class TestFeaturePreparation:
    """Tests for feature preparation for ML prediction."""

    def test_prepare_features_for_prediction(self, db_session, sample_pokemon):
        """Test preparing features for a battle prediction."""
        pikachu = get_pokemon_with_details(db_session, 1)
        charizard = get_pokemon_with_details(db_session, 2)

        move_a_info = {
            'move_type_name': 'Électrik',
            'effective_power': 110,
            'priority': 0,
            'stab': 1.5,
            'type_multiplier': 1.0
        }

        move_b_info = {
            'move_type_name': 'Feu',
            'effective_power': 90,
            'priority': 0,
            'stab': 1.5,
            'type_multiplier': 1.0
        }

        features = prepare_features_for_prediction(
            pikachu, charizard, move_a_info, move_b_info
        )

        assert isinstance(features, pd.DataFrame)
        assert len(features) == 1  # Single row

        # Check Pokemon A stats
        assert features['a_hp'].iloc[0] == 35
        assert features['a_attack'].iloc[0] == 55
        assert features['a_speed'].iloc[0] == 90

        # Check Pokemon B stats
        assert features['b_hp'].iloc[0] == 78
        assert features['b_speed'].iloc[0] == 100

        # Check types
        assert features['a_type_1'].iloc[0] == 'Électrik'
        assert features['b_type_1'].iloc[0] == 'Feu'
        assert features['b_type_2'].iloc[0] == 'Vol'

        # Check move info
        assert features['a_move_power'].iloc[0] == 110
        assert features['a_move_type'].iloc[0] == 'Électrik'
        assert features['a_move_stab'].iloc[0] == 1.5

        # Check computed features
        assert features['speed_diff'].iloc[0] == 90 - 100  # -10
        assert features['a_total_stats'].iloc[0] == 35 + 55 + 40 + 50 + 50 + 90

    def test_prepare_features_with_single_type_pokemon(self, db_session, sample_pokemon):
        """Test feature preparation with single-type Pokemon."""
        pikachu = get_pokemon_with_details(db_session, 1)
        blastoise = get_pokemon_with_details(db_session, 3)

        move_a_info = {
            'move_type_name': 'Électrik',
            'effective_power': 110,
            'priority': 0,
            'stab': 1.5,
            'type_multiplier': 2.0
        }

        move_b_info = {
            'move_type_name': 'Eau',
            'effective_power': 90,
            'priority': 0,
            'stab': 1.5,
            'type_multiplier': 0.5
        }

        features = prepare_features_for_prediction(
            pikachu, blastoise, move_a_info, move_b_info
        )

        # Single-type Pokemon should have 'none' for type_2
        assert features['a_type_2'].iloc[0] == 'none'
        assert features['b_type_2'].iloc[0] == 'none'

    def test_prepare_features_a_moves_first(self, db_session, sample_pokemon):
        """Test that a_moves_first is correctly calculated."""
        pikachu = get_pokemon_with_details(db_session, 1)  # Speed: 90
        blastoise = get_pokemon_with_details(db_session, 3)  # Speed: 78

        move_a_info = {
            'move_type_name': 'Électrik',
            'effective_power': 110,
            'priority': 0,
            'stab': 1.5,
            'type_multiplier': 2.0
        }

        move_b_info = {
            'move_type_name': 'Eau',
            'effective_power': 90,
            'priority': 0,
            'stab': 1.5,
            'type_multiplier': 0.5
        }

        features = prepare_features_for_prediction(
            pikachu, blastoise, move_a_info, move_b_info
        )

        # Pikachu is faster
        assert features['a_moves_first'].iloc[0] == 1

    def test_prepare_features_priority_overrides_speed(self, db_session, sample_pokemon):
        """Test that priority overrides speed for move order."""
        pikachu = get_pokemon_with_details(db_session, 1)  # Speed: 90
        charizard = get_pokemon_with_details(db_session, 2)  # Speed: 100

        move_a_info = {
            'move_type_name': 'Normal',
            'effective_power': 40,
            'priority': 1,  # Vive-Attaque
            'stab': 1.0,
            'type_multiplier': 1.0
        }

        move_b_info = {
            'move_type_name': 'Feu',
            'effective_power': 90,
            'priority': 0,
            'stab': 1.5,
            'type_multiplier': 1.0
        }

        features = prepare_features_for_prediction(
            pikachu, charizard, move_a_info, move_b_info
        )

        # Pikachu moves first due to priority (despite lower speed)
        assert features['a_moves_first'].iloc[0] == 1


# ============================================================
# 🔹 TESTS: Feature Engineering
# ============================================================

class TestFeatureEngineering:
    """Tests for feature engineering pipeline."""

    @patch.object(prediction_service.PredictionModel, '_scalers')
    @patch.object(prediction_service.PredictionModel, '_metadata')
    def test_apply_feature_engineering(self, mock_metadata, mock_scalers):
        """Test feature engineering pipeline."""
        # Mock scalers - they should return the input unchanged (identity transform)
        mock_scaler = Mock()
        mock_scaler.transform = Mock(side_effect=lambda x: x)

        mock_scaler_new = Mock()
        mock_scaler_new.transform = Mock(side_effect=lambda x: x)

        mock_scalers.__getitem__ = Mock(side_effect=lambda key: {
            'standard_scaler': mock_scaler,
            'standard_scaler_new_features': mock_scaler_new
        }[key])

        # Mock metadata
        mock_metadata.__getitem__ = Mock(side_effect=lambda key: {
            'feature_columns': ['a_hp', 'a_attack', 'a_type_1_Feu']
        }[key])

        # Create raw features
        df_raw = pd.DataFrame([{
            'a_hp': 35,
            'a_attack': 55,
            'a_defense': 40,
            'a_sp_attack': 50,
            'a_sp_defense': 50,
            'a_speed': 90,
            'b_hp': 78,
            'b_attack': 84,
            'b_defense': 78,
            'b_sp_attack': 109,
            'b_sp_defense': 85,
            'b_speed': 100,
            'a_type_1': 'Électrik',
            'a_type_2': 'none',
            'b_type_1': 'Feu',
            'b_type_2': 'Vol',
            'a_move_power': 110,
            'a_move_type': 'Électrik',
            'a_move_priority': 0,
            'a_move_stab': 1.5,
            'a_move_type_mult': 1.0,
            'b_move_power': 90,
            'b_move_type': 'Feu',
            'b_move_priority': 0,
            'b_move_stab': 1.5,
            'b_move_type_mult': 1.0,
            'speed_diff': -10,
            'hp_diff': -43,
            'a_total_stats': 320,
            'b_total_stats': 534,
            'a_moves_first': 0,
        }])

        features_final = apply_feature_engineering(df_raw)

        assert isinstance(features_final, pd.DataFrame)
        assert len(features_final) == 1

    @patch.object(prediction_service.PredictionModel, '_scalers')
    @patch.object(prediction_service.PredictionModel, '_metadata')
    def test_apply_feature_engineering_adds_missing_columns(
        self,
        mock_metadata,
        mock_scalers
    ):
        """Test that missing feature columns are added with 0."""
        # Mock scalers - they should return the input unchanged (identity transform)
        mock_scaler = Mock()
        mock_scaler.transform = Mock(side_effect=lambda x: x)

        mock_scaler_new = Mock()
        mock_scaler_new.transform = Mock(side_effect=lambda x: x)

        mock_scalers.__getitem__ = Mock(side_effect=lambda key: {
            'standard_scaler': mock_scaler,
            'standard_scaler_new_features': mock_scaler_new
        }[key])

        # Mock metadata with columns that don't exist in input
        mock_metadata.__getitem__ = Mock(side_effect=lambda key: {
            'feature_columns': ['a_hp', 'missing_col_1', 'missing_col_2']
        }[key])

        df_raw = pd.DataFrame([{
            'a_hp': 35,
            'a_attack': 55,
            'a_defense': 40,
            'a_sp_attack': 50,
            'a_sp_defense': 50,
            'a_speed': 90,
            'b_hp': 78,
            'b_attack': 84,
            'b_defense': 78,
            'b_sp_attack': 109,
            'b_sp_defense': 85,
            'b_speed': 100,
            'a_type_1': 'Électrik',
            'a_type_2': 'none',
            'b_type_1': 'Feu',
            'b_type_2': 'Vol',
            'a_move_power': 110,
            'a_move_type': 'Électrik',
            'a_move_priority': 0,
            'a_move_stab': 1.5,
            'a_move_type_mult': 1.0,
            'b_move_power': 90,
            'b_move_type': 'Feu',
            'b_move_priority': 0,
            'b_move_stab': 1.5,
            'b_move_type_mult': 1.0,
            'speed_diff': -10,
            'hp_diff': -43,
            'a_total_stats': 320,
            'b_total_stats': 534,
            'a_moves_first': 0,
        }])

        features_final = apply_feature_engineering(df_raw)

        # Missing columns should be added
        assert 'missing_col_1' in features_final.columns
        assert 'missing_col_2' in features_final.columns
        assert features_final['missing_col_1'].iloc[0] == 0
        assert features_final['missing_col_2'].iloc[0] == 0


# ============================================================
# 🔹 TESTS: Full Prediction Pipeline (Integration)
# ============================================================

class TestPredictionPipeline:
    """Integration tests for the full prediction pipeline."""

    @patch.object(prediction_service.PredictionModel, '_model')
    @patch.object(prediction_service.PredictionModel, '_scalers')
    @patch.object(prediction_service.PredictionModel, '_metadata')
    def test_predict_best_move_success(
        self,
        mock_metadata,
        mock_scalers,
        mock_model,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test successful prediction of best move."""
        # Mock model
        mock_model.predict = Mock(return_value=[1])  # A wins
        mock_model.predict_proba = Mock(return_value=[[0.2, 0.8]])  # 80% win prob

        # Mock scalers
        mock_scaler = Mock()
        mock_scaler.transform = Mock(side_effect=lambda x: x)

        mock_scaler_new = Mock()
        mock_scaler_new.transform = Mock(side_effect=lambda x: x)

        mock_scalers.__getitem__ = Mock(side_effect=lambda key: {
            'standard_scaler': mock_scaler,
            'standard_scaler_new_features': mock_scaler_new
        }[key])

        # Mock metadata
        feature_cols = [
            'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
            'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
            'a_move_power', 'b_move_power', 'a_total_stats', 'b_total_stats',
            'speed_diff', 'hp_diff', 'a_move_stab', 'a_move_type_mult',
            'b_move_stab', 'b_move_type_mult', 'a_move_priority', 'b_move_priority',
            'a_moves_first', 'stat_ratio', 'type_advantage_diff',
            'effective_power_a', 'effective_power_b', 'effective_power_diff',
            'priority_advantage'
        ]
        mock_metadata.__getitem__ = Mock(side_effect=lambda key: {
            'feature_columns': feature_cols
        }[key])

        result = predict_best_move(
            db_session,
            pokemon_a_id=1,  # Pikachu
            pokemon_b_id=3,  # Blastoise
            available_moves_a=['Tonnerre', 'Vive-Attaque']
        )

        assert result is not None
        assert result['pokemon_a_id'] == 1
        assert result['pokemon_a_name'] == 'Pikachu'
        assert result['pokemon_b_id'] == 3
        assert result['pokemon_b_name'] == 'Tortank'
        assert 'recommended_move' in result
        assert 'win_probability' in result
        assert 'all_moves' in result
        assert len(result['all_moves']) >= 1

    @patch.object(prediction_service.PredictionModel, '_model')
    @patch.object(prediction_service.PredictionModel, '_scalers')
    @patch.object(prediction_service.PredictionModel, '_metadata')
    def test_predict_best_move_ranks_by_win_probability(
        self,
        mock_metadata,
        mock_scalers,
        mock_model,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test that moves are ranked by win probability."""
        # Mock different probabilities for different moves
        call_count = [0]

        def mock_predict_proba(features, validate_features=False):
            call_count[0] += 1
            if call_count[0] == 1:
                return [[0.4, 0.6]]  # First move: 60% win prob
            else:
                return [[0.1, 0.9]]  # Second move: 90% win prob

        mock_model.predict = Mock(return_value=[1])
        mock_model.predict_proba = mock_predict_proba

        # Mock scalers
        mock_scaler = Mock()
        mock_scaler.transform = Mock(side_effect=lambda x: x)

        mock_scaler_new = Mock()
        mock_scaler_new.transform = Mock(side_effect=lambda x: x)

        mock_scalers.__getitem__ = Mock(side_effect=lambda key: {
            'standard_scaler': mock_scaler,
            'standard_scaler_new_features': mock_scaler_new
        }[key])

        # Mock metadata
        feature_cols = [
            'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
            'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
            'a_move_power', 'b_move_power', 'a_total_stats', 'b_total_stats',
            'speed_diff', 'hp_diff', 'a_move_stab', 'a_move_type_mult',
            'b_move_stab', 'b_move_type_mult', 'a_move_priority', 'b_move_priority',
            'a_moves_first', 'stat_ratio', 'type_advantage_diff',
            'effective_power_a', 'effective_power_b', 'effective_power_diff',
            'priority_advantage'
        ]
        mock_metadata.__getitem__ = Mock(side_effect=lambda key: {
            'feature_columns': feature_cols
        }[key])

        result = predict_best_move(
            db_session,
            pokemon_a_id=1,
            pokemon_b_id=3,
            available_moves_a=['Tonnerre', 'Vive-Attaque']
        )

        # Moves should be sorted by win probability (highest first)
        all_moves = result['all_moves']
        for i in range(len(all_moves) - 1):
            assert all_moves[i]['win_probability'] >= all_moves[i + 1]['win_probability']

    def test_predict_best_move_pokemon_a_not_found(
        self,
        db_session,
        sample_pokemon
    ):
        """Test error when Pokemon A doesn't exist."""
        with pytest.raises(ValueError, match="Pokemon A with ID 999 not found"):
            predict_best_move(
                db_session,
                pokemon_a_id=999,
                pokemon_b_id=3,
                available_moves_a=['Surf']
            )

    def test_predict_best_move_pokemon_b_not_found(
        self,
        db_session,
        sample_pokemon
    ):
        """Test error when Pokemon B doesn't exist."""
        with pytest.raises(ValueError, match="Pokemon B with ID 999 not found"):
            predict_best_move(
                db_session,
                pokemon_a_id=1,
                pokemon_b_id=999,
                available_moves_a=['Tonnerre']
            )

    def test_predict_best_move_no_valid_moves(
        self,
        db_session,
        sample_pokemon,
        sample_type_effectiveness
    ):
        """Test error when no valid moves are provided."""
        with pytest.raises(ValueError, match="No valid moves found for prediction"):
            predict_best_move(
                db_session,
                pokemon_a_id=1,
                pokemon_b_id=3,
                available_moves_a=['NonExistentMove']
            )
