import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Celular} from '../componentes/Celular';
import {Grano} from '../componentes/Grano';
import {Subtitulos, Titular} from '../componentes/Texto';
import {pulso, resorte, tween} from '../lib/anim';
import {Efectos} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// Reels para la cuenta del editor @viraliza.tu.perfil.arg. Un componente, 4 reels (datos abajo).
// Si existe la voz (prop voz), se agrega; si no, funciona solo con texto + música.
const VERDE = '#2BEA7A';
const ROJO = '#FF4D5E';
const AMARILLO = '#FFD84D';
const USUARIO = '@viraliza.tu.perfil.arg';

type Visual =
  | {tipo: 'split'; destacar?: string[]}
  | {tipo: 'tel'; video: string; desde?: number}
  | {tipo: 'malbien'; malo: string; bueno: string; num: string}
  | {tipo: 'paso'; num: string; video: string; desde?: number}
  | {tipo: 'tres'; videos: string[]}
  | {tipo: 'cta'};

export type Escena = {seg: number; titulo: {t: string; c?: string; fondo?: string}[][]; voz: string; visual: Visual; efecto?: 'excited' | 'pause' | 'whispers'};
export type PropsEditor = {escenas: Escena[]; voz?: string};

const Video: React.FC<{v: string; desde?: number; filtro?: string}> = ({v, desde = 0, filtro}) => (
  <OffthreadVideo src={staticFile(`demos/${v}.mp4`)} muted trimBefore={desde} style={{width: 1080, height: 1920, filter: filtro}} />
);

const Tel: React.FC<{v: string; desde?: number; ancho?: number; x?: number; y?: number; rot?: number; filtro?: string; marco?: string}> = ({v, desde, ancho = 560, x = 540, y = 1150, rot = 0, filtro, marco}) => (
  <div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 1.03, transform: `rotate(${rot}deg)`, filter: marco ? `drop-shadow(0 0 30px ${marco})` : undefined}}>
    <Celular ancho={ancho} ejemplo={false}>
      <Video v={v} desde={desde} filtro={filtro} />
    </Celular>
  </div>
);

