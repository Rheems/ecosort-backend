from django.core.management.base import BaseCommand
from django.utils import timezone
from education.models import UserEducationProgress
import pytz


class Command(BaseCommand):
    help = 'Reset daily streaks for inactive users at 23:55 WAT'

    def handle(self, *args, **kwargs):
        # WAT is UTC+1
        wat = pytz.timezone('Africa/Lagos')
        today = timezone.now().astimezone(wat).date()

        # Reset streaks for users who were not active today
        reset_count = UserEducationProgress.objects.filter(
            last_activity_date__lt=today
        ).update(daily_streak=0)

        self.stdout.write(
            self.style.SUCCESS(f'✅ Reset {reset_count} streaks successfully!')
        )