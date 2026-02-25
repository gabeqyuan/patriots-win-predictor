import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT / "models"

TEAM = "NE"          # Patriots code used by nflverse data
TRAIN_SEASONS = list(range(2002, 2025))  # historical seasons with completed scores
PREDICT_SEASON = 2025                     # the upcoming season to predict

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
