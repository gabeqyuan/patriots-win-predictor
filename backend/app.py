from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
# Allow calls from your Next.js dev server
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

@app.get("/")
def health():
    return {"ok": True, "service": "Patriots Win Predictor API"}

@app.post("/predict")
def predict():
    """
    Expects JSON like:
    {
        "date": "2025-09-07",
        "opponent": "Jets",
        "location": "home",   # or "away"
        "time": "1:00 PM"
    }
    """
    data = request.get_json(force=True) or {}
    location = data.get("location", "home")

    # simple heuristic so it isn't pure random
    base = 0.55 if location == "home" else 0.45
    jitter = random.uniform(-0.08, 0.08)
    p = max(0.05, min(0.95, base + jitter))

    result = "WIN" if p >= 0.5 else "LOSE"
    confidence = p if result == "WIN" else 1 - p

    return jsonify({"result": result, "confidence": round(confidence, 2)})
    
if __name__ == "__main__":
    app.run(debug=True)  # runs on http://127.0.0.1:5000
