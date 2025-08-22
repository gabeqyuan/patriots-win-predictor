'use client';

import { useState } from "react";

/**
 * Home component for the Patriots Win Predictor application.
 * 
 * This component manages user inputs for opponent, quarterback rating, and rushing yards.
 * It calculates a mock prediction of whether the Patriots will win or lose based on random probability.
 * 
 * State:
 * - inputs: An object containing the opponent's name, quarterback rating, and rushing yards.
 * - result: A string or null that holds the prediction result.
 * 
 * Methods:
 * - handleChange: Updates the inputs state based on user input.
 * - handlePredict: Generates a mock prediction and updates the result state.
 */
export default function Home(){

  
  const [inputs, setInputs] = useState({
    opponent: '',
    qbRating: '',
    rushingYards: '',
  });

  const [result, setResult] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setInputs({ ... inputs, [e.target.name]: e.target.value });
  }

  const handlePredict = () => {
    const mockProbability = Math.random();
    const prediction = mockProbability > 0.5 ? 'WIN' : 'LOSE';
    setResult(
      `Patriots will likely ${prediction} (Confidence: ${(mockProbability * 100).toFixed(1)}%)`
      );
  };


  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 bg-gray-50 text-gray-900">
      <h1 className="text-3xl font-bold mb-6">Patriots Win Predictor 🏈</h1>

      <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-md space-y-4">
        <label className="block">
          <span className="font-medium">Opponent</span>
          <select
            name="opponent"
            value={inputs.opponent}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded px-3 py-2"
          >
            <option value="">Select Team</option>
            <option value="Jets">Jets</option>
            <option value="Bills">Bills</option>
            <option value="Dolphins">Dolphins</option>
            <option value="Chiefs">Chiefs</option>
          </select>
        </label>

        <button
          onClick={handlePredict}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Predict
        </button>

        {result && (
          <p className="text-center mt-4 text-lg font-semibold text-green-700">{result}</p>
        )}
      </div>
    </main>
  );

}