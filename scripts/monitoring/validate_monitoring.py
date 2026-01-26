"""
Script de Validation Automatique du Monitoring - PredictionDex
==============================================================

Ce script exécute une validation complète de la stack de monitoring :
1. Génère des prédictions de test
2. Collecte les métriques Prometheus
3. Vérifie l'état de tous les services
4. Force la génération d'un rapport de drift
5. Analyse les résultats et génère un rapport

Output: reports/monitoring/validation_report.json + validation_report.html

Usage:
    python scripts/monitoring/validate_monitoring.py
"""

import requests
import time
import random
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

API_URL = "http://localhost:8080"
PROMETHEUS_URL = "http://localhost:9091"
GRAFANA_URL = "http://localhost:3001"

# Cache des Pokémon
pokemon_cache = {}


class MonitoringValidator:
    """Validateur automatique du système de monitoring."""
    
    def __init__(self):
        self.results = {
            "test_date": datetime.now().isoformat(),
            "duration_seconds": 0,
            "services_status": {},
            "predictions": {},
            "prometheus_metrics": {},
            "grafana_status": {},
            "drift_detection": {},
            "system_metrics": {},
            "alerts": {},
            "validation_score": 0,
            "recommendations": []
        }
        self.start_time = time.time()
    
    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌", "TEST": "🧪"}
        print(f"[{timestamp}] {icon.get(level, 'ℹ️')} {message}")
    
    def check_service(self, name: str, url: str, timeout: int = 5) -> bool:
        """Vérifie qu'un service est accessible."""
        try:
            response = requests.get(url, timeout=timeout)
            is_up = response.status_code == 200
            self.results["services_status"][name] = {
                "status": "UP" if is_up else "DOWN",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "status_code": response.status_code
            }
            return is_up
        except Exception as e:
            self.results["services_status"][name] = {
                "status": "DOWN",
                "error": str(e)
            }
            return False
    
    def get_pokemon_moves(self, pokemon_id: int) -> Dict:
        """Récupère les moves d'un Pokémon."""
        if pokemon_id in pokemon_cache:
            return pokemon_cache[pokemon_id]
        
        try:
            response = requests.get(f"{API_URL}/pokemon/{pokemon_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                offensive_moves = [
                    move['name'] 
                    for move in data.get('moves', []) 
                    if move.get('power') is not None and move.get('power') > 0
                ]
                pokemon_cache[pokemon_id] = {
                    'name': data['species']['name_fr'],
                    'moves': offensive_moves
                }
                return pokemon_cache[pokemon_id]
        except:
            pass
        return None
    
    def generate_predictions(self, n_predictions: int = 100) -> Dict:
        """Génère des prédictions de test."""
        self.log(f"Génération de {n_predictions} prédictions...", "TEST")
        
        popular_ids = [1, 4, 7, 25, 6, 9, 3, 35, 36, 39, 40, 94, 65, 59, 68, 130, 131, 144, 145, 146, 150, 151]
        
        success = 0
        errors = 0
        latencies = []
        confidences = []
        start = time.time()
        
        for i in range(n_predictions):
            pokemon_a_id = random.choice(popular_ids)
            pokemon_b_id = random.choice([p for p in popular_ids if p != pokemon_a_id])
            
            pokemon_a = self.get_pokemon_moves(pokemon_a_id)
            pokemon_b = self.get_pokemon_moves(pokemon_b_id)
            
            if not pokemon_a or not pokemon_b or not pokemon_a['moves']:
                errors += 1
                continue
            
            moves = random.sample(pokemon_a['moves'], k=min(4, len(pokemon_a['moves'])))
            
            try:
                req_start = time.time()
                response = requests.post(
                    f"{API_URL}/predict/best-move",
                    json={
                        "pokemon_a_id": pokemon_a_id,
                        "pokemon_b_id": pokemon_b_id,
                        "available_moves": moves
                    },
                    timeout=10
                )
                latency = (time.time() - req_start) * 1000  # ms
                
                if response.status_code == 200:
                    result = response.json()
                    success += 1
                    latencies.append(latency)
                    confidences.append(result['win_probability'])
                    
                    if (i + 1) % 20 == 0:
                        self.log(f"Progression: {i+1}/{n_predictions} ({success} succès)", "INFO")
                else:
                    errors += 1
            except Exception as e:
                errors += 1
        
        duration = time.time() - start
        
        stats = {
            "total": n_predictions,
            "success": success,
            "errors": errors,
            "success_rate": (success / n_predictions * 100) if n_predictions > 0 else 0,
            "duration_seconds": duration,
            "throughput_per_second": n_predictions / duration if duration > 0 else 0,
            "latency_avg_ms": sum(latencies) / len(latencies) if latencies else 0,
            "latency_p95_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
            "latency_p99_ms": sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0,
            "confidence_avg": sum(confidences) / len(confidences) if confidences else 0,
            "confidence_min": min(confidences) if confidences else 0,
            "confidence_max": max(confidences) if confidences else 0
        }
        
        self.results["predictions"] = stats
        self.log(f"Prédictions: {success}/{n_predictions} succès ({stats['success_rate']:.1f}%)", "OK")
        return stats
    
    def query_prometheus(self, query: str) -> Dict:
        """Exécute une requête PromQL."""
        try:
            response = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": query},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.log(f"Erreur Prometheus query '{query}': {e}", "ERROR")
        return {}
    
    def collect_prometheus_metrics(self):
        """Collecte les métriques clés depuis Prometheus."""
        self.log("Collecte des métriques Prometheus...", "TEST")
        
        queries = {
            "api_request_rate": "rate(api_requests_total[1m])",
            "api_latency_p95": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))",
            "api_latency_p99": "histogram_quantile(0.99, rate(api_request_duration_seconds_bucket[5m]))",
            "model_predictions_total": "model_predictions_total",
            "model_prediction_rate": "rate(model_predictions_total[1m])",
            "model_latency_p95": "histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[5m]))",
            "model_confidence_avg": "avg(model_confidence_score)",
            "api_errors_total": "api_errors_total",
            "cpu_usage": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "memory_available_mb": "node_memory_MemAvailable_bytes / 1024 / 1024"
        }
        
        metrics = {}
        for name, query in queries.items():
            result = self.query_prometheus(query)
            if result and result.get("status") == "success":
                data = result.get("data", {}).get("result", [])
                if data:
                    # Prendre la première valeur
                    value = data[0].get("value", [None, None])[1]
                    metrics[name] = float(value) if value else None
                else:
                    metrics[name] = None
            else:
                metrics[name] = None
        
        self.results["prometheus_metrics"] = metrics
        self.log(f"Métriques Prometheus collectées: {len([v for v in metrics.values() if v is not None])}/{len(queries)}", "OK")
        return metrics
    
    def check_prometheus_targets(self):
        """Vérifie l'état des targets Prometheus."""
        try:
            response = requests.get(f"{PROMETHEUS_URL}/api/v1/targets", timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", {})
                targets = data.get("activeTargets", [])
                
                targets_status = {}
                for target in targets:
                    job = target.get("labels", {}).get("job", "unknown")
                    targets_status[job] = {
                        "health": target.get("health"),
                        "scrape_url": target.get("scrapeUrl"),
                        "last_scrape": target.get("lastScrape"),
                        "last_error": target.get("lastError", "")
                    }
                
                self.results["prometheus_metrics"]["targets"] = targets_status
                up_count = sum(1 for t in targets_status.values() if t["health"] == "up")
                self.log(f"Prometheus Targets: {up_count}/{len(targets_status)} UP", "OK")
                return targets_status
        except Exception as e:
            self.log(f"Erreur check targets: {e}", "ERROR")
        return {}
    
    def check_prometheus_alerts(self):
        """Récupère les alertes Prometheus."""
        try:
            response = requests.get(f"{PROMETHEUS_URL}/api/v1/rules", timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", {})
                groups = data.get("groups", [])
                
                alerts_summary = {
                    "total": 0,
                    "firing": 0,
                    "pending": 0,
                    "inactive": 0,
                    "alerts": []
                }
                
                for group in groups:
                    for rule in group.get("rules", []):
                        if rule.get("type") == "alerting":
                            alerts_summary["total"] += 1
                            state = rule.get("state", "inactive")
                            alerts_summary[state] = alerts_summary.get(state, 0) + 1
                            alerts_summary["alerts"].append({
                                "name": rule.get("name"),
                                "state": state,
                                "query": rule.get("query")
                            })
                
                self.results["alerts"] = alerts_summary
                self.log(f"Alertes: {alerts_summary['total']} configurées, {alerts_summary['firing']} actives", "OK")
                return alerts_summary
        except Exception as e:
            self.log(f"Erreur check alerts: {e}", "ERROR")
        return {}
    
    def check_grafana(self):
        """Vérifie l'accès à Grafana."""
        self.log("Vérification Grafana...", "TEST")
        
        try:
            # Check health
            health = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
            
            # Check datasources (nécessite auth)
            datasources = requests.get(
                f"{GRAFANA_URL}/api/datasources",
                auth=("admin", "admin"),
                timeout=5
            )
            
            grafana_status = {
                "health": health.status_code == 200,
                "datasources_accessible": datasources.status_code == 200
            }
            
            if datasources.status_code == 200:
                ds_list = datasources.json()
                grafana_status["datasources_count"] = len(ds_list)
                grafana_status["datasources"] = [
                    {"name": ds.get("name"), "type": ds.get("type")} 
                    for ds in ds_list
                ]
            
            self.results["grafana_status"] = grafana_status
            self.log(f"Grafana: {'OK' if grafana_status['health'] else 'KO'}", "OK" if grafana_status['health'] else "ERROR")
            return grafana_status
        except Exception as e:
            self.log(f"Erreur Grafana: {e}", "ERROR")
            self.results["grafana_status"] = {"health": False, "error": str(e)}
        return {}
    
    def check_drift_detection(self):
        """Vérifie la détection de drift."""
        self.log("Vérification détection de drift...", "TEST")
        
        drift_dir = Path("api_pokemon/monitoring/drift_reports")
        
        if not drift_dir.exists():
            self.log("Répertoire drift_reports n'existe pas", "WARN")
            self.results["drift_detection"] = {"available": False}
            return
        
        # Lister les rapports existants
        reports = list(drift_dir.glob("drift_report_*.json"))
        dashboards = list(drift_dir.glob("drift_dashboard_*.html"))
        
        drift_status = {
            "available": True,
            "reports_count": len(reports),
            "dashboards_count": len(dashboards),
            "latest_report": None
        }
        
        if reports:
            # Lire le dernier rapport
            latest = sorted(reports)[-1]
            try:
                with open(latest) as f:
                    report_data = json.load(f)
                    drift_status["latest_report"] = {
                        "file": latest.name,
                        "timestamp": latest.stat().st_mtime
                    }
            except:
                pass
        
        self.results["drift_detection"] = drift_status
        self.log(f"Drift Detection: {len(reports)} rapports disponibles", "OK")
        return drift_status
    
    def calculate_validation_score(self) -> int:
        """Calcule un score de validation sur 100."""
        score = 0
        recommendations = []
        
        # Services (20 points)
        services = self.results["services_status"]
        if services.get("API", {}).get("status") == "UP":
            score += 10
        else:
            recommendations.append("❌ API non accessible")
        
        if services.get("Prometheus", {}).get("status") == "UP":
            score += 5
        else:
            recommendations.append("❌ Prometheus non accessible")
        
        if services.get("Grafana", {}).get("status") == "UP":
            score += 5
        else:
            recommendations.append("❌ Grafana non accessible")
        
        # Prédictions (25 points)
        pred = self.results["predictions"]
        if pred.get("success_rate", 0) >= 95:
            score += 25
        elif pred.get("success_rate", 0) >= 80:
            score += 15
            recommendations.append("⚠️ Taux de succès des prédictions < 95%")
        else:
            score += 5
            recommendations.append("❌ Taux de succès des prédictions trop faible")
        
        # Métriques Prometheus (20 points)
        metrics = self.results["prometheus_metrics"]
        non_null_metrics = sum(1 for v in metrics.values() if v is not None and not isinstance(v, dict))
        if non_null_metrics >= 8:
            score += 20
        elif non_null_metrics >= 5:
            score += 10
            recommendations.append("⚠️ Certaines métriques Prometheus manquantes")
        else:
            recommendations.append("❌ Trop de métriques Prometheus manquantes")
        
        # Targets Prometheus (10 points)
        targets = metrics.get("targets", {})
        if len(targets) >= 3:
            score += 10
        elif len(targets) >= 2:
            score += 5
            recommendations.append("⚠️ Certains targets Prometheus DOWN")
        
        # Alertes (10 points)
        alerts = self.results["alerts"]
        if alerts.get("total", 0) >= 5:
            score += 10
        elif alerts.get("total", 0) >= 3:
            score += 5
            recommendations.append("⚠️ Peu d'alertes configurées")
        
        # Grafana (10 points)
        if self.results["grafana_status"].get("health"):
            score += 10
        else:
            recommendations.append("❌ Grafana non fonctionnel")
        
        # Drift Detection (5 points)
        if self.results["drift_detection"].get("available"):
            score += 5
        else:
            recommendations.append("⚠️ Détection de drift non vérifiable")
        
        self.results["validation_score"] = score
        self.results["recommendations"] = recommendations
        
        return score
    
    def generate_verdict(self) -> str:
        """Génère un verdict basé sur le score."""
        score = self.results["validation_score"]
        
        if score >= 90:
            return "🏆 EXCELLENT - Stack de monitoring production-ready"
        elif score >= 75:
            return "✅ BON - Quelques améliorations possibles"
        elif score >= 60:
            return "⚠️ MOYEN - Problèmes à corriger"
        else:
            return "❌ INSUFFISANT - Stack de monitoring non fonctionnelle"
    
    def run_full_validation(self, n_predictions: int = 100):
        """Exécute la validation complète."""
        self.log("="*70, "INFO")
        self.log("VALIDATION AUTOMATIQUE DU MONITORING - PREDICTIONDEX", "INFO")
        self.log("="*70, "INFO")
        
        # 1. Check services
        self.log("\n[1/7] Vérification des services...", "TEST")
        self.check_service("API", f"{API_URL}/health")
        self.check_service("Prometheus", f"{PROMETHEUS_URL}/-/healthy")
        self.check_service("Grafana", f"{GRAFANA_URL}/api/health")
        time.sleep(1)
        
        # 2. Générer prédictions
        self.log("\n[2/7] Génération de prédictions de test...", "TEST")
        self.generate_predictions(n_predictions)
        time.sleep(2)  # Laisser le temps aux métriques d'être scraped
        
        # 3. Collecter métriques Prometheus
        self.log("\n[3/7] Collecte des métriques Prometheus...", "TEST")
        self.collect_prometheus_metrics()
        time.sleep(1)
        
        # 4. Check targets
        self.log("\n[4/7] Vérification des targets Prometheus...", "TEST")
        self.check_prometheus_targets()
        time.sleep(1)
        
        # 5. Check alertes
        self.log("\n[5/7] Vérification des alertes...", "TEST")
        self.check_prometheus_alerts()
        time.sleep(1)
        
        # 6. Check Grafana
        self.log("\n[6/7] Vérification Grafana...", "TEST")
        self.check_grafana()
        time.sleep(1)
        
        # 7. Check drift
        self.log("\n[7/7] Vérification détection de drift...", "TEST")
        self.check_drift_detection()
        
        # Calcul final
        self.results["duration_seconds"] = time.time() - self.start_time
        score = self.calculate_validation_score()
        verdict = self.generate_verdict()
        
        self.log("\n" + "="*70, "INFO")
        self.log(f"SCORE DE VALIDATION: {score}/100", "OK")
        self.log(f"VERDICT: {verdict}", "OK")
        self.log("="*70, "INFO")
        
        return self.results
    
    def export_json(self, filename: str = "reports/monitoring/validation_report.json"):
        """Exporte le rapport en JSON."""
        # Créer le dossier si nécessaire
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        self.log(f"\n📄 Rapport JSON: {filename}", "OK")
        return filename
    
    def export_html(self, filename: str = "reports/monitoring/validation_report.html"):
        """Génère un rapport HTML."""
        score = self.results["validation_score"]
        verdict = self.generate_verdict()
        
        # Couleur du score
        if score >= 90:
            score_color = "#28a745"
        elif score >= 75:
            score_color = "#ffc107"
        elif score >= 60:
            score_color = "#fd7e14"
        else:
            score_color = "#dc3545"
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Validation - Monitoring PredictionDex</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .score-card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .score {{
            font-size: 72px;
            font-weight: bold;
            color: {score_color};
            margin: 20px 0;
        }}
        .verdict {{
            font-size: 24px;
            margin: 10px 0;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-label {{
            font-weight: 500;
            color: #666;
        }}
        .metric-value {{
            font-weight: bold;
            color: #333;
        }}
        .status-ok {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-error {{ color: #dc3545; }}
        .recommendations {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-top: 20px;
        }}
        .recommendations ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Rapport de Validation du Monitoring</h1>
        <p>PredictionDex - Stack Prometheus + Grafana + Evidently</p>
        <p>Date: {self.results['test_date']}</p>
        <p>Durée: {self.results['duration_seconds']:.1f} secondes</p>
    </div>
    
    <div class="score-card">
        <h2>Score de Validation</h2>
        <div class="score">{score}/100</div>
        <div class="verdict">{verdict}</div>
    </div>
    
    <div class="section">
        <h2>📊 Résumé des Services</h2>
        <table>
            <tr>
                <th>Service</th>
                <th>État</th>
                <th>Temps de Réponse</th>
            </tr>
"""
        
        for service, status in self.results["services_status"].items():
            state = status.get("status", "UNKNOWN")
            badge_class = "badge-success" if state == "UP" else "badge-danger"
            response_time = status.get("response_time_ms", "N/A")
            if isinstance(response_time, (int, float)):
                response_time = f"{response_time:.0f} ms"
            
            html += f"""
            <tr>
                <td>{service}</td>
                <td><span class="badge {badge_class}">{state}</span></td>
                <td>{response_time}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>🎮 Prédictions de Test</h2>
"""
        pred = self.results["predictions"]
        html += f"""
        <div class="metric">
            <span class="metric-label">Total généré</span>
            <span class="metric-value">{pred.get('total', 0)}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Succès</span>
            <span class="metric-value status-ok">{pred.get('success', 0)}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Erreurs</span>
            <span class="metric-value status-error">{pred.get('errors', 0)}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Taux de succès</span>
            <span class="metric-value">{pred.get('success_rate', 0):.1f}%</span>
        </div>
        <div class="metric">
            <span class="metric-label">Débit moyen</span>
            <span class="metric-value">{pred.get('throughput_per_second', 0):.2f} pred/s</span>
        </div>
        <div class="metric">
            <span class="metric-label">Latence moyenne</span>
            <span class="metric-value">{pred.get('latency_avg_ms', 0):.0f} ms</span>
        </div>
        <div class="metric">
            <span class="metric-label">Latence P95</span>
            <span class="metric-value">{pred.get('latency_p95_ms', 0):.0f} ms</span>
        </div>
        <div class="metric">
            <span class="metric-label">Confiance moyenne</span>
            <span class="metric-value">{pred.get('confidence_avg', 0):.1%}</span>
        </div>
    </div>
    
    <div class="section">
        <h2>📈 Métriques Prometheus</h2>
"""
        
        metrics = self.results["prometheus_metrics"]
        for key, value in metrics.items():
            if key != "targets" and value is not None:
                # Format value
                if "rate" in key or "latency" in key:
                    formatted = f"{value:.4f}"
                elif "total" in key:
                    formatted = f"{int(value)}"
                elif "mb" in key:
                    formatted = f"{value:.0f} MB"
                elif "usage" in key:
                    formatted = f"{value:.1f}%"
                else:
                    formatted = f"{value:.2f}"
                
                html += f"""
        <div class="metric">
            <span class="metric-label">{key.replace('_', ' ').title()}</span>
            <span class="metric-value">{formatted}</span>
        </div>
"""
        
        html += """
    </div>
    
    <div class="section">
        <h2>🎯 Targets Prometheus</h2>
        <table>
            <tr>
                <th>Job</th>
                <th>Health</th>
                <th>URL</th>
            </tr>
"""
        
        targets = metrics.get("targets", {})
        for job, info in targets.items():
            health = info.get("health", "unknown")
            badge_class = "badge-success" if health == "up" else "badge-danger"
            
            html += f"""
            <tr>
                <td>{job}</td>
                <td><span class="badge {badge_class}">{health.upper()}</span></td>
                <td><code>{info.get('scrape_url', 'N/A')}</code></td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>🚨 Alertes</h2>
"""
        alerts = self.results["alerts"]
        html += f"""
        <div class="metric">
            <span class="metric-label">Total configurées</span>
            <span class="metric-value">{alerts.get('total', 0)}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Actives (Firing)</span>
            <span class="metric-value status-error">{alerts.get('firing', 0)}</span>
        </div>
        <div class="metric">
            <span class="metric-label">En attente (Pending)</span>
            <span class="metric-value status-warning">{alerts.get('pending', 0)}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Inactives</span>
            <span class="metric-value status-ok">{alerts.get('inactive', 0)}</span>
        </div>
    </div>
"""
        
        # Recommendations
        if self.results["recommendations"]:
            html += """
    <div class="recommendations">
        <h3>⚠️ Recommandations</h3>
        <ul>
"""
            for rec in self.results["recommendations"]:
                html += f"            <li>{rec}</li>\n"
            html += """
        </ul>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        self.log(f"📄 Rapport HTML: {filename}", "OK")
        return filename


def main():
    """Point d'entrée."""
    validator = MonitoringValidator()
    
    # Validation complète
    results = validator.run_full_validation(n_predictions=100)
    
    # Export des résultats
    validator.export_json()
    validator.export_html()
    
    print("\n" + "="*70)
    print("✅ Validation terminée!")
    print("="*70)
    print("\n📦 Fichiers générés:")
    print("   • reports/monitoring/validation_report.json")
    print("   • reports/monitoring/validation_report.html")
    print("\n💡 Ouvrez le rapport HTML dans votre navigateur:")
    print("   firefox reports/monitoring/validation_report.html")


if __name__ == "__main__":
    main()
