#!/usr/bin/env python3
"""
Interactive Docker Quick Start Guide.

Interactive script to guide users through starting and validating
the complete Docker stack.

This script provides a step-by-step walkthrough for:
    1. Checking Docker prerequisites (Docker, Docker Compose)
    2. Building Docker images
    3. Starting services in correct order
    4. Validating service health
    5. Displaying access URLs
    6. Running initial smoke tests

Features:
    - Colored terminal output for better readability
    - Progress indicators for long-running operations
    - Automatic health checks with retry logic
    - Helpful error messages and troubleshooting tips
    - Service URL summary at completion

Usage:
    # Start guided setup
    python scripts/quick_start_docker.py

    # Quick start without prompts
    python scripts/quick_start_docker.py --auto

Prerequisites:
    - Docker installed and running
    - Docker Compose v2+
    - Sufficient disk space (10GB recommended)
    - Ports available: 8080, 5432, 9091, 3001, 5001, 8502
"""

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
    print(f"\n🔧 {description}...")
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
            print("   ✅ Success")
            return True

        print(f"   ❌ Failed (code {result.returncode})")
        if result.stderr:
            print(f"   Error: {result.stderr[:200]}")
        return False

    except subprocess.TimeoutExpired:
        print("   ❌ Timeout (> 120s)")
        return False
    except OSError as exc:
        print(f"   ❌ Error: {exc}")
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
            print(f"   ✅ {name} accessible")
            return True

        print(f"   ⚠️  {name} responds with status {response.status_code}")
        return False
    except requests.exceptions.RequestException:
        print(f"   ❌ {name} not accessible")
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

    print_header("🚀 DOCKER QUICK START GUIDE")
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
        print("\n🤖 Running in automatic mode...")
    else:
        input("\n👉 Press ENTER to start...")

    # ========================================================================
    # STEP 1: Check Docker
    # ========================================================================

    print_step(1, "Docker Verification")

    if not run_command("docker --version", "Check Docker"):
        print("\n❌ Docker is not installed or not accessible")
        print("💡 Install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)

    # Detect Docker Compose version (v2 or v1)
    compose_cmd = get_docker_compose_command()
    if not compose_cmd:
        print("\n❌ Docker Compose is not installed")
        print("💡 Install Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)

    if not run_command(f"{compose_cmd} version", "Check Docker Compose"):
        print("\n❌ Docker Compose is not working")
        sys.exit(1)

    print(f"   ℹ️  Using: {compose_cmd}")

    # ========================================================================
    # STEP 2: Stop existing services
    # ========================================================================

    print_step(2, "Cleanup of existing services")

    print("\n⚠️  This step will stop existing Docker services")
    if auto_mode:
        response = "y"
        print("🤖 Auto mode: Proceeding with cleanup")
    else:
        response = input("Continue? (y/N): ").lower()

    if response == "y":
        run_command(f"{compose_cmd} down", "Stop services")
    else:
        print("ℹ️  Cleanup skipped")

    # ========================================================================
    # STEP 3: Build images
    # ========================================================================

    print_step(3, "Building Docker images")

    print("\n⚠️  This step may take 5-10 minutes the first time")
    if auto_mode:
        response = "y"
        print("🤖 Auto mode: Building images")
    else:
        response = input("Build images? (Y/n): ").lower()

    if response != "n":
        if not run_command(f"{compose_cmd} build --parallel", "Build images"):
            print("\n❌ Build failed")
            print("💡 Check the logs above")
            sys.exit(1)
    else:
        print("ℹ️  Build skipped")

    # ========================================================================
    # STEP 4: Start services
    # ========================================================================

    print_step(4, "Starting services")

    if not run_command(f"{compose_cmd} up -d", "Start the stack"):
        print("\n❌ Startup failed")
        sys.exit(1)

    # Some services may stay in "Created" state after first up -d
    # Retry with specific services to ensure they start
    print("\n🔄 Ensuring all services are started...")
    run_command(
        f"{compose_cmd} up -d ml_builder api grafana streamlit",
        "Start remaining services"
    )

    print("\n⏳ Waiting for complete startup (30s)...")
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

        print("\n💡 Do you want to generate test metrics for Grafana?")
        print("   This will create ML predictions and populate dashboards")

        if auto_mode:
            response = "n"
            print("🤖 Auto mode: Skipping metrics generation (can be done manually later)")
        else:
            response = input("\nGenerate metrics? (y/N): ").lower()

        if response == "y":
            if auto_mode:
                duration = 2
            else:
                duration = input("Duration in minutes (default: 2): ").strip()
                duration = int(duration) if duration else 2

            print(f"\n🎯 Generating metrics for {duration} minute(s)...")
            print("   (You can interrupt with Ctrl+C)")

            try:
                subprocess.run(
                    f"python scripts/generate_monitoring_data.py --duration {duration}",
                    shell=True,
                    timeout=duration * 60 + 30,
                    check=False
                )
            except KeyboardInterrupt:
                print("\n⚠️  Generation interrupted")
            except subprocess.TimeoutExpired:
                print("   ⚠️  Timeout")

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print_header("✅ STARTUP COMPLETE")

    if all_ok:
        print("\n🎉 All services are operational!")
        print("\n📍 Available URLs:")
        print("   • API (Swagger):  http://localhost:8080/docs")
        print("   • Streamlit:      http://localhost:8502")
        print("   • Grafana:        http://localhost:3001")
        print("   • Prometheus:     http://localhost:9091")
        print("   • MLflow:         http://localhost:5001")

        print("\n📊 Useful endpoints:")
        print("   • API metrics:    http://localhost:8080/metrics")
        print("   • Health check:   http://localhost:8080/health")

        print("\n💡 Useful commands:")
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

        print("\n🎯 Next steps:")
        print("   1. Open Grafana (http://localhost:3001)")
        print("   2. Check dashboards (Model Performance, API Performance)")
        print("   3. Test the API (http://localhost:8080/docs)")
        print("   4. Explore the interface (http://localhost:8502)")

    else:
        print("\n⚠️  Some services are not accessible")
        print("\n💡 Actions to take:")
        print("   1. Check logs: docker-compose logs <service>")
        print("   2. Restart services: docker-compose restart")
        print("   3. Validate stack: python scripts/validate_docker_stack.py")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
        sys.exit(1)
