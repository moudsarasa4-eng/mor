# Estudio de reels para negocios — índice (09/11/2026)

## Entregables
| Qué | Dónde |
|---|---|
| Reel vendedor (frase del dueño) | servicio/reel-vendedor/reel-vendedor.mp4 + portada.png + guion.md |
| Reel vendedor para anuncios (frase honesta) | servicio/reel-vendedor/reel-vendedor-anuncios.mp4 |
| Demo barbería / hamburguesería / pádel | demos/<rubro>/<rubro>.mp4 + portada.png + guion.md |
| Captions, hashtags, portadas, checklist | servicio/captions-y-publicacion.md |
| Test de ganchos, calendario, respuestas por DM | servicio/lanzamiento.md |
| Perfil de marca y voz | servicio/brand-profile.md · servicio/voice.md |
| Folleto (PNG WhatsApp + PDF) | servicio/folleto/ |
| Prospectos CABA | no se suben al repo público (quedan fuera) |
| Plantilla por cliente | clientes/_plantilla/ + clientes/nuevo-cliente.sh |
| Proyecto de video (Remotion) | plantillas/remotion/ · sonido: plantillas/audio/sintetizar.py |

Specs verificadas: 1080×1920, 30 fps, H.264 yuv420p (BT.709), AAC 48 kHz, −14 LUFS, sin marcas de agua.

## Cliente nuevo en minutos
1. `clientes/nuevo-cliente.sh lo-de-tito`
2. Fotos/clips del cliente → `plantillas/remotion/public/clientes/lo-de-tito/`
3. Editar `clientes/lo-de-tito/reel-01.json` (textos, colores, música, escenas)
4. `cd plantillas/remotion && ./render.sh ReelNegocio ../../clientes/lo-de-tito/entregas/reel-01.mp4 ../../clientes/lo-de-tito/reel-01.json`

## Cambiar nombre/usuario en el reel vendedor
`./render.sh ReelVendedor salida.mp4 props.json` con `{"fraseFuerte":["GANÁ VENTAS","VIRALIZANDO","TUS REELS"],"palabraVerde":"VENTAS","subFrase":"","editor":{"nombre":"…","usuario":"@…","iniciales":"…"}}`

## Primera vez en tu PC
Node 20+ y ffmpeg instalados → `cd plantillas/remotion && npm install`. Vista previa: `npm run studio`.
Remotion es gratis para personas y empresas de hasta 3 personas (más grandes necesitan licencia). Fuentes: licencia OFL. Música y efectos: sintetizados en este proyecto, sin samples ni copyright de terceros.

## Pendientes del dueño
Nombre, logo, @usuario y WhatsApp (en props y folleto.json) · precios · muestras gratis sí/no · gancho para anuncios · presupuesto IA paga.
