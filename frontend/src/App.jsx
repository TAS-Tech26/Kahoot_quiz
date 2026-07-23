// App.jsx


import {BrowserRouter, Route, Routes} from 'react-router-dom'

import HostLogin from './pages/HostLogin'
import JoinScreen from './pages/JoinScreen'
import NotFound from './pages/NotFound'
import SessionCreator from './pages/SessionCreator'

import HostGameWrapper from './wrappers/HostGameWrapper'
import HostProtectedRoute from './wrappers/HostProtectedRoute'
import PlayerGameWrapper from './wrappers/PlayerGameWrapper'


export default function App() {

    return (

        <BrowserRouter>
            <Routes>
                {/* Player Routes */}
                <Route
                    path = '/'
                    element = {<JoinScreen />}
                />

                <Route
                    path = '/game/:pin'
                    element = {<PlayerGameWrapper />}
                />

                {/* Host Routes */}
                <Route
                    path = '/host/login'
                    element = {<HostLogin />}
                />

                <Route
                    path = '/host/create-session'
                    element = {
                        <HostProtectedRoute>
                            <SessionCreator />
                        </HostProtectedRoute>
                    }
                />

                <Route
                    path = '/host/game/:pin'
                    element = {
                        <HostProtectedRoute>
                            <HostGameWrapper />
                        </HostProtectedRoute>
                    }
                />

                <Route
                    path = '*'
                    element = {<NotFound />}
                />
            </Routes>
        </BrowserRouter>

    )

}