// useGameState.js


import {useEffect, useState} from 'react'


export function useGameState(lastMessage, initialPlayers = 0) {

    const [gameState, setGameState] = useState('lobby') // lobby, active, locked, result, game_over
    const [playersCount, setPlayersCount] = useState(initialPlayers)
    const [currentQuestion, setCurrentQuestion] = useState(null)
    const [answerResult, setAnswerResult] = useState(null)
    const [answersSubmitted, setAnswersSubmitted] = useState(0)
    const [leaderboard, setLeaderboard] = useState([])

    useEffect(() => {
        if (!lastMessage) return

        switch (lastMessage.event) {
            case 'player_joined':
            case 'player_left':
                setPlayersCount(lastMessage.data.total_players)
                
                break
            case 'question_revealed':
                setAnswerResult(null)
                setAnswersSubmitted(0)
                setCurrentQuestion(lastMessage.data)
                setGameState('active')

                break
            case 'answer_result':
                setAnswerResult(lastMessage.data)
                setGameState('result')

                break
            case 'answer_submitted':
                setAnswersSubmitted(lastMessage.data.total_answers)

                break
            case 'game_over':
                setLeaderboard(lastMessage.data.leaderboard)
                setGameState('game_over')

                break
            default:
                break
        }
    }, [lastMessage])

    return {gameState, setGameState, playersCount, currentQuestion, answerResult, answersSubmitted, leaderboard}

}