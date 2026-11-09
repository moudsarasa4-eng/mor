import React from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {Grano} from '../componentes/Grano';
import {Subtitulos, Titular} from '../componentes/Texto';
import {pulso, resorte, tween} from '../lib/anim';
import {Efectos, Musica} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// DEMO 2 — "Brasa Viva" hamburguesería (NEGOCIO FICTICIO). 504 cuadros, 100 BPM (1 tiempo = 18 cuadros).
export const RESTO_DUR = 504;
const ROJO = '#E8432E';
const MOSTAZA = '#F6B73C';
const CARBON = '#2B1A10';
const CREMA = '#FFF3E2';

const Rayos: React.FC<{f: number}> = ({f}) => (
  <AbsoluteFill style={{overflow: 'hidden'}}>
    <div
      style={{
        position: 'absolute',
        left: 540 - 1500,
        top: 1050 - 1500,
        width: 3000,
        height: 3000,
        background: `repeating-conic-gradient(from ${f * 0.35}deg at 50% 50%, #FFE7B8 0deg 9deg, ${CREMA} 9deg 18deg)`,
      }}
    />
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 55%, rgba(255,243,226,0) 20%, rgba(246,183,60,0.28) 100%)'}} />
  </AbsoluteFill>
);

// ------------------------------------------------------------------ hamburguesa (capas que caen)
const CAPAS = ['panAbajo', 'carne', 'cheddar', 'carne', 'cheddar', 'panceta', 'lechuga', 'panArriba'] as const;
const ALTO: Record<string, number> = {panAbajo: 70, carne: 62, cheddar: 16, panceta: 22, lechuga: 26, panArriba: 150};

const Capa: React.FC<{tipo: string; goteo: number}> = ({tipo, goteo}) => {
  switch (tipo) {
    case 'panAbajo':
      return (
        <g>
          <path d="M -230 0 L 230 0 Q 236 66 180 70 L -180 70 Q -236 66 -230 0 Z" fill="#D88A35" />
          <rect x={-232} y={-4} width={464} height={18} rx={9} fill="#F3C27A" />
        </g>
      );
    case 'carne':
      return (
        <g>
          <rect x={-244} y={0} width={488} height={62} rx={30} fill="#5A3019" />
          <path d="M -220 18 Q -120 8 0 16 T 220 14" stroke="#7A4526" strokeWidth={7} fill="none" strokeLinecap="round" />
          <path d="M -200 42 Q -90 34 20 42 T 210 40" stroke="#3E1F0E" strokeWidth={6} fill="none" strokeLinecap="round" />
        </g>
      );
    case 'cheddar':
      return (
        <g>
          <path
            d={`M -250 0 L 250 0 L 250 16 L 200 16 L 186 ${16 + 40 * goteo} Q 172 ${26 + 44 * goteo} 160 ${16 + 30 * goteo} L 150 16 L 40 16 L 26 ${16 + 58 * goteo} Q 10 ${30 + 60 * goteo} -4 ${16 + 46 * goteo} L -12 16 L -120 16 L -132 ${16 + 34 * goteo} Q -146 ${26 + 36 * goteo} -158 ${16 + 22 * goteo} L -166 16 L -250 16 Z`}
            fill="#F59E1B"
          />
          <rect x={-250} y={0} width={500} height={6} fill="#FFC04D" />
        </g>
      );
    case 'panceta':
      return <path d="M -236 6 Q -180 -10 -120 8 T 0 6 T 120 8 T 236 4 L 236 20 Q 180 30 120 16 T 0 20 T -120 16 T -236 22 Z" fill="#B5432B" />;
    case 'lechuga':
      return <path d="M -256 10 Q -230 -8 -204 12 Q -178 -8 -152 12 Q -126 -8 -100 12 Q -74 -8 -48 12 Q -22 -8 4 12 Q 30 -8 56 12 Q 82 -8 108 12 Q 134 -8 160 12 Q 186 -8 212 12 Q 238 -8 258 10 L 250 26 L -250 26 Z" fill="#6BBF59" />;
    default:
      return (
        <g>
          <path d="M -236 150 Q -250 10 0 0 Q 250 10 236 150 Z" fill="#E3A048" />
          <path d="M -200 120 Q -210 30 -40 18" stroke="#F2C07A" strokeWidth={22} fill="none" strokeLinecap="round" opacity={0.7} />
          {[[-120, 60], [-60, 40], [10, 34], [80, 46], [140, 70], [-150, 100], [-40, 80], [40, 90], [120, 110], [170, 100], [-90, 110]].map(([x, y], i) => (
            <ellipse key={i} cx={x} cy={y} rx={8} ry={4.5} fill="#FFF5DD" transform={`rotate(${(i * 37) % 60 - 30} ${x} ${y})`} />
          ))}
        </g>
      );
  }
};

