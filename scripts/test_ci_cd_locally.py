#!/usr/bin/env python3
"""
Script pour tester le CI/CD localement avant de pousser sur GitHub
Usage: python3 scripts/test_ci_cd_locally.py
"""
import os
import sys
import time
import json
import shutil
import subprocess
import requests
from pathlib import Path

# Couleurs ANSI
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
RESET = '\033[0m'

def print_step(step_num, title):
    """Affiche un en-tête d'étape"""
    print(f"\n📋 Step {step_num}: {title}...")

def check_command(command):
    """Vérifie qu'une commande existe"""
    return shutil.which(command) is not None

def check_prerequisites():
    """Vérifie les prérequis"""
    print_step(1, "Checking prerequisites")

    if not check_command("docker"):
        print(f"{RED}❌ Docker is not installed{RESET}")
        return False

    if not (check_command("docker-compose") or check_command("docker")):
        print(f"{RED}❌ Docker Compose is not installed{RESET}")
        return False

    if not check_command("python3"):
        print(f"{RED}❌ Python 3 is not installed{RESET}")
        return False

    print(f"{GREEN}✅ All prerequisites OK{RESET}")
    return True

def create_env_file():
    """Crée le fichier .env s'il n'existe pas"""
    print_step(2, "Creating .env file")

    env_file = Path(".env")

    if env_file.exists():
        print(f"{GREEN}✅ .env file already exists{RESET}")
        return True

    env_content = """POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password
POSTGRES_DB=letsgo_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEV_MODE=true
API_KEY_REQUIRED=true
API_KEYS=test_key_for_local_ci,BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ
DISABLE_MLFLOW_TRACKING=false
USE_MLFLOW_REGISTRY=false
ML_SKIP_IF_EXISTS=true
"""

    env_file.write_text(env_content)
    print(f"{GREEN}✅ .env file created{RESET}")
    return True

def start_services():
    """Démarre les services Docker"""
    print_step(3, "Starting Docker services")

    # Arrêter les services existants
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        capture_output=True
    )

    # Démarrer les services
    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        capture_output=True
    )

    if result.returncode != 0:
        print(f"{RED}❌ Failed to start services{RESET}")
        return False

    print(f"⏳ Waiting for services to start...")
    time.sleep(10)
    return True

def wait_for_postgres():
    """Attend que PostgreSQL soit prêt"""
    print_step(4, "Waiting for PostgreSQL")

    for _ in range(30):  # 60 secondes max
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "db", "pg_isready", "-U", "letsgo_user"],
            capture_output=True
        )

        if result.returncode == 0:
            print(f"{GREEN}✅ PostgreSQL ready{RESET}")
            return True

        time.sleep(2)

    print(f"{RED}❌ PostgreSQL timeout{RESET}")
    return False

def wait_for_service(step, name, url, timeout=120, critical=True):
    """Attend qu'un service soit disponible"""
    print_step(step, f"Waiting for {name}")

    for _ in range(timeout // 3):
        try:
            response = requests.get(url, timeout=3)
            if response.status_code in [200, 302]:
                print(f"{GREEN}✅ {name} ready{RESET}")
                return True
        except Exception:
            pass

        time.sleep(3)

    if critical:
        print(f"{RED}❌ {name} timeout{RESET}")
        return False
    else:
        print(f"{YELLOW}⚠️  {name} timeout (non-critical){RESET}")
        return True

def check_service_status(name, url, success_codes=[200]):
    """Vérifie le statut d'un service"""
    try:
        response = requests.get(url, timeout=5)
        status = response.status_code

        if status in success_codes:
            return status, True
        else:
            return status, False
    except Exception:
        return 0, False

def check_all_services():
    """Vérifie le statut de tous les services"""
    print_step(9, "Checking all services status")

    # Afficher l'état des conteneurs
    print("\nService Status:")
    subprocess.run(["docker", "compose", "ps"])

    print("\nHealth Checks:")

    services = {
        "API": ("http://localhost:8080/health", [200]),
        "Prometheus": ("http://localhost:9091/-/healthy", [200]),
        "Grafana": ("http://localhost:3001/api/health", [200]),
        "MLflow": ("http://localhost:5001/health", [200]),
        "pgAdmin": ("http://localhost:5050", [200, 302])
    }

    results = {}

    for name, (url, success_codes) in services.items():
        status, ok = check_service_status(name, url, success_codes)
        results[name] = (status, ok)

        status_text = f"{GREEN}✅ OK ({status}){RESET}" if ok else f"{YELLOW}⚠️  WARN ({status}){RESET}"
        if name == "API" and not ok:
            status_text = f"{RED}❌ FAIL ({status}){RESET}"

        print(f"  - {name:12} {status_text}")

    return results

def install_dependencies():
    """Installe les dépendances Python"""
    print_step(10, "Installing Python dependencies")

    try:
        import requests
        print(f"{GREEN}✅ Dependencies already installed{RESET}")
        return True
    except ImportError:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "requests"],
            capture_output=True
        )

        if result.returncode == 0:
            print(f"{GREEN}✅ Dependencies installed{RESET}")
            return True
        else:
            print(f"{RED}❌ Failed to install dependencies{RESET}")
            return False

