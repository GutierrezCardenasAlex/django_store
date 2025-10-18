import os
import datetime
from django.contrib import admin, messages
from django.http import FileResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.conf import settings
from django.shortcuts import render
from django.core import management

from .models import (
    Cliente, Proveedor, Producto, Venta, DetalleVenta,
    Compra, DetalleCompra, Factura, Trabajo, BackupManager
)

# ------------------------------
# REGISTRO MODELOS NORMALES
# ------------------------------
admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Compra)
admin.site.register(DetalleCompra)
admin.site.register(Factura)
admin.site.register(Trabajo)


# ------------------------------
# BACKUP CONFIGURACION
# ------------------------------
APP_NAME = "inventario"

BACKUP_DIRS = {
    "Principal": os.path.join(settings.BASE_DIR, "backups"),
    "Extra": os.path.join(settings.BASE_DIR, "extra_backups"),
}

for path_dir in BACKUP_DIRS.values():
    os.makedirs(path_dir, exist_ok=True)

MAX_BACKUPS = 10

MODELOS = [
    "auth.User",
    "auth.Group",
    "auth.Permission",
    f"{APP_NAME}.Cliente",
    f"{APP_NAME}.Proveedor",
    f"{APP_NAME}.Categoria",
    f"{APP_NAME}.Producto",
    f"{APP_NAME}.Compra",
    f"{APP_NAME}.DetalleCompra",
    f"{APP_NAME}.Venta",
    f"{APP_NAME}.DetalleVenta",
    f"{APP_NAME}.Factura",
    f"{APP_NAME}.Notificacion",
    f"{APP_NAME}.Configuracion",
    f"{APP_NAME}.Trabajo",
]


# ------------------------------
# BACKUP ADMIN
# ------------------------------
@admin.register(BackupManager)
class BackupAdmin(admin.ModelAdmin):
    change_list_template = "admin/backups.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("create-backup/<str:carpeta>/", self.admin_site.admin_view(self.create_backup_view), name="create-backup"),
            path("download/<str:carpeta>/<str:filename>/", self.admin_site.admin_view(self.download_backup_view), name="download-backup"),
            path("restore/<str:carpeta>/<str:filename>/", self.admin_site.admin_view(self.restore_backup_view), name="restore-backup"),
            path("restore-external/", self.admin_site.admin_view(self.restore_external_view), name="restore-external"),
        ]
        return custom_urls + urls

    # ------------------------------
    # Mostrar lista de backups
    # ------------------------------
    def changelist_view(self, request, extra_context=None):
        backups = []
        for carpeta, path_dir in BACKUP_DIRS.items():
            for b in sorted(os.listdir(path_dir), reverse=True):
                tipo = "Automático" if b.startswith("backup_auto_") else "Manual"
                try:
                    partes = b.replace(".json", "").split("_")
                    fecha_str = partes[-2] + "_" + partes[-1]
                    fecha = datetime.datetime.strptime(fecha_str, "%Y%m%d_%H%M%S")
                except:
                    fecha = None
                backups.append({
                    "nombre": b,
                    "tipo": tipo,
                    "fecha": fecha,
                    "carpeta": carpeta
                })

        context = {
            "backups": backups,
            "es_superusuario": request.user.is_superuser,
            "carpetas": list(BACKUP_DIRS.keys())
        }
        return render(request, self.change_list_template, context)

    # ------------------------------
    # Crear backup manual
    # ------------------------------
    def create_backup_view(self, request, carpeta):
        if not request.user.is_superuser:
            messages.error(request, "❌ Solo los superusuarios pueden crear backups.")
            return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

        if carpeta not in BACKUP_DIRS:
            messages.error(request, "Carpeta de backup no válida.")
            return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

        filename = f"backup_manual_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(BACKUP_DIRS[carpeta], filename)

        with open(filepath, "w", encoding="utf-8") as f:
            management.call_command("dumpdata", *MODELOS, indent=2, stdout=f)

        self._limitar_backups(carpeta)
        messages.success(request, f"✅ Backup creado en {carpeta}: {filename}")
        return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

    # ------------------------------
    # Descargar backup
    # ------------------------------
    def download_backup_view(self, request, carpeta, filename):
        if carpeta not in BACKUP_DIRS:
            messages.error(request, "Carpeta de backup no válida.")
            return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

        filepath = os.path.join(BACKUP_DIRS[carpeta], filename)
        if not os.path.exists(filepath):
            messages.error(request, f"❌ El archivo {filename} no existe en {carpeta}.")
            return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

        return FileResponse(open(filepath, "rb"), as_attachment=True)

    # ------------------------------
    # Restaurar backup desde carpeta interna
    # ------------------------------
    def restore_backup_view(self, request, carpeta, filename):
        if not request.user.is_superuser:
            messages.error(request, "❌ Solo los superusuarios pueden restaurar backups.")
            return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

        if carpeta not in BACKUP_DIRS:
            messages.error(request, "Carpeta de backup no válida.")
            return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

        filepath = os.path.join(BACKUP_DIRS[carpeta], filename)
        if not os.path.exists(filepath):
            messages.error(request, f"❌ El archivo {filename} no existe en {carpeta}.")
            return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

        try:
            management.call_command("migrate")
            management.call_command("loaddata", filepath)
            messages.success(request, f"✅ Base de datos restaurada desde: {filename} ({carpeta})")
        except Exception as e:
            messages.error(request, f"❌ Error al restaurar backup: {e}")

        return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

    # ------------------------------
    # Restaurar backup externo
    # ------------------------------
    def restore_external_view(self, request):
        if not request.user.is_superuser:
            messages.error(request, "❌ Solo los superusuarios pueden restaurar backups.")
            return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

        if request.method == "POST":
            filepath = request.FILES.get("backup_file")
            if not filepath:
                messages.error(request, "❌ Debes seleccionar un archivo JSON.")
                return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

            tmp_path = os.path.join(settings.BASE_DIR, "tmp_restore.json")
            with open(tmp_path, "wb+") as dest:
                for chunk in filepath.chunks():
                    dest.write(chunk)

            try:
                management.call_command("migrate")
                management.call_command("loaddata", tmp_path)
                messages.success(request, f"✅ Base de datos restaurada desde: {filepath.name}")
            except Exception as e:
                messages.error(request, f"❌ Error al restaurar backup: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        return HttpResponseRedirect(reverse("admin:inventario_backupmanager_changelist"))

    # ------------------------------
    # Limitar backups
    # ------------------------------
    def _limitar_backups(self, carpeta):
        path_dir = BACKUP_DIRS[carpeta]
        # Ordenar los archivos por fecha descendente (los más recientes primero)
        backups = sorted(
            [b for b in os.listdir(path_dir) if b.endswith(".json")],
            key=lambda x: os.path.getmtime(os.path.join(path_dir, x)),
            reverse=True
        )
        # Conservar solo los 3 más recientes
        for old_backup in backups[3:]:
            os.remove(os.path.join(path_dir, old_backup))

