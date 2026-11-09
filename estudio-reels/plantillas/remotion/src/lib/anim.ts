import {Easing, interpolate, random, spring} from 'remotion';

export const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const EASE_OUT = Easing.bezier(0.22, 1, 0.36, 1);
export const EASE_IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);

/** interpolate con clamp y easing suave */
export const tween = (
  f: number,
  rango: [number, number],
  valores: [number, number],
  easing: (t: number) => number = EASE_OUT,
) => interpolate(f, rango, valores, {...CLAMP, easing});

/** Resorte con presets. delay en cuadros. */
export const resorte = (
  frame: number,
  fps: number,
  delay = 0,
  tipo: 'pop' | 'suave' | 'rebote' | 'seco' = 'pop',
) => {
  const config = {
    pop: {damping: 13, stiffness: 190, mass: 0.6},
    suave: {damping: 22, stiffness: 120, mass: 0.9},
    rebote: {damping: 9, stiffness: 160, mass: 0.7},
    seco: {damping: 30, stiffness: 300, mass: 0.5},
  }[tipo];
  return spring({frame: frame - delay, fps, config});
};

/** Pulso en cada tiempo (0..1, decae rápido). beat en cuadros. */
export const pulso = (frame: number, beat: number, desfase = 0, caida = 6) => {
  const r = (((frame - desfase) % beat) + beat) % beat;
  return Math.exp(-r / caida);
};

/** Vibración determinística (para "cámara en mano" o la máquina). */
export const temblor = (frame: number, seed: string, amp: number) => ({
  x: (random(`${seed}-x-${frame}`) - 0.5) * 2 * amp,
  y: (random(`${seed}-y-${frame}`) - 0.5) * 2 * amp,
});

/** Ruido suave (para derivas lentas). */
export const deriva = (frame: number, velocidad = 0.02, fase = 0) =>
  Math.sin(frame * velocidad + fase) * 0.6 + Math.sin(frame * velocidad * 0.53 + fase * 1.7) * 0.4;
