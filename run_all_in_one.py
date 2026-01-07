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
    # 1️⃣ Init DB + reference tables
    run(
        ["python", "app/scripts/init_db.py"],
        "Init DB & reference data"
    )

    # 2️⃣ Load CSV
    run(
        ["python", "app/scripts/load_all_csv.py"],
        "Load CSV data"
    )

    # 3️⃣ Enrich via PokéAPI
    run(
        ["python", "app/scripts/load_pokeapi.py"],
        "Enrich Pokémon via PokéAPI"
    )

    # 4️⃣ Scrape Poképédia
    run(
        ["scrapy", "crawl", "letsgo_moves_sql"],
        "Scrape Poképédia (LGPE moves)",
        cwd="pokepedia_scraper"
    )

    # 5️⃣ Héritage Méga
    run(
        ["python", "app/scripts/inherit_mega_moves.py"],
        "Inherit Mega moves"
    )

    print("\n✅ ALL DONE — database fully initialized")


if __name__ == "__main__":
    main()
