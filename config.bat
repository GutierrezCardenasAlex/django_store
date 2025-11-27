@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

set "LOG=config.log"

echo ======================================================
echo ============= CONFIGURACIÓN DEL PROYECTO =============
echo ======================================================
echo.

REM =====================================================
REM 1. Crear entorno virtual si no existe
REM =====================================================
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
    echo [%DATE% %TIME%] venv creado >> "%LOG%"
) else (
    echo ✔ Entorno virtual ya existe
)

call venv\Scripts\activate.bat
echo ✔ Entorno virtual activado
echo [%DATE% %TIME%] venv activado >> "%LOG%"

REM =====================================================
REM 2. Instalar dependencias
REM =====================================================
if exist requirements.txt (
    echo Instalando dependencias...
    pip install -q -r requirements.txt
    echo [%DATE% %TIME%] Dependencias instaladas >> "%LOG%"
) else (
    echo ⚠ No existe requirements.txt
)

REM =====================================================
REM 3. SI .env YA EXISTE — NO LO SOBRESCRIBAS
REM =====================================================
if exist ".env" (
    echo ------------------------------------------------------
    echo ✔ El archivo .env YA EXISTE
    echo    → No se sobrescribirá
    echo ------------------------------------------------------
    echo [%DATE% %TIME%] .env existente, se mantiene >> "%LOG%"
    goto MIGRAR
)

REM =====================================================
REM 4. Crear un nuevo archivo .env
REM =====================================================
echo El archivo .env NO existe. Creando nueva configuración...
echo.

echo Motor de BD:
echo [1] SQLite
echo [2] PostgreSQL
set /p motor="Elige motor (1/2): "

if "%motor%"=="1" (
    set DB_ENGINE=sqlite
    set DB_NAME=db.sqlite3
) else (
    set DB_ENGINE=postgresql
    set /p DB_HOST="Host: "
    set /p DB_PORT="Puerto (default 5432): "
    if "!DB_PORT!"=="" set DB_PORT=5432
    set /p DB_NAME="Nombre BD: "
    set /p DB_USERNAME="Usuario BD: "
    set /p DB_PASS="Password BD: "
)

REM SECRET KEY
set "chars=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
set "SECRET_KEY="
for /l %%i in (1,1,50) do (
    set /a "rand=!random! %% 72"
    set "SECRET_KEY=!SECRET_KEY!!chars:~%rand%,1!"
)

set /p ALLOWED_HOSTS="ALLOWED_HOSTS (ej: localhost,127.0.0.1): "
if "!ALLOWED_HOSTS!"=="" set ALLOWED_HOSTS=localhost

(
echo DEBUG=True
echo SECRET_KEY=!SECRET_KEY!
echo DB_ENGINE=!DB_ENGINE!
echo DB_HOST=!DB_HOST!
echo DB_PORT=!DB_PORT!
echo DB_NAME=!DB_NAME!
echo DB_USERNAME=!DB_USERNAME!
echo DB_PASS=!DB_PASS!
echo ALLOWED_HOSTS=!ALLOWED_HOSTS!
) > ".env"

echo ✔ Archivo .env creado exitosamente
echo [%DATE% %TIME%] Nuevo .env creado >> "%LOG%"

REM Carpetas
if not exist media mkdir media
if not exist static mkdir static
echo ✔ Carpetas media y static creadas
echo [%DATE% %TIME%] Carpetas creadas >> "%LOG%"

REM =====================================================
REM 5. APLICAR MIGRACIONES SIEMPRE
REM =====================================================
:MIGRAR
cls
echo ======================================================
echo           🔄 Aplicando migraciones de Django...
echo ======================================================
echo [%DATE% %TIME%] Migraciones iniciadas >> "%LOG%"

python manage.py makemigrations
python manage.py migrate

echo [%DATE% %TIME%] Migraciones completadas >> "%LOG%"
echo ✔ Migraciones aplicadas correctamente
echo.

REM =====================================================
REM 6. CREAR SUPERUSUARIO
REM =====================================================
:CREAR_SUPER
echo ======================================================
echo ¿Deseas crear un SUPERUSUARIO ahora?
echo ======================================================
set /p CREAR_SU="Crear superusuario? (Y/N): "

if /I "%CREAR_SU%"=="Y" goto SUPERUSER
goto FIN_CONFIG

:SUPERUSER
cls
echo ======================================================
echo            CREACIÓN DE SUPERUSUARIO
echo ======================================================
set /p SU_USER="Usuario: "
set /p SU_EMAIL="Correo: "
set /p SU_PASS="Contraseña: "

python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.create_superuser('%SU_USER%','%SU_EMAIL%','%SU_PASS%') if not User.objects.filter(username='%SU_USER%').exists() else print('Ya existe')"

echo ✔ Superusuario creado
echo [%DATE% %TIME%] Superusuario creado: %SU_USER% >> "%LOG%"
echo.

:FIN_CONFIG
echo ======================================================
echo        CONFIGURACIÓN COMPLETADA
echo ======================================================
pause
exit /b
