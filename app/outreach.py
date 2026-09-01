"""Outreach Writer — genera el email + WHY_THIS_COMPANY solo para empresas que
pasaron auditoría, usando experiencia REAL del CV (nunca inventada) y sin afirmar
que existe una vacante.
"""
import re
from datetime import date
from pathlib import Path

from app.db import get_conn, now

BASE_DIR = Path(__file__).resolve().parent.parent
OUTREACH_DIR = BASE_DIR / "outreach"

RUBROS_LEGIBLES = {
    "limpieza": "tareas de limpieza",
    "administrativo": "tareas administrativas",
    "atencion_cliente": "atención al cliente",
    "logistica": "logística y depósito",
}

PLANTILLA = """Asunto: Postulación espontánea - {rubro_legible}

Hola,

Mi nombre es Marco Ammazzalorso y vivo en Hurlingham, Provincia de Buenos Aires. Les escribo de forma espontánea porque {why_this_company_frase}

{experiencia}

Quisiera acercarles mi CV para ser tenido en cuenta ante futuras búsquedas relacionadas con {rubro_legible}. Quedo a disposición para enviarlo completo y coordinar una entrevista cuando les resulte conveniente.

Saludos cordiales,
Marco Ammazzalorso
"""


def slug(texto: str) -> str:
    texto = texto.strip().lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def generar_outreach(company_id: int, nombre_empresa: str, rubro: str, cv: str,
                      why_this_company: str, experiencia_real: str) -> str:
    if not experiencia_real.strip():
        raise ValueError("No se genera outreach sin experiencia real tomada del CV.")

    rubro_legible = RUBROS_LEGIBLES[rubro]
    why_frase = why_this_company.strip().rstrip(".") + "."
    email_texto = PLANTILLA.format(
        rubro_legible=rubro_legible,
        why_this_company_frase=why_frase[0].lower() + why_frase[1:],
        experiencia=experiencia_real.strip(),
    )

    hoy = date.today().isoformat()
    OUTREACH_DIR.mkdir(exist_ok=True)
    archivo = OUTREACH_DIR / f"{slug(nombre_empresa)}_{hoy}.md"
    contenido = f"""# {nombre_empresa}

- **CV usado:** {cv}
- **Fecha:** {hoy}

## Why this company
{why_this_company}

## Email listo para enviar

```
{email_texto}
```
"""
    archivo.write_text(contenido, encoding="utf-8")

    conn = get_conn()
    conn.execute(
        "INSERT INTO outreach (company_id, cv_usado, why_this_company, email_texto, archivo_md, estado, creado_en, actualizado_en) "
        "VALUES (?, ?, ?, ?, ?, 'generado', ?, ?)",
        (company_id, cv, why_this_company, email_texto, str(archivo), now(), now()),
    )
    conn.commit()
    conn.close()

    return str(archivo)


def actualizar_estado_outreach(outreach_id: int, nuevo_estado: str):
    """nuevo_estado en: generado, enviado, respondio, entrevista, rechazo, no_respondio, contratacion"""
    conn = get_conn()
    conn.execute(
        "UPDATE outreach SET estado=?, actualizado_en=? WHERE id=?",
        (nuevo_estado, now(), outreach_id),
    )
    conn.commit()
    conn.close()
