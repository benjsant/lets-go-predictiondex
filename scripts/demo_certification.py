#!/usr/bin/env python3
"""
Automated Demonstration Script - E1/E3 Certification.

This script automatically opens all visual components
in the browser and displays demonstration information.

Usage:
    # Full demonstration
    python scripts/demo_certification.py

    # Web interfaces only
    python scripts/demo_certification.py --web-only

    # With metrics generation
    python scripts/demo_certification.py --generate-metrics
"""

import argparse
import subprocess
import sys
import time
import webbrowser
from typing import List, Tuple

import requests


# URL Configuration
URLS = {
    "streamlit": "http://localhost:8502",
    "swagger": "http://localhost:8080/docs",
    "grafana": "http://localhost:3001",
    "prometheus": "http://localhost:9091",
    "mlflow": "http://localhost:5001",
    "github_actions": "https://github.com/YOUR_USERNAME/lets-go-predictiondex/actions",
}


class DemoLauncher:
    """Automatic demonstration launcher."""

    def __init__(self, generate_metrics: bool = False):
        """Initialize the demo launcher.

        Args:
            generate_metrics: Whether to generate metrics in background.
        """
        self.generate_metrics = generate_metrics
        self.services_ok = []
        self.services_failed = []

    def print_header(self, text: str, emoji: str = ""):
        """Display a formatted header.

        Args:
            text: Header text.
            emoji: Optional emoji prefix.
        """
        print("\n" + "=" * 80)
        print(f"{emoji} {text}")
        print("=" * 80)

    def print_section(self, text: str, emoji: str = ""):
        """Display a section.

        Args:
            text: Section text.
            emoji: Optional emoji prefix.
        """
        print(f"\n{emoji} {text}")
        print("-" * 80)

    def check_service(self, name: str, url: str) -> bool:
        """Check if a service is accessible.

        Args:
            name: Service name.
            url: Service URL.

        Returns:
            True if service is accessible, False otherwise.
        """
        try:
            response = requests.get(url.replace("/docs", "/health"), timeout=5)
            if response.status_code == 200:
                self.services_ok.append(name)
                return True
        except requests.exceptions.RequestException:
            pass

        self.services_failed.append(name)
        return False

    def check_docker(self) -> bool:
        """Check if Docker is running.

        Returns:
            True if Docker is running, False otherwise.
        """
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False

    def open_urls(self, urls: List[Tuple[str, str]]):
        """Open multiple URLs in the browser.

        Args:
            urls: List of (name, url) tuples to open.
        """
        for name, url in urls:
            print(f" Opening {name}...")
            time.sleep(1)
            webbrowser.open_new_tab(url)

    def display_demo_guide(self):
        """Display the demonstration guide."""
        self.print_header("DEMONSTRATION GUIDE - E1/E3 CERTIFICATION", "")

        print("""
┌─────────────────────────────────────────────────────────────────────┐
│ SUMMARY TABLE │
├─────────────────────────────────────────────────────────────────────┤
│ Component │ URL/Command │ Competency │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Streamlit │ http://localhost:8502 │ C10 - Interface │
│ 2. Swagger API │ http://localhost:8080 │ C9 - API + AI │
│ 3. Grafana │ http://localhost:3001 │ C11 - Monitoring │
│ 4. Prometheus │ http://localhost:9091 │ C11 - Metrics │
│ 5. MLflow │ http://localhost:5001 │ C13 - MLOps │
│ 6. PostgreSQL │ Via Swagger API │ E1.3 - Database │
│ 7. ETL Pipeline │ docker logs letsgo_etl │ E1.1, E1.2 │
│ 8. ML Training │ docker logs letsgo_ml │ C12 - AI Optim │
│ 9. Notebooks │ code notebooks/ │ E1.4 - Analysis │
│ 10. Documentation │ README.md │ E1.5 - Docs │
└─────────────────────────────────────────────────────────────────────┘
        """)

    def display_shortcuts(self):
        """Display useful shortcuts."""
        self.print_section("USEFUL COMMANDS", "")

        print("""
# Validate stack
python scripts/validate_docker_stack.py --verbose

# Generate metrics for Grafana (5 min)
python scripts/generate_monitoring_data.py --mode realistic --duration 5

# View ETL logs (data collection)
docker logs letsgo_etl --tail 200

# View ML logs (model training)
docker logs letsgo_ml --tail 200

# Open Jupyter notebooks
code notebooks/03_training_evaluation.ipynb

# Check Evidently drift report
ls -lh api_pokemon/monitoring/reports/
        """)

    def display_demo_order(self):
        """Display recommended demonstration order."""
        self.print_section("RECOMMENDED DEMONSTRATION ORDER (30 min)", "")

        print("""
Phase 1: INTERACTIVE WEB INTERFACES (12 min)
  1. Streamlit (4 min) - Battle and Prediction Page [*]
     → Show ML prediction in action
  2. Swagger API (3 min) - Endpoint /predict/best-move [*]
     → Test API with JSON
  3. Grafana (3 min) - API Performance Dashboard [*]
     → Real-time metrics (latency, throughput)
  4. Prometheus (1 min) - Targets UP
  5. MLflow (2 min) - Experiments + Model Registry

Phase 2: BACKEND COMPONENTS (10 min)
  6. PostgreSQL (3 min) - Via Swagger /pokemon, /types, /moves
     → Show 11 tables, FK relationships
  7. ETL Pipeline (3 min) - Formatted Docker logs
     → 5 steps: Init → CSV → PokeAPI → Scraping → Validation
  8. ML Training (4 min) - Logs + Notebooks
     → 898k battles dataset → XGBoost 94.46% accuracy

Phase 3: ADVANCED TECHNICAL (8 min)
  9. Drift Detection (2 min) - Evidently HTML reports
  10. GitHub Actions (3 min) - 4 CI/CD workflows
  11. Documentation (3 min) - README + Diagrams
        """)

    def display_competences_mapping(self):
        """Display component to competency mapping."""
        self.print_section("E1/E3 COMPETENCIES MAPPING", "")

        print("""
╔═════════════════════════════════════════════════════════════════════╗
║ BLOCK E1 - DATA ║
╠═════════════════════════════════════════════════════════════════════╣
║ E1.1 - Data Collection │ ETL Pipeline (3 sources) ║
║ E1.2 - Data Cleaning │ Validation, normalization ║
║ E1.3 - Database Design │ PostgreSQL 11 tables 3NF ║
║ E1.4 - Data Analysis │ Feature engineering 133 features ║
║ E1.5 - Documentation │ README + docs/ + diagrams ║
╠═════════════════════════════════════════════════════════════════════╣
║ BLOCK E3 - AI PRODUCTION ║
╠═════════════════════════════════════════════════════════════════════╣
║ C9 - REST API + AI │ FastAPI + XGBoost 94.46% ║
║ C10 - App Integration │ Streamlit 8 pages ║
║ C11 - AI Monitoring │ Prometheus + Grafana + Evidently ║
║ C12 - AI Optimization │ XGBoost optimized < 500ms ║
║ C13 - MLOps CI/CD │ MLflow + GitHub Actions ║
╚═════════════════════════════════════════════════════════════════════╝
        """)

    def run_demo(self, web_only: bool = False):
        """Run the complete demonstration.

        Args:
            web_only: If True, only open web interfaces without full guide.
        """
        self.print_header("LAUNCHING E1/E3 CERTIFICATION DEMONSTRATION", "")

        # 1. Check Docker
        self.print_section("Docker Stack Verification", "")
        if not self.check_docker():
            print("Docker is not running")
            print("\nStart the services:")
            print(" python scripts/start_docker_stack.py")
            sys.exit(1)
        print("Docker is active")

        # 2. Check services
        print("\nVerifying web services...")
        for name, url in URLS.items():
            if name == "github_actions":
                continue
            if self.check_service(name, url):
                print(f" {name:20s} - {url}")
            else:
                print(f" {name:20s} - {url}")

        # 3. Display guide
        self.display_demo_guide()

        # 4. Open web interfaces
        self.print_section("Opening Web Interfaces", "")
        print("\nOpening 5 browser tabs...")

        web_urls = [
            ("Streamlit", URLS["streamlit"]),
            ("Swagger API", URLS["swagger"]),
            ("Grafana", URLS["grafana"]),
            ("MLflow", URLS["mlflow"]),
            ("Prometheus", URLS["prometheus"]),
        ]

        self.open_urls(web_urls)

        print("\nWeb interfaces opened!")

        # 5. Generate metrics (optional)
        if self.generate_metrics and not web_only:
            self.print_section("Generating Monitoring Metrics", "")
            print("\nGenerating realistic traffic (5 min)...")
            print(" This will populate Grafana dashboards with data")

            try:
                # pylint: disable=consider-using-with
                # We intentionally run this in background without waiting
                subprocess.Popen(
                    [
                        "python",
                        "scripts/generate_monitoring_data.py",
                        "--mode", "realistic",
                        "--duration", "5"
                    ]
                )
                print("Metrics generation started in background")
                print(" Check Grafana: http://localhost:3001")
            except OSError as exc:
                print(f"Unable to start generation: {exc}")

        # 6. Display demo order
        if not web_only:
            self.display_demo_order()

        # 7. Display competencies
        self.display_competences_mapping()

        # 8. Display shortcuts
        self.display_shortcuts()

        # 9. Final summary
        self.print_header("DEMONSTRATION READY", "[OK]")

        if self.services_ok:
            print(f"\n{len(self.services_ok)} services accessible:")
            for service in self.services_ok:
                print(f" • {service}")

        if self.services_failed:
            print(f"\n{len(self.services_failed)} services not accessible:")
            for service in self.services_failed:
                print(f" • {service}")
            print("\nStart missing services:")
            print(" docker-compose up -d")

        print("\n CHECKLIST BEFORE DEMO:")
        print(" [ ] 5 browser tabs open")
        print(" [ ] All services UP (green)")
        print(" [ ] Metrics generated (Grafana)")
        print(" [ ] Notebooks open in VSCode")
        print(" [ ] README.md and docs/ prepared")

        print("\nREADY FOR CERTIFICATION!")
        print("\nFull guide: GUIDE_DEMONSTRATION_VISUELLE.md")

        print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automatic E1/E3 demonstration launcher"
    )
    parser.add_argument(
        "--web-only",
        action="store_true",
        help="Open only web interfaces (no full guide)"
    )
    parser.add_argument(
        "--generate-metrics",
        action="store_true",
        help="Start metrics generation in background"
    )

    args = parser.parse_args()

    launcher = DemoLauncher(generate_metrics=args.generate_metrics)

    try:
        launcher.run_demo(web_only=args.web_only)
        return 0
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted")
        return 1


if __name__ == "__main__":
    sys.exit(main())
