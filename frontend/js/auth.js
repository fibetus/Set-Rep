// Authentication functions

// Login form handling
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            
            try {
                const response = await fetch('/api/v1/auth/token/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: formData.get('email'),
                        password: formData.get('password'),
                    }),
                });

                const data = await response.json();
                
                if (response.ok) {
                    setToken(data.access, data.refresh);
                    window.location.href = 'index.html';
                } else {
                    const errorMessage = document.getElementById('error-message');
                    errorMessage.textContent = data.detail || 'Login failed. Please check your credentials.';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                console.error('Login error:', error);
                const errorMessage = document.getElementById('error-message');
                errorMessage.textContent = 'An error occurred. Please try again.';
                errorMessage.style.display = 'block';
            }
        });
    }

    // Register form handling
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            
            // Validate passwords match
            if (formData.get('password') !== formData.get('password2')) {
                const errorMessage = document.getElementById('error-message');
                errorMessage.textContent = 'Passwords do not match.';
                errorMessage.style.display = 'block';
                return;
            }

            try {
                const response = await fetch('/api/v1/users/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: formData.get('username'),
                        email: formData.get('email'),
                        password: formData.get('password'),
                    }),
                });

                const data = await response.json();
                
                if (response.ok) {
                    // Registration successful, redirect to login
                    window.location.href = 'login.html';
                } else {
                    const errorMessage = document.getElementById('error-message');
                    errorMessage.textContent = data.detail || 'Registration failed. Please try again.';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                console.error('Registration error:', error);
                const errorMessage = document.getElementById('error-message');
                errorMessage.textContent = 'An error occurred. Please try again.';
                errorMessage.style.display = 'block';
            }
        });
    }

    // Logout button handling
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            clearToken();
            window.location.href = 'index.html';
        });
    }

    const showError = (message) => {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    };

    const navigateTo = (url) => {
        window.location.href = url;
    };

    const loadWorkouts = async () => {
        try {
            const response = await fetch('/api/v1/workouts/', {
                headers: {
                    'Authorization': `Bearer ${getToken()}`
                }
            });
            if (response.ok) {
                const workouts = await response.json();
                const workoutsContainer = document.getElementById('workouts-container');
                if (workoutsContainer) {
                    workoutsContainer.innerHTML = workouts.map(workout => {
                        // Use name if present, otherwise use formatted date/time
                        let displayName = (workout.name && workout.name !== '' && workout.name !== 'undefined')
                            ? workout.name
                            : (workout.date ? `${new Date(workout.date).toLocaleDateString('pl-PL', {day:'2-digit', month:'2-digit', year:'numeric'})} - Workout #${workout.id}: ${new Date(workout.date).toLocaleTimeString('pl-PL', {hour:'2-digit', minute:'2-digit'})}` : 'Workout');
                        return `
                        <div class="workout-card">
                            <h3>${displayName}</h3>
                            <p>Date: ${workout.date ? new Date(workout.date).toLocaleDateString('pl-PL', {day:'2-digit', month:'2-digit', year:'numeric'}) : ''}</p>
                            <p>Exercises: ${workout.exercises ? workout.exercises.length : 0}</p>
                            <div class="workout-card-actions">
                                <button class="edit-btn" onclick="editWorkoutFromHome(${workout.id})">Edit</button>
                                <button class="delete-btn" onclick="deleteWorkoutFromHome(${workout.id})">Delete</button>
                            </div>
                        </div>
                        `;
                    }).join('');
                }
            }
        } catch (error) {
            console.error('Error loading workouts:', error);
        }
    };

    // Home button handler
    window.goHome = function() {
        window.location.href = 'index.html';
    };

    // Edit workout from home page
    window.editWorkoutFromHome = function(workoutId) {
        window.location.href = `edit-workout.html?id=${workoutId}`;
    };

    window.acceptWorkoutChanges = function() {
        window.location.href = 'index.html';
    };
    window.cancelWorkoutChanges = function() {
        window.location.href = 'index.html';
    };

    // Check authentication status on protected pages
    const protectedPages = ['workout.html', 'plan.html'];
    if (protectedPages.some(page => window.location.pathname.includes(page))) {
        if (!getToken()) {
            navigateTo('login.html');
        }
    }

    // Load workouts if on home page and logged in
    if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname === '') {
        if (getToken()) {
            loadWorkouts();
        }
    }

    window.deleteWorkoutFromHome = async function(workoutId) {
        if (!confirm('Are you sure you want to delete this workout?')) return;
        try {
            const response = await fetch(`/api/v1/workouts/${workoutId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${getToken()}`
                }
            });
            if (response.ok) {
                // Reload workouts
                loadWorkouts();
            } else {
                alert('Failed to delete workout');
            }
        } catch (error) {
            alert('Failed to delete workout');
        }
    };
}); 