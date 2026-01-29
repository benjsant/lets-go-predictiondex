#!/usr/bin/env python3
"""
Script pour peupler MLflow et Grafana avec des données de test.

Usage:
    python3 scripts/populate_monitoring.py
"""

import os
import random
import sys
import time
from pathlib import Path

import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8080")
API_KEY = "BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ"
MLFLOW_URL = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_services():
    """Vérifie que l'API et MLflow sont accessibles."""
    print("🔍 Vérification des services...")

    # API
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API accessible : {API_URL}")
        else:
            print(f"❌ API non accessible : {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API non accessible : {e}")
        return False

    # MLflow
    try:
        response = requests.get(f"{MLFLOW_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ MLflow accessible : {MLFLOW_URL}")
        else:
            print(f"❌ MLflow non accessible : {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MLflow non accessible : {e}")
        return False

    return True

def get_pokemon_moves(pokemon_id, headers):
    """Récupère les moves d'un Pokémon depuis l'API."""
    try:
        response = requests.get(
            f"{API_URL}/pokemons/{pokemon_id}",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            moves = [move["move_name"] for move in data.get("moves", [])]
            return moves[:4] if len(moves) >= 4 else moves
        return []
    except Exception:
        return []

def generate_predictions(n=50):
    """Génère des prédictions pour peupler Prometheus/Grafana."""
    print_header("GÉNÉRATION DE PRÉDICTIONS")
    print(f"📊 Génération de {n} prédictions...")

    # Pokémon populaires pour les tests
    popular_ids = [1, 4, 7, 25, 6, 9, 3, 35, 36, 39, 40, 94, 65, 59, 68, 130, 131, 144, 145, 146, 150, 151]

    success = 0
    errors = 0

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    start_time = time.time()

    for i in range(n):
        pokemon_a_id = random.choice(popular_ids)
        pokemon_b_id = random.choice([p for p in popular_ids if p != pokemon_a_id])

        # Récupérer les moves du Pokémon A
        moves = get_pokemon_moves(pokemon_a_id, headers)

        if not moves or len(moves) < 2:
            # Si pas assez de moves, utiliser des moves par défaut
            moves = ["Charge", "Griffe", "Flammèche", "Pistolet à O"][:4]

        payload = {
            "pokemon_a_id": pokemon_a_id,
            "pokemon_b_id": pokemon_b_id,
            "available_moves": moves
        }

        try:
            response = requests.post(
                f"{API_URL}/predict/best-move",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                success += 1
                if (i + 1) % 10 == 0:
                    print(f"   {i+1}/{n} prédictions effectuées...")
            else:
                errors += 1
                if errors <= 3:  # Afficher seulement les 3 premières erreurs
                    print(f"⚠️  Erreur {response.status_code} : {response.text[:100]}")
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"⚠️  Exception : {str(e)[:100]}")

    duration = time.time() - start_time

    print(f"\n✅ Prédictions générées : {success}/{n} succès")
    print(f"   Durée : {duration:.1f}s")
    print(f"   Throughput : {n/duration:.1f} req/s")

    if errors > 0:
        print(f"⚠️  {errors} erreurs (vérifiez que l'API Key est valide)")

    return success

def create_mlflow_experiment():
    """Crée une expérience MLflow de test avec des runs."""
    print_header("CRÉATION D'EXPÉRIENCE MLFLOW")

    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(MLFLOW_URL)
        client = MlflowClient(tracking_uri=MLFLOW_URL)

        # Créer une expérience de démo
        experiment_name = "demo_monitoring"

        try:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"✅ Expérience créée : {experiment_name} (ID: {experiment_id})")
        except Exception:
            # L'expérience existe déjà
            experiment = mlflow.get_experiment_by_name(experiment_name)
            experiment_id = experiment.experiment_id
            print(f"ℹ️  Expérience existe déjà : {experiment_name} (ID: {experiment_id})")

        # Créer quelques runs de test
        print(f"📝 Création de 3 runs de test...")

        for i in range(3):
            with mlflow.start_run(experiment_id=experiment_id, run_name=f"demo_run_{i+1}"):
                # Log des métriques de test
                accuracy = 0.90 + random.random() * 0.08  # 90-98%
                precision = 0.88 + random.random() * 0.10  # 88-98%
                recall = 0.87 + random.random() * 0.11     # 87-98%

                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                mlflow.log_metric("f1_score", 2 * (precision * recall) / (precision + recall))

                # Log des paramètres
                mlflow.log_param("model_type", "XGBoost")
                mlflow.log_param("n_estimators", random.choice([100, 200, 300]))
                mlflow.log_param("max_depth", random.choice([5, 7, 10]))
                mlflow.log_param("learning_rate", random.choice([0.01, 0.05, 0.1]))

                print(f"   ✅ Run {i+1}/3 créé (accuracy: {accuracy:.4f})")

        print(f"\n✅ Expérience MLflow peuplée avec succès")
        print(f"   Ouvrez MLflow : {MLFLOW_URL}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de la création de l'expérience MLflow : {e}")
        print(f"   Vérifiez que mlflow est installé : pip install mlflow")
        return False

