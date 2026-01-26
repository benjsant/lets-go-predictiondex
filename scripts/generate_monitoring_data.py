#!/usr/bin/env python3
"""
Générateur de données pour monitoring Grafana/Prometheus
=========================================================

Script pour générer des métriques de test et remplir les dashboards
Grafana avec des données réalistes.

Usage:
    # Génération 5 minutes
    python scripts/generate_monitoring_data.py
    
    # Génération 30 minutes
    python scripts/generate_monitoring_data.py --duration 30
    
    # Mode burst (beaucoup de requêtes rapidement)
    python scripts/generate_monitoring_data.py --mode burst
    
    # Mode réaliste (simule utilisateurs)
    python scripts/generate_monitoring_data.py --mode realistic
"""

import argparse
import requests
import time
import random
import sys
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path


# Configuration
API_BASE_URL = "http://localhost:8080"
PROMETHEUS_URL = "http://localhost:9091"
GRAFANA_URL = "http://localhost:3001"


class MetricsGenerator:
    """Générateur de métriques pour monitoring."""
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.pokemon_list = []
        self.stats = {
            "predictions": 0,
            "reads": 0,
            "errors": 0,
            "latencies": [],
            "start_time": time.time()
        }
    
    def initialize(self) -> bool:
        """Initialise le générateur et charge les Pokémon."""
        print("🔧 Initialisation...")
        
        try:
            # Vérifier API
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code != 200:
                print(f"❌ API non accessible: {response.status_code}")
                return False
            
            print("   ✅ API accessible")
            
            # Charger Pokémon
            response = requests.get(f"{self.api_url}/pokemon?limit=100", timeout=10)
            if response.status_code != 200:
                print(f"❌ Impossible de charger les Pokémon")
                return False
            
            self.pokemon_list = response.json()
            print(f"   ✅ {len(self.pokemon_list)} Pokémon chargés")
            
            # Vérifier Prometheus
            try:
                response = requests.get(f"{PROMETHEUS_URL}/api/v1/status/config", timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Prometheus accessible")
                else:
                    print(f"   ⚠️  Prometheus non accessible")
            except:
                print(f"   ⚠️  Prometheus non accessible")
            
            # Vérifier Grafana
            try:
                response = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Grafana accessible")
                else:
                    print(f"   ⚠️  Grafana non accessible")
            except:
                print(f"   ⚠️  Grafana non accessible")
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur initialisation: {e}")
            return False
    
    def generate_prediction(self) -> Tuple[bool, float]:
        """
        Génère une prédiction aléatoire.
        
        Returns:
            (success, latency_seconds)
        """
        poke1, poke2 = random.sample(self.pokemon_list, 2)
        
        start = time.time()
        try:
            response = requests.post(
                f"{self.api_url}/predict/battle",
                json={"pokemon1_id": poke1["id"], "pokemon2_id": poke2["id"]},
                timeout=5
            )
            latency = time.time() - start
            
            if response.status_code == 200:
                self.stats["predictions"] += 1
                self.stats["latencies"].append(latency)
                return True, latency
            
            return False, latency
        
        except Exception:
            return False, time.time() - start
    
    def generate_read(self) -> bool:
        """Génère une lecture de Pokémon."""
        poke = random.choice(self.pokemon_list)
        
        try:
            response = requests.get(f"{self.api_url}/pokemon/{poke['id']}", timeout=5)
            if response.status_code == 200:
                self.stats["reads"] += 1
                return True
            return False
        except:
            return False
    
    def generate_error(self) -> bool:
        """Génère une erreur intentionnelle."""
        try:
            response = requests.get(f"{self.api_url}/pokemon/99999", timeout=5)
            if response.status_code == 404:
                self.stats["errors"] += 1
                return True
            return False
        except:
            return False
    
    def print_stats(self):
        """Affiche les statistiques actuelles."""
        elapsed = time.time() - self.stats["start_time"]
        
        if self.stats["latencies"]:
            latencies_sorted = sorted(self.stats["latencies"])
            p50 = latencies_sorted[len(latencies_sorted) // 2] * 1000
            p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)] * 1000
            p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)] * 1000
            
            print(f"[{int(elapsed):4d}s] "
                  f"Prédictions: {self.stats['predictions']:5d} | "
                  f"Lectures: {self.stats['reads']:4d} | "
                  f"Erreurs: {self.stats['errors']:3d} | "
                  f"Latence: P50={p50:.1f}ms P95={p95:.1f}ms P99={p99:.1f}ms")
        else:
            print(f"[{int(elapsed):4d}s] "
                  f"Prédictions: {self.stats['predictions']:5d} | "
                  f"Lectures: {self.stats['reads']:4d} | "
                  f"Erreurs: {self.stats['errors']:3d}")
    
    def run_burst_mode(self, duration_minutes: int):
        """
        Mode burst: Maximum de requêtes rapidement.
        
        Args:
            duration_minutes: Durée en minutes
        """
        print(f"\n🚀 Mode BURST - {duration_minutes} minutes")
        print("=" * 80)
        
        duration = duration_minutes * 60
        last_report = time.time()
        
        while time.time() - self.stats["start_time"] < duration:
            # Générer requêtes en rafale
            for _ in range(10):
                action = random.choices(
                    ["predict", "read", "error"],
                    weights=[80, 15, 5]
                )[0]
                
                if action == "predict":
                    self.generate_prediction()
                elif action == "read":
                    self.generate_read()
                else:
                    self.generate_error()
            
            # Rapport toutes les 30s
            if time.time() - last_report >= 30:
                self.print_stats()
                last_report = time.time()
            
            # Petite pause
            time.sleep(0.1)
        
        print("\n" + "=" * 80)
        print("✅ Mode burst terminé!")
        self.print_final_stats()
    
    def run_realistic_mode(self, duration_minutes: int):
        """
        Mode réaliste: Simule des utilisateurs réels.
        
        Args:
            duration_minutes: Durée en minutes
        """
        print(f"\n👥 Mode REALISTIC - {duration_minutes} minutes")
        print("=" * 80)
        print("Simulation: 5-10 utilisateurs avec patterns réalistes")
        
        duration = duration_minutes * 60
        last_report = time.time()
        
        while time.time() - self.stats["start_time"] < duration:
            # Simuler utilisateur
            action = random.choices(
                ["predict", "read", "error"],
                weights=[60, 30, 10]
            )[0]
            
            if action == "predict":
                self.generate_prediction()
            elif action == "read":
                self.generate_read()
            else:
                self.generate_error()
            
            # Rapport toutes les 30s
            if time.time() - last_report >= 30:
                self.print_stats()
                last_report = time.time()
            
            # Pause réaliste (0.5-3 secondes entre requêtes)
            time.sleep(random.uniform(0.5, 3.0))
        
        print("\n" + "=" * 80)
        print("✅ Mode realistic terminé!")
        self.print_final_stats()
    
    def run_spike_mode(self, duration_minutes: int):
        """
        Mode spike: Pics de trafic aléatoires.
        
        Args:
            duration_minutes: Durée en minutes
        """
        print(f"\n📈 Mode SPIKE - {duration_minutes} minutes")
        print("=" * 80)
        print("Simulation: Pics de trafic aléatoires (charge variable)")
        
        duration = duration_minutes * 60
        last_report = time.time()
        
        while time.time() - self.stats["start_time"] < duration:
            # Décider si on est dans un pic
            is_spike = random.random() < 0.2  # 20% du temps
            
            if is_spike:
                # Pic: beaucoup de requêtes
                print("   🔥 PIC DE TRAFIC!")
                for _ in range(50):
                    action = random.choices(
                        ["predict", "read"],
                        weights=[70, 30]
                    )[0]
                    
                    if action == "predict":
                        self.generate_prediction()
                    else:
                        self.generate_read()
                    
                    time.sleep(0.05)
                
                time.sleep(random.uniform(5, 15))
            else:
                # Trafic normal
                action = random.choices(
                    ["predict", "read", "error"],
                    weights=[50, 40, 10]
                )[0]
                
                if action == "predict":
                    self.generate_prediction()
                elif action == "read":
                    self.generate_read()
                else:
                    self.generate_error()
                
                time.sleep(random.uniform(1.0, 3.0))
            
            # Rapport toutes les 30s
            if time.time() - last_report >= 30:
                self.print_stats()
                last_report = time.time()
        
        print("\n" + "=" * 80)
        print("✅ Mode spike terminé!")
        self.print_final_stats()
    
    def print_final_stats(self):
        """Affiche les statistiques finales."""
        elapsed = time.time() - self.stats["start_time"]
        total = self.stats["predictions"] + self.stats["reads"] + self.stats["errors"]
        
        print(f"\n📊 Statistiques finales:")
        print(f"   Durée totale: {elapsed/60:.1f} minutes")
        print(f"   Total requêtes: {total}")
        print(f"   Prédictions: {self.stats['predictions']} ({self.stats['predictions']/total*100:.1f}%)")
        print(f"   Lectures: {self.stats['reads']} ({self.stats['reads']/total*100:.1f}%)")
        print(f"   Erreurs: {self.stats['errors']} ({self.stats['errors']/total*100:.1f}%)")
        print(f"   Débit moyen: {total/(elapsed/60):.1f} req/min")
        
        if self.stats["latencies"]:
            latencies_sorted = sorted(self.stats["latencies"])
            p50 = latencies_sorted[len(latencies_sorted) // 2] * 1000
            p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)] * 1000
            p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)] * 1000
            avg = sum(self.stats["latencies"]) / len(self.stats["latencies"]) * 1000
            
            print(f"\n   Latences prédictions:")
            print(f"      Moyenne: {avg:.1f}ms")
            print(f"      P50: {p50:.1f}ms")
            print(f"      P95: {p95:.1f}ms")
            print(f"      P99: {p99:.1f}ms")
        
        print(f"\n💡 Consultez Grafana: {GRAFANA_URL}")
        print(f"💡 Consultez Prometheus: {PROMETHEUS_URL}")


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Générateur de métriques pour monitoring Grafana/Prometheus"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Durée de génération en minutes (défaut: 5)"
    )
    parser.add_argument(
        "--mode",
        choices=["burst", "realistic", "spike"],
        default="realistic",
        help="Mode de génération (défaut: realistic)"
    )
    parser.add_argument(
        "--api-url",
        default=API_BASE_URL,
        help=f"URL de l'API (défaut: {API_BASE_URL})"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("🎯 Générateur de métriques Prometheus/Grafana")
    print("=" * 80)
    
    generator = MetricsGenerator(api_url=args.api_url)
    
    if not generator.initialize():
        print("\n❌ Échec de l'initialisation")
        print("\n💡 Assurez-vous que les services sont démarrés:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    print()
    
    try:
        if args.mode == "burst":
            generator.run_burst_mode(args.duration)
        elif args.mode == "realistic":
            generator.run_realistic_mode(args.duration)
        elif args.mode == "spike":
            generator.run_spike_mode(args.duration)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Génération interrompue par l'utilisateur")
        generator.print_final_stats()
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
