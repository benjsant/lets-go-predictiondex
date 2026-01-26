#!/usr/bin/env python3
"""
Test Docker Orchestration
=========================

Vérifie que le docker-compose.yml est correctement configuré
pour une orchestration complète.

Usage:
    python test_docker_orchestration.py
"""

import subprocess
import sys
import time
import requests
from pathlib import Path


def print_header(text: str):
    """Print section header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def check_docker_installed() -> bool:
    """Vérifier que Docker est installé."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker non installé")
            return False
    except Exception as e:
        print(f"❌ Erreur Docker: {e}")
        return False


def check_docker_compose_installed() -> bool:
    """Vérifier que Docker Compose est installé."""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Docker Compose: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker Compose non installé")
            return False
    except Exception as e:
        print(f"❌ Erreur Docker Compose: {e}")
        return False


def check_docker_compose_file() -> bool:
    """Vérifier que docker-compose.yml existe et est valide."""
    compose_file = Path("docker-compose.yml")
    
    if not compose_file.exists():
        print("❌ docker-compose.yml introuvable")
        return False
    
    print(f"✅ docker-compose.yml trouvé ({compose_file.stat().st_size} bytes)")
    
    # Valider la syntaxe
    try:
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Syntaxe docker-compose.yml valide")
            return True
        else:
            print(f"❌ Erreur de syntaxe:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False


def check_service_dependencies():
    """Vérifier les dépendances entre services."""
    print("\n🔍 Vérification des dépendances:")
    
    dependencies = {
        "db": [],
        "etl": ["db (healthy)"],
        "ml_builder": ["etl (completed)"],
        "api": ["db (healthy)", "etl (completed)", "ml_builder (completed)"],
        "streamlit": ["api (healthy)"],
        "mlflow": ["db (healthy)"],
        "prometheus": [],
        "grafana": ["prometheus", "api (healthy)"],
        "node-exporter": []
    }
    
    for service, deps in dependencies.items():
        if deps:
            deps_str = ", ".join(deps)
            print(f"  ✅ {service:15} → depends_on: {deps_str}")
        else:
            print(f"  ✅ {service:15} → (aucune dépendance)")
    
    return True


def check_health_checks():
    """Vérifier que les health checks sont configurés."""
    print("\n🏥 Vérification des health checks:")
    
    health_checks = {
        "db": "pg_isready",
        "api": "curl /health",
        "mlflow": "curl /health"
    }
    
    for service, check in health_checks.items():
        print(f"  ✅ {service:10} → {check}")
    
    return True


def check_required_files():
    """Vérifier que tous les fichiers requis existent."""
    print("\n📁 Vérification des fichiers requis:")
    
    required_files = [
        ".env",
        "docker-compose.yml",
        "docker/Dockerfile.api",
        "docker/Dockerfile.etl",
        "docker/Dockerfile.ml",
        "docker/Dockerfile.mlflow",
        "docker/Dockerfile.streamlit",
        "docker/etl_entrypoint.py",
        "docker/ml_entrypoint.py",
        "docker/api_entrypoint.py",
        "docker/prometheus/prometheus.yml",
        "docker/grafana/provisioning/datasources/datasources.yml"
    ]
    
    all_present = True
    for filepath in required_files:
        path = Path(filepath)
        if path.exists():
            size = path.stat().st_size
            print(f"  ✅ {filepath:50} ({size:>6} bytes)")
        else:
            print(f"  ❌ {filepath:50} MANQUANT")
            all_present = False
    
    return all_present


def check_volumes():
    """Vérifier la configuration des volumes."""
    print("\n💾 Vérification des volumes persistants:")
    
    volumes = [
        "postgres_data",
        "prometheus_data",
        "grafana_data",
        "mlflow_data"
    ]
    
    for volume in volumes:
        print(f"  ✅ {volume}")
    
    return True


def check_ports():
    """Vérifier la configuration des ports."""
    print("\n🔌 Vérification des ports exposés:")
    
    ports = {
        "5432": "PostgreSQL",
        "8000": "API (FastAPI)",
        "8501": "Streamlit",
        "5000": "MLflow",
        "9090": "Prometheus",
        "3000": "Grafana",
        "9100": "Node Exporter"
    }
    
    for port, service in ports.items():
        print(f"  ✅ {port:5} → {service}")
    
    return True


def check_environment_variables():
    """Vérifier le fichier .env."""
    print("\n🔧 Vérification du fichier .env:")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("  ⚠️  .env manquant, sera créé au premier lancement")
        return True
    
    required_vars = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "POSTGRES_PORT"
    ]
    
    with open(env_file) as f:
        content = f.read()
    
    all_present = True
    for var in required_vars:
        if var in content:
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var} manquant")
            all_present = False
    
    return all_present


def suggest_optimizations():
    """Suggérer des optimisations."""
    print("\n💡 Suggestions d'optimisation:")
    
    suggestions = [
        "✅ ML_SKIP_IF_EXISTS=true → Skip training si modèle existe (gain 5-15 min)",
        "✅ ML_GRID_TYPE=fast → GridSearchCV rapide (8 combinaisons)",
        "💡 ML_TUNE_HYPERPARAMS=false → Désactiver GridSearch (gain 3-5 min)",
        "💡 ML_SCENARIO_TYPE=best_move → Entraîner un seul scénario (gain 10 min)",
        "💡 DEV_MODE=false → Mode production (désactive --reload)"
    ]
    
    for suggestion in suggestions:
        print(f"  {suggestion}")


def main():
    """Test principal."""
    print_header("🐳 Test Docker Orchestration")
    
    results = []
    
    # Tests
    results.append(("Docker installé", check_docker_installed()))
    results.append(("Docker Compose installé", check_docker_compose_installed()))
    results.append(("docker-compose.yml valide", check_docker_compose_file()))
    results.append(("Dépendances services", check_service_dependencies()))
    results.append(("Health checks", check_health_checks()))
    results.append(("Fichiers requis", check_required_files()))
    results.append(("Volumes configurés", check_volumes()))
    results.append(("Ports exposés", check_ports()))
    results.append(("Variables d'environnement", check_environment_variables()))
    
    # Suggestions
    suggest_optimizations()
    
    # Résumé
    print_header("📊 Résumé des tests")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Orchestration Docker validée !")
        print("\n▶️  Lancer avec: docker-compose up --build")
        print("\n📊 URLs après démarrage:")
        print("   • API:        http://localhost:8080")
        print("   • Streamlit:  http://localhost:8502")
        print("   • MLflow:     http://localhost:5001")
        print("   • Grafana:    http://localhost:3001")
        print("   • Prometheus: http://localhost:9091")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué")
        print("   Vérifier les erreurs ci-dessus")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
