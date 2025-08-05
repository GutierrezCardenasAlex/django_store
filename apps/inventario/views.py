from django.shortcuts import render
from apps.inventario.models import *

# Create your views here.

def index(request):
  context = {
    'segment': 'inventario'
  }
  return render(request, "inventario/index.html", context)


def lista_productos(request):
    productos = Producto.objects.all()  # Consulta todos los productos
    return render(request, 'inventario/index.html', {'productos': productos})