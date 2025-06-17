document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const workoutId = urlParams.get('id');
    const form = document.getElementById('edit-workout-form');
    const exercisesContainer = document.getElementById('workout-exercises');
    const workoutNameEl = document.getElementById('workout-name-display');

    if (!workoutId) {
        window.location.href = 'index.html';
        return;
    }

    let workoutData = {};

    async function loadWorkout() {
        try {
            const response = await apiRequest(`workouts/${workoutId}/`);
            if (!response.ok) {
                exercisesContainer.innerHTML = '<p>Failed to load workout data.</p>';
                return;
            }
            workoutData = await response.json();
            workoutNameEl.textContent = workoutData.name || `Workout #${workoutData.id}`;
            render();
        } catch (error) {
            console.error('Error loading workout:', error);
            exercisesContainer.innerHTML = '<p>An error occurred while loading the workout.</p>';
        }
    }

    function render() {
        exercisesContainer.innerHTML = '';
        if (!workoutData.exercises || workoutData.exercises.length === 0) {
            exercisesContainer.innerHTML = '<p>This workout has no exercises yet.</p>';
            return;
        }

        workoutData.exercises.forEach((exercise, exIndex) => {
            const exerciseEl = document.createElement('div');
            exerciseEl.className = 'exercise-set';
            
            const setsHTML = exercise.sets.map((set, setIndex) => `
                <div class="set-inputs">
                    <span>Set ${set.set_number || setIndex + 1}</span>
                    <input type="number" placeholder="Reps" value="${set.reps}" oninput="updateSet(${exIndex}, ${setIndex}, 'reps', this.value)">
                    <input type="number" placeholder="Weight" step="0.01" value="${set.weight}" oninput="updateSet(${exIndex}, ${setIndex}, 'weight', this.value)">
                    <button type="button" class="delete-set-btn" onclick="removeSet(${exIndex}, ${setIndex})">x</button>
                </div>
            `).join('');

            exerciseEl.innerHTML = `
                <div class="exercise-set-header">
                    <h3>${exercise.exercise.name}</h3>
                </div>
                ${setsHTML}
                <button type="button" class="add-set-btn" onclick="addSet(${exIndex})">Add Set</button>
            `;
            exercisesContainer.appendChild(exerciseEl);
        });
    }

    window.updateSet = (exIndex, setIndex, field, value) => {
        workoutData.exercises[exIndex].sets[setIndex][field] = parseFloat(value);
    };

    window.addSet = (exIndex) => {
        const sets = workoutData.exercises[exIndex].sets;
        const lastSet = sets.length > 0 ? sets[sets.length - 1] : { reps: 10, weight: 0 };
        const newSet = { ...lastSet, set_number: sets.length + 1 };
        sets.push(newSet);
        render();
    };

    window.removeSet = (exIndex, setIndex) => {
        workoutData.exercises[exIndex].sets.splice(setIndex, 1);
        // Re-number sets after removal
        workoutData.exercises[exIndex].sets.forEach((set, i) => {
            set.set_number = i + 1;
        });
        render();
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const payload = {
                name: workoutData.name,
                notes: workoutData.notes,
                exercises: workoutData.exercises.map(ex => ({
                    exercise_id: ex.exercise.id,
                    sets: ex.sets.map(set => ({ reps: set.reps, weight: set.weight }))
                }))
            };
            const response = await apiRequest(`workouts/${workoutId}/`, 'PUT', payload);
            if (response.ok) {
                window.location.href = 'index.html';
            } else {
                const error = await response.json();
                alert(`Failed to save workout: ${error.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error saving workout:', error);
            alert('An error occurred while saving the workout.');
        }
    });

    loadWorkout();
});

function cancelChanges() {
    window.location.href = 'index.html';
} 