"""CV_MATCH_ENGINE — calcula compatibilidad entre las necesidades inferidas de una
empresa y cada uno de los 4 CVs de Marco, con justificación explícita.

No inventa: las "necesidades" y los "indicadores del CV" deben ingresarse a mano
(por Claude, durante la investigación) a partir de datos reales de la empresa y
del texto real del CV — este módulo solo calcula el score y arma la explicación.
"""
from dataclasses import dataclass, field

CVS = ["limpieza", "administrativo", "atencion_cliente", "logistica"]

# Palabras clave típicas de cada CV, usadas solo como ayuda de superposición léxica.
# El score real depende de las "necesidades" y "evidencias" que se pasan explícitamente.
KEYWORDS_CV = {
    "limpieza": {"limpieza", "desinfeccion", "higiene", "riesgo_biologico", "hospitalaria"},
    "administrativo": {"caja", "stock", "administracion", "atencion_publico", "comercio"},
    "atencion_cliente": {"atencion_publico", "trato_cliente", "caja", "mostrador"},
    "logistica": {"deposito", "expedicion", "recepcion", "stock", "carga_descarga", "excel"},
}


@dataclass
class MatchResult:
    cv: str
    score: int
    justificacion: str
    evidencias_usadas: list[str] = field(default_factory=list)


def calcular_match(necesidades_empresa: list[str], evidencias_cv: dict[str, list[str]]) -> list[MatchResult]:
    """
    necesidades_empresa: lista de necesidades inferidas de la empresa, ej.
        ["deposito", "expedicion", "recepcion", "stock", "carga_descarga", "administracion_logistica"]
    evidencias_cv: dict cv -> lista de frases/ítems REALES tomados del CV que cubren
        alguna de esas necesidades, ej.
        {"logistica": ["operario de depósito y carga/descarga en Arcos Dorados",
                        "recepción, stock y despacho en comercio mayorista"]}
    """
    necesidades = set(necesidades_empresa)
    resultados = []
    for cv in CVS:
        evidencias = evidencias_cv.get(cv, [])
        keywords_cv = KEYWORDS_CV[cv]
        cubiertas = necesidades & keywords_cv
        cobertura = len(cubiertas) / max(1, len(necesidades))
        tiene_evidencia_real = len(evidencias) > 0

        if not tiene_evidencia_real:
            score = 0
            justificacion = f"Sin evidencia concreta en el CV de {cv} para estas necesidades."
        else:
            score = round(cobertura * 70 + min(30, len(evidencias) * 10))
            score = min(100, score)
            necesidades_txt = ", ".join(sorted(cubiertas)) if cubiertas else "necesidades generales del rubro"
            justificacion = (
                f"CV {cv} cubre {necesidades_txt} con evidencia real: "
                + "; ".join(evidencias)
            )

        resultados.append(MatchResult(cv=cv, score=score, justificacion=justificacion, evidencias_usadas=evidencias))

    resultados.sort(key=lambda r: r.score, reverse=True)
    return resultados


def mejor_cv(resultados: list[MatchResult]) -> MatchResult:
    return resultados[0]
