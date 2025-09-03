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
