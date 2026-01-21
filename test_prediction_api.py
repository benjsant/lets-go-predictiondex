#!/usr/bin/env python3
"""
Test Prediction API Service
============================

Tests the prediction service directly without HTTP client.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy.orm import Session
from core.db.session import SessionLocal
from api_pokemon.services import prediction_service


def test_model_loading():
    """Test that the model loads correctly."""
    print("1️⃣ Testing model loading...")

    model_instance = prediction_service.prediction_model
    model_instance.load()

    assert model_instance.model is not None
    assert model_instance.scalers is not None
    assert model_instance.metadata is not None

    print(f"   ✅ Model: {model_instance.metadata['model_type']} v{model_instance.metadata['version']}")
    print(f"   ✅ Features: {model_instance.metadata['n_features']}")
    print(f"   ✅ Test Accuracy: {model_instance.metadata['metrics']['test_accuracy']:.4f}")
    print(f"   ✅ Test ROC-AUC: {model_instance.metadata['metrics']['test_roc_auc']:.4f}")


def test_bulbasaur_vs_charmander():
    """Test: Bulbasaur (Grass) vs Charmander (Fire) - Type DISADVANTAGE."""
    print("\n2️⃣ Testing: Bulbasaur vs Charmander (Grass WEAK against Fire)")

    db = SessionLocal()

    try:
        result = prediction_service.predict_best_move(
            db=db,
            pokemon_a_id=1,  # Bulbasaur
            pokemon_b_id=4,  # Charmander
            available_moves_a=["Charge", "Fouet Lianes", "Tranch'Herbe"]
        )

        print(f"   Pokemon A: {result['pokemon_a_name']} (ID: {result['pokemon_a_id']})")
        print(f"   Pokemon B: {result['pokemon_b_name']} (ID: {result['pokemon_b_id']})")
        print(f"   Recommended: {result['recommended_move']}")
        print(f"   Win Probability: {result['win_probability']*100:.1f}%")

        print(f"\n   📊 All moves ranked:")
        for i, move in enumerate(result['all_moves'], 1):
            winner_emoji = "🏆" if move['predicted_winner'] == 'A' else "⚠️"
            print(f"      {i}. {winner_emoji} {move['move_name']:<18} "
                  f"{move['win_probability']*100:>5.1f}% "
                  f"(power: {move['move_power']:>3}, type_mult: {move['type_multiplier']:.1f}x)")

        # Validate
        assert result['recommended_move'] in ["Charge", "Fouet Lianes", "Tranch'Herbe"]
        assert result['win_probability'] < 0.5  # Should LOSE (type disadvantage - Grass weak to Fire)

        print(f"\n   ✅ Test passed: Type disadvantage correctly detected (Grass weak to Fire)")

    finally:
        db.close()


def test_charmander_vs_bulbasaur():
    """Test: Charmander (Fire) vs Bulbasaur (Grass) - Type ADVANTAGE."""
    print("\n3️⃣ Testing: Charmander vs Bulbasaur (Fire STRONG against Grass)")

    db = SessionLocal()

    try:
        result = prediction_service.predict_best_move(
            db=db,
            pokemon_a_id=4,  # Charmander
            pokemon_b_id=1,  # Bulbasaur
            available_moves_a=["Griffe", "Flammèche"]
        )

        print(f"   Pokemon A: {result['pokemon_a_name']}")
        print(f"   Pokemon B: {result['pokemon_b_name']}")
        print(f"   Recommended: {result['recommended_move']}")
        print(f"   Win Probability: {result['win_probability']*100:.1f}%")

        print(f"\n   📊 All moves ranked:")
        for i, move in enumerate(result['all_moves'], 1):
            winner_emoji = "🏆" if move['predicted_winner'] == 'A' else "⚠️"
            print(f"      {i}. {winner_emoji} {move['move_name']:<18} "
                  f"{move['win_probability']*100:>5.1f}%")

        # Should have higher win probability (type advantage - Fire strong vs Grass)
        assert result['win_probability'] > 0.5

        print(f"\n   ✅ Test passed: Type advantage correctly detected (Fire strong vs Grass)")

    finally:
        db.close()


def test_squirtle_vs_charmander():
    """Test: Squirtle (Water) vs Charmander (Fire) - Super effective."""
    print("\n4️⃣ Testing: Squirtle vs Charmander (Water super effective)")

    db = SessionLocal()

    try:
        result = prediction_service.predict_best_move(
            db=db,
            pokemon_a_id=7,  # Squirtle
            pokemon_b_id=4,  # Charmander
            available_moves_a=["Charge", "Pistolet à O", "Hydrocanon"]
        )

        print(f"   Pokemon A: {result['pokemon_a_name']}")
        print(f"   Pokemon B: {result['pokemon_b_name']}")
        print(f"   Recommended: {result['recommended_move']}")
        print(f"   Win Probability: {result['win_probability']*100:.1f}%")

        print(f"\n   📊 Top 3 moves:")
        for i, move in enumerate(result['all_moves'][:3], 1):
            winner_emoji = "🏆" if move['predicted_winner'] == 'A' else "⚠️"
            print(f"      {i}. {winner_emoji} {move['move_name']:<18} "
                  f"{move['win_probability']*100:>5.1f}% "
                  f"(type_mult: {move['type_multiplier']:.1f}x)")

        # Should strongly prefer Water moves
        assert result['win_probability'] > 0.7

        print(f"\n   ✅ Test passed: Super effective move recommended")

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING PREDICTION API SERVICE")
    print("=" * 70)

    try:
        test_model_loading()
        test_bulbasaur_vs_charmander()
        test_charmander_vs_bulbasaur()
        test_squirtle_vs_charmander()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - API IS READY")
        print("=" * 70)
        print("\n💡 To start the API server:")
        print("   cd api_pokemon")
        print("   uvicorn main:app --reload --port 8000")
        print("\n📚 API docs will be available at:")
        print("   http://localhost:8000/docs")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
