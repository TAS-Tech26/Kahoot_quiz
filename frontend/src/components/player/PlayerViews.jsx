// PlayerViews.jsx


import Timer from './Timer'


export const PlayerLobby = ({playersCount}) => (

    <div className = "flex-1 flex flex-col items-center justify-center w-full max-w-4xl mx-auto">
        <div className = "bg-card-dark border-4 border-ink shadow-brutal-lg p-12 text-center w-full">
            <h1 className = "text-text-inverted text-5xl md:text-7xl font-bold uppercase tracking-tighter mb-8">
                You're in!
            </h1>

            <div className = "inline-block bg-bg-base border-4 border-ink px-8 py-4 shadow-brutal-sm">
                <span className = "font-mono font-bold text-2xl text-ink uppercase">
                    Players: {playersCount}
                </span>
            </div>

            <p className = "mt-8 font-mono text-text-inverted/50 text-lg uppercase tracking-widest animate-pulse">
                Waiting for host to start...
            </p>
        </div>
    </div>

)

export const PlayerActiveQuestion = ({question, onAnswerSubmit, onLockUI}) => (

    <div className = "flex-1 flex flex-col items-center justify-center w-full max-w-4xl mx-auto space-y-8 mt-8">
        <Timer
            timeLimit = {question.time_limit}
            onTimeUp = {onLockUI}
        />
        
        <div className = "grid grid-cols-1 md:grid-cols-2 gap-6 w-full h-96">
            {question.choices.map((choice) => (
                <button
                    key = {choice.id}
                    onClick = {() => onAnswerSubmit(choice.id)}
                    className = "bg-btn-neutral text-ink font-bold text-3xl md:text-4xl border-4 border-ink shadow-brutal-md hover:-translate-y-1 hover:shadow-brutal-lg active:translate-y-1.5 active:shadow-none transition-all uppercase flex items-center justify-center"
                >
                    {choice.text}
                </button>
            ))}
        </div>
    </div>

)

export const PlayerLocked = () => (

    <div className = "flex-1 flex items-center justify-center w-full">
        <div className = "bg-btn-neutral border-4 border-ink shadow-brutal-lg p-12 text-center">
            <h2 className = "text-4xl font-bold uppercase text-ink mb-4">
                Answered!
            </h2>

            <div className = "inline-block px-6 py-2 bg-card-dark text-text-inverted border-4 border-ink font-mono font-bold animate-pulse">
                Waiting for others...
            </div>
        </div>
    </div>

)

export const PlayerResult = ({result}) => {

    if (!result) return null

    return (

        <div className = "flex-1 flex items-center justify-center w-full">
            <div
                className = {`
                    border-4 border-ink shadow-brutal-lg p-12 text-center w-full max-w-2xl
                    ${result.is_correct
                        ? 'bg-btn-correct'
                        : 'bg-btn-wrong'
                    }
                `}
            >
                <h1 className = "text-6xl font-bold uppercase text-ink tracking-tighter mb-4">
                    {result.is_correct
                        ? 'Correct!'
                        : 'Incorrect'
                    }
                </h1>

                <div className = "inline-block bg-bg-base border-4 border-ink px-6 py-3 shadow-brutal-sm">
                    <p className = "text-3xl font-mono font-bold text-ink">
                        +{result.points_earned} PTS
                    </p>
                </div>
            </div>
        </div>

    )

}

export const PlayerGameOver = ({leaderboard, currentPlayerId}) => {

    const playerRankIndex = leaderboard?.findIndex(p => p.player_id === currentPlayerId)
    const playerRank = playerRankIndex !== -1 ? playerRankIndex + 1 : 'N/A'

    return (

        <div className = "flex-1 flex flex-col items-center justify-center w-full max-w-2xl mx-auto space-y-8 mt-12">
            <div className = "bg-card-dark w-full border-4 border-ink shadow-brutal-lg p-12 text-center">
                <h1 className = "text-text-inverted text-5xl font-bold uppercase mb-8 tracking-tighter">
                    Game Over
                </h1>

                <div className = "bg-bg-base border-4 border-ink p-6 shadow-brutal-sm inline-block">
                    <p className = "text-xl font-mono font-bold text-ink uppercase mb-2">
                        Final Rank
                    </p>

                    <p className = "text-6xl font-bold text-ink">
                        #{playerRank}
                    </p>
                </div>

                <p className = "font-mono text-ink/70 font-bold uppercase tracking-widest text-center">
                    Look at the host screen for the podium.
                </p>
            </div>
        </div>

    )

}