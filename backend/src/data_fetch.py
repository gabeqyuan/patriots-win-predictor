import os
import nfl_data_py as nfl
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

def fetch_patriots_schedule():
    print("Downloading 2025 schedule...")
    df = nfl.import_schedules([2025])

    # Save full schedule for feature engineering
    full_path = os.path.join(RAW_DIR, "schedules.csv")
    df.to_csv(full_path, index=False)
    print(f"✅ Saved full NFL schedule to {full_path}")

    # Patriots games only
    pats_schedule = df[(df["home_team"] == "NE") | (df["away_team"] == "NE")].copy()

    # --- Normalize columns ---
    pats_schedule["date"] = pd.to_datetime(pats_schedule["gameday"]).dt.date.astype(str)
    pats_schedule["opponent"] = pats_schedule.apply(
        lambda x: x["away_team"] if x["home_team"] == "NE" else x["home_team"], axis=1
    )
    pats_schedule["home"] = pats_schedule["home_team"] == "NE"

    # Handle time column (sometimes missing)
    if "game_time" in pats_schedule.columns:
        pats_schedule["time"] = pats_schedule["game_time"].fillna("").astype(str).str.strip().replace("", None)
    else:
        pats_schedule["time"] = None

    # Select the final columns
    output = pats_schedule[["date", "opponent", "home", "time"]]

    # Save Pats-only schedule separately
    pats_path = os.path.join(RAW_DIR, "games.csv")
    output.to_csv(pats_path, index=False)
    print(f"✅ Saved Patriots schedule to {pats_path}")


if __name__ == "__main__":
    fetch_patriots_schedule()
