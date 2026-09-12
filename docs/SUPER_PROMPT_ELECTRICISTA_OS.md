# SUPER PROMPT — Electricista OS (para Claude Code)

> Pegá este documento como primer mensaje en una sesión de Claude Code abierta sobre el repo,
> junto con los 3 archivos de investigación (`cuadro_30_trabajos_electricista.xlsx`,
> `speechs-trabajos-demandados-upsells.md`, `prompt-motor-agenda-dinamica-y-calculadora-proyectista.md`).
> Este archivo es la **fuente de verdad** de qué construir y cómo auditarlo.

---

## 0. Contexto

Electricista OS es la app de gestión de **Marco Florentino**, electricista domiciliario matriculado
en Hurlingham (GBA Oeste). El frontend es **un único HTML autocontenido** en `dashboard/index.html`
(todo el CSS/JS inline, sin build, sin dependencias externas, se abre solo en el navegador). Puede
correr **sin backend** (datos demo + todo lo que persiste en `localStorage`) o conectado a una API
FastAPI (aún no incluida en este repo). Todo lo que se construya debe:

- Mantener el **único archivo autocontenido** (o, si se separa, seguir abriendo solo, sin build).
- **No romper el contrato** con los endpoints que el dashboard ya espera.
- Escapar **todo dato de cliente** con `esc()` antes de inyectarlo en el DOM (anti-XSS).
- Usar **delegación de eventos** con `data-action` / `data-change` / `data-input` (nada de `onclick` inline).
- Texto de interfaz en **español rioplatense**, tono directo, sin tecnicismos innecesarios.
- Ser **usable desde el celular** (Marco lo usa en la calle) y **accesible** (roles ARIA, labels, foco).

**Objetivo visual (lo más importante para Marco):** el dashboard tiene que **ordenarle la cabeza**.
Intuitivo, ordenado, visualmente dinámico, que **no deje escapar nada** y le recuerde todo lo que
tiene que hacer y tener en cuenta para su profesión. Nada librado al azar.

---

## 1. Fuentes de datos a incorporar (los 3 archivos)

### 1.1. Cuadro de 30 trabajos (`cuadro_30_trabajos_electricista.xlsx`)
Catálogo maestro del oficio. Columnas: **Rank, Trabajo, Precio mín, Precio máx, Fuente, Solución
(qué se hace), Materiales principales, Tiempo estimado, Notas.** Reglas:
- Es la **fuente por defecto** de `precio_estimado` y `duracion_estimada` para el motor de agenda y la proyección.
- Ítems marcados **`s/d`** (sin dato de precio): 18 (medición jabalina), 25 (pararrayos), 26 (alarma),
  27 (cámaras), 28 (cerco), 29 (domótica), 30 (wallbox). **Nunca inventar un precio**: pedir que Marco
  cargue el estimado a mano antes de usarlos en cálculos.
- **Anomalías ya corregidas** (respetar): ítem 16 "tecla de encendido" → descartar el máximo outlier
  ($698.546), dejar solo mínimo; ítem 25 "pararrayos" → rango inconsistente, descartado (cotizar caso a caso).
- Precios = **mano de obra de referencia** CABA/GBA may–jul 2026. Se desactualizan con la inflación:
  mostrarlos como orden de magnitud y dejar que Marco cargue **sus** precios (override en `localStorage`).

### 1.2. Speechs + upsells (`speechs-trabajos-demandados-upsells.md`)
11 trabajos top con, cada uno: **speech inicial**, **preguntas de calificación**, **3 upsells**.
Guardar como 3 objetos reutilizables por trabajo. Reglas:
- Sugerir **un solo upsell relevante** según la respuesta del cliente, no los 3 de una.
- Corrección normativa clave: el diferencial estándar obligatorio (AEA 90364-7-701) es **30 mA en toda
  la vivienda**; el **10 mA** es una **mejora opcional** para zonas de riesgo agravado (bañera/hidromasaje),
  **no** un mínimo exigido para "pileta o exterior". El speech no debe prometerlo como obligatorio.
- Corchetes `[Negocio]`, `[Nombre]`, `[$monto]` = se completan con la config de Marco.

### 1.3. Motor de agenda dinámica + calculadora proyectista (`prompt-motor-...md`)
Dos módulos deterministas (sin IA/ML — lógica de negocio auditable):
- **Módulo 1 — Agenda dinámica ("balanza"):** puntaje de conveniencia 0–100 para un cliente nuevo,
  ponderando Rentabilidad 30%, Costo de traslado 25%, Urgencia 15%, Confiabilidad 15%, Ajuste al hueco 15%.
  Cortes: **≥70 conviene**, **40–69 negociable**, **<40 no conviene (salvo estratégico)**. Nunca bloquear
  la decisión final. Sugerir mejor horario agrupando por zona. Explicar el **porqué** en lenguaje simple.
- **Módulo 2 — Proyectista:** ingreso mensual proyectado con **piso / esperado / techo** + desglose por
  tipo de trabajo. Alimenta un **umbral dinámico** del Módulo 1 (si va atrasado contra la meta, baja el
  umbral y acepta más; si va bien, sube y se pone selectivo).
