import React from 'react';
import {AbsoluteFill, Audio, random, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Celular} from '../componentes/Celular';
import {Grano} from '../componentes/Grano';
import {Subtitulos, Titular} from '../componentes/Texto';
import {pulso, resorte, tween} from '../lib/anim';
import {Efectos} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// "Te queda UN mes": problema → 5 beneficios → CTA → pregunta que vuelve al inicio.
export const EXAMEN_DUR = 800;
const s = (x: number) => Math.round(x * 30);
const T = [0, 2.78, 7.22, 8.93, 10.78, 12.94, 14.84, 16.72, 18.42, 20.65, 24.56, 26.66].map(s);
const LINK = s(22.59);
const RELEES = s(5.17);
const EXCITED = [0, T[3], T[9]];
const VERDE = '#2BEA7A';
const ROJO = '#FF4D5E';
const AMARILLO = '#FFD84D';
const CELESTE = '#4FC3FF';
const LINEAS = [
  'Te queda UN mes para los exámenes.',
  'Apuntes por todos lados. Leés… y al otro día, nada.',
  'Y el reloj corre.',
  'Nuestro plan de estudio online:',
  'Te dice qué estudiar cada día.',
  'Te pregunta, para que lo fijes.',
  'Te avisa cuándo repasar.',
  'Todo en el celu. Cero papeles.',
  'Ves tu avance hasta el examen.',
  'Treinta días. Un plan. Link en el perfil.',
  '¿Cuántos días te quedan?',
];

// ---------------------------------------------------------------- estudiante estresado (ilustración)
const Estudiante: React.FC<{f: number; estres: number; feliz?: boolean}> = ({f, estres, feliz}) => {
  const tiembla = estres * Math.sin(f * 1.7) * 3;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
      {/* lámpara */}
      <path d="M 840 1060 L 880 860 L 760 800" stroke="#3A3F55" strokeWidth={14} fill="none" strokeLinecap="round" />
      <path d="M 700 760 L 820 760 L 790 830 L 730 830 Z" fill="#4A506A" />
      <ellipse cx={760} cy={1120} rx={260} ry={60} fill={AMARILLO} opacity={0.09} />
      {/* persona */}
      <g transform={`translate(${tiembla} 0)`}>
        <path d="M 360 1120 C 360 960, 600 960, 600 1120 Z" fill="#3B4C8C" />
        <circle cx={480} cy={900} r={92} fill="#E3A87C" />
        <path d="M 390 880 C 380 790, 470 760, 540 790 C 600 810, 590 870, 575 880 C 540 840, 450 840, 390 880 Z" fill="#2B1D16" />
        {feliz ? (
          <>
            <path d="M 445 905 q 10 -12 20 0 M 505 905 q 10 -12 20 0" stroke="#2B1D16" strokeWidth={6} fill="none" strokeLinecap="round" />
            <path d="M 450 945 q 30 26 60 0" stroke="#2B1D16" strokeWidth={7} fill="none" strokeLinecap="round" />
          </>
        ) : (
          <>
            <circle cx={455} cy={905} r={7} fill="#2B1D16" />
            <circle cx={515} cy={905} r={7} fill="#2B1D16" />
            <path d="M 455 960 q 25 -16 50 0" stroke="#2B1D16" strokeWidth={6} fill="none" strokeLinecap="round" />
            <path d="M 435 880 l 30 8 M 535 880 l -30 8" stroke="#2B1D16" strokeWidth={6} strokeLinecap="round" />
            {/* manos en la cabeza */}
            <circle cx={385} cy={890} r={34} fill="#E3A87C" />
            <circle cx={575} cy={890} r={34} fill="#E3A87C" />
            {estres > 0.5 ? <path d="M 600 830 q 14 20 0 36" stroke={CELESTE} strokeWidth={8} fill="none" opacity={0.8} /> : null}
          </>
        )}
      </g>
      {/* escritorio */}
      <rect x={60} y={1110} width={960} height={40} rx={12} fill="#6B4A32" />
      <rect x={110} y={1150} width={40} height={360} fill="#4F3524" />
      <rect x={930} y={1150} width={40} height={360} fill="#4F3524" />
      {/* taza */}
      <rect x={800} y={1040} width={70} height={74} rx={10} fill="#E9ECF5" />
      <path d="M 870 1060 q 30 0 30 24 q 0 22 -30 22" stroke="#E9ECF5" strokeWidth={10} fill="none" />
    </svg>
  );
};

