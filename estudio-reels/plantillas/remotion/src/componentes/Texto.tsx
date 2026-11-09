import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {resorte, tween} from '../lib/anim';

// ---------------------------------------------------------------- Titular (palabra por palabra)
export type Palabra = {
  t: string;
  /** cuadro en que aparece */
  en: number;
  color?: string;
  /** caja tipo resaltador detrás de la palabra */
  fondo?: string;
  /** degradé de relleno (ej. dorado) */
  degradado?: string;
  fuente?: string;
  peso?: number;
  tam?: number;
  italica?: boolean;
  /** escala relativa al tamaño base */
  rel?: number;
};

type TitularProps = {
  lineas: Palabra[][];
  top: number;
  tam: number;
  fuente: string;
  peso?: number;
  color?: string;
  hasta?: number;
  alineacion?: 'center' | 'left' | 'right';
  interlineado?: number;
  sombra?: string;
  mayus?: boolean;
  tracking?: string;
  izquierda?: number;
  ancho?: number;
  /** tipo de entrada */
  entrada?: 'pop' | 'golpe' | 'sube';
  inclinacion?: number;
};

export const Titular: React.FC<TitularProps> = ({
  lineas,
  top,
  tam,
  fuente,
  peso = 900,
  color = '#fff',
  hasta,
  alineacion = 'center',
  interlineado = 1.02,
  sombra = '0 8px 30px rgba(0,0,0,0.45)',
  mayus = false,
  tracking = '-0.02em',
  izquierda = 70,
  ancho = 940,
  entrada = 'pop',
  inclinacion = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const salida = hasta === undefined ? 1 : tween(frame, [hasta - 7, hasta], [1, 0]);
  if (salida <= 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: izquierda,
        width: ancho,
        textAlign: alineacion,
        fontFamily: fuente,
        fontWeight: peso,
        fontSize: tam,
        lineHeight: interlineado,
        color,
        letterSpacing: tracking,
        textTransform: mayus ? 'uppercase' : 'none',
        textShadow: sombra,
        opacity: salida,
        transform: `scale(${0.94 + 0.06 * salida}) skewX(${inclinacion}deg)`,
      }}
    >
      {lineas.map((linea, i) => (
        <div key={i} style={{whiteSpace: 'nowrap'}}>
          {linea.map((p, j) => {
            const s = resorte(frame, fps, p.en, entrada === 'golpe' ? 'seco' : 'pop');
            if (frame < p.en) {
              return (
                <span key={j} style={{opacity: 0, display: 'inline-block', fontSize: p.rel ? `${p.rel}em` : undefined}}>
                  {p.t}
                  {j < linea.length - 1 ? ' ' : ''}
                </span>
              );
            }
            const esc =
              entrada === 'golpe' ? 1.45 - 0.45 * s : entrada === 'sube' ? 1 : 0.55 + 0.45 * s;
            const dy = entrada === 'sube' ? (1 - s) * tam * 0.6 : (1 - s) * tam * 0.18;
            const base: React.CSSProperties = {
              display: 'inline-block',
              transform: `translateY(${dy}px) scale(${esc})`,
              opacity: Math.min(1, s * 1.8),
              color: p.color,
              fontFamily: p.fuente,
              fontWeight: p.peso,
              fontStyle: p.italica ? 'italic' : undefined,
              fontSize: p.rel ? `${p.rel}em` : p.tam,
            };
            if (p.fondo) {
              Object.assign(base, {
                background: p.fondo,
                padding: '0.02em 0.16em 0.06em',
                borderRadius: '0.14em',
                textShadow: 'none',
                boxShadow: '0 10px 30px rgba(0,0,0,0.25)',
              });
            }
            if (p.degradado) {
              Object.assign(base, {
                backgroundImage: p.degradado,
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text',
                color: 'transparent',
                textShadow: 'none',
                filter: 'drop-shadow(0 6px 18px rgba(0,0,0,0.5))',
              });
            }
            return (
              <React.Fragment key={j}>
                <span style={base}>{p.t}</span>
                {j < linea.length - 1 ? <span style={{display: 'inline-block', width: '0.24em'}} /> : null}
              </React.Fragment>
            );
          })}
        </div>
      ))}
    </div>
  );
};

/** atajo: arma palabras a partir de un texto, una cada `paso` cuadros */
export const palabras = (
  texto: string,
  desde: number,
  paso: number,
  extra: (p: string, i: number) => Partial<Palabra> = () => ({}),
): Palabra[] =>
  texto.split(' ').map((t, i) => ({t, en: desde + i * paso, ...extra(t, i)}));

// ---------------------------------------------------------------- Subtítulos tipo "word-pop"
export type Frase = {texto: string; desde: number; hasta: number; paso?: number};

type SubProps = {
  frases: Frase[];
  top: number;
  tam: number;
  fuente: string;
  peso?: number;
  color?: string;
  colorActivo?: string;
  fondoActivo?: string;
  sombra?: string;
  mayus?: boolean;
  paso?: number;
  ancho?: number;
  izquierda?: number;
  /** contorno del texto (legibilidad sobre fondos claros) */
  contorno?: string;
};

export const Subtitulos: React.FC<SubProps> = ({
  frases,
  top,
  tam,
  fuente,
  peso = 800,
  color = '#fff',
  colorActivo = '#fff',
  fondoActivo = '#E8432E',
  sombra = '0 4px 16px rgba(0,0,0,0.5)',
  mayus = false,
  paso = 6,
  ancho = 860,
  izquierda = 110,
  contorno,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const frase = frases.find((f) => frame >= f.desde && frame < f.hasta);
  if (!frase) return null;
  const ws = frase.texto.split(' ');
  const pf = frase.paso ?? paso;
  const visibles = Math.min(ws.length, Math.floor((frame - frase.desde) / pf) + 1);
  const activa = visibles - 1;
  const salida = tween(frame, [frase.hasta - 4, frase.hasta], [1, 0]);
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: izquierda,
        width: ancho,
        textAlign: 'center',
        fontFamily: fuente,
        fontWeight: peso,
        fontSize: tam,
        lineHeight: 1.18,
        color,
        textTransform: mayus ? 'uppercase' : 'none',
        opacity: salida,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: `0.12em 0.26em`,
      }}
    >
      {ws.map((w, i) => {
        if (i >= visibles) return null;
        const s = resorte(frame, fps, frase.desde + i * pf, 'pop');
        const on = i === activa;
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              transform: `scale(${(0.6 + 0.4 * s) * (on ? 1.06 : 1)})`,
              opacity: Math.min(1, s * 2),
              padding: '0.02em 0.14em 0.06em',
              borderRadius: '0.16em',
              background: on ? fondoActivo : 'transparent',
              color: on ? colorActivo : color,
              textShadow: on ? 'none' : sombra,
              WebkitTextStroke: !on && contorno ? contorno : undefined,
              paintOrder: 'stroke fill',
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};
