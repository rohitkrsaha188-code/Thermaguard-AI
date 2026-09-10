import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# --- External API config (all optional - app must work without these) ---
NASA_FIRMS_API_KEY = os.getenv("NASA_FIRMS_API_KEY", "")
NASA_FIRMS_URL = os.getenv(
    "NASA_FIRMS_URL",
    "https://firms.modaps.eosdis.nasa.gov/api/area/csv",
)
OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'thermaguard.db'}"

# --- Demo data fallback paths ---
DATA_DIR = BASE_DIR / "data"
FIRES_CSV = DATA_DIR / "fires.csv"
INDUSTRIAL_CSV = DATA_DIR / "industrial_sites.csv"

# --- ML model ---
MODEL_PATH = BASE_DIR / "models" / "fire_classifier.pkl"

# --- Persistence detection thresholds ---
# Events within this radius of each other are considered "the same location"
PERSISTENCE_RADIUS_KM = float(os.getenv("PERSISTENCE_RADIUS_KM", "1.5"))


# Minimum number of detections at ~the same spot to be flagged persistent
PERSISTENCE_MIN_COUNT = int(os.getenv("PERSISTENCE_MIN_COUNT", "3"))

# --- Risk scoring thresholds (0-100 scale) ---
RISK_LEVEL_THRESHOLDS = {
    "Critical": 80,
    "High": 60,
    "Medium": 35,
    "Low": 0,
}

# --- Industrial proximity ---
INDUSTRIAL_PROXIMITY_KM = float(os.getenv("INDUSTRIAL_PROXIMITY_KM", "5.0"))

# --- Misc ---
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