const Escenario: React.FC<{e: Escena; f: number; dur: number}> = ({e, f, dur}) => {
  const {fps} = useVideoConfig();
  const v = e.visual;
  if (v.tipo === 'split') {
    const d = tween(f, [0, 14], [0, 1]);
    return (
      <>
        <Tel v="barberia-cruda" x={290 - (1 - d) * 400} ancho={440} y={1130} rot={-3} />
        <Tel v="barberia" desde={10} x={790 + (1 - d) * 400} ancho={440} y={1130} rot={3} marco={VERDE} />
        <div style={{position: 'absolute', top: 1395, left: 0, right: 0, display: 'flex', justifyContent: 'space-around', fontFamily: FUENTE.barlow, fontWeight: 900, fontStyle: 'italic', fontSize: 64}}>
          <span style={{color: ROJO}}>SIN EDITAR</span>
          <span style={{color: VERDE}}>EDITADO</span>
        </div>
        {(v.destacar ?? []).map((t, i) => {
          const sp = resorte(f, fps, 10 + i * Math.floor(dur / ((v.destacar?.length ?? 1) + 1)), 'rebote');
          return (
            <div key={i} style={{position: 'absolute', left: 0, right: 0, margin: '0 auto', width: 'fit-content', top: 430 + i * 74, padding: '6px 24px', borderRadius: 50, background: VERDE, color: '#0B0E1A', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 34, transform: `scale(${sp})`, boxShadow: `0 0 30px ${VERDE}88`}}>✓ {t}</div>
          );
        })}
      </>
    );
  }
  if (v.tipo === 'tel') return <Tel v={v.video} desde={v.desde} y={1220} marco={VERDE} />;
  if (v.tipo === 'malbien') {
    const fix = f >= dur * 0.5;
    return (
      <>
        <div style={{position: 'absolute', left: 70, top: 300, width: 170, height: 170, borderRadius: '50%', background: AMARILLO, color: '#0B0E1A', fontFamily: FUENTE.barlow, fontWeight: 900, fontSize: 130, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${resorte(f, fps, 0, 'rebote')})`}}>{v.num}</div>
        <Tel v={fix ? v.bueno : v.malo} desde={fix ? 20 : 0} y={1250} ancho={520} marco={fix ? VERDE : ROJO} filtro={fix ? undefined : 'grayscale(0.6) brightness(0.8)'} />
        <div style={{position: 'absolute', left: 760, top: 640, fontSize: 200, fontFamily: FUENTE.inter, fontWeight: 900, color: fix ? VERDE : ROJO, transform: `scale(${1 + 0.3 * Math.exp(-(f - (fix ? dur * 0.5 : 0)) / 4)})`}}>{fix ? '✓' : '✗'}</div>
      </>
    );
  }
  if (v.tipo === 'paso') {
    // línea de tiempo de edición + celular
    return (
      <>
        <Tel v={v.video} desde={v.desde} y={1080} ancho={460} marco={VERDE} />
        <div style={{position: 'absolute', left: 60, right: 60, top: 1230, height: 210, borderRadius: 24, background: '#151A2C', border: '2px solid #2A3150', padding: 18}}>
          {[0, 1, 2].map((p) => (
            <div key={p} style={{display: 'flex', gap: 6, marginBottom: 12, height: 44}}>
              {Array.from({length: 9}).map((_, k) => (
                <div key={k} style={{flex: 1 + ((k * 7 + p * 3) % 4), borderRadius: 8, background: [VERDE, '#4FC3FF', AMARILLO][p], opacity: k <= (f / 3) % 10 ? 0.9 : 0.25}} />
              ))}
            </div>
          ))}
          <div style={{position: 'absolute', top: 6, bottom: 6, width: 6, background: '#fff', left: 18 + ((f * 9) % 900), borderRadius: 3}} />
        </div>
        <div style={{position: 'absolute', left: 70, top: 300, width: 170, height: 170, borderRadius: '50%', background: VERDE, color: '#0B0E1A', fontFamily: FUENTE.barlow, fontWeight: 900, fontSize: 130, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${resorte(f, fps, 0, 'rebote')})`}}>{v.num}</div>
      </>
    );
  }
  if (v.tipo === 'tres') {
    return (
      <>
        {v.videos.map((vid, i) => {
          const sp = resorte(f, fps, i * 6, 'pop');
          return <Tel key={i} v={vid} desde={30} ancho={320} x={[200, 540, 880][i]} y={1180 + (1 - sp) * 900 + (i === 1 ? -40 : 0)} rot={[-6, 0, 6][i]} marco={VERDE} />;
        })}
      </>
    );
  }
  // cta
  return (
    <AbsoluteFill style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 40, fontFamily: FUENTE.inter, color: '#fff'}}>
      <div style={{width: 230, height: 230, borderRadius: '50%', padding: 8, background: `linear-gradient(135deg, ${VERDE}, #4FC3FF)`, transform: `scale(${resorte(f, fps, 0, 'rebote')})`}}>
        <div style={{width: '100%', height: '100%', borderRadius: '50%', background: '#151A2C', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 80}}>VP</div>
      </div>
      <div style={{fontWeight: 900, fontSize: 56}}>{USUARIO}</div>
      <div style={{fontWeight: 600, fontSize: 38, opacity: 0.75}}>Editor de reels para negocios · CABA</div>
      <div style={{marginTop: 20, background: VERDE, color: '#0B0E1A', fontWeight: 900, fontSize: 64, padding: '26px 60px', borderRadius: 30, transform: `scale(${1 + 0.05 * pulso(f, 15)})`, boxShadow: `0 0 50px ${VERDE}88`}}>Escribime "REEL"</div>
    </AbsoluteFill>
  );
};

export const duracionEditor = (p: PropsEditor) => Math.round(p.escenas.reduce((a, e) => a + e.seg, 0) * 30);

