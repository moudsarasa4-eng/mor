import React from 'react';
import {AbsoluteFill, Img, random, staticFile, useCurrentFrame} from 'remotion';

/** Grano de película + viñeta: le saca lo "digital" a los fondos planos. */
export const Grano: React.FC<{opacidad?: number; vineta?: number}> = ({opacidad = 0.06, vineta = 0.55}) => {
  const f = useCurrentFrame();
  const x = Math.floor(random(`gx${f}`) * 384);
  const y = Math.floor(random(`gy${f}`) * 384);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill
        style={{
          backgroundImage: `url(${staticFile('img/grano.png')})`,
          backgroundPosition: `${x}px ${y}px`,
          backgroundSize: '384px 384px',
          opacity: opacidad,
          mixBlendMode: 'overlay',
        }}
      />
      <AbsoluteFill
        style={{background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,${vineta}) 100%)`}}
      />
      {/* precarga invisible para que la textura esté lista en el primer cuadro */}
      <Img src={staticFile('img/grano.png')} style={{width: 1, height: 1, opacity: 0, position: 'absolute'}} />
    </AbsoluteFill>
  );
};
