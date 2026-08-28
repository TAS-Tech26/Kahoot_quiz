// HostControlPanel.jsx


import {useRef, useEffect} from 'react'
import {useWebSocket} from '../context/WebSocketContext'

import {useGameState} from '../hooks/useGameState'

import {HostActiveQuestion, HostLobby, HostPodium, HostResult, HostStaging} from '../components/host/HostViews'


export default function HostControlPanel() {

    const {lastMessage, isConnected, isReconnecting, sendMessage} = useWebSocket()

    const {gameState, playersCount, currentQuestion, answersSubmitted, leaderboard} = useGameState(lastMessage, 0)
    
    const isSubmittingRef = useRef(false)
    
    useEffect(() => {
        isSubmittingRef.current = false
    }, [gameState])

    const handleAction = (actionName) => {
        if (isSubmittingRef.current) return
        isSubmittingRef.current = true
        sendMessage(actionName, 'host', {})
    }

    if (!isConnected) {

        return (

            <div className = "min-h-screen flex items-center justify-center p-8 bg-bg-base">
                <div className = "bg-card-dark text-text-inverted border-4 border-ink p-8 shadow-brutal-lg font-mono text-2xl font-bold uppercase animate-pulse">
                    {isReconnecting ? "Reconnecting to Lobby..." : "Connecting to Lobby..."}
                </div>
            </div>

        )

    }

    return (

        <div className = "min-h-screen p-4 md:p-8 flex flex-col bg-bg-base text-ink font-mono">
            {gameState === 'lobby' && (
                <HostLobby
                    playersCount = {playersCount}
                    onStart = {() => handleAction('host_start')}
                />
            )}

            {gameState === 'staging' && currentQuestion && (
                <HostStaging
                    question = {currentQuestion}
                    onStartTimer = {() => handleAction('host_start_timer')}
                />
            )}

            {gameState === 'active' && currentQuestion && (
                <HostActiveQuestion
                    question = {currentQuestion}
                    answersSubmitted = {answersSubmitted}
                    totalPlayers = {playersCount}
                    onShowLeaderboard = {() => handleAction('host_show_leaderboard')}
                />
            )}

            {gameState === 'leaderboard' && (
                <HostResult
                    leaderboard = {leaderboard}
                    onNext = {() => handleAction('host_next_question')}
                />
            )}

            {gameState === 'game_over' && (
                <HostPodium leaderboard = {leaderboard} />
            )}
       </div>

    )

}