import React from 'react';
import {Audio, Sequence, staticFile} from 'remotion';

export type EventoSfx = {en: number; sfx: string; vol?: number};

/** Coloca efectos de sonido en cuadros exactos. sfx = nombre sin "sfx-" ni ".wav" */
export const Efectos: React.FC<{eventos: EventoSfx[]; volumen?: number}> = ({eventos, volumen = 1}) => (
  <>
    {eventos.map((e, i) => (
      <Sequence key={i} from={Math.max(0, Math.round(e.en))} durationInFrames={90} layout="none">
        <Audio src={staticFile(`audio/sfx-${e.sfx}.wav`)} volume={(e.vol ?? 0.6) * volumen} />
      </Sequence>
    ))}
  </>
);

export const Musica: React.FC<{archivo: string; volumen?: number; loop?: boolean}> = ({
  archivo,
  volumen = 0.85,
  loop = false,
}) => <Audio src={staticFile(`audio/${archivo}`)} volume={volumen} loop={loop} />;
