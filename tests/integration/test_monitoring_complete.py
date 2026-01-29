#!/usr/bin/env python3
"""
Test d'intégration du monitoring - Valide le fonctionnement réel
Génère du trafic API et vérifie que les métriques sont correctement collectées
"""
import os
import sys
import time
import requests
from typing import Dict, List, Optional
from pathlib import Path
import json

# Couleurs pour affichage terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Configuration
API_URL = "http://localhost:8080"
PROMETHEUS_URL = "http://localhost:9091"
GRAFANA_URL = "http://localhost:3001"

# Charger l'API key depuis .env
def load_api_key() -> Optional[str]:
    """Charge l'API key depuis le fichier .env"""
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("API_KEYS="):
                    keys = line.split("=", 1)[1].strip().strip('"')
                    return keys.split(",")[0] if keys else None
    return os.getenv("API_KEYS", "").split(",")[0] if os.getenv("API_KEYS") else None

API_KEY = load_api_key()
API_HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

class MonitoringTester:
    def __init__(self):
        self.results = {
            "api_traffic": {"success": 0, "errors": 0},
            "metrics_collected": {},
            "prometheus_queries": {},
            "percentiles_ok": {},
            "errors": []
        }

    def print_section(self, title: str):
        """Affiche un titre de section"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}{title:^80}{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")

    def print_success(self, message: str):
        """Affiche un message de succès"""
        print(f"{GREEN}✅ {message}{RESET}")

    def print_error(self, message: str):
        """Affiche un message d'erreur"""
        print(f"{RED}❌ {message}{RESET}")
        self.results["errors"].append(message)

    def print_warning(self, message: str):
        """Affiche un avertissement"""
        print(f"{YELLOW}⚠️  {message}{RESET}")

    def print_info(self, message: str):
        """Affiche une information"""
        print(f"   {message}")

    def check_services_health(self) -> bool:
        """Vérifie que tous les services sont up"""
        self.print_section("ÉTAPE 1: Vérification des services")

        services = {
            "API": f"{API_URL}/health",
            "Prometheus": f"{PROMETHEUS_URL}/-/healthy",
            "Grafana": f"{GRAFANA_URL}/api/health"
        }

        all_up = True
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.print_success(f"{service} est UP (HTTP {response.status_code})")
                else:
                    self.print_error(f"{service} retourne HTTP {response.status_code}")
                    all_up = False
            except Exception as e:
                self.print_error(f"{service} non accessible: {e}")
                all_up = False

        return all_up

    def generate_api_traffic(self, num_requests: int = 50) -> bool:
        """Génère du trafic vers l'API pour produire des métriques"""
        self.print_section("ÉTAPE 2: Génération de trafic API")

        self.print_info(f"Envoi de {num_requests} requêtes vers différents endpoints...")

        # Endpoints à tester
        endpoints = [
            ("/health", "GET"),
            ("/pokemon/1", "GET"),
            ("/pokemon/25", "GET"),
            ("/pokemon/6", "GET"),
            ("/moves/", "GET"),
            ("/types/", "GET"),
        ]

        # Ajouter des prédictions si possible
        prediction_payload = {
            "pokemon_a_id": 1,
            "pokemon_b_id": 25,
            "available_moves": [1, 2, 3, 4]
        }

        success_count = 0
        error_count = 0

        for i in range(num_requests):
            # Alterner entre différents endpoints
            if i % 7 == 0:
                # Prédiction
                try:
                    resp = requests.post(
                        f"{API_URL}/predict/best-move",
                        json=prediction_payload,
                        headers=API_HEADERS,
                        timeout=5
                    )
                    if resp.status_code in [200, 404, 422]:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    error_count += 1
            else:
                # Endpoints GET
                endpoint, method = endpoints[i % len(endpoints)]
                try:
                    resp = requests.get(
                        f"{API_URL}{endpoint}",
                        headers=API_HEADERS,
                        timeout=5
                    )
                    if resp.status_code in [200, 404]:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    error_count += 1

            # Petit délai entre requêtes
            if i % 10 == 0:
                time.sleep(0.1)

        self.results["api_traffic"]["success"] = success_count
        self.results["api_traffic"]["errors"] = error_count

        self.print_success(f"Trafic généré: {success_count} succès, {error_count} erreurs")
        self.print_info(f"Attente de 15 secondes pour que Prometheus scrape les métriques...")
        time.sleep(15)

        return success_count > 0

    def check_metrics_exposed(self) -> bool:
        """Vérifie que les métriques sont exposées sur /metrics"""
        self.print_section("ÉTAPE 3: Vérification des métriques exposées")

        try:
            response = requests.get(f"{API_URL}/metrics", timeout=5)
            if response.status_code != 200:
                self.print_error(f"Endpoint /metrics retourne HTTP {response.status_code}")
                return False

            metrics_text = response.text

            # Métriques critiques à vérifier
            critical_metrics = [
                "api_requests_total",
                "api_request_duration_seconds_bucket",
                "api_request_duration_seconds_count",
                "api_request_duration_seconds_sum",
                "model_predictions_total",
                "model_prediction_duration_seconds_bucket",
                "system_cpu_usage",
                "system_memory_usage"
            ]

            found_metrics = []
            missing_metrics = []

            for metric in critical_metrics:
                if metric in metrics_text:
                    found_metrics.append(metric)
                    # Extraire quelques valeurs pour vérification
                    lines = [line for line in metrics_text.split('\n') if metric in line and not line.startswith('#')]
                    if lines:
                        self.print_success(f"{metric}: {len(lines)} séries trouvées")
                        self.results["metrics_collected"][metric] = len(lines)
                    else:
                        self.print_warning(f"{metric}: métrique présente mais aucune série avec données")
                else:
                    missing_metrics.append(metric)
                    self.print_error(f"{metric}: ABSENTE")

            if missing_metrics:
                self.print_error(f"Métriques manquantes: {', '.join(missing_metrics)}")
                return False

            return True

        except Exception as e:
            self.print_error(f"Erreur lors de la vérification des métriques: {e}")
            return False

    def test_prometheus_queries(self) -> bool:
        """Test les requêtes Prometheus pour vérifier les données collectées"""
        self.print_section("ÉTAPE 4: Test des requêtes Prometheus")

        # Requêtes PromQL à tester
        queries = {
            "histogram_buckets_exist": "api_request_duration_seconds_bucket",
            "rate_works": "rate(api_request_duration_seconds_bucket[2m])",
            "sum_by_le": "sum(rate(api_request_duration_seconds_bucket[2m])) by (le)",
            "p50_simple": "histogram_quantile(0.50, sum(rate(api_request_duration_seconds_bucket[2m])) by (le))",
            "p95_simple": "histogram_quantile(0.95, sum(rate(api_request_duration_seconds_bucket[2m])) by (le))",
            "p99_simple": "histogram_quantile(0.99, sum(rate(api_request_duration_seconds_bucket[2m])) by (le))",
            "prediction_count": "model_predictions_total",
            "request_count": "api_requests_total",
        }

        all_ok = True

        for query_name, query in queries.items():
            try:
                response = requests.get(
                    f"{PROMETHEUS_URL}/api/v1/query",
                    params={"query": query},
                    timeout=10
                )

                if response.status_code != 200:
                    self.print_error(f"{query_name}: HTTP {response.status_code}")
                    self.results["prometheus_queries"][query_name] = "HTTP_ERROR"
                    all_ok = False
                    continue

                data = response.json()

                if data.get("status") != "success":
                    self.print_error(f"{query_name}: Status non-success")
                    self.results["prometheus_queries"][query_name] = "QUERY_ERROR"
                    all_ok = False
                    continue

                result = data.get("data", {}).get("result", [])

                if not result:
                    self.print_warning(f"{query_name}: Aucun résultat (peut être normal si pas assez de données)")
                    self.results["prometheus_queries"][query_name] = "NO_DATA"
                else:
                    # Vérifier la valeur
                    value = result[0].get("value", [None, None])[1]

                    if value is None or value == "NaN":
                        self.print_error(f"{query_name}: Valeur NaN")
                        self.results["prometheus_queries"][query_name] = "NaN"
                        all_ok = False
                    else:
                        self.print_success(f"{query_name}: Valeur = {value}")
                        self.results["prometheus_queries"][query_name] = value

                        # Pour les percentiles, vérifier que la valeur est plausible
                        if query_name.startswith("p"):
                            try:
                                val_float = float(value)
                                if 0 <= val_float <= 100:
                                    self.results["percentiles_ok"][query_name] = True
                                else:
                                    self.print_warning(f"{query_name}: Valeur hors plage normale (0-100s): {val_float}")
                            except ValueError:
                                pass

            except Exception as e:
                self.print_error(f"{query_name}: Exception - {e}")
                self.results["prometheus_queries"][query_name] = f"EXCEPTION: {e}"
                all_ok = False

        return all_ok

    def test_histogram_quantiles_detailed(self) -> bool:
        """Test détaillé des percentiles histogram"""
        self.print_section("ÉTAPE 5: Test détaillé des percentiles")

        # Test avec différentes configurations
        test_configs = [
            {
                "name": "Sans groupement (BROKEN)",
                "query": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[2m]))"
            },
            {
                "name": "Avec sum by (le) - CORRECT",
                "query": "histogram_quantile(0.95, sum(rate(api_request_duration_seconds_bucket[2m])) by (le))"
            },
            {
                "name": "Avec endpoint grouping",
                "query": "histogram_quantile(0.95, sum(rate(api_request_duration_seconds_bucket[2m])) by (le, endpoint))"
            },
            {
                "name": "Fenêtre 1m",
                "query": "histogram_quantile(0.95, sum(rate(api_request_duration_seconds_bucket[1m])) by (le))"
            },
            {
                "name": "Fenêtre 5m",
                "query": "histogram_quantile(0.95, sum(rate(api_request_duration_seconds_bucket[5m])) by (le))"
            }
        ]

        results_summary = []

        for config in test_configs:
            try:
                response = requests.get(
                    f"{PROMETHEUS_URL}/api/v1/query",
                    params={"query": config["query"]},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    result = data.get("data", {}).get("result", [])

                    if result:
                        value = result[0].get("value", [None, None])[1]
                        if value and value != "NaN":
                            self.print_success(f"{config['name']}: ✅ Valeur = {value}")
                            results_summary.append((config['name'], "OK", value))
                        else:
                            self.print_error(f"{config['name']}: ❌ NaN")
                            results_summary.append((config['name'], "NaN", None))
                    else:
                        self.print_warning(f"{config['name']}: ⚠️  NO DATA")
                        results_summary.append((config['name'], "NO_DATA", None))
                else:
                    self.print_error(f"{config['name']}: ❌ HTTP {response.status_code}")
                    results_summary.append((config['name'], "HTTP_ERROR", None))

            except Exception as e:
                self.print_error(f"{config['name']}: ❌ {e}")
                results_summary.append((config['name'], "ERROR", str(e)))

        # Résumé
        self.print_info("\n📊 RÉSUMÉ DES TESTS:")
        for name, status, value in results_summary:
            status_symbol = "✅" if status == "OK" else "❌" if status in ["NaN", "ERROR", "HTTP_ERROR"] else "⚠️"
            self.print_info(f"  {status_symbol} {name}: {status} {f'({value})' if value else ''}")

        return any(status == "OK" for _, status, _ in results_summary)

    def check_grafana_dashboards(self) -> bool:
        """Vérifie l'accessibilité des dashboards Grafana"""
        self.print_section("ÉTAPE 6: Vérification Grafana")

        try:
            # Vérifier datasource
            response = requests.get(
                f"{GRAFANA_URL}/api/datasources",
                auth=("admin", "admin"),
                timeout=5
            )

            if response.status_code == 200:
                datasources = response.json()
                prom_ds = [ds for ds in datasources if ds.get("type") == "prometheus"]
                if prom_ds:
                    self.print_success(f"Datasource Prometheus configurée: {prom_ds[0].get('name')}")
                else:
                    self.print_error("Aucune datasource Prometheus trouvée")
                    return False
            else:
                self.print_warning(f"Impossible de vérifier les datasources (HTTP {response.status_code})")

            # Vérifier dashboards
            response = requests.get(
                f"{GRAFANA_URL}/api/search?type=dash-db",
                auth=("admin", "admin"),
                timeout=5
            )

            if response.status_code == 200:
                dashboards = response.json()
                self.print_success(f"{len(dashboards)} dashboard(s) trouvé(s)")
                for dash in dashboards:
                    self.print_info(f"  - {dash.get('title')} (uid: {dash.get('uid')})")
            else:
                self.print_warning(f"Impossible de lister les dashboards (HTTP {response.status_code})")

            return True

        except Exception as e:
            self.print_error(f"Erreur lors de la vérification Grafana: {e}")
            return False

    def generate_report(self):
        """Génère le rapport final"""
        self.print_section("RAPPORT FINAL")

        # Calcul du score
        total_checks = 0
        passed_checks = 0

        # Services
        total_checks += 1
        if self.results["api_traffic"]["success"] > 0:
            passed_checks += 1

        # Métriques collectées
        total_checks += len(self.results["metrics_collected"])
        passed_checks += len([v for v in self.results["metrics_collected"].values() if v > 0])

        # Requêtes Prometheus
        total_checks += len(self.results["prometheus_queries"])
        passed_checks += len([v for v in self.results["prometheus_queries"].values()
                             if v not in ["NO_DATA", "NaN", "HTTP_ERROR", "QUERY_ERROR"]
                             and not str(v).startswith("EXCEPTION")])

        # Percentiles
        total_checks += 3  # P50, P95, P99
        passed_checks += len(self.results["percentiles_ok"])

        score_pct = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        print(f"\n📊 SCORE GLOBAL: {passed_checks}/{total_checks} ({score_pct:.1f}%)")

        if score_pct >= 80:
            self.print_success("✅ MONITORING FONCTIONNEL")
        elif score_pct >= 60:
            self.print_warning("⚠️  MONITORING PARTIELLEMENT FONCTIONNEL")
        else:
            self.print_error("❌ MONITORING DÉFAILLANT")

        # Détails
        print(f"\n📋 DÉTAILS:")
        print(f"  - Trafic API: {self.results['api_traffic']['success']} requêtes réussies")
        print(f"  - Métriques collectées: {len([v for v in self.results['metrics_collected'].values() if v > 0])}/{len(self.results['metrics_collected'])}")
        print(f"  - Requêtes Prometheus OK: {passed_checks - len(self.results['percentiles_ok'])}/{len(self.results['prometheus_queries'])}")
        print(f"  - Percentiles calculables: {len(self.results['percentiles_ok'])}/3")

        # Erreurs
        if self.results["errors"]:
            print(f"\n❌ ERREURS DÉTECTÉES ({len(self.results['errors'])}):")
            for error in self.results["errors"][:10]:
                print(f"  - {error}")
            if len(self.results["errors"]) > 10:
                print(f"  ... et {len(self.results['errors']) - 10} autres erreurs")

        # Sauvegarder résultats JSON
        report_dir = Path(__file__).parent.parent.parent / "reports" / "monitoring"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / "integration_test_results.json"

        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        self.print_info(f"\n💾 Rapport détaillé sauvegardé: {report_file}")

        return score_pct >= 80

def main():
    """Fonction principale"""
    title = "TEST D'INTÉGRATION MONITORING"
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{title:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    tester = MonitoringTester()

    try:
        # Étape 1: Vérifier services
        if not tester.check_services_health():
            print(f"\n{RED}❌ Services non disponibles. Arrêt du test.{RESET}")
            return 1

        # Étape 2: Générer trafic
        if not tester.generate_api_traffic(num_requests=100):
            print(f"\n{RED}❌ Impossible de générer du trafic. Arrêt du test.{RESET}")
            return 1

        # Étape 3: Vérifier métriques exposées
        if not tester.check_metrics_exposed():
            print(f"\n{RED}❌ Métriques non exposées correctement.{RESET}")
            # Continue quand même pour voir ce qui ne va pas

        # Étape 4: Test requêtes Prometheus
        tester.test_prometheus_queries()

        # Étape 5: Test détaillé percentiles
        tester.test_histogram_quantiles_detailed()

        # Étape 6: Vérifier Grafana
        tester.check_grafana_dashboards()

        # Rapport final
        success = tester.generate_report()

        return 0 if success else 1

    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Test interrompu par l'utilisateur{RESET}")
        return 130
    except Exception as e:
        print(f"\n{RED}❌ Erreur fatale: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
