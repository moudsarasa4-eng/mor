# Motor de Jackpots — Sistema de detección de oportunidades laborales ocultas

No es un buscador de empresas. Busca la combinación:
**empresa seria + actividad actual + posible necesidad de personal + puesto compatible +
CV correcto + contacto corporativo verificable + alta probabilidad de que valga la pena acercarse.**

## Para usar la app (no hace falta saber programar)

### 1. Instalación inicial (una sola vez)
- **Windows**: doble click en `start.bat`
- **Linux/Mac**: doble click en `start.sh` (o `./start.sh` en una terminal)

La primera vez instala todo lo necesario solo. Al final te va a pedir completar tu API key de búsqueda en el archivo `.env` (una sola línea: `SERPER_API_KEY=tu_key`, gratis en https://serper.dev).

### 2. Cómo iniciar
Doble click en `start.bat` (Windows) o `./start.sh` (Linux/Mac). Se abre sola una página en tu navegador: http://127.0.0.1:5000

### 3. Cómo ejecutar una búsqueda
En la página, apretá **▶ INICIAR BÚSQUEDA**. El motor empieza a buscar empresas reales por su cuenta, zona por zona (arranca en Hurlingham y va expandiendo), sin que tengas que decirle qué buscar.

### 4. Cómo pausar
Apretá **⏸ PAUSAR** en cualquier momento. El progreso queda guardado.

### 5. Cómo continuar
Apretá **↻ CONTINUAR**, o simplemente volvé a abrir la app otro día — retoma exactamente donde quedó, sin repetir trabajo.

### 6. Dónde están los resultados
- En la página: tabla de mejores oportunidades, actualizada en vivo.
- En archivos: `outreach/` tiene los emails listos para copiar y enviar a mano (nunca se envían solos).
- `reports/learning_report.md`: qué aprendió el motor sobre qué búsquedas/fuentes funcionan mejor.

---

## ⚠️ Límite honesto de lo que la app hace sola

El motor **descubre candidatas por su cuenta** (usando la API de búsqueda), pero el **juicio de calidad** — decidir si una empresa es realmente seria, clasificar la gravedad de una noticia negativa, justificar un match de CV, auditar antes de generar un email — hoy usa heurísticas simples (reglas y palabras clave), no comprensión real. Es más bruto que cuando Claude lo hace leyendo cada caso en una sesión de Claude Code. Para llegar a ese nivel de criterio de forma 100% autónoma haría falta además conectar una API de un modelo de lenguaje (con su propio costo), algo que no está incluido en esta versión.

Recomendación de uso real: dejá la app corriendo para que acumule candidatas descubiertas (`discovered_companies_raw`), y de tanto en tanto traé esa lista a una sesión de Claude Code para que las verifique, puntúe y audite con criterio real antes de generar los emails — igual que hicimos con Hurlingham.

---

## Arquitectura

```
jackpot-engine/
├── main.py                  CLI unificado (run/daily/zone/status/doctor/webapp + comandos de carga manual)
├── web/                     App web local (Flask): dashboard, iniciar/pausar/continuar
├── app/
│   ├── db.py / schema.sql    SQLite: el "cerebro estructurado"
│   ├── search_client.py      Cliente Serper.dev (búsqueda web real)
│   ├── keywords.py           Diccionario semilla + plantillas de query (Types A-G)
│   ├── discovery.py          Extrae candidatas, deduplica, aprende yield de keywords
│   ├── runner.py             Orquesta zonas, presupuesto diario, pausar/continuar
│   ├── run_state.py          Estado persistente de la corrida
│   ├── company.py            Company DNA: alta, scoring, transporte
│   ├── signals.py / negative_signals.py   Job Signal Engine / Negative Signal Engine
│   ├── cv_match.py           CV_MATCH_ENGINE con justificación
│   ├── geography.py / transport.py   Línea San Martín + colectivos 182/320/237/463
│   ├── scoring.py            Employer Score, Jackpot Score, Chances de entrar, Confidence
│   ├── audit.py              Audit Agent: checklist obligatorio antes de outreach
│   ├── outreach.py           Outreach Writer inteligente (nunca inventa experiencia)
│   ├── feedback.py           Feedback humano + motivos de descarte estructurados
│   ├── source_performance.py / learning_report.py   Estadísticas de qué funciona
│   └── cv_data.py            Única fuente de verdad de los 4 CVs reales
├── cvs/                      PDFs + texto extraído de los 4 CVs
├── outreach/                 Emails generados, listos para revisión y envío manual
├── reports/                   learning_report.md
├── data/database.sqlite       Se genera con init-db / doctor
└── config.yaml                 Zonas, umbrales, presupuesto de búsqueda
```

## Comandos (modo avanzado, sin la web)

```bash
python3 main.py doctor          # diagnóstico: python, dependencias, DB, API key, CVs
python3 main.py status          # estado actual: empresas descubiertas/verificadas/jackpots
python3 main.py zone Hurlingham --max-queries 20   # investigar una zona puntual
python3 main.py run             # corre continuo hasta agotar presupuesto o saturar zonas
python3 main.py daily           # modo diario (mismo motor, pensado para correr una vez por día)
python3 main.py dashboard       # tabla de top oportunidades en terminal
python3 main.py detalle --company-id N
```

Los comandos de carga manual (`add-company`, `add-signal`, `score`, `audit`, `outreach`, etc.) siguen disponibles para cuando Claude verifica y sube una empresa con criterio real — ver el historial del proyecto para ejemplos.

## Reglas duras (no negociables)
- Nunca se inventa ni asume contacto: solo lo verificado con fuente citable.
- Nunca se rastrea contacto personal de individuos: solo email/teléfono/formulario a nivel empresa (`add_contact` rechaza valores que parecen nombres de persona).
- Nunca se infla experiencia: el outreach exige experiencia real tomada de `app/cv_data.py`.
- Señal negativa crítica y vigente → descarte automático, con motivo explícito.
- Homónimo de otra provincia/país → se descarta, con motivo.
- Nada se envía automáticamente: outreach termina siempre en un `.md` para revisión y envío manual.
- El descubrimiento puede ser agresivo (muchas queries, muchas fuentes); el outreach sigue siendo selectivo y bajo revisión.
