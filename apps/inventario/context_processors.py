# inventario/context_processors.py

from .models import Notificacion

def notificaciones(request):
    if request.user.is_authenticated:
        notificaciones = Notificacion.objects.order_by('-fecha')[:20]
        no_leidas = Notificacion.objects.filter(leida=False).count()
        return {
            'notificaciones': notificaciones,
            'notificaciones_no_leidas_count': no_leidas
        }
    return {}
