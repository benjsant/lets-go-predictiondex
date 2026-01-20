#!/usr/bin/env python3
"""
Test rapide de tous les services PredictionDex
Usage: python test_all.py
"""

import subprocess
import requests
import json
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color


def print_header(text):
    """Print test header"""
    print(f"\n{text}")
    print("=" * len(text))
    print()


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{NC}")


def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{NC}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{NC}")


def run_docker_command(command):
    """Execute docker compose command"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    """Run all tests"""
    print_header("🧪 Test PredictionDex - Tous les Services")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Docker Compose
    print("1️⃣  Test: Docker Compose disponible")
    success, stdout, stderr = run_docker_command("docker compose version")
    if success:
        print_success("Docker Compose OK")
        tests_passed += 1
    else:
        print_error("Docker Compose non trouvé")
        tests_failed += 1
        return
    print()

    # Test 2: Services status
    print("2️⃣  Test: Statut des services")
    success, stdout, stderr = run_docker_command("docker compose ps --format json")
    if success:
        print(stdout)
        print()
    else:
        print_warning("Impossible de lister les services")
    print()

    # Test 3: PostgreSQL
    print("3️⃣  Test: PostgreSQL")
    success, stdout, stderr = run_docker_command(
        "docker compose exec -T db pg_isready -U letsgo_user -d letsgo_db"
    )
    if success:
        print_success("PostgreSQL OK")

        # Count Pokémon
        success_count, count_out, _ = run_docker_command(
            'docker compose exec -T db psql -U letsgo_user -d letsgo_db -t -c "SELECT COUNT(*) FROM pokemon;"'
        )
        if success_count:
            count = count_out.strip()
            print(f"   → Pokémon en base: {count}")
        tests_passed += 1
    else:
        print_error("PostgreSQL non disponible")
        tests_failed += 1
    print()

    # Test 4: API Health
    print("4️⃣  Test: API FastAPI")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print_success("API OK")
            health_data = response.json()
            print(f"   → Health: {health_data}")
            tests_passed += 1
        else:
            print_error(f"API retourne code {response.status_code}")
            tests_failed += 1
    except requests.exceptions.RequestException as e:
        print_error(f"API non disponible: {e}")
        tests_failed += 1
    print()

    # Test 5: API Pokémon endpoint
    print("5️⃣  Test: API Endpoint /pokemon/")
    try:
        response = requests.get("http://localhost:8000/pokemon/?limit=1", timeout=5)
        if response.status_code == 200:
            pokemon_data = response.json()
            if pokemon_data and len(pokemon_data) > 0:
                first_pokemon = pokemon_data[0]
                name_fr = first_pokemon.get("species", {}).get("name_fr", "?")
                print_success("Endpoint /pokemon/ OK")
                print(f"   → Premier Pokémon: {name_fr}")
                tests_passed += 1
            else:
                print_error("Endpoint /pokemon/ retourne des données vides")
                tests_failed += 1
        else:
            print_error(f"Endpoint /pokemon/ retourne code {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print_error(f"Endpoint /pokemon/ non disponible: {e}")
        tests_failed += 1
    print()

    # Test 6: Streamlit
    print("6️⃣  Test: Streamlit UI")
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print_success("Streamlit OK")
            print("   → URL: http://localhost:8501")
            tests_passed += 1
        else:
            print_error(f"Streamlit retourne code {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print_error(f"Streamlit non disponible: {e}")
        tests_failed += 1
    print()

    # Test 7: Dataset ML
    print("7️⃣  Test: Dataset ML")
    dataset_path = Path("data/datasets/pokemon_damage_ml.parquet")
    if dataset_path.exists():
        size_mb = dataset_path.stat().st_size / (1024 * 1024)
        print_success("Dataset ML OK")
        print(f"   → Fichier: pokemon_damage_ml.parquet")
        print(f"   → Taille: {size_mb:.2f} MB")
        tests_passed += 1
    else:
        print_error("Dataset ML non trouvé")
        print("   → Relancer: docker compose run --rm ml_builder")
        tests_failed += 1
    print()

    # Test 8: ETL completion check (via database)
    print("8️⃣  Test: ETL completion check")
    success_count, count_out, _ = run_docker_command(
        'docker compose exec -T db psql -U letsgo_user -d letsgo_db -t -c "SELECT COUNT(*) FROM pokemon;"'
    )
    if success_count:
        count = int(count_out.strip())
        if count > 0:
            print_success(f"ETL complété ({count} Pokémon en base)")
            tests_passed += 1
        else:
            print_warning("ETL non complété (0 Pokémon)")
            # Not counted as failure
    else:
        print_warning("Impossible de vérifier l'ETL")
    print()

    # Summary
    print_header("📊 RÉSUMÉ DES TESTS")
    print(f"Tests réussis: {GREEN}{tests_passed}{NC}")
    print(f"Tests échoués: {RED}{tests_failed}{NC}")
    print()

    print("🔗 Liens utiles:")
    print("   • Streamlit:    http://localhost:8501")
    print("   • API Swagger:  http://localhost:8000/docs")
    print("   • API Health:   http://localhost:8000/health")
    print()

    if tests_failed == 0:
        print_success("Tous les tests sont passés ! ✨")
        return 0
    else:
        print_error(f"{tests_failed} test(s) échoué(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
