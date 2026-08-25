// WebSocketContext.jsx


import {act, createContext, useContext, useEffect, useRef, useState} from 'react'
import {useLocation, useNavigate} from 'react-router-dom'


const WebSocketContext = createContext(null)


export const WebSocketProvider = ({pin, role, children}) => {

    const [lastMessage, setLastMessage] = useState(null)
    const [isConnected, setIsConnected] = useState(false)

    const socketRef = useRef(null) // Prevents multiple sockets (keeps the socket value persisting) from spawning during re-renders

    const navigate = useNavigate()
    const location = useLocation() // Read the data passed from JoinScreen

    const registrationStateRef = useRef(location.state)

    useEffect(() => {
        if (!pin) return

        const wsBase = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8001/ws'
        let wsUrl = `${wsBase}/game/${pin}/`

        if (role === 'host') {
            const token = localStorage.getItem('token')

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
                const savedTeamPin = localStorage.getItem(`team_pin_${pin}`)
                const registrationData = registrationStateRef.current // Fetched from router
                
                const activeTeamPin = registrationData?.team_pin || savedTeamPin

                if (activeTeamPin) {
                    localStorage.setItem(`team_pin_${pin}`, activeTeamPin)

                    // Recover player ID if disconnected
                    ws.send(JSON.stringify({action : 'player_join', role : 'player', data : {team_pin : activeTeamPin}}))
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
            try {
                const parsedData = JSON.parse(event.data)

                setLastMessage(parsedData)

                // Auto-save player_id to localStorage when backend sends 1
                if (['join_success', 'rejoin_success'].includes(parsedData.event)) localStorage.setItem(`team_pin_${pin}`, parsedData.data.team_pin)
            } catch (err) {
                console.error("Failed to parse incoming WS message : ", err)
            }
        }

        ws.onclose = () => setIsConnected(false)

        return () => {

            if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) ws.close()
                
        }
    }, [pin, navigate, role])

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