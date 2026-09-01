"""Test de humo: recorre el pipeline completo con datos ficticios para validar
que todos los módulos encastran (DB -> signals -> matching -> scoring -> audit -> outreach).

Uso: python3 -m pytest tests/ -v   (o simplemente python3 tests/test_pipeline.py)
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_pipeline_completo(tmp_path, monkeypatch):
    import app.db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.sqlite")
    db_module.init_db()

    from app.company import (
        upsert_company, add_source, add_signal, add_cv_match, add_contact,
        calcular_y_guardar_score,
    )
    from app.signals import Signal
    from app.scoring import EmployerInputs, Evidencia
    from app.audit import AuditChecklist, auditar
    from app.outreach import generar_outreach

    cid = upsert_company("Distribuidora Test SRL", "logistica", "Hurlingham",
                          localidad="Hurlingham", antiguedad_anios=22, tamano_estimado="grande",
                          actividad="Distribución mayorista con 3 depósitos")
    assert cid > 0

    sid = add_source(cid, "https://distribuidoratest.com.ar", tipo="sitio_propio")
    add_signal(cid, Signal(tipo="expansion_logistica", fuerza="fuerte",
                            descripcion="Nuevo depósito inaugurado en 2026", fuente_url="", fecha_evento="2026-03"))
    add_cv_match(cid, "logistica", 91, "Depósito y despacho reales en el CV")
    add_contact(cid, "email", "info@distribuidoratest.com.ar", verificado=True, fuente_id=sid)

    evidencias = [
        Evidencia("La empresa tiene 3 depósitos propios", "OBSERVADO"),
        Evidencia("Probablemente necesite personal de depósito", "INFERIDO"),
    ]
    resultado = calcular_y_guardar_score(
        cid,
        EmployerInputs(estabilidad=90, tamano=85, antiguedad=95, crecimiento=80, formalidad=88, actividad_actual=90),
        accessibility=100, contactability=100, evidencias=evidencias,
    )
    assert resultado["jackpot_score"] > 0
    assert resultado["cv_recomendado"] == "logistica"

    checklist = AuditChecklist(
        empresa_existe=True, localidad_correcta=True, fuentes_independientes=True,
        contacto_pertenece_a_empresa=True, email_publicado_por_la_empresa=True,
        experiencia_verificada_en_cv=True, sin_contradicciones=True,
        sin_señales_negativas_criticas=True, inferencia_puesto_justificada=True,
    )
    resultado_audit, fallos = auditar(cid, checklist)
    assert resultado_audit == "aprobado"
    assert fallos == []

    exp_file = tmp_path / "exp.txt"
    exp_file.write_text("Operario de logística y depósito en comercio mayorista: recepción, stock y despacho.", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    (tmp_path / "outreach").mkdir(exist_ok=True)
    import app.outreach as outreach_module
    monkeypatch.setattr(outreach_module, "OUTREACH_DIR", tmp_path / "outreach")

    archivo = generar_outreach(
        cid, "Distribuidora Test SRL", "logistica", "logistica",
        why_this_company="tiene operación logística activa y señales recientes de expansión",
        experiencia_real=exp_file.read_text(encoding="utf-8"),
    )
    assert Path(archivo).exists()
    contenido = Path(archivo).read_text(encoding="utf-8")
    assert "Marco Ammazzalorso" in contenido
    assert "recepción, stock y despacho" in contenido

    print("OK: pipeline completo validado.")


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
