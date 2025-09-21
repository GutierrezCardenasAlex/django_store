import os
import subprocess
import random
import string
import sys
import threading
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar

# ----------------------------
# Funciones auxiliares
# ----------------------------
def generar_secret_key(length=50):
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(random.choice(chars) for _ in range(length))

def ejecutar(cmd, log_widget=None):
    """Ejecutar comando y mostrar log en tiempo real"""
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        for line in process.stdout:
            if log_widget:
                log_widget.insert(END, line)
                log_widget.see(END)
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar: {cmd}\n{e}")
        sys.exit(1)

def terminar_instalador():
    if messagebox.askyesno("Salir", "¿Deseas terminar la ejecución del instalador?"):
        global server_process
        if server_process is not None:
            server_process.terminate()
        root.quit()

# ----------------------------
# Crear entorno virtual
# ----------------------------
if not os.path.exists("venv"):
    subprocess.call([sys.executable, "-m", "venv", "venv"])
venv_python = os.path.join("venv","Scripts","python.exe")
venv_pip = os.path.join("venv","Scripts","pip.exe")

# Instalar dependencias
if os.path.exists("requirements.txt"):
    subprocess.call([venv_pip,"install","--upgrade","pip"])
    subprocess.call([venv_pip,"install","-r","requirements.txt"])

# ----------------------------
# GUI Wizard PRO
# ----------------------------
root = Tk()
root.title("Instalador PRO Django")
root.geometry("700x650")

frames = {}
for i in range(5):
    frame = Frame(root)
    frame.place(relx=0,rely=0,relwidth=1,relheight=1)
    frames[i] = frame

current_frame = 0
db_var = StringVar(value="sqlite")
host_var = StringVar()
port_var = StringVar()
name_var = StringVar()
user_var = StringVar()
pass_var = StringVar()
hosts_var = StringVar()
su_user_var = StringVar()
su_email_var = StringVar()
su_pass_var = StringVar()
server_process = None

# ----------------------------
# Cambiar frame
# ----------------------------
def show_frame(i):
    global current_frame
    frames[current_frame].pack_forget()
    frames[i].pack(fill="both", expand=True)
    current_frame = i

# ----------------------------
# Detectar .env
# ----------------------------
env_exists = os.path.exists(".env")
if env_exists:
    messagebox.showinfo("Detección", "Se detectó archivo .env existente.\nSe omitirá configuración de DB y migraciones.")
    show_frame(4)
else:
    show_frame(0)

# ----------------------------
# Paso 0: Bienvenida
# ----------------------------
Label(frames[0], text="Bienvenido al Instalador PRO Django", font=("Arial",16,"bold")).pack(pady=50)
Button(frames[0], text="Next", command=lambda: show_frame(1)).pack(pady=10)
Button(frames[0], text="Salir", command=terminar_instalador, bg="red", fg="white").pack(pady=10)

# ----------------------------
# Paso 1: Config DB
# ----------------------------
Label(frames[1], text="Configuración de Base de Datos", font=("Arial",14,"bold")).pack(pady=10)
Radiobutton(frames[1], text="SQLite", variable=db_var, value="sqlite").pack()
Radiobutton(frames[1], text="PostgreSQL", variable=db_var, value="postgresql").pack()
for label, var in [("Host:", host_var), ("Puerto:", port_var), ("Nombre DB:", name_var), ("Usuario DB:", user_var), ("Password DB:", pass_var), ("ALLOWED_HOSTS:", hosts_var)]:
    Label(frames[1], text=label).pack()
    Entry(frames[1], textvariable=var, show="*" if "Password" in label else None).pack()
Button(frames[1], text="Back", command=lambda: show_frame(0)).pack(side=LEFT,padx=50,pady=20)
Button(frames[1], text="Next", command=lambda: show_frame(2)).pack(side=RIGHT,padx=50,pady=20)
Button(frames[1], text="Salir", command=terminar_instalador, bg="red", fg="white").pack(side=BOTTOM,pady=10)

