"""
All-in-one ETL bootstrap script for Pokémon Let's Go
===================================================

Features:
- Avoids re-running ETL if already done (.etl_done)
- Supports --force flag to rerun ETL
- Pure Python, Windows-friendly
- Path-safe (local + Docker)
"""

import subprocess
import sys
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
SCRAPER_DIR = BASE_DIR / "pokepedia_scraper"

ETL_FLAG_FILE = BASE_DIR / ".etl_done"


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


def main(force: bool = False):
    """
    Run the full ETL pipeline if not already done or if forced.
    """
    if ETL_FLAG_FILE.exists() and not force:
        print("ℹ️  ETL already done. Skipping. Use --force to rerun.")
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

    # --------------------------------------------------
    # Mark ETL as done
    # --------------------------------------------------
    ETL_FLAG_FILE.touch()
    print("\n✅ ETL COMPLETED")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
