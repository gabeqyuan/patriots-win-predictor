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

    const handlePredict = () => {
    const mockProbability = Math.random();
    const prediction = mockProbability > 0.5 ? "WIN" : "LOSE";
    setResult(
      `Patriots will likely ${prediction} (Confidence: ${(mockProbability * 100).toFixed(1)}%)`
    );
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
