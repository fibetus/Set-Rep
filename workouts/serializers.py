from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Exercise, WorkoutSession, LoggedExercise,
    Set, TrainingPlan, TrainingPlanExercise
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('id', 'name', 'muscle_group')
        read_only_fields = ('id',)

class SetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Set
        fields = ('id', 'set_number', 'reps', 'weight')
        read_only_fields = ('id',)

class LoggedExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        write_only=True,
        source='exercise'
    )
    sets = SetSerializer(many=True, read_only=True)

    class Meta:
        model = LoggedExercise
        fields = ('id', 'exercise', 'exercise_id', 'order', 'sets')
        read_only_fields = ('id',)

class WorkoutSessionSerializer(serializers.ModelSerializer):
    logged_exercises = LoggedExerciseSerializer(many=True, read_only=True)
    client = UserSerializer(read_only=True)

    class Meta:
        model = WorkoutSession
        fields = ('id', 'client', 'start_time', 'end_time', 'notes', 'logged_exercises')
        read_only_fields = ('id', 'client', 'start_time')

class TrainingPlanExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        write_only=True,
        source='exercise'
    )

    class Meta:
        model = TrainingPlanExercise
        fields = ('id', 'exercise', 'exercise_id', 'order')
        read_only_fields = ('id',)

class TrainingPlanSerializer(serializers.ModelSerializer):
    exercises = TrainingPlanExerciseSerializer(
        source='trainingplanexercise_set',
        many=True,
        read_only=True
    )
    client = UserSerializer(read_only=True)

    class Meta:
        model = TrainingPlan
        fields = ('id', 'client', 'name', 'description', 'exercises')
        read_only_fields = ('id', 'client')

    def create(self, validated_data):
        exercises = validated_data.pop('exercises', None)
        if exercises is None:
            exercises = self.context.get('exercises', [])
        plan = TrainingPlan.objects.create(**validated_data)
        for order, exercise_id in enumerate(exercises, start=1):
            TrainingPlanExercise.objects.create(
                plan=plan,
                exercise_id=exercise_id,
                order=order
            )
        return plan

    def update(self, instance, validated_data):
        exercises_data = self.context.get('exercises', None)
        
        # Update basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Update exercises if provided
        if exercises_data is not None:
            # Remove existing exercises
            instance.trainingplanexercise_set.all().delete()
            
            # Add new exercises
            for order, exercise_id in enumerate(exercises_data, start=1):
                TrainingPlanExercise.objects.create(
                    plan=instance,
                    exercise_id=exercise_id,
                    order=order
                )

        return instance 