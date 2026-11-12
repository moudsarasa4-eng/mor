import React from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {resorte, tween} from '../lib/anim';
import {FUENTE} from '../lib/fuentes';

// Serie de 5 reels de venta (@viraliza.tu.perfil.arg). Sin audio, solo texto animado y formas.
// Franja segura: y 288–1440 (15% arriba y 25% abajo libres).
export const ARRIBA = 288;
export const ABAJO = 1440;
export const CENTRO = (ARRIBA + ABAJO) / 2;
export const USUARIO = '@viraliza.tu.perfil.arg';

export type Paleta = {fondo: string; texto: string; acento: string};
export type Palabra = string | {t: string; acento?: boolean; tachar?: number; golpe?: boolean};

/** Bloque de texto: líneas de palabras, aparecen todas juntas en `en` (o palabra por palabra con `paso`). */
export const Frase: React.FC<{
  lineas: Palabra[][];
  p: Paleta;
  en: number;
  hasta?: number;
  y?: number;
  tam?: number;
  paso?: number;
}> = ({lineas, p, en, hasta, y = CENTRO, tam = 120, paso = 0}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < en || (hasta !== undefined && f >= hasta)) return null;
  let k = 0;
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: y, transform: 'translateY(-50%)', textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: tam, lineHeight: 1.02, letterSpacing: '-0.03em', color: p.texto, textTransform: 'uppercase'}}>
      {lineas.map((l, i) => (
        <div key={i}>
          {l.map((w, j) => {
            const o = typeof w === 'string' ? {t: w} : w;
            const inicio = en + (paso ? k * paso : 0) + (o.golpe ? 10 : 0);
            k++;
            if (f < inicio) return <span key={j} style={{opacity: 0}}>{o.t} </span>;
            const s = resorte(f, fps, inicio, o.golpe ? 'seco' : 'pop');
            const esc = o.golpe ? 1.8 - 0.8 * s : f - en < 2 && !paso ? 1 : 0.7 + 0.3 * s;
            const tach = o.tachar !== undefined ? tween(f, [o.tachar, o.tachar + 8], [0, 1]) : 0;
            return (
              <span key={j} style={{display: 'inline-block', position: 'relative', color: o.acento ? p.acento : p.texto, transform: `scale(${esc})`, opacity: f - en < 2 && !paso && !o.golpe ? 1 : Math.min(1, s * 2), margin: '0 0.12em'}}>
                {o.t}
                {tach > 0 ? <span style={{position: 'absolute', left: '-4%', top: '52%', height: '0.12em', width: `${108 * tach}%`, background: p.acento, borderRadius: 8}} /> : null}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

/** Rectángulos grises que pasan como un feed. */
export const Feed: React.FC<{desde: number; vel?: number; color?: string; destacado?: number; colorDest?: string}> = ({desde, vel = 22, color = '#CFCFD4', destacado, colorDest}) => {
  const f = useCurrentFrame() - desde;
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      {Array.from({length: 14}).map((_, i) => {
        const y = 1920 - f * vel + i * 560 - 400;
        const d = destacado === i;
        return (
          <div key={i} style={{position: 'absolute', left: 140, width: 800, top: y, height: 500, borderRadius: 36, background: d ? colorDest : color, opacity: d ? 1 : 0.55}}>
            <div style={{position: 'absolute', left: 40, top: 40, width: 90, height: 90, borderRadius: '50%', background: 'rgba(0,0,0,0.12)'}} />
            <div style={{position: 'absolute', left: 150, top: 60, width: 300, height: 26, borderRadius: 13, background: 'rgba(0,0,0,0.12)'}} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Pantalla partida con dos bloques de color. */
export const Partida: React.FC<{p: Paleta; arriba: {t: string; fondo: string; color: string}; abajo: {t: string; fondo: string; color: string}; en: number}> = ({arriba, abajo, en}) => {
  const f = useCurrentFrame();
  const a = tween(f, [en, en + 10], [0, 1]);
  const b = tween(f, [en + 8, en + 18], [0, 1]);
  const bloque = (x: typeof arriba, top: number, t: number, lado: number) => (
    <div style={{position: 'absolute', left: 90, right: 90, top, height: 360, borderRadius: 40, background: x.fondo, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 150, color: x.color, transform: `translateX(${(1 - t) * 1200 * lado}px)`}}>{x.t}</div>
  );
  return (
    <>
      {bloque(arriba, ARRIBA + 250, a, -1)}
      {bloque(abajo, ARRIBA + 650, b, 1)}
    </>
  );
};

/** Contador que sube. */
export const Contador: React.FC<{p: Paleta; desde: number; hasta: number; de: number; a: number; y?: number}> = ({p, desde, hasta, de, a, y = CENTRO - 120}) => {
  const f = useCurrentFrame();
  const n = Math.round(tween(f, [desde, hasta], [de, a], (t) => t));
  const pulso = Math.exp(-(((f - desde) % Math.max(1, Math.round((hasta - desde) / Math.max(1, a - de)))) / 3));
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, transform: `translateY(-50%) scale(${1 + 0.12 * pulso})`, textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 420, lineHeight: 1, color: p.acento}}>{n}</div>
  );
};

export const Flecha: React.FC<{p: Paleta; en: number; y: number}> = ({p, en, y}) => {
  const f = useCurrentFrame();
  const t = tween(f, [en, en + 12], [0, 1]);
  const bote = Math.sin((f - en) / 4) * 14;
  return (
    <svg width={1080} height={220} style={{position: 'absolute', left: 0, top: y + bote}}>
      <path d="M 540 10 L 540 170 M 470 110 L 540 180 L 610 110" stroke={p.acento} strokeWidth={26} fill="none" strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - t} />
    </svg>
  );
};

export const Emoji: React.FC<{e: string; x: number; y: number; tam: number; esc?: number; op?: number}> = ({e, x, y, tam, esc = 1, op = 1}) => (
  <div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam, fontSize: tam * 0.86, lineHeight: 1, textAlign: 'center', transform: `scale(${esc})`, opacity: op, fontFamily: '"Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", sans-serif'}}>{e}</div>
);

/** Cierre común: ESCRIBIME "PALABRA" → PRIMER REEL GRATIS + flecha + usuario. */
export const Cierre: React.FC<{p: Paleta; palabra: string; en: number; dur: number}> = ({p, palabra, en, dur}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < en) return null;
  const sal = tween(f, [en + dur - 8, en + dur], [1, 0]);
  const sp = resorte(f, fps, en + 30, 'rebote');
  return (
    <AbsoluteFill style={{opacity: sal}}>
      <Frase p={p} en={en} y={ARRIBA + 210} tam={110} lineas={[['ESCRIBIME'], [{t: `"${palabra}"`, acento: true}]]} />
      <Flecha p={p} en={en + 14} y={ARRIBA + 430} />
      <div style={{position: 'absolute', left: 90, right: 90, top: ARRIBA + 680, padding: '34px 20px', borderRadius: 40, background: p.acento, color: p.fondo, textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 92, lineHeight: 1, transform: `scale(${sp})`}}>PRIMER REEL GRATIS</div>
      <div style={{position: 'absolute', left: 0, right: 0, top: ARRIBA + 930, textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 800, fontSize: 52, color: p.texto, opacity: tween(f, [en + 40, en + 50], [0, 1])}}>{USUARIO}</div>
    </AbsoluteFill>
  );
};

/** Corte seco: destello corto en cada cambio de escena. */
export const Corte: React.FC<{en: number[]; color: string}> = ({en, color}) => {
  const f = useCurrentFrame();
  const c = en.find((x) => f >= x && f < x + 3);
  return c !== undefined ? <AbsoluteFill style={{background: color, opacity: 0.25}} /> : null;
};

export const ruido = (s: string) => random(s);

/** Marca fija desde el primer cuadro (arriba de la franja segura). */
export const Marca: React.FC<{p: Paleta}> = ({p}) => (
  <div style={{position: 'absolute', top: ARRIBA + 8, left: 0, right: 0, display: 'flex', justifyContent: 'center', zIndex: 50}}>
    <div style={{padding: '12px 30px', borderRadius: 40, background: p.acento, color: p.fondo, fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 34, letterSpacing: '0.04em'}}>VIRALIZA TU NEGOCIO · EDITOR DE REELS</div>
  </div>
);

export const PLANES = [
  {n: 'BÁSICO', precio: '$25.000', reels: '4 REELS', det: '1 por semana'},
  {n: 'MEDIO', precio: '$50.000', reels: '10 REELS', det: 'guion con gancho', rec: true},
  {n: 'PREMIUM', precio: '$100.000', reels: '20 REELS', det: '5 por semana'},
];

/** Tres tarjetas de planes que entran una por una. */
export const Planes: React.FC<{p: Paleta; en: number}> = ({p, en}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <>
      <Frase p={p} en={en} tam={84} y={ARRIBA + 170} lineas={[['PLANES', {t: 'POR MES', acento: true}]]} />
      {PLANES.map((pl, i) => {
        const s = resorte(f, fps, en + 10 + i * 18, 'pop');
        return (
          <div key={pl.n} style={{position: 'absolute', left: 80, right: 80, top: ARRIBA + 280 + i * 290, height: 250, borderRadius: 36, background: pl.rec ? p.acento : 'rgba(127,127,127,0.14)', border: pl.rec ? 'none' : `4px solid ${p.acento}`, color: pl.rec ? p.fondo : p.texto, fontFamily: FUENTE.inter, display: 'flex', alignItems: 'center', padding: '0 46px', justifyContent: 'space-between', opacity: Math.min(1, s * 2), transform: `translateX(${(1 - s) * (i % 2 ? 900 : -900)}px) scale(${pl.rec ? 1.03 : 1})`}}>
            <div>
              <div style={{fontWeight: 900, fontSize: 64, lineHeight: 1}}>{pl.n}</div>
              <div style={{fontWeight: 700, fontSize: 36, opacity: 0.85, marginTop: 10}}>{pl.reels} · {pl.det}</div>
            </div>
            <div style={{fontWeight: 900, fontSize: 70}}>{pl.precio}</div>
            {pl.rec ? <div style={{position: 'absolute', top: -26, right: 40, background: p.texto, color: p.fondo, fontWeight: 900, fontSize: 30, padding: '8px 22px', borderRadius: 30}}>RECOMENDADO</div> : null}
          </div>
        );
      })}
    </>
  );
};
