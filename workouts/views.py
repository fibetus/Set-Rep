from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import (
    Exercise, WorkoutSession, LoggedExercise,
    Set, TrainingPlan, TrainingPlanExercise,
    MuscleGroup, WorkoutTemplate, TemplateExercise,
    Workout, WorkoutExercise
)
from .serializers import (
    ExerciseSerializer, WorkoutSessionSerializer,
    LoggedExerciseSerializer, SetSerializer,
    TrainingPlanSerializer, MuscleGroupSerializer,
    WorkoutTemplateSerializer, WorkoutSerializer
)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Please provide both email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        
        return Response(
            {'message': 'User created successfully'},
            status=status.HTTP_201_CREATED
        )

class MuscleGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MuscleGroup.objects.all()
    serializer_class = MuscleGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Exercise.objects.all()
        muscle_group = self.request.query_params.get('muscle_group')
        if muscle_group:
            queryset = queryset.filter(muscle_groups__id=muscle_group)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class WorkoutSessionViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutSession.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        session = self.get_object()
        if session.end_time:
            return Response(
                {'error': 'Session already ended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        session.end_time = timezone.now()
        session.save()
        return Response(self.get_serializer(session).data)

    @action(detail=True, methods=['post'])
    def add_exercise(self, request, pk=None):
        session = self.get_object()
        serializer = LoggedExerciseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoggedExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = LoggedExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LoggedExercise.objects.filter(session__client=self.request.user)

    @action(detail=True, methods=['post'])
    def add_set(self, request, pk=None):
        logged_exercise = self.get_object()
        serializer = SetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(logged_exercise=logged_exercise)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetViewSet(viewsets.ModelViewSet):
    serializer_class = SetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Set.objects.filter(logged_exercise__session__client=self.request.user)

class TrainingPlanViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrainingPlan.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        exercises = self.request.data.get('exercises', [])
        serializer.save(
            client=self.request.user,
            exercises=exercises
        )

    def perform_update(self, serializer):
        exercises = self.request.data.get('exercises')
        serializer.save(exercises=exercises)

    @action(detail=True, methods=['post'])
    def create_from_session(self, request, pk=None):
        session = WorkoutSession.objects.get(pk=pk)
        if session.client != request.user:
            return Response(
                {'error': 'Not authorized to access this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create new plan
        plan_data = {
            'name': f"Plan from Session {session.id}",
            'description': f"Created from workout session on {session.start_time}",
            'client': request.user
        }
        plan = TrainingPlan.objects.create(**plan_data)

        # Copy exercises from session
        for order, logged_exercise in enumerate(session.logged_exercises.all(), start=1):
            TrainingPlanExercise.objects.create(
                plan=plan,
                exercise=logged_exercise.exercise,
                order=order
            )

        return Response(
            self.get_serializer(plan).data,
            status=status.HTTP_201_CREATED
        )

class WorkoutTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutTemplate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        template = serializer.save(user=self.request.user)
        
        # Create template exercises
        exercises_data = self.request.data.get('exercises', [])
        for i, exercise_data in enumerate(exercises_data):
            TemplateExercise.objects.create(
                template=template,
                exercise_id=exercise_data['exercise_id'],
                sets=exercise_data.get('sets', 3),
                reps=exercise_data.get('reps', 10),
                order=i
            )

    def update(self, request, *args, **kwargs):
        template = self.get_object()
        serializer = self.get_serializer(template, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_template = serializer.save()

        exercises_data = request.data.get('exercises')
        if exercises_data is not None:
            updated_template.templateexercise_set.all().delete()
            for i, exercise_data in enumerate(exercises_data):
                TemplateExercise.objects.create(
                    template=updated_template,
                    exercise_id=exercise_data['exercise_id'],
                    sets=exercise_data.get('sets', 3),
                    reps=exercise_data.get('reps', 10),
                    order=i
                )
        
        return Response(self.get_serializer(updated_template).data)

class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        workout = serializer.save(user=self.request.user)
        # Create workout exercises and sets
        exercises_data = self.request.data.get('exercises', [])
        for i, exercise_data in enumerate(exercises_data):
            workout_exercise = WorkoutExercise.objects.create(
                workout=workout,
                exercise_id=exercise_data['exercise_id'],
                order=i
            )
            for j, set_data in enumerate(exercise_data.get('sets', []), start=1):
                Set.objects.create(
                    workout_exercise=workout_exercise,
                    set_number=j,
                    reps=set_data['reps'],
                    weight=set_data['weight']
                )
        # Return the serialized workout
        return Response(self.get_serializer(workout).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        workout = self.get_object()
        serializer = self.get_serializer(workout, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_workout = serializer.save()

        # Clear existing exercises and sets
        updated_workout.workoutexercise_set.all().delete()

        # Create new exercises and sets from payload
        exercises_data = request.data.get('exercises', [])
        for i, exercise_data in enumerate(exercises_data):
            workout_exercise = WorkoutExercise.objects.create(
                workout=updated_workout,
                exercise_id=exercise_data['exercise_id'],
                order=i
            )
            for j, set_data in enumerate(exercise_data.get('sets', []), start=1):
                Set.objects.create(
                    workout_exercise=workout_exercise,
                    set_number=j,
                    reps=set_data['reps'],
                    weight=set_data['weight']
                )
        
        return Response(self.get_serializer(updated_workout).data)

    @action(detail=False, methods=['post'])
    def from_template(self, request):
        template_id = request.data.get('template_id')
        template = get_object_or_404(WorkoutTemplate, id=template_id, user=request.user)
        workout = Workout.objects.create(
            user=request.user,
            template=template
        )
        # Copy exercises from template
        for template_exercise in template.templateexercise_set.all():
            workout_exercise = WorkoutExercise.objects.create(
                workout=workout,
                exercise=template_exercise.exercise,
                order=template_exercise.order
            )
            # Create sets for this exercise
            for set_num in range(1, template_exercise.sets + 1):
                Set.objects.create(
                    workout_exercise=workout_exercise,
                    set_number=set_num,
                    reps=template_exercise.reps,
                    weight=0  # Default weight, can be edited later
                )
        # Set workout name in the standardized format
        same_day_workouts = Workout.objects.filter(user=workout.user, date__date=workout.date.date()).count()
        workout.name = f"Workout #{same_day_workouts} - {workout.date.strftime('%Y-%m-%d %H:%M')}"
        workout.save(update_fields=["name"])
        serializer = self.get_serializer(workout)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.data, status=status.HTTP_201_CREATED) 