def run_monitoring_validation():
    """Exécute la validation du monitoring"""
    print_step(11, "Running Monitoring Validation Script")
    print("=" * 50)

    # Le script a été déplacé
    validation_script = Path("tests/integration/test_monitoring_validation.py")

    if not validation_script.exists():
        print(f"{RED}❌ Validation script not found at {validation_script}{RESET}")
        return False, 0

    result = subprocess.run(
        [sys.executable, str(validation_script)],
        capture_output=False
    )

    if result.returncode == 0:
        print(f"\n{GREEN}✅ MONITORING VALIDATION PASSED!{RESET}")
        return True, 100
    else:
        print(f"\n{RED}❌ MONITORING VALIDATION FAILED!{RESET}")
        return False, 0

def check_reports():
    """Vérifie les rapports générés"""
    print_step(12, "Checking generated reports")

    score = 0

    json_report = Path("reports/monitoring/validation_report.json")
    if json_report.exists():
        try:
            data = json.loads(json_report.read_text())
            score = data.get("validation_score", 0)
            print(f"{GREEN}✅ JSON report generated{RESET}")
            print(f"   Score: {GREEN}{score}/100{RESET}")
        except Exception:
            print(f"{RED}❌ Failed to read JSON report{RESET}")
    else:
        print(f"{RED}❌ JSON report not found{RESET}")

    html_report = Path("reports/monitoring/validation_report.html")
    if html_report.exists():
        print(f"{GREEN}✅ HTML report generated{RESET}")
        print(f"   Location: {html_report}")
    else:
        print(f"{RED}❌ HTML report not found{RESET}")

    return score

def print_summary(api_status, score):
    """Affiche le résumé des tests"""
    print_step(13, "Test Summary")
    print("=" * 24)

    success = api_status and score >= 60

    if success:
        print(f"\n{GREEN}🏆 SUCCESS! Your CI/CD pipeline will work on GitHub Actions{RESET}\n")
        print("Next steps:")
        print("  1. Commit your changes: git add . && git commit -m 'Add monitoring validation workflow'")
        print("  2. Push to GitHub: git push origin main")
        print("  3. Check GitHub Actions: https://github.com/your-repo/lets-go-predictiondex/actions")
        print("  4. Download the HTML report from artifacts")
        return 0
    else:
        print(f"\n{RED}❌ FAILED! Fix the issues before pushing to GitHub{RESET}\n")
        print("Issues found:")
        if not api_status:
            print("  - API is not responding correctly")
        if score < 60:
            print(f"  - Monitoring score is too low ({score} < 60)")
        return 1

def cleanup_prompt():
    """Demande si l'utilisateur veut arrêter les services"""
    print()
    try:
        response = input("Do you want to stop the services? (y/N): ")
        if response.lower() in ['y', 'yes']:
            print("🧹 Cleaning up...")
            subprocess.run(["docker", "compose", "down", "-v"])
            print(f"{GREEN}✅ Services stopped{RESET}")
        else:
            print("⚙️  Services are still running")
            print("   Stop them manually with: docker compose down -v")
    except KeyboardInterrupt:
        print("\n⚙️  Services are still running")
        print("   Stop them manually with: docker compose down -v")

def main():
    """Fonction principale"""
    print("🎯 Testing CI/CD Pipeline Locally")
    print("=" * 34)

    # Étape 1: Vérifier les prérequis
    if not check_prerequisites():
        return 1

    # Étape 2: Créer .env
    if not create_env_file():
        return 1

    # Étape 3: Démarrer les services
    if not start_services():
        return 1

    # Étape 4: Attendre PostgreSQL
    if not wait_for_postgres():
        return 1

    # Étapes 5-8: Attendre les services
    if not wait_for_service(5, "API", "http://localhost:8080/health", timeout=120, critical=True):
        return 1

    wait_for_service(6, "Prometheus", "http://localhost:9091/-/healthy", timeout=60, critical=False)
    wait_for_service(7, "Grafana", "http://localhost:3001/api/health", timeout=60, critical=False)
    wait_for_service(8, "MLflow", "http://localhost:5001/health", timeout=60, critical=False)

    # Étape 9: Vérifier tous les services
    service_results = check_all_services()
    api_status = service_results.get("API", (0, False))[1]

    # Étape 10: Installer les dépendances
    if not install_dependencies():
        return 1

    # Étape 11: Exécuter la validation monitoring
    validation_ok, _ = run_monitoring_validation()

    # Étape 12: Vérifier les rapports
    score = check_reports()

    # Étape 13: Résumé
    exit_code = print_summary(api_status, score)

    # Étape 14: Nettoyage (optionnel)
    cleanup_prompt()

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
