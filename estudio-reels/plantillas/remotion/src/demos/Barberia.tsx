import React from 'react';
import {AbsoluteFill, random, useCurrentFrame} from 'remotion';
import {Grano} from '../componentes/Grano';
import {Titular} from '../componentes/Texto';
import {pulso, temblor, tween} from '../lib/anim';
import {Efectos, Musica} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// DEMO 1 — "Barbería Filo" (NEGOCIO FICTICIO). 560 cuadros a 30 fps, música 90 BPM (1 tiempo = 20 cuadros).
export const BARBERIA_DUR = 560;
export const BARBERIA_CRUDA_DUR = 120;

const ORO = 'linear-gradient(180deg,#FFF3C8 0%,#F2D27E 28%,#D2A445 58%,#94701F 100%)';
const CREMA = '#F6EEDB';
const PELO = '#17110C';

// La ilustración se dibuja en un lienzo de 600×800 y se muestra a 1000 px de ancho.
const K = 1000 / 600;
const SVG_X = 40;
const SVG_Y = 500;
const aPantalla = (x: number, y: number) => ({X: SVG_X + x * K, Y: SVG_Y + y * K});

const NUCA = 'M 196 455 C 230 492, 270 506, 300 507 C 330 506, 370 492, 404 455';
const ARRIBA =
  'M 150 336 C 138 214, 206 102, 300 100 C 394 102, 462 214, 450 336 C 420 356, 380 362, 300 362 C 220 362, 180 356, 150 336 Z';
const MELENA =
  'M 148 300 C 140 360, 134 420, 141 456 L 160 492 L 172 520 L 185 505 L 198 548 L 214 522 L 230 562 L 248 530 L 264 569 L 282 534 L 300 573 L 318 534 L 336 569 L 352 530 L 370 562 L 386 522 L 402 548 L 415 505 L 428 520 L 440 492 L 459 456 C 466 420, 460 360, 452 300 Z';
const CUELLO = 'M 236 470 L 233 642 Q 300 670 367 642 L 364 470 Z';

/** de 0..1 de avance de la máquina → altura de la línea de corte en el lienzo */
const lineaCorte = (r: number) => (r < 0.85 ? 612 - 310 * (r / 0.85) : 302 - 302 * ((r - 0.85) / 0.15));

type Maq = {x: number; y: number; rot: number} | null;

/** posición de la máquina en cada cuadro (sirve también para emitir pelitos) */
const maquinaEn = (f: number): Maq => {
  const fr = f >= 530 ? f - 560 : f;
  if (fr < 80) {
    const r = tween(fr, [-25, 70], [0, 1], (t) => t);
    if (r > 0.001 && r < 0.85) return {x: 386, y: lineaCorte(r), rot: -7};
    return null;
  }
  if (f >= 80 && f < 160) {
    const r = tween(f, [80, 150], [0, 1], (t) => t);
    if (r > 0.001 && r < 0.85) return {x: 214, y: lineaCorte(r), rot: 7};
    return null;
  }
  if (f >= 300 && f < 360) {
    const p = (f - 300) / 60;
    return {x: 318 + 30 * Math.sin(p * Math.PI), y: 470 - 120 * Math.sin(p * Math.PI), rot: -4};
  }
  return null;
};

