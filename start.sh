#!/usr/bin/env bash
# Motor de Jackpots — arranque para Linux/Mac.
set -e
cd "$(dirname "$0")"

if ! command -v python3 &>/dev/null; then
  echo "Python 3 no está instalado. Instalalo desde https://python.org y volvé a correr este script."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creando entorno virtual..."
  python3 -m venv .venv
fi

source .venv/bin/activate
echo "Instalando dependencias..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Se creó .env — completá SERPER_API_KEY antes de usar 'Iniciar búsqueda' (ver README.md)."
fi

python3 main.py doctor
echo ""
echo "Abriendo la app en http://127.0.0.1:5000 ... (la búsqueda arranca sola, no hace falta apretar nada)"
python3 main.py webapp
