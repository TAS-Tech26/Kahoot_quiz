// JoinScreen.jsx


import {useState} from 'react'
import {useNavigate} from 'react-router-dom'

import {verifyPin} from '../api/api'


export default function JoinScreen() {

    const [step, setStep] = useState(1)
    const [pin, setPin] = useState('')
    const [teamPin, setTeamPin] = useState('')
    const [errorMsg, setErrorMsg] = useState(null)
    const [isLoading, setIsLoading] = useState(false)

    const navigate = useNavigate()

    const handleVerifyRoom = async (e) => {
        e.preventDefault()

        if (!/^\d{6}$/.test(pin)) return setErrorMsg("Invalid Room PIN. Must be exactly 6 digits.")

        setIsLoading(true)
        setErrorMsg(null)

        try {
            const response = await verifyPin(pin)

            if (response.ok) {
                setStep(2)
            } else {
                setErrorMsg("Room not found or inactive.")
            }
        } catch (err) {
            setErrorMsg("Failed to contact the server.")
        } finally {
            setIsLoading(false)
        }
    }

    const handleJoinGame = (e) => {
        e.preventDefault()

        if (!teamPin.trim()) return setErrorMsg("Team PIN is required.")
        if (isLoading) return
        
        setIsLoading(true)

        navigate(`/game/${pin}`, {state : {team_pin : teamPin.trim()}})
    }

    return (

        <div className = "min-h-screen flex items-center justify-center p-4 bg-bg-base">
            <div className = "w-full max-w-lg bg-card-dark border-4 border-ink p-8 shadow-brutal-lg">
                <h1 className = "text-text-inverted text-5xl font-bold mb-8 uppercase tracking-tight">
                    {step === 1 ? "Join Game" : "Team Verification"}
                </h1>

                {errorMsg && (
                    <div className = "bg-btn-wrong text-ink border-4 border-ink p-4 mb-8 font-bold font-mono text-lg shadow-brutal-sm">
                        {errorMsg}
                    </div>
                )}

                {step === 1 ? (
                    <form onSubmit = {handleVerifyRoom}>
                        <input
                            type = 'text'
                            placeholder = "6-Digit Room PIN"
                            required
                            value = {pin}
                            onChange = {(e) => {
                                setPin(e.target.value)
                                setErrorMsg(null)
                            }}
                            className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 mb-8 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50 uppercase"
                        />

                        <button
                            type = 'submit'
                            disabled = {isLoading}
                            className = "w-full bg-ink text-text-inverted font-bold text-2xl py-4 border-4 border-ink shadow-brutal-md hover:-translate-y-1 hover:shadow-brutal-lg active:translate-y-1.5 active:translate-x-1.5 active:shadow-none transition-all uppercase disabled:opacity-50"
                        >
                            {isLoading ? 'Verifying...' : "Enter Room"}
                        </button>
                    </form>
                ) : (
                    <form onSubmit = {handleJoinGame}>
                        <div className = "bg-bg-base border-4 border-ink p-4 mb-6 text-ink font-mono font-bold uppercase text-center">
                            Room: {pin}
                        </div>

                        <input
                            type = 'text'
                            placeholder = "Team PIN"
                            required
                            value = {teamPin}
                            onChange = {(e) => {
                                setTeamPin(e.target.value)
                                setErrorMsg(null)
                            }}
                            className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 mb-8 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50 uppercase"
                        />

                        <button
                            type = 'submit'
                            disabled = {isLoading}
                            className = "w-full bg-btn-correct text-ink font-bold text-2xl py-4 border-4 border-ink shadow-brutal-md hover:-translate-y-1 hover:shadow-brutal-lg active:translate-y-1.5 active:translate-x-1.5 active:shadow-none transition-all uppercase disabled:opacity-50"
                        >
                            {isLoading ? 'Logging In...' : 'Log In'}
                        </button>
                    </form>
                )}
            </div>
        </div>

    )

}