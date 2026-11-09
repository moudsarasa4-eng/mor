#!/usr/bin/env bash
# Renderiza y normaliza el audio a -14 LUFS (video copiado sin recomprimir).
# Uso: ./render.sh <Composicion> <salida.mp4> [props.json]
set -e
cd "$(dirname "$0")"
C="$1"; OUT="$2"; P="$3"; TMP="out/_tmp_$$.mp4"; mkdir -p out
if [ -n "$P" ]; then npx remotion render "$C" "$TMP" --props="$P"; else npx remotion render "$C" "$TMP"; fi
ffmpeg -loglevel error -y -i "$TMP" -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
rm -f "$TMP"; echo "OK → $OUT"
