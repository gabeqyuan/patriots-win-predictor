import os
import nfl_data_py as nfl
import pandas as pd
import sys

# Add parent to path so we can import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from src.config import RAW_DIR, TRAIN_SEASONS, PREDICT_SEASON

def fetch_schedules():
    """
    Download historical seasons (for training) + the upcoming season (for prediction).
    """
    all_seasons = TRAIN_SEASONS + [PREDICT_SEASON]
    print(f"Downloading schedules for seasons {all_seasons[0]}–{all_seasons[-1]}...")
    df = nfl.import_schedules(all_seasons)

    full_path = os.path.join(str(RAW_DIR), "schedules.csv")
    df.to_csv(full_path, index=False)
    print(f"✅ Saved full NFL schedule ({len(df)} rows) to {full_path}")
    return df


def fetch_patriots_2025_games(df: pd.DataFrame | None = None):
    """
    Extract Patriots 2025 schedule for the frontend games.json / games.csv.
    """
    if df is None:
        df = pd.read_csv(os.path.join(str(RAW_DIR), "schedules.csv"))

    pats = df[
        (df["season"] == PREDICT_SEASON)
        & ((df["home_team"] == "NE") | (df["away_team"] == "NE"))
    ].copy()

    pats["date"] = pd.to_datetime(pats["gameday"]).dt.date.astype(str)
    pats["opponent"] = pats.apply(
        lambda x: x["away_team"] if x["home_team"] == "NE" else x["home_team"], axis=1
    )
    pats["home"] = pats["home_team"] == "NE"

    if "gametime" in pats.columns:
        pats["time"] = pats["gametime"].fillna("").astype(str).str.strip().replace("", None)
    else:
        pats["time"] = None

    output = pats[["date", "opponent", "home", "time"]]

    pats_path = os.path.join(str(RAW_DIR), "games.csv")
    output.to_csv(pats_path, index=False)
    print(f"✅ Saved Patriots {PREDICT_SEASON} schedule to {pats_path}")
    return output


if __name__ == "__main__":
    sched = fetch_schedules()
    fetch_patriots_2025_games(sched)
