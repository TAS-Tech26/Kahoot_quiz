// GameRoom.jsx


import {useEffect, useRef} from 'react'
import {useNavigate, useParams} from 'react-router-dom'

import {useWebSocket} from '../context/WebSocketContext'

import {useGameState} from '../hooks/useGameState'

import {PlayerActiveQuestion, PlayerLeaderboard, PlayerLobby, PlayerLocked, PlayerGameOver, PlayerResult, PlayerStaging} from '../components/player/PlayerViews'


export default function GameRoom() {

    const {pin} = useParams()
    const {lastMessage, isConnected, isReconnecting, sendMessage} = useWebSocket()
    const {gameState, setGameState, playersCount, currentQuestion, answerResult, leaderboard, playerRanks} = useGameState(lastMessage, 1)
    
    const isSubmittingRef = useRef(false)

    const navigate = useNavigate()

    const currentTeamPin = localStorage.getItem(`team_pin_${pin}`)

    const myRank = playerRanks[currentTeamPin] || null

    useEffect(() => {
        if (gameState === 'error' && answerResult?.type === 'stale_session') {
            localStorage.removeItem(`team_pin_${pin}`)

            navigate('/', {replace : true})
        }
        
        if (gameState !== 'locked') {
            isSubmittingRef.current = false
        }
    }, [gameState, answerResult, navigate, pin])

    const handleAnswerSubmit = (choiceId) => {
        if (gameState !== 'active' || isSubmittingRef.current) return

        isSubmittingRef.current = true
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
                    {isReconnecting ? "Reconnecting to game..." : "Connecting to game..."}
                </div>
            </div>

        )

    }

    return (

        <div className = "min-h-screen p-4 md:p-8 flex flex-col bg-bg-base text-ink">
            {gameState === 'lobby' && <PlayerLobby playersCount = {playersCount} />}

            {gameState === 'staging' && currentQuestion && (
                <PlayerStaging question = {currentQuestion} />
            )}

            {gameState === 'active' && currentQuestion && (
                <PlayerActiveQuestion
                    question = {currentQuestion}
                    onAnswerSubmit = {handleAnswerSubmit}
                    onLockUI = {handleLockUI}
                />
            )}

            {gameState === 'locked' && <PlayerLocked />}

            {gameState === 'result' && answerResult && <PlayerResult result = {answerResult} />}

            {gameState === 'leaderboard' && (
                <PlayerLeaderboard
                    leaderboard = {leaderboard}
                    myRank = {myRank}
                />
            )}

            {gameState === 'game_over' && (
                <PlayerGameOver
                    myRank = {myRank}
                />
            )}

            {gameState === 'error' && (
                <div className = "flex-1 flex flex-col items-center justify-center w-full max-w-2xl mx-auto">
                    <div className = "bg-btn-wrong text-ink border-4 border-ink shadow-brutal-lg p-12 text-center w-full">
                        <h2 className = "text-4xl font-bold uppercase mb-4 tracking-tighter">
                            Access Denied
                        </h2>

                        <div className = "bg-bg-base border-4 border-ink p-6 shadow-brutal-sm inline-block">
                            <p className = "font-mono text-xl font-bold uppercase">
                                {answerResult?.message || "Invalid team credentials."}
                            </p>
                        </div>

                        <button
                            onClick = {() => navigate('/', {replace : true})}
                            className = "mt-8 w-full bg-ink text-text-inverted px-6 py-4 font-bold text-2xl uppercase border-4 border-ink shadow-brutal-md hover:-translate-y-1 transition-all"
                        >
                            Return to Login
                        </button>
                    </div>
                </div>
            )}
        </div>

    )

}