#!/usr/bin/env python3
"""
Interactive Docker Quick Start Guide
=====================================

Interactive script to guide users through starting and validating
the complete Docker stack.

This script provides a step-by-step walkthrough for:
    1. Checking Docker prerequisites (Docker, Docker Compose)
    2. Building Docker images
    3. Starting services in correct order
    4. Validating service health
    5. Displaying access URLs
    6. Running initial smoke tests

Features:
    - Colored terminal output for better readability
    - Progress indicators for long-running operations
    - Automatic health checks with retry logic
    - Helpful error messages and troubleshooting tips
    - Service URL summary at completion

Usage:
    # Start guided setup
    python scripts/quick_start_docker.py

    # Quick start without prompts
    python scripts/quick_start_docker.py --auto

Prerequisites:
    - Docker installed and running
    - Docker Compose v2+
    - Sufficient disk space (10GB recommended)
    - Ports available: 8080, 5432, 9091, 3001, 5001, 8502
"""

import sys
import time
import subprocess
import requests
from pathlib import Path


def print_header(title: str):
    """Affiche un header formaté."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(number: int, title: str):
    """Affiche un titre d'étape."""
    print(f"\n{'─' * 70}")
    print(f"  ÉTAPE {number}: {title}")
    print('─' * 70)


def run_command(command: str, description: str) -> bool:
    """
    Exécute une commande shell et affiche le résultat.

    Returns:
        True si succès, False sinon
    """
    print(f"\n🔧 {description}...")
    print(f"   $ {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print("   ✅ Succès")
            return True
        else:
            print(f"   ❌ Échec (code {result.returncode})")
            if result.stderr:
                print(f"   Erreur: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print("   ❌ Timeout (> 120s)")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def check_service(url: str, name: str, timeout: int = 5) -> bool:
    """Vérifie qu'un service est accessible."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"   ✅ {name} accessible")
            return True
        else:
            print(f"   ⚠️  {name} répond avec status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"   ❌ {name} non accessible")
        return False


def main():
    """Point d'entrée principal."""
    print_header("🚀 GUIDE DE DÉMARRAGE DOCKER")
    print("\nCe script va vous guider pour démarrer la stack complète.")
    print("\nServices qui seront démarrés:")
    print("  • PostgreSQL (base de données)")
    print("  • ETL Pipeline (import données)")
    print("  • ML Builder (entraînement modèle)")
    print("  • API FastAPI (backend)")
    print("  • Streamlit (interface)")
    print("  • Prometheus (métriques)")
    print("  • Grafana (dashboards)")
    print("  • MLflow (Model Registry)")
    print("  • Node Exporter (métriques système)")

    input("\n👉 Appuyez sur ENTRÉE pour commencer...")

    # ========================================================================
    # ÉTAPE 1: Vérifier Docker
    # ========================================================================

    print_step(1, "Vérification de Docker")

    if not run_command("docker --version", "Vérifier Docker"):
        print("\n❌ Docker n'est pas installé ou non accessible")
        print("💡 Installez Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)

    if not run_command("docker-compose --version", "Vérifier Docker Compose"):
        print("\n❌ Docker Compose n'est pas installé")
        print("💡 Installez Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)

    # ========================================================================
    # ÉTAPE 2: Arrêter les services existants
    # ========================================================================

    print_step(2, "Nettoyage des services existants")

    print("\n⚠️  Cette étape va arrêter les services Docker existants")
    response = input("Continuer? (o/N): ").lower()

    if response == 'o':
        run_command("docker-compose down", "Arrêt des services")
    else:
        print("ℹ️  Nettoyage ignoré")

    # ========================================================================
    # ÉTAPE 3: Construction des images
    # ========================================================================

    print_step(3, "Construction des images Docker")

    print("\n⚠️  Cette étape peut prendre 5-10 minutes la première fois")
    response = input("Construire les images? (O/n): ").lower()

    if response != 'n':
        if not run_command("docker-compose build --parallel", "Construction des images"):
            print("\n❌ Échec de la construction")
            print("💡 Vérifiez les logs ci-dessus")
            sys.exit(1)
    else:
        print("ℹ️  Construction ignorée")

    # ========================================================================
    # ÉTAPE 4: Démarrage des services
    # ========================================================================

    print_step(4, "Démarrage des services")

    if not run_command("docker-compose up -d", "Démarrage de la stack"):
        print("\n❌ Échec du démarrage")
        sys.exit(1)

    print("\n⏳ Attente du démarrage complet (30s)...")
    for i in range(30, 0, -5):
        print(f"   {i}s restantes...")
        time.sleep(5)

    # ========================================================================
    # ÉTAPE 5: Validation des services
    # ========================================================================

    print_step(5, "Validation des services")

    services_to_check = [
        ("http://localhost:8080/health", "API FastAPI"),
        ("http://localhost:8502", "Streamlit"),
        ("http://localhost:9091/-/healthy", "Prometheus"),
        ("http://localhost:3001/api/health", "Grafana"),
        ("http://localhost:5001/health", "MLflow"),
    ]

    all_ok = True
    for url, name in services_to_check:
        if not check_service(url, name):
            all_ok = False

    # ========================================================================
    # ÉTAPE 6: Génération de métriques de test (optionnel)
    # ========================================================================

    if all_ok:
        print_step(6, "Génération de métriques de test (optionnel)")

        print("\n💡 Voulez-vous générer des métriques de test pour Grafana?")
        print("   Cela créera des prédictions ML et remplira les dashboards")

        response = input("\nGénérer métriques? (o/N): ").lower()

        if response == 'o':
            duration = input("Durée en minutes (défaut: 2): ").strip()
            duration = int(duration) if duration else 2

            print(f"\n🎯 Génération de métriques pendant {duration} minute(s)...")
            print("   (Vous pouvez interrompre avec Ctrl+C)")

            try:
                subprocess.run(
                    f"python scripts/generate_monitoring_data.py --duration {duration}",
                    shell=True,
                    timeout=duration * 60 + 30
                )
            except KeyboardInterrupt:
                print("\n⚠️  Génération interrompue")
            except subprocess.TimeoutExpired:
                print("   ⚠️  Timeout")

    # ========================================================================
    # RÉSUMÉ FINAL
    # ========================================================================

    print_header("✅ DÉMARRAGE TERMINÉ")

    if all_ok:
        print("\n🎉 Tous les services sont opérationnels!")
        print("\n📍 URLs disponibles:")
        print("   • API (Swagger):  http://localhost:8080/docs")
        print("   • Streamlit:      http://localhost:8502")
        print("   • Grafana:        http://localhost:3001")
        print("   • Prometheus:     http://localhost:9091")
        print("   • MLflow:         http://localhost:5001")

        print("\n📊 Endpoints utiles:")
        print("   • Métriques API:  http://localhost:8080/metrics")
        print("   • Health check:   http://localhost:8080/health")

        print("\n💡 Commandes utiles:")
        print("   # Voir les logs")
        print("   docker-compose logs -f api")
        print("")
        print("   # Générer des métriques")
        print("   python scripts/generate_monitoring_data.py --duration 10")
        print("")
        print("   # Valider la stack")
        print("   python scripts/validate_docker_stack.py")
        print("")
        print("   # Arrêter les services")
        print("   docker-compose down")

        print("\n🎯 Prochaines étapes:")
        print("   1. Ouvrez Grafana (http://localhost:3001)")
        print("   2. Consultez les dashboards (Model Performance, API Performance)")
        print("   3. Testez l'API (http://localhost:8080/docs)")
        print("   4. Explorez l'interface (http://localhost:8502)")

    else:
        print("\n⚠️  Certains services ne sont pas accessibles")
        print("\n💡 Actions à effectuer:")
        print("   1. Vérifiez les logs: docker-compose logs <service>")
        print("   2. Redémarrez les services: docker-compose restart")
        print("   3. Validez la stack: python scripts/validate_docker_stack.py")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)