export const ReelEditor: React.FC<PropsEditor> = ({escenas, voz}) => {
  const f = useCurrentFrame();
  let acc = 0;
  const tramos = escenas.map((e) => {
    const desde = Math.round(acc * 30);
    acc += e.seg;
    return {e, desde, dur: Math.round(e.seg * 30)};
  });
  const total = Math.round(acc * 30);
  const actual = tramos.find((t) => f >= t.desde && f < t.desde + t.dur) ?? tramos[tramos.length - 1];
  const lf = f - actual.desde;
  const ef = actual.e.efecto;
  let sx = 0, z = 1;
  if (ef === 'excited' && lf < 14) {
    sx = Math.sin(f * 3.1) * 18 * Math.exp(-lf / 4);
    z = 1 + 0.1 * Math.exp(-lf / 4);
  }
  if (lf < 8) z *= 1 + 0.05 * Math.exp(-lf / 3);
  const filtro = ef === 'pause' ? 'saturate(0.4) brightness(0.75)' : ef === 'whispers' ? 'brightness(0.55)' : 'none';
  const frases = tramos.map((t) => ({texto: t.e.voz, desde: t.desde + 2, hasta: t.desde + t.dur, paso: Math.max(3, Math.floor((t.dur * 0.8) / t.e.voz.split(' ').length))}));

  return (
    <AbsoluteFill style={{background: '#0B0E1A', overflow: 'hidden'}}>
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 50%, #18213D 0%, #0B0E1A 70%)'}} />
      <AbsoluteFill style={{transform: `translateX(${sx}px) scale(${z})`, filter: filtro}}>
        {tramos.map((t, i) => (
          <Sequence key={i} from={t.desde} durationInFrames={t.dur}>
            <EscenaWrap e={t.e} dur={t.dur} />
          </Sequence>
        ))}
      </AbsoluteFill>
      {ef === 'excited' && lf < 10 ? <AbsoluteFill style={{background: '#fff', opacity: 0.45 - lf * 0.045}} /> : null}
      {ef === 'pause' ? <AbsoluteFill style={{boxShadow: `inset 0 0 ${220 + 100 * pulso(f, 20, 0, 5)}px rgba(0,0,0,0.9)`}} /> : null}
      {ef === 'whispers' ? <AbsoluteFill style={{background: 'radial-gradient(circle, rgba(0,0,0,0) 35%, rgba(0,0,0,0.85) 90%)'}} /> : null}
      {tramos.map((t, i) =>
        f >= t.desde && f < t.desde + t.dur ? (
          <Titular key={i} top={t.e.visual.tipo === 'malbien' || t.e.visual.tipo === 'paso' ? 300 : 260} izquierda={t.e.visual.tipo === 'malbien' || t.e.visual.tipo === 'paso' ? 260 : 70} ancho={t.e.visual.tipo === 'malbien' || t.e.visual.tipo === 'paso' ? 760 : 940} alineacion={t.e.visual.tipo === 'malbien' || t.e.visual.tipo === 'paso' ? 'left' : 'center'} tam={t.e.visual.tipo === 'cta' ? 0.001 : 96} fuente={FUENTE.barlow} peso={900} inclinacion={-6} entrada={t.e.efecto === 'excited' ? 'golpe' : 'pop'} hasta={t.desde + t.dur}
            lineas={t.e.titulo.map((l, li) => l.map((w, wi) => ({t: w.t, en: t.desde + 1 + li * 5 + wi * 3, italica: true, color: w.c, fondo: w.fondo})))} />
        ) : null,
      )}
      <Subtitulos frases={frases} top={1500} tam={54} fuente={FUENTE.inter} peso={800} color="#fff" colorActivo="#0B0E1A" fondoActivo={VERDE} />
      <Grano opacidad={0.05} vineta={0.45} />
      {voz ? <Audio src={staticFile(`audio/${voz}`)} /> : null}
      <Audio src={staticFile('audio/base-energica-120.wav')} loop volume={voz ? 0.13 : 0.6} />
      <Efectos eventos={tramos.flatMap((t, i) => [{en: t.desde, sfx: i === 0 || t.e.efecto === 'excited' ? 'impacto' : 'whoosh', vol: 0.3}, ...(t.e.visual.tipo === 'malbien' ? [{en: t.desde + Math.round(t.dur * 0.5), sfx: 'pop', vol: 0.35}] : [])]).concat([{en: total - 8, sfx: 'swipe', vol: 0.3}])} />
    </AbsoluteFill>
  );
};

