// api.js


const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001/api'


export const apiCall = async (endpoint, options = {}) => {

    const token = localStorage.getItem('token')

    const headers = {'Content-Type' : 'application/json', ...options.headers}

    if (token) headers['Authorization'] = `Bearer ${token}`

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {...options, headers})

        if (response.status === 401) {
            console.error("Session expired. Please log in again.")

            localStorage.removeItem('token')

            window.location.href = '/host/login'
        }

        return response
    } catch (error) {
        console.error("Network or API Call Error:", error)
        throw error
    }
 
}

export const loginHost = async (credentials) => {
    const hubUrl = import.meta.env.VITE_HUB_API_URL || 'http://127.0.0.1:8000/api'

    return fetch(`${hubUrl}/host/login/`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(credentials)})
}

export const createGameSession = (quizId, eventName) => apiCall('/game/create/', {method: 'POST', body: JSON.stringify({quiz_id: quizId, event_name: eventName})})

export const getHostQuizzes = () => apiCall('/quizzes/', {method: 'GET'})

export const verifyPin = (pin) => apiCall(`/game/verify/${pin}`, {method: 'GET'})

export const deleteHostQuiz = (quizId) => apiCall(`/quizzes/${quizId}/delete/`, {method: 'DELETE'})

export const updateHostQuiz = (quizId, data) => apiCall(`/quizzes/${quizId}/update/`, {method: 'PUT', body: JSON.stringify(data)})

export const getHostQuizDetail = (quizId) => apiCall(`/quizzes/${quizId}/`, {method: 'GET'})

export const getTournamentLeaderboard = (eventName) => apiCall(`/export-scores/${eventName}/`, {method: 'GET'})