const Defs: React.FC<{id: string}> = ({id}) => (
  <defs>
    <radialGradient id={`${id}-piel`} cx="42%" cy="30%" r="78%">
      <stop offset="0%" stopColor="#DDA571" />
      <stop offset="55%" stopColor="#C68B59" />
      <stop offset="100%" stopColor="#965F35" />
    </radialGradient>
    <linearGradient id={`${id}-cuello`} x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stopColor="#8F5A31" />
      <stop offset="0.5" stopColor="#C68B59" />
      <stop offset="1" stopColor="#8F5A31" />
    </linearGradient>
    <linearGradient id={`${id}-capa`} x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stopColor="#262626" />
      <stop offset="1" stopColor="#080808" />
    </linearGradient>
    <linearGradient id={`${id}-oro`} x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stopColor="#FFF1C1" />
      <stop offset="0.45" stopColor="#E9C46A" />
      <stop offset="1" stopColor="#97701F" />
    </linearGradient>
    <linearGradient id={`${id}-plata`} x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stopColor="#F4F4F4" />
      <stop offset="0.5" stopColor="#B9B9B9" />
      <stop offset="1" stopColor="#7A7A7A" />
    </linearGradient>
    <linearGradient id={`${id}-cuerpo`} x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stopColor="#0E0E0E" />
      <stop offset="0.45" stopColor="#353535" />
      <stop offset="1" stopColor="#0E0E0E" />
    </linearGradient>
    <radialGradient id={`${id}-pelo`} cx="45%" cy="22%" r="85%">
      <stop offset="0" stopColor="#40301F" />
      <stop offset="0.5" stopColor="#1D150F" />
      <stop offset="1" stopColor="#0D0906" />
    </radialGradient>
    <linearGradient id={`${id}-fade`} x1="0" y1="330" x2="0" y2="505" gradientUnits="userSpaceOnUse">
      <stop offset="0" stopColor={PELO} stopOpacity="1" />
      <stop offset="0.3" stopColor={PELO} stopOpacity="0.88" />
      <stop offset="0.68" stopColor={PELO} stopOpacity="0.32" />
      <stop offset="1" stopColor={PELO} stopOpacity="0" />
    </linearGradient>
    <pattern id={`${id}-punto`} width="7" height="7" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.15" fill="#120D09" />
      <circle cx="5.4" cy="5.2" r="0.95" fill="#120D09" />
    </pattern>
    <linearGradient id={`${id}-dens`} x1="0" y1="340" x2="0" y2="508" gradientUnits="userSpaceOnUse">
      <stop offset="0" stopColor="#fff" stopOpacity="1" />
      <stop offset="1" stopColor="#fff" stopOpacity="0" />
    </linearGradient>
    <mask id={`${id}-mdens`} maskUnits="userSpaceOnUse" x="0" y="0" width="600" height="800">
      <rect x="0" y="300" width="600" height="220" fill={`url(#${id}-dens)`} />
    </mask>
    <clipPath id={`${id}-craneo`}>
      <ellipse cx="300" cy="330" rx="150" ry="192" />
    </clipPath>
    <linearGradient id={`${id}-brillo`} x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stopColor="#fff" stopOpacity="0" />
      <stop offset="0.5" stopColor="#fff" stopOpacity="0.38" />
      <stop offset="1" stopColor="#fff" stopOpacity="0" />
    </linearGradient>
    <filter id={`${id}-glow`} x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="b" />
      <feMerge>
        <feMergeNode in="b" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
);

const Oreja: React.FC<{cx: number; lado: number}> = ({cx, lado}) => (
  <g>
    <ellipse cx={cx} cy={405} rx={27} ry={48} fill="#BC7E4D" />
    <ellipse cx={cx + lado * 5} cy={402} rx={13} ry={30} fill="#93592E" opacity={0.55} />
  </g>
);

const Piel: React.FC<{id: string}> = ({id}) => (
  <>
    <path d={CUELLO} fill={`url(#${id}-cuello)`} />
    <ellipse cx="300" cy="530" rx="84" ry="24" fill="#000" opacity="0.2" />
    <Oreja cx={151} lado={1} />
    <Oreja cx={449} lado={-1} />
    <ellipse cx="300" cy="330" rx="150" ry="192" fill={`url(#${id}-piel)`} />
  </>
);

const Mechones: React.FC = () => (
  <g fill="none" stroke="#4E3B28" strokeWidth={3} strokeLinecap="round" opacity={0.55}>
    <path d="M 205 165 C 245 142, 290 140, 330 150" />
    <path d="M 228 205 C 270 188, 332 188, 384 204" />
    <path d="M 180 255 C 232 238, 300 234, 362 248" />
    <path d="M 252 122 C 292 112, 342 118, 372 137" />
    <path d="M 172 300 C 214 288, 252 284, 290 288" />
    <path d="M 318 286 C 360 284, 400 292, 432 304" />
  </g>
);

