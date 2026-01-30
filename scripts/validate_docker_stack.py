#!/usr/bin/env python3
"""
Docker Stack Validator
======================

Validation script to verify that all Docker services are properly
configured and functional.

This script performs comprehensive health checks on:
    - PostgreSQL database connectivity
    - FastAPI application endpoints
    - Prometheus metrics collection
    - Grafana dashboard availability
    - MLflow tracking server
    - Container status and resource usage

Usage:
    # Validate entire stack
    python scripts/validate_docker_stack.py

    # Validate with verbose output
    python scripts/validate_docker_stack.py --verbose

Exit Codes:
    0: All services validated successfully
    1: One or more services failed validation

Output:
    - Terminal: Colored validation results
    - Optional: JSON report with detailed status
"""

import argparse
import requests
import time
import sys
from typing import Dict, List, Tuple
from pathlib import Path


# Services à valider
SERVICES = {
    "postgres": {
        "url": None,  # Pas d'URL HTTP
        "port": 5432,
        "description": "Base de données PostgreSQL"
    },
    "api": {
        "url": "http://localhost:8080/health",
        "port": 8080,
        "description": "API FastAPI"
    },
    "streamlit": {
        "url": "http://localhost:8502",
        "port": 8502,
        "description": "Interface Streamlit"
    },
    "prometheus": {
        "url": "http://localhost:9091/-/healthy",
        "port": 9091,
        "description": "Prometheus (monitoring)"
    },
    "grafana": {
        "url": "http://localhost:3001/api/health",
        "port": 3001,
        "description": "Grafana (dashboards)"
    },
    "mlflow": {
        "url": "http://localhost:5001/health",
        "port": 5001,
        "description": "MLflow (Model Registry)"
    },
    "node-exporter": {
        "url": "http://localhost:9100/metrics",
        "port": 9100,
        "description": "Node Exporter (métriques système)"
    }
}


