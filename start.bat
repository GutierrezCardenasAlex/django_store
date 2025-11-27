@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

set "LOG=start.log"

echo ===========================
echo    INICIANDO PROYECTO
echo ===========================

REM ---------------------------------------
REM Verificar que venv exista
REM ---------------------------------------
if not exist venv (
    echo ❌ No existe el entorno virtual.
    echo Ejecuta primero: config.bat
    pause
    exit /b
)

REM ---------------------------------------
REM Activar entorno virtual
REM ---------------------------------------
call venv\Scripts\activate.bat
echo [%DATE% %TIME%] venv activado >> "%LOG%"

REM ---------------------------------------
REM Verificar archivo .env
REM ---------------------------------------
if not exist ".env" (
    echo ❌ No existe el archivo .env
    echo Ejecuta primero: config.bat
    pause
    exit /b
)


REM ---------------------------------------
REM Iniciar servidor Django
REM ---------------------------------------
echo 🚀 Iniciando servidor en 8001
echo [%DATE% %TIME%] Servidor iniciado >> "%LOG%"
python manage.py runserver 8001

echo [%DATE% %TIME%] Servidor detenido >> "%LOG%"
pause
exit /b
