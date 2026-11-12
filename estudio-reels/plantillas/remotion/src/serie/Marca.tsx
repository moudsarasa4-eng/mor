import React from 'react';
import {AbsoluteFill} from 'remotion';
import {FUENTE} from '../lib/fuentes';

// IDENTIDAD DE @viraliza.tu.perfil.arg — se usa igual en TODOS los reels.
export const MARCA = {
  negro: '#0A0A0A',
  lima: '#C6FF00', // acento principal (palabra clave, botones, logo)
  blanco: '#FFFFFF',
  rojo: '#FF2E4D', // solo para lo "malo" (tachar, ✗, antes)
  gris: '#2A2A2A',
  fuente: FUENTE.inter, // Inter Black 900, siempre en MAYÚSCULAS para frases de impacto
};

/** Logo: círculo lima con "play" negro + wordmark. */
export const Logo: React.FC<{tam?: number; conTexto?: boolean; color?: string}> = ({tam = 120, conTexto = true, color = MARCA.blanco}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: tam * 0.22}}>
    <div style={{width: tam, height: tam, borderRadius: '50%', background: MARCA.lima, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 0 ${tam * 0.4}px ${MARCA.lima}55`}}>
      <svg width={tam * 0.5} height={tam * 0.5} viewBox="0 0 10 10">
        <path d="M 2.6 1.6 L 8.6 5 L 2.6 8.4 Z" fill={MARCA.negro} />
      </svg>
    </div>
    {conTexto ? (
      <div style={{fontFamily: MARCA.fuente, lineHeight: 0.9}}>
        <div style={{fontWeight: 900, fontSize: tam * 0.62, color, letterSpacing: '-0.03em'}}>VIRALIZA</div>
        <div style={{fontWeight: 800, fontSize: tam * 0.28, color: MARCA.lima, letterSpacing: '0.18em'}}>TU PERFIL</div>
      </div>
    ) : null}
  </div>
);

/** Sello fijo de la cuenta (arriba de la franja segura, en todos los reels). */
export const Sello: React.FC<{top?: number}> = ({top = 300}) => (
  <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', justifyContent: 'center', zIndex: 50}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '10px 26px 10px 12px', borderRadius: 50, background: 'rgba(10,10,10,0.85)', border: `3px solid ${MARCA.lima}`}}>
      <Logo tam={44} conTexto={false} />
      <span style={{fontFamily: MARCA.fuente, fontWeight: 900, fontSize: 32, color: MARCA.blanco, letterSpacing: '0.02em'}}>EDITOR DE REELS</span>
    </div>
  </div>
);

export const FondoMarca: React.FC = () => (
  <AbsoluteFill style={{background: MARCA.negro}}>
    <AbsoluteFill style={{backgroundImage: `radial-gradient(circle at 50% 120%, ${MARCA.lima}22 0%, transparent 55%)`}} />
  </AbsoluteFill>
);
