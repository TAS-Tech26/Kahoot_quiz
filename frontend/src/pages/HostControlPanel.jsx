// HostControlPanel.jsx


import {useWebSocket} from '../context/WebSocketContext'

import {useGameState} from '../hooks/useGameState'

import {HostActiveQuestion, HostLobby, HostPodium, HostResult} from '../components/host/HostViews'


export default function HostControlPanel() {

    const {lastMessage, isConnected, sendMessage} = useWebSocket()

    const {gameState, playersCount, currentQuestion, answersSubmitted, leaderboard} = useGameState(lastMessage, 0)

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
                <HostLobby
                    playersCount = {playersCount}
                    onStart = {() => sendMessage('host_start', 'host', {})}
                />
            )}

            {gameState === 'active' && currentQuestion && (
                <HostActiveQuestion
                    question = {currentQuestion}
                    answersSubmitted = {answersSubmitted}
                    totalPlayers = {playersCount}
                    onShowLeaderboard = {() => sendMessage('host_show_leaderboard', 'host', {})}
                />
            )}

            {gameState === 'leaderboard' && (
                <HostResult
                    leaderboard = {leaderboard}
                    onNext = {() => sendMessage('host_next_question', 'host', {})}
                />
            )}

            {gameState === 'game_over' && (
                <HostPodium leaderboard = {leaderboard} />
            )}
       </div>

    )

}