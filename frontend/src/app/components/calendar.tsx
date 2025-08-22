'use client';
import React, { useEffect, useState } from "react";
import GameCard from "./gamecard";

interface Game {
    date: string;
    opponent: string;
    location: "home" | "away";
    time: string;
}

const Calendar = () => {
    const [games, setGames] = useState<Game[]>([]);

    useEffect(() => {
    fetch("/games.json")
        .then((res) => res.json())
        .then((data: Game[]) => setGames(data));
    }, []);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
            {games.map((game, index) => (
            <GameCard key={index} game={game} />
    ))}
</div>

    );
};

export default Calendar;
