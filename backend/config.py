"""FILE: backend/config.py  PURPOSE: Settings from environment variables (see .env.example). No secrets in code."""
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:      # python-dotenv is optional
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "data" / "assessments.db"))
    DATASET_PATH = os.environ.get("DATASET_PATH", str(BASE_DIR / "data" / "social_media_privacy_assessments.csv"))
    RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "120"))
    MAX_CONTENT_LENGTH = 16 * 1024          # requests are tiny; reject anything bigger
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
