@echo off
REM Motor de Jackpots — arranque para Windows. Doble click para iniciar.
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python no esta instalado. Instalalo desde https://python.org ^(marca "Add to PATH"^) y volve a correr este archivo.
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

if not exist ".env" (
    copy .env.example .env
    echo Se creo .env - completa SERPER_API_KEY antes de usar "Iniciar busqueda" ^(ver README.md^).
)

python main.py doctor
echo.
echo Abriendo la app en http://127.0.0.1:5000 ...
start "" http://127.0.0.1:5000
python main.py webapp
pause
