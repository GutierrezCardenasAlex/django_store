from django.contrib import admin
from .models import Producto, Entrada, Salida, DetalleSalida, Factura

admin.site.register(Producto)
admin.site.register(Entrada)
admin.site.register(Salida)
admin.site.register(DetalleSalida)
admin.site.register(Factura)
