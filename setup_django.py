import os
import subprocess
import random
import string
import sys

# ----------------------------
# Función para generar SECRET_KEY aleatoria
# ----------------------------
def generar_secret_key(length=50):
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(random.choice(chars) for _ in range(length))

# ----------------------------
# Ir a la carpeta del script
# ----------------------------
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------
# Activar entorno virtual
# ----------------------------
if not os.path.exists("venv"):
    print("Creando entorno virtual...")
    subprocess.call([sys.executable, "-m", "venv", "venv"])
else:
    print("Entorno virtual ya existe.")

# Activar el virtualenv
activate_script = os.path.join("venv", "Scripts", "activate.bat")
if os.name == "nt":
    os.system(f'call "{activate_script}"')

# ----------------------------
# Instalar requerimientos
# ----------------------------
if os.path.exists("requirements.txt"):
    print("Instalando requerimientos...")
    subprocess.call([os.path.join("venv","Scripts","pip.exe"), "install", "--upgrade", "pip"])
    subprocess.call([os.path.join("venv","Scripts","pip.exe"), "install", "-r", "requirements.txt"])
else:
    print("❌ No se encontró requirements.txt")
    sys.exit(1)

# ----------------------------
# Revisar si ya existe .env
# ----------------------------
if os.path.exists(".env"):
    print("✅ Configuración existente encontrada.")
    levantar = input("Desea levantar el servidor ahora? (s/n): ")
    if levantar.lower() == "s":
        subprocess.call([os.path.join("venv","Scripts","python.exe"), "manage.py", "runserver", "8001"])
    print("✅ Proyecto Django levantado exitosamente.")
    sys.exit(0)

# ----------------------------
# Configuración base de datos
# ----------------------------
print("Seleccione motor de base de datos:")
print("[1] SQLite")
print("[2] PostgreSQL")
motor = input("Elige una opción (1/2): ")

db_engine = "sqlite" if motor == "1" else "postgresql"

db_host = db_port = db_name = db_user = db_pass = ""
if db_engine == "postgresql":
    db_host = input("Host: ")
    db_port = input("Puerto (default 5432): ") or "5432"
    db_name = input("Nombre de la BD: ")
    db_user = input("Usuario: ")
    db_pass = input("Password: ")

# ----------------------------
# ALLOWED_HOSTS
# ----------------------------
allowed_hosts = input("Introduce hosts separados por coma (ej: localhost,127.0.0.1): ") or "localhost"

# ----------------------------
# Crear .env
# ----------------------------
secret_key = generar_secret_key()
with open(".env", "w") as f:
    f.write(f"DEBUG=True\n")
    f.write(f"SECRET_KEY={secret_key}\n")
    f.write(f"DB_ENGINE={db_engine}\n")
    if db_engine == "postgresql":
        f.write(f"DB_HOST={db_host}\n")
        f.write(f"DB_PORT={db_port}\n")
        f.write(f"DB_NAME={db_name}\n")
        f.write(f"DB_USERNAME={db_user}\n")
        f.write(f"DB_PASS={db_pass}\n")
    f.write(f"ALLOWED_HOSTS={allowed_hosts}\n")

print("✅ .env creado correctamente.")

# ----------------------------
# Crear carpetas media y static
# ----------------------------
os.makedirs("media", exist_ok=True)
os.makedirs("static", exist_ok=True)
print("✅ Carpetas media/ y static/ creadas.")

# ----------------------------
# Aplicar migraciones
# ----------------------------
print("Aplicando migraciones...")
subprocess.call([os.path.join("venv","Scripts","python.exe"), "manage.py", "makemigrations"])
subprocess.call([os.path.join("venv","Scripts","python.exe"), "manage.py", "migrate"])
print("✅ Migraciones aplicadas.")

# ----------------------------
# Crear superusuario
# ----------------------------
print("Vamos a crear un superusuario:")
su_user = input("Usuario: ")
su_email = input("Correo: ")
su_pass = input("Contraseña: ")

subprocess.call([
    os.path.join("venv","Scripts","python.exe"), 
    "manage.py", "shell", "-c",
    f"from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.create_superuser('{su_user}','{su_email}','{su_pass}') if not User.objects.filter(username='{su_user}').exists() else print('Ya existe el superusuario')"
])

# ----------------------------
# Preguntar si levantar servidor
# ----------------------------
levantar = input("Desea levantar el servidor ahora? (s/n): ")
if levantar.lower() == "s":
    subprocess.call([os.path.join("venv","Scripts","python.exe"), "manage.py", "runserver", "8001"])

print("✅ Proyecto Django PREMIUM configurado exitosamente.")
input("Presiona ENTER para salir...")
