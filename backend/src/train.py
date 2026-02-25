import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from .config import PROC_DIR, MODELS_DIR

FEATURES = [
    "is_home",
    "spread", "moneyline", "opp_moneyline",
    "pts_for_r4","pts_against_r4","pt_diff_r4","won_r4",
    "opp_pts_for_r4","opp_pts_against_r4","opp_pt_diff_r4","opp_won_r4"
]

def load_train_data():
    df = pd.read_csv(PROC_DIR / "patriots_team_games.csv")
    # Only train on past years (exclude current season if present)
    latest_season = df["season"].max()
    train_df = df[df["season"] < latest_season].copy()
    X = train_df[FEATURES].fillna(0)
    y = train_df["won"].astype(int)
    return X, y

def train_and_save():
    X, y = load_train_data()
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── Define candidate models + hyperparameter grids ──
    candidates = {
        "LogisticRegression": {
            "pipe": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=500)),
            ]),
            "params": {
                "clf__C": [0.001, 0.01, 0.1, 1, 10, 100],
                "clf__penalty": ["l1", "l2"],
                "clf__solver": ["liblinear"],
                "clf__class_weight": [None, "balanced"],
            },
        },
        "RandomForest": {
            "pipe": Pipeline([
                ("clf", RandomForestClassifier(random_state=42)),
            ]),
            "params": {
                "clf__n_estimators": [100, 200, 300],
                "clf__max_depth": [3, 5, 8, None],
                "clf__min_samples_split": [2, 5, 10],
                "clf__class_weight": [None, "balanced"],
            },
        },
        "GradientBoosting": {
            "pipe": Pipeline([
                ("clf", GradientBoostingClassifier(random_state=42)),
            ]),
            "params": {
                "clf__n_estimators": [100, 200, 300],
                "clf__max_depth": [2, 3, 5],
                "clf__learning_rate": [0.01, 0.05, 0.1, 0.2],
                "clf__subsample": [0.8, 1.0],
            },
        },
    }

    best_model = None
    best_score = -1
    best_name = ""

    print("=" * 55)
    print("HYPERPARAMETER TUNING (5-fold CV on training set)")
    print("=" * 55)

    for name, cfg in candidates.items():
        print(f"\n▶ {name}")
        grid = GridSearchCV(
            cfg["pipe"],
            cfg["params"],
            cv=5,
            scoring="roc_auc",
            n_jobs=-1,
            refit=True,
        )
        grid.fit(X_train, y_train)
        val_acc = grid.score(X_val, y_val)
        val_proba = grid.predict_proba(X_val)[:, 1]
        val_auc = roc_auc_score(y_val, val_proba)

        print(f"  Best CV ROC AUC:  {grid.best_score_:.3f}")
        print(f"  Val Accuracy:     {val_acc:.3f}")
        print(f"  Val ROC AUC:      {val_auc:.3f}")
        print(f"  Best params:      {grid.best_params_}")

        if val_auc > best_score:
            best_score = val_auc
            best_model = grid.best_estimator_
            best_name = name

    print(f"\n{'=' * 55}")
    print(f"🏆 BEST MODEL: {best_name}  (Val ROC AUC = {best_score:.3f})")
    print(f"{'=' * 55}")

    joblib.dump(best_model, MODELS_DIR / "win_model.joblib")
    print(f"Saved model -> {MODELS_DIR / 'win_model.joblib'}")


def evaluate():
    """Print detailed accuracy metrics for the trained model."""
    X, y = load_train_data()
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = joblib.load(MODELS_DIR / "win_model.joblib")

    # --- Validation set metrics ---
    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1]

    print("=" * 50)
    print("VALIDATION SET RESULTS (20% held out)")
    print("=" * 50)
    print(f"\nAccuracy: {model.score(X_val, y_val):.3f}")
    print(f"ROC AUC:  {roc_auc_score(y_val, y_proba):.3f}")
    print(f"\nConfusion Matrix (rows=actual, cols=predicted):")
    cm = confusion_matrix(y_val, y_pred)
    print(f"             Predicted Loss  Predicted Win")
    print(f"  Actual Loss    {cm[0][0]:>5}          {cm[0][1]:>5}")
    print(f"  Actual Win     {cm[1][0]:>5}          {cm[1][1]:>5}")
    print(f"\nClassification Report:")
    print(classification_report(y_val, y_pred, target_names=["Loss", "Win"]))

    # --- 5-fold cross-validation ---
    pipe = Pipeline(steps=[
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=200))
    ])
    cv_scores = cross_val_score(pipe, X, y, cv=5, scoring="accuracy")
    print("=" * 50)
    print("5-FOLD CROSS-VALIDATION (full dataset)")
    print("=" * 50)
    print(f"  Fold accuracies: {[f'{s:.3f}' for s in cv_scores]}")
    print(f"  Mean accuracy:   {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print()

    # --- Dataset stats ---
    print("=" * 50)
    print("DATASET INFO")
    print("=" * 50)
    print(f"  Total games:    {len(X)}")
    print(f"  Wins:           {y.sum()} ({y.mean()*100:.1f}%)")
    print(f"  Losses:         {len(y) - y.sum()} ({(1-y.mean())*100:.1f}%)")
    print(f"  Features used:  {FEATURES}")


if __name__ == "__main__":
    train_and_save()
    print()
    evaluate()
