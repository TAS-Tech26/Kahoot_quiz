// HostControlPanel.jsx


import {useWebSocket} from '../WebSocketContext'

import {useGameState} from '../hooks/useGameState'


export default function HostControlPanel() {

    const {lastMessaage, isConnected, sendMessage} = useWebSocket()

    const {gameState, playersCount, currentQuestion, answersSubmitted, leaderboard} = useGameState(lastMessaage, 0)

    const handleStartGame = () => sendMessage('start_game', 'host', {})
    const handleRevealAnswer = () => sendMessage('reveal_answer', 'host', {})
    const handleNextQuestion = () => sendMessage('next_question', 'host', {})

    if (!isConnected) {

        return (

            <div className = "min-h-screen flex items-center justify-center p-8 bg-bg-base">
                <div className = "bg-card-dark text-text-inverted border-4 border-ink p-8 shadow-brutal-lg font-mono text-2xl font-bold uppercase animate-pulse">
                    Connecting to Lobby...
                </div>
            </div>

        )

    }

    return (

        <div className = "min-h-screen p-4 md:p-8 flex flex-col bg-bg-base text-ink font-mono">
            {gameState === 'lobby' && (
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
                            onClick = {handleStartGame}
                            disabled = {playersCount === 0}
                            className = "block w-full bg-green-500 disabled:bg-gray-500 disabled:cursor-not-allowed text-text-inverted font-bold text-3xl py-6 border-4 border-ink shadow-brutal-md hover:translate-y-1 hover:shadow-brutal-sm transition-all uppercase"
                        >
                            Start Quiz
                        </button>
                    </div>
                </div>
            )}

            {gameState === 'active' && currentQuestion && (
                <div className = "flex-1 flex flex-col w-full max-w-5xl mx-auto space-y-8">
                    <div className = "bg-white border-4 border-ink shadow-brutal-lg p-8 text-center">
                        <h2 className = "text-4xl font-bold">
                            {currentQuestion.text}
                        </h2>
                    </div>

                    <div className = "flex justify-between items-center bg-card-dark text-text-inverted border-4 border-ink p-6 shadow-brutal-md">
                        <span className = "text-2xl uppercase font-bold">
                            Answers In:
                        </span>

                        <span className = "text-4xl font-bold">
                            {answersSubmitted} / {playersCount}
                        </span>
                    </div>

                    <button
                        onClick = {handleRevealAnswer}
                        className = "w-full bg-yellow-400 text-ink font-bold text-2xl py-4 border-4 border-ink shadow-brutal-md hover:translate-y-1 hover:shadow-brutal-sm transition-all uppercase"
                    >
                        Skip & Show Answer
                    </button>
                </div>
            )}

            {gameState === 'result' && (
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
                        onClick = {handleNextQuestion}
                        className = "block w-full bg-blue-500 text-text-inverted font-bold text-3xl py-6 border-4 border-ink shadow-brutal-md hover:translate-y-1 hover:shadow-brutal-sm transition-all uppercase"
                    >
                        Next Question
                    </button>
                </div>
            )}

            {gameState === 'game_over' && (
                <div className = "flex-1 flex flex-col w-full max-w-4xl mx-auto space-y-8 mt-12">
                    <h1 className = "text-6xl font-bold uppercase tracking-tighter">
                        Podium
                    </h1>

                    <div className = "w-full bg-white border-4 border-ink p-6 shadow-brutal-lg">
                        {leaderboard.map((player, index) => (
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
                        ))}
                    </div>
                </div>
            )}
        </div>

    )

}