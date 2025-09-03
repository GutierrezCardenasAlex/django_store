@echo off
REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Eliminar base de datos SQLite
if exist db.sqlite3 (
    echo Eliminando base de datos...
    del db.sqlite3
)

REM Eliminar archivos de migración (excepto __init__.py)
echo Eliminando migraciones...
for /d /r %%i in (*\migrations) do (
    del /q "%%i\*.py"
    del /q "%%i\*.pyc"
)

REM Volver a crear las migraciones
echo Creando nuevas migraciones...
python manage.py makemigrations

REM Aplicar migraciones
echo Aplicando migraciones...
python manage.py migrate

echo Base de datos reiniciada correctamente.
pause
