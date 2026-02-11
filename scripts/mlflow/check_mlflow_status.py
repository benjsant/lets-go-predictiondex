#!/usr/bin/env python3
"""
MLflow Status Verification Script.

Usage: python3 scripts/mlflow/check_mlflow_status.py
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

# ANSI Colors
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
RESET = "\033[0m"


def print_header(text):
    """Display a formatted header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    """Display a success message."""
    print(f"{GREEN}{text}{RESET}")


def print_error(text):
    """Display an error message."""
    print(f"{RED}{text}{RESET}")


def print_warning(text):
    """Display a warning message."""
    print(f"{YELLOW}{text}{RESET}")


def print_info(text):
    """Display an info message."""
    print(f"{CYAN}{text}{RESET}")


def check_mlflow_server():
    """Check if MLflow server is accessible."""
    print_header("1. MLFLOW SERVER CHECK")

    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print_success("MLflow Server is UP at http://localhost:5001")
            print_info("Access UI: http://localhost:5001")
            return True

        print_error(f"MLflow Server responds with code {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print_error("MLflow Server is not accessible")
        print_warning("Start with: docker compose up -d mlflow")
        return False
    except requests.exceptions.RequestException as exc:
        print_error(f"Connection error: {exc}")
        return False


def check_experiments():
    """List MLflow experiments."""
    print_header("2. MLFLOW EXPERIMENTS")

    try:
        response = requests.get(
            "http://localhost:5001/api/2.0/mlflow/experiments/search?max_results=50",
            timeout=5
        )

        if response.status_code != 200:
            print_error("Unable to retrieve experiments")
            return False

        data = response.json()
        experiments = data.get("experiments", [])

        if not experiments:
            print_warning("No experiments found")
            return False

        print_success(f"{len(experiments)} experiment(s) found:")
        for exp in experiments:
            exp_id = exp.get("experiment_id")
            exp_name = exp.get("name")
            created = exp.get("creation_time")
            if created:
                created_date = datetime.fromtimestamp(created / 1000).strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_date = "N/A"
            print(f" • ID {exp_id}: {exp_name} (created {created_date})")

        return True

    except requests.exceptions.RequestException as exc:
        print_error(f"Error retrieving experiments: {exc}")
        return False


def check_runs():
    """Check training runs."""
    print_header("3. TRAINING RUNS")

    try:
        response = requests.post(
            "http://localhost:5001/api/2.0/mlflow/runs/search",
            json={"max_results": 10},
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code != 200:
            print_error("Unable to retrieve runs")
            return False

        data = response.json()
        runs = data.get("runs", [])

        if not runs:
            print_warning("No training runs found")
            print_info("Experiments exist but no runs recorded")
            return False

        print_success(f"{len(runs)} training run(s) found:")

        for i, run in enumerate(runs[:5], 1): # Display max 5 runs
            info = run.get("info", {})
            data_run = run.get("data", {})

            run_id = info.get("run_id", "N/A")[:8]
            run_name = info.get("run_name", "Unnamed")
            status = info.get("status", "UNKNOWN")
            exp_id = info.get("experiment_id")

            # Get metrics
            metrics = data_run.get("metrics", [])
            metrics_dict = {m["key"]: m["value"] for m in metrics}

            print(f"\n {i}. Run: {run_name} (ID: {run_id}...)")
            print(f" Status: {status}")
            print(f" Experiment ID: {exp_id}")

            if metrics_dict:
                print(" Metrics:")
                for key, value in sorted(metrics_dict.items()):
                    if isinstance(value, float):
                        print(f" - {key}: {value:.4f}")
                    else:
                        print(f" - {key}: {value}")

        return True

    except requests.exceptions.RequestException as exc:
        print_error(f"Error retrieving runs: {exc}")
        return False


def check_registered_models():
    """Check registered models in Model Registry."""
    print_header("4. MODEL REGISTRY")

    try:
        response = requests.get(
            "http://localhost:5001/api/2.0/mlflow/registered-models/search?max_results=50",
            timeout=5
        )

        if response.status_code != 200:
            print_error("Unable to retrieve registered models")
            return False

        data = response.json()
        models = data.get("registered_models", [])

        if not models:
            print_warning("No models registered in Model Registry")
            print_info("To register existing model:")
            print_info(" python3 scripts/mlflow/register_existing_model.py")
            return False

        print_success(f"{len(models)} registered model(s):")
        for model in models:
            model_name = model.get("name")
            creation_time = model.get("creation_timestamp")
            if creation_time:
                created_date = datetime.fromtimestamp(creation_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_date = "N/A"
            latest_versions = model.get("latest_versions", [])

            print(f" • {model_name} (created {created_date})")

            if latest_versions:
                for version in latest_versions:
                    version_num = version.get("version")
                    stage = version.get("current_stage", "None")
                    print(f" - Version {version_num} ({stage})")

        return True

    except requests.exceptions.RequestException as exc:
        print_error(f"Error retrieving models: {exc}")
        return False


def check_local_models():
    """Check local models (pkl files)."""
    print_header("5. LOCAL MODELS (FILES)")

    models_dir = Path("models")

    if not models_dir.exists():
        print_error("Directory 'models/' not found")
        return False

    pkl_files = list(models_dir.glob("*.pkl"))
    json_files = list(models_dir.glob("*metadata*.json"))

    if not pkl_files:
        print_warning("No .pkl files found in models/")
        return False

    print_success(f"{len(pkl_files)} model(s) found:")
    for pkl_file in pkl_files:
        size = os.path.getsize(pkl_file) / (1024 * 1024) # MB
        print(f" • {pkl_file.name} ({size:.2f} MB)")

    if json_files:
        print_success(f"{len(json_files)} metadata file(s) found:")
        for json_file in json_files:
            print(f" • {json_file.name}")

    return True


def print_summary(checks):
    """Display verification summary."""
    print_header("SUMMARY")

    total = len(checks)
    passed = sum(checks.values())

    print(f"Checks: {passed}/{total} passed\n")

    for check_name, check_result in checks.items():
        status = f"{GREEN}PASS{RESET}" if check_result else f"{RED}FAIL{RESET}"
        print(f" {status} {check_name}")

    print()

    if passed == total:
        print_success("MLflow is fully operational!")
        print_info("Access UI: http://localhost:5001")
    elif checks.get("MLflow Server", False):
        print_warning("MLflow works but some elements are missing")
        if not checks.get("Registered Models", False):
            print_info("\nTo register existing model:")
            print(f"{CYAN} python3 scripts/mlflow/register_existing_model.py{RESET}")
    else:
        print_error("MLflow is not operational")
        print_info("\nTo start MLflow:")
        print(f"{CYAN} docker compose up -d mlflow{RESET}")

    print()


def main():
    """Main function."""
    print(f"{CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║ MLFLOW STATUS CHECK - PREDICTIONDEX ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(RESET)

    checks = {}

    # 1. Check server
    checks["MLflow Server"] = check_mlflow_server()

    if not checks["MLflow Server"]:
        print_summary(checks)
        sys.exit(1)

    # 2. Check experiments
    checks["Experiments"] = check_experiments()

    # 3. Check runs
    checks["Training Runs"] = check_runs()

    # 4. Check Model Registry
    checks["Registered Models"] = check_registered_models()

    # 5. Check local models
    checks["Local Models"] = check_local_models()

    # Summary
    print_summary(checks)

    # Exit code
    if all(checks.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
