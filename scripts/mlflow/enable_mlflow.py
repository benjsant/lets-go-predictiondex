#!/usr/bin/env python3
"""
Script pour activer MLflow et enregistrer le modèle existant
Usage: python3 scripts/mlflow/enable_mlflow.py
"""
import os
import sys
import time
import subprocess
import requests
from pathlib import Path

# Couleurs ANSI
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RESET = '\033[0m'

def print_header(text):
    """Affiche un en-tête formaté"""
    print(f"\n{BLUE}{'='*40}{RESET}")
    print(f"{BLUE}{text:^40}{RESET}")
    print(f"{BLUE}{'='*40}{RESET}\n")

def print_success(text):
    """Affiche un message de succès"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Affiche un message d'erreur"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Affiche un avertissement"""
    print(f"{YELLOW}{text}{RESET}")

def print_info(text):
    """Affiche une information"""
    print(f"{BLUE}{text}{RESET}")

def check_mlflow_server():
    """Vérifie que le serveur MLflow est accessible"""
    print_info("Étape 1: Vérification MLflow Server")

    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print_success("MLflow Server est UP")
            return True
    except Exception:
        pass

    print_error("MLflow Server n'est pas accessible")
    print_warning("   Démarrage de MLflow...")

    # Démarrer MLflow
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "mlflow"],
            check=True,
            capture_output=True
        )
        print_warning("   Attente de 10 secondes...")
        time.sleep(10)

        # Revérifier
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print_success("MLflow Server démarré")
            return True
        else:
            print_error("MLflow Server toujours inaccessible")
            print_warning("   Vérifiez les logs: docker compose logs mlflow")
            return False

    except Exception as e:
        print_error(f"Erreur lors du démarrage de MLflow: {e}")
        return False

def configure_environment():
    """Configure les variables d'environnement"""
    print_info("\nÉtape 2: Configuration environnement")

    os.environ["DISABLE_MLFLOW_TRACKING"] = "false"
    os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5001"
    os.environ["ML_SKIP_IF_EXISTS"] = "false"

    print_success("Variables d'environnement configurées:")
    print("   - DISABLE_MLFLOW_TRACKING=false")
    print("   - MLFLOW_TRACKING_URI=http://localhost:5001")
    print("   - ML_SKIP_IF_EXISTS=false")

def register_model():
    """Enregistre le modèle existant dans MLflow"""
    print_info("\nÉtape 3: Enregistrement du modèle v2 dans MLflow\n")

    # Chemin du script d'enregistrement
    script_path = Path(__file__).parent / "register_existing_model.py"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=False
        )

        return result.returncode == 0

    except Exception as e:
        print_error(f"Erreur lors de l'exécution du script: {e}")
        return False

def print_success_message():
    """Affiche le message de succès final"""
    print(f"\n{GREEN}{'='*40}{RESET}")
    print(f"{GREEN}{'✅ SUCCÈS!':^40}{RESET}")
    print(f"{GREEN}{'='*40}{RESET}\n")

    print_success("Le modèle v2 (96.24% accuracy) a été enregistré dans MLflow\n")

    print_info("📊 Vérifier dans MLflow UI:")
    print("   http://localhost:5001\n")

    print_info("🔧 Pour que l'API utilise MLflow Registry:")
    print("   1. Modifier docker-compose.yml ligne 128:")
    print("      USE_MLFLOW_REGISTRY: \"true\"")
    print("   2. Redémarrer l'API:")
    print("      docker compose restart api\n")

    print_info("🚀 Pour entraîner un nouveau modèle avec MLflow:")
    print("   export DISABLE_MLFLOW_TRACKING=false")
    print("   export MLFLOW_TRACKING_URI=http://localhost:5001")
    print("   python machine_learning/train_model.py --version v3\n")

def print_failure_message():
    """Affiche le message d'échec"""
    print(f"\n{RED}{'='*40}{RESET}")
    print(f"{RED}{'❌ ÉCHEC':^40}{RESET}")
    print(f"{RED}{'='*40}{RESET}\n")

    print_error("L'enregistrement du modèle a échoué")
    print_warning("Vérifiez les logs ci-dessus pour plus de détails")

def main():
    """Fonction principale"""
    print_header("ACTIVATION MLFLOW & ENREGISTREMENT")

    # Étape 1: Vérifier MLflow
    if not check_mlflow_server():
        sys.exit(1)

    # Étape 2: Configurer l'environnement
    configure_environment()

    # Étape 3: Enregistrer le modèle
    if register_model():
        print_success_message()
        sys.exit(0)
    else:
        print_failure_message()
        sys.exit(1)

if __name__ == "__main__":
    main()
