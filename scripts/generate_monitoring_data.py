#!/usr/bin/env python3
"""
Metrics Generator for Grafana/Prometheus Monitoring.

Script to generate test metrics and populate Grafana dashboards
with realistic data.

Usage:
    # Generate for 5 minutes
    python scripts/generate_monitoring_data.py

    # Generate for 30 minutes
    python scripts/generate_monitoring_data.py --duration 30

    # Burst mode (many requests quickly)
    python scripts/generate_monitoring_data.py --mode burst

    # Realistic mode (simulates users)
    python scripts/generate_monitoring_data.py --mode realistic
"""

import argparse
import random
import sys
import time
from typing import Dict, List, Tuple

import requests


# Configuration
API_BASE_URL = "http://localhost:8080"
PROMETHEUS_URL = "http://localhost:9091"
GRAFANA_URL = "http://localhost:3001"
API_KEY = "BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ"  # Default API key from docker-compose


class MetricsGenerator:
    """Metrics generator for monitoring."""

    def __init__(self, api_url: str = API_BASE_URL, api_key: str = API_KEY):
        """Initialize the generator.

        Args:
            api_url: Base URL for the API.
            api_key: API key for authentication.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key} if api_key else {}
        self.pokemon_list: List[Dict] = []
        self.stats: Dict = {
            "predictions": 0,
            "reads": 0,
            "errors": 0,
            "latencies": [],
            "start_time": time.time()
        }

    def initialize(self) -> bool:
        """Initialize the generator and load Pokemon."""
        print("🔧 Initializing...")

        try:
            # Check API
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code != 200:
                print(f"❌ API not accessible: {response.status_code}")
                return False

            print("   ✅ API accessible")

            # Load Pokemon
            response = requests.get(
                f"{self.api_url}/pokemon/",
                headers=self.headers,
                timeout=10
            )
            if response.status_code != 200:
                print(f"❌ Unable to load Pokemon: {response.status_code}")
                return False

            self.pokemon_list = response.json()
            print(f"   ✅ {len(self.pokemon_list)} Pokemon loaded")

            # Check Prometheus
            try:
                response = requests.get(f"{PROMETHEUS_URL}/api/v1/status/config", timeout=5)
                if response.status_code == 200:
                    print("   ✅ Prometheus accessible")
                else:
                    print("   ⚠️  Prometheus not accessible")
            except requests.exceptions.RequestException:
                print("   ⚠️  Prometheus not accessible")

            # Check Grafana
            try:
                response = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
                if response.status_code == 200:
                    print("   ✅ Grafana accessible")
                else:
                    print("   ⚠️  Grafana not accessible")
            except requests.exceptions.RequestException:
                print("   ⚠️  Grafana not accessible")

            return True

        except requests.exceptions.RequestException as exc:
            print(f"❌ Initialization error: {exc}")
            return False

    def generate_prediction(self) -> Tuple[bool, float]:
        """Generate a random prediction.

        Returns:
            Tuple of (success, latency_seconds).
        """
        poke1, poke2 = random.sample(self.pokemon_list, 2)

        # Use common moves for testing
        # These are popular moves that most Pokemon can learn
        available_moves_a = random.sample([
            "Charge", "Vive-Attaque", "Météores", "Hydrocanon",
            "Lance-Flammes", "Fatal-Foudre", "Séisme"
        ], k=4)

        available_moves_b = random.sample([
            "Charge", "Vive-Attaque", "Météores", "Hydrocanon",
            "Lance-Flammes", "Fatal-Foudre", "Séisme"
        ], k=4)

        start = time.time()
        try:
            response = requests.post(
                f"{self.api_url}/predict/best-move",
                headers=self.headers,
                json={
                    "pokemon_a_id": poke1["id"],
                    "pokemon_b_id": poke2["id"],
                    "available_moves": available_moves_a,
                    "available_moves_b": available_moves_b
                },
                timeout=10
            )
            latency = time.time() - start

            if response.status_code == 200:
                self.stats["predictions"] += 1
                self.stats["latencies"].append(latency)
                return True, latency

            return False, latency

        except requests.exceptions.RequestException:
            return False, time.time() - start

    def generate_read(self) -> bool:
        """Generate a Pokemon read request."""
        poke = random.choice(self.pokemon_list)

        try:
            response = requests.get(
                f"{self.api_url}/pokemon/{poke['id']}",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                self.stats["reads"] += 1
                return True
            return False
        except requests.exceptions.RequestException:
            return False

    def generate_error(self) -> bool:
        """Generate an intentional error."""
        try:
            response = requests.get(
                f"{self.api_url}/pokemon/99999",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 404:
                self.stats["errors"] += 1
                return True
            return False
        except requests.exceptions.RequestException:
            return False

    def print_stats(self):
        """Display current statistics."""
        elapsed = time.time() - self.stats["start_time"]

        if self.stats["latencies"]:
            latencies_sorted = sorted(self.stats["latencies"])
            p50 = latencies_sorted[len(latencies_sorted) // 2] * 1000
            p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)] * 1000
            p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)] * 1000

            print(f"[{int(elapsed):4d}s] "
                  f"Predictions: {self.stats['predictions']:5d} | "
                  f"Reads: {self.stats['reads']:4d} | "
                  f"Errors: {self.stats['errors']:3d} | "
                  f"Latency: P50={p50:.1f}ms P95={p95:.1f}ms P99={p99:.1f}ms")
        else:
            print(f"[{int(elapsed):4d}s] "
                  f"Predictions: {self.stats['predictions']:5d} | "
                  f"Reads: {self.stats['reads']:4d} | "
                  f"Errors: {self.stats['errors']:3d}")

    def run_burst_mode(self, duration_minutes: int):
        """Burst mode: Maximum requests quickly.

        Args:
            duration_minutes: Duration in minutes.
        """
        print(f"\n🚀 BURST Mode - {duration_minutes} minutes")
        print("=" * 80)

        duration = duration_minutes * 60
        last_report = time.time()

        while time.time() - self.stats["start_time"] < duration:
            # Generate requests in bursts
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

            # Report every 30s
            if time.time() - last_report >= 30:
                self.print_stats()
                last_report = time.time()

            # Small pause
            time.sleep(0.1)

        print("\n" + "=" * 80)
        print("✅ Burst mode completed!")
        self.print_final_stats()

    def run_realistic_mode(self, duration_minutes: int):
        """Realistic mode: Simulates real users.

        Args:
            duration_minutes: Duration in minutes.
        """
        print(f"\n👥 REALISTIC Mode - {duration_minutes} minutes")
        print("=" * 80)
        print("Simulation: 5-10 users with realistic patterns")

        duration = duration_minutes * 60
        last_report = time.time()

        while time.time() - self.stats["start_time"] < duration:
            # Simulate user
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

            # Report every 30s
            if time.time() - last_report >= 30:
                self.print_stats()
                last_report = time.time()

            # Realistic pause (0.5-3 seconds between requests)
            time.sleep(random.uniform(0.5, 3.0))

        print("\n" + "=" * 80)
        print("✅ Realistic mode completed!")
        self.print_final_stats()

    def run_spike_mode(self, duration_minutes: int):
        """Spike mode: Random traffic spikes.

        Args:
            duration_minutes: Duration in minutes.
        """
        print(f"\n📈 SPIKE Mode - {duration_minutes} minutes")
        print("=" * 80)
        print("Simulation: Random traffic spikes (variable load)")

        duration = duration_minutes * 60
        last_report = time.time()

        while time.time() - self.stats["start_time"] < duration:
            # Decide if we're in a spike
            is_spike = random.random() < 0.2  # 20% of the time

            if is_spike:
                # Spike: many requests
                print("   🔥 TRAFFIC SPIKE!")
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
                # Normal traffic
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

            # Report every 30s
            if time.time() - last_report >= 30:
                self.print_stats()
                last_report = time.time()

        print("\n" + "=" * 80)
        print("✅ Spike mode completed!")
        self.print_final_stats()

    def print_final_stats(self):
        """Display final statistics."""
        elapsed = time.time() - self.stats["start_time"]
        total = self.stats["predictions"] + self.stats["reads"] + self.stats["errors"]

        print("\n📊 Final statistics:")
        print(f"   Total duration: {elapsed/60:.1f} minutes")
        print(f"   Total requests: {total}")
        print(f"   Predictions: {self.stats['predictions']} ({self.stats['predictions']/total*100:.1f}%)")
        print(f"   Reads: {self.stats['reads']} ({self.stats['reads']/total*100:.1f}%)")
        print(f"   Errors: {self.stats['errors']} ({self.stats['errors']/total*100:.1f}%)")
        print(f"   Average throughput: {total/(elapsed/60):.1f} req/min")

        if self.stats["latencies"]:
            latencies_sorted = sorted(self.stats["latencies"])
            p50 = latencies_sorted[len(latencies_sorted) // 2] * 1000
            p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)] * 1000
            p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)] * 1000
            avg = sum(self.stats["latencies"]) / len(self.stats["latencies"]) * 1000

            print("\n   Prediction latencies:")
            print(f"      Average: {avg:.1f}ms")
            print(f"      P50: {p50:.1f}ms")
            print(f"      P95: {p95:.1f}ms")
            print(f"      P99: {p99:.1f}ms")

        print(f"\n💡 Check Grafana: {GRAFANA_URL}")
        print(f"💡 Check Prometheus: {PROMETHEUS_URL}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Metrics generator for Grafana/Prometheus monitoring"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Generation duration in minutes (default: 5)"
    )
    parser.add_argument(
        "--mode",
        choices=["burst", "realistic", "spike"],
        default="realistic",
        help="Generation mode (default: realistic)"
    )
    parser.add_argument(
        "--api-url",
        default=API_BASE_URL,
        help=f"API URL (default: {API_BASE_URL})"
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🎯 Prometheus/Grafana Metrics Generator")
    print("=" * 80)

    generator = MetricsGenerator(api_url=args.api_url)

    if not generator.initialize():
        print("\n❌ Initialization failed")
        print("\n💡 Make sure services are started:")
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
        print("\n\n⚠️  Generation interrupted by user")
        generator.print_final_stats()


if __name__ == "__main__":
    main()
