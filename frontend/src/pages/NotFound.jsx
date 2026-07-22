// NotFound.jsx


import {Link} from 'react-router-dom'


export default function NotFound() {

    return (

        <div className = "min-h-screen flex items-center justify-center p-4 bg-bg-base">
            <div className = "w-full max-w-lg bg-card-dark border-4 border-ink p-8 md:p-12 text-center shadow-brutal-lg flex flex-col items-center">
                <h1 className = "text-text-inverted text-8xl font-bold mb-4 uppercase tracking-tighter">
                    404
                </h1>

                <h2 className = "text-text-inverted/90 text-3xl font-bold mb-6 uppercase tracking-tight">
                    Page Not Found
                </h2>

                <p className = "text-text-inverted/70 font-mono text-lg mb-10 uppercase">
                    The page you are looking for doesn't exist or the link is broken.
                </p>

                <Link
                    to = '/'
                    className = "w-full inline-block bg-ink text-text-inverted font-bold text-2xl py-4 border-4 border-ink shadow-brutal-md transition-all hover:-translate-y-1 hover:shadow-brutal-lg active:translate-y-1.5 active:translate-x-1.5 active:shadow-none uppercase"
                >
                    Return to Home
                </Link>
            </div>
        </div>
    
    )

}