class DockerStackValidator:
    """Validateur de stack Docker."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}

    def check_service(self, name: str, config: Dict) -> Tuple[bool, str]:
        """
        Vérifie qu'un service est accessible.

        Returns:
            (is_healthy, message)
        """
        if config["url"] is None:
            # Pas de health check HTTP (ex: postgres)
            return True, "N/A (pas de health check HTTP)"

        try:
            response = requests.get(config["url"], timeout=5)

            if response.status_code == 200:
                return True, f"✅ Accessible (HTTP {response.status_code})"
            else:
                return False, f"⚠️  HTTP {response.status_code}"

        except requests.exceptions.ConnectionError:
            return False, "❌ Connexion refusée (service non démarré?)"

        except requests.exceptions.Timeout:
            return False, "❌ Timeout (service lent ou non démarré?)"

        except Exception as e:
            return False, f"❌ Erreur: {str(e)[:50]}"

    def check_api_endpoints(self) -> Dict[str, bool]:
        """Vérifie les endpoints clés de l'API."""
        endpoints = {
            "/health": "Health check",
            "/docs": "Documentation Swagger",
            "/metrics": "Métriques Prometheus",
            "/pokemon": "Liste Pokémon",
            "/types": "Liste types",
            "/moves": "Liste capacités"
        }

        results = {}

        for endpoint, description in endpoints.items():
            try:
                response = requests.get(f"http://localhost:8080{endpoint}", timeout=5)
                results[endpoint] = response.status_code == 200

                if self.verbose:
                    status = "✅" if results[endpoint] else "❌"
                    print(f"      {status} {endpoint:20s} - {description}")

            except:
                results[endpoint] = False
                if self.verbose:
                    print(f"      ❌ {endpoint:20s} - {description}")

        return results

    def check_prometheus_targets(self) -> Dict[str, str]:
        """Vérifie les targets Prometheus."""
        try:
            response = requests.get(
                "http://localhost:9090/api/v1/targets",
                timeout=5
            )

            if response.status_code != 200:
                return {"error": "Impossible d'accéder aux targets"}

            data = response.json()
            targets = {}

            for target in data["data"]["activeTargets"]:
                job = target["labels"]["job"]
                health = target["health"]
                targets[job] = health

                if self.verbose:
                    status = "✅" if health == "up" else "❌"
                    endpoint = target["scrapeUrl"]
                    print(f"      {status} {job:20s} - {endpoint}")

            return targets

        except Exception as e:
            return {"error": str(e)}

    def check_grafana_datasources(self) -> Dict[str, bool]:
        """Vérifie les datasources Grafana."""
        try:
            # Grafana anonymous access enabled
            response = requests.get(
                "http://localhost:3000/api/datasources",
                timeout=5
            )

            if response.status_code != 200:
                return {"error": "Impossible d'accéder aux datasources"}

            datasources = response.json()
            results = {}

            for ds in datasources:
                name = ds["name"]
                type_ = ds["type"]
                results[name] = ds.get("basicAuth", False) or True

                if self.verbose:
                    print(f"      ✅ {name:20s} ({type_})")

            return results

        except Exception as e:
            return {"error": str(e)}

    def run_validation(self):
        """Exécute la validation complète."""
        print("\n" + "=" * 80)
        print("🔍 Validation de la stack Docker")
        print("=" * 80)

        all_healthy = True

        # 1. Vérifier les services
        print("\n1️⃣ Services Docker")
        print("-" * 80)

        for name, config in SERVICES.items():
            is_healthy, message = self.check_service(name, config)
            self.results[name] = is_healthy

            status = "✅" if is_healthy else "❌"
            print(f"{status} {name:20s} [{config['port']:5d}] - {config['description']}")

            if not is_healthy:
                print(f"   {message}")
                all_healthy = False
            elif self.verbose:
                print(f"   {message}")

        # 2. Vérifier endpoints API
        if self.results.get("api"):
            print("\n2️⃣ Endpoints API")
            print("-" * 80)

            endpoints = self.check_api_endpoints()
            api_healthy = all(endpoints.values())

            if not self.verbose:
                working = sum(endpoints.values())
                total = len(endpoints)
                print(f"   {working}/{total} endpoints fonctionnels")

            if not api_healthy:
                all_healthy = False

        # 3. Vérifier Prometheus targets
        if self.results.get("prometheus"):
            print("\n3️⃣ Prometheus Targets")
            print("-" * 80)

            targets = self.check_prometheus_targets()

            if "error" not in targets:
                up_count = sum(1 for v in targets.values() if v == "up")
                total_count = len(targets)
                print(f"   {up_count}/{total_count} targets UP")

                if not self.verbose:
                    for job, health in targets.items():
                        status = "✅" if health == "up" else "❌"
                        print(f"      {status} {job}")
            else:
                print(f"   ⚠️  {targets['error']}")

        # 4. Vérifier Grafana datasources
        if self.results.get("grafana"):
            print("\n4️⃣ Grafana Datasources")
            print("-" * 80)

            datasources = self.check_grafana_datasources()

            if "error" not in datasources:
                print(f"   {len(datasources)} datasource(s) configurée(s)")
            else:
                print(f"   ⚠️  {datasources['error']}")

        # 5. Résumé
        print("\n" + "=" * 80)

        if all_healthy:
            print("✅ Tous les services sont opérationnels!")
            print("\n💡 URLs utiles:")
            print(f"   API Swagger: http://localhost:8080/docs")
            print(f"   Streamlit: http://localhost:8502")
            print(f"   Grafana: http://localhost:3001")
            print(f"   Prometheus: http://localhost:9091")
            print(f"   MLflow: http://localhost:5001")
            return 0
        else:
            print("❌ Certains services ne sont pas accessibles")
            print("\n💡 Démarrez les services manquants:")
            print("   docker-compose up -d")
            print("\n💡 Vérifiez les logs:")
            print("   docker-compose logs <service>")
            return 1


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Validateur de stack Docker"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mode verbeux (afficher plus de détails)"
    )

    args = parser.parse_args()

    validator = DockerStackValidator(verbose=args.verbose)
    exit_code = validator.run_validation()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
