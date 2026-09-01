-- Motor de Jackpots: esquema de base de datos (data/database.sqlite)

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    rubro TEXT NOT NULL,
    zona TEXT NOT NULL,
    localidad TEXT,
    antiguedad_anios INTEGER,
    tamano_estimado TEXT,          -- "chica" | "mediana" | "grande" | "desconocido"
    actividad TEXT,                -- descripción breve de qué hace
    estado TEXT NOT NULL DEFAULT 'candidata',  -- candidata | jackpot | en_revision | descartada
    motivo_descarte TEXT,
    reintentar_despues TEXT,       -- fecha ISO: no reinvestigar antes de esto
    creado_en TEXT NOT NULL,
    actualizado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    url TEXT NOT NULL,
    tipo TEXT,                     -- "sitio_propio" | "directorio" | "noticia" | "otro"
    descripcion TEXT,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tipo TEXT NOT NULL,            -- ej "nueva_planta", "expansion_logistica"
    fuerza TEXT NOT NULL,          -- "fuerte" | "media" | "debil"
    descripcion TEXT,
    fuente_id INTEGER REFERENCES sources(id),
    fecha_evento TEXT,             -- cuándo ocurrió el hecho (si se sabe)
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS negative_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tipo TEXT NOT NULL,            -- "despidos" | "cierre" | "concurso" | "paro" | etc
    gravedad TEXT NOT NULL,        -- "baja" | "media" | "critica"
    vigencia TEXT NOT NULL,        -- "actual" | "reciente" | "baja"
    fecha_evento TEXT,
    fuente_id INTEGER REFERENCES sources(id),
    descripcion TEXT,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_hypotheses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    puesto TEXT NOT NULL,          -- ej "operario de depósito"
    probabilidad INTEGER NOT NULL, -- 0-100
    justificacion TEXT,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cv_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    cv TEXT NOT NULL,              -- limpieza | administrativo | atencion_cliente | logistica
    match_score INTEGER NOT NULL,  -- 0-100
    justificacion TEXT NOT NULL,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tipo TEXT NOT NULL,            -- "email" | "telefono" | "formulario"
    valor TEXT NOT NULL,
    verificado INTEGER NOT NULL DEFAULT 0,  -- 0/1
    fuente_id INTEGER REFERENCES sources(id),
    es_persona INTEGER NOT NULL DEFAULT 0,  -- debe ser siempre 0; se valida en código
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    employer_score INTEGER NOT NULL,
    hiring_signal_score INTEGER NOT NULL,
    opportunity_score INTEGER NOT NULL,
    accessibility_score INTEGER NOT NULL,
    contactability_score INTEGER NOT NULL,
    jackpot_score INTEGER NOT NULL,
    confidence INTEGER NOT NULL,   -- 0-100
    cv_recomendado TEXT,
    puesto_objetivo TEXT,
    chances_estimadas INTEGER,     -- 0-100, distinto de opportunity_score (ver scoring.chances_de_entrar)
    chances_baja_confianza INTEGER NOT NULL DEFAULT 0,  -- 1 si hay que mostrar "~" / "*"
    sueldo_min INTEGER,            -- null si no hay evidencia suficiente
    sueldo_max INTEGER,
    sueldo_es_estimado INTEGER NOT NULL DEFAULT 1,
    sueldo_fuente TEXT,
    detalle_json TEXT,             -- desglose completo en JSON
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    resultado TEXT NOT NULL,       -- "aprobado" | "requiere_revision" | "rechazado"
    checklist_json TEXT NOT NULL,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outreach (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    cv_usado TEXT NOT NULL,
    why_this_company TEXT NOT NULL,
    email_texto TEXT NOT NULL,
    archivo_md TEXT,
    estado TEXT NOT NULL DEFAULT 'generado', -- generado | enviado | respondio | entrevista | rechazo | no_respondio | contratacion
    creado_en TEXT NOT NULL,
    actualizado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transport_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    red TEXT NOT NULL,             -- "San Martín" | "182" | "320" | "237" | "463" | otra
    tipo TEXT NOT NULL,            -- "tren" | "colectivo"
    minutos_caminata INTEGER NOT NULL,
    minutos_viaje_total INTEGER NOT NULL,
    combinaciones INTEGER NOT NULL DEFAULT 0,
    fuente TEXT,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS discard_reasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    codigo TEXT NOT NULL,  -- NO_CONTACT | HOMONYM | NEGATIVE_SIGNAL | TOO_SMALL | LOW_STABILITY |
                            -- LOW_CV_MATCH | NO_RELEVANT_OPERATION | NO_VERIFIABLE_CONTACT |
                            -- OUTDATED_INFORMATION | DUPLICATE | LOW_OPPORTUNITY
    detalle TEXT,
    reintentar_despues TEXT,  -- fecha ISO
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS human_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    marca TEXT NOT NULL,  -- EXCELENTE | BUEN_JACKPOT | MALA_EMPRESA | FALSO_POSITIVO | PRIORITARIA | NO_BUSCAR_DE_NUEVO
    nota TEXT,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zona TEXT NOT NULL,
    empresas_evaluadas INTEGER NOT NULL DEFAULT 0,
    jackpots INTEGER NOT NULL DEFAULT 0,
    descartadas INTEGER NOT NULL DEFAULT 0,
    creado_en TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_companies_zona ON companies(zona);
CREATE INDEX IF NOT EXISTS idx_companies_estado ON companies(estado);
