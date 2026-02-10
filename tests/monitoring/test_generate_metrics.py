#!/usr/bin/env python3
"""
Tests pour la génération de métriques Prometheus/Grafana
=========================================================

Ce module teste la génération de métriques pour remplir les dashboards
Grafana et valider l'infrastructure de monitoring.

Tests:
- Génération de prédictions (métriques ML)
- Stress test API (métriques performance)
- Validation endpoints Prometheus
- Vérification dashboards Grafana

Usage:
    pytest tests/monitoring/test_generate_metrics.py -v
    python tests/monitoring/test_generate_metrics.py  # Mode standalone
"""

import pytest
import requests
import time
import random
import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime


# Configuration
API_BASE_URL = "http://localhost:8080"
PROMETHEUS_URL = "http://localhost:9091"
GRAFANA_URL = "http://localhost:3001"


class TestMetricsGeneration:
    """Tests de génération de métriques pour monitoring."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup pour chaque test."""
        # Vérifier que l'API est accessible
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            assert response.status_code == 200, "API non disponible"
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API non accessible: {e}")
    
    def test_generate_prediction_metrics(self):
        """
        Test: Générer des métriques de prédiction
        
        Génère 100 prédictions avec différents Pokémon pour créer
        des métriques variées dans Prometheus/Grafana.
        """
        print("\n🎯 Génération de métriques de prédiction...")
        
        # Récupérer des Pokémon aléatoires
        response = requests.get(f"{API_BASE_URL}/pokemon?limit=50")
        assert response.status_code == 200
        pokemon_list = response.json()
        
        assert len(pokemon_list) > 10, "Pas assez de Pokémon dans la DB"
        
        # Générer des prédictions variées
        predictions_count = 100
        success_count = 0
        
        for i in range(predictions_count):
            # Sélectionner 2 Pokémon aléatoires
            poke1, poke2 = random.sample(pokemon_list, 2)
            
            payload = {
                "pokemon1_id": poke1["id"],
                "pokemon2_id": poke2["id"]
            }
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/predict/battle",
                    json=payload,
                    timeout=5
                )
                
                if response.status_code == 200:
                    success_count += 1
                    result = response.json()
                    
                    # Afficher quelques résultats
                    if i % 20 == 0:
                        winner = poke1["name"] if result["prediction"] == 0 else poke2["name"]
                        confidence = result["confidence"] * 100
                        print(f"   Prédiction {i+1}: {winner} gagne ({confidence:.1f}%)")
                
                # Pause pour éviter de surcharger
                if i % 10 == 0:
                    time.sleep(0.1)
                    
            except requests.exceptions.RequestException:
                pass
        
        print(f"✅ {success_count}/{predictions_count} prédictions générées")
        assert success_count > predictions_count * 0.9, "Trop d'échecs de prédiction"
    
    def test_generate_latency_metrics(self):
        """
        Test: Générer des métriques de latence variées
        
        Effectue des requêtes avec différents patterns pour créer
        des métriques de latence P50, P95, P99.
        """
        print("\n⏱️  Génération de métriques de latence...")
        
        latencies = []
        
        # Pattern 1: Requêtes rapides (GET simples)
        for i in range(50):
            start = time.time()
            response = requests.get(f"{API_BASE_URL}/pokemon?limit=10")
            latency = (time.time() - start) * 1000
            latencies.append(latency)
            
            if i % 10 == 0:
                print(f"   Requête rapide {i+1}: {latency:.2f}ms")
        
        # Pattern 2: Requêtes moyennes (prédictions)
        response = requests.get(f"{API_BASE_URL}/pokemon?limit=20")
        pokemon_list = response.json()
        
        for i in range(30):
            poke1, poke2 = random.sample(pokemon_list, 2)
            payload = {"pokemon1_id": poke1["id"], "pokemon2_id": poke2["id"]}
            
            start = time.time()
            response = requests.post(f"{API_BASE_URL}/predict/battle", json=payload)
            latency = (time.time() - start) * 1000
            latencies.append(latency)
            
            if i % 10 == 0:
                print(f"   Prédiction {i+1}: {latency:.2f}ms")
        
        # Calculer percentiles
        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        
        print(f"\n📊 Latences:")
        print(f"   P50: {p50:.2f}ms")
        print(f"   P95: {p95:.2f}ms")
        print(f"   P99: {p99:.2f}ms")
        
        assert p50 < 500, f"P50 trop élevé: {p50}ms"
        assert p99 < 2000, f"P99 trop élevé: {p99}ms"
    
    def test_generate_error_metrics(self):
        """
        Test: Générer des métriques d'erreur
        
        Effectue des requêtes invalides pour créer des métriques
        d'erreurs 4xx et 5xx.
        """
        print("\n❌ Génération de métriques d'erreur...")
        
        error_count = 0
        
        # Erreurs 404 (Pokémon inexistant)
        for i in range(10):
            response = requests.get(f"{API_BASE_URL}/pokemon/99999")
            if response.status_code == 404:
                error_count += 1
        
        # Erreurs 422 (Validation)
        for i in range(10):
            response = requests.post(
                f"{API_BASE_URL}/predict/battle",
                json={"pokemon1_id": -1, "pokemon2_id": -1}
            )
            if response.status_code == 422:
                error_count += 1
        
        print(f"✅ {error_count} erreurs générées (pour métriques)")
        assert error_count > 15, "Pas assez d'erreurs générées"
    
    def test_prometheus_metrics_endpoint(self):
        """
        Test: Vérifier que l'endpoint /metrics Prometheus fonctionne
        
        Valide que les métriques sont exposées correctement.
        """
        print("\n📊 Vérification endpoint Prometheus...")
        
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        assert response.status_code == 200, "Endpoint /metrics non accessible"
        
        metrics_text = response.text
        
        # Vérifier présence des métriques clés
        expected_metrics = [
            "prediction_total",
            "prediction_latency_seconds",
            "http_requests_total",
            "http_request_duration_seconds"
        ]
        
        found_metrics = []
        for metric in expected_metrics:
            if metric in metrics_text:
                found_metrics.append(metric)
                print(f"   ✅ {metric} présent")
            else:
                print(f"   ⚠️  {metric} absent")
        
        assert len(found_metrics) >= 2, f"Métriques manquantes: {expected_metrics}"
    
    def test_prometheus_query(self):
        """
        Test: Interroger Prometheus pour vérifier les métriques
        
        Effectue une query Prometheus pour valider que les données
        sont collectées correctement.
        """
        print("\n🔍 Interrogation Prometheus...")
        
        try:
            # Query: Nombre total de prédictions
            response = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": "prediction_total"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success" and data["data"]["result"]:
                    value = data["data"]["result"][0]["value"][1]
                    print(f"   ✅ prediction_total: {value}")
                else:
                    print("   ⚠️  Pas de données prediction_total encore")
            else:
                print(f"   ⚠️  Prometheus query failed: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Prometheus non accessible: {e}")
    
    def test_grafana_health(self):
        """
        Test: Vérifier que Grafana est accessible
        
        Valide que Grafana répond et peut afficher les dashboards.
        """
        print("\n📈 Vérification Grafana...")
        
        try:
            response = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Grafana: {data.get('database', 'unknown')} - {data.get('version', 'unknown')}")
            else:
                print(f"   ⚠️  Grafana health check failed: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Grafana non accessible: {e}")


