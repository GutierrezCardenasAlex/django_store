from django.shortcuts import render, get_object_or_404, redirect
from apps.inventario.models import *
from .forms import CompraForm, DetalleCompraForm, ProductoForm, ClienteForm ,Producto,VentaForm, DetalleVentaFormSet
from django.utils import timezone
import pytz


from datetime import datetime
from django.contrib import messages
from django.db import transaction

from django.shortcuts import redirect
from django.contrib import messages

def home_redirect(request):
    # Mensaje solo una vez por sesión
    if not request.session.get('mensaje_bienvenida'):
        messages.success(request, "¡Bienvenido al sistema de inventario!")
        request.session['mensaje_bienvenida'] = True

    # Redirige a la ruta del dashboard
    return redirect('/inventario/dashboard/')


from django.shortcuts import render
from .models import Configuracion

def index(request):
    configuracion = Configuracion.objects.first()  # Obtiene la primera configuración
    return render(request, "inventario/index.html", {"configuracion": configuracion})


def lista_productos(request):
    productos = Producto.objects.all()  # Consulta todos los productos
    return render(request, 'inventario/index.html', {'productos': productos})

def register_productos(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  # Redirige a la lista luego de registrar
    else:
        form = ProductoForm()
    
    return render(request, 'inventario/register.html', {'form': form})

def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  # Cambia al nombre correcto de tu vista de lista
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'inventario/editar.html', {'form': form})

def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('lista_productos')  # Cambia este nombre al de tu vista de lista


from django.shortcuts import render, redirect
from .models import Cliente
from .forms import ClienteForm
from django.core.paginator import Paginator

