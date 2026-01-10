"""
All-in-one bootstrap script for Pokémon Let's Go
-----------------------------------------------
- init database & reference data
- load CSV data
- enrich via PokéAPI
- scrape Poképédia (LGPE moves)
- inherit mega moves
"""

import subprocess
import sys


def run(cmd, label, cwd=None):
    print(f"\n▶ {label}")

    result = subprocess.run(
        cmd,
        cwd=cwd,
    )

    if result.returncode != 0:
        print(f"❌ Failed: {label}")
        sys.exit(1)


def main():
    print("🚀 ETL Pokémon Let's Go")

    run(["python", "app/scripts/etl_init_db.py"], "Extract: init & reference data")
    run(["python", "app/scripts/etl_load_csv.py"], "Extract/Load: CSV")
    run(["python", "app/scripts/etl_enrich_pokeapi.py"], "Enrich: PokéAPI")

    run(
        ["scrapy", "crawl", "letsgo_moves_sql"],
        "Extract: Poképédia (LGPE moves)",
        cwd="pokepedia_scraper"
    )

    run(
        ["python", "app/scripts/etl_post_process.py"],
        "Transform: inherit Mega moves"
    )

    print("\n✅ ETL COMPLETED")



if __name__ == "__main__":
    main()
