'use client';
import React, { useEffect, useState } from "react";
import GameCard from "./gamecard";

interface Game {
    date: string;
    opponent: string;
    home: boolean;
    time: string | null;
}

const Calendar = () => {
    const [games, setGames] = useState<Game[]>([]);

    useEffect(() => {
    fetch("/games.json")
        .then((res) => res.json())
        .then((data: Game[]) => setGames(data));
    }, []);

    return (
        <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* All games except the last 2 */}
            {games.slice(0, -2).map((game, index) => (
            <GameCard key={index} game={game} />
    ))}

    {/* Last row with 2 cards centered */}
    <div className="col-span-full flex justify-center gap-4">
        {games.slice(-2).map((game, index) => (
            <div className="w-1/2 md:w-1/3 lg:w-1/4">
                <GameCard key={index} game={game} />
            </div>
        ))}
    </div>
    </div>
</div>

    );
};

export default Calendar;
