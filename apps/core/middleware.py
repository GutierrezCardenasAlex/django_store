from django.shortcuts import redirect
from django.conf import settings

EXCLUDED_PATHS = [
    "/accounts/login/",
    "/admin/",
    "/logout/",
    "/api/",  # si tienes API pública
]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Permitir acceso a rutas excluidas sin login
        if any(request.path.startswith(path) for path in EXCLUDED_PATHS):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
