from django.core.management.base import BaseCommand
from django.utils import timezone
from marketplace.models import MaterialListing


class Command(BaseCommand):
    help = 'Expire all listings that have passed their TTL'

    def handle(self, *args, **kwargs):
        expired = MaterialListing.objects.filter(
            expires_at__lt=timezone.now(),
            status='active'
        ).update(status='expired')

        self.stdout.write(
            self.style.SUCCESS(f'✅ {expired} listings expired successfully!')
        )