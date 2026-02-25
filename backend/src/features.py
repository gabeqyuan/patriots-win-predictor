from __future__ import annotations
import pandas as pd
from .config import RAW_DIR, PROC_DIR, TEAM, TRAIN_SEASONS

def _team_perspective_rows(sched: pd.DataFrame) -> pd.DataFrame:
    """
    Convert game rows into two team-rows: one for home, one for away.
    Columns out: season, week, game_id, date, team, opp, is_home, pts_for, pts_against, won
    """
    keep_cols = [
        "game_id","season","week","gameday","home_team","away_team","home_score","away_score",
        "spread_line","home_moneyline","away_moneyline"
    ]
    s = sched[keep_cols].dropna(subset=["home_team","away_team"]).copy()

    home = pd.DataFrame({
        "game_id":  s["game_id"],
        "season":   s["season"],
        "week":     s["week"],
        "date":     pd.to_datetime(s["gameday"]),
        "team":     s["home_team"],
        "opp":      s["away_team"],
        "is_home":  1,
        "pts_for":  s["home_score"],
        "pts_against": s["away_score"],
        "spread":   s["spread_line"],           # negative = home favored
        "moneyline": s["home_moneyline"],
        "opp_moneyline": s["away_moneyline"],
    })
    away = pd.DataFrame({
        "game_id":  s["game_id"],
        "season":   s["season"],
        "week":     s["week"],
        "date":     pd.to_datetime(s["gameday"]),
        "team":     s["away_team"],
        "opp":      s["home_team"],
        "is_home":  0,
        "pts_for":  s["away_score"],
        "pts_against": s["home_score"],
        "spread":   -s["spread_line"],          # flip sign for away team perspective
        "moneyline": s["away_moneyline"],
        "opp_moneyline": s["home_moneyline"],
    })
    df = pd.concat([home, away], ignore_index=True)
    df["won"] = (df["pts_for"] > df["pts_against"]).astype(int)
    df.sort_values(["team","season","week"], inplace=True)
    return df

def _add_rolls(df: pd.DataFrame, window: int = 4) -> pd.DataFrame:
    df["pt_diff"] = df["pts_for"] - df["pts_against"]
    # rolling stats by team, EXCLUDING current game (shift)
    for col in ["pts_for","pts_against","pt_diff","won"]:
        df[f"{col}_r{window}"] = (
            df
            .groupby("team")[col]
            .apply(lambda s: s.shift(1).rolling(window, min_periods=1).mean())
            .reset_index(level=0, drop=True)
        )
    return df

def build_team_game_table() -> pd.DataFrame:
    sched = pd.read_csv(RAW_DIR / "schedules.csv")
    df = _team_perspective_rows(sched)
    df = _add_rolls(df, window=4)

    # split team vs opponent features for the Patriots' rows
    pats = df[df["team"].eq(TEAM)].copy()
    opp_rolls = (
        df[["team","season","week","pts_for_r4","pts_against_r4","pt_diff_r4","won_r4"]]
        .rename(columns={
            "team":"opp",
            "pts_for_r4":"opp_pts_for_r4",
            "pts_against_r4":"opp_pts_against_r4",
            "pt_diff_r4":"opp_pt_diff_r4",
            "won_r4":"opp_won_r4"
        })
    )
    merged = pats.merge(opp_rolls, on=["opp","season","week"], how="left")
    # drop rows with no prior history (early season)
    merged = merged.dropna(subset=["pts_for_r4","opp_pts_for_r4"])
    merged.to_csv(PROC_DIR / "patriots_team_games.csv", index=False)
    return merged

if __name__ == "__main__":
    out = build_team_game_table()
    print(f"Built features: {out.shape}")
