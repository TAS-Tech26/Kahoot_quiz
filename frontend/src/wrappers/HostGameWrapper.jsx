// HostGameWrapper.jsx


import {useParams} from 'react-router-dom'

import {WebSocketProvider} from '../context/WebSocketContext'

import HostControlPanel from '../pages/HostControlPanel'


export default function HostGameWrapper() {

    const {pin} = useParams()

    if (!pin || !/^\d{6}$/.test(pin)) {
        
        return (

            <Navigate
                to = '/host/dashboard'
                replace
            />

        )

    }

    return (

        <WebSocketProvider
            pin = {pin}
            role = 'host'
        >
            <HostControlPanel />
        </WebSocketProvider>

    )

}