# ----------------------------
# Paso 2: Crear .env y carpetas
# ----------------------------
def crear_env_pro():
    db_engine = db_var.get()
    secret_key = generar_secret_key()
    env_lines = ["DEBUG=True", f"SECRET_KEY={secret_key}", f"DB_ENGINE={db_engine}"]
    if db_engine=="postgresql":
        env_lines += [
            f"DB_HOST={host_var.get()}",
            f"DB_PORT={port_var.get() or '5432'}",
            f"DB_NAME={name_var.get()}",
            f"DB_USERNAME={user_var.get()}",
            f"DB_PASS={pass_var.get()}",
        ]
    env_lines.append(f"ALLOWED_HOSTS={hosts_var.get() or 'localhost'}")
    with open(".env","w") as f:
        f.write("\n".join(env_lines))
    os.makedirs("media", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    log_text.insert(END, ".env creado y carpetas listas\n")

Label(frames[2], text="Paso 2: Configuración .env y Carpetas", font=("Arial",14,"bold")).pack(pady=20)
Button(frames[2], text="Crear Configuración", command=crear_env_pro,bg="green",fg="white").pack(pady=10)
log_text = Text(frames[2], height=15)
log_text.pack(fill=BOTH, expand=True, pady=10)
Button(frames[2], text="Back", command=lambda: show_frame(1)).pack(side=LEFT,padx=50,pady=20)
Button(frames[2], text="Next", command=lambda: show_frame(3)).pack(side=RIGHT,padx=50,pady=20)
Button(frames[2], text="Salir", command=terminar_instalador, bg="red", fg="white").pack(side=BOTTOM,pady=10)

# ----------------------------
# Paso 3: Migraciones y superusuario con barra
# ----------------------------
def aplicar_migraciones_pro():
    progress['value'] = 0
    root.update_idletasks()
    ejecutar([venv_python,"manage.py","makemigrations"], log_widget=log_text)
    progress['value'] = 50
    root.update_idletasks()
    ejecutar([venv_python,"manage.py","migrate"], log_widget=log_text)
    progress['value'] = 100
    messagebox.showinfo("Exito","Migraciones aplicadas")
    root.update_idletasks()

def crear_superusuario_pro():
    cmd = f'from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.create_superuser("{su_user_var.get()}","{su_email_var.get()}","{su_pass_var.get()}") if not User.objects.filter(username="{su_user_var.get()}").exists() else print("Ya existe superusuario")'
    ejecutar([venv_python,"manage.py","shell","-c",cmd], log_widget=log_text)
    messagebox.showinfo("Exito","Superusuario creado")

Label(frames[3], text="Paso 3: Migraciones y Superusuario", font=("Arial",14,"bold")).pack(pady=10)
Button(frames[3], text="Aplicar Migraciones", command=lambda: threading.Thread(target=aplicar_migraciones_pro).start(), bg="orange", fg="white").pack(pady=5)
progress = Progressbar(frames[3], orient=HORIZONTAL, length=400, mode='determinate')
progress.pack(pady=10)

Label(frames[3], text="Crear Superusuario").pack()
for label, var in [("Usuario", su_user_var), ("Correo", su_email_var), ("Contraseña", su_pass_var)]:
    Label(frames[3], text=label).pack()
    Entry(frames[3], textvariable=var, show="*" if "Contraseña" in label else None).pack()
Button(frames[3], text="Crear Superusuario", command=lambda: threading.Thread(target=crear_superusuario_pro).start(), bg="blue", fg="white").pack(pady=5)
log_text = Text(frames[3], height=10)
log_text.pack(fill=BOTH, expand=True, pady=10)
Button(frames[3], text="Back", command=lambda: show_frame(2)).pack(side=LEFT,padx=50,pady=20)
Button(frames[3], text="Next", command=lambda: show_frame(4)).pack(side=RIGHT,padx=50,pady=20)
Button(frames[3], text="Salir", command=terminar_instalador, bg="red", fg="white").pack(side=BOTTOM,pady=10)

# ----------------------------
# Paso 4: Control PRO del Servidor Django
# ----------------------------
def levantar_servidor():
    global server_process
    if server_process is None:
        server_process = subprocess.Popen([venv_python, "manage.py", "runserver", "8001"])
        status_label.config(text="Servidor corriendo ✅")
        log_text.insert(END, "Servidor levantado en http://127.0.0.1:8001\n")
        log_text.see(END)
    else:
        messagebox.showinfo("Info", "El servidor ya está corriendo")

def detener_servidor():
    global server_process
    if server_process is not None:
        server_process.terminate()
        server_process = None
        status_label.config(text="Servidor detenido ❌")
        log_text.insert(END, "Servidor detenido\n")
        log_text.see(END)
    else:
        messagebox.showinfo("Info", "El servidor no está corriendo")

def reiniciar_servidor():
    detener_servidor()
    levantar_servidor()

Label(frames[4], text="Paso 4: Control de Servidor Django", font=("Arial",14,"bold")).pack(pady=20)
status_label = Label(frames[4], text="Servidor detenido ❌", font=("Arial",14))
status_label.pack(pady=20)
log_text = Text(frames[4], height=15)
log_text.pack(fill=BOTH, expand=True, pady=10)

Button(frames[4], text="Levantar Servidor", command=levantar_servidor, bg="green", fg="white").pack(pady=5)
Button(frames[4], text="Detener Servidor", command=detener_servidor, bg="red", fg="white").pack(pady=5)
Button(frames[4], text="Reiniciar Servidor", command=reiniciar_servidor, bg="orange", fg="white").pack(pady=5)
Button(frames[4], text="Back", command=lambda: show_frame(3)).pack(side=LEFT,padx=50,pady=20)
Button(frames[4], text="Finalizar", command=lambda: messagebox.showinfo("Exito","Instalador completado")).pack(side=RIGHT,padx=50,pady=20)
Button(frames[4], text="Salir", command=terminar_instalador, bg="red", fg="white").pack(side=BOTTOM,pady=10)

# ----------------------------
# Iniciar Wizard PRO
# ----------------------------
root.mainloop()
