"""Datos de negocio (espejo del frontend): 30 trabajos + speechs + clasificador.

Fuentes: Home Solution / iProfesional / Servidos (2026) + AEA 90364.
Los `mn`/`mx` en None son "s/d" (sin dato de precio): no se inventan precios.
"""

# r=rank, n=nombre, mn/mx=precio ref (ARS), tmin/tmax=tiempo (min)
CATALOGO_30 = [
    {"r": 1, "n": "Búsqueda y reparación de cortocircuito", "mn": 57974, "mx": 91865, "tmin": 60, "tmax": 180},
    {"r": 2, "n": "Cambio/instalación de térmica (termomagnética)", "mn": 22367, "mx": 41465, "tmin": 20, "tmax": 40},
    {"r": 3, "n": "Cambio/instalación de disyuntor diferencial", "mn": 26274, "mx": 47775, "tmin": 30, "tmax": 45},
    {"r": 4, "n": "Instalación de boca eléctrica completa", "mn": 29436, "mx": 58746, "tmin": 60, "tmax": 120},
    {"r": 5, "n": "Colocación/cambio de tomacorriente", "mn": 13916, "mx": 24435, "tmin": 15, "tmax": 30},
    {"r": 6, "n": "Visita de diagnóstico / presupuestación", "mn": 25577, "mx": 71101, "tmin": 30, "tmax": 60},
    {"r": 7, "n": "Instalación eléctrica para aire acondicionado", "mn": 46161, "mx": 97327, "tmin": 90, "tmax": 180},
    {"r": 8, "n": "Colocación de artefactos de iluminación", "mn": 16051, "mx": 183753, "tmin": 30, "tmax": 90},
    {"r": 9, "n": "Instalación de termotanque eléctrico", "mn": 52392, "mx": 135591, "tmin": 90, "tmax": 180},
    {"r": 10, "n": "Instalación de cocina eléctrica", "mn": 34034, "mx": 83435, "tmin": 90, "tmax": 180},
    {"r": 11, "n": "Instalación de anafe eléctrico", "mn": 30992, "mx": 59434, "tmin": 60, "tmax": 120},
    {"r": 12, "n": "Instalación de horno eléctrico", "mn": 51968, "mx": 96347, "tmin": 90, "tmax": 150},
    {"r": 13, "n": "Instalación de estufa eléctrica", "mn": 45426, "mx": 59873, "tmin": 60, "tmax": 120},
    {"r": 14, "n": "Ventilador de techo con luces", "mn": 47068, "mx": 75783, "tmin": 90, "tmax": 150},
    {"r": 15, "n": "Ventilador de techo (sin luces)", "mn": 43045, "mx": 71862, "tmin": 60, "tmax": 120},
    {"r": 16, "n": "Cambio de tecla/interruptor de pared", "mn": 18707, "mx": None, "tmin": 20, "tmax": 40},
    {"r": 17, "n": "Puesta a tierra / jabalina", "mn": 57441, "mx": 121359, "tmin": 90, "tmax": 180},
    {"r": 18, "n": "Medición de resistencia a tierra (telurómetro)", "mn": None, "mx": None, "tmin": 30, "tmax": 45},
    {"r": 19, "n": "Armado/cambio de tablero (4-6 circuitos)", "mn": 155000, "mx": 310000, "tmin": 180, "tmax": 360},
    {"r": 20, "n": "Certificado DCI", "mn": 149036, "mx": 266951, "tmin": 120, "tmax": 240},
    {"r": 21, "n": "Trámites de conexión (distribuidora)", "mn": 114704, "mx": 159596, "tmin": 30, "tmax": 60},
    {"r": 22, "n": "Instalación de portero eléctrico", "mn": 38329, "mx": 165932, "tmin": 120, "tmax": 300},
    {"r": 23, "n": "Instalación de detector de humo", "mn": 33657, "mx": 73912, "tmin": 30, "tmax": 45},
    {"r": 24, "n": "Campana de extracción (conexión eléctrica)", "mn": 46092, "mx": 97734, "tmin": 90, "tmax": 180},
    {"r": 25, "n": "Colocación de pararrayos", "mn": None, "mx": None, "tmin": 240, "tmax": 480},
    {"r": 26, "n": "Instalación de alarma", "mn": None, "mx": None, "tmin": 180, "tmax": 360},
    {"r": 27, "n": "Instalación de cámaras de seguridad", "mn": None, "mx": None, "tmin": 180, "tmax": 360},
    {"r": 28, "n": "Instalación de cerco eléctrico", "mn": None, "mx": None, "tmin": 240, "tmax": 480},
    {"r": 29, "n": "Llaves inteligentes / domótica básica", "mn": None, "mx": None, "tmin": 45, "tmax": 90},
    {"r": 30, "n": "Cargador de auto eléctrico (wallbox)", "mn": None, "mx": None, "tmin": 120, "tmax": 240},
]

