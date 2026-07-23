// GameRoom.jsx


import {useWebSocket} from '../context/WebSocketContext'

import {useGameState} from '../hooks/useGameState'

import {PlayerActiveQuestion, PlayerLobby, PlayerLocked, PlayerGameOver, PlayerResult} from '../components/player/PlayerViews'


export default function GameRoom() {

    const {lastMessage, isConnected, sendMessage} = useWebSocket()

    const {gameState, setGameState, playersCount, currentQuestion, answerResult, leaderboard} = useGameState(lastMessage, 1)

    const currentPlayerId = localStorage.getItem('player_id')

    const handleAnswerSubmit = (choiceId) => {
        if (gameState !== 'active') return

        setGameState('locked') // Locally freeze the UI while waiting for the server to respond
        sendMessage('submit_answer', 'player', {choice_id : choiceId})
    }

    const handleLockUI = () => {
        if (gameState === 'active') setGameState('locked')
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

            {gameState === 'active' && currentQuestion && (
                <PlayerActiveQuestion
                    question = {currentQuestion}
                    onAnswerSubmit = {handleAnswerSubmit}
                    onLockUI = {handleLockUI}
                />
            )}

            {gameState === 'locked' && <PlayerLocked />}

            {gameState === 'result' && answerResult && <PlayerResult result = {answerResult} />}

            {gameState === 'game_over' && (
                <PlayerGameOver
                    leaderboard = {leaderboard}
                    currentPlayerId = {currentPlayerId}
                />
            )}
        </div>

    )

}