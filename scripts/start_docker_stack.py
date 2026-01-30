#!/usr/bin/env python3
"""
Script de démarrage rapide pour Docker + monitoring
===================================================

Remplace start_docker_stack.sh en Python pur.

Usage:
    python scripts/start_docker_stack.py
"""

import sys
import subprocess
import time
from pathlib import Path


def print_header(text: str):
    """Affiche un header formaté."""
    print("=" * 50)
    print(text)
    print("=" * 50)
    print()


def check_command(command: str) -> bool:
    """Vérifie si une commande existe."""
    try:
        subprocess.run(
            ["which", command],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run_command(command: str, description: str = None) -> bool:
    """Exécute une commande shell."""
    if description:
        print(f"🔧 {description}...")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            if description:
                print(f"✅ {description} - OK\n")
            return True
        else:
            print(f"❌ Erreur: {result.stderr[:200]}\n")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout\n")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}\n")
        return False


def create_env_file():
    """Crée le fichier .env s'il n'existe pas."""
    env_path = Path(".env")

    if env_path.exists():
        print("✅ Fichier .env existant\n")
        return True

    print("📝 Création du fichier .env...")

    env_content = """# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=letsgo_db
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password

# API
API_BASE_URL=http://api:8080
DEV_MODE=true

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5001
MLFLOW_BACKEND_STORE_URI=postgresql://letsgo_user:letsgo_password@db:5432/letsgo_db

# Monitoring
PROMETHEUS_URL=http://prometheus:9091
GRAFANA_URL=http://grafana:3000
"""

    try:
        env_path.write_text(env_content)
        print("✅ Fichier .env créé\n")
        return True
    except Exception as e:
        print(f"❌ Erreur création .env: {e}\n")
        return False


def check_docker_status():
    """Vérifie le statut des services Docker."""
    try:
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')

            # Compter services UP
            services_up = sum(1 for line in lines if 'Up' in line)

            if services_up > 0:
                print(f"   ✅ {services_up} service(s) en cours d'exécution")
                return services_up

        return 0

    except Exception:
        return 0


def main():
    """Point d'entrée principal."""
    print_header("🚀 Démarrage PredictionDex - Full Stack")

    # 1. Vérifier Docker
    if not check_command("docker"):
        print("❌ Docker n'est pas installé")
        print("💡 Installez Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)

    if not check_command("docker-compose"):
        print("❌ Docker Compose n'est pas installé")
        print("💡 Installez Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)

    print("✅ Docker et Docker Compose détectés\n")

    # 2. Créer fichier .env
    if not create_env_file():
        sys.exit(1)

    # 3. Construction des images
    print("📦 Construction des images Docker...")
    if not run_command("docker-compose build --parallel", "Construction des images"):
        print("⚠️  Échec de la construction, mais on continue...\n")

    # 4. Démarrage des services
    print("🚀 Démarrage des services...")
    if not run_command("docker-compose up -d", "Démarrage de la stack"):
        print("❌ Échec du démarrage")
        sys.exit(1)

    # 5. Attente du démarrage
    print("⏳ Attente du démarrage complet (30s)...")
    for i in range(6, 0, -1):
        print(f"   {i*5}s restantes...")
        time.sleep(5)
    print()

    # 6. Vérifier les services
    print("🔍 Vérification des services...")

    services = [
        ("db", 5432, "PostgreSQL"),
        ("api", 8000, "API FastAPI"),
        ("streamlit", 8501, "Interface Streamlit"),
        ("prometheus", 9090, "Prometheus"),
        ("grafana", 3000, "Grafana"),
        ("mlflow", 5001, "MLflow"),
    ]

    all_ok = True
    for service, port, name in services:
        # Vérifier via docker-compose ps
        result = subprocess.run(
            f"docker-compose ps {service} 2>/dev/null | grep -q Up",
            shell=True,
            capture_output=True
        )

        if result.returncode == 0:
            print(f"   ✅ {name} ({port})")
        else:
            print(f"   ❌ {name} ({port}) - Non démarré")
            all_ok = False

    print()

    # 7. Résumé final
    print_header("✅ Tous les services sont opérationnels!" if all_ok else "⚠️  Certains services ne sont pas démarrés")

    if all_ok:
        print("🌐 URLs disponibles:")
        print("   API (Swagger):    http://localhost:8080/docs")
        print("   Streamlit:        http://localhost:8502")
        print("   Grafana:          http://localhost:3001")
        print("   Prometheus:       http://localhost:9091")
        print("   MLflow:           http://localhost:5001")
        print()
        print("📊 Métriques API:    http://localhost:8080/metrics")
        print("🔥 Health API:       http://localhost:8080/health")
        print()
        print("💡 Commandes utiles:")
        print("   # Voir les logs")
        print("   docker-compose logs -f api")
        print()
        print("   # Générer des métriques de test")
        print("   python scripts/generate_monitoring_data.py --duration 10")
        print()
        print("   # Valider la stack")
        print("   python scripts/validate_docker_stack.py")
        print()
        print("   # Arrêter les services")
        print("   docker-compose down")
        print()
    else:
        print("💡 Actions à effectuer:")
        print("   1. Vérifiez les logs: docker-compose logs <service>")
        print("   2. Redémarrez: docker-compose restart")
        print("   3. Validez: python scripts/validate_docker_stack.py")
        print()

    print("=" * 50)

    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
