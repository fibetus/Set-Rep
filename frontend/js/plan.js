document.addEventListener('DOMContentLoaded', async () => {
    const planControls = document.getElementById('plan-controls');
    const plansList = document.getElementById('plans-list');
    const planDetail = document.getElementById('plan-detail');

    // Load all plans
    async function loadPlans() {
        let resp = await apiRequest('/plans/');
        if (!resp.ok) {
            plansList.innerText = 'Failed to load plans.';
            return;
        }
        let plans = await resp.json();
        let html = '<ul>';
        for (let plan of plans) {
            html += `<li><a href="#" onclick="showPlan(${plan.id});return false;">${plan.name}</a></li>`;
        }
        html += '</ul>';
        plansList.innerHTML = html;
    }

    window.showPlan = async function(planId) {
        let resp = await apiRequest(`/plans/${planId}/`);
        if (!resp.ok) {
            planDetail.innerText = 'Failed to load plan.';
            return;
        }
        let plan = await resp.json();
        let html = `<h3>${plan.name}</h3><div>${plan.description || ''}</div>`;
        html += '<h4>Exercises</h4><ul>';
        for (let ex of plan.exercises) {
            html += `<li>${ex.exercise.name} (${ex.exercise.muscle_group})</li>`;
        }
        html += '</ul>';
        html += `<button onclick="deletePlan(${plan.id})">Delete Plan</button>`;
        html += `<button onclick="editPlan(${plan.id})">Edit Plan</button>`;
        html += `<button onclick="startWorkoutFromPlan(${plan.id})">Start Workout from Plan</button>`;
        planDetail.innerHTML = html;
    };

    window.deletePlan = async function(planId) {
        if (!confirm('Delete this plan?')) return;
        let resp = await apiRequest(`/plans/${planId}/`, 'DELETE');
        if (resp.ok) {
            planDetail.innerHTML = '';
            loadPlans();
        } else {
            alert('Failed to delete plan');
        }
    };

    window.editPlan = async function(planId) {
        let resp = await apiRequest(`/plans/${planId}/`);
        if (!resp.ok) {
            planDetail.innerText = 'Failed to load plan.';
            return;
        }
        let plan = await resp.json();
        let exercisesResp = await apiRequest('/exercises/');
        let exercises = exercisesResp.ok ? await exercisesResp.json() : [];
        let html = `<h3>Edit Plan: ${plan.name}</h3>
            <form id="edit-plan-form">
                <label>Name</label><input name="name" value="${plan.name}" required />
                <label>Description</label><textarea name="description">${plan.description || ''}</textarea>
                <label>Exercises</label><select name="exercises" multiple required style="height:120px;">`;
        for (let ex of exercises) {
            let selected = plan.exercises.some(e => e.exercise.id === ex.id) ? 'selected' : '';
            html += `<option value="${ex.id}" ${selected}>${ex.name} (${ex.muscle_group})</option>`;
        }
        html += `</select><button type="submit">Save</button></form>`;
        planDetail.innerHTML = html;
        document.getElementById('edit-plan-form').onsubmit = async (e) => {
            e.preventDefault();
            const name = e.target.name.value;
            const description = e.target.description.value;
            const exercises = Array.from(e.target.exercises.selectedOptions).map(o => o.value);
            let resp = await apiRequest(`/plans/${planId}/`, 'PATCH', { name, description, exercises });
            if (resp.ok) {
                showPlan(planId);
                loadPlans();
            } else {
                alert('Failed to update plan');
            }
        };
    };

    window.startWorkoutFromPlan = async function(planId) {
        // Create a new session and pre-populate with plan exercises
        let sessionResp = await apiRequest('/sessions/', 'POST', { notes: `Started from plan ${planId}` });
        if (!sessionResp.ok) {
            alert('Failed to start session');
            return;
        }
        let session = await sessionResp.json();
        let planResp = await apiRequest(`/plans/${planId}/`);
        let plan = planResp.ok ? await planResp.json() : null;
        if (plan) {
            for (let ex of plan.exercises) {
                await apiRequest(`/sessions/${session.id}/logged-exercises/`, 'POST', { exercise_id: ex.exercise.id });
            }
        }
        window.location = `workout.html?id=${session.id}`;
    };

    planControls.innerHTML = `<button id="create-plan-btn">Create New Plan</button>`;
    document.getElementById('create-plan-btn').onclick = async () => {
        let exercisesResp = await apiRequest('/exercises/');
        let exercises = exercisesResp.ok ? await exercisesResp.json() : [];
        let html = `<h3>Create New Plan</h3>
            <form id="create-plan-form">
                <label>Name</label><input name="name" required />
                <label>Description</label><textarea name="description"></textarea>
                <label>Exercises</label><select name="exercises" multiple required style="height:120px;">`;
        for (let ex of exercises) {
            html += `<option value="${ex.id}">${ex.name} (${ex.muscle_group})</option>`;
        }
        html += `</select><button type="submit">Create</button></form>`;
        planDetail.innerHTML = html;
        document.getElementById('create-plan-form').onsubmit = async (e) => {
            e.preventDefault();
            const name = e.target.name.value;
            const description = e.target.description.value;
            const exercises = Array.from(e.target.exercises.selectedOptions).map(o => o.value);
            let resp = await apiRequest('/plans/', 'POST', { name, description, exercises });
            if (resp.ok) {
                planDetail.innerHTML = '';
                loadPlans();
            } else {
                alert('Failed to create plan');
            }
        };
    };

    loadPlans();
}); 