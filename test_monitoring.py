"""
Script de test pour peupler les métriques de monitoring.
Génère des prédictions en boucle pour tester Prometheus + Grafana + Evidently.
"""

import requests
import time
import random
from datetime import datetime

API_URL = "http://localhost:8000"

# Liste de Pokémon disponibles (IDs réels de la DB)
POKEMON_IDS = list(range(1, 152))  # Génération 1 (1-151)

# Moves populaires par type
WATER_MOVES = ["Surf", "Hydro Pump", "Water Gun", "Bubble Beam", "Aqua Tail"]
FIRE_MOVES = ["Flamethrower", "Fire Blast", "Ember", "Fire Punch", "Heat Wave"]
GRASS_MOVES = ["Solar Beam", "Razor Leaf", "Vine Whip", "Seed Bomb", "Energy Ball"]
ELECTRIC_MOVES = ["Thunder", "Thunderbolt", "Thunder Shock", "Discharge", "Wild Charge"]
PSYCHIC_MOVES = ["Psychic", "Confusion", "Psybeam", "Dream Eater", "Zen Headbutt"]
NORMAL_MOVES = ["Body Slam", "Hyper Beam", "Tackle", "Take Down", "Double-Edge"]
FIGHTING_MOVES = ["Karate Chop", "Low Kick", "Submission", "Seismic Toss", "Hi Jump Kick"]
ROCK_MOVES = ["Rock Throw", "Rock Slide", "Stone Edge", "Earthquake", "Dig"]
ICE_MOVES = ["Ice Beam", "Blizzard", "Ice Punch", "Aurora Beam", "Icy Wind"]

ALL_MOVES = (
    WATER_MOVES + FIRE_MOVES + GRASS_MOVES + ELECTRIC_MOVES + 
    PSYCHIC_MOVES + NORMAL_MOVES + FIGHTING_MOVES + ROCK_MOVES + ICE_MOVES
)