CATALOGO_POR_RANK = {t["r"]: t for t in CATALOGO_30}

# Speechs por trabajo (speech + preguntas + upsells). rank refiere al CATALOGO_30.
SPEECHS = [
    {"rank": 1, "nombre": "Cortocircuito / diagnóstico",
     "preguntas": ["¿Hay olor a quemado o marcas visibles (chispas, negro)?", "¿Es reciente o intermitente hace tiempo?", "¿En qué zona de la casa se nota más?"],
     "upsells": ["Reemplazo del tramo de cableado afectado.", "Revisión preventiva del resto de la instalación.", "Informe técnico de la falla (seguro/alquiler)."]},
    {"rank": 2, "nombre": "Salta la térmica / el disyuntor",
     "preguntas": ["¿Térmica o disyuntor?", "¿Coincide con un aparato puntual o es al azar?", "¿El tablero es viejo o ya renovado?"],
     "upsells": ["Circuito exclusivo para el aparato que sobrecarga.", "Revisión general del tablero.", "Diferencial 10mA como mejora OPCIONAL en baño con bañera (la norma exige 30mA en toda la casa)."]},
    {"rank": 4, "nombre": "Boca eléctrica / ampliar tomas",
     "preguntas": ["¿Cuántas bocas y de qué tipo?", "¿El circuito existente tiene lugar o hay que armar uno nuevo?", "¿Pared de material o durlock?"],
     "upsells": ["Tomas con USB integrado.", "Circuito independiente para la zona nueva.", "Llaves con control por wifi (domótica básica)."]},
    {"rank": 7, "nombre": "Instalación para aire acondicionado",
     "preguntas": ["¿Cuántas frigorías/BTU?", "¿Ya está instalado el equipo o va todo junto?", "¿El tablero tiene lugar?"],
     "upsells": ["Llave térmica dedicada + diferencial si falta.", "Estabilizador de tensión (protege el compresor).", "Preinstalación para un segundo equipo."]},
    {"rank": 6, "nombre": "Visita de diagnóstico / presupuesto",
     "preguntas": ["¿Qué problema específico tenés?", "¿Es la primera vez que llamás por esto?", "¿Podés mandar una foto del tablero/zona?"],
     "upsells": ["Paquete de revisión preventiva anual.", "Certificación si el motivo real es un trámite.", "Presupuesto de obra completa si aparece algo mayor."]},
    {"rank": 8, "nombre": "Artefactos de iluminación",
     "preguntas": ["¿Cuántos artefactos y en qué ambientes?", "¿Reemplazo o punto nuevo?", "¿Tenés los artefactos o necesitás asesoramiento?"],
     "upsells": ["Cambio a LED (ahorra consumo).", "Dimmer para regular intensidad.", "Sensor de movimiento/crepuscular."]},
    {"rank": 9, "nombre": "Termotanque eléctrico",
     "preguntas": ["¿Qué potencia tiene el termotanque?", "¿Hay punto eléctrico ya hecho o es nuevo?", "¿Reemplazo o primera instalación?"],
     "upsells": ["Térmica y cable dimensionados a la potencia real.", "Diferencial específico para el circuito.", "Revisión de la puesta a tierra (crítica con agua)."]},
    {"rank": 10, "nombre": "Cocina eléctrica",
     "preguntas": ["¿Qué potencia tiene la cocina/horno?", "¿El tablero tiene módulos libres?", "¿Cambio de gas a eléctrica o ya había eléctrica?"],
     "upsells": ["Actualización del tablero si no tiene lugar.", "Revisión de la acometida/medidor.", "Circuito adicional para horno empotrado a futuro."]},
    {"rank": 14, "nombre": "Ventilador de techo con luz",
     "preguntas": ["¿Reemplaza una lámpara o es punto nuevo?", "¿Techo de losa o liviano (necesita refuerzo)?", "¿Control por cadena, pared o remoto?"],
     "upsells": ["Llave con dimmer + control de velocidad.", "Refuerzo estructural del punto de fijación.", "Cotizar otro ventilador en la misma visita."]},
    {"rank": 19, "nombre": "Tablero nuevo / renovación",
     "preguntas": ["¿Cuántos circuitos tiene la casa hoy?", "¿Es para uso general o necesitás certificación?", "¿Hay puesta a tierra instalada?"],
     "upsells": ["Puesta a tierra si no existe.", "Certificación técnica con informe.", "Protección contra sobretensiones."]},
    {"rank": 17, "nombre": "Puesta a tierra / jabalina",
     "preguntas": ["¿La casa es antigua (+15-20 años) sin reformas?", "¿Es por un trámite o por seguridad general?", "¿Tenés patio/jardín con tierra accesible?"],
     "upsells": ["Medición de resistencia con informe.", "Revisión del diferencial existente.", "Actualización de tablero si es muy viejo."]},
]

