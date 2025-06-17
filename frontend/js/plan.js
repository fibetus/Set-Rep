document.addEventListener('DOMContentLoaded', async () => {
    const planControls = document.getElementById('plan-controls');
    const plansList = document.getElementById('plans-list');
    const planDetail = document.getElementById('plan-detail');

    // Load all plans
    async function loadPlans() {
        try {
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
        } catch (error) {
            console.error('Error loading plans:', error);
            plansList.innerText = 'Error loading plans.';
        }
    }

    window.showPlan = async function(planId) {
        try {
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
            html += `<button onclick="useTemplate(${plan.id})">Use as Workout</button>`;
            planDetail.innerHTML = html;
        } catch (error) {
            console.error('Error showing plan:', error);
            planDetail.innerText = 'Error displaying plan.';
        }
    };

    window.deletePlan = async function(planId) {
        if (!confirm('Delete this plan?')) return;
        let resp = await apiRequest(`/templates/${planId}/`, 'DELETE');
        if (resp.ok) {
            planDetail.innerHTML = '';
            loadPlans();
        } else {
            alert('Failed to delete plan');
        }
    };

    window.editPlan = function(planId) {
        window.location.href = `edit-template.html?id=${planId}`;
    };

    window.acceptTemplateChanges = function() {
        window.location.href = 'index.html';
    };
    window.cancelTemplateChanges = function() {
        window.location.href = 'index.html';
    };

    window.useTemplate = async function(templateId) {
        if (!confirm('Start a new workout using this template?')) return;

        try {
            const response = await apiRequest('workouts/from_template/', 'POST', { template_id: templateId });
            
            if (response.ok) {
                const newWorkout = await response.json();
                window.location.href = `edit-workout.html?id=${newWorkout.id}`;
            } else {
                const error = await response.json();
                alert(`Failed to create workout: ${error.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error creating workout from template:', error);
            alert('An error occurred while creating the workout.');
        }
    };

    planControls.innerHTML = `<button id="create-plan-btn">Create New Template</button>`;
    document.getElementById('create-plan-btn').onclick = async () => {
        let exercisesResp = await apiRequest('/exercises/');
        let exercises = exercisesResp.ok ? await exercisesResp.json() : [];
        let html = `<h3>Create New Template</h3>
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
            let resp = await apiRequest('/templates/', 'POST', { name, description, exercises: exercises.map(id => ({ exercise_id: id })) });
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