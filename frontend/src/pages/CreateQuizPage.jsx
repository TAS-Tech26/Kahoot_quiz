// CreatePageQuiz.jsx


import {useNavigate} from 'react-router-dom'

import QuizBuilder from '../features/QuizBuilder/QuizBuilder'


export default function CreateQuizPage() {

    const navigate = useNavigate()

    return (

        <div className = "min-h-screen bg-bg-base flex flex-col">
            <div className = "w-full bg-card-dark border-b-4 border-ink p-4 flex justify-between items-center shadow-brutal-sm z-10">
                <h1 className = "text-text-inverted font-bold text-2xl uppercase tracking-tighter ml-4">
                    Quiz Creator
                </h1>

                <button
                    onClick = {() => navigate('/host/create-session')}
                    className = "bg-btn-neutral text-ink border-4 border-ink font-bold font-mono text-lg px-6 py-2 shadow-brutal-sm hover:-translate-y-1 hover:shadow-brutal-md active:translate-y-1 active:shadow-none transition-all uppercase"
                >
                    Back to Main Page
                </button>
            </div>
            
            <div className = 'flex-1'>
                <QuizBuilder/>
            </div>
        </div>

    )

}