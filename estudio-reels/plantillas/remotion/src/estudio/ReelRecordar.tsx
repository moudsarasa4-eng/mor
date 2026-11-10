import React from 'react';
import {AbsoluteFill, Audio, interpolate, random, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Grano} from '../componentes/Grano';
import {Subtitulos, Titular} from '../componentes/Texto';
import {pulso, resorte, tween} from '../lib/anim';
import {Efectos} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// "Tu forma de estudiar está mal": práctica de recuperación (Roediger y Karpicke, 2006).
// Las etiquetas de ElevenLabs se ven: [excited] = sacudón + destello + estallido, [pause] = congelado,
// [whispers] = viñeta y texto chico.
export const RECORDAR_DUR = 1228;
const s = (x: number) => Math.round(x * 30);
const T = [0, 4.68, 8.05, 10.63, 15.11, 16.21, 18.63, 23.48, 28.67, 35.2, 36.69, 37.94, 40.4].map(s);
const SUSURRO = s(26.91);
const EXCITED = [0, T[5], T[8]];
const PAUSAS: [number, number][] = [[T[4], T[5]], [T[11], RECORDAR_DUR - 14]];
const LINEAS = [
  'Tu forma de estudiar… está mal. Y la ciencia lo probó.',
  '2006. Dos grupos de estudiantes. Mismo texto.',
  'Grupo uno: lo lee… y lo relee… y lo relee.',
  'Grupo dos: lo lee UNA vez. Cierra el libro. Y trata de recordar.',
  'Una semana después…',
  '¡Gana el grupo dos!',
  '¿Por qué? Porque cada vez que sacás algo de tu memoria… tu cerebro lo graba más fuerte.',
  'Releer se siente fácil. Recordar cuesta. Y justo por eso funciona.',
  'Por eso nuestro plan no te hace leer más: te hace preguntas. Todos los días. En el momento justo.',
  'Vos respondés. Tu cerebro hace el resto.',
  'Link en el perfil.',
  'Ahora decime… ¿vos seguís releyendo?',
];
const VERDE = '#2BEA7A';
const CELESTE = '#4FC3FF';
const ROJO = '#FF4D5E';
const AMARILLO = '#FFD84D';
const enRango = (f: number, [a, b]: [number, number]) => f >= a && f < b;

// ---------------------------------------------------------------- efectos de las etiquetas
const Estallido: React.FC<{f: number; en: number; color: string}> = ({f, en, color}) => {
  const t = f - en;
  if (t < 0 || t > 26) return null;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill style={{background: '#fff', opacity: Math.max(0, 0.55 - t * 0.09)}} />
      {Array.from({length: 26}).map((_, i) => {
        const a = random(`ea${en}${i}`) * Math.PI * 2;
        const v = 30 + random(`ev${en}${i}`) * 40;
        const d = v * t * (1 - t / 60);
        const sz = 10 + random(`es${en}${i}`) * 18;
        return (
          <div key={i} style={{position: 'absolute', left: 540 + Math.cos(a) * d - sz / 2, top: 960 + Math.sin(a) * d - sz / 2, width: sz, height: i % 3 ? sz : sz * 2.6, borderRadius: i % 2 ? '50%' : 4, background: [color, '#fff', AMARILLO][i % 3], opacity: 1 - t / 26, transform: `rotate(${t * 20 + i * 40}deg)`}} />
        );
      })}
      <div style={{position: 'absolute', left: 540 - t * 40, top: 960 - t * 40, width: t * 80, height: t * 80, borderRadius: '50%', border: `${Math.max(2, 18 - t)}px solid ${color}`, opacity: 1 - t / 26}} />
    </AbsoluteFill>
  );
};

const Reloj: React.FC<{f: number; desde: number}> = ({f, desde}) => {
  const t = f - desde;
  return (
    <div style={{position: 'absolute', left: 340, top: 720, width: 400, height: 400}}>
      <svg width={400} height={400} viewBox="0 0 400 400">
        <circle cx={200} cy={200} r={180} fill="#111522" stroke="#fff" strokeWidth={14} />
        {Array.from({length: 12}).map((_, i) => (
          <line key={i} x1={200} y1={40} x2={200} y2={66} stroke="#fff" strokeWidth={8} transform={`rotate(${i * 30} 200 200)`} />
        ))}
        <line x1={200} y1={200} x2={200} y2={70} stroke={AMARILLO} strokeWidth={12} strokeLinecap="round" transform={`rotate(${t * 48} 200 200)`} />
        <line x1={200} y1={200} x2={200} y2={110} stroke="#fff" strokeWidth={14} strokeLinecap="round" transform={`rotate(${t * 4} 200 200)`} />
        <circle cx={200} cy={200} r={14} fill={AMARILLO} />
      </svg>
    </div>
  );
};

