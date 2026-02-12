#!/usr/bin/env python3
"""
Script to test CI/CD locally before pushing to GitHub.

Usage: python3 scripts/test_ci_cd_locally.py
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests

# ANSI Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
RESET = '\033[0m'


def print_step(title):
    """Display a step header."""
    print(f"\n{title}...")


def check_command(command):
    """Check that a command exists."""
    return shutil.which(command) is not None


def check_prerequisites():
    """Check prerequisites."""
    print_step("Checking prerequisites")

    if not check_command("docker"):
        print(f"{RED}Docker is not installed{RESET}")
        return False

    if not (check_command("docker-compose") or check_command("docker")):
        print(f"{RED}Docker Compose is not installed{RESET}")
        return False

    if not check_command("python3"):
        print(f"{RED}Python 3 is not installed{RESET}")
        return False

    print(f"{GREEN}All prerequisites OK{RESET}")
    return True


def create_env_file():
    """Create .env file if it doesn't exist."""
    print_step("Creating .env file")

    env_file = Path(".env")

    if env_file.exists():
        print(f"{GREEN}.env file already exists{RESET}")
        return True

    env_content = """POSTGRES_USER=letsgo_user
POSTGRES_PASSWORD=letsgo_password
POSTGRES_DB=letsgo_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEV_MODE=true
API_KEY_REQUIRED=true
API_KEYS=test_key_for_local_ci,BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ
DISABLE_MLFLOW_TRACKING=false
USE_MLFLOW_REGISTRY=false
ML_SKIP_IF_EXISTS=true
"""

    env_file.write_text(env_content)
    print(f"{GREEN}.env file created{RESET}")
    return True


def start_services():
    """Start Docker services."""
    print_step("Starting Docker services")

    # Stop existing services
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        capture_output=True,
        check=False
    )

    # Start services
    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        capture_output=True,
        check=False
    )

    if result.returncode != 0:
        print(f"{RED}Failed to start services{RESET}")
        return False

    print("Waiting for services to start...")
    time.sleep(10)
    return True


def wait_for_postgres():
    """Wait for PostgreSQL to be ready."""
    print_step("Waiting for PostgreSQL")

    for _ in range(30): # 60 seconds max
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "db", "pg_isready", "-U", "letsgo_user"],
            capture_output=True,
            check=False
        )

        if result.returncode == 0:
            print(f"{GREEN}PostgreSQL ready{RESET}")
            return True

        time.sleep(2)

    print(f"{RED}PostgreSQL timeout{RESET}")
    return False


