# docker/wait_for_db.py
"""
wait_for_db.py

Utility script used in Dockerized environments to block execution until a
PostgreSQL database is available and ready to accept connections.

This script is typically executed as:
- an entrypoint step,
- a pre-start hook for ETL pipelines,
- or a prerequisite for ML training or inference services.

Its main purpose is to avoid race conditions where dependent services
attempt to connect to PostgreSQL before the database container has
finished initializing.

The script retrieves database connection parameters from environment
variables, attempts to establish a connection multiple times, and exits
with an appropriate status code:
- exit code 0 if the database becomes available,
- exit code 1 if the database remains unreachable after all retries.

Environment Variables
---------------------
POSTGRES_HOST : str
    Hostname or service name of the PostgreSQL server (default: "db").
POSTGRES_PORT : int
    Port on which PostgreSQL is listening (default: 5432).
POSTGRES_DB : str
    Name of the PostgreSQL database to connect to (default: "letsgo_db").
POSTGRES_USER : str
    Database user name (default: "letsgo_user").
POSTGRES_PASSWORD : str
    Database user password (default: "letsgo_password").

Typical Usage
-------------
This script is often used in Docker Compose or Kubernetes setups, for example:

    python docker/wait_for_db.py

It ensures that downstream processes only start once the database
is reachable.
"""

import os
import sys
import time
import psycopg2
from psycopg2 import OperationalError

# Database connection parameters retrieved from environment variables.
# Defaults are provided to allow local or Docker-based execution without
# explicit configuration.
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")

# Retry configuration
MAX_RETRIES = 30
RETRY_INTERVAL = 2  # seconds


def wait_for_db():
    """
    Block execution until a PostgreSQL database is ready to accept connections.

    This function attempts to establish a connection to PostgreSQL using
    the connection parameters defined via environment variables.
    If the connection fails, it retries up to `MAX_RETRIES` times, waiting
    `RETRY_INTERVAL` seconds between each attempt.

    The function is designed to be resilient in containerized environments
    where the database service may take several seconds to start.

    Returns
    -------
    bool
        True if a connection to PostgreSQL is successfully established
        within the allowed number of retries.
        False if all connection attempts fail.

    Side Effects
    ------------
    - Prints progress and error messages to stdout for visibility in
      container logs.
    - Introduces delays between retries using `time.sleep`.

    Typical Failure Causes
    ----------------------
    - PostgreSQL container not yet initialized
    - Incorrect database credentials
    - Network or service name resolution issues
    """
    print(f"[WAIT] Waiting for PostgreSQL at {DB_HOST}:{DB_PORT}...", flush=True)

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
            print(
                f"[OK] PostgreSQL is ready! (attempt {attempt}/{MAX_RETRIES})",
                flush=True
            )
            return True
        except OperationalError as e:
            print(
                f"[WAIT] Attempt {attempt}/{MAX_RETRIES}: DB not ready yet... ({e})",
                flush=True
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_INTERVAL)
            else:
                print(
                    f"[ERROR] Failed to connect to PostgreSQL after {MAX_RETRIES} attempts",
                    flush=True
                )
                return False

    return False


if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    else:
        sys.exit(1)
