#!/usr/bin/env python3
"""
Test Complet du Système PredictionDex
Valide tous les composants de A à Z: Monitoring, MLflow, ETL, API, Streamlit
"""
import os
import sys
import time
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Couleurs
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

# Configuration
API_URL = "http://localhost:8080"
PROMETHEUS_URL = "http://localhost:9091"
GRAFANA_URL = "http://localhost:3001"
MLFLOW_URL = "http://localhost:5001"
STREAMLIT_URL = "http://localhost:8502"
PGADMIN_URL = "http://localhost:5050"

# Charger API key
def load_api_key() -> Optional[str]:
    # Remonter à la racine du projet depuis tests/integration/
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("API_KEYS="):
                    keys = line.split("=", 1)[1].strip().strip('"')
                    return keys.split(",")[0] if keys else None
    return None

API_KEY = load_api_key()
API_HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

class SystemTester:
    def __init__(self):
        self.results = {
            "services": {},
            "monitoring": {},
            "mlflow": {},
            "api": {},
            "data": {},
            "predictions": {},
            "errors": []
        }
        self.total_tests = 0
        self.passed_tests = 0

    def print_header(self, title: str, color: str = BLUE):
        print(f"\n{color}{'='*100}{RESET}")
        print(f"{color}{title:^100}{RESET}")
        print(f"{color}{'='*100}{RESET}\n")

    def print_section(self, title: str):
        print(f"\n{CYAN}{'─'*100}{RESET}")
        print(f"{CYAN}📋 {title}{RESET}")
        print(f"{CYAN}{'─'*100}{RESET}")

    def print_test(self, name: str, passed: bool, details: str = ""):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            symbol = f"{GREEN}✅{RESET}"
        else:
            symbol = f"{RED}❌{RESET}"

        status = f"{symbol} {name}"
        if details:
            status += f" {YELLOW}({details}){RESET}"
        print(f"  {status}")

    def print_info(self, message: str):
        print(f"     {message}")

    def print_warning(self, message: str):
        print(f"  {YELLOW}⚠️  {message}{RESET}")

    def print_error(self, message: str):
        print(f"  {RED}❌ {message}{RESET}")
        self.results["errors"].append(message)

    def print_success(self, message: str):
        print(f"  {GREEN}✅ {message}{RESET}")

    # ========================================================================
    # PHASE 1: SERVICES
    # ========================================================================

    def test_all_services(self) -> bool:
        """Test que tous les services Docker sont UP"""
        self.print_header("🚀 PHASE 1: VÉRIFICATION SERVICES DOCKER", MAGENTA)

        services = {
            "PostgreSQL": {"url": None, "docker": "db", "port": "5432"},
            "API": {"url": f"{API_URL}/health", "docker": "api", "port": "8080"},
            "Streamlit": {"url": STREAMLIT_URL, "docker": "streamlit", "port": "8502"},
            "MLflow": {"url": f"{MLFLOW_URL}/health", "docker": "mlflow", "port": "5001"},
            "Prometheus": {"url": f"{PROMETHEUS_URL}/-/healthy", "docker": "prometheus", "port": "9091"},
            "Grafana": {"url": f"{GRAFANA_URL}/api/health", "docker": "grafana", "port": "3001"},
            "pgAdmin": {"url": PGADMIN_URL, "docker": "pgadmin", "port": "5050"},
        }

        all_up = True

        for service_name, config in services.items():
            url = config.get("url")

            if url:
                try:
                    response = requests.get(url, timeout=5, allow_redirects=True)
                    if response.status_code in [200, 302]:
                        self.print_test(f"{service_name}", True, f"HTTP {response.status_code}")
                        self.results["services"][service_name] = "UP"
                    else:
                        self.print_test(f"{service_name}", False, f"HTTP {response.status_code}")
                        self.results["services"][service_name] = f"ERROR_{response.status_code}"
                        all_up = False
                except Exception as e:
                    self.print_test(f"{service_name}", False, str(e))
                    self.results["services"][service_name] = "DOWN"
                    all_up = False
            else:
                # PostgreSQL - check via docker
                import subprocess
                try:
                    result = subprocess.run(
                        ["docker", "exec", "letsgo_postgres", "pg_isready", "-U", "letsgo_user"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        self.print_test(f"{service_name}", True, "pg_isready OK")
                        self.results["services"][service_name] = "UP"
                    else:
                        self.print_test(f"{service_name}", False, "Not ready")
                        self.results["services"][service_name] = "NOT_READY"
                        all_up = False
                except Exception as e:
                    self.print_test(f"{service_name}", False, str(e))
                    self.results["services"][service_name] = "ERROR"
                    all_up = False

        return all_up

    # ========================================================================
    # PHASE 2: MONITORING (Prometheus + Grafana + Evidently)
    # ========================================================================

    def test_monitoring_stack(self) -> bool:
        """Test complet du monitoring"""
        self.print_header("📊 PHASE 2: MONITORING (Prometheus + Grafana + Evidently)", MAGENTA)

        # 2.1 Prometheus Targets
        self.print_section("2.1 Prometheus - Targets & Scraping")
        try:
            response = requests.get(f"{PROMETHEUS_URL}/api/v1/targets", timeout=5)
            if response.status_code == 200:
                data = response.json()
                active_targets = data.get("data", {}).get("activeTargets", [])

                up_count = sum(1 for t in active_targets if t.get("health") == "up")
                total_count = len(active_targets)

                self.print_test("Prometheus Targets", up_count == total_count,
                              f"{up_count}/{total_count} UP")

                for target in active_targets:
                    job = target.get("labels", {}).get("job", "unknown")
                    health = target.get("health", "unknown")
                    if health == "up":
                        self.print_info(f"  ✅ {job}: {health}")
                    else:
                        self.print_info(f"  ❌ {job}: {health}")

                self.results["monitoring"]["prometheus_targets"] = f"{up_count}/{total_count}"
            else:
                self.print_test("Prometheus Targets", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Prometheus Targets", False, str(e))
            return False

        # 2.2 Métriques collectées
        self.print_section("2.2 Prometheus - Métriques Disponibles")

        critical_metrics = {
            "api_requests_total": "API Requests Counter",
            "api_request_duration_seconds_bucket": "API Latency Histogram",
            "model_predictions_total": "Model Predictions Counter",
            "model_prediction_duration_seconds_bucket": "Model Latency Histogram",
            "model_confidence_score_bucket": "Confidence Distribution",
            "system_cpu_usage_percent": "CPU Usage",
            "system_memory_usage_percent": "Memory Usage"
        }

        metrics_ok = True
        for metric, description in critical_metrics.items():
            try:
                response = requests.get(
                    f"{PROMETHEUS_URL}/api/v1/query",
                    params={"query": metric},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("data", {}).get("result", [])
                    if result:
                        self.print_test(description, True, f"{len(result)} séries")
                        self.results["monitoring"][metric] = len(result)
                    else:
                        self.print_test(description, False, "Aucune donnée")
                        metrics_ok = False
                else:
                    self.print_test(description, False, f"HTTP {response.status_code}")
                    metrics_ok = False
            except Exception as e:
                self.print_test(description, False, str(e))
                metrics_ok = False

        # 2.3 Percentiles (après corrections)
        self.print_section("2.3 Prometheus - Percentiles (P50, P95, P99)")

        percentile_queries = {
            "P50": "histogram_quantile(0.50, sum(rate(api_request_duration_seconds_bucket[2m])) by (le))",
            "P95": "histogram_quantile(0.95, sum(rate(api_request_duration_seconds_bucket[2m])) by (le))",
            "P99": "histogram_quantile(0.99, sum(rate(api_request_duration_seconds_bucket[2m])) by (le))"
        }

        percentiles_ok = True
        for name, query in percentile_queries.items():
            try:
                response = requests.get(
                    f"{PROMETHEUS_URL}/api/v1/query",
                    params={"query": query},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("data", {}).get("result", [])
                    if result:
                        value = result[0].get("value", [None, None])[1]
                        if value and value != "NaN":
                            self.print_test(f"{name} Latency", True, f"{float(value)*1000:.2f}ms")
                            self.results["monitoring"][f"latency_{name}"] = float(value)
                        else:
                            self.print_test(f"{name} Latency", False, "NaN")
                            percentiles_ok = False
                    else:
                        self.print_test(f"{name} Latency", False, "No data")
                        percentiles_ok = False
                else:
                    self.print_test(f"{name} Latency", False, f"HTTP {response.status_code}")
                    percentiles_ok = False
            except Exception as e:
                self.print_test(f"{name} Latency", False, str(e))
                percentiles_ok = False

        # 2.4 Grafana Dashboards
        self.print_section("2.4 Grafana - Dashboards")

        try:
            response = requests.get(
                f"{GRAFANA_URL}/api/search?type=dash-db",
                auth=("admin", "admin"),
                timeout=5
            )
            if response.status_code == 200:
                dashboards = response.json()
                self.print_test("Grafana Dashboards", len(dashboards) >= 2,
                              f"{len(dashboards)} dashboards")

                for dash in dashboards:
                    self.print_info(f"  📊 {dash.get('title')} (uid: {dash.get('uid')})")

                self.results["monitoring"]["grafana_dashboards"] = len(dashboards)
            else:
                self.print_test("Grafana Dashboards", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Grafana Dashboards", False, str(e))
            return False

        # 2.5 Evidently (Drift Detection)
        self.print_section("2.5 Evidently - Drift Detection")

        # Vérifier si le module drift detection existe
        drift_report_dir = Path(__file__).parent.parent / "reports" / "drift"

        if drift_report_dir.exists():
            reports = list(drift_report_dir.glob("*.html"))
            self.print_test("Drift Reports", len(reports) > 0, f"{len(reports)} rapports")
            self.results["monitoring"]["drift_reports"] = len(reports)
        else:
            self.print_warning("Dossier drift reports non trouvé (normal si pas encore généré)")
            self.results["monitoring"]["drift_reports"] = 0

        return metrics_ok and percentiles_ok

    # ========================================================================
    # PHASE 3: MLFLOW
    # ========================================================================

    def test_mlflow_stack(self) -> bool:
        """Test MLflow Registry et Tracking"""
        self.print_header("🎯 PHASE 3: MLFLOW (Registry + Tracking + Experiments)", MAGENTA)

        # 3.1 Expérimentations
        self.print_section("3.1 MLflow - Expérimentations")

        try:
            response = requests.get(f"{MLFLOW_URL}/api/2.0/mlflow/experiments/search", timeout=5)
            if response.status_code == 200:
                data = response.json()
                experiments = data.get("experiments", [])

                non_default = [e for e in experiments if e.get("name") != "Default"]

                self.print_test("MLflow Experiments", len(non_default) > 0,
                              f"{len(non_default)} expérimentations")

                for exp in non_default:
                    name = exp.get("name")
                    exp_id = exp.get("experiment_id")
                    self.print_info(f"  🧪 {name} (ID: {exp_id})")

                self.results["mlflow"]["experiments"] = len(non_default)
            else:
                self.print_test("MLflow Experiments", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test("MLflow Experiments", False, str(e))
            return False

        # 3.2 Model Registry
        self.print_section("3.2 MLflow - Model Registry")

        try:
            response = requests.get(
                f"{MLFLOW_URL}/api/2.0/mlflow/registered-models/search",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get("registered_models", [])

                self.print_test("Registered Models", len(models) > 0,
                              f"{len(models)} modèles")

                for model in models:
                    name = model.get("name")
                    versions = model.get("latest_versions", [])

                    self.print_info(f"  📦 {name}: {len(versions)} version(s)")

                    for v in versions:
                        version_num = v.get("version")
                        stage = v.get("current_stage")
                        status = v.get("status")

                        stage_emoji = "🏆" if stage == "Production" else "📝"
                        self.print_info(f"     {stage_emoji} v{version_num}: {stage} ({status})")

                self.results["mlflow"]["models"] = len(models)

                # Vérifier qu'il y a au moins un modèle en Production
                prod_models = sum(1 for m in models
                                for v in m.get("latest_versions", [])
                                if v.get("current_stage") == "Production")

                self.print_test("Production Models", prod_models > 0,
                              f"{prod_models} en production")

            else:
                self.print_test("Registered Models", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Registered Models", False, str(e))
            return False

        # 3.3 Runs récents
        self.print_section("3.3 MLflow - Runs Récents")

        try:
            # Chercher les runs de l'expérimentation principale
            response = requests.get(
                f"{MLFLOW_URL}/api/2.0/mlflow/runs/search",
                json={"experiment_ids": ["1"]},  # ID de pokemon_battle_winner
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                runs = data.get("runs", [])

                self.print_test("MLflow Runs", len(runs) > 0, f"{len(runs)} runs")

                for run in runs[:5]:  # Top 5 runs
                    run_id = run.get("info", {}).get("run_id", "")[:8]
                    run_name = run.get("info", {}).get("run_name", "unnamed")
                    status = run.get("info", {}).get("status", "unknown")

                    self.print_info(f"  🏃 {run_name} ({run_id}...): {status}")

                self.results["mlflow"]["runs"] = len(runs)
            else:
                self.print_warning("Impossible de récupérer les runs (peut être normal)")
                self.results["mlflow"]["runs"] = 0
        except Exception as e:
            self.print_warning(f"Erreur runs: {e}")

        return True

    # ========================================================================
    # PHASE 4: API
    # ========================================================================

    def test_api_endpoints(self) -> bool:
        """Test tous les endpoints de l'API"""
        self.print_header("🔌 PHASE 4: API REST (FastAPI)", MAGENTA)

        # 4.1 Health & Info
        self.print_section("4.1 API - Health & Info")

        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            self.print_test("Health Check", response.status_code == 200,
                          response.json().get("status", ""))
        except Exception as e:
            self.print_test("Health Check", False, str(e))

        # 4.2 Pokémon endpoints
        self.print_section("4.2 API - Pokémon Endpoints")

        pokemon_tests = [
            ("/pokemon/", "GET", "Liste Pokémon"),
            ("/pokemon/1", "GET", "Bulbizarre (ID 1)"),
            ("/pokemon/25", "GET", "Pikachu (ID 25)"),
            ("/pokemon/6", "GET", "Dracaufeu (ID 6)"),
        ]

        for endpoint, method, description in pokemon_tests:
            try:
                response = requests.get(f"{API_URL}{endpoint}", headers=API_HEADERS, timeout=5)
                self.print_test(description, response.status_code == 200,
                              f"HTTP {response.status_code}")
            except Exception as e:
                self.print_test(description, False, str(e))

        # 4.3 Autres endpoints
        self.print_section("4.3 API - Autres Endpoints")

        other_tests = [
            ("/moves/", "Capacités"),
            ("/types/", "Types"),
            ("/metrics", "Métriques Prometheus"),
        ]

        for endpoint, description in other_tests:
            try:
                headers = API_HEADERS if endpoint != "/metrics" else {}
                response = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=5)
                self.print_test(description, response.status_code == 200,
                              f"HTTP {response.status_code}")
            except Exception as e:
                self.print_test(description, False, str(e))

        # 4.4 Prédictions ML
        self.print_section("4.4 API - Prédictions ML")

        prediction_payload = {
            "pokemon_a_id": 6,  # Dracaufeu
            "pokemon_b_id": 25,  # Pikachu
            "available_moves": [1, 2, 3, 4]
        }

        try:
            response = requests.post(
                f"{API_URL}/predict/best-move",
                json=prediction_payload,
                headers=API_HEADERS,
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                recommended = result.get("recommended_move")
                win_prob = result.get("win_probability", 0)

                self.print_test("Prédiction ML", True,
                              f"Move {recommended}, Win: {win_prob*100:.1f}%")
                self.results["predictions"]["success"] = True
                self.results["predictions"]["win_probability"] = win_prob
            else:
                self.print_test("Prédiction ML", False, f"HTTP {response.status_code}")
                self.results["predictions"]["success"] = False
        except Exception as e:
            self.print_test("Prédiction ML", False, str(e))
            self.results["predictions"]["success"] = False

        # Model Info
        try:
            response = requests.get(f"{API_URL}/predict/model-info", headers=API_HEADERS, timeout=5)
            if response.status_code == 200:
                info = response.json()
                model_type = info.get("model_type")
                accuracy = info.get("metrics", {}).get("test_accuracy", 0)

                self.print_test("Model Info", True,
                              f"{model_type}, Accuracy: {accuracy*100:.2f}%")
                self.results["predictions"]["model_accuracy"] = accuracy
            else:
                self.print_test("Model Info", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test("Model Info", False, str(e))

        return True

    # ========================================================================
    # PHASE 5: DONNÉES
    # ========================================================================

    def test_data_availability(self) -> bool:
        """Test que les données sont bien chargées"""
        self.print_header("💾 PHASE 5: DONNÉES (ETL + Database)", MAGENTA)

        # Compter les Pokémon
        try:
            response = requests.get(f"{API_URL}/pokemon/", headers=API_HEADERS, timeout=5)
            if response.status_code == 200:
                pokemon_list = response.json()
                count = len(pokemon_list)

                self.print_test("Pokémon en base", count > 100, f"{count} Pokémon")
                self.results["data"]["pokemon_count"] = count
            else:
                self.print_test("Pokémon en base", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test("Pokémon en base", False, str(e))

        # Compter les capacités
        try:
            response = requests.get(f"{API_URL}/moves/", headers=API_HEADERS, timeout=5)
            if response.status_code == 200:
                moves_list = response.json()
                count = len(moves_list)

                self.print_test("Capacités en base", count > 100, f"{count} capacités")
                self.results["data"]["moves_count"] = count
            else:
                self.print_test("Capacités en base", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test("Capacités en base", False, str(e))

        # Compter les types
        try:
            response = requests.get(f"{API_URL}/types/", headers=API_HEADERS, timeout=5)
            if response.status_code == 200:
                types_list = response.json()
                count = len(types_list)

                self.print_test("Types en base", count >= 18, f"{count} types")
                self.results["data"]["types_count"] = count
            else:
                self.print_test("Types en base", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.print_test("Types en base", False, str(e))

        return True

    # ========================================================================
    # RAPPORT FINAL
    # ========================================================================

    def generate_final_report(self):
        """Génère le rapport final"""
        self.print_header("📋 RAPPORT FINAL DE VALIDATION", GREEN if self.passed_tests/self.total_tests >= 0.9 else RED)

        # Score global
        score_pct = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0

        print(f"\n{CYAN}{'='*100}{RESET}")
        print(f"{CYAN}SCORE GLOBAL: {self.passed_tests}/{self.total_tests} ({score_pct:.1f}%){RESET}")
        print(f"{CYAN}{'='*100}{RESET}\n")

        # Verdict
        if score_pct >= 95:
            print(f"{GREEN}🏆 EXCELLENT - Système Production-Ready{RESET}")
        elif score_pct >= 85:
            print(f"{GREEN}✅ TRÈS BON - Système Fonctionnel{RESET}")
        elif score_pct >= 75:
            print(f"{YELLOW}⚠️  BON - Quelques ajustements nécessaires{RESET}")
        else:
            print(f"{RED}❌ INSUFFISANT - Problèmes à résoudre{RESET}")

        # Détails par composant
        print(f"\n{CYAN}DÉTAILS PAR COMPOSANT:{RESET}\n")

        # Services
        services_up = sum(1 for v in self.results["services"].values() if v == "UP")
        total_services = len(self.results["services"])
        print(f"  🚀 Services Docker: {services_up}/{total_services} UP")

        # Monitoring
        print(f"  📊 Monitoring:")
        print(f"     - Targets Prometheus: {self.results['monitoring'].get('prometheus_targets', 'N/A')}")
        print(f"     - Dashboards Grafana: {self.results['monitoring'].get('grafana_dashboards', 0)}")
        print(f"     - P95 Latency: {self.results['monitoring'].get('latency_P95', 0)*1000:.2f}ms" if 'latency_P95' in self.results['monitoring'] else "     - P95 Latency: N/A")

        # MLflow
        print(f"  🎯 MLflow:")
        print(f"     - Expérimentations: {self.results['mlflow'].get('experiments', 0)}")
        print(f"     - Modèles enregistrés: {self.results['mlflow'].get('models', 0)}")
        print(f"     - Runs: {self.results['mlflow'].get('runs', 0)}")

        # API
        print(f"  🔌 API:")
        print(f"     - Prédictions ML: {'✅' if self.results['predictions'].get('success') else '❌'}")
        print(f"     - Model Accuracy: {self.results['predictions'].get('model_accuracy', 0)*100:.2f}%" if 'model_accuracy' in self.results['predictions'] else "     - Model Accuracy: N/A")

        # Données
        print(f"  💾 Données:")
        print(f"     - Pokémon: {self.results['data'].get('pokemon_count', 0)}")
        print(f"     - Capacités: {self.results['data'].get('moves_count', 0)}")
        print(f"     - Types: {self.results['data'].get('types_count', 0)}")

        # Erreurs
        if self.results["errors"]:
            print(f"\n{RED}ERREURS DÉTECTÉES:{RESET}")
            for error in self.results["errors"][:10]:
                print(f"  • {error}")

        # Sauvegarder le rapport JSON
        report_dir = Path(__file__).parent.parent / "reports" / "validation"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / "system_validation_report.json"

        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n{CYAN}💾 Rapport détaillé: {report_file}{RESET}")

        # Liens utiles
        print(f"\n{CYAN}🔗 LIENS UTILES:{RESET}")
        print(f"  • API Docs: http://localhost:8080/docs")
        print(f"  • MLflow UI: http://localhost:5001")
        print(f"  • Grafana: http://localhost:3001 (admin/admin)")
        print(f"  • Prometheus: http://localhost:9091")
        print(f"  • Streamlit: http://localhost:8502")
        print(f"  • pgAdmin: http://localhost:5050 (admin@predictiondex.com/admin)")

        return score_pct >= 85

def main():
    tester = SystemTester()

    try:
        # Phase 1: Services
        if not tester.test_all_services():
            print(f"\n{RED}❌ Services non disponibles. Arrêt des tests.{RESET}")
            return 1

        # Phase 2: Monitoring
        tester.test_monitoring_stack()

        # Phase 3: MLflow
        tester.test_mlflow_stack()

        # Phase 4: API
        tester.test_api_endpoints()

        # Phase 5: Données
        tester.test_data_availability()

        # Rapport final
        success = tester.generate_final_report()

        return 0 if success else 1

    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Tests interrompus{RESET}")
        return 130
    except Exception as e:
        print(f"\n{RED}❌ Erreur fatale: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
