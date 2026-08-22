// SessionCreator.jsx


import {useEffect, useState} from 'react'
import {useNavigate} from 'react-router-dom'

import {createGameSession, getHostQuizzes, deleteHostQuiz} from '../api/api'


export default function SessionCreator() {

    const [quizzes, setQuizzes] = useState([])
    const [errorMsg, setErrorMsg] = useState('')
    const [isLoading, setIsLoading] = useState(true)
    const [deployingId, setDeployingId] = useState(null)
    const [isDeleting, setIsDeleting] = useState(null)
    const [eventName, setEventName] = useState('')

    const navigate = useNavigate()

    useEffect(() => {
        const fetchQuizzes = async () => {
            try {
                const response = await getHostQuizzes()

                if (response.ok) {
                    const data = await response.json()

                    setQuizzes(data)
                } else {
                    setErrorMsg("Failed to retrieve your quizzes.")
                }
            } catch (err) {
                setErrorMsg("Failed to contact the server.")
            } finally {
                setIsLoading(false)
            }
        }

        fetchQuizzes()
    }, [])

    const handleDeployGame = async (quizId) => {
        if (!eventName.trim()) {
            setErrorMsg("You must specify the event name before deploying.")

            return
        }

        setErrorMsg(null)
        setDeployingId(quizId)

        try {
            const response = await createGameSession(quizId, eventName.trim())
            const data = await response.json()

            if (response.ok) {
                navigate(`/host/game/${data.pin}`)
            } else {
                setErrorMsg(`DEPLOYMENT REJECTED: ${data.error || "Unknown anomaly detected."}`)
                setDeployingId(null)
            }
        } catch (err) {
            setErrorMsg("Failed to establish contact with the server.")
            setDeployingId(null)
        }
    }

    const handleDeleteQuiz = async(quizId) => {
        if (!window.confirm("Are you sure you want to permanently delete this quiz? This cannot be undone.")) return

        setErrorMsg(null)
        setIsDeleting(quizId)

        try {
            const response = await deleteHostQuiz(quizId)

            if (response.ok) {
                setQuizzes((prev) => prev.filter(q => q.id !== quizId))
            } else {
                const data = await response.json()
                
                setErrorMsg(`${data.error || "Unknown error."}`)
            }
        } catch (err) {
            setErrorMsg("Failed to establish contact with the server.")
        } finally {
            setIsDeleting(null)
        }
    }

    return (

        <div className = "min-h-screen bg-bg-base p-4 md:p-8 text-ink flex flex-col items-center">
            <div className = "w-full max-w-5xl">
                <div className = "flex justify-between items-end mb-12 border-b-8 border-ink pb-4">
                    <h1 className = "text-5xl md:text-6xl font-bold uppercase tracking-tighter">
                        Command Center
                    </h1>

                    <button
                        onClick = {() => navigate('/host/quiz/create')}
                        className = "bg-btn-correct text-ink border-4 border-ink px-6 py-3 font-bold font-mono text-xl shadow-brutal-sm hover:-translate-y-1 hover:shadow-brutal-md active:translate-y-1 active:shadow-none transition-all uppercase"
                    >
                        + Create New Quiz
                    </button>
                </div>

                {errorMsg && (
                    <div className = "bg-btn-wrong text-ink border-4 border-ink p-4 mb-8 font-bold font-mono text-lg shadow-brutal-sm uppercase">
                        {errorMsg}
                    </div>
                )}
                
                <div className = "mb-8 bg-card-dark p-6 border-4 border-ink shadow-brutal-sm flex justify-between items-end gap-6 flex-wrap">
                    <div className = "flex-1 min-w-[300px]">
                        <label className = "block text-text-inverted font-mono font-bold text-xl uppercase mb-4">
                            Event Name
                        </label>

                        <input
                            type = 'text'
                            placeholder = 'e.g. Bid2Build'
                            value = {eventName}
                            onChange = {(e) => setEventName(e.target.value)}
                            className = "w-full max-w-md bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-xl focus:outline-none focus:shadow-brutal-md uppercase"
                        />
                    </div>

                    <button
                        onClick = {() => navigate(`/host/tournament/${eventName.trim()}`)}
                        disabled = {!eventName.trim()}
                        className = "bg-btn-correct text-ink border-4 border-ink px-8 py-4 font-bold font-mono text-xl shadow-brutal-sm hover:-translate-y-1 hover:shadow-brutal-md active:translate-y-1 active:shadow-none transition-all uppercase disabled:opacity-50"
                    >
                        View Global Scores
                    </button>
                </div>

                {isLoading ? (
                    <div className = "text-center font-mono text-2xl font-bold uppercase animate-pulse">
                        Retrieving quizzes...
                    </div>
                ) : (
                    <div className = "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {quizzes.length === 0 ? (
                            <div className = "col-span-full bg-card-dark text-text-inverted border-4 border-ink p-12 text-center shadow-brutal-lg">
                                <p className = "font-mono text-2xl uppercase font-bold">
                                    No quizzes found.
                                </p>

                                <p className = "font-mono mt-4 text-text-inverted/70">
                                    Click "Create New Quiz" to begin.
                                </p>
                            </div>
                        ) : (
                            quizzes.map((quiz) => (
                                <div
                                    key = {quiz.id}
                                    className = "bg-btn-neutral border-4 border-ink p-6 shadow-brutal-lg flex flex-col justify-between"
                                >
                                    <div>
                                        <div className = "flex justify-between items-start mb-2">
                                            <div className = "text-xs font-mono font-bold uppercase tracking-widest text-ink/50">
                                                ID: {quiz.id}
                                            </div>

                                            <div className = "flex gap-2">
                                                <button
                                                    onClick = {() => navigate(`/host/quiz/edit/${quiz.id}`)}
                                                    className = "text-ink hover:text-blue-600 font-bold text-xl px-2 transition-colors"
                                                    title = "Edit Quiz"
                                                >
                                                    E
                                                </button>

                                                <button
                                                    onClick = {() => handleDeleteQuiz(quiz.id)}
                                                    disabled = {isDeleting === quiz.id}
                                                    className = "text-btn-wrong hover:text-ink font-bold text-xl px-2 transition-colors disabled:opacity-50"
                                                    title = "Delete Quiz"
                                                >
                                                    X
                                                </button>
                                            </div>
                                        </div>

                                        <h2 className = "text-2xl font-bold uppercase tracking-tight mb-6 line-clamp-2">
                                            {quiz.title}
                                        </h2>
                                    </div>

                                    <button
                                        onClick = {() => handleDeployGame(quiz.id)}
                                        disabled = {deployingId === quiz.id || !eventName.trim()}
                                        className = "w-full bg-ink text-text-inverted font-bold text-xl py-4 border-4 border-ink shadow-brutal-sm hover:-translate-y-1 hover:shadow-brutal-md active:translate-y-1 active:shadow-none transition-all uppercase tracking-widest disabled:opacity-50"
                                    >
                                        {deployingId === quiz.id ? 'Deploying...' : 'Deploy'}
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>

    )

}