SPEECH_POR_RANK = {s["rank"]: s for s in SPEECHS}

# Emergencia (chispas / quemado / calor) y clasificador por lenguaje real.
EMERGENCIA_CLAVES = ["quemado", "olor a quemado", "huele a quemado", "chispa", "chispas",
                     "humo", "fuego", "arde", "se calienta", "calienta", "caliente al tacto",
                     "descarga", "calambre"]

# Síntomas de falla primero (no confundir "la luz de la cocina" con "cocina eléctrica").
CLASIFICADOR = [
    {"claves": ["corto", "cortocircuito", "corto circuito"], "rank": 1, "urg": "ALTA"},
    {"claves": ["salta la termica", "salta la llave", "salta el disyuntor", "salta el diferencial",
                "se baja la llave", "salta la luz", "se corta la proteccion", "salta", "disyuntor",
                "diferencial", "termica"], "rank": 2, "urg": "MEDIA"},
    {"claves": ["no vuelve la luz", "se corta la luz", "me corta la luz", "se me corta la luz",
                "sin luz", "quede sin luz", "corte de luz", "se corta"], "rank": 1, "urg": "ALTA"},
    {"claves": ["parpadea", "titila", "parpadeo", "tira y da luz"], "rank": 1, "urg": "MEDIA"},
    {"claves": ["enchufe", "tomacorriente", "toma muerto", "no anda el toma", "no tengo corriente",
                "no anda un enchufe", "muerto"], "rank": 4, "urg": "BAJA"},
    {"claves": ["termotanque"], "rank": 9, "urg": "MEDIA"},
    {"claves": ["aire acondicionado", "split", "frigorias", "aire nuevo", "poner un aire",
                "poner aire", "instalar aire", "btu"], "rank": 7, "urg": "MEDIA"},
    {"claves": ["cocina electrica", "anafe", "horno electrico", "instalar cocina", "instalar horno"], "rank": 10, "urg": "MEDIA"},
    {"claves": ["ventilador"], "rank": 14, "urg": "BAJA"},
    {"claves": ["tablero", "tapita", "riel din", "cambiar el tablero"], "rank": 19, "urg": "MEDIA"},
    {"claves": ["puesta a tierra", "jabalina", "descarga a tierra", "toma de tierra"], "rank": 17, "urg": "MEDIA"},
    {"claves": ["boca", "punto de luz", "pasar un cable", "agregar toma", "agregar boca",
                "mas tomas", "ampliar"], "rank": 4, "urg": "BAJA"},
    {"claves": ["lampara", "artefacto", "aplique", "spot", "iluminacion", "led", "foco",
                "luminaria", "dicroica"], "rank": 8, "urg": "BAJA"},
    {"claves": ["certificado", "dci", "alquilar", "alquiler", "escritura", "habilitacion"], "rank": 20, "urg": "BAJA"},
    {"claves": ["presupuesto", "cuanto sale", "cuanto cuesta", "cotizar", "diagnostico", "presupuestar"], "rank": 6, "urg": "BAJA"},
]

FALLAS = {1, 2, 3}
