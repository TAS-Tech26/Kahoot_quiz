// HostProtectedRoute.jsx


import {Navigate} from 'react-router-dom'


export default function HostProtectedRoute({children}) {
    
    const token = localStorage.getItem('token')

    if (!token || token === 'undefined' || token === 'null') {

        return (

            <Navigate
                to = '/host/login'
                replace
            />
            
        )
        
    }

    return children

}