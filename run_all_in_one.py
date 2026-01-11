# run_all_in_one.py
"""
All-in-one ETL bootstrap script for Pokémon Let's Go
===================================================

This script orchestrates the complete ETL pipeline of the Pokémon Let's Go
project from a single entry point.

It sequentially executes all required ETL steps in a controlled and
fail-fast manner, ensuring database consistency and reproducibility.

Pipeline steps executed:
1. Database initialization and reference data setup
2. CSV-based data extraction and loading (deterministic core dataset)
3. External API enrichment using PokéAPI
4. Web scraping of Poképédia for Pokémon Let's Go moves
5. Post-processing transformations (Mega Pokémon move inheritance)

Design principles:
- Explicit execution order
- Clear separation of ETL responsibilities
- Immediate failure on error (fail-fast)
- Simplicity over orchestration complexity

This script intentionally avoids heavy orchestration tools (Airflow, Prefect)
because:
- The pipeline is linear and deterministic
- Execution frequency is low (one-shot or batch-based)
- Operational overhead would outweigh the benefits

Execution contexts:
- Local development
- Docker containers
- CI/CD pipelines
- Initial project bootstrap

ETL scope:
- E1: End-to-end ETL orchestration and data lifecycle control

Note:
This script does not implement parallelism or scheduling.
Those concerns are deferred to E3 or future production scaling.
"""

import subprocess
import sys


def run(cmd, label, cwd=None):
    """
    Execute a subprocess command as a single ETL step.

    This helper function standardizes:
    - Logging of the executed step
    - Error handling
    - Immediate termination on failure

    Args:
        cmd (list[str]):
            Command and arguments to execute (e.g. ["python", "script.py"])
        label (str):
            Human-readable label describing the ETL step
        cwd (str | None):
            Optional working directory for the command execution

    Behavior:
        - Prints the step label before execution
        - Executes the command synchronously
        - Stops the entire pipeline if the command fails

    Rationale:
        In an ETL context, partial execution is often worse than failure.
        A fail-fast strategy prevents silent data corruption or
        inconsistent intermediate states.
    """
    print(f"\n▶ {label}")

    result = subprocess.run(
        cmd,
        cwd=cwd,
    )

    if result.returncode != 0:
        print(f"❌ Failed: {label}")
        sys.exit(1)


def main():
    """
    Entry point for the complete Pokémon Let's Go ETL pipeline.

    This function defines the strict execution order of all ETL phases:
    - Initialization
    - Extraction
    - Loading
    - Enrichment
    - Transformation

    Each step depends on the successful completion of the previous one.
    """

    print("🚀 ETL Pokémon Let's Go")

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

    print("\n✅ ETL COMPLETED")


if __name__ == "__main__":
    main()
