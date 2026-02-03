#!/usr/bin/env python3
"""
Script de vérification de l'état de MLflow
Usage: python3 scripts/mlflow/check_mlflow_status.py
"""
import requests
import sys
from datetime import datetime

# Couleurs ANSI
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
RESET = '\033[0m'

def print_header(text):
    """Affiche un en-tête formaté"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Affiche un message de succès"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Affiche un message d'erreur"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Affiche un avertissement"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    """Affiche une information"""
    print(f"{CYAN}ℹ️  {text}{RESET}")

def check_mlflow_server():
    """Vérifie que le serveur MLflow est accessible"""
    print_header("1. VÉRIFICATION SERVEUR MLFLOW")

    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print_success("MLflow Server est UP sur http://localhost:5001")
            print_info("Accéder à l'UI: http://localhost:5001")
            return True
        else:
            print_error(f"MLflow Server répond avec le code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("MLflow Server n'est pas accessible")
        print_warning("Lancer avec: docker compose up -d mlflow")
        return False
    except Exception as e:
        print_error(f"Erreur lors de la connexion: {e}")
        return False

def check_experiments():
    """Liste les expérimentations MLflow"""
    print_header("2. EXPÉRIMENTATIONS MLFLOW")

    try:
        response = requests.get(
            "http://localhost:5001/api/2.0/mlflow/experiments/search?max_results=50",
            timeout=5
        )

        if response.status_code != 200:
            print_error("Impossible de récupérer les expérimentations")
            return False

        data = response.json()
        experiments = data.get("experiments", [])

        if not experiments:
            print_warning("Aucune expérimentation trouvée")
            return False

        print_success(f"{len(experiments)} expérimentation(s) trouvée(s):")
        for exp in experiments:
            exp_id = exp.get("experiment_id")
            exp_name = exp.get("name")
            created = exp.get("creation_time")
            created_date = datetime.fromtimestamp(created / 1000).strftime("%Y-%m-%d %H:%M:%S") if created else "N/A"
            print(f"   • ID {exp_id}: {exp_name} (créé le {created_date})")

        return True

    except Exception as e:
        print_error(f"Erreur lors de la récupération des expérimentations: {e}")
        return False

def check_runs():
    """Vérifie les runs d'entraînement"""
    print_header("3. RUNS D'ENTRAÎNEMENT")

    try:
        response = requests.post(
            "http://localhost:5001/api/2.0/mlflow/runs/search",
            json={"max_results": 10},
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code != 200:
            print_error("Impossible de récupérer les runs")
            return False

        data = response.json()
        runs = data.get("runs", [])

        if not runs:
            print_warning("Aucun run d'entraînement trouvé")
            print_info("Les expérimentations existent mais sans runs enregistrés")
            return False

        print_success(f"{len(runs)} run(s) d'entraînement trouvé(s):")

        for i, run in enumerate(runs[:5], 1):  # Afficher max 5 runs
            info = run.get("info", {})
            data_run = run.get("data", {})

            run_id = info.get("run_id", "N/A")[:8]
            run_name = info.get("run_name", "Unnamed")
            status = info.get("status", "UNKNOWN")
            exp_id = info.get("experiment_id")

            # Récupérer les métriques
            metrics = data_run.get("metrics", [])
            metrics_dict = {m["key"]: m["value"] for m in metrics}

            print(f"\n   {i}. Run: {run_name} (ID: {run_id}...)")
            print(f"      Status: {status}")
            print(f"      Experiment ID: {exp_id}")

            if metrics_dict:
                print(f"      Métriques:")
                for key, value in sorted(metrics_dict.items()):
                    if isinstance(value, float):
                        print(f"         - {key}: {value:.4f}")
                    else:
                        print(f"         - {key}: {value}")

        return True

    except Exception as e:
        print_error(f"Erreur lors de la récupération des runs: {e}")
        return False

def check_registered_models():
    """Vérifie les modèles enregistrés dans le Model Registry"""
    print_header("4. MODEL REGISTRY")

    try:
        response = requests.get(
            "http://localhost:5001/api/2.0/mlflow/registered-models/search?max_results=50",
            timeout=5
        )

        if response.status_code != 200:
            print_error("Impossible de récupérer les modèles enregistrés")
            return False

        data = response.json()
        models = data.get("registered_models", [])

        if not models:
            print_warning("Aucun modèle enregistré dans le Model Registry")
            print_info("Pour enregistrer le modèle existant:")
            print_info("   python3 scripts/mlflow/register_existing_model.py")
            return False

        print_success(f"{len(models)} modèle(s) enregistré(s):")
        for model in models:
            model_name = model.get("name")
            creation_time = model.get("creation_timestamp")
            created_date = datetime.fromtimestamp(creation_time / 1000).strftime("%Y-%m-%d %H:%M:%S") if creation_time else "N/A"
            latest_versions = model.get("latest_versions", [])

            print(f"   • {model_name} (créé le {created_date})")

            if latest_versions:
                for version in latest_versions:
                    version_num = version.get("version")
                    stage = version.get("current_stage", "None")
                    print(f"      - Version {version_num} ({stage})")

        return True

    except Exception as e:
        print_error(f"Erreur lors de la récupération des modèles: {e}")
        return False

def check_local_models():
    """Vérifie les modèles locaux (fichiers .pkl)"""
    print_header("5. MODÈLES LOCAUX (FICHIERS)")

    from pathlib import Path
    import os

    models_dir = Path("models")

    if not models_dir.exists():
        print_error("Répertoire 'models/' introuvable")
        return False

    pkl_files = list(models_dir.glob("*.pkl"))
    json_files = list(models_dir.glob("*metadata*.json"))

    if not pkl_files:
        print_warning("Aucun fichier .pkl trouvé dans models/")
        return False

    print_success(f"{len(pkl_files)} modèle(s) trouvé(s):")
    for pkl_file in pkl_files:
        size = os.path.getsize(pkl_file) / (1024 * 1024)  # MB
        print(f"   • {pkl_file.name} ({size:.2f} MB)")

    if json_files:
        print_success(f"{len(json_files)} fichier(s) metadata trouvé(s):")
        for json_file in json_files:
            print(f"   • {json_file.name}")

    return True

def print_summary(checks):
    """Affiche un résumé des vérifications"""
    print_header("RÉSUMÉ")

    total = len(checks)
    passed = sum(checks.values())

    print(f"Vérifications: {passed}/{total} réussies\n")

    for check_name, check_result in checks.items():
        status = f"{GREEN}✅ PASS{RESET}" if check_result else f"{RED}❌ FAIL{RESET}"
        print(f"   {status}  {check_name}")

    print()

    if passed == total:
        print_success("🎉 MLflow est complètement opérationnel!")
        print_info("Accéder à l'UI: http://localhost:5001")
    elif checks.get("Serveur MLflow", False):
        print_warning("MLflow fonctionne mais il manque des éléments")
        if not checks.get("Modèles enregistrés", False):
            print_info("\nPour enregistrer le modèle existant:")
            print(f"{CYAN}   python3 scripts/mlflow/register_existing_model.py{RESET}")
    else:
        print_error("MLflow n'est pas opérationnel")
        print_info("\nPour démarrer MLflow:")
        print(f"{CYAN}   docker compose up -d mlflow{RESET}")

    print()

def main():
    """Fonction principale"""
    print(f"{CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         VÉRIFICATION ÉTAT MLFLOW - PREDICTIONDEX          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(RESET)

    checks = {}

    # 1. Vérifier le serveur
    checks["Serveur MLflow"] = check_mlflow_server()

    if not checks["Serveur MLflow"]:
        print_summary(checks)
        sys.exit(1)

    # 2. Vérifier les expérimentations
    checks["Expérimentations"] = check_experiments()

    # 3. Vérifier les runs
    checks["Runs d'entraînement"] = check_runs()

    # 4. Vérifier le Model Registry
    checks["Modèles enregistrés"] = check_registered_models()

    # 5. Vérifier les modèles locaux
    checks["Modèles locaux"] = check_local_models()

    # Résumé
    print_summary(checks)

    # Code de sortie
    if all(checks.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
