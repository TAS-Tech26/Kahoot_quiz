// PlayerGameWrapper.jsx


import {useParams, Navigate} from 'react-router-dom'

import {WebSocketProvider} from '../WebSocketContext'

import GameRoom from '../pages/GameRoom'


export default function PlayerGameWrapper() {

    const {pin} = useParams()

    if (!pin || !/^\d{6}$/.test(pin)) {
        
        return (

            <Navigate
                to = '/'
                replace
            />

        )

    }

    return (

        <WebSocketProvider
            pin = {pin}
            role = 'player'
        >
            <GameRoom />
        </WebSocketProvider>

    )

}