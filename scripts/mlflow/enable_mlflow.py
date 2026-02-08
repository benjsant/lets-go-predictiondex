#!/usr/bin/env python3
"""
Script to activate MLflow and register the existing model.

Usage: python3 scripts/mlflow/enable_mlflow.py
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# ANSI Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RESET = '\033[0m'


def print_header(text):
    """Display a formatted header."""
    print(f"\n{BLUE}{'='*40}{RESET}")
    print(f"{BLUE}{text:^40}{RESET}")
    print(f"{BLUE}{'='*40}{RESET}\n")


def print_success(text):
    """Display a success message."""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Display an error message."""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    """Display a warning message."""
    print(f"{YELLOW}{text}{RESET}")


def print_info(text):
    """Display an info message."""
    print(f"{BLUE}{text}{RESET}")


def check_mlflow_server():
    """Check that MLflow server is accessible."""
    print_info("Step 1: MLflow Server Verification")

    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print_success("MLflow Server is UP")
            return True
    except requests.exceptions.RequestException:
        pass

    print_error("MLflow Server is not accessible")
    print_warning("   Starting MLflow...")

    # Start MLflow
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "mlflow"],
            check=True,
            capture_output=True
        )
        print_warning("   Waiting 10 seconds...")
        time.sleep(10)

        # Re-check
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print_success("MLflow Server started")
            return True

        print_error("MLflow Server still not accessible")
        print_warning("   Check logs: docker compose logs mlflow")
        return False

    except subprocess.CalledProcessError as exc:
        print_error(f"Error starting MLflow: {exc}")
        return False
    except requests.exceptions.RequestException as exc:
        print_error(f"Connection error after startup: {exc}")
        return False


def configure_environment():
    """Configure environment variables."""
    print_info("\nStep 2: Environment configuration")

    os.environ["DISABLE_MLFLOW_TRACKING"] = "false"
    os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5001"
    os.environ["ML_SKIP_IF_EXISTS"] = "false"

    print_success("Environment variables configured:")
    print("   - DISABLE_MLFLOW_TRACKING=false")
    print("   - MLFLOW_TRACKING_URI=http://localhost:5001")
    print("   - ML_SKIP_IF_EXISTS=false")


def register_model():
    """Register the existing model in MLflow."""
    print_info("\nStep 3: Registering model v2 in MLflow\n")

    # Path to the registration script
    script_path = Path(__file__).parent / "register_existing_model.py"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=False
        )

        return result.returncode == 0

    except OSError as exc:
        print_error(f"Error executing script: {exc}")
        return False


def print_success_message():
    """Display the final success message."""
    print(f"\n{GREEN}{'='*40}{RESET}")
    print(f"{GREEN}{'✅ SUCCESS!':^40}{RESET}")
    print(f"{GREEN}{'='*40}{RESET}\n")

    print_success("Model v2 (96.24% accuracy) has been registered in MLflow\n")

    print_info("📊 Check in MLflow UI:")
    print("   http://localhost:5001\n")

    print_info("🔧 To make the API use MLflow Registry:")
    print("   1. Modify docker-compose.yml line 128:")
    print('      USE_MLFLOW_REGISTRY: "true"')
    print("   2. Restart the API:")
    print("      docker compose restart api\n")

    print_info("🚀 To train a new model with MLflow:")
    print("   export DISABLE_MLFLOW_TRACKING=false")
    print("   export MLFLOW_TRACKING_URI=http://localhost:5001")
    print("   python machine_learning/train_model.py --version v3\n")


def print_failure_message():
    """Display the failure message."""
    print(f"\n{RED}{'='*40}{RESET}")
    print(f"{RED}{'❌ FAILURE':^40}{RESET}")
    print(f"{RED}{'='*40}{RESET}\n")

    print_error("Model registration failed")
    print_warning("Check the logs above for more details")


def main():
    """Main function."""
    print_header("MLFLOW ACTIVATION & REGISTRATION")

    # Step 1: Check MLflow
    if not check_mlflow_server():
        sys.exit(1)

    # Step 2: Configure environment
    configure_environment()

    # Step 3: Register the model
    if register_model():
        print_success_message()
        sys.exit(0)
    else:
        print_failure_message()
        sys.exit(1)


if __name__ == "__main__":
    main()
