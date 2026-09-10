@echo off
REM Analiza TODAS las candidatas ya descubiertas y genera la lista para contactar.
REM No gasta presupuesto de busquedas. Doble click para correrlo.
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python no esta instalado. Instalalo desde https://python.org ^(marca "Add to PATH"^).
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
echo Instalando dependencias...
pip install -q -r requirements.txt

python main.py procesar-todo
echo.
echo Listo. Los archivos quedaron en tu carpeta Descargas.
pause
