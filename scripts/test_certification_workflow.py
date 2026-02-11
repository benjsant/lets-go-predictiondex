#!/usr/bin/env python3
"""
Local test script for E1/E3 certification workflow.

Simulates GitHub Actions execution locally to verify before push.

Usage:
    python scripts/test_certification_workflow.py
    python scripts/test_certification_workflow.py --job e1-data-validation
    python scripts/test_certification_workflow.py --job e3-c13-mlops
    python scripts/test_certification_workflow.py --all
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# ANSI Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(text: str):
    """Display a formatted header."""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{BOLD}{text:^80}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")


def print_step(step: str):
    """Display a step."""
    print(f"{CYAN}▶ {step}{RESET}")


def print_success(text: str):
    """Display a success message."""
    print(f"{GREEN}{text}{RESET}")


def print_error(text: str):
    """Display an error message."""
    print(f"{RED}{text}{RESET}")


def print_warning(text: str):
    """Display a warning message."""
    print(f"{YELLOW}{text}{RESET}")


def run_command(cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict] = None) -> bool:
    """Execute a command and return True if successful."""
    try:
        subprocess.run(
            cmd,
            cwd=cwd,
            env=env or os.environ.copy(),
            capture_output=False,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        print_error(f"Command failed: {' '.join(cmd)}")
        return False
    except OSError as exc:
        print_error(f"Error: {exc}")
        return False


def check_prerequisites() -> bool:
    """Check prerequisites."""
    print_header("CHECKING PREREQUISITES")

    required_tools = {
        'python3': 'Python 3.11+',
        'docker': 'Docker',
        'docker-compose': 'Docker Compose (or "docker compose")',
        'pip': 'pip',
    }

    all_ok = True
    for tool, name in required_tools.items():
        if subprocess.run(['which', tool], capture_output=True, check=False).returncode == 0:
            print_success(f"{name} found")
        else:
            # Try "docker compose" if "docker-compose" doesn't exist
            if tool == 'docker-compose':
                if subprocess.run(['docker', 'compose', 'version'],
                                  capture_output=True, check=False).returncode == 0:
                    print_success(f"{name} found (Docker Compose v2)")
                    continue
            print_error(f"{name} not found")
            all_ok = False

    # Check Python version
    try:
        result = subprocess.run(['python3', '--version'],
                                capture_output=True, text=True, check=False)
        version = result.stdout.strip()
        print_success(f"Python version: {version}")
    except OSError:
        print_error("Unable to check Python version")
        all_ok = False

    return all_ok


def setup_environment() -> Dict[str, str]:
    """Configure test environment."""
    print_header("CONFIGURING ENVIRONMENT")

    env = os.environ.copy()

    # Common variables
    env_vars = {
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'letsgo_test',
        'POSTGRES_USER': 'letsgo_user',
        'POSTGRES_PASSWORD': 'letsgo_password',
        'PYTHONPATH': str(Path.cwd()),
        'DISABLE_MLFLOW_TRACKING': 'true',
        'ML_SKIP_IF_EXISTS': 'true',
    }

    for key, value in env_vars.items():
        env[key] = value
        print_step(f"{key}={value}")

    print_success("Environment configured")
    return env


def test_e1_data_validation(env: Dict[str, str]) -> bool:
    """Test E1 job - Data Validation."""
    print_header("JOB E1: DATA COLLECTION AND PROCESSING")

    steps = [
        ("E1.1 - Collect data",
         ["pytest", "tests/etl/", "-v", "-k",
          "test_pokemon_fetcher or test_pokepedia_scraper", "--tb=short"]),

        ("E1.3 - Database structure",
         ["pytest", "tests/core/db/", "-v", "--tb=short"]),

        ("E1.4 - Features",
         ["pytest", "tests/ml/test_features.py", "-v", "--tb=short"]),
    ]

    results = []
    for step_name, cmd in steps:
        print_step(step_name)
        success = run_command(cmd, env=env)
        results.append(success)

        if success:
            print_success(f"{step_name} PASSED")
        else:
            print_warning(f"{step_name} FAILED (non-blocking for test)")

    # Check documentation
    print_step("E1.5 - Check documentation")
    docs = [
        Path("etl_pokemon/README.md"),
        Path("README.md"),
    ]

    for doc in docs:
        if doc.exists():
            print_success(f"{doc} found")
        else:
            print_warning(f"{doc} missing")

    return all(results)


def test_e3_c9_api_rest(env: Dict[str, str]) -> bool:
    """Test C9 job - REST API."""
    print_header("JOB C9: REST API EXPOSING AI")

    print_step("Test API with AI")
    success = run_command(
        ["pytest", "tests/api/test_prediction_api.py", "-v", "--tb=short"],
        env=env
    )

    if success:
        print_success("API tests passed")
    else:
        print_warning("API tests failed")

    print_step("API Coverage")
    run_command(
        ["pytest", "tests/api/", "-v", "--cov=api_pokemon",
         "--cov-report=term-missing"],
        env=env
    )

    return success


def test_e3_c10_integration(env: Dict[str, str]) -> bool:
    """Test C10 job - Application Integration."""
    print_header("JOB C10: APPLICATION INTEGRATION")

    print_step("Check interface structure")
    interface_files = [
        Path("interface/app.py"),
        Path("interface/pages/2_Compare.py"),
        Path("interface/services/api_client.py"),
        Path("interface/services/prediction_service.py"),
    ]

    all_found = True
    for file in interface_files:
        if file.exists():
            print_success(f"{file} found")
        else:
            print_error(f"{file} missing")
            all_found = False

    print_step("Test interface")
    run_command(
        ["pytest", "tests/interface/", "-v", "--tb=short"],
        env=env
    )

    return all_found


def test_e3_c11_monitoring(env: Dict[str, str]) -> bool:
    """Test C11 job - Monitoring."""
    print_header("JOB C11: AI MODEL MONITORING")

    print_step("Check monitoring infrastructure")
    monitoring_files = [
        Path("api_pokemon/monitoring/drift_detection.py"),
        Path("docker/prometheus/prometheus.yml"),
        Path("docker/grafana"),
    ]

    for file in monitoring_files:
        if file.exists():
            print_success(f"{file} found")
        else:
            print_warning(f"{file} missing")

    print_step("Test monitoring")
    success = run_command(
        ["pytest", "tests/monitoring/", "-v", "--tb=short"],
        env=env
    )

    return success


def test_e3_c12_optimization(env: Dict[str, str]) -> bool:
    """Test C12 job - Optimization."""
    print_header("JOB C12: MODEL OPTIMIZATION")

    print_step("Test ML")
    success = run_command(
        ["pytest", "tests/ml/", "-v", "--tb=short"],
        env=env
    )

    print_step("Test inference")
    run_command(
        ["pytest", "tests/ml/test_model_inference.py", "-v", "--tb=short"],
        env=env
    )

    return success


def test_e3_c13_mlops(env: Dict[str, str]) -> bool:
    """Test C13 job - MLOps CI/CD."""
    print_header("JOB C13: MLOPS AND CI/CD")

    print_step("Check GitHub Actions workflows")
    workflows_dir = Path(".github/workflows")

    if workflows_dir.exists():
        workflows = list(workflows_dir.glob("*.yml"))
        print_success(f"{len(workflows)} workflows found:")
        for workflow in workflows:
            print(f" • {workflow.name}")
    else:
        print_error(".github/workflows/ directory missing")
        return False

    print_step("Test ML pipeline")
    success = run_command(
        ["pytest", "tests/ml/", "-v", "--cov=machine_learning",
         "--cov-report=term-missing"],
        env=env
    )

    print_step("Check ML artifacts")
    models_dir = Path("models")
    if models_dir.exists():
        models = list(models_dir.glob("*.pkl")) + list(models_dir.glob("*.json"))
        if models:
            print_success(f"{len(models)} artifacts found in models/")
        else:
            print_warning("No models found (normal if not trained yet)")

    return success


def generate_report(results: Dict[str, bool]):
    """Generate final report."""
    print_header("E1/E3 CERTIFICATION REPORT")

    print(f"\n{BOLD}Results by job:{RESET}\n")

    # E1
    print(f"{BOLD}BLOCK E1: Data Collection and Processing{RESET}")
    e1_result = results.get('e1-data-validation', False)
    status = f"{GREEN}VALIDATED{RESET}" if e1_result else f"{RED}FAILED{RESET}"
    print(f" E1 Data Validation: {status}\n")

    # E3
    print(f"{BOLD}BLOCK E3: AI Production Integration{RESET}")
    e3_jobs = [
        ('e3-c9-api-rest', 'C9 - REST API with AI'),
        ('e3-c10-integration', 'C10 - App Integration'),
        ('e3-c11-monitoring', 'C11 - AI Monitoring'),
        ('e3-c12-optimization', 'C12 - AI Optimization'),
        ('e3-c13-mlops', 'C13 - MLOps CI/CD'),
    ]

    for job_id, job_name in e3_jobs:
        result = results.get(job_id, False)
        status = f"{GREEN}VALIDATED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f" {job_name}: {status}")

    # Global score
    total_jobs = len(results)
    passed_jobs = sum(1 for v in results.values() if v)
    score = (passed_jobs / total_jobs * 100) if total_jobs > 0 else 0

    print(f"\n{BOLD}Global Score:{RESET}")
    print(f" {passed_jobs}/{total_jobs} jobs passed ({score:.1f}%)")

    if score >= 80:
        print(f"\n{GREEN}{BOLD}PROJECT READY FOR CERTIFICATION{RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}IMPROVEMENTS NEEDED{RESET}")

    print(f"\n{BOLD} Documentation:{RESET}")
    print(" • README.md")
    print(" • docs/certification/CI_CD_CERTIFICATION_E1_E3.md")
    print(" • docs/CERTIFICATION_E1_E3_VALIDATION.md")

    print(f"\n{BOLD} Next steps:{RESET}")
    if score >= 80:
        print(" 1. Push to GitHub")
        print(" 2. Check GitHub Actions workflow")
        print(" 3. Download certification report")
        print(" 4. Prepare presentation")
    else:
        print(" 1. Fix failing tests")
        print(" 2. Re-test locally")
        print(" 3. Push to GitHub")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Local test for E1/E3 certification workflow"
    )
    parser.add_argument(
        '--job',
        choices=[
            'e1-data-validation',
            'e3-c9-api-rest',
            'e3-c10-integration',
            'e3-c11-monitoring',
            'e3-c12-optimization',
            'e3-c13-mlops',
            'all'
        ],
        default='all',
        help='Specific job to test (default: all)'
    )

    args = parser.parse_args()

    print_header("LOCAL TEST - E1/E3 CERTIFICATION WORKFLOW")
    print(f"{BOLD}Project:{RESET} Let's Go PredictionDex")
    print(f"{BOLD}Date:{RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{BOLD}Job:{RESET} {args.job}")

    # Check prerequisites
    if not check_prerequisites():
        print_error("Missing prerequisites. Install required tools.")
        return 1

    # Setup environment
    env = setup_environment()

    # Run tests
    results = {}

    if args.job in ('all', 'e1-data-validation'):
        results['e1-data-validation'] = test_e1_data_validation(env)

    if args.job in ('all', 'e3-c9-api-rest'):
        results['e3-c9-api-rest'] = test_e3_c9_api_rest(env)

    if args.job in ('all', 'e3-c10-integration'):
        results['e3-c10-integration'] = test_e3_c10_integration(env)

    if args.job in ('all', 'e3-c11-monitoring'):
        results['e3-c11-monitoring'] = test_e3_c11_monitoring(env)

    if args.job in ('all', 'e3-c12-optimization'):
        results['e3-c12-optimization'] = test_e3_c12_optimization(env)

    if args.job in ('all', 'e3-c13-mlops'):
        results['e3-c13-mlops'] = test_e3_c13_mlops(env)

    # Generate report
    generate_report(results)

    # Exit code
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
