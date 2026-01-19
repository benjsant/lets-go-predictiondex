import subprocess
import sys
import time
import os
from pathlib import Path
import psycopg2

ETL_FLAG = Path("/app/extraction_pokemon/.etl_done")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")


def wait_for_db(timeout=60):
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


def run_etl_once():
    if ETL_FLAG.exists():
        print("ℹ️ ETL already done, skipping")
        return

    print("🚀 Running ETL Pokémon Let's Go pipeline")
    try:
        subprocess.run(
            ["python", "/app/extraction_pokemon/run_all_in_one.py"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("❌ ETL failed")
        sys.exit(1)

    ETL_FLAG.touch()
    print("✅ ETL COMPLETED")


def start_api():
    cmd = [
        "uvicorn",
        "extraction_pokemon.api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
    ]
    if DEV_MODE:
        cmd.append("--reload")

    print(f"🚀 Starting API {'(DEV MODE)' if DEV_MODE else ''}")
    subprocess.run(cmd, check=True)


def main():
    wait_for_db()
    run_etl_once()
    start_api()


if __name__ == "__main__":
    main()
