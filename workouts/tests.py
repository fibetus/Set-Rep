from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import (
    Exercise, WorkoutSession, LoggedExercise,
    Set, TrainingPlan, TrainingPlanExercise
)

class ExerciseModelTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(
            name="Bench Press",
            muscle_group="Chest"
        )

    def test_exercise_creation(self):
        self.assertEqual(self.exercise.name, "Bench Press")
        self.assertEqual(self.exercise.muscle_group, "Chest")
        self.assertEqual(str(self.exercise), "Bench Press (Chest)")

class WorkoutSessionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.session = WorkoutSession.objects.create(
            client=self.user,
            notes="Test workout"
        )

    def test_session_creation(self):
        self.assertEqual(self.session.client, self.user)
        self.assertEqual(self.session.notes, "Test workout")
        self.assertIsNone(self.session.end_time)

class WorkoutSessionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.exercise = Exercise.objects.create(
            name="Bench Press",
            muscle_group="Chest"
        )

    def test_create_session(self):
        url = '/api/v1/sessions/'
        data = {'notes': 'Test workout'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutSession.objects.count(), 1)
        self.assertEqual(WorkoutSession.objects.get().notes, 'Test workout')

    def test_end_session(self):
        session = WorkoutSession.objects.create(client=self.user)
        url = f'/api/v1/sessions/{session.id}/end_session/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session.refresh_from_db()
        self.assertIsNotNone(session.end_time)

class TrainingPlanAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.exercise = Exercise.objects.create(
            name="Bench Press",
            muscle_group="Chest"
        )

    def test_create_plan(self):
        url = '/api/v1/plans/'
        data = {
            'name': 'Test Plan',
            'description': 'Test description',
            'exercises': [self.exercise.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TrainingPlan.objects.count(), 1)
        plan = TrainingPlan.objects.get()
        self.assertEqual(plan.name, 'Test Plan')
        self.assertEqual(plan.exercises.count(), 1) 