def verify_grafana_datasource():
    """Vérifie que Grafana a Prometheus comme datasource."""
    print_header("VÉRIFICATION GRAFANA")

    grafana_url = "http://localhost:3001"

    try:
        # Vérifier que Grafana répond
        response = requests.get(f"{grafana_url}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Grafana accessible : {grafana_url}")
        else:
            print(f"⚠️  Grafana répond avec status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Grafana non accessible : {e}")
        return False

    print(f"\n📊 Dashboard Grafana :")
    print(f"   URL : {grafana_url}")
    print(f"   Login : admin / admin")
    print(f"   Après connexion, allez dans Dashboards")

    return True

def check_prometheus_metrics():
    """Vérifie que Prometheus a des métriques."""
    print_header("VÉRIFICATION PROMETHEUS")

    prom_url = "http://localhost:9091"

    try:
        # Vérifier les métriques pokemon
        response = requests.get(
            f"{prom_url}/api/v1/query",
            params={"query": "pokemon_predictions_total"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("result"):
                value = data["data"]["result"][0]["value"][1]
                print(f"✅ Métriques Prometheus présentes")
                print(f"   pokemon_predictions_total : {value}")
            else:
                print(f"⚠️  Aucune métrique pokemon_predictions_total trouvée")
                print(f"   Les métriques apparaîtront après des prédictions")
        else:
            print(f"⚠️  Prometheus répond avec status {response.status_code}")

    except Exception as e:
        print(f"❌ Prometheus non accessible : {e}")
        return False

    return True

def main():
    """Point d'entrée principal."""
    print_header("🚀 POPULATION MLflow & Grafana")

    # 1. Vérifier les services
    if not check_services():
        print("\n❌ Les services ne sont pas tous accessibles.")
        print("   Démarrez-les avec : docker compose up -d")
        sys.exit(1)

    # 2. Générer des prédictions (peuple Prometheus/Grafana)
    success = generate_predictions(n=50)

    if success < 10:
        print("\n⚠️  Peu de prédictions réussies. Vérifiez l'API Key et les données.")

    # 3. Créer une expérience MLflow
    mlflow_ok = create_mlflow_experiment()

    # 4. Vérifier Grafana
    verify_grafana_datasource()

    # 5. Vérifier Prometheus
    check_prometheus_metrics()

    # Résumé final
    print_header("✅ TERMINÉ")

    print("📊 Prochaines étapes :\n")
    print("1. MLflow UI :")
    print(f"   {MLFLOW_URL}")
    print("   → Vous devriez voir l'expérience 'demo_monitoring' avec 3 runs\n")

    print("2. Grafana :")
    print("   http://localhost:3001")
    print("   → Login: admin / admin")
    print("   → Allez dans Dashboards → Pokémon Predictions")
    print("   → Les graphiques devraient afficher des données\n")

    print("3. Prometheus :")
    print("   http://localhost:9091")
    print("   → Query: pokemon_predictions_total")
    print("   → Vous devriez voir ~50 prédictions\n")

    if mlflow_ok and success >= 40:
        print("🎉 MLflow et Grafana sont maintenant peuplés avec des données de test !")
    else:
        print("⚠️  Quelques problèmes rencontrés, mais les services sont accessibles.")

if __name__ == "__main__":
    main()
