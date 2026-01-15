# run_all_in_one.py
"""
All-in-one ETL bootstrap script for Pokémon Let's Go
===================================================

This version:
- Avoids re-running ETL if already done (.etl_done)
- Supports --force flag to rerun ETL
- Pure Python, Windows-friendly
"""

import subprocess
import sys
from pathlib import Path

ETL_FLAG_FILE = Path(__file__).parent / ".etl_done"


def run(cmd, label, cwd=None):
    """
    Execute a subprocess command as a single ETL step.
    Stops immediately if the command fails.
    """
    print(f"\n▶ {label}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Failed: {label}")
        sys.exit(1)


def main(force=False):
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
        ["python", "app/scripts/etl_init_db.py"],
        "Init: database schema & reference data"
    )

    # --------------------------------------------------
    # Core ETL (CSV)
    # --------------------------------------------------
    run(
        ["python", "app/scripts/etl_load_csv.py"],
        "Extract/Load: CSV reference data"
    )

    # --------------------------------------------------
    # External enrichment (API)
    # --------------------------------------------------
    run(
        ["python", "app/scripts/etl_enrich_pokeapi.py"],
        "Enrich: PokéAPI"
    )

    # --------------------------------------------------
    # Web scraping (Poképédia)
    # --------------------------------------------------
    run(
        ["scrapy", "crawl", "letsgo_moves_sql"],
        "Extract: Poképédia (LGPE moves)",
        cwd="pokepedia_scraper"
    )

    # --------------------------------------------------
    # Post-processing transformations
    # --------------------------------------------------
    run(
        ["python", "app/scripts/etl_post_process.py"],
        "Transform: inherit Mega Pokémon moves"
    )

    # --------------------------------------------------
    # Mark ETL as done
    # --------------------------------------------------
    ETL_FLAG_FILE.touch()
    print("\n✅ ETL COMPLETED")


if __name__ == "__main__":
    force_rerun = "--force" in sys.argv
    main(force=force_rerun)