const EscenaWrap: React.FC<{e: Escena; dur: number}> = ({e, dur}) => {
  const f = useCurrentFrame();
  return <Escenario e={e} f={f} dur={dur} />;
};

// ------------------------------------------------------------------ los 4 reels
const cta: Escena = {seg: 3, titulo: [], voz: 'Escribime "REEL".', visual: {tipo: 'cta'}};

export const REEL1: PropsEditor = {
  voz: 'vo-editor1.wav',
  escenas: [
    {seg: 2.1, efecto: 'excited', titulo: [[{t: 'MISMO VIDEO.'}], [{t: 'DISTINTA EDICIÓN', fondo: VERDE, c: '#0B0E1A'}]], voz: 'Mismo video. Distinta edición.', visual: {tipo: 'split'}},
    {seg: 2.38, titulo: [[{t: 'ESTE LO PASÁS…', c: ROJO}]], voz: 'Este lo ve cualquiera y lo pasa.', visual: {tipo: 'split'}},
    {seg: 2.47, titulo: [[{t: 'ESTE LO MIRÁS', c: VERDE}], [{t: 'HASTA EL FINAL'}]], voz: 'Este… lo mirás hasta el final.', visual: {tipo: 'split'}},
    {seg: 7.91, titulo: [[{t: '¿LA DIFERENCIA?', c: AMARILLO}]], voz: '¿La diferencia? Gancho en los primeros dos segundos. Subtítulos. Y un corte cada vez que tu ojo se aburre.', visual: {tipo: 'split', destacar: ['Gancho en 2 s', 'Subtítulos', 'Cortes con ritmo']}},
    {seg: 3.44, efecto: 'pause', titulo: [[{t: 'TU NEGOCIO YA TIENE'}], [{t: 'LOS VIDEOS', c: VERDE}]], voz: 'Tu negocio ya tiene los videos. Le falta la edición.', visual: {tipo: 'tel', video: 'barberia-cruda'}},
    {...cta, seg: 3.3, voz: 'Escribime "REEL" y te muestro cómo quedaría el tuyo.'},
  ],
};

export const REEL2: PropsEditor = {
  escenas: [
    {seg: 3.2, efecto: 'excited', titulo: [[{t: 'NADIE TERMINA'}], [{t: 'TUS REELS?', fondo: ROJO, c: '#fff'}]], voz: 'Si nadie termina tus reels… es por uno de estos tres errores.', visual: {tipo: 'tel', video: 'barberia-cruda'}},
    {seg: 4.4, titulo: [[{t: 'ARRANCÁS'}], [{t: 'SALUDANDO', c: ROJO}]], voz: 'Uno: arrancás saludando. Los primeros dos segundos son para el gancho, no para el "hola".', visual: {tipo: 'malbien', num: '1', malo: 'barberia-cruda', bueno: 'barberia'}},
    {seg: 3.8, titulo: [[{t: 'SIN'}], [{t: 'SUBTÍTULOS', c: ROJO}]], voz: 'Dos: sin subtítulos. La mayoría mira sin sonido… y se va.', visual: {tipo: 'malbien', num: '2', malo: 'barberia-cruda', bueno: 'resto'}},
    {seg: 4.2, titulo: [[{t: 'PLANO'}], [{t: 'FIJO', c: ROJO}]], voz: 'Tres: plano fijo. Si la imagen no cambia cada dos o tres segundos… el pulgar sigue de largo.', visual: {tipo: 'malbien', num: '3', malo: 'barberia-cruda', bueno: 'padel'}},
    {seg: 2.0, efecto: 'pause', titulo: [[{t: '¿CUÁL COMETÉS', c: AMARILLO}], [{t: 'VOS?'}]], voz: '¿Cuál cometés vos?', visual: {tipo: 'tel', video: 'barberia-cruda'}},
    {...cta, seg: 3.4, voz: 'Guardalo. Y si querés que te lo edite yo, escribime "REEL".'},
  ],
};

