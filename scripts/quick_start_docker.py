#!/usr/bin/env python3
"""Interactive Docker quick start guide."""

import argparse
import shutil
import subprocess
import sys
import time

import requests


def get_docker_compose_command():
    """
    Detect Docker Compose command (v2 'docker compose' or v1 'docker-compose').

    Returns:
        str: The appropriate docker compose command
    """
    # Try docker compose (v2) first
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            timeout=5,
            check=False
        )
        if result.returncode == 0:
            return "docker compose"
    except (subprocess.TimeoutExpired, OSError):
        pass

    # Fallback to docker-compose (v1)
    if shutil.which("docker-compose"):
        return "docker-compose"

    return None


def print_header(title: str):
    """Display a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(number: int, title: str):
    """Display a step title."""
    print(f"\n{'─' * 70}")
    print(f"  STEP {number}: {title}")
    print("─" * 70)


def run_command(command: str, description: str) -> bool:
    """
    Execute a shell command and display the result.

    Args:
        command: Shell command to execute
        description: Human-readable description of the command

    Returns:
        True if successful, False otherwise
    """
    print(f"\n[RUN] {description}...")
    print(f"   $ {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            check=False
        )

        if result.returncode == 0:
            print("   [OK] Success")
            return True

        print(f"   [ERROR] Failed (code {result.returncode})")
        if result.stderr:
            print(f"   Error: {result.stderr[:200]}")
        return False

    except subprocess.TimeoutExpired:
        print("   [ERROR] Timeout (> 120s)")
        return False
    except OSError as exc:
        print(f"   [ERROR] Error: {exc}")
        return False


def check_service(url: str, name: str, timeout: int = 5) -> bool:
    """
    Check if a service is accessible.

    Args:
        url: Service URL to check
        name: Service name for display
        timeout: Request timeout in seconds

    Returns:
        True if service responds with 200, False otherwise
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"   [OK] {name} accessible")
            return True

        print(f"   [WARN] {name} responds with status {response.status_code}")
        return False
    except requests.exceptions.RequestException:
        print(f"   [ERROR] {name} not accessible")
        return False


