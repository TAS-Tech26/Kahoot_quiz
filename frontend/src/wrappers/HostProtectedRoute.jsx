// HostProtectedRoute.jsx


import {Navigate} from 'react-router-dom'


export default function HostProtectedRoute({children}) {
    
    const token = localStorage.getItem('access_token')

    if (!token) {

        return (

            <Navigate
                to = '/host/login'
                replace
            />
            
        )
        
    }

    return children

}