const Hamburguesa: React.FC<{f: number; inicio: number; escala?: number}> = ({f, inicio, escala = 1}) => {
  const {fps} = useVideoConfig();
  let y = 0;
  const capas = CAPAS.map((tipo, i) => {
    const en = inicio + i * 5;
    const s = resorte(f, fps, en, 'rebote');
    const caida = (1 - s) * -900;
    const yy = y;
    y -= ALTO[tipo] - (tipo === 'cheddar' ? 4 : 2);
    if (f < en) return null;
    const aplast = tipo === 'panArriba' ? 1 - 0.08 * Math.max(0, Math.sin(Math.min(1, (f - en) / 8) * Math.PI)) : 1;
    return (
      <g key={i} transform={`translate(0 ${yy - ALTO[tipo] + caida}) scale(1 ${aplast})`}>
        <Capa tipo={tipo} goteo={tween(f, [en + 6, en + 40], [0.2, 1])} />
      </g>
    );
  });
  return (
    <svg width={1080} height={1000} viewBox="-540 -700 1080 1000" style={{position: 'absolute', left: 0, top: 560, overflow: 'visible', transform: `scale(${escala})`}}>
      <ellipse cx={0} cy={10} rx={300} ry={36} fill="#000" opacity={0.12} />
      {capas}
      <Vapor f={f} x={0} y={y - 40} />
    </svg>
  );
};

const Vapor: React.FC<{f: number; x: number; y: number}> = ({f, x, y}) => (
  <g opacity={0.65}>
    {[-90, 0, 90].map((dx, i) => {
      const t = ((f + i * 14) % 42) / 42;
      return (
        <path
          key={i}
          d={`M ${x + dx} ${y - t * 120} q 22 -30 0 -60 q -22 -30 0 -60`}
          stroke="#fff"
          strokeWidth={10}
          fill="none"
          strokeLinecap="round"
          opacity={Math.sin(t * Math.PI)}
        />
      );
    })}
  </g>
);

