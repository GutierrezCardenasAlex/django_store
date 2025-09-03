from django.urls import path

from apps.inventario import views
from .views import crear_compra, crear_venta

urlpatterns = [
    #url inventario
    path("", views.index, name="inventario"),
    path('inventario/', views.lista_productos, name='lista_productos'),
    path('inventario/register', views.register_productos, name='register_productos'), 
    path('inventario/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('inventario/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    #url clientes 
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/register', views.register_clientes, name='register_clientes'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),
    #compras
    path('compras/nueva/', crear_compra, name='crear_compra'),
    path('ventas/crear/', crear_venta, name='crear_venta'),
    path('ventas/', views.ventas_list, name='ventas_list'),
    path('ventas/<int:pk>/', views.detalle_ventas, name='detalle_ventas'),

    path('inventario/', views.panel_notificaciones, name='panel_notificaciones'),

    # Marcar una notificación específica como leída
    path('notificacion/<int:notificacion_id>/leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),

    # Marcar todas como leídas
    path('inventario/marcar_todas/', views.marcar_todas_como_leidas, name='marcar_todas_como_leidas'),

    # Eliminar todas las notificaciones
    path('notificaciones/eliminar_todas/', views.eliminar_todas_las_notificaciones, name='eliminar_todas_las_notificaciones'),


]

