import subprocess
import sys
from pathlib import Path
import threading
import os

ETL_FLAG = Path("/app/.etl_done")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"


def run(cmd, label, cwd=None):
    """Run a subprocess command and fail fast."""
    print(f"\n▶ {label}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Failed: {label}")
        sys.exit(1)


def start_uvicorn():
    cmd = [
        "uvicorn",
        "app.api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
    ]

    if DEV_MODE:
        cmd.append("--reload")

    subprocess.run(cmd)


def start_streamlit():
    cmd = [
        "streamlit", "run",
        "app/streamlit/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ]
    subprocess.run(cmd)


def main():
    # --------------------------------------------------
    # ETL (une seule fois)
    # --------------------------------------------------
    if not ETL_FLAG.exists():
        print("🚀 Running ETL Pokémon Let's Go")
        run(["python", "/app/run_all_in_one.py"], "ETL pipeline")
        ETL_FLAG.touch()
        print("✅ ETL COMPLETED")
    else:
        print("ℹ️ ETL already done, skipping")

    # --------------------------------------------------
    # Launch services
    # --------------------------------------------------
    t_api = threading.Thread(target=start_uvicorn)
    t_ui = threading.Thread(target=start_streamlit)

    t_api.start()
    t_ui.start()

    t_api.join()
    t_ui.join()


if __name__ == "__main__":
    main()