// ------------------------------------------------------------------ papas
const Papas: React.FC<{f: number; inicio: number}> = ({f, inicio}) => {
  const {fps} = useVideoConfig();
  const papas = Array.from({length: 13}).map((_, i) => {
    const s = resorte(f, fps, inicio + 2 + i * 2, 'rebote');
    const x = -150 + i * 25 + (random(`px${i}`) - 0.5) * 16;
    const h = 230 + random(`ph${i}`) * 110;
    const rot = (random(`pr${i}`) - 0.5) * 22;
    return (
      <g key={i} transform={`translate(${x} ${-20 - h * s + 40}) rotate(${rot})`}>
        <rect x={-15} y={0} width={30} height={h} rx={8} fill="#FFC93C" />
        <rect x={-15} y={0} width={9} height={h} rx={4} fill="#FFE27A" />
        <rect x={-15} y={0} width={30} height={14} rx={7} fill="#E39A22" />
      </g>
    );
  });
  const salsa = tween(f, [inicio + 34, inicio + 60], [0, 1]);
  return (
    <svg width={1080} height={1100} viewBox="-540 -650 1080 1100" style={{position: 'absolute', left: 0, top: 520, overflow: 'visible'}}>
      <defs>
        <clipPath id="cono">
          <path d="M -210 -40 L 210 -40 L 120 380 L -120 380 Z" />
        </clipPath>
      </defs>
      <ellipse cx={0} cy={395} rx={170} ry={26} fill="#000" opacity={0.12} />
      {papas}
      <g clipPath="url(#cono)">
        <rect x={-260} y={-60} width={520} height={460} fill={CREMA} />
        {Array.from({length: 8}).map((_, i) => (
          <rect key={i} x={-260 + i * 70} y={-60} width={35} height={460} fill={ROJO} transform="skewX(-6)" />
        ))}
      </g>
      <path d="M -214 -44 L 214 -44" stroke="#C7311F" strokeWidth={14} strokeLinecap="round" />
      <path
        d="M -150 -80 C -90 -150, -40 -40, 10 -120 S 110 -60, 150 -130"
        pathLength={1}
        strokeDasharray="1 1"
        strokeDashoffset={1 - salsa}
        stroke="#F59E1B"
        strokeWidth={26}
        fill="none"
        strokeLinecap="round"
      />
      {Array.from({length: 18}).map((_, i) => {
        const en = inicio + 56 + i;
        if (f < en) return null;
        const t = Math.min(1, (f - en) / 12);
        const x = (random(`vx${i}`) - 0.5) * 300;
        const y0 = -420;
        const y1 = -120 - random(`vy${i}`) * 140;
        return <circle key={i} cx={x} cy={y0 + (y1 - y0) * t} r={9} fill="none" stroke="#3F9B3A" strokeWidth={7} />;
      })}
    </svg>
  );
};

// ------------------------------------------------------------------ pizza (porción que estira)
const Pizza: React.FC<{f: number; inicio: number}> = ({f, inicio}) => {
  const p = tween(f, [inicio + 8, inicio + 70], [0, 1]);
  const lift = p * 300;
  const hilos = [-60, -20, 25, 65];
  return (
    <svg width={1080} height={1100} viewBox="-540 -600 1080 1100" style={{position: 'absolute', left: 0, top: 560, overflow: 'visible'}}>
      <ellipse cx={0} cy={210} rx={360} ry={56} fill="#000" opacity={0.12} />
      <ellipse cx={0} cy={140} rx={340} ry={120} fill="#C9772E" />
      <ellipse cx={0} cy={130} rx={300} ry={100} fill="#D9452B" />
      <ellipse cx={0} cy={126} rx={286} ry={92} fill="#FFD666" />
      {[[-150, 120], [120, 100], [40, 160], [-60, 90], [200, 150]].map(([x, y], i) => (
        <ellipse key={i} cx={x} cy={y} rx={22} ry={10} fill="#2B2B2B" />
      ))}
      <path d="M 0 126 L 260 60 Q 300 110 270 170 Z" fill="#5A2A12" opacity={0.35} />
      {hilos.map((dx, i) => {
        const w = Math.max(3, 16 * (1 - p * 0.75));
        return (
          <path
            key={i}
            d={`M ${150 + dx} ${110} C ${160 + dx} ${60 - lift * 0.3}, ${170 + dx} ${-lift * 0.6}, ${180 + dx * 0.7} ${100 - lift}`}
            stroke="#FFD666"
            strokeWidth={w}
            fill="none"
            strokeLinecap="round"
          />
        );
      })}
      <g transform={`translate(${170} ${110 - lift}) rotate(${-8 * p})`}>
        <path d="M -40 0 L 130 -60 Q 170 -10 140 50 Z" fill="#C9772E" />
        <path d="M -30 0 L 122 -50 Q 152 -8 128 40 Z" fill="#FFD666" />
        <ellipse cx={60} cy={-6} rx={16} ry={8} fill="#2B2B2B" />
        <circle cx={100} cy={10} r={9} fill="#3F9B3A" />
      </g>
    </svg>
  );
};

