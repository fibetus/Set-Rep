// Authentication functions
function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function removeToken() {
    localStorage.removeItem('access_token');
}

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
                    setToken(data.access);
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
            removeToken();
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
                    workoutsContainer.innerHTML = workouts.map(workout => `
                        <div class="workout-card">
                            <h3>${workout.name}</h3>
                            <p>Date: ${new Date(workout.date).toLocaleDateString()}</p>
                            <p>Exercises: ${workout.exercises.length}</p>
                        </div>
                    `).join('');
                }
            }
        } catch (error) {
            console.error('Error loading workouts:', error);
        }
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
}); 