def test_health():
    """Test l'endpoint /health."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health: OK")
            return True
        else:
            print(f"❌ API Health: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API inaccessible: {e}")
        return False


def test_metrics():
    """Test l'endpoint /metrics."""
    try:
        response = requests.get(f"{API_URL}/metrics", timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            has_api_metrics = "api_requests_total" in metrics_text
            has_model_metrics = "model_predictions_total" in metrics_text
            
            print(f"✅ Métriques Prometheus exposées")
            print(f"   - API metrics: {'✅' if has_api_metrics else '❌'}")
            print(f"   - Model metrics: {'✅' if has_model_metrics else '❌'}")
            return True
        else:
            print(f"❌ Metrics endpoint: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Metrics inaccessibles: {e}")
        return False


def generate_prediction(pokemon_a_id, pokemon_b_id, moves=None):
    """
    Génère une prédiction via l'API.
    
    Args:
        pokemon_a_id: ID du Pokémon A
        pokemon_b_id: ID du Pokémon B
        moves: Liste de moves (optionnel)
    
    Returns:
        dict: Résultat de la prédiction ou None
    """
    if moves is None:
        moves = random.sample(ALL_MOVES, k=min(4, len(ALL_MOVES)))
    
    payload = {
        "pokemon_a_id": pokemon_a_id,
        "pokemon_b_id": pokemon_b_id,
        "available_moves": moves
    }
    
    try:
        response = requests.post(
            f"{API_URL}/predict/best-move",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Prediction failed ({response.status_code}): {response.text[:100]}")
            return None
            
    except Exception as e:
        print(f"⚠️  Error during prediction: {e}")
        return None


def run_test_batch(n_predictions=50, delay=0.5):
    """
    Génère un batch de prédictions.
    
    Args:
        n_predictions: Nombre de prédictions à générer
        delay: Délai entre chaque prédiction (secondes)
    """
    print(f"\n{'='*60}")
    print(f"🚀 Génération de {n_predictions} prédictions")
    print(f"{'='*60}\n")
    
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    for i in range(n_predictions):
        # Choisir deux Pokémon aléatoires différents
        pokemon_a = random.choice(POKEMON_IDS)
        pokemon_b = random.choice([p for p in POKEMON_IDS if p != pokemon_a])
        
        # Choisir 3-4 moves aléatoires
        n_moves = random.randint(3, 4)
        moves = random.sample(ALL_MOVES, k=n_moves)
        
        print(f"[{i+1}/{n_predictions}] Pokémon {pokemon_a} vs {pokemon_b} ({', '.join(moves[:2])}...)", end=" ")
        
        result = generate_prediction(pokemon_a, pokemon_b, moves)
        
        if result:
            recommended_move = result.get('recommended_move', 'N/A')
            win_prob = result.get('win_probability', 0)
            print(f"✅ {recommended_move} ({win_prob:.1%})")
            success_count += 1
        else:
            print(f"❌")
            error_count += 1
        
        # Pause entre les requêtes
        time.sleep(delay)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"📊 Résultats")
    print(f"{'='*60}")
    print(f"✅ Succès: {success_count}/{n_predictions} ({success_count/n_predictions*100:.1f}%)")
    print(f"❌ Erreurs: {error_count}/{n_predictions}")
    print(f"⏱️  Durée totale: {elapsed:.1f}s")
    print(f"📈 Débit moyen: {n_predictions/elapsed:.2f} prédictions/s")
    print(f"\n💡 Vérifiez maintenant les dashboards Grafana:")
    print(f"   - http://localhost:3000/d/api-performance")
    print(f"   - http://localhost:3000/d/model-performance")
    print(f"   - http://localhost:9090/graph (Prometheus)")


def main():
    """Point d'entrée principal."""
    print(f"\n{'='*60}")
    print(f"🎯 Test de Monitoring - PredictionDex")
    print(f"{'='*60}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Test de santé
    print("1️⃣  Test de l'API...")
    if not test_health():
        print("\n❌ L'API n'est pas accessible. Lancez d'abord:")
        print("   docker compose up db api -d")
        return
    
    print()
    
    # 2. Test des métriques
    print("2️⃣  Test des métriques Prometheus...")
    if not test_metrics():
        print("\n❌ Les métriques ne sont pas exposées.")
        return
    
    print()
    
    # 3. Menu interactif
    print("3️⃣  Génération de prédictions\n")
    print("Choisissez un mode:")
    print("  1. Quick test    (10 prédictions)")
    print("  2. Medium test   (50 prédictions)")
    print("  3. Stress test   (200 prédictions)")
    print("  4. Custom")
    
    choice = input("\nVotre choix [1-4]: ").strip()
    
    if choice == "1":
        n_predictions = 10
        delay = 1.0
    elif choice == "2":
        n_predictions = 50
        delay = 0.5
    elif choice == "3":
        n_predictions = 200
        delay = 0.2
    elif choice == "4":
        try:
            n_predictions = int(input("Nombre de prédictions: "))
            delay = float(input("Délai entre prédictions (s): "))
        except ValueError:
            print("❌ Valeurs invalides, utilisation des valeurs par défaut")
            n_predictions = 50
            delay = 0.5
    else:
        print("❌ Choix invalide, utilisation du mode Medium")
        n_predictions = 50
        delay = 0.5
    
    # 4. Exécution du batch
    run_test_batch(n_predictions, delay)
    
    # 5. Résumé final
    print(f"\n{'='*60}")
    print(f"✅ Test terminé!")
    print(f"{'='*60}\n")
    print("📋 Prochaines étapes:")
    print("   1. Ouvrir Grafana: http://localhost:3000 (admin/admin)")
    print("   2. Vérifier les dashboards:")
    print("      - API Performance: requêtes, latence, erreurs")
    print("      - Model Performance: prédictions, confiance, latence")
    print("   3. Vérifier Prometheus: http://localhost:9090/graph")
    print("   4. Attendre 1h pour voir un rapport de drift Evidently")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
