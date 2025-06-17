from django.core.management.base import BaseCommand
from workouts.models import Workout

class Command(BaseCommand):
    help = 'Fixes the names of existing workouts to a standardized format.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to fix workout names...')
        workouts = Workout.objects.all()
        fixed_count = 0
        for workout in workouts:
            # Standardized format: Workout #{id} - YYYY-MM-DD HH:MM
            new_name = f"Workout #{workout.id} - {workout.date.strftime('%Y-%m-%d %H:%M')}"
            if workout.name != new_name:
                workout.name = new_name
                workout.save(update_fields=['name'])
                fixed_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} workout names.')) 