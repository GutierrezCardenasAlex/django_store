# config/urls.py
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views

# Función para redirigir la raíz al inventario/dashboard
def redirect_root(request):
    return redirect('/inventario/')

urlpatterns = [
    path('', redirect_root),  # ✅ Aquí redirige la raíz
    path(
        'login/',
        auth_views.LoginView.as_view(
            redirect_authenticated_user=True,
            next_page='/inventario/'
        ),
        name='login'
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("inventario/", include("apps.inventario.urls")),
    path("", include("apps.dyn_api.urls")),
    path("", include("admin_datta.urls")),
    path("login/jwt/", obtain_auth_token),
]
