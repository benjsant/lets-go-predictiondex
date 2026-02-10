# docker/etl_entrypoint.py
"""
etl_entrypoint.py

Docker entrypoint script responsible for launching the ETL (Extract, Transform,
Load) pipeline once the PostgreSQL database is available.

This script is designed to be used as the main entrypoint of an ETL container.
It ensures proper startup sequencing in containerized environments by waiting
for the database service to be ready before executing the ETL pipeline.

Typical responsibilities include:
- Waiting for PostgreSQL to accept connections.
- Executing the ETL pipeline as a separate Python process.
- Propagating success or failure via appropriate exit codes.

Exit Codes
----------
0 : Successful execution (database available and ETL pipeline completed).
1 : Failure during database availability check or ETL pipeline execution.

Environment Variables
---------------------
Database configuration:
- POSTGRES_HOST : str
    Hostname or service name of the PostgreSQL server (default: "db").
- POSTGRES_PORT : int
    PostgreSQL port (default: 5432).
- POSTGRES_DB : str
    Database name (default: "letsgo_db").
- POSTGRES_USER : str
    Database user (default: "letsgo_user").
- POSTGRES_PASSWORD : str
    Database password (default: "letsgo_password").

Typical Usage
-------------
This script is executed automatically when the ETL Docker container starts:

    python docker/etl_entrypoint.py
"""

import subprocess
import sys
import time
import os
import psycopg2

# Database connection parameters retrieved from environment variables.
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")


def wait_for_db(timeout=60):
    """
    Wait until the PostgreSQL database is ready to accept connections.

    This function repeatedly attempts to establish a connection to PostgreSQL
    using the credentials provided via environment variables. It blocks execution
    until a connection succeeds or the specified timeout is exceeded.

    This mechanism prevents the ETL pipeline from starting before the database
    service has fully initialized, which is a common issue in Docker-based
    deployments.

    Parameters
    ----------
    timeout : int, optional
        Maximum number of seconds to wait for the database to become available
        (default: 60).

    Returns
    -------
    bool
        True if the database becomes available within the timeout window.
        False if the timeout is exceeded without a successful connection.

    Side Effects
    ------------
    - Logs progress information to stdout for observability in container logs.
    - Introduces retry delays using `time.sleep`.

    Common Failure Causes
    ---------------------
    - PostgreSQL container still starting
    - Invalid database credentials
    - Network or service resolution issues
    """
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
        except psycopg2.OperationalError:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"❌ Timeout waiting for PostgreSQL after {timeout}s", flush=True)
                return False
            print(f"⏳ DB not ready yet (elapsed: {int(elapsed)}s)...", flush=True)
            time.sleep(2)


def run_etl():
    """
    Execute the ETL pipeline.

    This function launches the ETL process as a separate Python subprocess.
    The ETL logic itself is implemented in `etl_pokemon/pipeline.py`.

    The function captures the subprocess exit code and reports success or
    failure accordingly, allowing the container to exit with a meaningful
    status code.

    Returns
    -------
    bool
        True if the ETL pipeline completes successfully (exit code 0).
        False if the ETL pipeline fails or returns a non-zero exit code.

    Side Effects
    ------------
    - Executes an external Python process via `subprocess.run`.
    - Streams ETL logs directly to stdout.
    """
    print("🚀 Starting ETL pipeline...", flush=True)
    result = subprocess.run(
        ["python", "etl_pokemon/pipeline.py"],
        check=False
    )

    if result.returncode == 0:
        print("✅ ETL pipeline completed successfully!", flush=True)
        return True
    else:
        print(
            f"❌ ETL pipeline failed with exit code {result.returncode}",
            flush=True
        )
        return False


def main():
    """
    Main container entrypoint for the ETL service.

    This function controls the full lifecycle of the ETL container:
    1. Logs container startup.
    2. Waits for the PostgreSQL database to become available.
    3. Executes the ETL pipeline.
    4. Exits with an appropriate status code for Docker and CI/CD systems.
    """
    print("🐳 ETL Container Starting...", flush=True)

    # Wait for database availability
    if not wait_for_db(timeout=60):
        print("❌ Database not available. Exiting.", flush=True)
        sys.exit(1)

    # Run ETL pipeline
    if not run_etl():
        print("❌ ETL failed. Exiting.", flush=True)
        sys.exit(1)

    print("✅ ETL container finished successfully.", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