export const REEL3: PropsEditor = {
  escenas: [
    {seg: 3.2, efecto: 'excited', titulo: [[{t: 'DE VIDEO COMÚN'}], [{t: 'A REEL QUE SE MIRA', c: VERDE}]], voz: 'Así convierto un video común en un reel que se mira hasta el final.', visual: {tipo: 'split'}},
    {seg: 2.6, titulo: [[{t: 'CORTO'}], [{t: 'LO QUE SOBRA', c: VERDE}]], voz: 'Paso uno: corto todo lo que sobra. Si no suma, se va.', visual: {tipo: 'paso', num: '1', video: 'barberia-cruda'}},
    {seg: 2.4, titulo: [[{t: 'EL GANCHO'}], [{t: 'ADELANTE', c: VERDE}]], voz: 'Paso dos: el gancho adelante. Lo más fuerte, primero.', visual: {tipo: 'paso', num: '2', video: 'barberia'}},
    {seg: 2.8, titulo: [[{t: 'SUBTÍTULOS'}], [{t: 'PALABRA POR PALABRA', c: VERDE}]], voz: 'Paso tres: subtítulos palabra por palabra, para que se entienda sin sonido.', visual: {tipo: 'paso', num: '3', video: 'resto', desde: 84}},
    {seg: 3.2, titulo: [[{t: 'RITMO'}], [{t: 'Y LOOP', c: VERDE}]], voz: 'Paso cuatro: ritmo. Música, efectos y un final que te devuelve al principio.', visual: {tipo: 'paso', num: '4', video: 'padel', desde: 300}},
    {seg: 1.6, efecto: 'whispers', titulo: [[{t: 'por eso lo ves dos veces', c: '#cfd6ff'}]], voz: 'Por eso lo ves dos veces.', visual: {tipo: 'tel', video: 'barberia'}},
    {...cta, seg: 3.2, efecto: 'excited', voz: 'Vos grabás. Yo edito. Escribime "REEL".'},
  ],
};

export const REEL4: PropsEditor = {
  escenas: [
    {seg: 3.0, efecto: 'excited', titulo: [[{t: 'ME MANDARON'}], [{t: 'UN AUDIO Y UNA IDEA', c: AMARILLO}]], voz: 'Un plan de estudio me mandó un audio y una idea.', visual: {tipo: 'tel', video: 'estudio3', desde: 0}},
    {seg: 2.0, titulo: [[{t: 'ESTO LES'}], [{t: 'DEVOLVÍ', c: VERDE}]], voz: 'Esto es lo que les devolví.', visual: {tipo: 'tres', videos: ['estudio1', 'estudio2', 'estudio3']}},
    {seg: 6.0, titulo: [[{t: '3 REELS', c: VERDE}], [{t: '3 FORMATOS'}]], voz: 'Una historia de 1972 con animación. Un experimento científico con marcador. Y una publicidad con cinco beneficios en veinticinco segundos.', visual: {tipo: 'tres', videos: ['estudio1', 'estudio2', 'estudio3']}},
    {seg: 2.8, efecto: 'pause', titulo: [[{t: 'SIN CÁMARAS.'}], [{t: 'SOLO EDICIÓN', c: VERDE}]], voz: 'Sin cámaras. Sin actores. Solo edición.', visual: {tipo: 'tel', video: 'estudio2', desde: 150}},
    {...cta, seg: 3.4, voz: 'Si tenés un negocio y no sabés qué subir… escribime "REEL".'},
  ],
};
