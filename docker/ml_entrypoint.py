#!/usr/bin/env python3
"""
ML Builder Entrypoint - Wait for DB and build ML dataset
"""
import subprocess
import sys
import time
import os
import psycopg2

# Database connection from environment
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")


def wait_for_db(timeout=60):
    """Wait for PostgreSQL to be ready."""
    print("⏳ Waiting for PostgreSQL to be ready...", flush=True)
    start_time = time.time()

    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME,
                connect_timeout=3
            )
            conn.close()
            print(f"✅ PostgreSQL {DB_NAME} is ready!", flush=True)
            return True
        except psycopg2.OperationalError as e:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"❌ Timeout waiting for PostgreSQL after {timeout}s", flush=True)
                return False
            print(f"⏳ DB not ready yet (elapsed: {int(elapsed)}s)...", flush=True)
            time.sleep(2)


def run_ml_builder():
    """Run the ML dataset builder."""
    print("🚀 Starting ML dataset builder...", flush=True)
    result = subprocess.run(
        ["python", "machine_learning/build_dataset_ml_v1.py"],
        check=False
    )

    if result.returncode == 0:
        print("✅ ML dataset built successfully!", flush=True)
        return True
    else:
        print(f"❌ ML builder failed with exit code {result.returncode}", flush=True)
        return False


def main():
    """Main entrypoint."""
    print("🐳 ML Builder Container Starting...", flush=True)

    # Wait for database
    if not wait_for_db(timeout=60):
        print("❌ Database not available. Exiting.", flush=True)
        sys.exit(1)

    # Run ML builder
    if not run_ml_builder():
        print("❌ ML builder failed. Exiting.", flush=True)
        sys.exit(1)

    print("✅ ML builder container finished successfully.", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
