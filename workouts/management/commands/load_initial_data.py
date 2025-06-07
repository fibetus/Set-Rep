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

        # Create muscle groups
        muscle_group_objects = {}
        for name, description in muscle_groups.items():
            group, created = MuscleGroup.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            muscle_group_objects[name] = group
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created muscle group "{name}"')
                )

        # Create exercises with their muscle groups
        exercises = [
            # Chest exercises
            {
                'name': 'Bench Press',
                'description': 'A compound exercise that primarily targets the chest muscles',
                'muscle_groups': ['Chest', 'Shoulders', 'Triceps'],
                'instructions': '1. Lie on a flat bench\n2. Grip the bar slightly wider than shoulder-width\n3. Lower the bar to your chest\n4. Push the bar back up to starting position',
                'equipment_needed': 'Barbell, Bench'
            },
            {
                'name': 'Incline Dumbbell Press',
                'description': 'Targets the upper chest muscles',
                'muscle_groups': ['Chest', 'Shoulders', 'Triceps'],
                'instructions': '1. Set bench to 30-45 degree angle\n2. Hold dumbbells at chest level\n3. Press up and together\n4. Lower back to starting position',
                'equipment_needed': 'Dumbbells, Incline Bench'
            },
            {
                'name': 'Cable Flyes',
                'description': 'Isolates the chest muscles with constant tension',
                'muscle_groups': ['Chest'],
                'instructions': '1. Stand between two cable machines\n2. Pull cables forward and together\n3. Return to starting position with control',
                'equipment_needed': 'Cable Machine'
            },

            # Back exercises
            {
                'name': 'Pull-ups',
                'description': 'A compound exercise that primarily targets the back muscles',
                'muscle_groups': ['Back', 'Biceps'],
                'instructions': '1. Hang from a pull-up bar with hands slightly wider than shoulder-width\n2. Pull your body up until your chin is over the bar\n3. Lower yourself back down with control',
                'equipment_needed': 'Pull-up Bar'
            },
            {
                'name': 'Bent Over Rows',
                'description': 'Targets the middle and upper back',
                'muscle_groups': ['Back', 'Biceps'],
                'instructions': '1. Bend at hips and knees\n2. Hold barbell with overhand grip\n3. Pull bar to lower chest\n4. Lower with control',
                'equipment_needed': 'Barbell'
            },
            {
                'name': 'Lat Pulldowns',
                'description': 'Isolates the latissimus dorsi',
                'muscle_groups': ['Back', 'Biceps'],
                'instructions': '1. Sit at lat pulldown machine\n2. Pull bar to upper chest\n3. Return to starting position',
                'equipment_needed': 'Lat Pulldown Machine'
            },

            # Shoulder exercises
            {
                'name': 'Overhead Press',
                'description': 'A compound exercise for shoulder development',
                'muscle_groups': ['Shoulders', 'Triceps'],
                'instructions': '1. Hold barbell at shoulder level\n2. Press overhead until arms are straight\n3. Lower back to shoulders',
                'equipment_needed': 'Barbell'
            },
            {
                'name': 'Lateral Raises',
                'description': 'Isolates the lateral deltoids',
                'muscle_groups': ['Shoulders'],
                'instructions': '1. Hold dumbbells at sides\n2. Raise arms out to sides until parallel to floor\n3. Lower with control',
                'equipment_needed': 'Dumbbells'
            },
            {
                'name': 'Face Pulls',
                'description': 'Targets rear deltoids and upper back',
                'muscle_groups': ['Shoulders', 'Back'],
                'instructions': '1. Use rope attachment on cable machine\n2. Pull rope towards face\n3. Separate hands at end of movement',
                'equipment_needed': 'Cable Machine'
            },

            # Biceps exercises
            {
                'name': 'Barbell Curls',
                'description': 'Classic biceps exercise',
                'muscle_groups': ['Biceps'],
                'instructions': '1. Hold barbell with underhand grip\n2. Curl bar up to shoulders\n3. Lower with control',
                'equipment_needed': 'Barbell'
            },
            {
                'name': 'Hammer Curls',
                'description': 'Targets biceps and forearms',
                'muscle_groups': ['Biceps'],
                'instructions': '1. Hold dumbbells with neutral grip\n2. Curl up while maintaining grip\n3. Lower with control',
                'equipment_needed': 'Dumbbells'
            },
            {
                'name': 'Preacher Curls',
                'description': 'Isolates the biceps',
                'muscle_groups': ['Biceps'],
                'instructions': '1. Sit at preacher bench\n2. Curl weight up\n3. Lower with control',
                'equipment_needed': 'Preacher Bench, EZ Bar or Dumbbells'
            },

            # Triceps exercises
            {
                'name': 'Tricep Pushdowns',
                'description': 'Isolates the triceps',
                'muscle_groups': ['Triceps'],
                'instructions': '1. Use rope or bar attachment\n2. Push down until arms are straight\n3. Return to starting position',
                'equipment_needed': 'Cable Machine'
            },
            {
                'name': 'Skull Crushers',
                'description': 'Targets the long head of triceps',
                'muscle_groups': ['Triceps'],
                'instructions': '1. Lie on bench\n2. Lower weight to forehead\n3. Extend arms back up',
                'equipment_needed': 'EZ Bar or Dumbbells, Bench'
            },
            {
                'name': 'Diamond Push-ups',
                'description': 'Bodyweight triceps exercise',
                'muscle_groups': ['Triceps', 'Chest'],
                'instructions': '1. Place hands close together\n2. Perform push-up\n3. Keep elbows close to body',
                'equipment_needed': 'None'
            },

            # Leg exercises
            {
                'name': 'Squats',
                'description': 'A compound exercise that primarily targets the leg muscles',
                'muscle_groups': ['Legs'],
                'instructions': '1. Stand with feet shoulder-width apart\n2. Lower your body by bending your knees\n3. Keep your back straight and chest up\n4. Return to starting position',
                'equipment_needed': 'None (bodyweight) or Barbell'
            },
            {
                'name': 'Leg Press',
                'description': 'Machine-based leg exercise',
                'muscle_groups': ['Legs'],
                'instructions': '1. Sit in leg press machine\n2. Place feet shoulder-width apart\n3. Push platform away\n4. Return with control',
                'equipment_needed': 'Leg Press Machine'
            },
            {
                'name': 'Romanian Deadlifts',
                'description': 'Targets hamstrings and glutes',
                'muscle_groups': ['Legs', 'Back'],
                'instructions': '1. Hold barbell with overhand grip\n2. Hinge at hips\n3. Lower bar along legs\n4. Return to standing',
                'equipment_needed': 'Barbell'
            },

            # Abs exercises
            {
                'name': 'Crunches',
                'description': 'Classic abdominal exercise',
                'muscle_groups': ['Abs'],
                'instructions': '1. Lie on back\n2. Place hands behind head\n3. Curl upper body towards knees\n4. Return with control',
                'equipment_needed': 'None'
            },
            {
                'name': 'Plank',
                'description': 'Core stability exercise',
                'muscle_groups': ['Abs'],
                'instructions': '1. Hold push-up position\n2. Keep body straight\n3. Hold for time',
                'equipment_needed': 'None'
            },
            {
                'name': 'Russian Twists',
                'description': 'Targets obliques and core',
                'muscle_groups': ['Abs'],
                'instructions': '1. Sit on floor\n2. Lean back slightly\n3. Rotate torso side to side',
                'equipment_needed': 'None (optional: medicine ball)'
            }
        ]

        # Create exercises
        for exercise_data in exercises:
            muscle_groups = exercise_data.pop('muscle_groups')
            exercise, created = Exercise.objects.get_or_create(
                name=exercise_data['name'],
                defaults=exercise_data
            )
            if created:
                for muscle_group in muscle_groups:
                    exercise.muscle_groups.add(muscle_group_objects[muscle_group])
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created exercise "{exercise.name}"')
                ) 