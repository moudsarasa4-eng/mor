"""Gestión de estado del motor de jackpots: zonas auditadas y empresas registradas.

Uso:
    python3 engine/estado.py siguiente-zona
    python3 engine/estado.py marcar-zona "Hurlingham"
    python3 engine/estado.py agregar-empresa --zona Hurlingham --nombre "Acme SRL" \
        --rubro logistica --estado jackpot --motivo "18 años, ISO 9001" \
        --fuente "https://acme.com.ar" --contacto "info@acme.com.ar" --cv logistica
    python3 engine/estado.py listar
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

PROGRESO_PATH = Path(__file__).resolve().parent.parent / "progreso.json"


def cargar():
    with open(PROGRESO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar(data):
    with open(PROGRESO_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def orden_zonas(data):
    return data["zonas"]["cercana"] + data["zonas"]["media"] + data["zonas"]["extendida"]


def siguiente_zona(data):
    for z in orden_zonas(data):
        if z not in data["zonas_auditadas"]:
            return z
    return None


def cmd_siguiente_zona(args, data):
    z = siguiente_zona(data)
    print(z if z else "Todas las zonas fueron auditadas.")


def cmd_marcar_zona(args, data):
    if args.zona not in data["zonas_auditadas"]:
        data["zonas_auditadas"].append(args.zona)
    nxt = siguiente_zona(data)
    data["proxima_zona"] = nxt
    guardar(data)
    print(f"Zona '{args.zona}' marcada como auditada. Próxima zona: {nxt}")


def cmd_agregar_empresa(args, data):
    ya_existe = any(
        e["nombre"].strip().lower() == args.nombre.strip().lower()
        for e in data["empresas"]
    )
    if ya_existe:
        print(f"AVISO: '{args.nombre}' ya está registrada. No se duplica.")
        return
    entry = {
        "nombre": args.nombre,
        "zona": args.zona,
        "rubro": args.rubro,
        "estado": args.estado,  # "jackpot" | "descartada"
        "motivo": args.motivo,
        "fuente": args.fuente,
        "contacto": args.contacto or None,
        "cv_asignado": args.cv or None,
        "fecha": date.today().isoformat(),
    }
    data["empresas"].append(entry)
    guardar(data)
    print(f"Empresa '{args.nombre}' registrada como {args.estado}.")


def cmd_listar(args, data):
    for e in data["empresas"]:
        if args.zona and e["zona"] != args.zona:
            continue
        if args.estado and e["estado"] != args.estado:
            continue
        print(f"[{e['estado'].upper()}] {e['nombre']} ({e['zona']}, {e['rubro']}) - {e['motivo']}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("siguiente-zona")

    p_marcar = sub.add_parser("marcar-zona")
    p_marcar.add_argument("zona")

    p_add = sub.add_parser("agregar-empresa")
    p_add.add_argument("--zona", required=True)
    p_add.add_argument("--nombre", required=True)
    p_add.add_argument("--rubro", required=True, choices=["limpieza", "administrativo", "atencion_cliente", "logistica"])
    p_add.add_argument("--estado", required=True, choices=["jackpot", "descartada"])
    p_add.add_argument("--motivo", required=True)
    p_add.add_argument("--fuente", required=True)
    p_add.add_argument("--contacto", default=None)
    p_add.add_argument("--cv", default=None, choices=["limpieza", "administrativo", "atencion_cliente", "logistica", None])

    p_list = sub.add_parser("listar")
    p_list.add_argument("--zona", default=None)
    p_list.add_argument("--estado", default=None, choices=["jackpot", "descartada"])

    args = p.parse_args()
    data = cargar()

    if args.cmd == "siguiente-zona":
        cmd_siguiente_zona(args, data)
    elif args.cmd == "marcar-zona":
        # zona viene como positional en el parser de arriba
        args.zona = args.zona if hasattr(args, "zona") else sys.argv[2]
        cmd_marcar_zona(args, data)
    elif args.cmd == "agregar-empresa":
        cmd_agregar_empresa(args, data)
    elif args.cmd == "listar":
        cmd_listar(args, data)


if __name__ == "__main__":
    main()
