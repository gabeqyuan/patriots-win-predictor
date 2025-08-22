from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True) or {}
    
    is_home = data.get("home", True)  # default True if missing
    opponent = data.get("opponent", "Unknown")
    date = data.get("date", "")
    time = data.get("time", "")

    # Dummy prediction logic
    import random
    prediction = "win" if random.random() > 0.5 else "lose"
    confidence = random.random()

    return jsonify({"result": prediction, "confidence": confidence})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
