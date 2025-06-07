from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    Exercise, WorkoutSession, LoggedExercise,
    Set, TrainingPlan, TrainingPlanExercise
)
from .serializers import (
    ExerciseSerializer, WorkoutSessionSerializer,
    LoggedExerciseSerializer, SetSerializer,
    TrainingPlanSerializer
)

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['muscle_group']

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