const Badge: React.FC<{n: string; f: number; en: number; nombre: string}> = ({n, f, en, nombre}) => {
  const {fps} = useVideoConfig();
  const s = resorte(f, fps, en, 'rebote');
  return (
    <div style={{position: 'absolute', top: 285, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 26, transform: `scale(${0.5 + 0.5 * s})`, opacity: Math.min(1, s * 2)}}>
      <div style={{width: 150, height: 150, borderRadius: '50%', background: ROJO, color: '#fff', fontFamily: FUENTE.rubik, fontWeight: 900, fontSize: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 14px 0 #A9281A'}}>{n}</div>
      <div style={{fontFamily: FUENTE.rubik, fontWeight: 900, fontSize: 96, color: CARBON, lineHeight: 1, letterSpacing: '-0.02em', borderBottom: `14px solid ${MOSTAZA}`}}>{nombre}</div>
    </div>
  );
};

const subs = {top: 1490, tam: 70, fuente: FUENTE.rubik, peso: 800, color: CARBON, colorActivo: '#fff', fondoActivo: ROJO, sombra: 'none', paso: 7};

export const Resto: React.FC<{conAudio?: boolean}> = ({conAudio = true}) => {
  const f = useCurrentFrame();
  const bump = 1 + 0.012 * pulso(f, 18);
  const corte = (c: number) => (f >= c && f < c + 12 ? 1 + 0.08 * Math.exp(-(f - c) / 4) : 1);
  const z = bump * corte(72) * corte(180) * corte(288) * corte(396) * corte(450);
  const fr = f >= 486 ? f - 504 : f; // loop: la hamburguesa vuelve a armarse
  return (
    <AbsoluteFill style={{background: CREMA, overflow: 'hidden'}}>
      <Rayos f={f} />
      <AbsoluteFill style={{transform: `scale(${z})`}}>
        <AbsoluteFill style={{transform: f >= 396 && f < 486 ? undefined : 'translateY(-130px) scale(1.3)', transformOrigin: '540px 1080px'}}>
        {f < 180 || f >= 486 ? <Hamburguesa f={fr} inicio={-18} /> : null}
        {f >= 180 && f < 288 ? <Papas f={f} inicio={180} /> : null}
        {f >= 288 && f < 396 ? <Pizza f={f} inicio={288} /> : null}
        {f >= 396 && f < 486 ? (
          <div style={{position: 'absolute', top: 760, left: 0, right: 0, height: 700}}>
            {['🍔', '🍟', '🍕'].map((_, i) => (
              <div key={i} style={{position: 'absolute', left: 60 + i * 330, top: 0, width: 300, height: 600, overflow: 'visible', transform: `scale(0.42)`, transformOrigin: '150px 300px'}}>
                <div style={{position: 'absolute', left: -390, top: -560, width: 1080, height: 1920}}>
                  {i === 0 ? <Hamburguesa f={200} inicio={0} /> : i === 1 ? <Papas f={300} inicio={180} /> : <Pizza f={330} inicio={288} />}
                </div>
                <div style={{position: 'absolute', left: 90, top: 820, width: 120, height: 120, borderRadius: '50%', background: ROJO, color: '#fff', fontFamily: FUENTE.rubik, fontWeight: 900, fontSize: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: 'scale(2.2)'}}>{i + 1}</div>
              </div>
            ))}
          </div>
        ) : null}
        </AbsoluteFill>
      </AbsoluteFill>

      {f < 72 || f >= 500 ? (
        <Titular
          top={250}
          tam={140}
          fuente={FUENTE.rubik}
          peso={900}
          color={CARBON}
          sombra="none"
          interlineado={1.0}
          hasta={f >= 500 ? undefined : 72}
          lineas={[[{t: '¿CUÁL', en: f >= 500 ? 500 : -6}, {t: 'PEDÍS', en: f >= 500 ? 502 : -5}], [{t: 'PRIMERO?', en: f >= 500 ? 503 : -4, fondo: ROJO, color: '#fff'}]]}
        />
      ) : null}
      {f >= 72 && f < 180 ? <Badge n="1" f={f} en={74} nombre="Doble cheddar" /> : null}
      {f >= 180 && f < 288 ? <Badge n="2" f={f} en={182} nombre="Papas cheddar" /> : null}
      {f >= 288 && f < 396 ? <Badge n="3" f={f} en={290} nombre="Muzza a la piedra" /> : null}
      <Subtitulos
        {...subs}
        frases={[
          {texto: 'doble carne, doble cheddar y panceta', desde: 84, hasta: 180},
          {texto: 'con verdeo, para compartir (o no)', desde: 192, hasta: 288},
          {texto: 'el queso que estira', desde: 300, hasta: 396},
        ]}
      />
      {f >= 396 && f < 450 ? (
        <Titular top={250} tam={150} fuente={FUENTE.rubik} peso={900} color={CARBON} sombra="none" hasta={450}
          lineas={[[{t: '¿1,', en: 398}, {t: '2', en: 402}, {t: 'o', en: 405}, {t: '3?', en: 408, fondo: ROJO, color: '#fff'}]]} />
      ) : null}
      {f >= 410 && f < 450 ? (
        <Titular top={1430} tam={66} fuente={FUENTE.rubik} peso={800} color={CARBON} sombra="none" hasta={450}
          lineas={[[{t: 'Mandáselo a con quien', en: 412}], [{t: 'pedís el viernes', en: 418, fondo: MOSTAZA}]]} />
      ) : null}
      {f >= 450 && f < 500 ? (
        <AbsoluteFill style={{background: ROJO, opacity: tween(f, [450, 456], [0, 1]) * tween(f, [492, 500], [1, 0]), display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 40}}>
          <div style={{fontFamily: FUENTE.rubik, fontWeight: 900, fontSize: 190, color: CREMA, lineHeight: 0.9, textAlign: 'center', letterSpacing: '-0.03em', transform: `scale(${0.7 + 0.3 * tween(f, [452, 460], [0, 1])})`}}>BRASA<br />VIVA</div>
          <div style={{fontFamily: FUENTE.rubik, fontWeight: 800, fontSize: 80, color: CREMA}}>Pedí por mensaje</div>
          <div style={{fontFamily: FUENTE.rubik, fontWeight: 900, fontSize: 52, background: MOSTAZA, color: CARBON, padding: '20px 50px', borderRadius: 80, opacity: tween(f, [462, 468], [0, 1])}}>LINK EN EL PERFIL</div>
        </AbsoluteFill>
      ) : null}
      <Grano opacidad={0.05} vineta={0.25} />
      {conAudio ? (
        <>
          <Musica archivo="musica-resto.wav" volumen={0.75} />
          <Efectos
            eventos={[
              ...[0, 5, 10, 15, 20, 25, 30].map((d) => ({en: Math.max(0, d - 18 + 18), sfx: 'plop', vol: 0.35})),
              {en: 72, sfx: 'whoosh', vol: 0.45}, {en: 74, sfx: 'pop', vol: 0.45},
              {en: 180, sfx: 'whoosh', vol: 0.45}, {en: 182, sfx: 'pop', vol: 0.45},
              {en: 288, sfx: 'whoosh', vol: 0.45}, {en: 290, sfx: 'pop', vol: 0.45},
              {en: 396, sfx: 'golpe', vol: 0.5}, {en: 450, sfx: 'whoosh', vol: 0.45}, {en: 454, sfx: 'golpe', vol: 0.5},
            ]}
          />
        </>
      ) : null}
    </AbsoluteFill>
  );
};
