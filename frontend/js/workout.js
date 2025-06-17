document.addEventListener('DOMContentLoaded', () => {
    const exercisesGrid = document.getElementById('exercises-grid');
    const selectedExercisesContainer = document.getElementById('selected-exercises');
    const muscleGroupsContainer = document.getElementById('muscle-groups');

    const urlParams = new URLSearchParams(window.location.search);
    const workoutId = urlParams.get('id');

    let selectedExercises = new Map();

    const checkAuth = () => {
        if (!localStorage.getItem('access_token')) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    };

    const apiRequest = async (endpoint, method = 'GET', body = null) => {
        const headers = new Headers({
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        });

        const config = { method, headers };
        if (body) {
            config.body = JSON.stringify(body);
        }

        const response = await fetch(`/api/v1${endpoint}`, config);
        if (response.status === 401) {
            window.location.href = 'login.html';
        }
        return response;
    };
    
    const loadMuscleGroups = async () => {
        const response = await apiRequest('/muscle-groups/');
        if (response.ok) {
            const muscleGroups = await response.json();
            muscleGroupsContainer.innerHTML = muscleGroups.map(mg => 
                `<button class="muscle-group-btn" onclick="loadExercises(${mg.id})">${mg.name}</button>`
            ).join('');
        }
    };
    
    window.loadExercises = async (muscleGroupId = null) => {
        let endpoint = '/exercises/';
        if (muscleGroupId) {
            endpoint += `?muscle_group=${muscleGroupId}`;
        }
        const response = await apiRequest(endpoint);
        if (response.ok) {
            const exercises = await response.json();
            renderAvailableExercises(exercises);
        }
    };

    const renderAvailableExercises = (exercises) => {
        exercisesGrid.innerHTML = exercises.map(ex => `
            <div class="exercise-card">
                <h3>${ex.name}</h3>
                <p>${ex.description || 'No description available.'}</p>
                <button onclick="addExerciseToWorkout(${ex.id}, '${ex.name}')">Add to Workout</button>
            </div>
        `).join('');
    };

    window.addExerciseToWorkout = (exerciseId, exerciseName) => {
        if (!selectedExercises.has(exerciseId)) {
            selectedExercises.set(exerciseId, {
                id: exerciseId,
                name: exerciseName,
                sets: [{ reps: 10, weight: 20 }] // Start with one default set
            });
            renderSelectedExercises();
        }
    };

    window.removeExercise = (exerciseId) => {
        if (selectedExercises.has(exerciseId)) {
            selectedExercises.delete(exerciseId);
            renderSelectedExercises();
        }
    };

    window.addSet = (exerciseId) => {
        const exercise = selectedExercises.get(exerciseId);
        if (exercise) {
            exercise.sets.push({ reps: 10, weight: 20 });
            renderSelectedExercises();
        }
    };

    window.removeSet = (exerciseId, setIndex) => {
        const exercise = selectedExercises.get(exerciseId);
        if (exercise && exercise.sets[setIndex]) {
            exercise.sets.splice(setIndex, 1);
            renderSelectedExercises();
        }
    };
    
    window.updateSet = (exerciseId, setIndex, field, value) => {
        const exercise = selectedExercises.get(exerciseId);
        if (exercise && exercise.sets[setIndex]) {
            exercise.sets[setIndex][field] = value;
        }
    };

    const renderSelectedExercises = () => {
        selectedExercisesContainer.innerHTML = '';
        if (selectedExercises.size === 0) {
            selectedExercisesContainer.innerHTML = '<p>No exercises added yet.</p>';
            return;
        }

        selectedExercises.forEach((exercise) => {
            const exerciseEl = document.createElement('div');
            exerciseEl.className = 'exercise-set';
            
            const setsHTML = exercise.sets.map((set, index) => `
                <div class="set-inputs">
                    <span>Set ${index + 1}</span>
                    <input type="number" placeholder="Reps" value="${set.reps}" oninput="updateSet(${exercise.id}, ${index}, 'reps', this.value)">
                    <input type="number" placeholder="Weight" step="0.5" value="${set.weight}" oninput="updateSet(${exercise.id}, ${index}, 'weight', this.value)">
                    <button class="delete-set-btn" onclick="removeSet(${exercise.id}, ${index})">x</button>
                </div>
            `).join('');

            exerciseEl.innerHTML = `
                <div class="exercise-set-header">
                    <h3>${exercise.name}</h3>
                    <button class="remove-exercise-btn" onclick="removeExercise(${exercise.id})">Remove</button>
                </div>
                ${setsHTML}
                <button class="add-set-btn" onclick="addSet(${exercise.id})">Add Set</button>
            `;
            selectedExercisesContainer.appendChild(exerciseEl);
        });
    };

    window.saveWorkout = async () => {
        if (!checkAuth()) return;

        const exercisesPayload = Array.from(selectedExercises.values()).map(ex => ({
            exercise_id: ex.id,
            sets: ex.sets.map(set => ({
                reps: parseInt(set.reps, 10),
                weight: parseFloat(set.weight)
            }))
        }));

        const method = workoutId ? 'PUT' : 'POST';
        const endpoint = workoutId ? `/workouts/${workoutId}/` : '/workouts/';
        
        const response = await apiRequest(endpoint, method, { exercises: exercisesPayload });

        if (response.ok) {
            showNotification('Workout saved successfully!', 'success');
            setTimeout(() => window.location.href = 'index.html', 1500);
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Failed to save workout.', 'error');
        }
    };

    const loadWorkoutForEditing = async (id) => {
        const response = await apiRequest(`/workouts/${id}/`);
        if (response.ok) {
            const workout = await response.json();
            document.querySelector('h1').textContent = `Edit Workout - ${workout.name}`;
            
            selectedExercises.clear();
            workout.exercises.forEach(ex => {
                selectedExercises.set(ex.exercise.id, {
                    id: ex.exercise.id,
                    name: ex.exercise.name,
                    sets: ex.sets.map(s => ({ reps: s.reps, weight: s.weight }))
                });
            });
            renderSelectedExercises();
        } else {
            showNotification('Failed to load workout for editing.', 'error');
        }
    };

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
    
    // Initial Load
    const init = async () => {
        if (!checkAuth()) return;
        
        await loadMuscleGroups();
        await window.loadExercises(); // Load all exercises initially
        
        if (workoutId) {
            await loadWorkoutForEditing(workoutId);
        } else {
            renderSelectedExercises();
        }
    };

    init();
}); 