def main():
    """Main entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Docker Quick Start Guide")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run in automatic mode without prompts (use default values)"
    )
    args = parser.parse_args()
    auto_mode = args.auto

    print_header("[START] DOCKER QUICK START GUIDE")
    print("\nThis script will guide you to start the complete stack.")
    print("\nServices to be started:")
    print("  • PostgreSQL (database)")
    print("  • ETL Pipeline (data import)")
    print("  • ML Builder (model training)")
    print("  • API FastAPI (backend)")
    print("  • Streamlit (interface)")
    print("  • Prometheus (metrics)")
    print("  • Grafana (dashboards)")
    print("  • MLflow (Model Registry)")
    print("  • Node Exporter (system metrics)")

    if auto_mode:
        print("\n[AUTO] Running in automatic mode...")
    else:
        input("\n[INPUT] Press ENTER to start...")

    # ========================================================================
    # STEP 1: Check Docker
    # ========================================================================

    print_step(1, "Docker Verification")

    if not run_command("docker --version", "Check Docker"):
        print("\n[ERROR] Docker is not installed or not accessible")
        print("[TIP] Install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)

    # Detect Docker Compose version (v2 or v1)
    compose_cmd = get_docker_compose_command()
    if not compose_cmd:
        print("\n[ERROR] Docker Compose is not installed")
        print("[TIP] Install Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)

    if not run_command(f"{compose_cmd} version", "Check Docker Compose"):
        print("\n[ERROR] Docker Compose is not working")
        sys.exit(1)

    print(f"   [INFO] Using: {compose_cmd}")

    # ========================================================================
    # STEP 2: Stop existing services
    # ========================================================================

    print_step(2, "Cleanup of existing services")

    print("\n[WARN] This step will stop existing Docker services")
    if auto_mode:
        response = "y"
        print("[AUTO] Auto mode: Proceeding with cleanup")
    else:
        response = input("Continue? (y/N): ").lower()

    if response == "y":
        run_command(f"{compose_cmd} down", "Stop services")
    else:
        print("[INFO] Cleanup skipped")

    # ========================================================================
    # STEP 3: Build images
    # ========================================================================

    print_step(3, "Building Docker images")

    print("\n[WARN] This step may take 5-10 minutes the first time")
    if auto_mode:
        response = "y"
        print("[AUTO] Auto mode: Building images")
    else:
        response = input("Build images? (Y/n): ").lower()

    if response != "n":
        if not run_command(f"{compose_cmd} build --parallel", "Build images"):
            print("\n[ERROR] Build failed")
            print("[TIP] Check the logs above")
            sys.exit(1)
    else:
        print("[INFO] Build skipped")

    # ========================================================================
    # STEP 4: Start services
    # ========================================================================

    print_step(4, "Starting services")

    if not run_command(f"{compose_cmd} up -d", "Start the stack"):
        print("\n[ERROR] Startup failed")
        sys.exit(1)

    # Some services may stay in "Created" state after first up -d
    # Retry with specific services to ensure they start
    print("\n[RETRY] Ensuring all services are started...")
    run_command(
        f"{compose_cmd} up -d ml_builder api grafana streamlit",
        "Start remaining services"
    )

    print("\n[WAIT] Waiting for complete startup (30s)...")
    for i in range(30, 0, -5):
        print(f"   {i}s remaining...")
        time.sleep(5)

    # ========================================================================
    # STEP 5: Validate services
    # ========================================================================

    print_step(5, "Service validation")

    services_to_check = [
        ("http://localhost:8080/health", "API FastAPI"),
        ("http://localhost:8502", "Streamlit"),
        ("http://localhost:9091/-/healthy", "Prometheus"),
        ("http://localhost:3001/api/health", "Grafana"),
        ("http://localhost:5001/health", "MLflow"),
    ]

    all_ok = True
    for url, name in services_to_check:
        if not check_service(url, name):
            all_ok = False

    # ========================================================================
    # STEP 6: Generate test metrics (optional)
    # ========================================================================

    if all_ok:
        print_step(6, "Generate test metrics (optional)")

        print("\n[TIP] Do you want to generate test metrics for Grafana?")
        print("   This will create ML predictions and populate dashboards")

        if auto_mode:
            response = "n"
            print("[AUTO] Auto mode: Skipping metrics generation (can be done manually later)")
        else:
            response = input("\nGenerate metrics? (y/N): ").lower()

        if response == "y":
            if auto_mode:
                duration = 2
            else:
                duration = input("Duration in minutes (default: 2): ").strip()
                duration = int(duration) if duration else 2

            print(f"\n[ACTION] Generating metrics for {duration} minute(s)...")
            print("   (You can interrupt with Ctrl+C)")

            try:
                subprocess.run(
                    f"python scripts/generate_monitoring_data.py --duration {duration}",
                    shell=True,
                    timeout=duration * 60 + 30,
                    check=False
                )
            except KeyboardInterrupt:
                print("\n[WARN] Generation interrupted")
            except subprocess.TimeoutExpired:
                print("   [WARN] Timeout")

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print_header("[OK] STARTUP COMPLETE")

    if all_ok:
        print("\n[SUCCESS] All services are operational!")
        print("\n[URLS] Available URLs:")
        print("   • API (Swagger):  http://localhost:8080/docs")
        print("   • Streamlit:      http://localhost:8502")
        print("   • Grafana:        http://localhost:3001")
        print("   • Prometheus:     http://localhost:9091")
        print("   • MLflow:         http://localhost:5001")

        print("\n[ENDPOINTS] Useful endpoints:")
        print("   • API metrics:    http://localhost:8080/metrics")
        print("   • Health check:   http://localhost:8080/health")

        print("\n[TIP] Useful commands:")
        print("   # View logs")
        print("   docker-compose logs -f api")
        print("")
        print("   # Generate metrics")
        print("   python scripts/generate_monitoring_data.py --duration 10")
        print("")
        print("   # Validate stack")
        print("   python scripts/validate_docker_stack.py")
        print("")
        print("   # Stop services")
        print("   docker-compose down")

        print("\n[NEXT] Next steps:")
        print("   1. Open Grafana (http://localhost:3001)")
        print("   2. Check dashboards (Model Performance, API Performance)")
        print("   3. Test the API (http://localhost:8080/docs)")
        print("   4. Explore the interface (http://localhost:8502)")

    else:
        print("\n[WARN] Some services are not accessible")
        print("\n[TIP] Actions to take:")
        print("   1. Check logs: docker-compose logs <service>")
        print("   2. Restart services: docker-compose restart")
        print("   3. Validate stack: python scripts/validate_docker_stack.py")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Script interrupted by user")
        sys.exit(1)