// ---------------------------------------------------------------- piezas visuales
const Persona: React.FC<{color: string; x: number; y: number; s?: number}> = ({color, x, y, s: sc = 1}) => (
  <div style={{position: 'absolute', left: x - 50 * sc, top: y - 60 * sc, width: 100 * sc, height: 130 * sc}}>
    <div style={{width: 64 * sc, height: 64 * sc, borderRadius: '50%', background: color, margin: '0 auto'}} />
    <div style={{width: 100 * sc, height: 56 * sc, borderRadius: `${50 * sc}px ${50 * sc}px 12px 12px`, background: color, marginTop: 8 * sc}} />
  </div>
);

const Hoja: React.FC<{x: number; y: number; rot?: number; op?: number; color?: string}> = ({x, y, rot = 0, op = 1, color = '#F4F6FF'}) => (
  <div style={{position: 'absolute', left: x - 70, top: y - 90, width: 140, height: 180, background: color, borderRadius: 12, transform: `rotate(${rot}deg)`, opacity: op, boxShadow: '0 12px 30px rgba(0,0,0,0.4)', padding: '26px 18px'}}>
    {[0, 1, 2, 3, 4].map((i) => (
      <div key={i} style={{height: 10, background: '#B9C0D8', borderRadius: 5, marginBottom: 14, width: `${[100, 85, 95, 70, 60][i]}%`}} />
    ))}
  </div>
);

