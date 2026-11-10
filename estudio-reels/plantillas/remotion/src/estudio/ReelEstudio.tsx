import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Grano} from '../componentes/Grano';
import {Subtitulos, Titular} from '../componentes/Texto';
import {pulso, resorte, tween} from '../lib/anim';
import {Efectos, Musica} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// Reel "Leitner 1972": historia → ciencia → plan de estudio → pregunta que vuelve al inicio.
// Tiempos sincronizados con la voz de ElevenLabs (vo-estudio.wav, acelerada 10%).
export const ESTUDIO_DUR = 1140;
const S = (s: number) => Math.round(s * 30);
const T = [0, 5.69, 8.56, 13.19, 15.84, 20.58, 24.3, 29.46, 32.18, 34.06, 37.4].map(S);
const LINEAS = [
  'Esto lo descubrió un alemán en 1972… y casi nadie estudia así.',
  'Sebastian Leitner metió tarjetas en una caja.',
  'Lo que sabías avanzaba… y lo volvías a ver cada vez más tarde.',
  'Lo que fallabas… volvía al principio.',
  'Tu cerebro fija lo que recordás justo antes de olvidarlo.',
  'No es estudiar más horas. Es repasar en el momento justo.',
  'Un plan que te dice qué leer cada día… y cuándo repasar.',
  'Vos seguís el plan. Tu cerebro hace el resto.',
  'Está en el link del perfil.',
  'Y ahora que lo sabés… ¿vas a seguir estudiando como antes?',
];
const SEPIA = '#F2E4C4';
const TINTA = '#2A1D12';
const VERDE = '#2BEA7A';
const ROJO = '#FF5A4E';
const CELESTE = '#58C7FF';

// ---------------------------------------------------------------- escena retro: caja de Leitner
const Caja: React.FC<{f: number}> = ({f}) => {
  const {fps} = useVideoConfig();
  const ent = resorte(f, fps, T[1] - 6, 'suave');
  const W = 860;
  const comp = W / 5;
  // tarjeta verde: avanza 1→5 durante la línea 3; tarjeta roja: vuelve a 1 en la línea 4
  const paso = Math.min(4, Math.max(0, Math.floor((f - T[2] - 8) / ((T[3] - T[2]) / 4.4))));
  const pv = f < T[2] ? 0 : paso;
  const salto = f >= T[2] ? ((f - T[2] - 8) % ((T[3] - T[2]) / 4.4)) / ((T[3] - T[2]) / 4.4) : 1;
  const xv = 110 + pv * comp + comp / 2;
  const yv = 1040 - (f >= T[2] && f < T[3] && salto < 0.5 ? Math.sin(salto * 2 * Math.PI) * 120 : 0);
  const r = tween(f, [T[3] + 10, T[3] + 40], [0, 1]);
  const xr = 110 + (3 - 3 * r) * comp + comp / 2;
  const yr = 1040 - Math.sin(r * Math.PI) * 260;
  return (
    <div style={{position: 'absolute', inset: 0, opacity: ent, transform: `translateY(${(1 - ent) * 300}px)`}}>
      {/* tarjetas cayendo (línea 2) */}
      {Array.from({length: 6}).map((_, i) => {
        const en = T[1] + 6 + i * 10;
        const s = resorte(f, fps, en, 'rebote');
        if (f < en || f >= T[2] + 4) return null;
        return (
          <div key={i} style={{position: 'absolute', left: 110 + comp / 2 - 70 + (i % 2) * 8, top: 1060 - 600 * (1 - s) - i * 6, width: 140, height: 90, background: '#FFFDF6', border: `3px solid ${TINTA}`, borderRadius: 8, transform: `rotate(${(i % 3) * 4 - 4}deg)`}} />
        );
      })}
      {/* caja */}
      <div style={{position: 'absolute', left: 110, top: 1120, width: W, height: 230, background: '#B7834A', border: `6px solid ${TINTA}`, borderRadius: 18, display: 'flex', boxShadow: '0 20px 0 rgba(42,29,18,0.25)'}}>
        {[1, 2, 3, 4, 5].map((n, i) => (
          <div key={n} style={{flex: 1, borderLeft: i ? `5px solid ${TINTA}` : 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: FUENTE.bebas, color: TINTA}}>
            <div style={{fontSize: 90, lineHeight: 0.9}}>{n}</div>
            <div style={{fontFamily: FUENTE.inter, fontWeight: 800, fontSize: 26}}>{['hoy', '+1 día', '+3 días', '+7 días', '+15 días'][i]}</div>
          </div>
        ))}
      </div>
      {f >= T[2] - 4 ? (
        <Tarjeta x={xv} y={yv} color={VERDE} texto="✓ la sabía" />
      ) : null}
      {f >= T[3] ? <Tarjeta x={xr} y={yr} color={ROJO} texto="✗ la fallé" /> : null}
    </div>
  );
};

