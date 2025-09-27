@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

set "LOG=panel_django.log"

REM =====================================================
REM PANEL DJANGO PRO AMIGABLE - AUTOREFRESH + LOG
REM =====================================================

REM ----------------------------
REM Activar entorno virtual y dependencias
REM ----------------------------
if not exist venv (
    echo [%DATE% %TIME%] Creando entorno virtual... >> "%LOG%"
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [%DATE% %TIME%] Entorno virtual activado >> "%LOG%"

if exist requirements.txt (
    echo 📦 Instalando dependencias...
    echo [%DATE% %TIME%] Instalando dependencias desde requirements.txt >> "%LOG%"
    pip install -q -r requirements.txt
)

REM ----------------------------
REM Comenzar monitoreo automático
REM ----------------------------
goto AUTO_MONITOR

:AUTO_MONITOR
cls
call :DIAGNOSTICO

if "!TODO_OK!"=="1" (
    echo ✅ Todo está LISTO. Arrancando servidor automáticamente...
    echo [%DATE% %TIME%] Todo listo, arrancando servidor automáticamente >> "%LOG%"
    timeout /t 2 >nul
    python manage.py runserver 8001
    echo [%DATE% %TIME%] Servidor detenido >> "%LOG%"
    goto FIN
)

echo ⚠️ Faltan configuraciones.
echo Presiona [M] para abrir el menú o [S] para salir. Esperando 5 segundos...
choice /c MS /n /t 5 /d M >nul
if errorlevel 2 goto FIN
goto MENU

:MENU
cls
call :DIAGNOSTICO
echo =============================== 
echo      PANEL DJANGO PRO AMIGABLE
echo ===============================
echo 1. Configurar proyecto (.env + BD + carpetas)
echo 2. Aplicar migraciones
echo 3. Crear superusuario
echo 4. Levantar servidor manualmente
echo 5. Apagar servidor
echo 6. Ver log de eventos
echo 7. Volver al monitoreo automático
echo 0. Salir
echo ===============================
set /p opcion="Elige opción: "

if "%opcion%"=="1" call :CONFIGURAR_ENV & goto MENU
if "%opcion%"=="2" call :MIGRAR & goto MENU
if "%opcion%"=="3" call :SUPERUSUARIO & goto MENU
if "%opcion%"=="4" call :LEVANTAR & goto MENU
if "%opcion%"=="5" call :APAGAR & goto MENU
if "%opcion%"=="6" type "%LOG%" & pause & goto MENU
if "%opcion%"=="7" goto AUTO_MONITOR
if "%opcion%"=="0" goto FIN
goto MENU

:DIAGNOSTICO
set "TODO_OK=1"
set "COLOR_LISTO=2"
set "COLOR_FALTA=4"

REM 1. Entorno virtual
if exist venv (set "VENV=LISTO" & set "VENV_COLOR=!COLOR_LISTO!") else (set "VENV=FALTA" & set "VENV_COLOR=!COLOR_FALTA!" & set TODO_OK=0)
if defined VIRTUAL_ENV (set "VENV_ACT=LISTO" & set "VENV_ACT_COLOR=!COLOR_LISTO!") else (set "VENV_ACT=FALTA" & set "VENV_ACT_COLOR=!COLOR_FALTA!")

REM 2. .env
if exist ".env" (set "ENV=LISTO" & set "ENV_COLOR=!COLOR_LISTO!") else (set "ENV=FALTA" & set "ENV_COLOR=!COLOR_FALTA!" & set TODO_OK=0)

REM 3. Migraciones pendientes
set "MIG=LISTO" & set "MIG_COLOR=!COLOR_LISTO!"
for /f "delims=" %%i in ('python manage.py showmigrations ^| findstr "\[ \]" 2^>nul') do (set "MIG=PENDIENTE" & set "MIG_COLOR=!COLOR_FALTA!" & set TODO_OK=0)

REM 4. Servidor corriendo
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if %errorlevel%==0 (set "SERVER=LISTO" & set "SERVER_COLOR=!COLOR_LISTO!") else (set "SERVER=FALTA" & set "SERVER_COLOR=!COLOR_FALTA!")

REM Mostrar tablero
echo =============================== ESTADO DEL SISTEMA ===============================
call :COLOR !VENV_COLOR! & echo VENV:            !VENV!
call :COLOR !VENV_ACT_COLOR! & echo VENV activo:     !VENV_ACT!
call :COLOR !ENV_COLOR! & echo Config .ENV:       !ENV!
call :COLOR !MIG_COLOR! & echo Migraciones:      !MIG!
call :COLOR !SERVER_COLOR! & echo Servidor:        !SERVER!
call :COLOR 7
echo ================================================================================
if "!TODO_OK!"=="1" (
    call :COLOR !COLOR_LISTO!
    echo ✅ TODO LISTO - Sistema puede iniciar automáticamente
) else (
    call :COLOR !COLOR_FALTA!
    echo ⚠️ SISTEMA CON PENDIENTES - Completa lo faltante
)
call :COLOR 7
echo.
goto :EOF

:COLOR
if "%1"=="2" color 0A
if "%1"=="4" color 0C
if "%1"=="7" color 07
goto :EOF

:CONFIGURAR_ENV
cls
echo =============================== CONFIGURAR PROYECTO ===============================
echo.

REM ----------------------------
REM Elegir motor de base de datos
REM ----------------------------
echo Selecciona el motor de base de datos:
echo [1] SQLite
echo [2] PostgreSQL
set /p motor="Elige una opcion (1/2): "

if "%motor%"=="1" (
    set DB_ENGINE=sqlite
    set DB_NAME=db.sqlite3
) else (
    set DB_ENGINE=postgresql
    set /p DB_HOST="Host: "
    set /p DB_PORT="Puerto (default 5432): "
    if "!DB_PORT!"=="" set DB_PORT=5432
    set /p DB_NAME="Nombre de la BD: "
    set /p DB_USERNAME="Usuario: "
    set /p DB_PASS="Password: "
)

REM ----------------------------
REM Generar SECRET_KEY aleatoria
REM ----------------------------
set "chars=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
set "SECRET_KEY="
for /l %%i in (1,1,50) do set /a "rand=!random! %% 72" & set "SECRET_KEY=!SECRET_KEY!!chars:~%rand%,1!"

REM ----------------------------
REM Configurar ALLOWED_HOSTS
REM ----------------------------
echo.
echo Configurar ALLOWED_HOSTS para Django
set /p ALLOWED_HOSTS="Introduce hosts separados por coma (ej: localhost,127.0.0.1): "
if "!ALLOWED_HOSTS!"=="" set ALLOWED_HOSTS=localhost

REM ----------------------------
REM Crear .env
REM ----------------------------
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

REM ----------------------------
REM Crear carpetas media y static
REM ----------------------------
if not exist media mkdir media
if not exist static mkdir static

echo [%DATE% %TIME%] Configuración completada, .env creado y carpetas listas >> "%LOG%"
echo ✅ Configuración completada, .env y carpetas creadas
pause
goto :EOF

:MIGRAR
cls
echo 🔄 Aplicando migraciones...
echo [%DATE% %TIME%] Iniciando migraciones >> "%LOG%"
python manage.py makemigrations || (echo [%DATE% %TIME%] ❌ Error en makemigrations >> "%LOG%" & echo ❌ Error)
python manage.py migrate || (echo [%DATE% %TIME%] ❌ Error en migrate >> "%LOG%" & echo ❌ Error)
echo [%DATE% %TIME%] Migraciones completadas >> "%LOG%"
echo ✅ Migraciones finalizadas
pause
goto :EOF

:SUPERUSUARIO
cls
set /p SU_USER="Usuario: "
set /p SU_EMAIL="Correo: "
set /p SU_PASS="Contraseña: "
echo [%DATE% %TIME%] Creando superusuario %SU_USER% >> "%LOG%"
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.create_superuser('%SU_USER%','%SU_EMAIL%','%SU_PASS%') if not User.objects.filter(username='%SU_USER%').exists() else print('Ya existe')"
echo [%DATE% %TIME%] Superusuario %SU_USER% creado >> "%LOG%"
pause
goto :EOF

:LEVANTAR
cls
echo 🚀 Levantando servidor manualmente...
echo [%DATE% %TIME%] Servidor levantado manualmente >> "%LOG%"
python manage.py runserver 8001
echo [%DATE% %TIME%] Servidor detenido >> "%LOG%"
pause
goto :EOF

:APAGAR
cls
echo ⛔ Deteniendo servidor...
taskkill /F /IM python.exe >nul 2>&1
echo [%DATE% %TIME%] Servidor detenido manualmente >> "%LOG%"
echo ✅ Servidor detenido
pause
goto :EOF

:FIN
echo 👋 Saliendo del panel...
echo [%DATE% %TIME%] Salida del sistema >> "%LOG%"
endlocal
exit /b
