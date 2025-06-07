const API_BASE = '/api/v1';

function getToken() {
    return localStorage.getItem('access');
}

function setToken(token, refresh) {
    localStorage.setItem('access', token);
    localStorage.setItem('refresh', refresh);
}

function clearToken() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
}

async function apiRequest(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
    };

    // Add authorization header if token exists
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method,
        headers,
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}/${endpoint}`, config);
        const responseData = await response.json();

        if (!response.ok) {
            // Handle token expiration
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = 'login.html';
                throw new Error('Session expired. Please login again.');
            }
            throw new Error(responseData.detail || 'An error occurred');
        }

        return responseData;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// User related API calls
async function registerUser(userData) {
    return apiRequest('users/', 'POST', userData);
}

async function loginUser(credentials) {
    return apiRequest('auth/token/', 'POST', credentials);
}

async function getUserProfile() {
    return apiRequest('users/me/');
}

// Workout related API calls
async function getWorkouts() {
    return apiRequest('workouts/');
}

async function createWorkout(workoutData) {
    return apiRequest('workouts/', 'POST', workoutData);
}

async function updateWorkout(workoutId, workoutData) {
    return apiRequest(`workouts/${workoutId}/`, 'PUT', workoutData);
}

async function deleteWorkout(workoutId) {
    return apiRequest(`workouts/${workoutId}/`, 'DELETE');
}

// Training plan related API calls
async function getTrainingPlans() {
    return apiRequest('training-plans/');
}

async function createTrainingPlan(planData) {
    return apiRequest('training-plans/', 'POST', planData);
}

async function updateTrainingPlan(planId, planData) {
    return apiRequest(`training-plans/${planId}/`, 'PUT', planData);
}

async function deleteTrainingPlan(planId) {
    return apiRequest(`training-plans/${planId}/`, 'DELETE');
} 