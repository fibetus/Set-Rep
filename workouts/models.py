from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Exercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    muscle_groups = models.ManyToManyField(MuscleGroup)
    instructions = models.TextField(blank=True)
    equipment_needed = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class WorkoutTemplate(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercises = models.ManyToManyField(Exercise, through='TemplateExercise')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class TemplateExercise(models.Model):
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=10)
    rest_time = models.IntegerField(default=60)  # in seconds
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, default="")
    notes = models.TextField(blank=True)
    exercises = models.ManyToManyField(Exercise, through='WorkoutExercise')

    def __str__(self):
        if self.name:
            return f"{self.name} - {self.date.strftime('%Y-%m-%d %H:%M')}"
        return f"Workout on {self.date.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new object
            super().save(*args, **kwargs)  # Save to get an ID
            
            # Determine the daily count
            same_day_workouts = Workout.objects.filter(
                user=self.user,
                date__date=self.date.date()
            ).count()

            self.name = f"Workout #{same_day_workouts} - {self.date.strftime('%Y-%m-%d %H:%M')}"
            
            # We only want to save the name field, not trigger a full save again
            super().save(update_fields=['name'])
        else:
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date']

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    rest_time = models.IntegerField(default=60)  # in seconds
    order = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.name} in {self.workout}"

class WorkoutSession(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Workout Session {self.id} - {self.client.username}"

class LoggedExercise(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='logged_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['session', 'exercise']

    def __str__(self):
        return f"{self.exercise.name} in Session {self.session.id}"

class Set(models.Model):
    logged_exercise = models.ForeignKey(LoggedExercise, on_delete=models.CASCADE, related_name='sets', null=True, blank=True)
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE, related_name='sets', null=True, blank=True)
    set_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    weight = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['set_number']
        unique_together = [
            ('logged_exercise', 'set_number'),
            ('workout_exercise', 'set_number')
        ]

    def __str__(self):
        if self.workout_exercise:
            return f"Set {self.set_number} of {self.workout_exercise.exercise.name}"
        return f"Set {self.set_number} of {self.logged_exercise.exercise.name}"

class TrainingPlan(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_plans')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    exercises = models.ManyToManyField(Exercise, through='TrainingPlanExercise')

    def __str__(self):
        return f"{self.name} - {self.client.username}"

class TrainingPlanExercise(models.Model):
    plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['plan', 'exercise']

    def __str__(self):
        return f"{self.exercise.name} in Plan {self.plan.name}" 