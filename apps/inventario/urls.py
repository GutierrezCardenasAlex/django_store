from django.urls import path

from apps.inventario import views

urlpatterns = [
    path("", views.index, name="inventario"),
    path('inventario/', views.lista_productos, name='lista_productos'),
]

