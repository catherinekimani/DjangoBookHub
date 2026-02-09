from django.core.management.base import BaseCommand
from django.utils import timezone
from BookManager.models import CustomUser

class Command(BaseCommand):
    help = 'Deletes incomplete user accounts'

    def handle(self, *args, **kwargs):
        incomplete_users = CustomUser.objects.filter(is_verified=False, date_joined__lte=timezone.now() - timezone.timedelta(minutes=3))
        for user in incomplete_users:
            user.delete()
        self.stdout.write(self.style.SUCCESS('Incomplete user accounts deleted successfully'))
