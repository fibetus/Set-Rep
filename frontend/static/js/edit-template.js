document.addEventListener('DOMContentLoaded', async () => {
    // DOM Elements
    const form = document.getElementById('edit-template-form');
    const nameInput = document.getElementById('template-name');
    const descriptionInput = document.getElementById('template-description');
    const muscleGroupsContainer = document.getElementById('muscle-groups');
    const exercisesGrid = document.getElementById('exercises-grid');

    // State
    const urlParams = new URLSearchParams(window.location.search);
    const templateId = urlParams.get('id');
    let allExercises = [];
    let selectedExerciseIds = new Set();

    if (!templateId) {
        alert('No template ID provided!');
        window.location.href = '/plan.html';
        return;
    }

    // API Helper
    const apiRequest = async (endpoint, method = 'GET', body = null) => {
        const config = {
            method,
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        };
        if (body) config.body = JSON.stringify(body);
        const response = await fetch(`/api/v1${endpoint}`, config);
        if (response.status === 401) window.location.href = '/login.html';
        return response;
    };

    // Render Functions
    const renderMuscleGroups = (muscleGroups) => {
        muscleGroupsContainer.innerHTML = '<button class="muscle-group-btn active" data-group-id="null">All</button>' +
            muscleGroups.map(mg => `<button class="muscle-group-btn" data-group-id="${mg.id}">${mg.name}</button>`).join('');
        
        muscleGroupsContainer.addEventListener('click', (event) => {
            if (event.target.matches('.muscle-group-btn')) {
                const muscleGroupId = event.target.dataset.groupId === 'null' ? null : parseInt(event.target.dataset.groupId, 10);
                filterExercisesByGroup(muscleGroupId, event.target);
            }
        });
    };

    const renderExercises = (exercisesToRender) => {
        exercisesGrid.innerHTML = exercisesToRender.map(ex => `
            <div class="exercise-card ${selectedExerciseIds.has(ex.id) ? 'selected' : ''}" data-exercise-id="${ex.id}">
                <h3>${ex.name}</h3>
                <p>${ex.muscle_groups.map(mg => mg.name).join(', ')}</p>
            </div>
        `).join('');
        
        exercisesGrid.addEventListener('click', (event) => {
            const card = event.target.closest('.exercise-card');
            if (card) {
                const exerciseId = parseInt(card.dataset.exerciseId, 10);
                toggleExerciseSelection(exerciseId, card);
            }
        });
    };

    // Event Handlers
    const filterExercisesByGroup = (muscleGroupId, activeBtn) => {
        document.querySelectorAll('#muscle-groups .muscle-group-btn').forEach(btn => btn.classList.remove('active'));
        activeBtn.classList.add('active');
        const filtered = muscleGroupId ? allExercises.filter(ex => ex.muscle_groups.some(mg => mg.id === muscleGroupId)) : allExercises;
        renderExercises(filtered);
    };

    const toggleExerciseSelection = (exerciseId, card) => {
        if (selectedExerciseIds.has(exerciseId)) {
            selectedExerciseIds.delete(exerciseId);
            card.classList.remove('selected');
        } else {
            selectedExerciseIds.add(exerciseId);
            card.classList.add('selected');
        }
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            name: nameInput.value,
            description: descriptionInput.value,
            exercises: Array.from(selectedExerciseIds).map(id => ({ exercise_id: id }))
        };
        const response = await apiRequest(`/templates/${templateId}/`, 'PUT', payload);
        if (response.ok) {
            alert('Template updated successfully!');
            window.location.href = '/plan.html';
        } else {
            alert('Failed to update template.');
        }
    });

    // Initial Load
    try {
        const [templateRes, exercisesRes, muscleGroupsRes] = await Promise.all([
            apiRequest(`/templates/${templateId}/`),
            apiRequest('/exercises/'),
            apiRequest('/muscle-groups/')
        ]);

        if (!templateRes.ok || !exercisesRes.ok || !muscleGroupsRes.ok) throw new Error('Failed to load initial data.');

        const template = await templateRes.json();
        allExercises = await exercisesRes.json();
        const muscleGroups = await muscleGroupsRes.json();

        nameInput.value = template.name;
        descriptionInput.value = template.description;
        template.exercises.forEach(ex => selectedExerciseIds.add(ex.exercise.id));
        
        renderMuscleGroups(muscleGroups);
        renderExercises(allExercises);

    } catch (error) {
        console.error(error);
        alert('Error loading page.');
    }
}); 