const Maquina: React.FC<{m: NonNullable<Maq>; id: string; vib: {x: number; y: number}}> = ({m, id, vib}) => (
  <g transform={`translate(${m.x + vib.x} ${m.y + vib.y}) rotate(${m.rot})`}>
    <rect x={-44} y={-2} width={88} height={24} rx={6} fill={`url(#${id}-plata)`} />
    {Array.from({length: 13}).map((_, i) => (
      <rect key={i} x={-41 + i * 6.6} y={-11} width={3.6} height={11} rx={1} fill="#D8D8D8" />
    ))}
    <rect x={-37} y={20} width={74} height={196} rx={32} fill={`url(#${id}-cuerpo)`} />
    <rect x={-37} y={124} width={74} height={15} fill={`url(#${id}-oro)`} />
    <circle cx={0} cy={78} r={9} fill="#2e2e2e" stroke={`url(#${id}-oro)`} strokeWidth={3} />
  </g>
);

const Navaja: React.FC<{t: number; id: string}> = ({t, id}) => {
  const x = 186 + 228 * t;
  const y = 448 + 58 * Math.sin(Math.PI * t) - 6;
  const rot = -18 + 36 * t;
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot})`}>
      <path d="M -4 -2 L 152 -9 Q 172 1 152 12 L -4 14 Z" fill={`url(#${id}-plata)`} stroke="#8d8d8d" strokeWidth={1} />
      <path d="M 2 -1 L 150 -7" stroke="#fff" strokeWidth={2.4} opacity={0.85} />
      <rect x={-140} y={-3} width={140} height={19} rx={9.5} fill="#141414" stroke={`url(#${id}-oro)`} strokeWidth={2.6} />
    </g>
  );
};

const Pelitos: React.FC<{f: number}> = ({f}) => {
  const out: React.ReactNode[] = [];
  for (let e = f - 22; e <= f; e++) {
    const m = maquinaEn(e);
    if (!m) continue;
    for (let i = 0; i < 3; i++) {
      const dt = f - e;
      const vx = (random(`px${e}-${i}`) - 0.5) * 8;
      const vy = -1.5 - random(`py${e}-${i}`) * 5;
      const x = m.x + (random(`ox${e}-${i}`) - 0.5) * 70 + vx * dt;
      const y = m.y - 6 + vy * dt + 0.5 * 0.6 * dt * dt;
      const s = 1.4 + random(`ps${e}-${i}`) * 2.2;
      out.push(
        <ellipse
          key={`${e}-${i}`}
          cx={x}
          cy={y}
          rx={s}
          ry={s * 0.45}
          fill="#1B130C"
          opacity={1 - dt / 22}
          transform={`rotate(${random(`pr${e}-${i}`) * 180} ${x} ${y})`}
        />,
      );
    }
  }
  return <g>{out}</g>;
};

type Estado = {
  revealR: number;
  revealL: number;
  split: number | null;
  linea: number;
  navaja: number | null;
  brillo: number | null;
  maquina: Maq;
  pelitos: boolean;
  vib: {x: number; y: number};
};

