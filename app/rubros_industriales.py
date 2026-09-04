"""Nomenclador CLAE (AFIP) — divisiones de industria manufacturera (10-33).
Nivel de división (2 dígitos): estable, público, no requiere scraping para
tenerlo (es la clasificación estándar ISIC Rev.4 / CLAE de industria).

Cada rubro se mapea a la categoría de CV más probable — la mayoría de fábricas
necesita depósito/carga y descarga (logística) o administración; se marca la
categoría secundaria más razonable para no perder casos donde el CV
administrativo encaje mejor (ej. una fábrica chica con más perfil de oficina).
"""

RUBROS_CLAE = {
    "10": "Elaboración de productos alimenticios",
    "11": "Elaboración de bebidas",
    "12": "Elaboración de productos de tabaco",
    "13": "Fabricación de productos textiles",
    "14": "Confección de prendas de vestir",
    "15": "Fabricación de cueros y productos conexos",
    "16": "Producción de madera y fabricación de productos de madera",
    "17": "Fabricación de papel y productos de papel",
    "18": "Impresión y reproducción de grabaciones",
    "19": "Fabricación de coque y productos de la refinación del petróleo",
    "20": "Fabricación de sustancias y productos químicos",
    "21": "Fabricación de productos farmacéuticos",
    "22": "Fabricación de productos de caucho y plástico",
    "23": "Fabricación de otros productos minerales no metálicos",
    "24": "Fabricación de metales comunes",
    "25": "Fabricación de productos elaborados de metal",
    "26": "Fabricación de productos informáticos, electrónicos y ópticos",
    "27": "Fabricación de equipo eléctrico",
    "28": "Fabricación de maquinaria y equipo n.c.p.",
    "29": "Fabricación de vehículos automotores, remolques y semirremolques",
    "30": "Fabricación de otros tipos de equipo de transporte",
    "31": "Fabricación de muebles",
    "32": "Otras industrias manufactureras",
    "33": "Reparación e instalación de maquinaria y equipo",
}

# Todas las fábricas necesitan depósito/carga y descarga con alta probabilidad;
# el CV logística es el default razonable. Se deja explícito para poder ajustar
# rubro por rubro si la revisión real muestra otro patrón.
CATEGORIA_POR_DEFECTO = "logistica"

PARTIDOS_DEFAULT = ["Moron", "Hurlingham", "Merlo", "Ituzaingo"]
