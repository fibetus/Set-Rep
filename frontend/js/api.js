const API_BASE = '/api/v1';

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

async function refreshToken() {
    isRefreshing = true;
    const refresh = localStorage.getItem('refresh');
    if (!refresh) {
        return Promise.reject('No refresh token available.');
    }

    try {
        const response = await fetch(`${API_BASE}/auth/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });
        const data = await response.json();
        if (!response.ok) throw new Error('Failed to refresh token.');

        setToken(data.access, data.refresh || refresh);
        processQueue(null, data.access);
        return data.access;
    } catch (error) {
        processQueue(error, null);
        clearToken();
        window.location.href = 'login.html';
        return Promise.reject(error);
    } finally {
        isRefreshing = false;
    }
}

function getToken() {
    return localStorage.getItem('access');
}

function setToken(token, refresh) {
    localStorage.setItem('access', token);
    if(refresh) localStorage.setItem('refresh', refresh);
}

function clearToken() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
}

async function apiRequest(endpoint, method = 'GET', data = null) {
    const originalRequest = () => {
        const token = getToken();
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers,
            body: data ? JSON.stringify(data) : null,
        };

        return fetch(`${API_BASE}/${endpoint}`, config);
    };

    let response = await originalRequest();

    if (response.status === 401) {
        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            })
            .then(token => {
                return originalRequest();
            })
            .catch(err => {
                return Promise.reject(err);
            });
        }

        try {
            await refreshToken();
            response = await originalRequest();
        } catch (error) {
            return Promise.reject(error);
        }
    }

    return response;
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