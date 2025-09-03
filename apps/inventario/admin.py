from django.contrib import admin
from .models import Cliente, Proveedor, Producto, Venta, DetalleVenta, Compra, DetalleCompra, Factura 

admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Compra)
admin.site.register(DetalleCompra)
admin.site.register(Factura)