class TestContinuousMetricsGeneration:
    """Générateur de métriques en continu (pour démo)."""
    
    def test_stress_test_realistic(self):
        """
        Test: Stress test réaliste avec métriques variées
        
        Simule un trafic utilisateur réaliste:
        - 70% prédictions
        - 20% consultations
        - 10% erreurs
        """
        print("\n🚀 Stress test réaliste (60s)...")
        
        duration = 60  # secondes
        start_time = time.time()
        
        stats = {
            "predictions": 0,
            "reads": 0,
            "errors": 0,
            "total": 0
        }
        
        # Récupérer des Pokémon pour le test
        response = requests.get(f"{API_BASE_URL}/pokemon?limit=50")
        if response.status_code != 200:
            pytest.skip("API non accessible pour stress test")
        
        pokemon_list = response.json()
        
        while time.time() - start_time < duration:
            stats["total"] += 1
            action = random.choices(
                ["predict", "read", "error"],
                weights=[70, 20, 10]
            )[0]
            
            try:
                if action == "predict":
                    # Prédiction
                    poke1, poke2 = random.sample(pokemon_list, 2)
                    response = requests.post(
                        f"{API_BASE_URL}/predict/battle",
                        json={"pokemon1_id": poke1["id"], "pokemon2_id": poke2["id"]},
                        timeout=5
                    )
                    if response.status_code == 200:
                        stats["predictions"] += 1
                
                elif action == "read":
                    # Lecture
                    poke = random.choice(pokemon_list)
                    response = requests.get(f"{API_BASE_URL}/pokemon/{poke['id']}")
                    if response.status_code == 200:
                        stats["reads"] += 1
                
                else:
                    # Erreur intentionnelle
                    response = requests.get(f"{API_BASE_URL}/pokemon/99999")
                    if response.status_code == 404:
                        stats["errors"] += 1
                
                # Afficher stats toutes les 10s
                elapsed = time.time() - start_time
                if int(elapsed) % 10 == 0 and stats["total"] % 10 == 0:
                    print(f"   [{int(elapsed)}s] Prédictions: {stats['predictions']}, "
                          f"Lectures: {stats['reads']}, Erreurs: {stats['errors']}")
                
                # Pause réaliste entre requêtes
                time.sleep(random.uniform(0.1, 0.5))
            
            except requests.exceptions.RequestException:
                pass
        
        print(f"\n✅ Stress test terminé:")
        print(f"   Total requêtes: {stats['total']}")
        print(f"   Prédictions: {stats['predictions']}")
        print(f"   Lectures: {stats['reads']}")
        print(f"   Erreurs: {stats['errors']}")
        
        assert stats["predictions"] > 50, "Pas assez de prédictions générées"


