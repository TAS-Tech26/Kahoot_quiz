// GameRoom.jsx


import {useWebSocket} from '../WebSocketContext'

import {useGameState} from '../hooks/useGameState'


const LobbyView = ({playersCount}) => (
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


export default function GameRoom() {

    const {lastMessage, isConnected, sendMessage} = useWebSocket()

    const {gameState, setGameState, playersCount} = useGameState(lastMessage, 1)

    const handleAnswerSubmit = (choiceId) => {
        if (gameState !== 'active') return

        setGameState('locked') // Locally freeze the UI while waiting for the server to respond
        sendMessage('submit_answer', 'player', {choice_id : choiceId})
    }

    if (!isConnected) {

        return (

            <div className = "min-h-screen flex items-center justify-center p-8 bg-bg-base">
                <div className = "bg-card-dark text-text-inverted border-4 border-ink p-8 shadow-brutal-lg font-mono text-2xl font-bold uppercase animate-pulse">
                    Connecting to game...
                </div>
            </div>

        )

    }

    return (

        <div className = "min-h-screen p-4 md:p-8 flex flex-col bg-bg-base text-ink">
            {gameState === 'lobby' && <LobbyView playersCount = {playersCount} />}
        </div>

    )

}