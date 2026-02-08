#!/usr/bin/env python3
"""
Quick Start Script for Docker + Monitoring.

Replaces start_docker_stack.sh in pure Python.

Usage:
    python scripts/start_docker_stack.py
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path


def print_header(text: str):
    """Display a formatted header."""
    print("=" * 50)
    print(text)
    print("=" * 50)
    print()


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


def check_command(command: str) -> bool:
    """Check if a command exists."""
    try:
        subprocess.run(
            ["which", command],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run_command(command: str, description: str = None) -> bool:
    """Execute a shell command."""
    if description:
        print(f"🔧 {description}...")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
            check=False
        )

        if result.returncode == 0:
            if description:
                print(f"✅ {description} - OK\n")
            return True

        print(f"❌ Error: {result.stderr[:200]}\n")
        return False

    except subprocess.TimeoutExpired:
        print("❌ Timeout\n")
        return False
    except OSError as exc:
        print(f"❌ Error: {exc}\n")
        return False


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = Path(".env")

    if env_path.exists():
        print("✅ .env file exists\n")
        return True

    print("📝 Creating .env file...")

    env_content = """# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=letsgo_db
POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password

# API
API_BASE_URL=http://api:8080
DEV_MODE=true

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5001
MLFLOW_BACKEND_STORE_URI=postgresql://letsgo_user:letsgo_password@db:5432/letsgo_db

# Monitoring
PROMETHEUS_URL=http://prometheus:9091
GRAFANA_URL=http://grafana:3000
"""

    try:
        env_path.write_text(env_content)
        print("✅ .env file created\n")
        return True
    except OSError as exc:
        print(f"❌ Error creating .env: {exc}\n")
        return False


def check_docker_status(compose_cmd: str):
    """Check Docker services status.

    Args:
        compose_cmd: Docker compose command to use
    """
    try:
        result = subprocess.run(
            f"{compose_cmd} ps",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')

            # Count services UP
            services_up = sum(1 for line in lines if 'Up' in line)

            if services_up > 0:
                print(f"   ✅ {services_up} service(s) running")
                return services_up

        return 0

    except (subprocess.TimeoutExpired, OSError):
        return 0


def main():
    """Main entry point."""
    print_header("🚀 Starting PredictionDex - Full Stack")

    # 1. Check Docker
    if not check_command("docker"):
        print("❌ Docker is not installed")
        print("💡 Install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)

    # Detect Docker Compose version (v2 or v1)
    compose_cmd = get_docker_compose_command()
    if not compose_cmd:
        print("❌ Docker Compose is not installed")
        print("💡 Install Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)

    print(f"✅ Docker and Docker Compose detected (using: {compose_cmd})\n")

    # 2. Create .env file
    if not create_env_file():
        sys.exit(1)

    # 3. Build images
    print("📦 Building Docker images...")
    if not run_command(f"{compose_cmd} build --parallel", "Building images"):
        print("⚠️  Build failed, but continuing...\n")

    # 4. Start services
    print("🚀 Starting services...")
    if not run_command(f"{compose_cmd} up -d", "Starting stack"):
        print("❌ Startup failed")
        sys.exit(1)

    # 5. Wait for startup
    print("⏳ Waiting for complete startup (30s)...")
    for i in range(6, 0, -1):
        print(f"   {i*5}s remaining...")
        time.sleep(5)
    print()

    # 6. Check services
    print("🔍 Checking services...")

    services = [
        ("db", 5432, "PostgreSQL"),
        ("api", 8000, "FastAPI API"),
        ("streamlit", 8501, "Streamlit Interface"),
        ("prometheus", 9090, "Prometheus"),
        ("grafana", 3000, "Grafana"),
        ("mlflow", 5001, "MLflow"),
    ]

    all_ok = True
    for service, port, name in services:
        # Check via docker compose ps
        result = subprocess.run(
            f"{compose_cmd} ps {service} 2>/dev/null | grep -q Up",
            shell=True,
            capture_output=True,
            check=False
        )

        if result.returncode == 0:
            print(f"   ✅ {name} ({port})")
        else:
            print(f"   ❌ {name} ({port}) - Not started")
            all_ok = False

    print()

    # 7. Final summary
    if all_ok:
        print_header("✅ All services are operational!")
    else:
        print_header("⚠️  Some services are not started")

    if all_ok:
        print("🌐 Available URLs:")
        print("   API (Swagger):    http://localhost:8080/docs")
        print("   Streamlit:        http://localhost:8502")
        print("   Grafana:          http://localhost:3001")
        print("   Prometheus:       http://localhost:9091")
        print("   MLflow:           http://localhost:5001")
        print()
        print("📊 API Metrics:      http://localhost:8080/metrics")
        print("🔥 API Health:       http://localhost:8080/health")
        print()
        print("💡 Useful commands:")
        print("   # View logs")
        print("   docker-compose logs -f api")
        print()
        print("   # Generate test metrics")
        print("   python scripts/generate_monitoring_data.py --duration 10")
        print()
        print("   # Validate stack")
        print("   python scripts/validate_docker_stack.py")
        print()
        print("   # Stop services")
        print("   docker-compose down")
        print()
    else:
        print("💡 Actions to take:")
        print("   1. Check logs: docker-compose logs <service>")
        print("   2. Restart: docker-compose restart")
        print("   3. Validate: python scripts/validate_docker_stack.py")
        print()

    print("=" * 50)

    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
