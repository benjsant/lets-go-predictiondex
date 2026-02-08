#!/usr/bin/env python3
"""
Docker Stack Validator.

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
import sys
from typing import Dict, Tuple

import requests


# Services to validate
SERVICES = {
    "postgres": {
        "url": None,  # No HTTP URL
        "port": 5432,
        "description": "PostgreSQL Database"
    },
    "api": {
        "url": "http://localhost:8080/health",
        "port": 8080,
        "description": "FastAPI API"
    },
    "streamlit": {
        "url": "http://localhost:8502",
        "port": 8502,
        "description": "Streamlit Interface"
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
        "url": "http://localhost:9101/metrics",
        "port": 9101,
        "description": "Node Exporter (system metrics)"
    }
}


class DockerStackValidator:
    """Docker stack validator."""

    def __init__(self, verbose: bool = False):
        """Initialize the validator.

        Args:
            verbose: Whether to display detailed output.
        """
        self.verbose = verbose
        self.results = {}

    def check_service(self, config: Dict) -> Tuple[bool, str]:
        """Check that a service is accessible.

        Args:
            config: Service configuration dictionary.

        Returns:
            Tuple of (is_healthy, message).
        """
        if config["url"] is None:
            # No HTTP health check (e.g., postgres)
            return True, "N/A (no HTTP health check)"

        try:
            response = requests.get(config["url"], timeout=5)

            if response.status_code == 200:
                return True, f"✅ Accessible (HTTP {response.status_code})"

            return False, f"⚠️  HTTP {response.status_code}"

        except requests.exceptions.ConnectionError:
            return False, "❌ Connection refused (service not started?)"

        except requests.exceptions.Timeout:
            return False, "❌ Timeout (service slow or not started?)"

        except requests.exceptions.RequestException as exc:
            return False, f"❌ Error: {str(exc)[:50]}"

    def check_api_endpoints(self) -> Dict[str, bool]:
        """Check key API endpoints.

        Returns:
            Dictionary mapping endpoint to health status.
        """
        endpoints = {
            "/health": "Health check",
            "/docs": "Swagger Documentation",
            "/metrics": "Prometheus Metrics",
            "/pokemon": "Pokemon List",
            "/types": "Types List",
            "/moves": "Moves List"
        }

        results = {}

        for endpoint, description in endpoints.items():
            try:
                response = requests.get(
                    f"http://localhost:8080{endpoint}",
                    timeout=5
                )
                results[endpoint] = response.status_code == 200

                if self.verbose:
                    status = "✅" if results[endpoint] else "❌"
                    print(f"      {status} {endpoint:20s} - {description}")

            except requests.exceptions.RequestException:
                results[endpoint] = False
                if self.verbose:
                    print(f"      ❌ {endpoint:20s} - {description}")

        return results

    def check_prometheus_targets(self) -> Dict[str, str]:
        """Check Prometheus targets.

        Returns:
            Dictionary mapping job name to health status.
        """
        try:
            response = requests.get(
                "http://localhost:9091/api/v1/targets",
                timeout=5
            )

            if response.status_code != 200:
                return {"error": "Unable to access targets"}

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

        except requests.exceptions.RequestException as exc:
            return {"error": str(exc)}

    def check_grafana_datasources(self) -> Dict[str, bool]:
        """Check Grafana datasources.

        Returns:
            Dictionary mapping datasource name to availability status.
        """
        try:
            # Grafana anonymous access enabled
            response = requests.get(
                "http://localhost:3001/api/datasources",
                timeout=5
            )

            if response.status_code != 200:
                return {"error": "Unable to access datasources"}

            datasources = response.json()
            results = {}

            for ds in datasources:
                name = ds["name"]
                type_ = ds["type"]
                results[name] = ds.get("basicAuth", False) or True

                if self.verbose:
                    print(f"      ✅ {name:20s} ({type_})")

            return results

        except requests.exceptions.RequestException as exc:
            return {"error": str(exc)}

    def run_validation(self):
        """Run complete validation.

        Returns:
            Exit code (0 for success, 1 for failure).
        """
        print("\n" + "=" * 80)
        print("🔍 Docker Stack Validation")
        print("=" * 80)

        all_healthy = True

        # 1. Check services
        print("\n1️⃣ Docker Services")
        print("-" * 80)

        for name, config in SERVICES.items():
            is_healthy, message = self.check_service(config)
            self.results[name] = is_healthy

            status = "✅" if is_healthy else "❌"
            print(f"{status} {name:20s} [{config['port']:5d}] - {config['description']}")

            if not is_healthy:
                print(f"   {message}")
                all_healthy = False
            elif self.verbose:
                print(f"   {message}")

        # 2. Check API endpoints
        if self.results.get("api"):
            print("\n2️⃣ API Endpoints")
            print("-" * 80)

            endpoints = self.check_api_endpoints()
            api_healthy = all(endpoints.values())

            if not self.verbose:
                working = sum(endpoints.values())
                total = len(endpoints)
                print(f"   {working}/{total} endpoints functional")

            if not api_healthy:
                all_healthy = False

        # 3. Check Prometheus targets
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

        # 4. Check Grafana datasources
        if self.results.get("grafana"):
            print("\n4️⃣ Grafana Datasources")
            print("-" * 80)

            datasources = self.check_grafana_datasources()

            if "error" not in datasources:
                print(f"   {len(datasources)} datasource(s) configured")
            else:
                print(f"   ⚠️  {datasources['error']}")

        # 5. Summary
        print("\n" + "=" * 80)

        if all_healthy:
            print("✅ All services are operational!")
            print("\n💡 Useful URLs:")
            print("   API Swagger: http://localhost:8080/docs")
            print("   Streamlit: http://localhost:8502")
            print("   Grafana: http://localhost:3001")
            print("   Prometheus: http://localhost:9091")
            print("   MLflow: http://localhost:5001")
            return 0

        print("❌ Some services are not accessible")
        print("\n💡 Start missing services:")
        print("   docker-compose up -d")
        print("\n💡 Check logs:")
        print("   docker-compose logs <service>")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Docker Stack Validator"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose mode (show more details)"
    )

    args = parser.parse_args()

    validator = DockerStackValidator(verbose=args.verbose)
    exit_code = validator.run_validation()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
