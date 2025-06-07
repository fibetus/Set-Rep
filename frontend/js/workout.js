document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('id');
    const sessionControls = document.getElementById('session-controls');
    const workoutContent = document.getElementById('workout-content');

    if (!sessionId) {
        // Start new session
        sessionControls.innerHTML = `<button id="start-session-btn">Start New Session</button>`;
        document.getElementById('start-session-btn').onclick = async () => {
            let resp = await apiRequest('/sessions/', 'POST', { notes: '' });
            if (resp.ok) {
                let data = await resp.json();
                window.location = `workout.html?id=${data.id}`;
            } else {
                alert('Failed to start session');
            }
        };
        return;
    }

    // Load session details
    let resp = await apiRequest(`/sessions/${sessionId}/`);
    if (!resp.ok) {
        workoutContent.innerText = 'Failed to load session.';
        return;
    }
    let session = await resp.json();
    renderSession(session);

    async function renderSession(session) {
        let html = `<h2>Session #${session.id}</h2>`;
        html += `<div>Start: ${new Date(session.start_time).toLocaleString()}</div>`;
        if (session.end_time) {
            html += `<div>End: ${new Date(session.end_time).toLocaleString()}</div>`;
        } else {
            html += `<button id="end-session-btn">End Session</button>`;
        }
        html += `<label>Notes:</label><textarea id="session-notes">${session.notes || ''}</textarea><button id="save-notes-btn">Save Notes</button>`;
        html += `<h3>Logged Exercises</h3>`;
        html += `<div id="logged-exercises"></div>`;
        html += `<h4>Add Exercise</h4><div id="add-exercise"></div>`;
        workoutContent.innerHTML = html;
        document.getElementById('save-notes-btn').onclick = async () => {
            let notes = document.getElementById('session-notes').value;
            await apiRequest(`/sessions/${session.id}/`, 'PATCH', { notes });
            alert('Notes saved!');
        };
        if (!session.end_time) {
            document.getElementById('end-session-btn').onclick = async () => {
                let resp = await apiRequest(`/sessions/${session.id}/end_session/`, 'POST');
                if (resp.ok) {
                    window.location.reload();
                } else {
                    alert('Failed to end session');
                }
            };
        }
        renderLoggedExercises(session.logged_exercises);
        renderAddExercise();
    }

    async function renderLoggedExercises(loggedExercises) {
        let html = '';
        for (let le of loggedExercises) {
            html += `<div class="exercise-block"><b>${le.exercise.name} (${le.exercise.muscle_group})</b>
                <button onclick="deleteLoggedExercise(${le.id})">Remove</button>
                <div>Sets:</div>
                <table class="sets-table"><tr><th>#</th><th>Reps</th><th>Weight</th><th>Actions</th></tr>`;
            for (let s of le.sets) {
                html += `<tr><td>${s.set_number}</td><td>${s.reps}</td><td>${s.weight}</td>
                    <td><button onclick="editSet(${s.id}, ${le.id})">Edit</button> <button onclick="deleteSet(${s.id}, ${le.id})">Delete</button></td></tr>`;
            }
            html += `</table>
                <form onsubmit="return addSet(event, ${le.id})">
                    <input type="number" name="reps" placeholder="Reps" min="1" required />
                    <input type="number" name="weight" placeholder="Weight" min="0" step="0.01" required />
                    <button type="submit">Add Set</button>
                </form>
            </div>`;
        }
        document.getElementById('logged-exercises').innerHTML = html;
    }

    window.addSet = async function(event, loggedExerciseId) {
        event.preventDefault();
        const form = event.target;
        const reps = form.reps.value;
        const weight = form.weight.value;
        let resp = await apiRequest(`/logged-exercises/${loggedExerciseId}/sets/`, 'POST', { reps, weight });
        if (resp.ok) {
            window.location.reload();
        } else {
            alert('Failed to add set');
        }
    };

    window.deleteSet = async function(setId, loggedExerciseId) {
        if (!confirm('Delete this set?')) return;
        let resp = await apiRequest(`/sets/${setId}/`, 'DELETE');
        if (resp.ok) {
            window.location.reload();
        } else {
            alert('Failed to delete set');
        }
    };

    window.editSet = async function(setId, loggedExerciseId) {
        const reps = prompt('New reps:');
        const weight = prompt('New weight:');
        if (!reps || !weight) return;
        let resp = await apiRequest(`/sets/${setId}/`, 'PATCH', { reps, weight });
        if (resp.ok) {
            window.location.reload();
        } else {
            alert('Failed to update set');
        }
    };

    window.deleteLoggedExercise = async function(loggedExerciseId) {
        if (!confirm('Remove this exercise and all its sets?')) return;
        let resp = await apiRequest(`/logged-exercises/${loggedExerciseId}/`, 'DELETE');
        if (resp.ok) {
            window.location.reload();
        } else {
            alert('Failed to remove exercise');
        }
    };

    async function renderAddExercise() {
        let resp = await apiRequest('/exercises/');
        if (!resp.ok) {
            document.getElementById('add-exercise').innerText = 'Failed to load exercises.';
            return;
        }
        let exercises = await resp.json();
        let html = `<form id="add-exercise-form">
            <select name="exercise_id" required>
                <option value="">Select exercise</option>`;
        for (let ex of exercises) {
            html += `<option value="${ex.id}">${ex.name} (${ex.muscle_group})</option>`;
        }
        html += `</select>
            <button type="submit">Add Exercise</button>
        </form>`;
        document.getElementById('add-exercise').innerHTML = html;
        document.getElementById('add-exercise-form').onsubmit = async (e) => {
            e.preventDefault();
            const exercise_id = e.target.exercise_id.value;
            let resp = await apiRequest(`/sessions/${sessionId}/logged-exercises/`, 'POST', { exercise_id });
            if (resp.ok) {
                window.location.reload();
            } else {
                alert('Failed to add exercise');
            }
        };
    }
}); 