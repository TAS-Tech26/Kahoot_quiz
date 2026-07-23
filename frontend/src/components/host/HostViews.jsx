// HostViews.jsx


export const HostLobby = ({playersCount, onStart}) => (

    <div className = "flex-1 flex flex-col items-center justify-center w-full max-w-4xl mx-auto">
        <div className = "bg-card-dark border-4 border-ink shadow-brutal-lg p-12 text-center w-full">
            <h1 className = "text-text-inverted text-5xl md:text-7xl font-bold uppercase tracking-tighter mb-8">
                Game Lobby
            </h1>

            <div className = "inline-block bg-bg-base border-4 border-ink px-8 py-4 shadow-brutal-sm mb-8">
                <span className = "font-bold text-2xl uppercase">
                    Players In: {playersCount}
                </span>
            </div>

            <button
                onClick = {onStart}
                disabled = {playersCount === 0}
                className = "block w-full bg-green-500 disabled:bg-gray-500 disabled:cursor-not-allowed text-text-inverted font-bold text-3xl py-6 border-4 border-ink shadow-brutal-md uppercase"
            >
                Start Quiz
            </button>
        </div>
    </div>
    
)

export const HostActiveQuestion = ({question, answersSubmitted, totalPlayers, onReveal}) => (

    <div className = "flex-1 flex flex-col w-full max-w-5xl mx-auto space-y-8">
        <div className = "bg-btn-neutral border-4 border-ink shadow-brutal-lg p-8 text-center">
            <h2 className = "text-4xl font-bold text-ink">
                {question.text}
            </h2>
        </div>

        <div className = "flex justify-between items-center bg-card-dark text-text-inverted border-4 border-ink p-6 shadow-brutal-md">
            <span className = "text-2xl uppercase font-bold">
                Answers In:
            </span>

            <span className = "text-4xl font-bold">
                {answersSubmitted} / {totalPlayers}
            </span>
        </div>

        <button
            onClick = {onReveal}
            className = "w-full bg-btn-wrong text-text-inverted font-bold text-2xl py-4 border-4 border-ink shadow-brutal-md hover:translate-y-1 hover:shadow-brutal-sm active:translate-y-1.5 active:shadow-none transition-all uppercase"
        >
            Skip & Show Answer
        </button>
    </div>

)

export const HostResult = ({onNext}) => (

    <div className = "flex-1 flex flex-col items-center justify-center w-full max-w-4xl mx-auto space-y-8">
        <div className = "bg-card-dark border-4 border-ink shadow-brutal-lg p-12 text-center w-full">
            <h2 className = "text-text-inverted text-5xl font-bold uppercase mb-4">
                Time's Up!
            </h2>

            <p className = "text-text-inverted/70 text-xl uppercase tracking-widest mb-8">
                Answers revealed on player screens.
            </p>
        </div>

        <button
            onClick = {onNext}
            className = "block w-full bg-btn-correct text-text-inverted font-bold text-3xl py-6 border-4 border-ink shadow-brutal-md hover:translate-y-1 hover:shadow-brutal-sm active:translate-y-1.5 active:shadow-none transition-all uppercase"
        >
            Next Question
        </button>
    </div>

)

export const HostPodium = ({leaderboard}) => (

    <div className = "flex-1 flex flex-col w-full max-w-4xl mx-auto space-y-8 mt-12">
        <h1 className = "text-6xl font-bold uppercase tracking-tighter">
            Podium
        </h1>

        <div className = "w-full bg-btn-neutral border-4 border-ink p-6 shadow-brutal-lg">
            {leaderboard?.length > 0 ? (
                leaderboard.map((player, index) => (
                    <div
                        key = {index}
                        className = "flex justify-between items-center border-b-4 border-ink py-4 last:border-b-0"
                    >
                        <span className = "text-2xl font-bold">
                            #{index + 1} {player.name}
                        </span>

                        <span className = "text-2xl font-bold">
                            {player.score} PTS
                        </span>
                    </div>
                ))
            ) : (
                <div className = "text-center text-ink/70 font-bold uppercase py-4">
                    No data available.
                </div>
            )}
        </div>
    </div>

)