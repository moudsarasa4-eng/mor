"""Extrae el texto de los 4 CVs en PDF (carpeta cvs/) a archivos .txt para uso del motor.

Uso:
    python3 app/leer_cvs.py
"""
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        PdfReader = None

CVS_DIR = Path(__file__).resolve().parent.parent / "cvs"

ARCHIVOS = {
    "limpieza": "cv_limpieza.pdf",
    "administrativo": "cv_administrativo.pdf",
    "atencion_cliente": "cv_atencion_cliente.pdf",
    "logistica": "cv_logistica.pdf",
}


def extraer_texto(pdf_path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError("Instalá pypdf: pip install pypdf")
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def main():
    faltantes = []
    for clave, nombre_archivo in ARCHIVOS.items():
        pdf_path = CVS_DIR / nombre_archivo
        if not pdf_path.exists():
            faltantes.append(nombre_archivo)
            continue
        texto = extraer_texto(pdf_path)
        out_path = CVS_DIR / f"{clave}.txt"
        out_path.write_text(texto, encoding="utf-8")
        print(f"OK: {nombre_archivo} -> {out_path.name} ({len(texto)} caracteres)")

    if faltantes:
        print("\nFaltan estos PDFs en la carpeta cvs/:")
        for f in faltantes:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
