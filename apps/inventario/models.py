from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    nit_ci = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}".strip()


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    unidad_medida = models.CharField(max_length=20, blank=True, null=True)
    ganancia = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Compra #{self.id} - {self.fecha}"


class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


class Venta(models.Model):
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]
    fecha = models.DateField()
    hora = models.TimeField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha}"
    
    def calcular_monto(self):
        return sum(det.subtotal for det in self.detalles.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guardamos primero para que tenga ID
        self.monto = self.calcular_monto()
        super().save(update_fields=['monto'])


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return (self.precio_unitario - self.descuento) * self.cantidad

    @property
    def ganancia_unitaria(self):
        return self.precio_unitario - self.producto.precio_compra

    @property
    def ganancia_total(self):
        return self.ganancia_unitaria * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


class Factura(models.Model):
    nro_factura = models.IntegerField(unique=True)
    fecha = models.DateField()
    hora = models.TimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='factura')

    def __str__(self):
        return f"Factura #{self.nro_factura}"


class Notificacion(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.producto.nombre} - {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"


# models.py

from django.db import models

class Configuracion(models.Model):
    porcentaje_ganancia = models.DecimalField(
        max_digits=5, decimal_places=2, default=20.00,
        help_text="Porcentaje de ganancia aplicado al precio de compra."
    )
    permitir_descuentos = models.BooleanField(default=True)
    porcentaje_descuento_maximo = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        help_text="Porcentaje máximo de descuento permitido."
    )

    nombre_negocio = models.CharField(max_length=100, default="Mi Negocio")
    moneda = models.CharField(max_length=10, default="Bs.")
    
    direccion = models.CharField(max_length=200, blank=True, null=True, default="")
    telefono = models.CharField(max_length=20, blank=True, null=True, default="")
    nit = models.CharField(max_length=20, blank=True, null=True, default="")

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuración ({self.nombre_negocio})"

    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"



from django.db import models

class BackupManager(models.Model):
    class Meta:
        managed = False  # No crea tabla
        verbose_name = "Backup Manager"
        verbose_name_plural = "Backup Manager"


from django.db import models
from django.utils import timezone

class Trabajo(models.Model):
    nombre = models.CharField(max_length=150, help_text="Nombre del trabajo o servicio")
    descripcion = models.TextField(blank=True, null=True, help_text="Detalles opcionales")
    costo = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo del trabajo")
    fecha = models.DateField(default=timezone.now, help_text="Fecha de registro del trabajo")

    def __str__(self):
        return f"{self.nombre} - Bs. {self.costo}"
