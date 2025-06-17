from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from workouts.models import (
    Exercise, WorkoutSession, LoggedExercise,
    Set, TrainingPlan, TrainingPlanExercise,
    Workout, WorkoutExercise, MuscleGroup
)

class ExerciseModelTest(TestCase):
    def setUp(self):
        self.muscle_group = MuscleGroup.objects.create(name="Chest")
        self.exercise = Exercise.objects.create(
            name="Bench Press"
        )
        self.exercise.muscle_groups.add(self.muscle_group)

    def test_exercise_creation(self):
        self.assertEqual(self.exercise.name, "Bench Press")
        self.assertEqual(str(self.exercise), "Bench Press")

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
        self.muscle_group = MuscleGroup.objects.create(name="Chest")
        self.exercise = Exercise.objects.create(
            name="Bench Press"
        )
        self.exercise.muscle_groups.add(self.muscle_group)

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
        self.muscle_group = MuscleGroup.objects.create(name="Chest")
        self.exercise = Exercise.objects.create(
            name="Bench Press"
        )
        self.exercise.muscle_groups.add(self.muscle_group)

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

class WorkoutModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.muscle_group = MuscleGroup.objects.create(name="Chest")
        self.exercise = Exercise.objects.create(
            name="Bench Press",
            description="A chest exercise"
        )
        self.exercise.muscle_groups.add(self.muscle_group)
        self.workout = Workout.objects.create(user=self.user)

    def test_workout_creation(self):
        self.assertEqual(self.workout.user, self.user)
        self.assertTrue(self.workout.name.startswith("Workout #1"))
        self.assertIn(self.workout.date.strftime('%Y-%m-%d'), self.workout.name)

    def test_multiple_workouts_same_day(self):
        workout2 = Workout.objects.create(user=self.user)
        self.assertTrue(workout2.name.startswith("Workout #2"))

class WorkoutExerciseAndSetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.muscle_group = MuscleGroup.objects.create(name="Chest")
        self.exercise = Exercise.objects.create(
            name="Bench Press",
            description="A chest exercise"
        )
        self.exercise.muscle_groups.add(self.muscle_group)
        self.workout = Workout.objects.create(user=self.user)
        self.workout_exercise = WorkoutExercise.objects.create(
            workout=self.workout,
            exercise=self.exercise,
            order=1
        )

    def test_workout_exercise_creation(self):
        self.assertEqual(self.workout_exercise.workout, self.workout)
        self.assertEqual(self.workout_exercise.exercise, self.exercise)
        self.assertEqual(self.workout_exercise.order, 1)

    def test_set_creation(self):
        set1 = Set.objects.create(
            workout_exercise=self.workout_exercise,
            set_number=1,
            reps=10,
            weight=100.0
        )
        set2 = Set.objects.create(
            workout_exercise=self.workout_exercise,
            set_number=2,
            reps=8,
            weight=95.0
        )

        self.assertEqual(set1.reps, 10)
        self.assertEqual(set1.weight, 100.0)
        self.assertEqual(set2.reps, 8)
        self.assertEqual(set2.weight, 95.0)
        self.assertEqual(self.workout_exercise.sets.count(), 2)

class WorkoutAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.muscle_group = MuscleGroup.objects.create(name="Chest")
        self.exercise = Exercise.objects.create(
            name="Bench Press",
            description="A chest exercise"
        )
        self.exercise.muscle_groups.add(self.muscle_group)

    def test_create_workout_with_exercise_and_sets(self):
        url = '/api/v1/workouts/'
        data = {
            'exercises': [
                {
                    'exercise_id': self.exercise.id,
                    'sets': [
                        {'reps': 10, 'weight': 100.0},
                        {'reps': 8, 'weight': 95.0}
                    ]
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        workout = Workout.objects.get()
        workout_exercise = workout.workoutexercise_set.get()
        self.assertEqual(workout_exercise.sets.count(), 2)
        
        set1 = workout_exercise.sets.get(set_number=1)
        set2 = workout_exercise.sets.get(set_number=2)
        self.assertEqual(set1.reps, 10)
        self.assertEqual(set1.weight, 100.0)
        self.assertEqual(set2.reps, 8)
        self.assertEqual(set2.weight, 95.0) 