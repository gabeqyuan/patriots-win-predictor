import React, { useState } from "react";

interface Game {
    date: string;
    opponent: string;
    location: "home" | "away";
    time: string;
}

interface Props {
    game: Game;
}

const GameCard: React.FC<Props> = ({ game }) => {
    const [result, setResult] = useState<string | null>(null);

    const handlePredict = async () => {
        try {
            const res = await fetch("http://127.0.0.1:5000/predict", {
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
        <p>{game.date} - {game.time}</p>
        <p className="capitalize">{game.location}</p>
        {result && <p className="mt-2 text-green-700 font-semibold">{result}</p>}
</div>

    );
};

export default GameCard;
