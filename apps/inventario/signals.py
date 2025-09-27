from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto, Notificacion

@receiver(post_save, sender=Producto)
def notificar_bajo_stock(sender, instance, **kwargs):
    if instance.cantidad     < 5:
        Notificacion.objects.create(
            producto=instance,
            mensaje=f"El producto '{instance.nombre}' tiene bajo stock ({instance.cantidad} unidades)."
        )




import os
import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core import management
from .models import Cliente, Proveedor, Producto, Venta, Compra, BackupManager

# Carpeta de backups
BACKUP_DIR = os.path.join(settings.BASE_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

MAX_BACKUPS = 10

MODELOS = [
    "auth.User",
    "auth.Group",
    "auth.Permission",
    "inventario.Cliente",
    "inventario.Proveedor",
    "inventario.Categoria",
    "inventario.Producto",
    "inventario.Compra",
    "inventario.DetalleCompra",
    "inventario.Venta",
    "inventario.DetalleVenta",
    "inventario.Factura",
]

def limitar_backups():
    backups = sorted(os.listdir(BACKUP_DIR))
    if len(backups) > MAX_BACKUPS:
        for old_backup in backups[:-MAX_BACKUPS]:
            os.remove(os.path.join(BACKUP_DIR, old_backup))

def crear_backup(automatico=True):
    """Crea un backup automático o manual"""
    tipo = "auto" if automatico else "manual"
    filename = f"backup_{tipo}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(BACKUP_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        management.call_command("dumpdata", *MODELOS, indent=2, stdout=f)
    limitar_backups()
    return filename

# Signal para User
@receiver(post_save, sender=User)
def backup_al_crear_usuario(sender, instance, created, **kwargs):
    if created:
        crear_backup(automatico=True)

# Signals para modelos clave
CLAVES = [Cliente, Proveedor, Producto, Venta, Compra]

for modelo in CLAVES:
    @receiver(post_save, sender=modelo)
    def backup_al_guardar_modelo(sender, instance, created, **kwargs):
        if created:
            crear_backup(automatico=True)
