// HostLogin.jsx


import {useState} from 'react'
import {useNavigate} from 'react-router-dom'

import {loginHost} from '../api/api'


export default function HostLogin() {

    const [credentials, setCredentials] = useState({username : '', password : ''})
    const [errorMsg, setErrorMsg] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    
    const navigate = useNavigate()

    const handleChange = (e) => {
        setCredentials((prev) => ({...prev, [e.target.name] : e.target.value}))
        setErrorMsg('') // Clear err when typing
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        if (!credentials.username.trim() || !credentials.password.trim()) {
            setErrorMsg("Credentials cannot be empty.")

            return
        }

        setIsLoading(true)
        setErrorMsg('')

        try {
            const response = await loginHost(credentials)
            const data = await response.json()

            if (response.ok) {
                localStorage.setItem('token', data.token)

                navigate('/host/create-session', {replace : true})
            } else {
                setErrorMsg(data.detail || "Invalid administrative credentials.")
            }
        } catch (err) {
            setErrorMsg("CRITICAL ERROR: Failed to establish contact with the server.")
        } finally {
            setIsLoading(false)
        }
    }

    return (

        <div className = "min-h-screen flex items-center justify-center p-4 bg-bg-base">
            <form
                onSubmit = {handleSubmit}
                className = "w-full max-w-lg bg-card-dark border-4 border-ink p-8 md:p-12 shadow-brutal-lg"
            >
                <div className = "mb-10 border-b-4 border-ink pb-4">
                    <h1 className = "text-text-inverted text-5xl font-bold uppercase tracking-tighter">
                        Host Access
                    </h1>

                    <p className = "text-text-inverted/70 font-mono mt-2 uppercase tracking-widest">
                        System Authentication
                    </p>
                </div>

                {errorMsg && (
                    <div className = "bg-btn-wrong text-ink border-4 border-ink p-4 mb-8 font-bold font-mono text-lg shadow-brutal-sm uppercase">
                        {errorMsg}
                    </div>
                )}

                <div className = "space-y-6 mb-10">
                    <div>
                        <label className = "block text-text-inverted font-mono text-xl mb-2 uppercase">
                            Username
                        </label>

                        <input
                            type = 'text'
                            name = 'username'
                            required
                            value = {credentials.username}
                            onChange = {handleChange}
                            className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow"
                        />
                    </div>

                    <div>
                        <label className = "block text-text-inverted font-mono text-xl mb-2 uppercase">
                            Password
                        </label>

                        <input
                            type = 'password'
                            name = 'password'
                            required
                            value = {credentials.password}
                            onChange = {handleChange}
                            className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow"
                        />
                    </div>
                </div>

                <button
                    type = 'submit'
                    disabled = {isLoading}
                    className = "w-full bg-ink text-text-inverted font-bold text-2xl py-5 border-4 border-ink shadow-brutal-md transition-all hover:-translate-y-1 hover:shadow-brutal-lg active:translate-y-1.5 active:translate-x-1.5 active:shadow-none disabled:opacity-50 disabled:pointer-events-none uppercase tracking-widest"
                >
                    {isLoading
                        ? "Logging in..."
                        : "Log in"
                    }
                </button>
            </form>
        </div>

    )

}