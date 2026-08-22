// api.js


const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001/api'


export const apiCall = async (endpoint, options = {}) => {

    const token = localStorage.getItem('access_token')

    const headers = {'Content-Type' : 'application/json', ...options.headers}

    if (token) headers['Authorization'] = `Bearer ${token}`

    const response = await fetch(`${BASE_URL}${endpoint}`, {...options, headers})

    if (response.status === 401) {
        console.error("Session expired. Please log in again.")

        localStorage.removeItem('access_token')

        window.location.href = '/host/login'
    }

    return response
 
}

export const loginHost = (credentials) => apiCall('/token/', {method : 'POST', body : JSON.stringify(credentials)})

export const createGameSession = (quizId, eventName) => apiCall('/game/create/', {method : 'POST', body : JSON.stringify({quiz_id : quizId, event_name : eventName})})

export const getHostQuizzes = () => apiCall('/quizzes/', {method : 'GET'})

export const verifyPin = (pin) => apiCall(`/game/verify/${pin}`, {method : 'GET'})

export const deleteHostQuiz = (quizId) => apiCall(`/quizzes/${quizId}/delete/`, {method : 'DELETE'})

export const updateHostQuiz = (quizId, data) => apiCall(`/quizzes/${quizId}/update/`, {method : 'PUT', body : JSON.stringify(data)})

export const getHostQuizDetail = (quizId) => apiCall(`/quizzes/${quizId}/`, {method : 'GET'})

export const getTournamentLeaderboard = (eventName) => apiCall(`/export-scores/${eventName}/`, {method : 'GET'})