- **Todo configurable desde la app** (pesos, cortes, factor estacional, meta mensual, matriz de tiempos
  entre zonas). Nada hardcodeado que Marco no pueda ajustar.

---

## 2. Qué construir (módulos)

1. **Datos embebidos:** `CATALOGO_30`, `SPEECHS`, diccionario de sinónimos, matriz de zonas, config nueva.
   Precios/tiempos con override editable en `localStorage`.
2. **💬 WhatsApp (intake + triage):** pegás/reenviás el mensaje del cliente → clasifica el trabajo por
   sinónimos ("salta la térmica" = "salta la llave" = "disyuntor", etc.), **detecta emergencia** (chispas,
   olor a quemado, calor → bandera roja + guion de seguridad), sugiere **speech + preguntas + 1 upsell**,
   y crea el prospecto con urgencia y trabajo estimado. Biblioteca de speechs navegable con copiar.
   Esto deja **las bases de WhatsApp puestas** en modo "manual mejorado" (sin integración todavía).
3. **📋 Catálogo:** los 30 trabajos navegables, con **mi precio** editable, solución, materiales, tiempo,
   notas y upsells. Es la fuente de precio/duración del resto.
4. **⚖️ ¿Conviene? (agenda dinámica + proyección):** la balanza (puntaje + recomendación + mejor horario +
   explicación) y la proyección mensual piso/esperado/techo con meta y umbral dinámico. Pesos, cortes y
   matriz de zonas editables.
5. **🎯 Hoy (dashboard que ordena la cabeza):** centro de control con urgencias, turnos, cobros, **stock
   bajo**, **meta del mes** (barra de progreso) y **recordatorios/pendientes** para que no se escape nada:
   garantías por vencer, presupuestos sin respuesta, seguimiento post-trabajo (reseña), revisión anual.
6. **🧮 Calculadora** (ya existe): cables/materiales AEA 90364. Conectarla con el catálogo/precios.

---

## 3. Reglas técnicas de aplicación

- Cada dato de cliente pasa por `esc()`. Cada acción va por delegación (`data-*`).
- Precios y config: `localStorage` con defaults de referencia; siempre visible el aviso
  "precios de referencia, actualizá con los tuyos".
- Reusá lo que ya existe: `toast()`, `fmt()`, `pillClass()`, el patrón de "Generar prompt PDF",
  la checklist "Qué llevar", la ficha de cliente.
- El motor de agenda y la proyección son **determinísticos** y **explicables** (mostrar el desglose del
  puntaje y el porqué de la recomendación, no una caja negra).
- Nada de dependencias externas ni build. Nada de romper el modo demo.

---

## 4. Criterios de aceptación (Definition of Done)

- [ ] La app abre sola (sin backend) y ninguna sección queda en blanco ni tira excepción JS.
- [ ] WhatsApp: un mensaje con "salta la térmica y huele a quemado" ⇒ clasifica térmica/disyuntor,
      **marca emergencia**, muestra guion de seguridad y crea prospecto urgente.
- [ ] Catálogo: los 30 trabajos se ven; editar "mi precio" persiste y se refleja en agenda/proyección.
- [ ] ¿Conviene?: un cliente de alto $/hora en zona agrupada da **≥70 "conviene"**; uno de bajo ticket que
      obliga a cruzar zonas da **<40** con explicación; la proyección muestra piso/esperado/techo.
- [ ] Hoy: barra de meta del mes + lista de pendientes/recordatorios accionables.
- [ ] Todo escapado (XSS), todo por delegación, responsive a 390px, sin scroll horizontal del body.

---

## 5. Auditoría (hacerla cuando creas que terminaste)

1. `node --check` sobre el JS extraído del HTML (sintaxis).
2. Smoke test headless (Chromium/Playwright) que recorra **todas** las pestañas:
   - carga sin backend (datos demo), sin `pageerror`;
   - WhatsApp intake (emergencia + no-emergencia), creación de prospecto;
   - Catálogo (render 30, editar precio, persistencia);
   - ¿Conviene? (3 escenarios de puntaje + proyección piso/esperado/techo);
   - Calculadora (obra + rápido) intactas;
   - Hoy (meta + recordatorios), modal + Escape, responsive 390px, XSS escapado.
3. Corregir hasta que **todos** los checks pasen. Recién ahí, commit + push a la rama de trabajo.
4. Dejar un resumen: qué se aplicó de cada archivo, qué quedó pendiente de backend, y cómo probarlo.

---

## 6. Pendiente de backend (documentar, no bloquear)
- Ingreso automático de WhatsApp (API oficial Cloud o puente) — hoy en modo manual mejorado.
- Persistencia central multi-dispositivo (hoy `localStorage` por navegador).
- Facturación real (ARCA/TusFacturasAPP) — hoy simulada y marcada como tal.
- Ruta/tiempos reales entre zonas (hoy matriz fija editable).
