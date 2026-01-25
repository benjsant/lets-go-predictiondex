"""
Script de test intelligent pour le monitoring.
Utilise les vraies capacités des Pokémon depuis la base de données.
"""

import requests
import time
import random
from datetime import datetime

API_URL = "http://localhost:8000"

# Cache des Pokémon et leurs moves
pokemon_cache = {}


def get_pokemon_moves(pokemon_id):
    """
    Récupère les moves offensifs d'un Pokémon depuis l'API.
    
    Args:
        pokemon_id: ID du Pokémon
    
    Returns:
        list: Liste des noms de moves offensifs
    """
    if pokemon_id in pokemon_cache:
        return pokemon_cache[pokemon_id]
    
    try:
        response = requests.get(f"{API_URL}/pokemon/{pokemon_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Filtrer les moves offensifs (avec power)
            offensive_moves = [
                move['name'] 
                for move in data.get('moves', []) 
                if move.get('power') is not None and move.get('power') > 0
            ]
            pokemon_cache[pokemon_id] = {
                'name': data['species']['name_fr'],
                'moves': offensive_moves
            }
            return pokemon_cache[pokemon_id]
    except Exception as e:
        print(f"⚠️  Erreur récupération Pokémon {pokemon_id}: {e}")
    
    return None


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


def generate_prediction(pokemon_a_id, pokemon_b_id):
    """
    Génère une prédiction avec les vraies capacités.
    
    Args:
        pokemon_a_id: ID du Pokémon A
        pokemon_b_id: ID du Pokémon B
    
    Returns:
        dict: Résultat de la prédiction ou None
    """
    # Récupérer les moves des deux Pokémon
    pokemon_a = get_pokemon_moves(pokemon_a_id)
    pokemon_b = get_pokemon_moves(pokemon_b_id)
    
    if not pokemon_a or not pokemon_b:
        return None
    
    if not pokemon_a['moves'] or not pokemon_b['moves']:
        return None
    
    # Choisir 3-4 moves pour A
    n_moves = min(4, len(pokemon_a['moves']))
    moves_a = random.sample(pokemon_a['moves'], k=n_moves)
    
    payload = {
        "pokemon_a_id": pokemon_a_id,
        "pokemon_b_id": pokemon_b_id,
        "available_moves": moves_a
    }
    
    try:
        response = requests.post(
            f"{API_URL}/predict/best-move",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            result['pokemon_a_name'] = pokemon_a['name']
            result['pokemon_b_name'] = pokemon_b['name']
            return result
        else:
            print(f"⚠️  Prediction failed ({response.status_code}): {response.text[:100]}")
            return None
            
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None


def run_test_batch(n_predictions=50, delay=0.5):
    """
    Génère un batch de prédictions avec vraies données.
    
    Args:
        n_predictions: Nombre de prédictions
        delay: Délai entre prédictions (secondes)
    """
    print(f"\n{'='*70}")
    print(f"🚀 Génération de {n_predictions} prédictions avec vraies capacités")
    print(f"{'='*70}\n")
    
    # IDs Pokémon populaires (Génération 1)
    popular_ids = [
        1, 4, 7, 25, 6, 9, 3,  # Starters + Pikachu + Evos
        35, 36, 39, 40,  # Fées
        94, 65, 59, 68,  # Fantômes/Psy/Combat
        130, 131, 144, 145, 146, 150, 151  # Légendaires
    ]
    
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    for i in range(n_predictions):
        # Choisir deux Pokémon différents
        pokemon_a_id = random.choice(popular_ids)
        pokemon_b_id = random.choice([p for p in popular_ids if p != pokemon_a_id])
        
        # Affichage compact
        print(f"[{i+1:3d}/{n_predictions}] ", end="", flush=True)
        
        result = generate_prediction(pokemon_a_id, pokemon_b_id)
        
        if result:
            poke_a = result.get('pokemon_a_name', 'N/A')
            poke_b = result.get('pokemon_b_name', 'N/A')
            move = result.get('recommended_move', 'N/A')
            win_prob = result.get('win_probability', 0) * 100
            
            print(f"{poke_a:12s} vs {poke_b:12s} → {move:15s} ({win_prob:5.1f}%) ✅")
            success_count += 1
        else:
            print(f"Pokémon {pokemon_a_id} vs {pokemon_b_id} ❌")
            error_count += 1
        
        time.sleep(delay)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*70}")
    print(f"📊 Résultats du Test")
    print(f"{'='*70}")
    print(f"✅ Succès:      {success_count:3d}/{n_predictions} ({success_count/n_predictions*100:5.1f}%)")
    print(f"❌ Erreurs:     {error_count:3d}/{n_predictions}")
    print(f"⏱️  Durée:       {elapsed:.1f}s")
    print(f"📈 Débit:       {n_predictions/elapsed:.2f} pred/s")
    print(f"💾 Cache:       {len(pokemon_cache)} Pokémon chargés")
    
    if success_count > 0:
        print(f"\n{'='*70}")
        print(f"✅ Les métriques sont maintenant disponibles dans:")
        print(f"{'='*70}")
        print(f"📊 Grafana Dashboard API Performance:")
        print(f"   → http://localhost:3000/d/api-performance")
        print(f"\n📊 Grafana Dashboard Model Performance:")
        print(f"   → http://localhost:3000/d/model-performance")
        print(f"\n📈 Prometheus Queries:")
        print(f"   → http://localhost:9090/graph")
        print(f"\n💡 Requêtes Prometheus utiles:")
        print(f"   • rate(api_requests_total[1m])")
        print(f"   • rate(model_predictions_total[1m])")
        print(f"   • histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))")


def main():
    """Point d'entrée principal."""
    print(f"\n{'='*70}")
    print(f"🎯 Test de Monitoring - PredictionDex (Version Intelligente)")
    print(f"{'='*70}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test santé
    print("1️⃣  Vérification de l'API...")
    if not test_health():
        print("\n❌ L'API n'est pas accessible.")
        print("💡 Lancez: docker compose up db api -d")
        return
    
    print()
    
    # Menu
    print("2️⃣  Choix du test\n")
    print("  [1] Quick Test     - 10 prédictions (10s)")
    print("  [2] Medium Test    - 50 prédictions (30s)")
    print("  [3] Full Test      - 100 prédictions (1min)")
    print("  [4] Stress Test    - 200 prédictions (2min)")
    print("  [5] Custom")
    
    choice = input("\n👉 Votre choix [1-5]: ").strip()
    
    configs = {
        "1": (10, 1.0),
        "2": (50, 0.5),
        "3": (100, 0.5),
        "4": (200, 0.5)
    }
    
    if choice in configs:
        n_predictions, delay = configs[choice]
    elif choice == "5":
        try:
            n_predictions = int(input("Nombre de prédictions: "))
            delay = float(input("Délai entre prédictions (s): "))
        except ValueError:
            print("❌ Valeurs invalides, mode Medium utilisé")
            n_predictions, delay = 50, 0.5
    else:
        print("❌ Choix invalide, mode Medium utilisé")
        n_predictions, delay = 50, 0.5
    
    # Exécution
    run_test_batch(n_predictions, delay)
    
    print(f"\n{'='*70}")
    print(f"✅ Test terminé avec succès!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