# ============================================================================
# Script standalone pour génération continue
# ============================================================================

def generate_metrics_continuous(duration_minutes: int = 5):
    """
    Génère des métriques en continu pour remplir Grafana.
    
    Args:
        duration_minutes: Durée de génération en minutes
    """
    print(f"\n🎯 Génération continue de métriques pendant {duration_minutes} minutes")
    print("=" * 70)
    
    duration = duration_minutes * 60
    start_time = time.time()
    
    # Récupérer des Pokémon
    try:
        response = requests.get(f"{API_BASE_URL}/pokemon?limit=100", timeout=10)
        pokemon_list = response.json()
        print(f"✅ {len(pokemon_list)} Pokémon chargés\n")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    stats = {
        "predictions": 0,
        "reads": 0,
        "errors": 0,
        "latencies": []
    }
    
    last_report = time.time()
    
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        
        # Générer requête aléatoire
        action = random.choices(
            ["predict", "read", "error"],
            weights=[60, 30, 10]
        )[0]
        
        try:
            req_start = time.time()
            
            if action == "predict":
                poke1, poke2 = random.sample(pokemon_list, 2)
                response = requests.post(
                    f"{API_BASE_URL}/predict/battle",
                    json={"pokemon1_id": poke1["id"], "pokemon2_id": poke2["id"]},
                    timeout=5
                )
                if response.status_code == 200:
                    stats["predictions"] += 1
                    stats["latencies"].append(time.time() - req_start)
            
            elif action == "read":
                poke = random.choice(pokemon_list)
                response = requests.get(f"{API_BASE_URL}/pokemon/{poke['id']}")
                if response.status_code == 200:
                    stats["reads"] += 1
            
            else:
                response = requests.get(f"{API_BASE_URL}/pokemon/99999")
                if response.status_code == 404:
                    stats["errors"] += 1
        
        except Exception:
            pass
        
        # Rapport toutes les 30 secondes
        if time.time() - last_report >= 30:
            avg_latency = sum(stats["latencies"][-100:]) / len(stats["latencies"][-100:]) if stats["latencies"] else 0
            print(f"[{int(elapsed)}s] Prédictions: {stats['predictions']:4d} | "
                  f"Lectures: {stats['reads']:4d} | Erreurs: {stats['errors']:3d} | "
                  f"Latence moy: {avg_latency*1000:.1f}ms")
            last_report = time.time()
        
        # Pause variable (simule trafic réaliste)
        time.sleep(random.uniform(0.2, 1.0))
    
    print("\n" + "=" * 70)
    print("✅ Génération terminée!")
    print(f"   Prédictions: {stats['predictions']}")
    print(f"   Lectures: {stats['reads']}")
    print(f"   Erreurs: {stats['errors']}")
    
    if stats["latencies"]:
        latencies_sorted = sorted(stats["latencies"])
        p50 = latencies_sorted[len(latencies_sorted) // 2] * 1000
        p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)] * 1000
        p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)] * 1000
        print(f"\n   Latences: P50={p50:.1f}ms, P95={p95:.1f}ms, P99={p99:.1f}ms")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        # Mode génération continue
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        generate_metrics_continuous(duration)
    else:
        # Mode tests pytest
        print("\n" + "=" * 70)
        print("Tests de génération de métriques Prometheus/Grafana")
        print("=" * 70)
        pytest.main([__file__, "-v", "-s"])
