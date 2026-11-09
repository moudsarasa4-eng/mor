import React from 'react';

// Íconos GENÉRICOS (dibujados acá, no son los de ninguna app). viewBox 24x24, trazo.
type P = {size: number; color?: string; grosor?: number; relleno?: string; style?: React.CSSProperties};

const Svg: React.FC<P & {children: React.ReactNode}> = ({size, color = '#fff', grosor = 1.9, relleno = 'none', style, children}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill={relleno}
    stroke={color}
    strokeWidth={grosor}
    strokeLinecap="round"
    strokeLinejoin="round"
    style={style}
  >
    {children}
  </svg>
);

export const Corazon: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M12 20.5s-7.2-4.4-9.2-8.8C1.4 8.3 3.5 4.8 6.9 4.8c2 0 3.5 1 4.3 2.5.8-1.5 2.3-2.5 4.3-2.5 3.4 0 5.5 3.5 4.1 6.9-2 4.4-7.6 8.8-7.6 8.8z" />
  </Svg>
);
export const Burbuja: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M20.2 11.6a8.2 8.2 0 0 1-12 7.3L3.8 20.3l1.4-4.1a8.2 8.2 0 1 1 15-4.6z" />
  </Svg>
);
export const Avion: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M21.2 3.2 2.9 10.4l7.2 2.7 2.8 7.4z" />
    <path d="M10.1 13.1 15.4 7.9" />
  </Svg>
);
export const Puntos: React.FC<P> = ({size, color = '#fff', style}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={style}>
    {[5, 12, 19].map((x) => (
      <circle key={x} cx={x} cy={12} r={1.9} fill={color} />
    ))}
  </svg>
);
export const Nota: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M9 17.5V6.2l10-2.1v11" />
    <circle cx={6.6} cy={17.6} r={2.5} />
    <circle cx={16.6} cy={15.2} r={2.5} />
  </Svg>
);
export const Casa: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M3.5 10.8 12 4l8.5 6.8V20h-5.6v-5.6H9.1V20H3.5z" />
  </Svg>
);
export const Lupa: React.FC<P> = (p) => (
  <Svg {...p}>
    <circle cx={10.5} cy={10.5} r={6.2} />
    <path d="m15.2 15.2 5 5" />
  </Svg>
);
export const Mas: React.FC<P> = (p) => (
  <Svg {...p}>
    <rect x={3.5} y={3.5} width={17} height={17} rx={4.5} />
    <path d="M12 8v8M8 12h8" />
  </Svg>
);
export const Videos: React.FC<P> = (p) => (
  <Svg {...p}>
    <rect x={3.5} y={3.5} width={17} height={17} rx={4.5} />
    <path d="m10 8.6 5.4 3.4-5.4 3.4z" />
  </Svg>
);
export const Persona: React.FC<P> = (p) => (
  <Svg {...p}>
    <circle cx={12} cy={8.6} r={3.8} />
    <path d="M4.6 20.2c1.2-3.6 4-5.4 7.4-5.4s6.2 1.8 7.4 5.4" />
  </Svg>
);
export const Check: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="m4.5 12.5 4.6 4.6L19.5 6.7" />
  </Svg>
);
export const Flecha: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </Svg>
);
export const Chat: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M4 5.5h16v10.5H9.5L5 19.8V16H4z" />
  </Svg>
);
export const Reloj: React.FC<P> = (p) => (
  <Svg {...p}>
    <circle cx={12} cy={12} r={8} />
    <path d="M12 7.5V12l3 2" />
  </Svg>
);

// Barra de estado genérica
export const Senal: React.FC<{alto: number; color?: string}> = ({alto, color = '#fff'}) => (
  <svg width={alto * 1.25} height={alto} viewBox="0 0 20 16">
    {[0, 1, 2, 3].map((i) => (
      <rect key={i} x={i * 5} y={12 - i * 3.6} width={3.4} height={4 + i * 3.6} rx={1} fill={color} />
    ))}
  </svg>
);
export const Wifi: React.FC<{alto: number; color?: string}> = ({alto, color = '#fff'}) => (
  <svg width={alto * 1.3} height={alto} viewBox="0 0 22 17" fill="none" stroke={color} strokeWidth={2.4} strokeLinecap="round">
    <path d="M2 6.2a13.5 13.5 0 0 1 18 0" />
    <path d="M5.4 9.8a8.5 8.5 0 0 1 11.2 0" />
    <circle cx={11} cy={14} r={1.6} fill={color} stroke="none" />
  </svg>
);
export const Bateria: React.FC<{alto: number; color?: string; nivel?: number}> = ({alto, color = '#fff', nivel = 0.78}) => (
  <svg width={alto * 2} height={alto} viewBox="0 0 30 15">
    <rect x={1} y={1} width={25} height={13} rx={3.5} fill="none" stroke={color} strokeOpacity={0.55} strokeWidth={1.6} />
    <rect x={3} y={3} width={21 * nivel} height={9} rx={2} fill={color} />
    <rect x={27.3} y={5} width={2} height={5} rx={1} fill={color} fillOpacity={0.55} />
  </svg>
);
