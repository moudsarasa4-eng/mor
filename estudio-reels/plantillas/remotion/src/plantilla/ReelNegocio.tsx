import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {z} from 'zod';
import {Grano} from '../componentes/Grano';
import {Subtitulos, Titular} from '../componentes/Texto';
import {pulso, tween} from '../lib/anim';
import {Efectos, Musica} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// PLANTILLA POR CLIENTE: todo sale de un JSON (clientes/<negocio>/reel-XX.json).
// Escenas con foto o clip del cliente (o fondo de color si no hay material), gancho, subtítulos
// palabra por palabra y cierre de marca. Música original en bucle.

const escena = z.object({
  segundos: z.number().min(0.5),
  media: z.string().optional(), // ruta dentro de public/, ej. "clientes/lo-de-tito/01.jpg" o ".mp4"
  titulo: z.string().optional(), // texto grande (1–4 palabras); *palabra* = color de acento
  subtitulo: z.string().optional(), // aparece palabra por palabra
});

export const esquemaNegocio = z.object({
  negocio: z.string(),
  usuario: z.string(),
  colores: z.object({fondo: z.string(), texto: z.string(), acento: z.string()}),
  fuente: z.enum(['inter', 'bebas', 'rubik', 'barlow', 'playfair']),
  musica: z.enum(['base-energica-120.wav', 'base-groove-100.wav', 'base-urbana-90.wav', 'base-suave-80.wav']),
  ejemplo: z.boolean(),
  escenas: z.array(escena).min(1),
  cierre: z.object({frase: z.string(), boton: z.string()}),
});
export type PropsNegocio = z.infer<typeof esquemaNegocio>;

const FPS = 30;
export const duracionNegocio = (p: PropsNegocio) => Math.round((p.escenas.reduce((a, e) => a + e.segundos, 0) + 2.5) * FPS);

const Media: React.FC<{src?: string; dur: number; fondo: string; acento: string}> = ({src, dur, fondo, acento}) => {
  const f = useCurrentFrame();
  if (!src) {
    return (
      <AbsoluteFill style={{background: fondo}}>
        <div style={{position: 'absolute', left: 540 - 600 + Math.sin(f / 30) * 80, top: 960 - 600, width: 1200, height: 1200, borderRadius: '50%', background: acento, opacity: 0.25, filter: 'blur(160px)'}} />
      </AbsoluteFill>
    );
  }
  const esVideo = /\.(mp4|mov|webm)$/i.test(src);
  const zoom = 1.04 + 0.08 * (f / dur); // Ken Burns suave en fotos
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {esVideo ? (
        <OffthreadVideo src={staticFile(src)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      ) : (
        <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`}} />
      )}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 35%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.55) 100%)'}} />
    </AbsoluteFill>
  );
};

const palabrasTitulo = (t: string, acento: string) =>
  t.split(' ').map((w, i) => ({t: w.replace(/\*/g, ''), en: i * 3 - 4, color: w.startsWith('*') ? acento : undefined}));

export const ReelNegocio: React.FC<PropsNegocio> = (p) => {
  const f = useCurrentFrame();
  const fuente = FUENTE[p.fuente];
  let t0 = 0;
  const cortes: number[] = [];
  const bloques = p.escenas.map((e, i) => {
    const desde = Math.round(t0 * FPS);
    const dur = Math.round(e.segundos * FPS);
    t0 += e.segundos;
    if (i > 0) cortes.push(desde);
    const z = f >= desde && f < desde + 10 ? 1 + 0.06 * Math.exp(-(f - desde) / 4) : 1;
    return (
      <Sequence key={i} from={desde} durationInFrames={dur}>
        <AbsoluteFill style={{transform: `scale(${z * (1 + 0.008 * pulso(f, 15))})`}}>
          <Media src={e.media} dur={dur} fondo={p.colores.fondo} acento={p.colores.acento} />
        </AbsoluteFill>
        {e.titulo ? <Titular top={290} tam={120} fuente={fuente} peso={900} color={p.colores.texto} lineas={[palabrasTitulo(e.titulo, p.colores.acento)]} hasta={dur} /> : null}
        {e.subtitulo ? (
          <Subtitulos frases={[{texto: e.subtitulo, desde: 6, hasta: dur}]} top={1380} tam={66} fuente={fuente} color={p.colores.texto} fondoActivo={p.colores.acento} colorActivo={p.colores.fondo} />
        ) : null}
      </Sequence>
    );
  });
  const cierre = Math.round(t0 * FPS);
  return (
    <AbsoluteFill style={{background: p.colores.fondo}}>
      {bloques}
      <Sequence from={cierre}>
        <AbsoluteFill style={{background: p.colores.fondo, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 40, fontFamily: fuente, color: p.colores.texto}}>
          <div style={{fontSize: 130, fontWeight: 900, textAlign: 'center', lineHeight: 0.95, padding: '0 60px'}}>{p.negocio}</div>
          <div style={{fontSize: 70, fontWeight: 800}}>{p.cierre.frase}</div>
          <div style={{fontSize: 48, fontWeight: 900, background: p.colores.acento, color: p.colores.fondo, padding: '18px 46px', borderRadius: 80, opacity: tween(f - cierre, [6, 12], [0, 1])}}>{p.cierre.boton}</div>
          <div style={{fontSize: 40, opacity: 0.7}}>{p.usuario}</div>
        </AbsoluteFill>
      </Sequence>
      {p.ejemplo ? (
        <div style={{position: 'absolute', top: 270, left: 60, fontFamily: FUENTE.inter, fontWeight: 800, fontSize: 30, letterSpacing: '0.14em', color: '#fff', background: 'rgba(0,0,0,0.55)', padding: '8px 18px', borderRadius: 10}}>EJEMPLO</div>
      ) : null}
      <Grano opacidad={0.04} vineta={0.35} />
      <Musica archivo={p.musica} volumen={0.75} loop />
      <Efectos eventos={[...cortes.map((c) => ({en: c - 2, sfx: 'whoosh', vol: 0.35})), {en: cierre, sfx: 'golpe', vol: 0.45}]} />
    </AbsoluteFill>
  );
};

export const ejemploNegocio: PropsNegocio = {
  negocio: 'Estudio Lila (ejemplo)',
  usuario: '@estudiolila.ejemplo',
  colores: {fondo: '#2A1622', texto: '#FFF4F8', acento: '#FF9EC4'},
  fuente: 'inter',
  musica: 'base-suave-80.wav',
  ejemplo: true,
  escenas: [
    {segundos: 3, titulo: '3 horas de *trabajo*', subtitulo: 'en 15 segundos'},
    {segundos: 3, titulo: 'Paso *1*', subtitulo: 'acá va el clip o la foto que manda el cliente'},
    {segundos: 3, titulo: 'Paso *2*', subtitulo: 'cada escena: segundos, media, título y subtítulo'},
    {segundos: 3, titulo: 'El *resultado*', subtitulo: 'mandáselo a tu amiga que necesita turno'},
  ],
  cierre: {frase: 'Turnos por mensaje', boton: 'LINK EN EL PERFIL'},
};
