"""Genera el archivo outreach/[empresa]_[fecha].md a partir de datos de una empresa
YA APROBADA por el usuario y el fragmento de CV real correspondiente.

Este script NO busca empresas, NO envía nada y NO inventa experiencia: el texto de
experiencia se pasa a mano (copiado literal del CV) para evitar cualquier invención.

Uso:
    python3 engine/generar_email.py \
        --empresa "Acme SRL" \
        --rubro logistica \
        --zona Hurlingham \
        --motivo-seriedad "18 años en el rubro, planta propia, certificación ISO 9001" \
        --fuente "https://acme.com.ar/nosotros" \
        --contacto "info@acme.com.ar" \
        --cv logistica \
        --experiencia-file cvs/experiencia_logistica_snippet.txt
"""
import argparse
import re
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTREACH_DIR = BASE_DIR / "outreach"

PLANTILLA_EMAIL = """Asunto: Postulación espontánea - {rubro_legible}

Hola,

Mi nombre es Marco Ammazzalorso y vivo en Hurlingham, Provincia de Buenos Aires. Les escribo de forma espontánea porque conozco {empresa} y me gustaría postularme para eventuales búsquedas relacionadas con {rubro_legible}.

{experiencia}

Quedo a disposición para enviar mi CV completo y coordinar una entrevista cuando les resulte conveniente.

Saludos cordiales,
Marco Ammazzalorso
"""

RUBROS_LEGIBLES = {
    "limpieza": "tareas de limpieza",
    "administrativo": "tareas administrativas",
    "atencion_cliente": "atención al cliente",
    "logistica": "logística y depósito",
}


def slug(texto: str) -> str:
    texto = texto.strip().lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--empresa", required=True)
    p.add_argument("--rubro", required=True, choices=list(RUBROS_LEGIBLES.keys()))
    p.add_argument("--zona", required=True)
    p.add_argument("--motivo-seriedad", required=True)
    p.add_argument("--fuente", required=True)
    p.add_argument("--contacto", required=True)
    p.add_argument("--cv", required=True, choices=list(RUBROS_LEGIBLES.keys()))
    p.add_argument("--experiencia-file", required=True,
                    help="Archivo de texto con 2-3 líneas de experiencia REAL, copiadas literal del CV.")
    args = p.parse_args()

    exp_path = Path(args.experiencia_file)
    if not exp_path.exists():
        raise SystemExit(f"No existe el archivo de experiencia: {exp_path}")
    experiencia = exp_path.read_text(encoding="utf-8").strip()
    if not experiencia:
        raise SystemExit("El archivo de experiencia está vacío. No se genera el email sin contenido real del CV.")

    rubro_legible = RUBROS_LEGIBLES[args.rubro]
    email_texto = PLANTILLA_EMAIL.format(
        rubro_legible=rubro_legible,
        empresa=args.empresa,
        experiencia=experiencia,
    )

    hoy = date.today().isoformat()
    nombre_archivo = f"{slug(args.empresa)}_{hoy}.md"
    OUTREACH_DIR.mkdir(exist_ok=True)
    out_path = OUTREACH_DIR / nombre_archivo

    contenido = f"""# {args.empresa}

- **Zona:** {args.zona}
- **Rubro:** {rubro_legible}
- **Por qué es seria:** {args.motivo_seriedad}
- **Fuente de verificación:** {args.fuente}
- **Contacto usado:** {args.contacto}
- **CV asignado:** {args.cv}
- **Fecha:** {hoy}

## Email listo para enviar

```
{email_texto}
```
"""
    out_path.write_text(contenido, encoding="utf-8")
    print(f"Generado: {out_path}")


if __name__ == "__main__":
    main()