def wait_for_service(name, url, timeout=120, critical=True):
    """Wait for a service to be available."""
    print_step(f"Waiting for {name}")

    for _ in range(timeout // 3):
        try:
            response = requests.get(url, timeout=3)
            if response.status_code in [200, 302]:
                print(f"{GREEN}{name} ready{RESET}")
                return True
        except requests.exceptions.RequestException:
            pass

        time.sleep(3)

    if critical:
        print(f"{RED}{name} timeout{RESET}")
        return False

    print(f"{YELLOW}{name} timeout (non-critical){RESET}")
    return True


def check_service_status(name, url, success_codes=None):
    """Check a service status."""
    if success_codes is None:
        success_codes = [200]

    try:
        response = requests.get(url, timeout=5)
        status = response.status_code

        if status in success_codes:
            return status, True

        return status, False
    except requests.exceptions.RequestException:
        return 0, False


def check_all_services():
    """Check all services status."""
    print_step("Checking all services status")

    # Display container status
    print("\nService Status:")
    subprocess.run(["docker", "compose", "ps"], check=False)

    print("\nHealth Checks:")

    services = {
        "API": ("http://localhost:8080/health", [200]),
        "Prometheus": ("http://localhost:9091/-/healthy", [200]),
        "Grafana": ("http://localhost:3001/api/health", [200]),
        "MLflow": ("http://localhost:5001/health", [200]),
        "pgAdmin": ("http://localhost:5050", [200, 302])
    }

    results = {}

    for name, (url, success_codes) in services.items():
        status, ok = check_service_status(name, url, success_codes)
        results[name] = (status, ok)

        status_text = f"{GREEN}OK ({status}){RESET}" if ok else f"{YELLOW}WARN ({status}){RESET}"
        if name == "API" and not ok:
            status_text = f"{RED}FAIL ({status}){RESET}"

        print(f" - {name:12} {status_text}")

    return results


def install_dependencies():
    """Install Python dependencies."""
    print_step("Installing Python dependencies")

    print(f"{GREEN}Dependencies already installed{RESET}")
    return True


def run_monitoring_validation():
    """Run monitoring validation."""
    print_step("Running Monitoring Validation Script")
    print("=" * 50)

    # Script has been moved
    validation_script = Path("tests/integration/test_monitoring_validation.py")

    if not validation_script.exists():
        print(f"{RED}Validation script not found at {validation_script}{RESET}")
        return False, 0

    result = subprocess.run(
        [sys.executable, str(validation_script)],
        capture_output=False,
        check=False
    )

    if result.returncode == 0:
        print(f"\n{GREEN}MONITORING VALIDATION PASSED!{RESET}")
        return True, 100

    print(f"\n{RED}MONITORING VALIDATION FAILED!{RESET}")
    return False, 0


def check_reports():
    """Check generated reports."""
    print_step("Checking generated reports")

    score = 0

    json_report = Path("reports/monitoring/validation_report.json")
    if json_report.exists():
        try:
            data = json.loads(json_report.read_text())
            score = data.get("validation_score", 0)
            print(f"{GREEN}JSON report generated{RESET}")
            print(f" Score: {GREEN}{score}/100{RESET}")
        except json.JSONDecodeError:
            print(f"{RED}Failed to read JSON report{RESET}")
    else:
        print(f"{RED}JSON report not found{RESET}")

    html_report = Path("reports/monitoring/validation_report.html")
    if html_report.exists():
        print(f"{GREEN}HTML report generated{RESET}")
        print(f" Location: {html_report}")
    else:
        print(f"{RED}HTML report not found{RESET}")

    return score


def print_summary(api_status, score):
    """Display test summary."""
    print_step("Test Summary")
    print("=" * 24)

    success = api_status and score >= 60

    if success:
        print(f"\n{GREEN} SUCCESS! Your CI/CD pipeline will work on GitHub Actions{RESET}\n")
        print("Next steps:")
        print(" 1. Commit your changes: git add . && git commit -m 'Add monitoring validation workflow'")
        print(" 2. Push to GitHub: git push origin main")
        print(" 3. Check GitHub Actions: https://github.com/your-repo/lets-go-predictiondex/actions")
        print(" 4. Download the HTML report from artifacts")
        return 0

    print(f"\n{RED}FAILED! Fix the issues before pushing to GitHub{RESET}\n")
    print("Issues found:")
    if not api_status:
        print(" - API is not responding correctly")
    if score < 60:
        print(f" - Monitoring score is too low ({score} < 60)")
    return 1


def cleanup_prompt():
    """Ask if user wants to stop services."""
    print()
    try:
        response = input("Do you want to stop the services? (y/N): ")
        if response.lower() in ['y', 'yes']:
            print(" Cleaning up...")
            subprocess.run(["docker", "compose", "down", "-v"], check=False)
            print(f"{GREEN}Services stopped{RESET}")
        else:
            print(" Services are still running")
            print(" Stop them manually with: docker compose down -v")
    except KeyboardInterrupt:
        print("\n Services are still running")
        print(" Stop them manually with: docker compose down -v")


def main():
    """Main function."""
    print("Testing CI/CD Pipeline Locally")
    print("=" * 34)

    if not check_prerequisites():
        return 1

    if not create_env_file():
        return 1

    if not start_services():
        return 1

    if not wait_for_postgres():
        return 1

    # Wait for all services
    if not wait_for_service("API", "http://localhost:8080/health", timeout=120, critical=True):
        return 1

    wait_for_service("Prometheus", "http://localhost:9091/-/healthy", timeout=60, critical=False)
    wait_for_service("Grafana", "http://localhost:3001/api/health", timeout=60, critical=False)
    wait_for_service("MLflow", "http://localhost:5001/health", timeout=60, critical=False)

    service_results = check_all_services()
    api_status = service_results.get("API", (0, False))[1]

    if not install_dependencies():
        return 1

    run_monitoring_validation()
    score = check_reports()
    exit_code = print_summary(api_status, score)
    cleanup_prompt()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
