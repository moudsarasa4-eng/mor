@echo off
REM Comando integral: doble click y hace todo (actualizar, instalar, procesar y exportar).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0hacer_todo.ps1"
