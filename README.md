# Motor de Jackpots — Sistema de detección de oportunidades laborales ocultas

No es un buscador de empresas. Busca la combinación:
**empresa seria + actividad actual + posible necesidad de personal + puesto compatible +
CV correcto + contacto corporativo verificable + alta probabilidad de que valga la pena acercarse.**

Es curado y de bajo volumen (2-4 jackpots por zona), no scraping masivo. La investigación
(descubrimiento, verificación de fuentes, lectura de señales) la hace Claude junto con el
usuario, zona por zona; este motor es la capa de datos, scoring, auditoría y generación de
outreach — nada se envía sin revisión humana.

## Arquitectura

```
jackpot-engine/
├── app/
│   ├── db.py              # SQLite: conexión + init
│   ├── schema.sql          # esquema completo (companies, signals, scores, outreach, ...)
│   ├── company.py          # Company DNA: alta/actualización, cálculo y guardado de score
│   ├── signals.py          # Job Signal Engine: HIRING_SIGNAL_SCORE (0-100)
│   ├── negative_signals.py # Negative Signal Engine: gravedad/vigencia, descarte automático
│   ├── cv_match.py         # CV_MATCH_ENGINE: empresa ↔ 4 CVs, con justificación
│   ├── geography.py        # Línea San Martín como columna vertebral, accessibility score
│   ├── scoring.py          # Employer Score + Jackpot Score + Confidence
│   ├── audit.py            # Audit Agent: checklist obligatorio antes de outreach
│   ├── outreach.py         # Outreach Writer: email + WHY_THIS_COMPANY
│   ├── learning.py         # analiza resultados reales de outreach, sugiere ajustes de peso
│   ├── dashboard.py        # resumen y detalle en terminal
│   └── leer_cvs.py         # extrae texto de los PDFs de cvs/
├── data/
│   └── database.sqlite     # el "cerebro estructurado" (se genera con init-db)
├── cvs/                    # PDFs de los 4 CVs + .txt extraídos
├── outreach/                # un .md por empresa con el email listo para copiar
├── tests/test_pipeline.py  # test de humo end-to-end
├── config.yaml              # zonas, umbrales, embudo de investigación, reglas duras
├── progreso.md               # resumen legible para humanos (la fuente de verdad es la DB)
└── main.py                   # CLI unificado
```

## Modelo mental (evidencia clasificada)

Toda afirmación se etiqueta como una de:
- **OBSERVADO** — verificado con fuente citable.
- **INFERIDO** — deducción razonable a partir de datos observados.
- **NO_DETERMINADO** — no se pudo establecer.
- **REQUIERE_REVISION** — dato sensible (ej. salario) que un humano debe confirmar.

El `confidence` (0-100) de cada score depende de esta mezcla, no solo del jackpot_score.

## Pipeline (embudo, ver `config.yaml`)

```
Descubrimiento barato (hasta 15 candidatas/zona)
   → Filtrado rápido (homónimos, sin señales, rubro incompatible)
   → Verificación profunda (hasta 6/zona): fuentes, señales, negative signals
   → CV match + scoring (Employer / Hiring Signal / Opportunity / Accessibility / Contactability)
   → Jackpot Score + Confidence
   → Audit Agent (checklist crítico)
   → Outreach Writer (solo si audit = aprobado)
   → Revisión humana
   → outreach/[empresa]_[fecha].md listo para copiar/enviar a mano
```

## Uso

```bash
pip install -r requirements.txt
python3 main.py init-db
python3 app/leer_cvs.py                 # una vez, con los 4 PDFs en cvs/

python3 main.py siguiente-zona          # próxima zona a investigar

# por cada empresa candidata aprobada durante la investigación:
python3 main.py add-company --nombre "..." --rubro logistica --zona Hurlingham --antiguedad 22 --tamano grande --actividad "..."
python3 main.py add-source --company-id <ID> --url "..." --tipo sitio_propio
python3 main.py add-signal --company-id <ID> --tipo expansion_logistica --fuerza fuerte --descripcion "..."
python3 main.py add-negative-signal --company-id <ID> --tipo paro --gravedad baja --vigencia baja --descripcion "..."   # si aplica
python3 main.py add-cv-match --company-id <ID> --cv logistica --score 91 --justificacion "..."
python3 main.py add-contact --company-id <ID> --tipo email --valor "info@empresa.com" --verificado
python3 main.py score --company-id <ID> --zona Hurlingham --estabilidad 90 --tamano 85 --antiguedad 95 --crecimiento 80 --formalidad 88 --actividad-actual 90 --contacto-verificado --evidencias '[{"afirmacion":"...", "nivel":"OBSERVADO"}]'

# solo si el score amerita, auditar antes de escribir el email:
python3 main.py audit --company-id <ID> --empresa-existe --localidad-correcta --fuentes-independientes --contacto-pertenece-a-empresa --email-publicado --experiencia-verificada --sin-contradicciones --sin-senales-criticas --inferencia-justificada

# generar el email (solo si audit = aprobado), con experiencia REAL copiada del CV en un archivo:
python3 main.py outreach --company-id <ID> --nombre "..." --rubro logistica --cv logistica --why "..." --experiencia-file cvs/exp_snippet.txt

python3 main.py marcar-zona "Hurlingham"
python3 main.py dashboard
python3 main.py detalle --company-id <ID>
python3 main.py why-not --company-id <ID>
python3 main.py learning   # solo útil con >=20 outreach con resultado real cargado
```

## Reglas duras (no negociables)
- Nunca se inventa ni asume contacto: solo lo verificado con fuente citable.
- Nunca se rastrea contacto personal de individuos (`add_contact` rechaza valores que parecen nombres de persona): solo email/teléfono/formulario a nivel empresa.
- Nunca se infla experiencia: el outreach exige un archivo de experiencia copiado literal del CV; sin eso, no genera nada.
- Señal negativa crítica y vigente → descarte automático, con motivo explícito (`why-not`).
- Homónimo de otra provincia/país → se descarta en la etapa de filtrado, con motivo.
- Nada se envía automáticamente: el resultado es siempre un `.md` en `outreach/` para revisión y envío manual.
