from django import forms
from .models import Producto, Cliente, Compra, DetalleCompra, Producto, Venta, DetalleVenta, Proveedor
from django.forms import inlineformset_factory
from django.forms import modelformset_factory

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'descuento']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control cantidad', 'min': '1'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control descuento', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar data-precio a cada opción
        self.fields['producto'].widget.choices = [
            (p.pk, f"{p.nombre}") for p in Producto.objects.all()
        ]
        self.fields['producto'].widget.attrs.update({'class': 'form-control'})


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'metodo_pago']
        widgets = {
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
        }

from django import forms
from django.forms import modelformset_factory  # ✅ <-- esta línea

from .models import DetalleVenta

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'descuento']

    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        if not producto:
            raise forms.ValidationError("Debes seleccionar un producto.")
        return producto


DetalleVentaFormSet = modelformset_factory(
    DetalleVenta,
    form=DetalleVentaForm,
    extra=0,
    can_delete=False
)


class CompraForm(forms.ModelForm):
    incluir_proveedor = forms.BooleanField(required=False, label="¿Agregar proveedor?")

    class Meta:
        model = Compra
        fields = ['proveedor', 'fecha', 'hora']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }

from .models import Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción (opcional)', 'rows': 3}),
        }

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'precio']
    

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre','descripcion','precio_compra','cantidad','categoria','unidad_medida']  # ajusta según tu modelo
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre','apellido','nit_ci','direccion','telefono','email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'nit_ci': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# forms.py

from django import forms
from .models import Configuracion

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = [
            'porcentaje_ganancia',
            'permitir_descuentos',
            'porcentaje_descuento_maximo',
            'nombre_negocio',
            'moneda'
        ]
        widgets = {
            'porcentaje_ganancia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'permitir_descuentos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'porcentaje_descuento_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'nombre_negocio': forms.TextInput(attrs={'class': 'form-control'}),
            'moneda': forms.TextInput(attrs={'class': 'form-control'}),
        }


from django import forms

class CompraProductoExistenteForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, label='Cantidad a comprar')
    precio_compra = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        label='Precio de compra unitario'
    )