const Tarjeta: React.FC<{x: number; y: number; color: string; texto: string}> = ({x, y, color, texto}) => (
  <div style={{position: 'absolute', left: x - 85, top: y - 60, width: 170, height: 110, background: '#FFFDF6', border: `5px solid ${color}`, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 26, color: TINTA, boxShadow: `0 0 30px ${color}88`}}>
    {texto}
  </div>
);

// ---------------------------------------------------------------- cerebro: camino que se refuerza
const NODOS: [number, number][] = [[300, 980], [420, 880], [560, 940], [680, 840], [800, 930]];
const Cerebro: React.FC<{f: number; fuerza: number; brillo?: number}> = ({f, fuerza, brillo = 1}) => (
  <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
    <defs>
      <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="10" result="b" />
        <feMerge>
          <feMergeNode in="b" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <path
      d="M 300 1180 C 160 1170, 150 1000, 230 940 C 200 820, 300 720, 420 740 C 470 660, 620 650, 680 720 C 800 690, 900 790, 870 890 C 960 960, 920 1120, 800 1140 C 760 1220, 600 1230, 540 1170 C 480 1230, 340 1240, 300 1180 Z"
      fill="rgba(88,199,255,0.06)"
      stroke={CELESTE}
      strokeWidth={5}
      opacity={0.75 * brillo}
    />
    <path d="M 540 740 C 520 860, 560 1000, 540 1170" stroke={CELESTE} strokeWidth={3} fill="none" opacity={0.35 * brillo} />
    <polyline points={NODOS.map((n) => n.join(',')).join(' ')} stroke={VERDE} strokeWidth={4 + 16 * fuerza} fill="none" strokeLinecap="round" strokeLinejoin="round" filter="url(#glow)" opacity={(0.3 + 0.7 * fuerza) * brillo} />
    {NODOS.map(([x, y], i) => (
      <circle key={i} cx={x} cy={y} r={14 + 10 * fuerza + 5 * pulso(f, 15, i * 3)} fill={VERDE} filter="url(#glow)" opacity={brillo} />
    ))}
  </svg>
);

// ---------------------------------------------------------------- curva del olvido con repasos
const Curva: React.FC<{f: number; desde: number}> = ({f, desde}) => {
  const p = tween(f, [desde, desde + 80], [0, 1], (t) => t);
  const pts: string[] = [];
  const reps = [0.25, 0.5, 0.75];
  for (let i = 0; i <= 200 * p; i++) {
    const x = i / 200;
    let ult = 0;
    let k = 0;
    for (const r of reps) if (x >= r) {ult = r; k++;}
    const decae = Math.exp(-(x - ult) * (6 / (1 + k * 1.6)));
    const piso = 0.15 + k * 0.17;
    const y = piso + (1 - piso) * decae;
    pts.push(`${120 + x * 840},${1350 - y * 420}`);
  }
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
      <line x1={120} y1={1350} x2={960} y2={1350} stroke="#ffffff55" strokeWidth={3} />
      <line x1={120} y1={1350} x2={120} y2={900} stroke="#ffffff55" strokeWidth={3} />
      <text x={130} y={890} fill="#ffffffaa" fontFamily="Inter" fontWeight={700} fontSize={30}>lo que recordás</text>
      <text x={760} y={1395} fill="#ffffffaa" fontFamily="Inter" fontWeight={700} fontSize={30}>tiempo →</text>
      <polyline points={pts.join(' ')} stroke={VERDE} strokeWidth={9} fill="none" strokeLinejoin="round" />
      {reps.map((r, i) => (p >= r ? <text key={i} x={120 + r * 840 - 50} y={1335} fill={VERDE} fontFamily="Inter" fontWeight={900} fontSize={30}>repaso</text> : null))}
    </svg>
  );
};

