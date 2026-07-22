// HostDashboard.jsx


import {useState} from 'react'
import {useNavigate} from 'react-router-dom'

import {createGameSession} from '../api'


export default function SessionCreator() {

    const [quizId, setQuizId] = useState('')
    const [errorMsg, setErrorMsg] = useState('')
    const [isDeploying, setIsDeploying] = useState(false)

    const navigate = useNavigate()

    const handleCreateGame = async (e) => {
        e.preventDefault()

        setErrorMsg(null)

        if (!quizId.trim()) return setErrorMsg("ERROR: Target Quiz ID is required to initialise deployment.")

        setIsDeploying(true)

        try {
            const response = await createGameSession(quizId)
            const data = await response.json()

            if (response.ok) {
                navigate(`/host/game/${data.pin}`)
            } else {
                setErrorMsg(`DEPLOYMENT REJECTED: ${data.error || "Unknown anomaly detected."}`)
            }
        } catch (err) {
            setErrorMsg("CRITICAL ERROR: Failed to establish contact with the server.")
        } finally {
            setIsDeploying(false)
        }
    }

    return (

        <div className = "min-h-screen bg-bg-base p-4 md:p-8 text-ink flex flex-col items-center">
            <div className = "w-full max-w-2xl">
                <h1 className = "text-5xl md:text-6xl font-bold uppercase mb-12 border-b-8 border-ink pb-4 tracking-tighter">
                    Command Center
                </h1>

                {errorMsg && (
                    <div className = "bg-btn-wrong text-ink border-4 border-ink p-4 mb-8 font-bold font-mono text-lg shadow-brutal-sm">
                        {errorMsg}
                    </div>
                )}

                <form
                    onSubmit = {handleCreateGame}
                    className = "bg-card-dark border-4 border-ink p-8 shadow-brutal-lg"
                >
                    <h2 className = "text-text-inverted text-3xl font-bold mb-6 uppercase tracking-tight">
                        Deploy Session
                    </h2>

                    <div className = 'mb-8'>
                        <label className = "block text-text-inverted font-mono text-xl mb-4">
                            Target Quiz ID
                        </label>

                        <input
                            type = 'number'
                            placeholder = 'e.g. 1'
                            value = {quizId}
                            onChange = {(e) => {
                                setQuizId(e.target.value)
                                setErrorMsg(null)
                            }}
                            className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-2xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50"
                        />
                    </div>

                    <button
                        type = 'submit'
                        disabled = {isDeploying}
                        className = "w-full bg-ink text-text-inverted font-bold text-2xl md:text-3xl py-6 border-4 border-ink shadow-brutal-md hover:-translate-y-1 hover:shadow-brutal-lg active:-translate-y-1.5 active:translate-x-1.5 active:shadow-none disabled:opacity-50 disabled:pointer-events-none transition-all uppercase tracking-widest"
                    >
                        {isDeploying
                            ? 'Initialising...'
                            : "Initialise Game"
                        }
                    </button>
                </form>
            </div>
        </div>

    )

}