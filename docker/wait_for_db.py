#docker/wait_for_db.py
"""
Wait for PostgreSQL to be ready before starting ETL or ML processes.
"""
import os
import sys
import time
import psycopg2
from psycopg2 import OperationalError

# Database connection parameters from environment
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")

MAX_RETRIES = 30
RETRY_INTERVAL = 2  # seconds


def wait_for_db():
    """
    Wait for PostgreSQL to be ready to accept connections.
    Retries up to MAX_RETRIES times with RETRY_INTERVAL between attempts.
    """
    print(f"⏳ Waiting for PostgreSQL at {DB_HOST}:{DB_PORT}...", flush=True)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=3
            )
            conn.close()
            print(f"✅ PostgreSQL is ready! (attempt {attempt}/{MAX_RETRIES})", flush=True)
            return True
        except OperationalError as e:
            print(f"⏳ Attempt {attempt}/{MAX_RETRIES}: DB not ready yet... ({e})", flush=True)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_INTERVAL)
            else:
                print(f"❌ Failed to connect to PostgreSQL after {MAX_RETRIES} attempts", flush=True)
                return False

    return False


if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    else:
        sys.exit(1)