const Papeles: React.FC<{f: number; desde: number; vuelan?: number}> = ({f, desde, vuelan = 0}) => {
  const {fps} = useVideoConfig();
  return (
    <>
      {Array.from({length: 16}).map((_, i) => {
        const en = desde + i * 4;
        if (f < en) return null;
        const sp = resorte(f, fps, en, 'rebote');
        const x0 = 120 + random(`px${i}`) * 820;
        const y0 = 1010 - (i % 5) * 16 - random(`py${i}`) * 40;
        const rot = (random(`pr${i}`) - 0.5) * 50;
        const vx = (random(`vx${i}`) - 0.5) * 900 * vuelan;
        const vy = -1300 * vuelan;
        return (
          <div key={i} style={{position: 'absolute', left: x0 - 80 + vx, top: y0 - 60 - (1 - sp) * 900 + vy, width: 160, height: 120, background: i % 4 === 0 ? '#FFF3A6' : '#F6F7FB', borderRadius: 6, transform: `rotate(${rot + vuelan * 200}deg)`, boxShadow: '0 8px 20px rgba(0,0,0,0.35)', padding: '16px 14px', opacity: 1 - vuelan}}>
            {[0, 1, 2].map((k) => (
              <div key={k} style={{height: 8, background: '#B9C0D8', borderRadius: 4, marginBottom: 12, width: `${[90, 70, 80][k]}%`}} />
            ))}
          </div>
        );
      })}
    </>
  );
};

const Calendario: React.FC<{dia: number; x?: number; y?: number; esc?: number; temblor?: number; f: number}> = ({dia, x = 540, y = 760, esc = 1, temblor = 0, f}) => (
  <div style={{position: 'absolute', left: x - 170, top: y - 190, width: 340, height: 380, borderRadius: 30, background: '#fff', overflow: 'hidden', boxShadow: '0 30px 60px rgba(0,0,0,0.5)', transform: `scale(${esc}) rotate(${Math.sin(f * 1.3) * temblor}deg)`}}>
    <div style={{height: 100, background: ROJO, color: '#fff', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 44, display: 'flex', alignItems: 'center', justifyContent: 'center', letterSpacing: '0.06em'}}>FALTAN</div>
    <div style={{textAlign: 'center', fontFamily: FUENTE.barlow, fontWeight: 900, fontSize: 200, color: '#11131C', lineHeight: 1.05}}>{dia}</div>
    <div style={{textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 800, fontSize: 36, color: '#11131C', marginTop: -12}}>DÍAS</div>
  </div>
);

