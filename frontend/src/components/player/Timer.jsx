// Timer.jsx


import {useEffect, useState} from 'react'


export default function Timer({timeLimit, onTimeUp}) {

    const [timeLeft, setTimeLeft] = useState(timeLimit)

    useEffect(() => {
        if (timeLeft <= 0) {
            if (onTimeUp) onTimeUp()

            return
        }

        const timer = setInterval(() => {
            setTimeLeft((prev) => prev - 1)
        }, 1000);

        return () => clearInterval(timer)
    }, [timeLeft, onTimeUp])

    const percentage = (timeLeft / timeLimit) * 100 // Percentage for progress bar

    let barColor = 'bg-btn-correct'

    if (percentage <= 50) barColor = 'bg-yellow-400'
    if (percentage <= 20) barColor = 'bg-btn-wrong'

    return (

        <div className = "w-full mb-8">
            <div className = "flex justify-between items-end mb-2 font-mono font-bold text-2xl uppercase text-ink">
                <span>Time Remaining</span>

                <span className = {timeLeft <= 3 ? "animate-pulse text-btn-wrong" : ''}>
                    {timeLeft}s
                </span>
            </div>

            <div className = "w-full h-8 bg-card-dark border-4 border-ink shadow-brutal-sm relative overflow-hidden">
                {/* Shrinking progress bar */}
                <div
                    className = {`h-full ${barColor} border-r-4 border-ink transition-all duration-1000 ease-linear`}
                    style = {{width : `${percentage}%`}}
                />
            </div>
        </div>

    )

}