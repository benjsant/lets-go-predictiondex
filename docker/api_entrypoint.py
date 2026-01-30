"""
API Entrypoint Script

This script serves as the entrypoint for the API container in the Let's Go PredictionDex project.
It performs the following tasks:

1. Waits for the PostgreSQL database to be ready before starting the API.
2. Launches the FastAPI application using Uvicorn.
3. Supports a development mode with automatic reload.

Environment Variables:
----------------------
- DEV_MODE (str): If set to "true", enables development mode with automatic reload.
- POSTGRES_HOST (str): Database host (default: "db").
- POSTGRES_PORT (int): Database port (default: 5432).
- POSTGRES_USER (str): Database username (default: "letsgo_user").
- POSTGRES_PASSWORD (str): Database password (default: "letsgo_password").
- POSTGRES_DB (str): Database name (default: "letsgo_db").

Usage:
------
Run this script as the main entrypoint in the API container.
It will block until the database is ready, then start the API server.
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import psycopg2

# Development mode flag
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# Database connection parameters
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")


def wait_for_db(timeout=60):
    """
    Wait for PostgreSQL database to be ready.

    Attempts to connect to the database repeatedly until successful or until
    the timeout is reached.

    Parameters:
    -----------
    timeout : int
        Maximum number of seconds to wait for the database before exiting
        with an error.

    Behavior:
    ---------
    - Prints status messages to stdout.
    - Exits the script with code 1 if the database is not ready within the timeout.
    """
    start_time = time.time()
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME,
            )
            conn.close()
            print(f"✅ Database {DB_NAME} is ready")
            return
        except psycopg2.OperationalError:
            if time.time() - start_time > timeout:
                print("❌ Timeout waiting for database")
                sys.exit(1)
            print("⏳ Waiting for database...")
            time.sleep(2)


def start_api():
    """
    Start the FastAPI application using Uvicorn.

    Uses the environment variable DEV_MODE to determine whether to
    enable automatic reload for development.

    Behavior:
    ---------
    - Binds the API server to 0.0.0.0 on port 8080.
    - Blocks until the API server stops.
    - Raises an exception if the subprocess exits with a non-zero code.
    """
    cmd = [
        "uvicorn",
        "api_pokemon.main:app",
        "--host", "0.0.0.0",
        "--port", "8080",  # Port modified from default 8000
    ]
    if DEV_MODE:
        cmd.append("--reload")
    subprocess.run(cmd, check=True)


def main():
    """
    Main entrypoint function for the API container.

    Workflow:
    ---------
    1. Wait for the PostgreSQL database to become available.
    2. Start the FastAPI application.
    """
    wait_for_db()
    start_api()


if __name__ == "__main__":
    main()
