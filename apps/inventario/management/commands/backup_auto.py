import os
import datetime
from django.core.management.base import BaseCommand
from django.core import management
from django.conf import settings

APP_NAME = "inventario"
BACKUP_DIR = os.path.join(settings.BASE_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)
MAX_BACKUPS = 10

MODELOS = [
    "auth.User",
    "auth.Group",
    "auth.Permission",
    f"{APP_NAME}.Cliente",
    f"{APP_NAME}.Proveedor",
    f"{APP_NAME}.Categoria",
    f"{APP_NAME}.Producto",
    f"{APP_NAME}.Compra",
    f"{APP_NAME}.DetalleCompra",
    f"{APP_NAME}.Venta",
    f"{APP_NAME}.DetalleVenta",
    f"{APP_NAME}.Factura",
    f"{APP_NAME}.Notificacion",
    f"{APP_NAME}.Configuracion",
    f"{APP_NAME}.Trabajo",
]

class Command(BaseCommand):
    help = "Crear backup automático diario"

    def handle(self, *args, **kwargs):
        filename = f"backup_auto_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(BACKUP_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            management.call_command("dumpdata", *MODELOS, indent=2, stdout=f)

        # Limitar backups antiguos
        backups = sorted(os.listdir(BACKUP_DIR))
        if len(backups) > MAX_BACKUPS:
            for old_backup in backups[:-MAX_BACKUPS]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))

        self.stdout.write(self.style.SUCCESS(f"✅ Backup automático creado: {filename}"))
