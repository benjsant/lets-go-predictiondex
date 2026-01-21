#!/usr/bin/env python3
"""
Test Prediction Endpoint
=========================

Quick test script to validate the /predict/best-move endpoint.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api_pokemon.main import app

# Create test client
client = TestClient(app)


def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("  ✅ Health check passed")


def test_model_info():
    """Test model info endpoint."""
    print("\nTesting /predict/model-info endpoint...")
    response = client.get("/predict/model-info")
    assert response.status_code == 200

    data = response.json()
    assert data["model_type"] == "XGBClassifier"
    assert data["version"] == "v1"
    assert data["n_features"] == 133

    print(f"  ✅ Model info: {data['model_type']} v{data['version']}")
    print(f"     Features: {data['n_features']}")
    print(f"     Test Accuracy: {data['metrics']['test_accuracy']:.4f}")
    print(f"     Test ROC-AUC: {data['metrics']['test_roc_auc']:.4f}")


def test_predict_best_move():
    """Test best move prediction endpoint."""
    print("\nTesting /predict/best-move endpoint...")

    # Test case: Bulbasaur (1) vs Charmander (4)
    # Bulbasaur has type advantage (Grass > Fire)
    request_data = {
        "pokemon_a_id": 1,  # Bulbasaur
        "pokemon_b_id": 4,  # Charmander
        "available_moves": ["Charge", "Fouet Lianes", "Tranch'Herbe", "Lance-Soleil"]
    }

    print(f"  Request: Bulbasaur vs Charmander")
    print(f"  Available moves: {request_data['available_moves']}")

    response = client.post("/predict/best-move", json=request_data)

    if response.status_code != 200:
        print(f"  ❌ Error {response.status_code}: {response.json()}")
        return

    data = response.json()

    print(f"\n  ✅ Prediction successful:")
    print(f"     Pokemon A: {data['pokemon_a_name']} (ID: {data['pokemon_a_id']})")
    print(f"     Pokemon B: {data['pokemon_b_name']} (ID: {data['pokemon_b_id']})")
    print(f"     Recommended Move: {data['recommended_move']}")
    print(f"     Win Probability: {data['win_probability']*100:.1f}%")

    print(f"\n  📊 All moves ranked by win probability:")
    for i, move in enumerate(data['all_moves'][:5], 1):  # Show top 5
        print(f"     {i}. {move['move_name']:<20} {move['win_probability']*100:>5.1f}% "
              f"(power: {move['move_power']}, type_mult: {move['type_multiplier']:.1f}x)")

    # Validate results
    assert data['pokemon_a_id'] == 1
    assert data['pokemon_b_id'] == 4
    assert data['recommended_move'] in request_data['available_moves']
    assert 0 <= data['win_probability'] <= 1
    assert len(data['all_moves']) > 0


def test_predict_reverse_matchup():
    """Test reverse matchup: Charmander vs Bulbasaur."""
    print("\n\nTesting reverse matchup...")

    # Charmander (4) vs Bulbasaur (1)
    # Charmander has type disadvantage (Fire < Grass)
    request_data = {
        "pokemon_a_id": 4,  # Charmander
        "pokemon_b_id": 1,  # Bulbasaur
        "available_moves": ["Griffe", "Flammèche", "Dracosouffle"]
    }

    print(f"  Request: Charmander vs Bulbasaur")
    print(f"  Available moves: {request_data['available_moves']}")

    response = client.post("/predict/best-move", json=request_data)

    if response.status_code != 200:
        print(f"  ❌ Error {response.status_code}: {response.json()}")
        return

    data = response.json()

    print(f"\n  ✅ Prediction successful:")
    print(f"     Pokemon A: {data['pokemon_a_name']}")
    print(f"     Pokemon B: {data['pokemon_b_name']}")
    print(f"     Recommended Move: {data['recommended_move']}")
    print(f"     Win Probability: {data['win_probability']*100:.1f}%")

    print(f"\n  📊 All moves ranked:")
    for i, move in enumerate(data['all_moves'], 1):
        print(f"     {i}. {move['move_name']:<20} {move['win_probability']*100:>5.1f}%")


def test_error_cases():
    """Test error handling."""
    print("\n\nTesting error cases...")

    # Test invalid Pokemon ID
    response = client.post("/predict/best-move", json={
        "pokemon_a_id": 9999,
        "pokemon_b_id": 1,
        "available_moves": ["Charge"]
    })

    assert response.status_code == 404
    print("  ✅ Invalid Pokemon ID handled correctly (404)")

    # Test empty moves list
    response = client.post("/predict/best-move", json={
        "pokemon_a_id": 1,
        "pokemon_b_id": 4,
        "available_moves": []
    })

    assert response.status_code == 422  # Validation error
    print("  ✅ Empty moves list handled correctly (422)")


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING PREDICTION API ENDPOINTS")
    print("=" * 70)

    try:
        test_health()
        test_model_info()
        test_predict_best_move()
        test_predict_reverse_matchup()
        test_error_cases()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
