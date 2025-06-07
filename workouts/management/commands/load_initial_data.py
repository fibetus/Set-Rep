from django.core.management.base import BaseCommand
from workouts.models import MuscleGroup, Exercise

class Command(BaseCommand):
    help = 'Load initial exercise data'

    def handle(self, *args, **options):
        # Create muscle groups
        muscle_groups = {
            'Chest': 'Pectoralis major and minor muscles',
            'Back': 'Latissimus dorsi, trapezius, and rhomboids',
            'Shoulders': 'Deltoids and rotator cuff muscles',
            'Biceps': 'Biceps brachii and brachialis',
            'Triceps': 'Triceps brachii',
            'Legs': 'Quadriceps, hamstrings, and calves',
            'Abs': 'Rectus abdominis and obliques',
        }

        for name, description in muscle_groups.items():
            MuscleGroup.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )

        # Create example exercises
        exercises = [
            {
                'name': 'Bench Press',
                'description': 'A compound exercise that primarily targets the chest muscles',
                'muscle_groups': ['Chest', 'Shoulders', 'Triceps'],
                'instructions': '1. Lie on a flat bench\n2. Grip the bar slightly wider than shoulder-width\n3. Lower the bar to your chest\n4. Push the bar back up to starting position',
                'equipment_needed': 'Barbell, Bench'
            },
            {
                'name': 'Pull-ups',
                'description': 'A compound exercise that primarily targets the back muscles',
                'muscle_groups': ['Back', 'Biceps'],
                'instructions': '1. Hang from a pull-up bar with hands slightly wider than shoulder-width\n2. Pull your body up until your chin is over the bar\n3. Lower yourself back down with control',
                'equipment_needed': 'Pull-up Bar'
            },
            {
                'name': 'Squats',
                'description': 'A compound exercise that primarily targets the leg muscles',
                'muscle_groups': ['Legs'],
                'instructions': '1. Stand with feet shoulder-width apart\n2. Lower your body by bending your knees\n3. Keep your back straight and chest up\n4. Return to starting position',
                'equipment_needed': 'None (bodyweight) or Barbell'
            }
        ]

        for exercise_data in exercises:
            muscle_groups = exercise_data.pop('muscle_groups')
            exercise, created = Exercise.objects.get_or_create(
                name=exercise_data['name'],
                defaults=exercise_data
            )
            if created:
                for muscle_group in muscle_groups:
                    exercise.muscle_groups.add(MuscleGroup.objects.get(name=muscle_group))
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created exercise "{exercise.name}"')
                ) 