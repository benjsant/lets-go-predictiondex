# run_all_in_one.py
"""
All-in-one ETL bootstrap script for Pokémon Let's Go
===================================================

Features:
- Checks database for ETL completion instead of file flags
- Supports --force flag to rerun ETL
- Pure Python, Windows-friendly
- Path-safe (local + Docker)
"""

import subprocess
import sys
import os
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
SCRAPER_DIR = BASE_DIR / "pokepedia_scraper"


def run(cmd: list[str], label: str, cwd: Path | None = None):
    """
    Execute a subprocess command as a single ETL step.
    Stops immediately if the command fails.
    """
    print(f"\n▶ {label}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=False
    )
    if result.returncode != 0:
        print(f"❌ Failed: {label}")
        sys.exit(1)


def check_etl_already_done() -> bool:
    """
    Check if ETL has already been completed by querying the database.
    Returns True if Pokemon table has data, False otherwise.
    """
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "letsgo_user"),
            password=os.getenv("POSTGRES_PASSWORD", "letsgo_password"),
            dbname=os.getenv("POSTGRES_DB", "letsgo_db"),
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pokemon;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0
    except Exception:
        # If table doesn't exist or any error, assume ETL not done
        return False


def main(force: bool = False):
    """
    Run the full ETL pipeline if not already done or if forced.
    """
    if check_etl_already_done() and not force:
        print("ℹ️  ETL already done (Pokemon data exists in DB). Skipping. Use --force to rerun.")
        return

    print("🚀 Running full ETL Pokémon Let's Go pipeline")

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------
    run(
        ["python", str(SCRIPTS_DIR / "etl_init_db.py")],
        "Init: database schema & reference data"
    )

    # --------------------------------------------------
    # Core ETL (CSV)
    # --------------------------------------------------
    run(
        ["python", str(SCRIPTS_DIR / "etl_load_csv.py")],
        "Extract/Load: CSV reference data"
    )

    # --------------------------------------------------
    # External enrichment (PokéAPI)
    # --------------------------------------------------
    run(
        ["python", str(SCRIPTS_DIR / "etl_enrich_pokeapi.py")],
        "Enrich: PokéAPI"
    )

    # --------------------------------------------------
    # Web scraping (Poképédia)
    # --------------------------------------------------
    run(
        ["scrapy", "crawl", "letsgo_moves_sql"],
        "Extract: Poképédia (LGPE moves)",
        cwd=SCRAPER_DIR
    )

    # --------------------------------------------------
    # Post-processing transformations
    # --------------------------------------------------
    run(
        ["python", str(SCRIPTS_DIR / "etl_post_process.py")],
        "Transform: inherit Mega Pokémon moves"
    )

    print("\n✅ ETL COMPLETED")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
