#!/usr/bin/env python3
"""
ETL Entrypoint - Wait for DB and run ETL pipeline
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


def run_etl():
    """Run the ETL pipeline."""
    print("🚀 Starting ETL pipeline...", flush=True)
    result = subprocess.run(
        ["python", "etl_pokemon/pipeline.py"],
        check=False
    )

    if result.returncode == 0:
        print("✅ ETL pipeline completed successfully!", flush=True)
        return True
    else:
        print(f"❌ ETL pipeline failed with exit code {result.returncode}", flush=True)
        return False


def main():
    """Main entrypoint."""
    print("🐳 ETL Container Starting...", flush=True)

    # Wait for database
    if not wait_for_db(timeout=60):
        print("❌ Database not available. Exiting.", flush=True)
        sys.exit(1)

    # Run ETL
    if not run_etl():
        print("❌ ETL failed. Exiting.", flush=True)
        sys.exit(1)

    print("✅ ETL container finished successfully.", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
