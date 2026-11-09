#!/usr/bin/env bash
# Uso: ./nuevo-cliente.sh nombre-del-negocio
set -e
[ -z "$1" ] && { echo "Uso: $0 nombre-del-negocio"; exit 1; }
D="$(dirname "$0")"; N="$1"
[ -e "$D/$N" ] && { echo "Ya existe $D/$N"; exit 1; }
cp -r "$D/_plantilla" "$D/$N"
mkdir -p "$D/../plantillas/remotion/public/clientes/$N"
sed -i "s/NEGOCIO/$N/g" "$D/$N/reel-01.json"
echo "Listo: clientes/$N. Fotos/clips del cliente → plantillas/remotion/public/clientes/$N/"
