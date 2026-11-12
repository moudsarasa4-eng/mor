#!/usr/bin/env python3
"""Genera la vidriera de Viraliza (un solo HTML, fuentes embebidas, sin dependencias externas).
Uso: python3 vidriera.py salida.html"""
import sys, base64, os
F = os.path.join(os.path.dirname(__file__), '..', 'remotion', 'public', 'fonts')
def b(n): return base64.b64encode(open(f'{F}/{n}.woff2', 'rb').read()).decode()
fonts = ''.join(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;src:url(data:font/woff2;base64,{b(n)}) format('woff2');font-display:swap}}"
                for fam, w, n in [('Playfair', 700, 'playfair-display-latin-700-normal'), ('Inter', 500, 'inter-latin-500-normal'),
                                  ('Inter', 600, 'inter-latin-600-normal'), ('Inter', 700, 'inter-latin-700-normal'), ('Inter', 800, 'inter-latin-800-normal')])
IG = "https://ig.me/m/viraliza.tu.perfil.arg"
PASOS = [
    ("Contratás el servicio", "Elegís un plan o un servicio suelto. Pago por adelantado, sin permanencia."),
    ("Nos pasás tu material", "Videos o fotos de tu local, producto o servicio, tomados con el celular. Si no tenés, te digo qué grabar."),
    ("Te armo el plan de reels", "Calendario del mes con cada reel editado, su portada, el texto del posteo listo para copiar y los hashtags."),
    ("Publicás y crecés", "Subís cada reel en la fecha indicada. Si querés, lo potenciamos con anuncios de Instagram."),
]
SERV = [
    ("Plan de reels mensual", "Reels editados con gancho, subtítulos y portada + texto del posteo y hashtags para cada uno.", "desde $25.000 / mes", "REEL"),
    ("Anuncios de Instagram", "Armado del anuncio, público por zona e intereses, y seguimiento semanal. El presupuesto de anuncios lo pagás aparte a Meta.", "desde $40.000 / mes", "ANUNCIOS"),
    ("Carta digital con QR", "Tu carta en el celular, con fotos y tu marca. Cambiás precios en un minuto, sin reimprimir.", "$35.000", "CARTA"),
    ("Optimización de perfil", "Nombre buscable, biografía clara, destacadas con tu marca y link a tu WhatsApp.", "$15.000", "PERFIL"),
    ("Plantillas de historias", "5 plantillas con tu marca: promoción, novedad, testimonio, horarios y pregunta.", "$20.000", "HISTORIAS"),
    ("Página web", "Una página con tus servicios, precios, galería, mapa y botón de WhatsApp.", "desde $60.000", "WEB"),
]
PLANES = [("Esencial", "4 reels por mes", "$25.000", False), ("Profesional", "10 reels por mes", "$50.000", True), ("Signature", "20 reels por mes", "$100.000", False)]
INCLUYE = ["Edición profesional de cada reel", "Portada para tu grilla", "Texto del posteo listo para copiar", "Hashtags elegidos para tu rubro y zona", "Calendario de publicación"]