const Cabeza: React.FC<{id: string; e: Estado; f: number}> = ({id, e, f}) => {
  const yR = lineaCorte(e.revealR);
  const yL = lineaCorte(e.revealL);
  return (
    <svg width={600 * K} height={800 * K} viewBox="0 0 600 800" style={{position: 'absolute', left: SVG_X, top: SVG_Y, overflow: 'visible'}}>
      <Defs id={id} />
      <mask id={`${id}-mdesp`} maskUnits="userSpaceOnUse" x="-100" y="-100" width="800" height="1000">
        {e.split !== null ? (
          <rect x={e.split} y={-100} width={800} height={1000} fill="#fff" />
        ) : (
          <>
            <rect x={300} y={yR} width={400} height={1000} fill="#fff" />
            <rect x={-100} y={yL} width={400} height={1000} fill="#fff" />
          </>
        )}
      </mask>
      {/* capa de barbero */}
      <path d="M 6 810 C 28 690, 150 640, 236 628 L 364 628 C 450 640, 572 690, 594 810 Z" fill={`url(#${id}-capa)`} />
      <path d="M 222 641 Q 300 671 378 641" stroke={`url(#${id}-oro)`} strokeWidth={7} fill="none" strokeLinecap="round" />
      {/* ANTES */}
      <Piel id={id} />
      <path d={MELENA} fill={`url(#${id}-pelo)`} />
      <path d={ARRIBA} fill={`url(#${id}-pelo)`} />
      <g fill="none" stroke="#3A2B1C" strokeWidth={2.5} strokeLinecap="round" opacity={0.6}>
        <path d="M 170 420 C 176 470, 190 500, 196 540" />
        <path d="M 250 430 C 252 480, 258 520, 262 560" />
        <path d="M 350 430 C 348 480, 342 520, 338 560" />
        <path d="M 430 420 C 424 470, 410 500, 404 540" />
      </g>
      <Mechones />
      {/* DESPUÉS (se va destapando) */}
      <g mask={`url(#${id}-mdesp)`}>
        <Piel id={id} />
        <g clipPath={`url(#${id}-craneo)`}>
          <rect x="140" y="300" width="320" height="230" fill={`url(#${id}-fade)`} />
          <rect x="140" y="300" width="320" height="230" fill={`url(#${id}-punto)`} mask={`url(#${id}-mdens)`} opacity="0.5" />
        </g>
        <path d={ARRIBA} fill={`url(#${id}-pelo)`} />
        <Mechones />
        <path d={NUCA} stroke="#1A120C" strokeWidth={1.6} fill="none" opacity={0.45} />
      </g>
      {/* línea dorada (paso 1) */}
      {e.linea > 0 ? (
        <path
          d={NUCA}
          pathLength={1}
          stroke={`url(#${id}-oro)`}
          strokeWidth={6}
          strokeLinecap="round"
          fill="none"
          strokeDasharray="1 1"
          strokeDashoffset={1 - e.linea}
          filter={`url(#${id}-glow)`}
        />
      ) : null}
      {/* brillo (paso 3) */}
      {e.brillo !== null ? (
        <g clipPath={`url(#${id}-craneo)`}>
          <rect
            x={60 + 480 * e.brillo}
            y={80}
            width={90}
            height={560}
            fill={`url(#${id}-brillo)`}
            transform={`rotate(22 ${105 + 480 * e.brillo} 360)`}
          />
        </g>
      ) : null}
      {/* divisor antes/después */}
      {e.split !== null ? (
        <g>
          <line x1={e.split} y1={40} x2={e.split} y2={790} stroke={`url(#${id}-oro)`} strokeWidth={5} />
          <circle cx={e.split} cy={400} r={26} fill="#0B0A08" stroke={`url(#${id}-oro)`} strokeWidth={4} />
          <path
            d={`M ${e.split - 8} 390 l -8 10 l 8 10 M ${e.split + 8} 390 l 8 10 l -8 10`}
            stroke="#F2D27E"
            strokeWidth={3.5}
            fill="none"
            strokeLinecap="round"
          />
        </g>
      ) : null}
      {e.pelitos ? <Pelitos f={f} /> : null}
      {e.navaja !== null ? <Navaja t={e.navaja} id={id} /> : null}
      {e.maquina ? <Maquina m={e.maquina} id={id} vib={e.vib} /> : null}
    </svg>
  );
};

const Bokeh: React.FC<{f: number; color?: string; opacidad?: number}> = ({f, color = '#C99A3B', opacidad = 1}) => (
  <>
    {Array.from({length: 8}).map((_, i) => {
      const x = random(`bx${i}`) * 1080;
      const y = 200 + random(`by${i}`) * 1500;
      const r = 90 + random(`br${i}`) * 170;
      return (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: x - r + Math.sin(f / 70 + i) * 30,
            top: y - r + Math.cos(f / 90 + i * 2) * 24,
            width: r * 2,
            height: r * 2,
            borderRadius: '50%',
            background: color,
            opacity: (0.06 + random(`bo${i}`) * 0.1) * opacidad,
            filter: 'blur(40px)',
          }}
        />
      );
    })}
  </>
);

