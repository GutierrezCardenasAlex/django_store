from django.urls import path
from . import views
from .views import detener_servidor,reiniciar_servidor
from .views import (
    ProveedorListView,
    ProveedorCreateView,
    ProveedorUpdateView,
    ProveedorDeleteView,
    crear_compra,
    crear_venta
)

urlpatterns = [
    # Redirección desde la raíz de inventario
    path('', views.home_redirect, name='home_redirect'),

    # Dashboard / Resumen financiero
    path('dashboard/', views.resumen_financiero, name='resumen_financiero'),

    # Productos
    path('productos/register/', views.register_productos, name='register_productos'),
    path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/<int:id>/comprar/', views.comprar_producto_existente, name='comprar_producto_existente'),
    path('productos/', views.lista_productos, name='lista_productos'),  # Lista de productos

    # Clientes
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/ajax/registrar/', views.ajax_registrar_cliente, name='ajax_registrar_cliente'),
    path('clientes/ajax/editar/<int:id>/', views.ajax_editar_cliente, name='ajax_editar_cliente'),
    path('clientes/ajax/eliminar/<int:id>/', views.ajax_eliminar_cliente, name='ajax_eliminar_cliente'),
    path('clientes/register', views.register_clientes, name='register_clientes'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),

    # Categorías
    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categorias/nueva/", views.crear_categoria, name="crear_categoria"),
    path("categorias/editar/<int:pk>/", views.editar_categoria, name="editar_categoria"),
    path("categorias/eliminar/<int:pk>/", views.eliminar_categoria, name="eliminar_categoria"),

    # Compras
    path('compras/nueva/', views.crear_compra, name='crear_compra'),
    path('compras/', views.compras_list, name='compras_list'),
    path('compras/editar/<int:pk>/', views.editar_compra, name='editar_compra'),
    path('compras/eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),

    # Ventas
    path('ventas/crear/', crear_venta, name='crear_venta'),
    path('ventas/', views.ventas_list, name='ventas_list'),
    path('ventas/<int:pk>/', views.detalle_ventas, name='detalle_ventas'),
    path('ventas/crear/buscar-productos/', views.buscar_productos, name='buscar_productos'),

    # Notificaciones
    path('panel_notificaciones/', views.panel_notificaciones, name='panel_notificaciones'),
    path('notificacion/<int:notificacion_id>/leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('marcar_todas/', views.marcar_todas_como_leidas, name='marcar_todas_como_leidas'),
    path('eliminar_todas/', views.eliminar_todas_las_notificaciones, name='eliminar_todas_las_notificaciones'),

    # Proveedores
    path('proveedores/', ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/editar/<int:pk>/', ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/eliminar/<int:pk>/', ProveedorDeleteView.as_view(), name='proveedor_delete'),

    # Configuración
    path('configuraciones/', views.editar_configuracion, name='editar_configuracion'),

    #servidor
    path("detener/", detener_servidor, name="detener_servidor"),
    path("reiniciar/", reiniciar_servidor, name="reiniciar_servidor"),

    # Impresiones
    path('imprimir-ventas/', views.imprimir_ventas, name='imprimir_ventas'),
    path('imprimir-compras/', views.imprimir_compras, name='imprimir_compras'),
    path('imprimir-productos/', views.imprimir_productos, name='imprimir_productos'),
    path('reporte-completo/', views.reporte_completo, name='reporte_completo'),
]
