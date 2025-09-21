from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Crea un superusuario"

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "password123")
            self.stdout.write(self.style.SUCCESS("Superusuario creado"))
        else:
            self.stdout.write(self.style.WARNING("Superusuario ya existe"))