const Carriles: React.FC<{f: number}> = ({f}) => {
  const {fps} = useVideoConfig();
  const e1 = resorte(f, fps, T[1] + 8, 'pop');
  const e2 = resorte(f, fps, T[1] + 16, 'pop');
  const relee = f >= T[2] ? Math.min(3, 1 + Math.floor((f - T[2]) / ((T[3] - T[2]) / 3))) : 0;
  const cierra = tween(f, [T[3] + 30, T[3] + 50], [0, 1]);
  const piensa = f >= T[3] + 70;
  const foco1 = f >= T[2] && f < T[3];
  const foco2 = f >= T[3];
  return (
    <>
      {[0, 1].map((i) => {
        const col = i ? VERDE : CELESTE;
        const e = i ? e2 : e1;
        const foco = i ? foco2 : foco1;
        const x = i ? 780 : 300;
        return (
          <div key={i} style={{position: 'absolute', left: x - 220, top: 640, width: 440, height: 700, borderRadius: 40, border: `5px solid ${col}`, background: `${col}12`, opacity: e * (f >= T[2] && !foco ? 0.35 : 1), transform: `translateY(${(1 - e) * 300}px) scale(${foco ? 1.04 : 1})`, boxShadow: foco ? `0 0 60px ${col}66` : 'none'}}>
            <div style={{textAlign: 'center', marginTop: 26, fontFamily: FUENTE.barlow, fontWeight: 900, fontStyle: 'italic', fontSize: 74, color: col}}>GRUPO {i + 1}</div>
          </div>
        );
      })}
      <Persona color={CELESTE} x={300} y={830} />
      <Persona color={VERDE} x={780} y={830} />
      {/* grupo 1: relee x3 */}
      {[0, 1, 2].map((k) => (relee > k || f < T[2] ? <Hoja key={k} x={300 + k * 18} y={1100 + k * -14} rot={(k - 1) * 6} op={f < T[2] && k > 0 ? 0 : 1} /> : null))}
      {f >= T[2] ? (
        <div style={{position: 'absolute', left: 120, top: 1240, width: 360, textAlign: 'center', fontFamily: FUENTE.barlow, fontWeight: 900, fontStyle: 'italic', fontSize: 92, color: CELESTE, transform: `scale(${1 + 0.15 * pulso(f - T[2], Math.round((T[3] - T[2]) / 3), 0, 4)})`}}>RELEE ×{relee}</div>
      ) : null}
      {/* grupo 2: lee una vez, cierra, recuerda */}
      {f >= T[3] || f < T[2] ? <Hoja x={780} y={1100} op={1 - cierra} rot={cierra * 80} /> : <Hoja x={780} y={1100} />}
      {f >= T[3] + 30 ? (
        <div style={{position: 'absolute', left: 700, top: 1030, width: 160, height: 140, borderRadius: 10, background: '#7A4CFF', transform: `scaleX(${cierra})`, boxShadow: '0 12px 30px rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 30}}>LIBRO</div>
      ) : null}
      {piensa
        ? ['?', '?', '?'].map((q, k) => {
            const sp = resorte(f, fps, T[3] + 70 + k * 6, 'rebote');
            return (
              <div key={k} style={{position: 'absolute', left: 690 + k * 70, top: 900 - k * 20 - sp * 40, fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 80, color: AMARILLO, opacity: sp}}>{q}</div>
            );
          })
        : null}
      {f >= T[3] + 70 ? <div style={{position: 'absolute', left: 580, top: 1240, width: 400, textAlign: 'center', fontFamily: FUENTE.barlow, fontWeight: 900, fontStyle: 'italic', fontSize: 80, color: VERDE}}>RECUERDA</div> : null}
    </>
  );
};

const Marcador: React.FC<{f: number}> = ({f}) => {
  const p = tween(f, [T[5] + 4, T[5] + 30], [0, 1]);
  const vals = [
    {n: 'GRUPO 1 · releyó', v: 42, c: CELESTE},
    {n: 'GRUPO 2 · se puso a prueba', v: 56, c: VERDE},
  ];
  return (
    <div style={{position: 'absolute', left: 110, top: 760, width: 860, fontFamily: FUENTE.inter, color: '#fff'}}>
      <div style={{fontWeight: 700, fontSize: 30, opacity: 0.7, marginBottom: 20}}>Cuánto recordaban 1 semana después</div>
      {vals.map((v) => (
        <div key={v.n} style={{marginBottom: 40}}>
          <div style={{fontWeight: 800, fontSize: 38, marginBottom: 12}}>{v.n}</div>
          <div style={{height: 110, background: '#1A2035', borderRadius: 18, overflow: 'hidden'}}>
            <div style={{width: `${v.v * p}%`, height: '100%', background: v.c, borderRadius: 18, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingRight: 24, fontWeight: 900, fontSize: 60, color: '#0B0E1A', boxShadow: `0 0 40px ${v.c}88`}}>
              {p > 0.3 ? `${Math.round(v.v * p)}%` : ''}
            </div>
          </div>
        </div>
      ))}
      <div style={{fontWeight: 600, fontSize: 24, opacity: 0.55}}>Fuente: Roediger y Karpicke (2006), Psychological Science, experimento 1. Escala desde 0.</div>
    </div>
  );
};

const Cerebro: React.FC<{f: number; fuerza: number; tirones?: number[]}> = ({f, fuerza, tirones = []}) => (
  <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
    <defs>
      <filter id="g2" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="12" result="b" />
        <feMerge>
          <feMergeNode in="b" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <path d="M 300 1180 C 160 1170, 150 1000, 230 940 C 200 820, 300 720, 420 740 C 470 660, 620 650, 680 720 C 800 690, 900 790, 870 890 C 960 960, 920 1120, 800 1140 C 760 1220, 600 1230, 540 1170 C 480 1230, 340 1240, 300 1180 Z" fill="rgba(79,195,255,0.07)" stroke={CELESTE} strokeWidth={6} />
    <polyline points="300,980 420,880 560,940 680,840 800,930" stroke={VERDE} strokeWidth={4 + 20 * fuerza} fill="none" strokeLinecap="round" strokeLinejoin="round" filter="url(#g2)" opacity={0.3 + 0.7 * fuerza} />
    {tirones.map((en, i) => {
      const t = f - en;
      if (t < 0 || t > 24) return null;
      return <circle key={i} cx={560} cy={940 - t * 22} r={26} fill={AMARILLO} filter="url(#g2)" opacity={1 - t / 24} />;
    })}
  </svg>
);

const Preguntas: React.FC<{f: number}> = ({f}) => {
  const {fps} = useVideoConfig();
  const qs = ['¿Qué hace la mitocondria?', '¿Año de la Revolución de Mayo?', '¿Fórmula del área del círculo?'];
  const dias = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];
  return (
    <div style={{position: 'absolute', left: 110, top: 640, width: 860, fontFamily: FUENTE.inter, color: '#fff'}}>
      {qs.map((q, i) => {
        const en = T[8] + 10 + i * 30;
        const sp = resorte(f, fps, en, 'rebote');
        const ok = f >= en + 22;
        return (
          <div key={i} style={{display: 'flex', alignItems: 'center', gap: 22, background: '#151A2C', border: `4px solid ${ok ? VERDE : '#2A3150'}`, borderRadius: 28, padding: '26px 30px', marginBottom: 22, opacity: Math.min(1, sp * 2), transform: `translateX(${(1 - sp) * (i % 2 ? 300 : -300)}px)`}}>
            <div style={{flex: 1, fontWeight: 800, fontSize: 42}}>{q}</div>
            <div style={{width: 70, height: 70, borderRadius: '50%', background: ok ? VERDE : 'transparent', border: `5px solid ${ok ? VERDE : '#3A4268'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 44, color: '#0B0E1A'}}>{ok ? '✓' : ''}</div>
          </div>
        );
      })}
      <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 34}}>
        {dias.map((d, i) => {
          const on = f >= T[8] + 110 + i * 7;
          return (
            <div key={i} style={{width: 100, height: 100, borderRadius: 24, background: on ? AMARILLO : '#1A2035', color: on ? '#0B0E1A' : '#5A6488', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 44, transform: `scale(${on ? 1 + 0.12 * Math.exp(-(f - T[8] - 110 - i * 7) / 4) : 1})`, boxShadow: on ? `0 0 30px ${AMARILLO}88` : 'none'}}>{d}</div>
          );
        })}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- reel
export const ReelRecordar: React.FC = () => {
  const f = useCurrentFrame();
  const enPausa = PAUSAS.some((p) => enRango(f, p));
  const susurro = f >= SUSURRO && f < T[8];
  // [excited]: sacudón + zoom
  let sx = 0, sy = 0, z = 1;
  for (const e of EXCITED) {
    const t = f - e;
    if (t >= 0 && t < 16) {
      const a = 22 * Math.exp(-t / 5);
      sx += (random(`sx${f}`) - 0.5) * a;
      sy += (random(`sy${f}`) - 0.5) * a;
      z *= 1 + 0.12 * Math.exp(-t / 4);
    }
  }
  for (const c of T.slice(1, 12)) if (f >= c && f < c + 8) z *= 1 + 0.05 * Math.exp(-(f - c) / 3);
  if (enPausa) z *= 1 + 0.0015 * (f - (PAUSAS.find((p) => enRango(f, p)) as [number, number])[0]);
  else z *= 1 + 0.01 * pulso(f, 15);
  const filtro = enPausa ? 'saturate(0.25) brightness(0.7)' : susurro ? 'brightness(0.6)' : 'none';
  const loopIn = f >= RECORDAR_DUR - 14;
  const frases = LINEAS.map((t, i) => ({texto: t, desde: T[i] + 2, hasta: T[i + 1], paso: Math.max(3, Math.floor(((T[i + 1] - T[i]) * 0.82) / t.split(' ').length))}));
  const musicaVol = (fr: number) => (PAUSAS.some((p) => enRango(fr, p)) || (fr >= SUSURRO && fr < T[8]) ? 0.04 : 0.13);

  return (
    <AbsoluteFill style={{background: '#0B0E1A', overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${z})`, filter: filtro}}>
        <AbsoluteFill style={{background: `radial-gradient(circle at 50% 45%, ${f < T[1] || loopIn ? '#3A0F1A' : '#17213F'} 0%, #0B0E1A 70%)`}} />
        {/* S1 / loop: "está mal" */}
        {(f < T[1] || loopIn) && (
          <div style={{position: 'absolute', left: 390, top: 860, width: 300, height: 380}}>
            <Hoja x={150} y={190} rot={-6} />
            <div style={{position: 'absolute', inset: -20, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 340, color: ROJO, transform: `scale(${loopIn ? 1 : 1 + 0.6 * Math.exp(-f / 4)}) rotate(-8deg)`, textShadow: `0 0 50px ${ROJO}`}}>✗</div>
          </div>
        )}
        {f >= T[1] && f < T[1] + 40 ? <div style={{position: 'absolute', top: 360, left: 0, right: 0, textAlign: 'center', fontFamily: FUENTE.barlow, fontWeight: 900, fontStyle: 'italic', fontSize: 300, color: '#fff', opacity: tween(f, [T[1] + 30, T[1] + 40], [1, 0])}}>2006</div> : null}
        {f >= T[1] && f < T[4] ? <Carriles f={f} /> : null}
        {enRango(f, PAUSAS[0]) ? <Reloj f={f} desde={T[4]} /> : null}
        {f >= T[5] && f < T[6] ? <Marcador f={f} /> : null}
        {f >= T[6] && f < T[7] ? <Cerebro f={f} fuerza={tween(f, [T[6], T[7] - 20], [0.15, 1])} tirones={[T[6] + 30, T[6] + 70, T[6] + 110]} /> : null}
        {f >= T[7] && f < T[8] ? (
          <div style={{position: 'absolute', left: 90, top: 760, width: 900, display: 'flex', gap: 30}}>
            {[{t: 'RELEER', d: 'se siente fácil', c: CELESTE, v: 25}, {t: 'RECORDAR', d: 'cuesta', c: VERDE, v: 90}].map((b, i) => (
              <div key={i} style={{flex: 1, textAlign: 'center', fontFamily: FUENTE.barlow, color: b.c}}>
                <div style={{fontWeight: 900, fontStyle: 'italic', fontSize: 100}}>{b.t}</div>
                <div style={{fontFamily: FUENTE.inter, fontWeight: 700, fontSize: 38, color: '#fff', opacity: 0.8}}>{b.d}</div>
                <div style={{fontFamily: FUENTE.inter, fontWeight: 700, fontSize: 26, color: '#fff', opacity: 0.5, marginTop: 30}}>esfuerzo</div>
                <div style={{height: 34, background: '#1A2035', borderRadius: 17, marginTop: 10, overflow: 'hidden'}}>
                  <div style={{width: `${b.v * tween(f, [T[7] + 10 + i * 30, T[7] + 40 + i * 30], [0, 1])}%`, height: '100%', background: b.c}} />
                </div>
              </div>
            ))}
          </div>
        ) : null}
        {f >= T[8] && f < T[9] ? <Preguntas f={f} /> : null}
        {f >= T[9] && f < T[10] ? <Cerebro f={f} fuerza={1} tirones={[T[9] + 4, T[9] + 20]} /> : null}
        {f >= T[11] && !loopIn ? <Cerebro f={f} fuerza={0.4} /> : null}
      </AbsoluteFill>

      {/* [whispers]: viñeta */}
      {susurro ? <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.85) 90%)'}} /> : null}
      {/* [pause]: latido */}
      {enPausa ? <AbsoluteFill style={{boxShadow: `inset 0 0 ${200 + 120 * pulso(f, 20, 0, 5)}px rgba(0,0,0,0.9)`}} /> : null}
      {EXCITED.map((e, i) => (
        <Estallido key={i} f={f} en={e} color={[ROJO, VERDE, AMARILLO][i]} />
      ))}

      {/* titulares grandes */}
      {(f < T[1] || loopIn) && <Titular top={290} tam={110} fuente={FUENTE.barlow} peso={900} inclinacion={-6} entrada="golpe" hasta={loopIn ? undefined : T[1]} lineas={[[{t: 'TU FORMA DE', en: loopIn ? RECORDAR_DUR - 14 : -6, italica: true}], [{t: 'ESTUDIAR', en: loopIn ? RECORDAR_DUR - 12 : -4, italica: true}], [{t: 'ESTÁ MAL', en: loopIn ? RECORDAR_DUR - 10 : 4, italica: true, fondo: ROJO, color: '#fff'}]]} />}
      {f >= T[1] + 40 && f < T[4] ? <Titular top={330} tam={84} fuente={FUENTE.barlow} peso={900} inclinacion={-6} hasta={T[4]} lineas={[[{t: f < T[2] ? 'MISMO TEXTO' : f < T[3] ? 'LEE Y RELEE' : 'LEE UNA VEZ Y RECUERDA', en: f < T[2] ? T[1] + 40 : f < T[3] ? T[2] : T[3], italica: true, color: f < T[3] && f >= T[2] ? CELESTE : f >= T[3] ? VERDE : undefined}]]} /> : null}
      {enRango(f, PAUSAS[0]) ? <Titular top={330} tam={110} fuente={FUENTE.barlow} peso={900} inclinacion={-6} lineas={[[{t: '1 SEMANA', en: T[4], italica: true, color: AMARILLO}], [{t: 'DESPUÉS…', en: T[4] + 6, italica: true}]]} /> : null}
      {f >= T[5] && f < T[6] ? <Titular top={300} tam={130} fuente={FUENTE.barlow} peso={900} inclinacion={-6} entrada="golpe" hasta={T[6]} lineas={[[{t: '¡GANA EL', en: T[5], italica: true}, {t: '2!', en: T[5] + 3, italica: true, fondo: VERDE, color: '#0B0E1A'}]]} /> : null}
      {f >= T[6] && f < T[7] ? <Titular top={300} tam={92} fuente={FUENTE.barlow} peso={900} inclinacion={-6} hasta={T[7]} lineas={[[{t: 'RECORDAR', en: T[6] + 4, italica: true, color: AMARILLO}], [{t: '= GRABAR MÁS FUERTE', en: T[6] + 40, italica: true}]]} /> : null}
      {susurro ? <Titular top={1260} tam={52} fuente={FUENTE.inter} peso={600} color="#cfd6ff" sombra="none" lineas={[[{t: 'y justo por eso funciona', en: SUSURRO + 2, italica: true}]]} /> : null}
      {f >= T[8] && f < T[9] ? <Titular top={300} tam={96} fuente={FUENTE.barlow} peso={900} inclinacion={-6} entrada="golpe" hasta={T[9]} lineas={[[{t: 'NO LEER MÁS:', en: T[8], italica: true}], [{t: 'TE PREGUNTA', en: T[8] + 5, italica: true, fondo: AMARILLO, color: '#0B0E1A'}]]} /> : null}
      {f >= T[9] && f < T[10] ? <Titular top={330} tam={96} fuente={FUENTE.barlow} peso={900} inclinacion={-6} hasta={T[10]} lineas={[[{t: 'VOS RESPONDÉS', en: T[9], italica: true}], [{t: 'TU CEREBRO HACE EL RESTO', en: T[9] + 14, italica: true, color: VERDE, rel: 0.7}]]} /> : null}
      {f >= T[10] && f < T[11] ? <Titular top={760} tam={150} fuente={FUENTE.barlow} peso={900} inclinacion={-6} entrada="golpe" hasta={T[11]} lineas={[[{t: 'LINK EN', en: T[10], italica: true}], [{t: 'EL PERFIL', en: T[10] + 3, italica: true, fondo: VERDE, color: '#0B0E1A'}]]} /> : null}
      {f >= T[11] && !loopIn ? (
        <>
          <Titular top={300} tam={110} fuente={FUENTE.barlow} peso={900} inclinacion={-6} lineas={[[{t: '¿VOS SEGUÍS', en: T[11] + 18, italica: true}], [{t: 'RELEYENDO?', en: T[11] + 26, italica: true, color: AMARILLO}]]} />
          <div style={{position: 'absolute', top: 1250, left: 0, right: 0, textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 800, fontSize: 44, color: '#fff', opacity: tween(f, [T[11] + 40, T[11] + 50], [0, 1])}}>Comentá <span style={{color: VERDE}}>SÍ</span> o <span style={{color: ROJO}}>NO</span> 👇</div>
        </>
      ) : null}

      {!loopIn ? (
        <Subtitulos frases={frases} top={1440} tam={54} fuente={FUENTE.inter} peso={800} color="#fff" colorActivo="#0B0E1A" fondoActivo={VERDE} />
      ) : null}
      <Grano opacidad={0.05} vineta={0.45} />

      <Audio src={staticFile('audio/vo-recordar.wav')} volume={1} />
      <Audio src={staticFile('audio/base-energica-120.wav')} loop volume={(fr) => musicaVol(fr)} />
      <Efectos
        eventos={[
          {en: 0, sfx: 'impacto', vol: 0.35},
          {en: T[1], sfx: 'golpe', vol: 0.35},
          ...[0, 1, 2].map((k) => ({en: T[2] + k * Math.round((T[3] - T[2]) / 3), sfx: 'pop-suave', vol: 0.3})),
          {en: T[3] + 30, sfx: 'golpe', vol: 0.3},
          {en: T[3] + 70, sfx: 'pop', vol: 0.3},
          {en: T[4], sfx: 'subida', vol: 0.25},
          {en: T[5], sfx: 'impacto', vol: 0.45},
          {en: T[6], sfx: 'whoosh', vol: 0.3},
          ...[30, 70, 110].map((k) => ({en: T[6] + k, sfx: 'brillo', vol: 0.25})),
          {en: T[7], sfx: 'whoosh', vol: 0.25},
          {en: T[8], sfx: 'impacto', vol: 0.4},
          ...[0, 1, 2].map((k) => ({en: T[8] + 32 + k * 30, sfx: 'ding', vol: 0.25})),
          {en: T[10], sfx: 'golpe', vol: 0.35},
          {en: RECORDAR_DUR - 14, sfx: 'swipe', vol: 0.35},
        ]}
      />
    </AbsoluteFill>
  );
};

export const _i = interpolate;
