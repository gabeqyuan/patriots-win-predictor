import React, { useState } from "react";

interface Game {
    date: string;
    opponent: string;
    home: boolean;
    time: string | null;
}

interface Props {
    game: Game;
}

const GameCard: React.FC<Props> = ({ game }) => {
    const [result, setResult] = useState<string | null>(null);

    const handlePredict = async () => {
        try {
            const res = await fetch("http://127.0.0.1:5050/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
              body: JSON.stringify(game), // your {date, opponent, location, time}
            });
            const data = await res.json(); // { result, confidence }
            setResult(
              `Patriots will likely ${data.result} (Confidence: ${(data.confidence * 100).toFixed(1)}%)`
            );
            } catch (e) {
            setResult("Prediction service unavailable. Try again.");
            }
    };

    return (
        <div
            className="border rounded-lg p-4 shadow hover:shadow-lg transition cursor-pointer bg-white text-gray-900 hover:bg-blue-50"
            onClick={handlePredict}
        >
            <h2 className="text-lg font-bold text-gray-900">{game.opponent}</h2>
            <p>{game.date} - {game.time ?? "TBD"}</p>
            <p>{game.home ? "Home" : "Away"}</p>

        {result && (
            <p className="mt-2 text-green-700 font-semibold">{result}</p>
        )}
        </div>

    );
};

export default GameCard;
