from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from .config import MODELS_DIR, PROC_DIR, RAW_DIR

app = Flask(__name__)
CORS(app)

# Feature columns (must match train.py)
FEATURES = [
    "is_home",
    "spread", "moneyline", "opp_moneyline",
    "pts_for_r4", "pts_against_r4", "pt_diff_r4", "won_r4",
    "opp_pts_for_r4", "opp_pts_against_r4", "opp_pt_diff_r4", "opp_won_r4",
]

# NFL team abbreviation lookup (display name -> nflverse code)
TEAM_ABBREV = {
    "Cardinals": "ARI", "Falcons": "ATL", "Ravens": "BAL", "Bills": "BUF",
    "Panthers": "CAR", "Bears": "CHI", "Bengals": "CIN", "Browns": "CLE",
    "Cowboys": "DAL", "Broncos": "DEN", "Lions": "DET", "Packers": "GB",
    "Texans": "HOU", "Colts": "IND", "Jaguars": "JAX", "Chiefs": "KC",
    "Raiders": "LV", "Chargers": "LAC", "Rams": "LA", "Dolphins": "MIA",
    "Vikings": "MIN", "Patriots": "NE", "Saints": "NO", "Giants": "NYG",
    "Jets": "NYJ", "Eagles": "PHI", "Steelers": "PIT", "49ers": "SF",
    "Seahawks": "SEA", "Buccaneers": "TB", "Titans": "TEN", "Commanders": "WAS",
}

def _load_model():
    path = MODELS_DIR / "win_model.joblib"
    if not path.exists():
        return None
    return joblib.load(path)

def _get_team_rolling(team_code: str, season: int = 2024) -> dict:
    """
    Get the most recent rolling-4 stats for a team from the processed data.
    Uses the last available row for that team (end of prior season as proxy).
    """
    proc_path = PROC_DIR / "patriots_team_games.csv"
    if not proc_path.exists():
        return {}
    df = pd.read_csv(proc_path)
    # For NE stats, use NE rows; for opponent, read from the full feature table
    # We stored all-teams rolling stats inside features.py; reuse the raw build
    sched = pd.read_csv(RAW_DIR / "schedules.csv")
    from .features import _team_perspective_rows, _add_rolls
    all_teams = _add_rolls(_team_perspective_rows(sched), window=4)
    rows = all_teams[(all_teams["team"] == team_code) & (all_teams["season"] <= season)]
    if rows.empty:
        return {}
    last = rows.iloc[-1]
    return {
        "pts_for_r4": last.get("pts_for_r4", 0),
        "pts_against_r4": last.get("pts_against_r4", 0),
        "pt_diff_r4": last.get("pt_diff_r4", 0),
        "won_r4": last.get("won_r4", 0),
    }


def _get_betting_lines(opp_code: str, is_home: bool) -> dict:
    """
    Look up spread & moneyline for a Patriots game from the 2025 schedule.
    Returns values from the Patriots' perspective.
    """
    sched = pd.read_csv(RAW_DIR / "schedules.csv")
    if is_home:
        game = sched[(sched["season"] == 2025) & (sched["home_team"] == "NE") & (sched["away_team"] == opp_code)]
    else:
        game = sched[(sched["season"] == 2025) & (sched["away_team"] == "NE") & (sched["home_team"] == opp_code)]

    if game.empty:
        return {"spread": 0, "moneyline": 0, "opp_moneyline": 0}

    row = game.iloc[0]
    if is_home:
        return {
            "spread": row.get("spread_line", 0),
            "moneyline": row.get("home_moneyline", 0),
            "opp_moneyline": row.get("away_moneyline", 0),
        }
    else:
        return {
            "spread": -row.get("spread_line", 0),   # flip for away perspective
            "moneyline": row.get("away_moneyline", 0),
            "opp_moneyline": row.get("home_moneyline", 0),
        }


@app.route("/predict", methods=["POST"])
def predict():
    model = _load_model()
    if model is None:
        return jsonify({"error": "Model not trained yet. Run the training pipeline first."}), 503

    data = request.get_json(force=True) or {}
    is_home = 1 if data.get("home", True) else 0
    opponent_name = data.get("opponent", "")
    opp_code = TEAM_ABBREV.get(opponent_name, opponent_name)

    # Get rolling stats for NE and opponent (from end of 2024 season)
    ne_stats = _get_team_rolling("NE", season=2024)
    opp_stats = _get_team_rolling(opp_code, season=2024)
    betting = _get_betting_lines(opp_code, is_home == 1)

    row = {
        "is_home": is_home,
        "spread": betting.get("spread", 0),
        "moneyline": betting.get("moneyline", 0),
        "opp_moneyline": betting.get("opp_moneyline", 0),
        "pts_for_r4": ne_stats.get("pts_for_r4", 0),
        "pts_against_r4": ne_stats.get("pts_against_r4", 0),
        "pt_diff_r4": ne_stats.get("pt_diff_r4", 0),
        "won_r4": ne_stats.get("won_r4", 0),
        "opp_pts_for_r4": opp_stats.get("pts_for_r4", 0),
        "opp_pts_against_r4": opp_stats.get("pts_against_r4", 0),
        "opp_pt_diff_r4": opp_stats.get("pt_diff_r4", 0),
        "opp_won_r4": opp_stats.get("won_r4", 0),
    }

    X = pd.DataFrame([row])[FEATURES].fillna(0)
    prob = model.predict_proba(X)[0]  # [P(loss), P(win)]
    win_prob = float(prob[1])
    prediction = "win" if win_prob >= 0.5 else "lose"

    return jsonify({
        "result": prediction,
        "confidence": win_prob,
        "features": row,
    })


@app.route("/predict_all", methods=["GET"])
def predict_all():
    """Predict all 2025 Patriots games at once."""
    model = _load_model()
    if model is None:
        return jsonify({"error": "Model not trained yet."}), 503

    games_path = RAW_DIR / "games.csv"
    if not games_path.exists():
        return jsonify({"error": "No games schedule found."}), 404

    games = pd.read_csv(games_path)
    results = []
    for _, g in games.iterrows():
        is_home = 1 if g["home"] else 0
        opp_code = TEAM_ABBREV.get(g["opponent"], g["opponent"])

        ne_stats = _get_team_rolling("NE", season=2024)
        opp_stats = _get_team_rolling(opp_code, season=2024)
        betting = _get_betting_lines(opp_code, is_home == 1)

        row = {
            "is_home": is_home,
            "spread": betting.get("spread", 0),
            "moneyline": betting.get("moneyline", 0),
            "opp_moneyline": betting.get("opp_moneyline", 0),
            "pts_for_r4": ne_stats.get("pts_for_r4", 0),
            "pts_against_r4": ne_stats.get("pts_against_r4", 0),
            "pt_diff_r4": ne_stats.get("pt_diff_r4", 0),
            "won_r4": ne_stats.get("won_r4", 0),
            "opp_pts_for_r4": opp_stats.get("pts_for_r4", 0),
            "opp_pts_against_r4": opp_stats.get("pts_against_r4", 0),
            "opp_pt_diff_r4": opp_stats.get("pt_diff_r4", 0),
            "opp_won_r4": opp_stats.get("won_r4", 0),
        }
        X = pd.DataFrame([row])[FEATURES].fillna(0)
        prob = model.predict_proba(X)[0]
        win_prob = float(prob[1])

        results.append({
            "date": g["date"],
            "opponent": g["opponent"],
            "home": bool(g["home"]),
            "time": g.get("time"),
            "prediction": "win" if win_prob >= 0.5 else "lose",
            "confidence": win_prob,
        })

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