// ---------------------------------------------------------------- pantallas de la app (genéricas)
const Pantalla: React.FC<{b: number; f: number; ancho: number}> = ({b, f, ancho}) => {
  const u = ancho / 100;
  const base: React.CSSProperties = {position: 'absolute', inset: 0, background: '#0F1322', fontFamily: FUENTE.inter, color: '#fff', padding: `${16 * u}px ${6 * u}px`};
  const card: React.CSSProperties = {background: '#1A2035', borderRadius: 4 * u, padding: `${4 * u}px ${5 * u}px`, marginBottom: 3 * u, fontWeight: 800, fontSize: 4.6 * u};
  if (b === 0)
    return (
      <div style={base}>
        <div style={{fontWeight: 900, fontSize: 8 * u}}>Hoy</div>
        <div style={{opacity: 0.6, fontSize: 4 * u, marginBottom: 5 * u}}>Día 12 de 30</div>
        {['Bioquímica · cap. 3', 'Anatomía · repaso', 'Fisiología · preguntas'].map((t, i) => (
          <div key={i} style={{...card, opacity: tween(f, [T[4] + i * 8, T[4] + i * 8 + 8], [0, 1]), borderLeft: `${1.4 * u}px solid ${[CELESTE, VERDE, AMARILLO][i]}`}}>{t}</div>
        ))}
      </div>
    );
  if (b === 1) {
    const ok = f >= T[5] + 30;
    return (
      <div style={base}>
        <div style={{opacity: 0.6, fontSize: 4 * u, marginBottom: 4 * u}}>Pregunta 4 de 10</div>
        <div style={{...card, fontSize: 6 * u, padding: `${8 * u}px ${5 * u}px`}}>¿Qué enzima limita la glucólisis?</div>
        {['Hexoquinasa', 'Fosfofructoquinasa 1', 'Piruvato quinasa'].map((t, i) => (
          <div key={i} style={{...card, fontWeight: 700, background: ok && i === 1 ? VERDE : '#1A2035', color: ok && i === 1 ? '#0F1322' : '#fff'}}>{t}{ok && i === 1 ? '  ✓' : ''}</div>
        ))}
      </div>
    );
  }
  if (b === 2) {
    const sp = tween(f, [T[6] + 6, T[6] + 18], [0, 1]);
    return (
      <div style={base}>
        <div style={{...card, transform: `translateY(${(1 - sp) * -30 * u}px)`, opacity: sp, display: 'flex', gap: 3 * u, alignItems: 'center', border: `${0.6 * u}px solid ${AMARILLO}`}}>
          <div style={{fontSize: 9 * u}}>🔔</div>
          <div>
            <div style={{fontWeight: 900}}>Repasar hoy</div>
            <div style={{fontWeight: 600, opacity: 0.7, fontSize: 3.8 * u}}>Bioquímica cap. 1 · antes de olvidarlo</div>
          </div>
        </div>
        <div style={{marginTop: 8 * u, opacity: 0.6, fontSize: 4 * u}}>Próximos repasos</div>
        {['Mañana · Anatomía', 'En 3 días · Fisiología', 'En 7 días · Bioquímica'].map((t, i) => (
          <div key={i} style={{...card, fontWeight: 700}}>{t}</div>
        ))}
      </div>
    );
  }
  if (b === 3)
    return (
      <div style={{...base, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 4 * u}}>
        <div style={{fontWeight: 900, fontSize: 16 * u, color: VERDE}}>0</div>
        <div style={{fontWeight: 800, fontSize: 6 * u}}>papeles perdidos</div>
        <div style={{opacity: 0.6, fontSize: 4 * u}}>apuntes, preguntas y repasos en un lugar</div>
      </div>
    );
  const p = tween(f, [T[8] + 4, T[9] - 6], [0.2, 1]);
  return (
    <div style={{...base, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
      <svg width={60 * u} height={60 * u} viewBox="0 0 100 100">
        <circle cx={50} cy={50} r={40} stroke="#1A2035" strokeWidth={12} fill="none" />
        <circle cx={50} cy={50} r={40} stroke={VERDE} strokeWidth={12} fill="none" strokeDasharray={`${251 * p} 251`} strokeLinecap="round" transform="rotate(-90 50 50)" />
        <text x={50} y={58} textAnchor="middle" fill="#fff" fontFamily="Inter" fontWeight={900} fontSize={22}>{Math.round(p * 100)}%</text>
      </svg>
      <div style={{fontWeight: 800, fontSize: 5.5 * u, marginTop: 4 * u}}>temario estudiado</div>
    </div>
  );
};

const BENEF = [
  {n: '1', t: 'QUÉ ESTUDIAR HOY', c: CELESTE},
  {n: '2', t: 'PREGUNTAS, NO RELEER', c: VERDE},
  {n: '3', t: 'REPASO A TIEMPO', c: AMARILLO},
  {n: '4', t: 'TODO EN EL CELU', c: CELESTE},
  {n: '5', t: 'TU AVANCE', c: VERDE},
];

export const ReelExamen: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const susurro = f >= T[2] && f < T[3];
  const pausa = f >= T[10];
  let sx = 0, sy = 0, z = 1;
  for (const e of EXCITED) {
    const t = f - e;
    if (t >= 0 && t < 14) {
      const a = 20 * Math.exp(-t / 4);
      sx += (random(`x${f}`) - 0.5) * a;
      sy += (random(`y${f}`) - 0.5) * a;
      z *= 1 + 0.1 * Math.exp(-t / 4);
    }
  }
  for (const c of T.slice(1, 11)) if (f >= c && f < c + 8) z *= 1 + 0.05 * Math.exp(-(f - c) / 3);
  z *= 1 + 0.008 * pulso(f, 15);
  const b = f >= T[4] && f < T[9] ? Math.min(4, T.slice(4, 9).filter((x) => f >= x).length - 1) : -1;
  const diaCuenta = f < T[2] ? 30 : f < T[3] ? 30 - Math.min(9, Math.floor((f - T[2]) / 6)) : 30;
  const frases = LINEAS.map((t, i) => ({texto: t, desde: T[i] + 1, hasta: T[i + 1], paso: Math.max(3, Math.floor(((T[i + 1] - T[i]) * 0.8) / t.split(' ').length))}));
  const telIn = resorte(f, fps, T[3] + 8, 'pop');

  return (
    <AbsoluteFill style={{background: '#0C0F1C', overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${z})`, filter: susurro ? 'brightness(0.45) saturate(0.6)' : pausa ? 'saturate(0.5)' : 'none'}}>
        <AbsoluteFill style={{background: 'radial-gradient(circle at 60% 55%, #1E2747 0%, #0C0F1C 70%)'}} />
        {/* problema */}
        {f < T[4] ? <Estudiante f={f} estres={f < T[3] ? 1 : 0.3} /> : null}
        {f >= T[1] && f < T[4] ? <Papeles f={f} desde={T[1]} vuelan={tween(f, [T[3], T[3] + 20], [0, 1])} /> : null}
        {f < T[1] || pausa ? <Calendario f={f} dia={30} x={800} y={720} esc={0.85} temblor={6} /> : null}
        {f >= T[2] && f < T[3] ? <Calendario f={f} dia={diaCuenta} x={800} y={720} esc={0.85} /> : null}
        {f >= RELEES && f < T[2] ? (
          <div style={{position: 'absolute', left: 560, top: 560, width: 300, height: 190, borderRadius: 100, background: '#fff', opacity: 0.95, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10}}>
            {Array.from({length: 5}).map((_, i) => (
              <div key={i} style={{width: 34, height: 12, borderRadius: 6, background: '#9AA3C2', opacity: tween(f, [RELEES + 14 + i * 4, RELEES + 20 + i * 4], [1, 0])}} />
            ))}
            <div style={{position: 'absolute', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 70, color: ROJO, opacity: tween(f, [RELEES + 36, RELEES + 42], [0, 1])}}>?</div>
          </div>
        ) : null}
        {/* solución: celular */}
        {f >= T[3] + 8 && f < T[9] ? (
          <div style={{position: 'absolute', left: 540 - 230, top: 640 + (1 - telIn) * 900, transform: `rotate(${(1 - telIn) * 12}deg)`}}>
            <Celular ancho={460} ejemplo={false} mezclaPantalla={1} pantalla={b >= 0 ? <Pantalla b={b} f={f} ancho={460 * 0.93} /> : <div style={{position: 'absolute', inset: 0, background: '#0F1322', display: 'flex', alignItems: 'center', justifyContent: 'center', color: VERDE, fontFamily: FUENTE.barlow, fontWeight: 900, fontStyle: 'italic', fontSize: 60, textAlign: 'center'}}>PLAN DE<br />ESTUDIO</div>} />
          </div>
        ) : null}
        {/* 30 días completos */}
        {f >= T[9] && f < T[10] ? (
          <div style={{position: 'absolute', left: 150, top: 650, width: 780, display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 14}}>
            {Array.from({length: 30}).map((_, i) => {
              const on = f >= T[9] + 4 + i * 1.6;
              return (
                <div key={i} style={{height: 100, borderRadius: 18, background: on ? VERDE : '#1A2035', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 42, color: on ? '#0C0F1C' : '#4A5378', transform: `scale(${on ? 1 + 0.15 * Math.exp(-(f - T[9] - 4 - i * 1.6) / 3) : 1})`}}>{on ? '✓' : i + 1}</div>
              );
            })}
          </div>
        ) : null}
        {f >= T[9] && f < T[10] ? <div style={{opacity: 0.0}} /> : null}
      </AbsoluteFill>
      {susurro ? <AbsoluteFill style={{background: 'radial-gradient(circle, rgba(0,0,0,0) 35%, rgba(0,0,0,0.85) 90%)'}} /> : null}
      {pausa ? <AbsoluteFill style={{boxShadow: `inset 0 0 ${220 + 100 * pulso(f, 20, 0, 5)}px rgba(0,0,0,0.9)`}} /> : null}
      {EXCITED.map((e, i) => {
        const t = f - e;
        if (t < 0 || t > 10) return null;
        return <AbsoluteFill key={i} style={{background: '#fff', opacity: 0.5 - t * 0.05}} />;
      })}

      {/* titulares */}
      {f < T[1] || pausa ? (
        <Titular top={250} tam={120} fuente={FUENTE.barlow} peso={900} inclinacion={-6} entrada="golpe"
          lineas={pausa ? [[{t: '¿CUÁNTOS DÍAS', en: T[10] + 2, italica: true}], [{t: 'TE QUEDAN?', en: T[10] + 8, italica: true, color: AMARILLO}]] : [[{t: 'TE QUEDA', en: -6, italica: true}], [{t: 'UN MES', en: -3, italica: true, fondo: ROJO, color: '#fff'}]]} />
      ) : null}
      {f >= T[1] && f < T[2] ? <Titular top={260} tam={96} fuente={FUENTE.barlow} peso={900} inclinacion={-6} hasta={T[2]} lineas={f < RELEES ? [[{t: 'APUNTES', en: T[1] + 2, italica: true}], [{t: 'POR TODOS LADOS', en: T[1] + 8, italica: true, color: AMARILLO}]] : [[{t: 'LEÉS…', en: RELEES, italica: true}], [{t: 'Y AL OTRO DÍA, NADA', en: RELEES + 14, italica: true, color: ROJO}]]} /> : null}
      {susurro ? <Titular top={300} tam={64} fuente={FUENTE.inter} peso={600} color="#cfd6ff" sombra="none" lineas={[[{t: 'y el reloj corre…', en: T[2] + 2, italica: true}]]} /> : null}
      {f >= T[3] && f < T[4] ? <Titular top={260} tam={96} fuente={FUENTE.barlow} peso={900} inclinacion={-6} entrada="golpe" hasta={T[4]} lineas={[[{t: 'TU PLAN DE', en: T[3] + 2, italica: true}], [{t: 'ESTUDIO ONLINE', en: T[3] + 6, italica: true, fondo: VERDE, color: '#0C0F1C'}]]} /> : null}
      {b >= 0 ? (
        <div style={{position: 'absolute', top: 250, left: 70, right: 70, display: 'flex', alignItems: 'center', gap: 26, justifyContent: 'center'}}>
          <div key={`n${b}`} style={{width: 150, height: 150, borderRadius: '50%', background: BENEF[b].c, color: '#0C0F1C', fontFamily: FUENTE.barlow, fontWeight: 900, fontSize: 110, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${0.6 + 0.4 * resorte(f, fps, T[4 + b], 'rebote')})`, boxShadow: `0 0 40px ${BENEF[b].c}88`}}>{BENEF[b].n}</div>
          <div style={{fontFamily: FUENTE.barlow, fontWeight: 900, fontStyle: 'italic', fontSize: 84, color: '#fff', lineHeight: 0.95, maxWidth: 640, transform: `translateX(${(1 - resorte(f, fps, T[4 + b] + 2, 'pop')) * 120}px)`}}>{BENEF[b].t}</div>
        </div>
      ) : null}
      {f >= T[9] && f < T[10] ? <Titular top={260} tam={110} fuente={FUENTE.barlow} peso={900} inclinacion={-6} entrada="golpe" lineas={f < LINK ? [[{t: '30 DÍAS.', en: T[9] + 2, italica: true}, {t: '1 PLAN.', en: T[9] + 20, italica: true, color: VERDE}]] : [[{t: 'LINK EN', en: LINK, italica: true}], [{t: 'EL PERFIL', en: LINK + 3, italica: true, fondo: VERDE, color: '#0C0F1C'}]]} /> : null}

      <Subtitulos frases={frases} top={1500} tam={56} fuente={FUENTE.inter} peso={800} color="#fff" colorActivo="#0C0F1C" fondoActivo={VERDE} />
      <Grano opacidad={0.05} vineta={0.45} />

      <Audio src={staticFile('audio/vo-examen.wav')} volume={1} />
      <Audio src={staticFile('audio/base-energica-120.wav')} loop volume={(fr) => (fr >= T[2] && fr < T[3]) || fr >= T[10] ? 0.04 : 0.13} />
      <Efectos
        eventos={[
          {en: 0, sfx: 'impacto', vol: 0.35},
          ...Array.from({length: 8}).map((_, i) => ({en: T[1] + i * 8, sfx: 'plop', vol: 0.18})),
          {en: RELEES + 36, sfx: 'womp', vol: 0.3},
          ...Array.from({length: 8}).map((_, i) => ({en: T[2] + i * 6, sfx: 'tick', vol: 0.4})),
          {en: T[3], sfx: 'impacto', vol: 0.4},
          {en: T[3] + 8, sfx: 'whoosh', vol: 0.3},
          ...[4, 5, 6, 7, 8].map((k) => ({en: T[k], sfx: 'pop', vol: 0.35})),
          {en: T[6] + 6, sfx: 'ding', vol: 0.3},
          {en: T[9], sfx: 'impacto', vol: 0.4},
          {en: LINK, sfx: 'golpe', vol: 0.35},
          {en: EXAMEN_DUR - 10, sfx: 'swipe', vol: 0.3},
        ]}
      />
    </AbsoluteFill>
  );
};
