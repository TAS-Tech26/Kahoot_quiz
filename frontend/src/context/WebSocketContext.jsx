// WebSocketContext.jsx


import {createContext, useContext, useEffect, useRef, useState} from 'react'
import {useLocation, useNavigate} from 'react-router-dom'


const WebSocketContext = createContext(null)


export const WebSocketProvider = ({pin, role, children}) => {

    const [lastMessage, setLastMessage] = useState(null)
    const [isConnected, setIsConnected] = useState(false)

    const socketRef = useRef(null) // Prevents multiple sockets (keeps the socket value persisting) from spawning during re-renders

    const navigate = useNavigate()
    const location = useLocation() // Read the data passed from JoinScreen

    useEffect(() => {
        if (!pin) return

        const wsBase = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws'
        let wsUrl = `${wsBase}/game/${pin}/`

        if (role === 'host') {
            const token = localStorage.getItem('access_token')

            if (!token) {
                console.error("Host connection failed: Missing authentication token.")

                navigate('/host/login', {replace : true})

                return
            }

            wsUrl += `?token=${token}`
        }

        const ws = new WebSocket(wsUrl)

        socketRef.current = ws

        ws.onopen = () => {
            setIsConnected(true)

            if (role === 'player') {
                const savedPlayerId = localStorage.getItem('player_id')
                const registrationData = location.state() // Fetched from router

                if (savedPlayerId) {
                    // Recover player ID if disconnected
                    ws.send(JSON.stringify({action : 'player_join', role : 'player', data : {player_id : savedPlayerId}}))
                } else if (registrationData) {
                    // New player registration
                    ws.send(JSON.stringify({action : 'player_join', role : 'player', data : registrationData}))

                    window.history.replaceState({}, document.title)
                } else {
                    console.error("Connection rejected: No player registration data found.")

                    ws.close()

                    navigate('/')
                }
            } else if (role === 'host') {
                console.log("Host connected to game room.")
            }
        }

        ws.onmessage = (event) => {
            const parsedData = JSON.parse(event.data)

            setLastMessage(parsedData)

            // Auto-save player_id to localStorage when backend sends 1
            if (['join_success', 'rejoin_success'].includes(parsedData.event)) localStorage.setItem('player_id', parsedData.data.player_id)
        }

        ws.onclose = () => setIsConnected(false)

        return () => ws.close()
    }, [pin, navigate, role, location.state])

    const sendMessage = (action, role, data = {}) => {
        if (socketRef.current?.readyState === WebSocket.OPEN) socketRef.current.send(JSON.stringify({action, role, data}))
    }

    return (

        <WebSocketContext.Provider value = {{sendMessage, lastMessage, isConnected}}>
            {children}
        </WebSocketContext.Provider>
    
    )

}

export const useWebSocket = () => useContext(WebSocketContext)