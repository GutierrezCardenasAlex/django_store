@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

REM =====================================================
REM  PANEL DJANGO PREMIUM - ESTABLE Y COLORIDO
REM =====================================================

call :INICIO
goto MENU

:INICIO
REM Crear/activar venv
if not exist venv python -m venv venv
call venv\Scripts\activate.bat

REM Instalar dependencias si existe requirements.txt
if exist requirements.txt pip install -q -r requirements.txt

call :DIAGNOSTICO
goto :EOF

:MENU
cls
call :DIAGNOSTICO

echo =============================== 
echo      PANEL DJANGO PREMIUM
echo ===============================
echo 1. Inicializar proyecto (.env + migraciones)
echo 2. Migraciones
echo 3. Crear superusuario
echo 4. Levantar servidor
echo 5. Apagar servidor
echo 0. Salir
echo ===============================
set /p opcion="Elige opción: "

if "%opcion%"=="1" goto INICIALIZAR
if "%opcion%"=="2" goto MIGRAR
if "%opcion%"=="3" goto SUPERUSUARIO
if "%opcion%"=="4" goto LEVANTAR
if "%opcion%"=="5" goto APAGAR
if "%opcion%"=="0" exit /b
goto MENU

:DIAGNOSTICO
set "TODO_OK=1"

REM Colores de texto: 2=verde,4=rojo,7=blanco
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
cls
echo =============================== PANEL DJANGO ===============================
call :COLOR !VENV_COLOR! & echo VENV:            !VENV!
call :COLOR !VENV_ACT_COLOR! & echo VENV activo:     !VENV_ACT!
call :COLOR !ENV_COLOR! & echo Config .ENV:       !ENV!
call :COLOR !MIG_COLOR! & echo Migraciones:      !MIG!
call :COLOR !SERVER_COLOR! & echo Servidor:        !SERVER!
call :COLOR 7
echo ============================================================================

if "!TODO_OK!"=="1" (
    call :COLOR !COLOR_LISTO!
    echo ✅ SISTEMA LISTO PARA USAR
) else (
    call :COLOR !COLOR_FALTA!
    echo ⚠️ SISTEMA CON PENDIENTES - Revisa los items en rojo
)
call :COLOR 7
echo.
goto :EOF

:COLOR
REM Cambiar color de texto
if "%1"=="2" color 0A
if "%1"=="4" color 0C
if "%1"=="7" color 07
goto :EOF

:INICIALIZAR
cls
if not exist ".env" call :CONFIGURAR_ENV
call :MIGRAR
pause
goto MENU

:CONFIGURAR_ENV
set "chars=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
set "SECRET_KEY="
for /l %%i in (1,1,50) do set /a "rand=!random! %% 72" & set "SECRET_KEY=!SECRET_KEY!!chars:~%rand%,1!"
(
echo DEBUG=True
echo SECRET_KEY=!SECRET_KEY!
echo ALLOWED_HOSTS=localhost
) > .env
if not exist media mkdir media
if not exist static mkdir static
echo ✅ .env y carpetas creadas
goto :EOF

:MIGRAR
cls
echo 🔄 Aplicando migraciones...
python manage.py makemigrations 2>nul
if %errorlevel% neq 0 echo ❌ Error al generar migraciones
python manage.py migrate 2>nul
if %errorlevel% neq 0 echo ❌ Error al aplicar migraciones
echo ✅ Migraciones finalizadas
pause
goto :EOF

:SUPERUSUARIO
cls
set /p SU_USER="Usuario: "
set /p SU_EMAIL="Correo: "
set /p SU_PASS="Contraseña: "
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.create_superuser('%SU_USER%','%SU_EMAIL%','%SU_PASS%') if not User.objects.filter(username='%SU_USER%').exists() else print('Ya existe')"
pause
goto MENU

:LEVANTAR
cls
echo 🚀 Levantando servidor...
python manage.py runserver 8001
pause
goto MENU

:APAGAR
cls
echo ⛔ Deteniendo servidor...
taskkill /F /IM python.exe >nul 2>&1
echo ✅ Servidor detenido
pause
goto MENU