def listar_clientes(request):
    clientes = Cliente.objects.all()
    total_clientes = clientes.count() 

    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    # ✅ Control de per_page seguro
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
        if per_page <= 0:
            per_page = 10
    except ValueError:
        per_page = 10

    # 🔎 Filtro de búsqueda
    if search_query:
        clientes = clientes.filter(
            nombre__icontains=search_query
        ) | clientes.filter(
            apellido__icontains=search_query
        ) | clientes.filter(
            nit_ci__icontains=search_query
        ) | clientes.filter(
            direccion__icontains=search_query
        ) | clientes.filter(
            telefono__icontains=search_query
        )

    paginator = Paginator(clientes, per_page)
    page_obj = paginator.get_page(page_number)

    # 📋 Formulario
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')
    else:
        form = ClienteForm()

    return render(request, 'clientes/index.html', {
        'clientes': page_obj,
        'form': form,
        'search_query': search_query,
        'per_page': per_page,
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ClienteForm

@csrf_exempt
def ajax_registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'cliente': {
                    'id': cliente.id,
                    'nombre': cliente.nombre,
                    'apellido': cliente.apellido,
                    'nit_ci': cliente.nit_ci,
                    'direccion': cliente.direccion,
                    'telefono': cliente.telefono,
                }
            })
        else:
            # Enviamos errores en formato limpio
            errors = {field: error.get_json_data() for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

from django.http import JsonResponse
from django.template.loader import render_to_string

def ajax_editar_clientes(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Cliente actualizado correctamente',
                'cliente': {
                    'id': cliente.id,
                    'nombre': cliente.nombre,
                    'apellido': cliente.apellido,
                    'nit_ci': cliente.nit_ci,
                    'direccion': cliente.direccion,
                    'telefono': cliente.telefono,
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ClienteForm(instance=cliente)
        html_form = render_to_string('clientes/includes/form_editar.html', {'form': form, 'cliente': cliente}, request=request)
        return JsonResponse({'html_form': html_form})

from django.http import JsonResponse
from django.template.loader import render_to_string

def ajax_editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'message': 'Cliente actualizado correctamente.',
                'cliente': {
                    'id': cliente.id,
                    'nombre': cliente.nombre,
                    'apellido': cliente.apellido,
                    'nit_ci': cliente.nit_ci,
                    'direccion': cliente.direccion,
                    'telefono': cliente.telefono,
                }
            })
        else:
            html_form = render_to_string('clientes/includes/form_editar.html', {'form': form}, request=request)
            return JsonResponse({'html_form': html_form}, status=400)
    else:
        form = ClienteForm(instance=cliente)
        html_form = render_to_string('clientes/includes/form_editar.html', {'form': form}, request=request)
        return JsonResponse({'html_form': html_form})


def ajax_eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    return JsonResponse({'success': True, 'message': 'Cliente eliminado correctamente'})



def register_clientes(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')  # Redirige a la lista luego de registrar
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/register.html', {'form': form})

def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')  # Cambia al nombre correcto de tu vista de lista
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/editar.html', {'form': form})

def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    return redirect('listar_clientes')  # Cambia este nombre al de tu vista de lista


from django.contrib.auth.decorators import login_required
bolivia_tz = pytz.timezone('America/La_Paz')
bolivia_now = timezone.now().astimezone(bolivia_tz)
from decimal import Decimal
from .models import Configuracion
@login_required
def crear_compra(request):
    if request.method == 'POST':
        producto_form = ProductoForm(request.POST)
        compra_form = CompraForm(request.POST)
        configuracion = Configuracion.objects.first()

        if not configuracion:
            return render(request, 'error.html', {'mensaje': 'No hay configuración cargada.'})

        # Obtener el porcentaje de ganancia
        porcentaje_ganancia = configuracion.porcentaje_ganancia

        if producto_form.is_valid() and compra_form.is_valid():
            # Obtener instancia del producto sin guardar aún
            producto = producto_form.save(commit=False)

            # Asignar precio_venta = precio_compra antes de guardar
            #estimacion a ganar es de un 20 %
            producto.precio_venta = producto.precio_compra  + (producto.precio_compra * producto.ganancia / Decimal('100')) 
            producto.save()

            # Calcular monto total
            precio = producto.precio_compra
            cantidad = producto.cantidad
            monto_total = precio * cantidad

            # Crear compra
            compra = compra_form.save(commit=False)
            compra.monto = monto_total
            compra.usuario = request.user

            # Verificamos si se debe incluir el proveedor
            incluir_proveedor = compra_form.cleaned_data.get('incluir_proveedor')
            if not incluir_proveedor:
                compra.proveedor = None  # Anulamos proveedor si no se quiere incluir

            compra.save()

            # Crear detalle
            detalle = DetalleCompraForm().save(commit=False)
            detalle.compra = compra
            detalle.producto = producto
            detalle.cantidad = cantidad
            detalle.precio = precio
            detalle.save()

            return redirect('lista_productos')

    else:
        producto_form = ProductoForm()
        compra_form = CompraForm(initial={
            'fecha': bolivia_now().date(),
            'hora': bolivia_now().time()
        })

    return render(request, 'compras/crear_compra.html', {
        'producto_form': producto_form,
        'compra_form': compra_form,
    })


from django.shortcuts import render
from .models import Compra

def compras_list(request):
    compras = Compra.objects.select_related('usuario', 'proveedor').order_by('-fecha', '-hora')
    return render(request, 'compras/compras_list.html', {'compras': compras})

def editar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    if request.method == "POST":
        form = CompraForm(request.POST, instance=compra)
        if form.is_valid():
            form.save()
            messages.success(request, f'Compra #{compra.id} actualizada con éxito.')
            return redirect('compras_list')  # Redirige a la lista de compras
    else:
        form = CompraForm(instance=compra)

    return render(request, 'compras/editar_compra.html', {'form': form, 'compra': compra})


def eliminar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    if request.method == "POST":
        compra.delete()
        messages.success(request, f'Compra #{compra.id} eliminada con éxito.')
        return redirect('compras_list')
    return redirect('compras_list')  # Redirige si no es POST

from decimal import Decimal
from django.shortcuts import get_object_or_404, render, redirect
from .models import Producto, Compra, DetalleCompra, Configuracion
from .forms import CompraForm, CompraProductoExistenteForm
from django.utils.timezone import now as bolivia_now

def comprar_producto_existente(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        compra_form = CompraForm(request.POST)
        producto_form = CompraProductoExistenteForm(request.POST)
        configuracion = Configuracion.objects.first()
        if not configuracion:
            return render(request, 'error.html', {'mensaje': 'No hay configuración cargada.'})

        if compra_form.is_valid() and producto_form.is_valid():

            # Cantidad puede venir vacía → quedará como None
            cantidad = producto_form.cleaned_data.get('cantidad')
            precio_compra = producto_form.cleaned_data['precio_compra']
            ganancia = producto_form.cleaned_data['ganancia']

            # Actualizar precio y ganancia del producto SIEMPRE
            producto.ganancia = ganancia
            producto.precio_compra = precio_compra
            producto.precio_venta = precio_compra + (precio_compra * ganancia / Decimal('100'))
            producto.save()

            # Crear la compra
            compra = compra_form.save(commit=False)
            compra.usuario = request.user

            # Si cantidad es None → monto debe ser 0
            compra.monto = (precio_compra * cantidad) if cantidad else 0

            incluir_proveedor = compra_form.cleaned_data.get('incluir_proveedor')
            if not incluir_proveedor:
                compra.proveedor = None

            compra.save()

            # SOLO modificar stock y crear detalle si hay cantidad
            if cantidad:
                # Actualizar stock
                producto.cantidad += cantidad
                producto.save()

                # Crear detalle de compra
                DetalleCompra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=cantidad,
                    precio=precio_compra
                )

            return redirect('lista_productos')


    else:
        compra_form = CompraForm(initial={
            'fecha': bolivia_now().date(),
            'hora': bolivia_now().time()
        })

        producto_form = CompraProductoExistenteForm(initial={
            'precio_compra': producto.precio_compra,
            'ganancia': producto.ganancia  
        })

    return render(request, 'inventario/comprar_existente.html', {
        'producto': producto,
        'compra_form': compra_form,
        'producto_form': producto_form
    })



@login_required
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST, queryset=DetalleVenta.objects.none())

        if venta_form.is_valid() and formset.is_valid():
            venta = venta_form.save(commit=False)
            venta.usuario = request.user
            venta.fecha = datetime.now().date()
            venta.hora = datetime.now().time()
            venta.monto = 0
            venta.save()

            total = 0
            for form in formset:
                detalle = form.save(commit=False)
                detalle.venta = venta

                producto = Producto.objects.select_for_update().get(pk=detalle.producto.pk)

                if producto.cantidad < detalle.cantidad:
                    messages.error(request, f"No hay suficiente stock de {producto.nombre}")
                    transaction.set_rollback(True)
                    return redirect('crear_venta')

                producto.cantidad -= detalle.cantidad
                producto.save()

                detalle.precio_unitario = producto.precio_venta
                detalle.save()

                subtotal = (producto.precio_venta * detalle.cantidad) - detalle.descuento
                total += subtotal

            venta.monto = total
            venta.save()

            messages.success(request, "Venta creada exitosamente.")
            return redirect('ventas_list')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        venta_form = VentaForm()
        formset = DetalleVentaFormSet(queryset=DetalleVenta.objects.none())

    return render(request, 'ventas/crear_venta.html', {
        'venta_form': venta_form,
        'formset': formset,
        'productos': Producto.objects.none(),  # 👈 clave: NO mostrar productos en el select inicial
    })

# views.py
from django.http import JsonResponse
from django.db.models import Q
from .models import Producto
from django.contrib.auth.decorators import login_required

@login_required
def buscar_productos(request):
    q = request.GET.get("q", "")
    productos = Producto.objects.filter(
        Q(nombre__icontains=q)
    )
    data = [{
        "id": p.id,
        "nombre": p.nombre,
        "precio_venta": float(p.precio_venta),
        "stock": p.cantidad,
    } for p in productos]
    return JsonResponse(data, safe=False)



def ventas_list(request):
    ventas = Venta.objects.prefetch_related('detalles__producto').all().order_by('-fecha', '-hora')

    for venta in ventas:
        venta.total = sum(det.subtotal for det in venta.detalles.all())
        venta.ganancia_total = sum(det.ganancia_total for det in venta.detalles.all())

    return render(request, 'ventas/ventas_list.html', {'ventas': ventas})


def detalle_ventas(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/detalle_ventas.html', {'venta': venta})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Notificacion

def panel_notificaciones(request):
    notificaciones = Notificacion.objects.order_by('-fecha')[:20]
    notificaciones_no_leidas_count = Notificacion.objects.filter(leida=False).count()

    context = {
        'notificaciones': notificaciones,
        'notificaciones_no_leidas_count': notificaciones_no_leidas_count
    }
    return render(request, 'includes/navigation.html', context)


def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)
    notificacion.leida = True
    notificacion.save()
    messages.success(request, "Notificación marcada como leída.")
    return redirect('panel_notificaciones')

def marcar_todas_como_leidas(request):
    Notificacion.objects.filter(leida=False).update(leida=True)
    messages.success(request, "Todas las notificaciones han sido marcadas como leídas.")
    return redirect(request.META.get('HTTP_REFERER', 'panel_notificaciones'))

def eliminar_todas_las_notificaciones(request):
    Notificacion.objects.all().delete()
    messages.success(request, "Todas las notificaciones han sido eliminadas.")
    return redirect(request.META.get('HTTP_REFERER', 'panel_notificaciones'))



from django.shortcuts import render
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Venta, DetalleVenta, Compra, Cliente, Proveedor, Producto, Trabajo

def resumen_financiero(request):
    # Si la ruta es '/', mostramos solo un mensaje de bienvenida
    if request.path == '/':
        messages.info(request, "¡Bienvenido al sistema de inventario!")
        return render(request, 'pages/bienvenida.html')

    # --- Si la URL es otra (por ejemplo /inventario), carga el dashboard ---
    total_ventas = Venta.objects.aggregate(total=Sum('monto'))['total'] or 0
    total_compras = Compra.objects.aggregate(total=Sum('monto'))['total'] or 0
    total_trabajos_todos = Trabajo.objects.aggregate(total=Sum('costo'))['total'] or 0

    if total_ventas > 0:
        ganancia_total = DetalleVenta.objects.annotate(
            ganancia=ExpressionWrapper(
                (F('precio_unitario') - F('producto__precio_compra')) * F('cantidad'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).aggregate(total=Sum('ganancia'))['total'] or 0
    else:
        ganancia_total = 0

    total_clientes = Cliente.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_productos = Producto.objects.count()
    total_trabajos = Trabajo.objects.count()

    productos = Producto.objects.all()
    nombres_productos = [p.nombre for p in productos]
    stock_productos = [p.cantidad for p in productos]

    ventas_recientes = Venta.objects.all().order_by('-fecha', '-hora')[:10]

    context = {
        'total_ventas': total_ventas,
        'total_compras': total_compras,
        'total_trabajos_todos': total_trabajos_todos,
        'ganancia': ganancia_total,
        'total_clientes': total_clientes,
        'total_proveedores': total_proveedores,
        'total_productos': total_productos,
        'total_trabajos': total_trabajos,
        'ventas': ventas_recientes,
        'nombres_productos': nombres_productos,
        'stock_productos': stock_productos
    }
    return render(request, 'pages/index.html', context)

    
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Proveedor
from .forms import ProveedorForm  # Lo vamos a crear abajo

# Ver lista de proveedores
class ProveedorListView(ListView):
    model = Proveedor
    template_name = 'proveedor/lista.html'
    context_object_name = 'proveedores'

# Crear proveedor
class ProveedorCreateView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedor/form.html'
    success_url = reverse_lazy('proveedor_list')

# Editar proveedor
class ProveedorUpdateView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedor/form.html'
    success_url = reverse_lazy('proveedor_list')

# Eliminar proveedor
class ProveedorDeleteView(DeleteView):
    model = Proveedor
    template_name = 'proveedor/confirmar_eliminar.html'
    success_url = reverse_lazy('proveedor_list')


# views.py

from django.shortcuts import render, redirect
from .models import Configuracion
from .forms import ConfiguracionForm
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def editar_configuracion(request):
    config, _ = Configuracion.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('editar_configuracion')
    else:
        form = ConfiguracionForm(instance=config)

    return render(request, 'configuracion/editar_configuracion.html', {
        'form': form
    })



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Categoria
from .forms import CategoriaForm

@login_required
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, "categorias/lista.html", {"categorias": categorias})

@login_required
def crear_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Categoría creada correctamente.")
            return redirect("lista_categorias")
        else:
            messages.error(request, "❌ Hubo un error. Revisa los datos.")
    else:
        form = CategoriaForm()

    return render(request, "categorias/crear.html", {"form": form})

from django.shortcuts import get_object_or_404

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Categoría actualizada correctamente.")
            return redirect("lista_categorias")
        else:
            messages.error(request, "❌ Hubo un error al actualizar.")
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, "categorias/editar.html", {"form": form, "categoria": categoria})


@login_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        categoria.delete()
        messages.success(request, "🗑️ Categoría eliminada correctamente.")
        return redirect("lista_categorias")

    return render(request, "categorias/eliminar.html", {"categoria": categoria})


# views.py
import os
import signal
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required  # Solo admins pueden detener el servidor
def detener_servidor(request):
    pid = os.getpid()  # Obtiene el PID del proceso actual
    os.kill(pid, signal.SIGINT)  # Envía la señal para detener el servidor
    return HttpResponse("El servidor Django se está deteniendo...")



import os
import signal
import subprocess
import sys
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def reiniciar_servidor(request):
    if request.method == "POST":
        python_exe = sys.executable
        manage_py = os.path.join(os.getcwd(), "manage.py")

        # Levantar un nuevo servidor
        subprocess.Popen([python_exe, manage_py, "runserver"])

        # Detener el actual
        os.kill(os.getpid(), signal.SIGINT)

        return HttpResponse("Reiniciando servidor...")

    return HttpResponse("Método no permitido", status=405)


from django.shortcuts import render
from .models import Venta, Compra, Producto

def imprimir_ventas(request):
    ventas = Venta.objects.all()
    return render(request, "imprimir/imprimir_ventas_detalle.html", {"ventas": ventas})

def imprimir_compras(request):
    compras = Compra.objects.all()
    return render(request, "imprimir/imprimir_compras_detallado.html", {"compras": compras})

def imprimir_productos(request):
    productos = Producto.objects.all()
    return render(request, "imprimir/imprimir_productos_detallado.html", {"productos": productos})


from django.shortcuts import render
from .models import Producto, Compra, Venta
from django.db.models import F, Sum

from .models import Producto, Compra, Venta, Configuracion

def reporte_completo(request):
    productos = Producto.objects.all()
    compras = Compra.objects.prefetch_related('detalles')
    ventas = Venta.objects.prefetch_related('detalles')

    # Calcular totales de Compras y Ventas
    total_compras = sum(d.precio * d.cantidad for compra in compras for d in compra.detalles.all())
    total_ventas = sum(d.subtotal for venta in ventas for d in venta.detalles.all())

    # Obtener la configuración del negocio
    configuracion = Configuracion.objects.first()  # Suponiendo que solo hay un registro de configuración

    context = {
        'productos': productos,
        'compras': compras,
        'ventas': ventas,
        'total_compras': total_compras,
        'total_ventas': total_ventas,
        'configuracion': configuracion
    }
    return render(request, "imprimir/reporte_completo.html", context)


from django.shortcuts import render, get_object_or_404, redirect
from .models import Trabajo
from .forms import TrabajoForm
from django.contrib import messages

# Lista de trabajos
def lista_trabajos(request):
    trabajos = Trabajo.objects.all().order_by('-fecha')
    return render(request, 'trabajos/lista_trabajos.html', {'trabajos': trabajos})

# Crear trabajo
def crear_trabajo(request):
    if request.method == 'POST':
        form = TrabajoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trabajo creado correctamente.')
            return redirect('lista_trabajos')
    else:
        form = TrabajoForm()
    return render(request, 'trabajos/crear_trabajo.html', {'form': form})

# Ver detalles de un trabajo
def detalle_trabajo(request, pk):
    trabajo = get_object_or_404(Trabajo, pk=pk)
    return render(request, 'trabajos/detalle_trabajo.html', {'trabajo': trabajo})

# Eliminar trabajo
def eliminar_trabajo(request, pk):
    trabajo = get_object_or_404(Trabajo, pk=pk)
    if request.method == 'POST':
        trabajo.delete()
        messages.success(request, 'Trabajo eliminado correctamente.')
        return redirect('lista_trabajos')
    return render(request, 'trabajos/eliminar_trabajo.html', {'trabajo': trabajo})


