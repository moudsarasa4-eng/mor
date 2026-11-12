# TRASPASO — Viraliza (@viraliza.tu.perfil.arg) · para continuar en otro chat de Claude
Actualizado: 12/11/2026. Leelo completo antes de hacer nada. Idioma: español rioplatense (voseo).

## 1. Quién es el usuario y qué vende
- Editor de reels / presencia digital para negocios locales de CABA y GBA. Marca: **VIRALIZA** (cuenta IG: @viraliza.tu.perfil.arg). Contacto de todos los CTA: https://ig.me/m/viraliza.tu.perfil.arg
- Vende por Instagram (DM). Trabaja con Claude + Remotion + ElevenLabs (voces "Mauricio", "Carlos", "Tomás" — argentinas).
- Tiene otro negocio aparte: **plan de estudio** (páginas HTML publicadas en Cloudflare vía GitHub `marcoamma04-bot/paginas-plan-de-estudio`, skill `publicar-pagina-plan-estudio`). Es OTRA cuenta: no mezclar con Viraliza. Los reels de estudio son de ese cliente.

## 2. Repositorio y archivos
- GitHub: `moudsarasa4-eng/mor`, rama **`estudio-reels`**, carpeta **`estudio-reels/`** (el resto del repo `mor` es otro proyecto: no tocar). Repo PÚBLICO: no subir datos personales ni listas de prospectos.
- Proyecto de video: `estudio-reels/plantillas/remotion/` (Remotion 4.0.541, React 19, Three.js). `npm install`, luego `npx remotion studio`. Render: `./render.sh <Composición> salida.mp4 [props.json]` (normaliza audio a −14 LUFS). Para reels sin audio: `npx remotion render <Comp> out.mp4 --muted`.
  - En nube sin Chrome: `export REMOTION_BROWSER=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.
- Música/SFX originales (sin copyright): `estudio-reels/plantillas/audio/sintetizar.py` → `public/audio/`.
- Página vidriera: generador `estudio-reels/plantillas/web/vidriera.py` → `cuenta-editor/servicios/vidriera-viraliza.html` (un solo archivo, fuentes embebidas). Falta publicarla (Cloudflare Pages/Workers como el plan de estudio, o GitHub Pages).

## 3. Identidad de marca VIGENTE (premium) — usar en TODO
- El usuario rechazó la versión negra/lima ("parece hecho por un niño"). Vigente: **lujo sobrio**.
- Colores: negro cálido `#0F0E0C`, marfil `#F2ECE2`, champagne `#C9A96E` (acento, 1 palabra por pantalla), piedra `#8C857A`.
- Tipografía: **Playfair Display 700** para títulos (en la web, sin itálica = más formal), **Inter** para detalles (espaciado en mayúsculas para sellos). Sin emojis en reels premium. Movimientos lentos, mucho aire, líneas finas doradas.
- Logo: monograma "V" en círculo fino dorado + "V I R A L I Z A" espaciado. Sello en reels: "— VIRALIZA · ESTUDIO —".
- Código: `src/serie/BocetoPremium.tsx` (LUJO, Monograma), `src/serie/ReelServicio.tsx` (reels premium).

## 4. Precios (definidos por el usuario)
| Plan reels | Precio/mes | Reels |
|---|---|---|
| Esencial | $25.000 | 4 (1 por semana) |
| Profesional (RECOMENDADO) | $50.000 | 10 |
| Signature | $100.000 | 20 |
Todos incluyen: edición, portada, texto del posteo para copiar, hashtags por rubro y zona, calendario.
Servicios sueltos: Carta digital QR $35.000 · Optimización de perfil $15.000 · Plantillas de historias (5) $20.000 · Link en bio $20.000 · Página web desde $60.000 · **Anuncios de Instagram desde $40.000/mes** (el presupuesto de Meta lo paga el cliente; precio propuesto por Claude, confirmar). Combo "Kit Presencia" (perfil + historias + link) $45.000.
Oferta de entrada: **primer reel sin cargo** (uno por negocio).
Ojo: con estética de lujo, $25.000 puede parecer barato → se sugirió no mostrar precios en algunos reels o subir Signature (pendiente).

