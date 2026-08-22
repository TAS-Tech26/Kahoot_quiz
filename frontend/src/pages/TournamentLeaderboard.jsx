// TournamentLeaderboard.jsx


import {useEffect, useState} from 'react'
import {useNavigate, useParams} from 'react-router-dom'

import {getTournamentLeaderboard} from '../api/api'


export default function TournamentLeaderboard() {

    const {eventName} = useParams()
    
    const navigate = useNavigate()

    const [leaderboard, setLeaderboard] = useState([])
    const [totalTeams, setTotalTeams] = useState(0)
    const [isLoading, setIsLoading] = useState(true)
    const [errorMsg, setErrorMsg] = useState(null)

    useEffect(() => {
        const fetchLeaderboard = async () => {
            try {
                const response = await getTournamentLeaderboard(eventName)
                const data = await response.json()

                if (response.ok) {
                    setLeaderboard(data.scores)
                    setTotalTeams(data.total_teams)
                } else {
                    setErrorMsg(data.error || "Failed to load tournament data.")
                }
            } catch (err) {
                setErrorMsg("Failed to establish contact with the server.")
            } finally {
                setIsLoading(false)
            }
        }

        fetchLeaderboard()
    } , [eventName])

    return (

        <div className = "min-h-screen bg-bg-base p-4 md:p-8 text-ink flex flex-col items-center">
            <div className = "w-full max-w-5xl">
                <div className = "flex justify-between items-end mb-12 border-b-8 border-ink pb-4">
                    <div>
                        <h1 className = "text-5xl md:text-6xl font-bold uppercase tracking-tighter">
                            Global Standings
                        </h1>

                        <p className = "font-mono text-2xl uppercase mt-2 font-bold text-ink/70">
                            Event: {eventName}
                        </p>
                    </div>

                    <button
                        onClick = {() => navigate('/host/create-session')}
                        className = "bg-btn-neutral text-ink border-4 border-ink px-6 py-3 font-bold font-mono text-xl shadow-brutal-sm hover:-translate-y-1 hover:shadow-brutal-md active:translate-y-1 active:shadow-none transition-all uppercase"
                    >
                        Back to Command Center
                    </button>
                </div>

                {errorMsg && (
                    <div className = "bg-btn-wrong text-ink border-4 border-ink p-4 mb-8 font-bold font-mono text-xl shadow-brutal-sm uppercase">
                        {errorMsg}
                    </div>
                )}

                {isLoading ? (
                    <div className = "text-center font-mono text-2xl font-bold uppercase animate-pulse">
                        Calculating Global Scores...
                    </div>
                ) : leaderboard.length > 0 ? (
                    <div className = "bg-card-dark text-text-inverted border-4 border-ink p-8 shadow-brutal-lg">
                        <div className = "flex justify-between items-center border-b-4 border-ink pb-4 mb-6">
                            <h2 className = "text-3xl font-bold uppercase tracking-tight">
                                Top Teams
                            </h2>

                            <span className = "font-mono text-xl uppercase bg-bg-base text-ink px-4 py-2 border-4 border-ink font-bold">
                                Total Teams: {totalTeams}
                            </span>
                        </div>

                        <div className = "space-y-4 font-mono">
                            {leaderboard.map((team, index) => (
                                <div
                                    key = {team.team_code}
                                    className = {`
                                        flex justify-between items-center p-6 border-4 border-ink shadow-brutal-sm transition-all
                                        ${index < 3
                                            ? "bg-text-inverted text-card-dark font-black scale-[1.02]"
                                            : "bg-btn-neutral text-ink"
                                        }    
                                    `}
                                >
                                    <div className = "flex gap-6 items-center w-1/3">
                                        <span className = 'text-3xl'>
                                            #{index + 1}
                                        </span>

                                        <span className = "text-2xl truncate">
                                            Team {team.team_code}
                                        </span>
                                    </div>

                                    <div className = "flex gap-8 items-center w-2/3 justify-end text-lg uppercase tracking-tight">
                                        <div className = "flex flex-col items-end">
                                            <span className = "text-sm opacity-70">
                                                Accuracy
                                            </span>

                                            <span>{team.global_correct} / Qs</span>
                                        </div>

                                        <div className = "flex flex-col items-end">
                                            <span className = "text-sm opacity-70">
                                                Speed
                                            </span>

                                            <span>{team.global_time ? team.global_time.toFixed(2) : '0.00'}</span>
                                        </div>

                                        <div className = "flex flex-col items-end bg-bg-base border-4 border-ink px-4 py-2 ml-4">
                                            <span className = "text-sm opacity-70">
                                                Score
                                            </span>

                                            <span className = "text-2xl font-black">
                                                {team.global_score} PTS
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    !errorMsg && (
                        <div className = "bg-card-dark text-text-inverted border-4 border-ink p-12 text-center shadow-brutal-lg">
                            <p className = "font-mono text-2xl uppercase font-bold">
                                No data available.
                            </p>

                            <p className = "font-mono pt-4 text-text-inverted/70">
                                Rooms for this event might still be active or no games have been played.
                            </p>
                        </div>
                    )
                )}
            </div>
        </div>

    )

}