// ---------------------------------------------------------------- plan del día
const Plan: React.FC<{f: number}> = ({f}) => {
  const {fps} = useVideoConfig();
  const items = [
    {t: 'Leer capítulo 4', d: 'nuevo'},
    {t: 'Repasar capítulo 2', d: 'día 3'},
    {t: 'Repasar capítulo 1', d: 'día 7'},
  ];
  const ent = resorte(f, fps, T[6], 'suave');
  return (
    <div style={{position: 'absolute', left: 120, top: 720, width: 840, padding: 50, borderRadius: 48, background: '#141826', border: '2px solid #2A3047', boxShadow: '0 40px 100px rgba(0,0,0,0.5)', opacity: ent, transform: `translateY(${(1 - ent) * 200}px) scale(${0.9 + 0.1 * ent})`, fontFamily: FUENTE.inter, color: '#fff'}}>
      <div style={{fontWeight: 900, fontSize: 52}}>Hoy</div>
      <div style={{fontWeight: 600, fontSize: 30, opacity: 0.6, marginBottom: 30}}>Tu plan de estudio</div>
      {items.map((it, i) => {
        const s = resorte(f, fps, T[6] + 20 + i * 22, 'pop');
        const tilde = f >= T[7] + 8 + i * 10;
        return (
          <div key={i} style={{display: 'flex', alignItems: 'center', gap: 26, padding: '24px 0', borderTop: i ? '2px solid #232842' : 'none', opacity: Math.min(1, s * 2), transform: `translateX(${(1 - s) * 80}px)`}}>
            <div style={{width: 58, height: 58, borderRadius: 16, border: `4px solid ${tilde ? VERDE : '#3A4160'}`, background: tilde ? VERDE : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#04130a', fontWeight: 900, fontSize: 40}}>{tilde ? '✓' : ''}</div>
            <div style={{flex: 1, fontWeight: 800, fontSize: 44, textDecoration: tilde ? 'line-through' : 'none', opacity: tilde ? 0.6 : 1}}>{it.t}</div>
            <div style={{fontWeight: 800, fontSize: 28, color: it.d === 'nuevo' ? CELESTE : VERDE, border: `3px solid ${it.d === 'nuevo' ? CELESTE : VERDE}`, borderRadius: 40, padding: '6px 18px'}}>{it.d}</div>
          </div>
        );
      })}
    </div>
  );
};

export const ReelEstudio: React.FC = () => {
  const f = useCurrentFrame();
  const retro = f < T[4] || f >= ESTUDIO_DUR - 18;
  const aRetro = f >= ESTUDIO_DUR - 18 ? tween(f, [ESTUDIO_DUR - 18, ESTUDIO_DUR - 2], [0, 1]) : 1;
  const fuerza = f < T[4] ? 0 : f < T[5] ? tween(f, [T[4] + 20, T[5]], [0.15, 1]) : 1;
  const golpe = (c: number) => (f >= c && f < c + 10 ? 1 + 0.06 * Math.exp(-(f - c) / 3) : 1);
  const z = T.slice(1, 10).reduce((a, c) => a * golpe(c), 1) * (1 + 0.006 * pulso(f, 22));
  const frases = LINEAS.map((t, i) => {
    const n = t.split(' ').length;
    return {texto: t, desde: T[i] + 2, hasta: T[i + 1], paso: Math.max(3, Math.floor(((T[i + 1] - T[i]) * 0.8) / n))};
  });
  return (
    <AbsoluteFill style={{background: '#0B0E1A', overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${z})`}}>
        {/* fondo moderno */}
        <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, #18223F 0%, #0B0E1A 65%)'}} />
        {f >= T[4] && f < T[5] + 20 ? <Cerebro f={f} fuerza={fuerza} /> : null}
        {f >= T[5] && f < T[6] ? <Curva f={f} desde={T[5] + 6} /> : null}
        {f >= T[6] && f < T[8] ? <Plan f={f} /> : null}
        {f >= T[7] && f < T[10] ? <div style={{opacity: f < T[8] ? 0.35 : f < T[9] ? 0 : 1}}><Cerebro f={f} fuerza={1} brillo={f >= T[9] ? tween(f, [T[9] + 30, ESTUDIO_DUR - 20], [1, 0.25]) : 1} /></div> : null}
        {/* retro 1972 */}
        {retro ? (
          <AbsoluteFill style={{background: SEPIA, opacity: aRetro}}>
            <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, rgba(255,255,255,0.35) 0%, rgba(120,80,30,0.25) 100%)'}} />
            <div style={{position: 'absolute', top: 640, left: 0, right: 0, textAlign: 'center', fontFamily: FUENTE.bebas, fontSize: 330, color: TINTA, opacity: f < T[1] || f >= ESTUDIO_DUR - 18 ? 1 : 0.12, letterSpacing: '0.04em'}}>1972</div>
            {f >= T[1] - 6 && f < T[4] ? <Caja f={f} /> : null}
          </AbsoluteFill>
        ) : null}
      </AbsoluteFill>

      {/* titulares por escena */}
      {f < T[1] ? <Titular top={300} tam={96} fuente={FUENTE.inter} peso={900} color={TINTA} sombra="none" hasta={T[1]} lineas={[[{t: 'Casi nadie', en: -6}], [{t: 'estudia así', en: -3, fondo: TINTA, color: SEPIA}]]} /> : null}
      {f >= T[1] && f < T[3] ? <Titular top={300} tam={84} fuente={FUENTE.inter} peso={900} color={TINTA} sombra="none" hasta={T[3]} lineas={[[{t: 'La caja de', en: T[1] + 2}], [{t: 'Leitner', en: T[1] + 6, fondo: TINTA, color: SEPIA}]]} /> : null}
      {f >= T[3] && f < T[4] ? <Titular top={300} tam={84} fuente={FUENTE.inter} peso={900} color={TINTA} sombra="none" hasta={T[4]} lineas={[[{t: 'Si fallás,', en: T[3] + 2}], [{t: 'vuelve a 1', en: T[3] + 6, color: ROJO}]]} /> : null}
      {f >= T[4] && f < T[5] ? <Titular top={300} tam={92} fuente={FUENTE.inter} peso={900} hasta={T[5]} lineas={[[{t: 'Justo antes', en: T[4] + 2}], [{t: 'de olvidar', en: T[4] + 7, color: VERDE}]]} /> : null}
      {f >= T[5] && f < T[6] ? <Titular top={300} tam={86} fuente={FUENTE.inter} peso={900} hasta={T[6]} lineas={[[{t: 'Más horas', en: T[5] + 2, color: '#8A90A8'}], [{t: 'el momento justo', en: T[5] + 40, color: VERDE}]]} /> : null}
      {f >= T[6] && f < T[8] ? <Titular top={330} tam={84} fuente={FUENTE.inter} peso={900} hasta={T[8]} lineas={[[{t: 'Vos seguís el plan', en: T[6] + 2}]]} /> : null}
      {f >= T[8] && f < T[9] ? <Titular top={760} tam={120} fuente={FUENTE.inter} peso={900} hasta={T[9]} lineas={[[{t: 'Link en', en: T[8] + 1}], [{t: 'el perfil', en: T[8] + 4, color: VERDE}]]} /> : null}
      {f >= T[9] && f < ESTUDIO_DUR - 18 ? <Titular top={300} tam={84} fuente={FUENTE.inter} peso={900} hasta={ESTUDIO_DUR - 18} lineas={[[{t: '¿Vas a seguir', en: T[9] + 2}], [{t: 'estudiando', en: T[9] + 6}], [{t: 'como antes?', en: T[9] + 10, color: VERDE}]]} /> : null}

      <Subtitulos
        frases={frases}
        top={1430}
        tam={58}
        fuente={FUENTE.inter}
        peso={800}
        color="#fff"
        colorActivo="#04130a"
        fondoActivo={VERDE}
        contorno="10px rgba(0,0,0,0.85)"
      />
      <Grano opacidad={retro ? 0.1 : 0.05} vineta={0.45} />

      <Audio src={staticFile('audio/vo-estudio.wav')} volume={1} />
      <Musica archivo="base-suave-80.wav" volumen={0.16} loop />
      <Efectos
        eventos={[
          {en: T[1], sfx: 'whoosh', vol: 0.25},
          ...[0, 1, 2, 3, 4, 5].map((i) => ({en: T[1] + 6 + i * 10, sfx: 'plop', vol: 0.2})),
          {en: T[3] + 10, sfx: 'womp', vol: 0.25},
          {en: T[4], sfx: 'whoosh', vol: 0.3},
          {en: T[5], sfx: 'whoosh', vol: 0.25},
          {en: T[6], sfx: 'swipe', vol: 0.3},
          {en: T[7] + 8, sfx: 'click', vol: 0.4}, {en: T[7] + 18, sfx: 'click', vol: 0.4}, {en: T[7] + 28, sfx: 'click', vol: 0.4},
          {en: T[8], sfx: 'pop', vol: 0.3},
          {en: ESTUDIO_DUR - 18, sfx: 'swipe', vol: 0.3},
        ]}
      />
    </AbsoluteFill>
  );
};
