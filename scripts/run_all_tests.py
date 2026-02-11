#!/usr/bin/env python3
"""
Orchestration script to run all project tests VIA DOCKER.

Usage: python3 scripts/run_all_tests.py [--local] [--build]

By default, runs tests in an isolated Docker container (recommended).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

# ANSI Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(text):
    """Display a formatted header."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{BOLD}{text:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")


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


def check_docker():
    """Check that Docker is available."""
    print_info("Checking Docker...")

    if not shutil.which("docker"):
        print_error("Docker is not installed or not in PATH")
        return False

    # Check that Docker daemon is accessible
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5,
            check=False
        )
        if result.returncode == 0:
            print_success("Docker is available")
            return True

        print_error("Docker daemon is not accessible")
        return False
    except subprocess.TimeoutExpired:
        print_error("Docker check timeout")
        return False
    except OSError as exc:
        print_error(f"Error checking Docker: {exc}")
        return False


def check_docker_compose():
    """Check that Docker Compose is available."""
    print_info("Checking Docker Compose...")

    # Try 'docker compose' (v2)
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            timeout=5,
            check=False
        )
        if result.returncode == 0:
            print_success("Docker Compose v2 available")
            return ["docker", "compose"]
    except (subprocess.TimeoutExpired, OSError):
        pass

    # Try 'docker-compose' (v1)
    if shutil.which("docker-compose"):
        print_success("Docker Compose v1 available")
        return ["docker-compose"]

    print_error("Docker Compose is not available")
    return None


def check_services_running(compose_cmd):
    """Check that main services are running."""
    print_info("Checking Docker services...")

    try:
        result = subprocess.run(
            compose_cmd + ["ps", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )

        if result.returncode == 0:
            # Count running services
            services = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        service = json.loads(line)
                        if service.get('State') == 'running':
                            services.append(service.get('Service'))
                    except json.JSONDecodeError:
                        pass

            if len(services) >= 5: # At least 5 services (db, api, mlflow, prometheus, grafana)
                print_success(f"{len(services)} active services")
                return True

            print_warning(f"Only {len(services)} active services")
            return False

    except subprocess.TimeoutExpired:
        print_warning("Service check timeout")
    except OSError as exc:
        print_warning(f"Unable to check services: {exc}")

    return False


def start_services(compose_cmd):
    """Start all Docker services."""
    print_info("Starting Docker services...")

    # Longer timeout in CI environment (GitHub Actions is slower)
    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
    timeout_seconds = 600 if is_ci else 180

    if is_ci:
        print_info(f"CI environment - Extended timeout to {timeout_seconds}s for image build...")

    try:
        result = subprocess.run(
            compose_cmd + ["up", "-d"],
            timeout=timeout_seconds,
            check=False
        )

        if result.returncode == 0:
            print_success("Services started")
            wait_time = 45 if is_ci else 30
            print_info(f"Waiting {wait_time} seconds for services to be ready...")
            time.sleep(wait_time)
            return True

        print_error("Failed to start services")
        return False

    except subprocess.TimeoutExpired:
        print_error("Service startup timeout")
        return False
    except OSError as exc:
        print_error(f"Error during startup: {exc}")
        return False


def run_tests_in_docker(compose_cmd, build=False):
    """Run tests in a Docker container."""
    print_header("RUNNING TESTS VIA DOCKER")

    print_info("Configuration:")
    print(" - Environment: Docker (isolated)")
    print(f" - Build image: {'Yes' if build else 'No (using cache)'}")
    print(" - Required services: PostgreSQL, API, MLflow, Prometheus, Grafana")

    # Build command
    cmd = compose_cmd + ["--profile", "tests", "up"]

    if build:
        cmd.append("--build")

    cmd.extend(["--abort-on-container-exit", "--exit-code-from", "tests", "tests"])

    print_info("\nRunning tests...")
    print_info(f"Command: {' '.join(cmd)}\n")

    try:
        # Run tests (real-time output)
        result = subprocess.run(cmd, check=False)

        return result.returncode

    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
        return 130
    except OSError as exc:
        print_error(f"Error running tests: {exc}")
        return 1


def run_tests_locally():
    """Run integration tests from host (legacy)."""
    print_header("RUNNING TESTS FROM HOST")

    print_warning("Local mode (legacy) - May fail if Docker DB is not accessible")
    print_info("Running complete system test...")

    try:
        result = subprocess.run(
            [sys.executable, "tests/integration/test_complete_system.py"],
            check=False
        )
        return result.returncode
    except OSError as exc:
        print_error(f"Error: {exc}")
        return 1


def cleanup_tests_container(compose_cmd):
    """Clean up tests container after execution."""
    print_info("\nCleaning up tests container...")

    try:
        subprocess.run(
            compose_cmd + ["rm", "-f", "tests"],
            capture_output=True,
            timeout=10,
            check=False
        )
        print_success("Tests container cleaned up")
    except (subprocess.TimeoutExpired, OSError):
        pass


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run all tests via Docker (recommended)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/run_all_tests.py # Run via Docker (cache)
  python3 scripts/run_all_tests.py --build # Run via Docker (rebuild)
  python3 scripts/run_all_tests.py --local # Run from host (legacy)
        """
    )

    parser.add_argument(
        "--local",
        action="store_true",
        help="Run tests from host instead of Docker (not recommended)"
    )

    parser.add_argument(
        "--build",
        action="store_true",
        help="Rebuild Docker test image before running"
    )

    parser.add_argument(
        "--no-start",
        action="store_true",
        help="Don't start services automatically (assumes they're already running)"
    )

    args = parser.parse_args()

    print_header("FULL TESTS - Let's Go PredictionDex")

    # Local mode (legacy)
    if args.local:
        print_warning("Local mode enabled (not recommended)")
        return run_tests_locally()

    # Docker mode (recommended)
    print_success("Docker mode enabled (recommended)")

    # 1. Check Docker
    if not check_docker():
        print_error("\nDocker is not available")
        print_info("Install Docker: https://docs.docker.com/get-docker/")
        return 1

    # 2. Check Docker Compose
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        print_error("\nDocker Compose is not available")
        return 1

    # 3. Check/Start services
    if not args.no_start:
        services_running = check_services_running(compose_cmd)

        if not services_running:
            print_warning("Docker services not started")

            # In CI environment (GitHub Actions), start automatically
            is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

            if is_ci:
                print_info("CI environment detected - starting services automatically...")
                if not start_services(compose_cmd):
                    print_error("\nUnable to start services")
                    return 1
            else:
                response = input(f"\n{YELLOW}Start services now? (y/N): {RESET}")
                if response.lower() in ['y', 'yes', 'o', 'oui']:
                    if not start_services(compose_cmd):
                        print_error("\nUnable to start services")
                        return 1
                else:
                    print_error("\nTests require services to be running")
                    print_info("Start manually: docker compose up -d")
                    return 1

    # 4. Run tests
    exit_code = run_tests_in_docker(compose_cmd, build=args.build)

    # 5. Cleanup
    cleanup_tests_container(compose_cmd)

    # 6. Summary
    print_header("FINAL RESULT")

    if exit_code == 0:
        print_success("ALL TESTS PASSED")
        print_info("\nReports available in: ./reports/")
        return 0

    print_error(f"TESTS FAILED (code: {exit_code})")
    print_info("\nCheck the logs above for details")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