## 5. Proceso que se comunica (pedido explícito)
1. Contratás el servicio. 2. Nos pasás videos/fotos de tu local, producto o servicio. 3. Te armo el plan de reels: cada reel + portada + texto del posteo para copiar + hashtags. 4. Publicás (y opcional: anuncios de Instagram).

## 6. Qué está hecho (en `estudio-reels/`)
- `cuenta-editor/servicios/`: investigación de 3 servicios + guiones ElevenLabs, **vidriera-viraliza.html** (formal, con procedimiento), reels premium `reel-carta-qr.mp4`, `reel-optimizacion-perfil.mp4`, `reel-plantillas-historias.mp4` (+ portadas).
- `cuenta-editor/serie/`: bocetos (`bocetos-premium.png` vigente; `bocetos-plantillas.png` descartado), serie de 5 reels por rubro en estilo VIEJO (rosa/negro/bordó…) → **rehacer en estilo premium**. Reel 1 Estética fue aprobado en estructura (editor + anuncio de ejemplo dentro del celular) antes del cambio a premium.
- `cuenta-editor/investigacion-y-guiones.md`: cómo se venden los editores + 5 guiones.
- `servicio/`, `demos/`: reel vendedor y demos (barbería, hamburguesería, pádel) — estilo anterior.
- `clientes/plan-de-estudio/`: 3 reels del plan de estudio (Leitner, recordar, examen) — cliente aparte.
- `clientes/_plantilla/` + `nuevo-cliente.sh`: kit por cliente (brief, plan del mes, reporte, JSON de reel).
- Prospección CABA (71 negocios con mensajes) quedó SOLO en la sesión anterior (no se subió: datos reales). Si hace falta, rehacer.

## 7. Pendientes (en orden)
1. Decidir mostrar precios en reels o "consultá por mensaje".
2. Rehacer los 5 reels por rubro (estética, gimnasios, odontología, gastronomía, inmobiliarias) en estilo premium, con: marca desde el primer cuadro, gancho, problema, "soy editor", anuncio de ejemplo en celular, planes, cierre "Escribime PALABRA". Palabras: UÑAS, ENERO, TURNO, PLATO, PROPIEDAD.
3. Video de 25 s de la vidriera (scroll + 4 pasos) para mandar cuando un prospecto responde.
4. Publicar la vidriera y ponerla como link en la bio.
5. Bio de IG (no se pudo leer el perfil: pedir captura). Propuesta: nombre "Viraliza | Editor de reels CABA"; bio "Reels que hacen ver tu marca como lo que vale ✨ / Estudio de reels para negocios · CABA / Primer reel sin cargo 👇".
6. Agregar voces de ElevenLabs a los reels cuando el usuario mande los MP3 (sincronizar por pausas: no hay transcripción en la nube).

## 8. Reglas que el usuario pidió / que se respetan
- Formato reels: 1080×1920, 30 fps, H.264, 22–28 s; dejar libre 15% arriba y 25% abajo; máx. 7 palabras por pantalla; algo cambia cada 2–3 s; el último cuadro empalma con el primero; sin marcas de agua.
- Antes de producir: bocetar y mostrar; revisar cuadros de prueba con guías de zona segura.
- Usar las skills de redes ("social-media-skills:*": reels-script, hook-writer, caption-writer, instagram-seo, etc.) y dejarlas ejecutadas en el chat (el usuario lo pidió explícitamente).
- Honestidad: no prometer viral ni ventas; no inventar métricas, testimonios ni "más elegido"; negocios de ejemplo con etiqueta EJEMPLO; no usar datos personales de clientes (ej. el HTML de "Florencia") en reels públicos; prospección en frío a mano, pocos por día, con baja fácil.
- Primer mensaje a prospectos: 2 líneas + pregunta; el video/página recién cuando responden.
- Commits al final de cada tarea, push a `estudio-reels` (el hook del entorno lo exige).
