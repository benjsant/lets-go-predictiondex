# interface/config/settings.py

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (works for local dev, ignored in Docker if env already set)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
API_KEY = os.getenv("STREAMLIT_API_KEY", "")
