from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from apps.inventario import views as inventario_views
from django.contrib.auth import views as auth_views  # 👈 Importa las vistas de auth

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),  # 👈 Vista de login
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),  # 👈 Cierre de sesión

    path("", include("apps.dyn_api.urls")),
    path("", include("admin_datta.urls")),

    path("admin/", admin.site.urls),
    path("", inventario_views.resumen_financiero, name="resumen_financiero"),
    path("inventario/", include("apps.inventario.urls")),
]

try:
    urlpatterns.append(path("api/", include("api.urls")))
    urlpatterns.append(path("login/jwt/", view=obtain_auth_token))
except:
    pass
