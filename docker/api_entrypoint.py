# docker/api_entrypoint.py
"""Docker entrypoint for the API container.

Waits for PostgreSQL, then starts the FastAPI server via Uvicorn.
"""

import subprocess
import sys
import time
import os
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
    """Wait for PostgreSQL to accept connections, with timeout in seconds."""
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
            print(f" Database {DB_NAME} is ready")
            return
        except psycopg2.OperationalError:
            if time.time() - start_time > timeout:
                print(" Timeout waiting for database")
                sys.exit(1)
            print(" Waiting for database...")
            time.sleep(2)


def start_api():
    """Start the FastAPI application using Uvicorn."""
    cmd = [
        "uvicorn",
        "api_pokemon.main:app",
        "--host", "0.0.0.0",
        "--port", "8080",
    ]
    if DEV_MODE:
        cmd.append("--reload")
    subprocess.run(cmd, check=True)


def main():
    """Container entrypoint: wait for DB, then start API."""
    wait_for_db()
    start_api()


if __name__ == "__main__":
    main()