pasos = ''.join(f'<li><span class="n">{i+1:02d}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for i, (t, d) in enumerate(PASOS))
cards = ''.join(f'<article class="card"><h3>{t}</h3><p>{d}</p><div class="pie"><span class="precio">{p}</span><a class="btn" href="{IG}" target="_blank" rel="noopener">Consultar</a></div></article>' for t, d, p, k in SERV)
planes = ''.join(f'<div class="plan{" rec" if r else ""}">{"<span class=tag>Recomendado</span>" if r else ""}<h3>{n}</h3><p>{d}</p><div class="monto">{p}<small> / mes</small></div><ul>{"".join(f"<li>{x}</li>" for x in INCLUYE)}</ul><a class="btn{" lleno" if r else ""}" href="{IG}" target="_blank" rel="noopener">Contratar {n}</a></div>' for n, d, p, r in PLANES)

html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Viraliza · Reels y presencia digital para negocios</title>
<meta name="description" content="Plan de reels mensual con textos y hashtags, anuncios de Instagram, carta digital con QR y optimización de perfil. CABA y GBA.">
<style>{fonts}
:root{{--fondo:#0F0E0C;--panel:#161410;--marfil:#F2ECE2;--oro:#C9A96E;--piedra:#9A9286;--linea:rgba(201,169,110,.28)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--fondo);color:var(--marfil);font-family:Inter,system-ui,sans-serif;font-weight:500;line-height:1.6;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 22px}}
header{{display:flex;align-items:center;justify-content:space-between;padding:22px 0;border-bottom:1px solid var(--linea)}}
.logo{{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--marfil)}}
.logo b{{width:40px;height:40px;border:1.5px solid var(--oro);border-radius:50%;display:grid;place-items:center;font-family:Playfair;color:var(--oro);font-size:20px}}
.logo span{{letter-spacing:.32em;font-weight:700;font-size:13px}}
nav a{{color:var(--piedra);text-decoration:none;font-size:14px;margin-left:22px}}
.hero{{padding:84px 0 64px}}
.kicker{{letter-spacing:.28em;font-size:12px;color:var(--oro);font-weight:700;text-transform:uppercase}}
h1{{font-family:Playfair;font-weight:700;font-size:clamp(36px,6vw,64px);line-height:1.1;margin:18px 0 18px;max-width:820px;letter-spacing:-.01em}}
h1 em,h2 em{{font-style:normal;color:var(--oro)}}
.lead{{color:var(--piedra);max-width:600px;font-size:18px;margin-bottom:30px}}
.acciones{{display:flex;gap:12px;flex-wrap:wrap}}
.btn{{display:inline-block;border:1px solid var(--oro);color:var(--oro);padding:13px 22px;text-decoration:none;font-weight:700;font-size:14px;border-radius:4px;transition:.2s}}
.btn:hover{{background:var(--oro);color:var(--fondo)}}
.btn.lleno{{background:var(--oro);color:var(--fondo)}}
section{{padding:72px 0;border-top:1px solid var(--linea)}}
h2{{font-family:Playfair;font-size:clamp(28px,4vw,40px);line-height:1.15;margin:10px 0 12px}}
.sub{{color:var(--piedra);margin-bottom:36px;max-width:640px}}
.pasos{{list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}}
.pasos li{{background:var(--panel);border:1px solid var(--linea);border-radius:8px;padding:24px;display:flex;flex-direction:column;gap:12px}}
.pasos .n{{font-family:Playfair;color:var(--oro);font-size:30px;line-height:1}}
.pasos h3,.card h3,.plan h3{{font-weight:800;font-size:19px;letter-spacing:-.01em}}
.pasos p,.card p,.plan p{{color:var(--piedra);font-size:15px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}
.card{{background:var(--panel);border:1px solid var(--linea);border-radius:8px;padding:24px;display:flex;flex-direction:column;gap:10px}}
.card p{{flex:1}}
.pie{{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:8px}}
.precio{{font-weight:800;color:var(--oro)}}
.planes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}
.plan{{background:var(--panel);border:1px solid var(--linea);border-radius:8px;padding:28px;position:relative;display:flex;flex-direction:column;gap:10px}}
.plan.rec{{border-color:var(--oro);box-shadow:0 0 0 1px var(--oro)}}
.monto{{font-family:Playfair;font-size:40px;margin:6px 0}}
.monto small{{font-family:Inter;font-size:15px;color:var(--piedra)}}
.plan ul{{list-style:none;margin:8px 0 16px;flex:1}}
.plan li{{color:var(--piedra);font-size:14px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.05)}}
.plan li::before{{content:"✓ ";color:var(--oro);font-weight:800}}
.tag{{position:absolute;top:-12px;left:28px;background:var(--oro);color:var(--fondo);font-size:11px;font-weight:800;letter-spacing:.14em;padding:4px 10px;border-radius:3px;text-transform:uppercase}}
.nota{{color:var(--piedra);font-size:13px;margin-top:16px}}
details{{border-bottom:1px solid var(--linea);padding:18px 0}}
summary{{cursor:pointer;font-weight:700}}
details p{{color:var(--piedra);margin-top:10px}}
.final{{text-align:center}}
footer{{padding:40px 0;color:var(--piedra);font-size:13px;text-align:center;border-top:1px solid var(--linea)}}
.flotante{{position:fixed;right:16px;bottom:16px;z-index:9;box-shadow:0 8px 24px rgba(0,0,0,.5)}}
@media(max-width:600px){{nav{{display:none}}.hero{{padding:56px 0 48px}}}}
</style></head><body>
<div class="wrap">
<header><a class="logo" href="#"><b>V</b><span>VIRALIZA</span></a><nav><a href="#proceso">Cómo funciona</a><a href="#planes">Planes</a><a href="#servicios">Servicios</a></nav></header>
<div class="hero"><div class="kicker">Reels y presencia digital · CABA y GBA</div>
<h1>Contenido profesional para tu negocio, <em>listo para publicar.</em></h1>
<p class="lead">Nos pasás fotos y videos de tu local. Te devolvemos el plan del mes: reels editados, textos para copiar y hashtags para que te encuentren.</p>
<div class="acciones"><a class="btn lleno" href="{IG}" target="_blank" rel="noopener">Pedir el primer reel sin cargo</a><a class="btn" href="#proceso">Ver cómo funciona</a></div></div>
<section id="proceso"><div class="kicker">Procedimiento</div><h2>Cómo <em>trabajamos</em></h2><p class="sub">Cuatro pasos. Vos te ocupás de tu negocio; nosotros, de cómo se ve en Instagram.</p><ol class="pasos">{pasos}</ol></section>
<section id="planes"><div class="kicker">Planes mensuales</div><h2>Plan de <em>reels</em></h2><p class="sub">Todos los planes incluyen el texto de cada posteo y los hashtags.</p><div class="planes">{planes}</div><p class="nota">Precios en pesos argentinos. Ningún proveedor serio puede garantizar resultados virales: garantizamos contenido bien hecho y entregado a tiempo.</p></section>
<section id="servicios"><div class="kicker">Servicios</div><h2>Todo lo que tu perfil <em>necesita</em></h2><p class="sub">Se contratan sueltos o junto con un plan.</p><div class="grid">{cards}</div></section>
<section><div class="kicker">Preguntas</div><h2>Preguntas <em>frecuentes</em></h2>
<details><summary>¿Tengo que grabar?</summary><p>Con fotos o videos del celular alcanza. Te mandamos una guía corta de qué grabar.</p></details>
<details><summary>¿Quién publica los reels?</summary><p>Vos, desde tu cuenta, con el texto y los hashtags que te entregamos. No necesitamos tu contraseña.</p></details>
<details><summary>¿Cómo funcionan los anuncios?</summary><p>Armamos y seguimos la campaña; el presupuesto que invertís en Meta lo pagás vos directamente, y lo definimos juntos.</p></details>
<details><summary>¿Cómo pago?</summary><p>Planes: abono mensual por adelantado. Servicios sueltos: 50% al comenzar y 50% al entregar.</p></details>
</section>
<section class="final"><h2>Empezá con un reel <em>sin cargo.</em></h2><p class="sub" style="margin:0 auto 26px">Uno por negocio, para que veas cómo trabajamos antes de contratar.</p><a class="btn lleno" href="{IG}" target="_blank" rel="noopener">Escribir por Instagram</a></section>
<footer>VIRALIZA · @viraliza.tu.perfil.arg · Buenos Aires</footer>
</div>
<a class="btn lleno flotante" href="{IG}" target="_blank" rel="noopener">Escribinos</a>
</body></html>"""
open(sys.argv[1], 'w').write(html)
print('ok', len(html) // 1024, 'KB')
