// JoinScreen.jsx


import {useState} from 'react'
import {useNavigate} from 'react-router-dom'


export default function JoinScreen() {

    const [formData, setFormData] = useState({
        pin : '',
        fullName : '',
        contactInfo : '',
        schoolName : '',
        gradeLevel : ''
    })

    const [errorMsg, setErrorMsg] = useState(null)

    const navigate = useNavigate()

    const handleChange = (e) => {
        setFormData(prev => ({...prev, [e.target.name] : e.target.value}))

        setErrorMsg(null)
    }

    const handleSubmit = (e) => {
        e.preventDefault()

        if (!/^\d{6}$/.test(formData.pin)) return setErrorMsg("Invalid PIN. Must be exactly 6 digits.")

        if (!formData.fullName.trim() || !formData.contactInfo.trim() || !formData.schoolName.trim() || !formData.gradeLevel.trim()) {
            
            return setErrorMsg("Please fill out all required fields to join.")
        
        }

        navigate(`/game/${formData.pin}`, {
            state : {
                full_name : formData.fullName.trim(),
                contact_info : formData.contactInfo.trim(),
                school_name : formData.schoolName.trim(),
                grade_level : formData.gradeLevel.trim()
            }
        })
    }

    return (

        <div className = "min-h-screen flex items-center justify-center p-4">
            <form
                onSubmit={handleSubmit}
                className = "w-full max-w-lg bg-card-dark border-4 border-ink p-8 shadow-brutal-lg"
            >
                <h1 className = "text-text-inverted text-5xl font-bold mb-8 uppercase tracking-tight">
                    Join Game
                </h1>

                {errorMsg && (
                    <div className = "bg-btn-wrong text-ink border-4 border-ink p-4 mb-8 font-bold font-mono text-lg shadow-brutal-sm">
                        {errorMsg}
                    </div>
                )}

                <div className = "space-y-4 mb-8">
                    <input
                        type = 'text'
                        placeholder = "6-Digit PIN *"
                        required
                        value = {formData.pin}
                        onChange = {handleChange}
                        className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50"
                    />

                    <input
                        type = 'text'
                        placeholder = "Full Name *"
                        required
                        value = {formData.fullName}
                        onChange = {handleChange}
                        className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50"
                    />

                    <input
                        type = 'text'
                        placeholder = "Email/Phone *"
                        required
                        value = {formData.contactInfo}
                        onChange = {handleChange}
                        className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50"
                    />

                    <div className = "flex gap-4">
                        <input
                            type = 'text'
                            placeholder = "School Name *"
                            required
                            value = {formData.schoolName}
                            onChange = {handleChange}
                            className = "w-2/3 bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50"
                        />

                        <input
                            type = 'text'
                            placeholder = "Grade *"
                            required
                            value = {formData.gradeLevel}
                            onChange = {handleChange}
                            className = "w-1/3 bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50"
                        />
                    </div>
                </div>

                <button
                    type = 'submit'
                    className = "w-full bg-ink text-text-inverted font-bold text-2xl py-4 border-4 border-ink shadow-brutal-md transition-all hover:-translate-y-1 hover:shadow-brutal-lg active:translate-y-1.5 active:translate-x-1.5 active:shadow-none"
                >
                    Join Game
                </button>
            </form>
        </div>

    )

}