"""
All-in-one ETL bootstrap script for Pokémon Let's Go.

This script orchestrates the full ETL pipeline:
- Initializes the database schema
- Loads CSV reference data
- Enriches data using PokéAPI
- Scrapes Poképédia for LGPE moves
- Applies post-processing transformations

Features:
- Checks database state instead of relying on file flags
- Supports a --force flag to rerun the ETL
- Pure Python, Windows-friendly
- Path-safe (local execution and Docker-compatible)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
SCRAPER_DIR = BASE_DIR / "pokepedia_scraper"


def run(cmd: Sequence[str], label: str, cwd: Path | None = None) -> None:
    """
    Execute a subprocess command as a single ETL step.

    The execution stops immediately if the command fails.

    Args:
        cmd: Command and arguments to execute.
        label: Human-readable label for logging.
        cwd: Optional working directory for the command.

    Raises:
        SystemExit: If the subprocess returns a non-zero exit code.
    """
    print(f"\n▶ {label}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=False,
        check=False,
    )

    if result.returncode != 0:
        print(f"❌ Failed: {label}")
        sys.exit(1)


def check_etl_already_done() -> bool:
    """
    Check whether the ETL has already been executed.

    The check is performed by querying the database and verifying
    whether the `pokemon` table contains data.

    Returns:
        True if Pokémon data exists in the database, False otherwise.
    """
    try:
        import psycopg2  # pylint: disable=import-outside-toplevel

        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "letsgo_user"),
            password=os.getenv("POSTGRES_PASSWORD", "letsgo_password"),
            dbname=os.getenv("POSTGRES_DB", "letsgo_db"),
            connect_timeout=5,
        )

        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM pokemon;")
        count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return count > 0

    except Exception:
        # Any error (missing table, connection issue, etc.)
        # is interpreted as ETL not completed.
        return False


def main(force: bool = False) -> None:
    """
    Run the full Pokémon Let's Go ETL pipeline.

    The ETL is skipped if data already exists in the database,
    unless the --force flag is provided.

    Args:
        force: Force ETL execution even if data already exists.
    """
    if check_etl_already_done() and not force:
        print(
            "ℹ️  ETL already done (Pokémon data exists in DB). "
            "Skipping. Use --force to rerun."
        )
        return

    print("🚀 Running full ETL Pokémon Let's Go pipeline")

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------
    run(
        ["python", str(SCRIPTS_DIR / "etl_init_db.py")],
        "Init: database schema & reference data",
    )

    # --------------------------------------------------
    # Core ETL (CSV)
    # --------------------------------------------------
    run(
        ["python", str(SCRIPTS_DIR / "etl_load_csv.py")],
        "Extract/Load: CSV reference data",
    )

    # --------------------------------------------------
    # External enrichment (PokéAPI)
    # --------------------------------------------------
    run(
        ["python", str(SCRIPTS_DIR / "etl_enrich_pokeapi.py")],
        "Enrich: PokéAPI",
    )

    # --------------------------------------------------
    # Web scraping (Poképédia)
    # --------------------------------------------------
    run(
        ["scrapy", "crawl", "letsgo_moves_sql"],
        "Extract: Poképédia (LGPE moves)",
        cwd=SCRAPER_DIR,
    )

    # --------------------------------------------------
    # Post-processing transformations
    # --------------------------------------------------
    run(
        ["python", str(SCRIPTS_DIR / "etl_previous_evolution.py")],
        "Transform: inherit previous evolution Pokémon moves",
    )

    run(
        ["python", str(SCRIPTS_DIR / "etl_post_process.py")],
        "Transform: inherit Mega Pokémon moves",
    )

    print("\n✅ ETL COMPLETED")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