const Chispas: React.FC<{f: number; desde: number}> = ({f, desde}) => {
  const t = tween(f, [desde, desde + 15], [0, 1]);
  if (t <= 0) return null;
  return (
    <AbsoluteFill style={{opacity: t}}>
      {Array.from({length: 46}).map((_, i) => {
        const x = random(`cx${i}`) * 1080;
        const y = (random(`cy${i}`) * 2000 - (f - desde) * (0.6 + random(`cv${i}`))) % 2000;
        const s = 3 + random(`cs${i}`) * 6;
        const tw = 0.4 + 0.6 * Math.abs(Math.sin(f * 0.12 + i));
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: (y + 2000) % 2000,
              width: s,
              height: s,
              borderRadius: '50%',
              background: '#F6D98A',
              boxShadow: '0 0 12px #F6D98A',
              opacity: tw,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** franjas de barbero que cruzan la pantalla en los cortes */
const Barrido: React.FC<{f: number; en: number}> = ({f, en}) => {
  const p = (f - en + 5) / 11;
  if (p <= 0 || p >= 1) return null;
  const x = -1600 + 3200 * p;
  return (
    <div
      style={{
        position: 'absolute',
        top: -400,
        left: x,
        width: 900,
        height: 2800,
        transform: 'rotate(18deg)',
        background: 'repeating-linear-gradient(135deg,#E9C46A 0 70px,#0B0A08 70px 140px)',
        boxShadow: '0 0 80px rgba(0,0,0,0.6)',
      }}
    />
  );
};

const Poste: React.FC<{alto: number}> = ({alto}) => (
  <div style={{width: alto * 0.28, height: alto, position: 'relative'}}>
    <div style={{position: 'absolute', top: 0, left: -alto * 0.03, right: -alto * 0.03, height: alto * 0.1, borderRadius: alto * 0.05, background: ORO}} />
    <div
      style={{
        position: 'absolute',
        top: alto * 0.1,
        bottom: alto * 0.1,
        left: 0,
        right: 0,
        background: 'repeating-linear-gradient(150deg,#E9C46A 0 18px,#141414 18px 36px,#F6EEDB 36px 54px,#141414 54px 72px)',
        border: '3px solid #E9C46A',
      }}
    />
    <div style={{position: 'absolute', bottom: 0, left: -alto * 0.03, right: -alto * 0.03, height: alto * 0.1, borderRadius: alto * 0.05, background: ORO}} />
  </div>
);

const camara = (f: number) => {
  // [escala, punto del lienzo enfocado, punto de pantalla destino, rotación]
  let s = 1;
  let foco: [number, number] = [300, 380];
  let dest: [number, number] = [540, 1150];
  let r = 0;
  if (f < 80 || f >= 530) s = f >= 530 ? 1 : tween(f, [0, 80], [1.0, 1.06]);
  else if (f < 160) {
    s = tween(f, [80, 160], [1.22, 1.28]);
    foco = [300, 420];
    dest = [540, 1180];
    r = tween(f, [80, 160], [-2.2, -1]);
  } else if (f < 240) {
    s = 0.98;
  } else if (f < 300) {
    s = tween(f, [240, 300], [1.72, 1.8]);
    foco = [300, 470];
    dest = [540, 1250];
  } else if (f < 360) {
    s = 1.5;
    foco = [320, 430];
    dest = [540, 1230];
  } else if (f < 420) {
    s = tween(f, [360, 420], [1.74, 1.82]);
    foco = [300, 470];
    dest = [540, 1250];
  } else if (f < 480) {
    s = tween(f, [420, 480], [1.04, 1.1]);
    foco = [300, 360];
    dest = [540, 1180];
    r = tween(f, [420, 480], [0, 1.6]);
  }
  for (const c of [80, 160, 240, 300, 360, 420, 480]) if (f >= c && f < c + 14) s *= 1 + 0.07 * Math.exp(-(f - c) / 4);
  s *= 1 + 0.008 * pulso(f, 20);
  const p = aPantalla(foco[0], foco[1]);
  return {s, tx: dest[0] - s * p.X, ty: dest[1] - s * p.Y, r, dest};
};

const estadoEn = (f: number): Estado => {
  const fr = f >= 530 ? f - 560 : f;
  const revealR = fr < 80 ? tween(fr, [-25, 70], [0, 1], (t) => t) : 1;
  const revealL = f >= 530 || f < 80 ? 0 : tween(f, [80, 150], [0, 1], (t) => t);
  const split = f >= 160 && f < 240 ? (f < 172 ? tween(f, [160, 172], [640, 300]) : 300 + 55 * Math.sin(((f - 172) / 68) * Math.PI * 2)) : null;
  const linea = f >= 240 && f < 300 ? tween(f, [246, 286], [0, 1]) : 0;
  const navaja = f >= 360 && f < 420 ? tween(f, [362, 410], [0, 1]) : null;
  const brillo = f >= 384 && f < 420 ? tween(f, [384, 412], [0, 1]) : null;
  const maquina = maquinaEn(f);
  return {
    revealR,
    revealL,
    split,
    linea,
    navaja,
    brillo,
    maquina,
    pelitos: !!maquina || (f >= 300 && f < 380),
    vib: temblor(f, 'maq', 1.4),
  };
};

export const Barberia: React.FC<{conAudio?: boolean}> = ({conAudio = true}) => {
  const f = useCurrentFrame();
  const cam = camara(f);
  const e = estadoEn(f);
  const desenfoque = f < 480 ? 0 : f < 530 ? tween(f, [480, 492], [0, 16]) : tween(f, [534, 552], [16, 0]);
  const brilloEsc = f < 480 ? 1 : f < 530 ? tween(f, [480, 492], [1, 0.32]) : tween(f, [534, 552], [0.32, 1]);
  const cta = f >= 480 && f < 548;
  const salidaCta = tween(f, [530, 545], [1, 0]);

  return (
    <AbsoluteFill style={{background: '#0B0A08', overflow: 'hidden'}}>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 70% 55% at 50% 58%, #33271A 0%, #17120C 45%, #0B0A08 80%)'}} />
      <Bokeh f={f} />
      <AbsoluteFill style={{filter: desenfoque ? `blur(${desenfoque}px) brightness(${brilloEsc})` : undefined}}>
        <div style={{position: 'absolute', inset: 0, transform: `rotate(${cam.r}deg)`, transformOrigin: `${cam.dest[0]}px ${cam.dest[1]}px`}}>
          <div style={{position: 'absolute', inset: 0, transform: `translate(${cam.tx}px, ${cam.ty}px) scale(${cam.s})`, transformOrigin: '0 0'}}>
            <Cabeza id="bf" e={e} f={f} />
          </div>
        </div>
      </AbsoluteFill>

      {/* B1 — gancho */}
      {f < 80 ? (
        <Titular
          top={235}
          tam={150}
          fuente={FUENTE.bebas}
          peso={400}
          color={CREMA}
          tracking="0.01em"
          interlineado={0.92}
          hasta={80}
          lineas={[
            [{t: 'EL CORTE QUE', en: -6}],
            [{t: 'MÁS PIDEN', en: 2, degradado: ORO, rel: 1.42}],
            [{t: 'este mes', en: 10, fuente: FUENTE.playfair, peso: 700, italica: true, rel: 0.62, color: CREMA}],
          ]}
        />
      ) : null}
      {/* B2 */}
      {f >= 80 && f < 160 ? (
        <Titular
          top={235}
          tam={215}
          fuente={FUENTE.bebas}
          peso={400}
          color={CREMA}
          tracking="0.01em"
          interlineado={0.86}
          hasta={160}
          lineas={[
            [{t: 'DEGRADÉ', en: 82}],
            [{t: 'BAJO', en: 88, degradado: ORO}],
            [{t: 'con línea marcada', en: 96, fuente: FUENTE.playfair, peso: 700, italica: true, rel: 0.36, color: CREMA}],
          ]}
        />
      ) : null}
      {/* B3 — antes / después */}
      {f >= 160 && f < 240 ? (
        <>
          <Titular
            top={250}
            tam={140}
            fuente={FUENTE.playfair}
            peso={700}
            color={CREMA}
            tracking="0"
            interlineado={1.0}
            hasta={240}
            lineas={[[{t: 'De esto…', en: 164, italica: true}], [{t: '…a esto', en: 200, italica: true, degradado: ORO}]]}
          />
          <div style={{position: 'absolute', top: 1505, left: 0, right: 0, display: 'flex', justifyContent: 'space-around', fontFamily: FUENTE.bebas, fontSize: 70, color: CREMA, letterSpacing: '0.12em', opacity: tween(f, [168, 176], [0, 1]) * tween(f, [232, 240], [1, 0])}}>
            <span style={{borderBottom: '5px solid #E9C46A', paddingBottom: 4}}>ANTES</span>
            <span style={{borderBottom: '5px solid #E9C46A', paddingBottom: 4}}>DESPUÉS</span>
          </div>
        </>
      ) : null}
      {/* B4 — 3 pasos */}
      {[
        {n: '1', a: 'MARCAMOS', b: 'LA LÍNEA', d: 240},
        {n: '2', a: 'DEGRADAMOS', b: 'A MÁQUINA', d: 300},
        {n: '3', a: 'TERMINAMOS', b: 'A NAVAJA', d: 360},
      ].map((p) =>
        f >= p.d && f < p.d + 60 ? (
          <React.Fragment key={p.n}>
            <Titular top={205} izquierda={80} ancho={260} alineacion="left" tam={330} fuente={FUENTE.bebas} peso={400} tracking="0" interlineado={1} hasta={p.d + 60} lineas={[[{t: p.n, en: p.d + 1, degradado: ORO}]]} />
            <Titular
              top={262}
              izquierda={300}
              ancho={720}
              alineacion="left"
              tam={128}
              fuente={FUENTE.bebas}
              peso={400}
              color={CREMA}
              tracking="0.02em"
              interlineado={0.95}
              hasta={p.d + 60}
              lineas={[[{t: p.a, en: p.d + 4}], [{t: p.b, en: p.d + 9, degradado: ORO}]]}
            />
          </React.Fragment>
        ) : null,
      )}
      {/* B5 — envíos */}
      {f >= 420 && f < 480 ? (
        <Titular
          top={225}
          tam={150}
          fuente={FUENTE.bebas}
          peso={400}
          color={CREMA}
          tracking="0.01em"
          interlineado={0.95}
          hasta={480}
          lineas={[
            [{t: 'Mandáselo', en: 422, fuente: FUENTE.playfair, peso: 700, italica: true, rel: 0.72}],
            [{t: 'AL AMIGO QUE', en: 428}],
            [{t: 'LO NECESITA', en: 434, degradado: ORO}],
          ]}
        />
      ) : null}
      <Chispas f={f} desde={420} />
      {/* B6 — cierre de marca */}
      {cta ? (
        <AbsoluteFill style={{opacity: salidaCta, transform: `translateY(${(1 - salidaCta) * -80}px)`}}>
          <div style={{position: 'absolute', top: 470, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 34, transform: `scale(${0.8 + 0.2 * tween(f, [482, 492], [0, 1])})`, opacity: tween(f, [481, 489], [0, 1])}}>
            <Poste alto={300} />
            <div style={{fontFamily: FUENTE.bebas, lineHeight: 0.84, color: CREMA}}>
              <div style={{fontSize: 108, letterSpacing: '0.16em'}}>BARBERÍA</div>
              <div style={{fontSize: 250, backgroundImage: ORO, WebkitBackgroundClip: 'text', color: 'transparent', letterSpacing: '0.04em'}}>FILO</div>
            </div>
          </div>
          <Titular top={905} tam={104} fuente={FUENTE.bebas} peso={400} color={CREMA} tracking="0.06em" lineas={[[{t: 'TURNOS POR MENSAJE', en: 494}]]} />
          <div
            style={{
              position: 'absolute',
              top: 1060,
              left: '50%',
              transform: `translateX(-50%) scale(${0.7 + 0.3 * tween(f, [500, 508], [0, 1])})`,
              opacity: tween(f, [500, 506], [0, 1]),
              background: ORO,
              color: '#120D07',
              fontFamily: FUENTE.inter,
              fontWeight: 900,
              fontSize: 46,
              padding: '22px 46px',
              borderRadius: 80,
              whiteSpace: 'nowrap',
              boxShadow: '0 18px 50px rgba(233,196,106,0.35)',
            }}
          >
            LINK EN EL PERFIL
          </div>
        </AbsoluteFill>
      ) : null}
      {[160, 240, 480].map((c) => (
        <Barrido key={c} f={f} en={c} />
      ))}
      <Grano opacidad={0.07} vineta={0.6} />
      {conAudio ? (
        <>
          <Musica archivo="musica-barberia.wav" volumen={0.78} />
          <Efectos
            eventos={[
              {en: 0, sfx: 'maquina', vol: 0.32},
              {en: 82, sfx: 'pop', vol: 0.4},
              {en: 84, sfx: 'maquina', vol: 0.28},
              {en: 156, sfx: 'whoosh', vol: 0.5},
              {en: 164, sfx: 'pop-suave', vol: 0.4},
              {en: 200, sfx: 'pop-suave', vol: 0.4},
              {en: 236, sfx: 'whoosh', vol: 0.45},
              {en: 242, sfx: 'pop', vol: 0.4},
              {en: 282, sfx: 'brillo', vol: 0.35},
              {en: 300, sfx: 'pop', vol: 0.4},
              {en: 300, sfx: 'maquina', vol: 0.28},
              {en: 360, sfx: 'pop', vol: 0.4},
              {en: 392, sfx: 'brillo', vol: 0.45},
              {en: 420, sfx: 'pop-suave', vol: 0.4},
              {en: 476, sfx: 'whoosh', vol: 0.45},
              {en: 482, sfx: 'golpe', vol: 0.55},
              {en: 500, sfx: 'pop', vol: 0.4},
              {en: 536, sfx: 'swipe', vol: 0.45},
            ]}
          />
        </>
      ) : null}
    </AbsoluteFill>
  );
};

/** El MISMO material sin editar: plano fijo, oscuro, torcido, sin texto ni cortes ni música. */
export const BarberiaCruda: React.FC = () => {
  const f = useCurrentFrame();
  const sh = {x: Math.sin(f / 7) * 5 + Math.sin(f / 3.1) * 2, y: Math.cos(f / 9) * 4 + Math.sin(f / 2.7) * 1.5};
  const e: Estado = {
    revealR: tween(f, [0, 120], [0.12, 0.6], (t) => t),
    revealL: 0,
    split: null,
    linea: 0,
    navaja: null,
    brillo: null,
    maquina: {x: 386, y: lineaCorte(tween(f, [0, 120], [0.12, 0.6], (t) => t)), rot: -7},
    pelitos: false,
    vib: {x: 0, y: 0},
  };
  return (
    <AbsoluteFill style={{background: '#4A4A44', overflow: 'hidden'}}>
      <AbsoluteFill style={{background: 'linear-gradient(180deg,#5b5b54 0%,#3d3d38 100%)'}} />
      <AbsoluteFill
        style={{
          transform: `translate(${-70 + sh.x}px, ${150 + sh.y}px) rotate(3.5deg) scale(0.74)`,
          filter: 'saturate(0.35) brightness(0.55) contrast(0.8) blur(1.3px)',
        }}
      >
        <Cabeza id="bc" e={e} f={f} />
      </AbsoluteFill>
      <Grano opacidad={0.12} vineta={0.35} />
    </AbsoluteFill>
  );
};
