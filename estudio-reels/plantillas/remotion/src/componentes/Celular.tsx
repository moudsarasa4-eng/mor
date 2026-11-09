import React from 'react';
import {FUENTE} from '../lib/fuentes';
import {Avion, Bateria, Burbuja, Casa, Corazon, Lupa, Mas, Nota, Persona, Puntos, Senal, Videos, Wifi} from './Iconos';

// Celular GENÉRICO (sin marca) con una interfaz de reels GENÉRICA (sin logo, sin números).

export type UIReel = {
  cuenta: string;
  inicial?: string;
  colorAvatar?: string;
  descripcion?: string;
  audio?: string;
};

export type Resaltado = {
  /** rectángulo en coordenadas del video 1080×1920 */
  x: number;
  y: number;
  w: number;
  h: number;
  /** 0..1: animación de entrada */
  t: number;
  color?: string;
  etiqueta?: string;
};

type Props = {
  ancho: number;
  /** contenido en 1080×1920 (se escala solo) */
  children?: React.ReactNode;
  /** contenido que ocupa toda la pantalla, en px de pantalla (ej.: bandeja de mensajes) */
  pantalla?: React.ReactNode;
  ui?: UIReel | null;
  ejemplo?: boolean;
  progreso?: number;
  hora?: string;
  resaltar?: Resaltado | null;
  /** 0 = normal, 1 = muy apagado */
  apagado?: number;
  /** cuánto se ve la pantalla del video vs la pantalla alternativa (0..1) */
  mezclaPantalla?: number;
  conNav?: boolean;
};

export const medidasCelular = (ancho: number) => {
  const bisel = ancho * 0.035;
  const ws = ancho - 2 * bisel;
  const videoH = (ws * 16) / 9;
  const navH = ws * 0.115;
  const hs = videoH + navH;
  return {bisel, ws, videoH, navH, hs, alto: hs + 2 * bisel};
};

export const Celular: React.FC<Props> = ({
  ancho,
  children,
  pantalla,
  ui = null,
  ejemplo = true,
  progreso,
  hora = '21:47',
  resaltar = null,
  apagado = 0,
  mezclaPantalla = 0,
  conNav = true,
}) => {
  const {bisel, ws, videoH, navH, hs, alto} = medidasCelular(ancho);
  const u = ws / 100; // 1u = 1% del ancho de pantalla
  const radioCuerpo = ancho * 0.14;
  const radioPantalla = ancho * 0.11;
  const escala = ws / 1080;

  return (
    <div style={{position: 'relative', width: ancho, height: alto}}>
      {/* botones laterales */}
      <div style={{...boton, right: -ancho * 0.011, top: alto * 0.2, height: alto * 0.085, width: ancho * 0.016}} />
      <div style={{...boton, left: -ancho * 0.011, top: alto * 0.16, height: alto * 0.06, width: ancho * 0.016}} />
      <div style={{...boton, left: -ancho * 0.011, top: alto * 0.235, height: alto * 0.06, width: ancho * 0.016}} />
      {/* cuerpo */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: radioCuerpo,
          background: 'linear-gradient(150deg,#3a3a43 0%,#17171c 30%,#0b0b0e 62%,#2a2a32 100%)',
          boxShadow: `0 ${ancho * 0.07}px ${ancho * 0.16}px rgba(0,0,0,0.62), 0 ${ancho * 0.015}px ${ancho * 0.03}px rgba(0,0,0,0.5), inset 0 0 0 ${Math.max(1, ancho * 0.004)}px rgba(255,255,255,0.16)`,
        }}
      />
      {/* pantalla */}
      <div
        style={{
          position: 'absolute',
          left: bisel,
          top: bisel,
          width: ws,
          height: hs,
          borderRadius: radioPantalla,
          overflow: 'hidden',
          background: '#000',
        }}
      >
        <div style={{position: 'absolute', left: 0, top: 0, width: ws, height: videoH, overflow: 'hidden'}}>
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: 1080,
              height: 1920,
              transform: `scale(${escala})`,
              transformOrigin: '0 0',
              opacity: 1 - mezclaPantalla,
            }}
          >
            {children}
          </div>
          {ui && mezclaPantalla < 1 ? (
            <div style={{position: 'absolute', inset: 0, opacity: 1 - mezclaPantalla}}>
              <InterfazReel u={u} videoH={videoH} ws={ws} ui={ui} progreso={progreso} />
            </div>
          ) : null}
          {resaltar ? <Resalte r={resaltar} escala={escala} u={u} /> : null}
        </div>
        {pantalla ? (
          <div style={{position: 'absolute', left: 0, top: 0, width: ws, height: videoH, opacity: mezclaPantalla}}>
            {pantalla}
          </div>
        ) : null}
        {conNav ? <BarraNav u={u} top={videoH} alto={navH} ws={ws} /> : null}
        <BarraEstado u={u} hora={hora} ws={ws} />
        {ejemplo ? (
          <div
            style={{
              position: 'absolute',
              left: 4 * u,
              top: 8.6 * u,
              padding: `${0.7 * u}px ${1.7 * u}px`,
              borderRadius: 1.2 * u,
              background: 'rgba(0,0,0,0.58)',
              border: `${Math.max(1, 0.18 * u)}px solid rgba(255,255,255,0.4)`,
              color: '#fff',
              fontFamily: FUENTE.inter,
              fontWeight: 800,
              fontSize: 2.7 * u,
              letterSpacing: '0.14em',
            }}
          >
            EJEMPLO
          </div>
        ) : null}
        {apagado > 0 ? <div style={{position: 'absolute', inset: 0, background: `rgba(0,0,0,${apagado})`}} /> : null}
        {/* reflejo del vidrio */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(118deg, rgba(255,255,255,0.13) 0%, rgba(255,255,255,0.03) 28%, rgba(255,255,255,0) 40%)',
            pointerEvents: 'none',
          }}
        />
        {/* cámara frontal */}
        <div
          style={{
            position: 'absolute',
            left: ws / 2 - 1.5 * u,
            top: 1.9 * u,
            width: 3 * u,
            height: 3 * u,
            borderRadius: '50%',
            background: 'radial-gradient(circle at 35% 35%, #2b3140 0%, #07080b 60%)',
            boxShadow: `0 0 0 ${0.3 * u}px #000`,
          }}
        />
      </div>
    </div>
  );
};

const boton: React.CSSProperties = {
  position: 'absolute',
  borderRadius: 6,
  background: 'linear-gradient(90deg,#1b1b20,#3b3b44,#1b1b20)',
};

const BarraEstado: React.FC<{u: number; hora: string; ws: number}> = ({u, hora}) => (
  <div
    style={{
      position: 'absolute',
      left: 0,
      right: 0,
      top: 0,
      height: 7 * u,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: `0 ${6 * u}px`,
      color: '#fff',
      fontFamily: FUENTE.inter,
      fontWeight: 600,
      fontSize: 3.3 * u,
      textShadow: '0 1px 4px rgba(0,0,0,0.4)',
    }}
  >
    <span>{hora}</span>
    <span style={{display: 'flex', gap: 1.4 * u, alignItems: 'center'}}>
      <Senal alto={2.6 * u} />
      <Wifi alto={2.6 * u} />
      <Bateria alto={2.5 * u} />
    </span>
  </div>
);

const BarraNav: React.FC<{u: number; top: number; alto: number; ws: number}> = ({u, top, alto, ws}) => {
  const s = 6 * u;
  const g = 0.32 * 24 / 6; // grosor visual parejo
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        top,
        width: ws,
        height: alto,
        background: '#000',
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'flex-start',
        paddingTop: 2.2 * u,
        borderTop: `${Math.max(1, 0.12 * u)}px solid rgba(255,255,255,0.12)`,
      }}
    >
      <Casa size={s} grosor={g} />
      <Lupa size={s} grosor={g} />
      <Mas size={s} grosor={g} />
      <Videos size={s} grosor={g} relleno="rgba(255,255,255,0.15)" />
      <Persona size={s} grosor={g} />
      <div
        style={{
          position: 'absolute',
          bottom: 1.6 * u,
          left: ws / 2 - 14 * u,
          width: 28 * u,
          height: 0.9 * u,
          borderRadius: u,
          background: 'rgba(255,255,255,0.75)',
        }}
      />
    </div>
  );
};

const InterfazReel: React.FC<{u: number; videoH: number; ws: number; ui: UIReel; progreso?: number}> = ({
  u,
  videoH,
  ws,
  ui,
  progreso,
}) => {
  const icono = 7.2 * u;
  const g = 1.9;
  const columna = [<Corazon key="c" size={icono} grosor={g} />, <Burbuja key="b" size={icono} grosor={g} />, <Avion key="a" size={icono} grosor={g} />, <Puntos key="p" size={icono} />];
  return (
    <div style={{position: 'absolute', inset: 0, fontFamily: FUENTE.inter, color: '#fff'}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: videoH * 0.32,
          background: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.5) 100%)',
        }}
      />
      {columna.map((ic, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: ws - 11.2 * u,
            top: videoH - (58 - i * 11.5) * u,
            filter: 'drop-shadow(0 1px 3px rgba(0,0,0,0.45))',
          }}
        >
          {ic}
        </div>
      ))}
      <div
        style={{
          position: 'absolute',
          left: ws - 10.6 * u,
          top: videoH - 11.5 * u,
          width: 6.2 * u,
          height: 6.2 * u,
          borderRadius: 1.4 * u,
          border: `${0.45 * u}px solid #fff`,
          background: ui.colorAvatar ?? '#444',
        }}
      />
      {/* cuenta */}
      <div style={{position: 'absolute', left: 3.6 * u, top: videoH - 25.5 * u, display: 'flex', alignItems: 'center', gap: 2 * u}}>
        <div
          style={{
            width: 7.4 * u,
            height: 7.4 * u,
            borderRadius: '50%',
            background: ui.colorAvatar ?? '#555',
            border: `${0.35 * u}px solid rgba(255,255,255,0.9)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: 3.1 * u,
          }}
        >
          {ui.inicial ?? ui.cuenta.slice(0, 1).toUpperCase()}
        </div>
        <span style={{fontWeight: 700, fontSize: 3.4 * u, textShadow: '0 1px 4px rgba(0,0,0,0.5)'}}>{ui.cuenta}</span>
        <span
          style={{
            fontWeight: 600,
            fontSize: 2.9 * u,
            padding: `${0.5 * u}px ${1.8 * u}px`,
            border: `${0.25 * u}px solid rgba(255,255,255,0.85)`,
            borderRadius: 1.4 * u,
          }}
        >
          Seguir
        </span>
      </div>
      {ui.descripcion ? (
        <div
          style={{
            position: 'absolute',
            left: 3.6 * u,
            width: ws * 0.72,
            top: videoH - 15.6 * u,
            fontSize: 3.15 * u,
            fontWeight: 500,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            textShadow: '0 1px 4px rgba(0,0,0,0.55)',
          }}
        >
          {ui.descripcion}
        </div>
      ) : null}
      <div
        style={{
          position: 'absolute',
          left: 3.6 * u,
          top: videoH - 9.4 * u,
          display: 'flex',
          alignItems: 'center',
          gap: 1.2 * u,
          fontSize: 2.9 * u,
          fontWeight: 500,
          opacity: 0.95,
        }}
      >
        <Nota size={3.2 * u} grosor={2.2} />
        <span>{ui.audio ?? 'Audio original'}</span>
      </div>
      {progreso !== undefined ? (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 0.55 * u, background: 'rgba(255,255,255,0.28)'}}>
          <div style={{width: `${Math.min(1, Math.max(0, progreso)) * 100}%`, height: '100%', background: '#fff'}} />
        </div>
      ) : null}
    </div>
  );
};

const Resalte: React.FC<{r: Resaltado; escala: number; u: number}> = ({r, escala, u}) => {
  const color = r.color ?? '#2BEA7A';
  const s = 1.08 - 0.08 * r.t;
  return (
    <div
      style={{
        position: 'absolute',
        left: r.x * escala,
        top: r.y * escala,
        width: r.w * escala,
        height: r.h * escala,
        borderRadius: 3 * u,
        border: `${0.9 * u}px solid ${color}`,
        boxShadow: `0 0 ${3.5 * u}px ${color}, inset 0 0 ${2 * u}px ${color}55`,
        opacity: r.t,
        transform: `scale(${s})`,
      }}
    >
      {r.etiqueta ? (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: -5.2 * u,
            transform: 'translateX(-50%)',
            background: color,
            color: '#04130a',
            fontFamily: FUENTE.inter,
            fontWeight: 900,
            fontSize: 3.4 * u,
            padding: `${0.5 * u}px ${2 * u}px`,
            borderRadius: 1.6 * u,
            whiteSpace: 'nowrap',
          }}
        >
          {r.etiqueta}
        </div>
      ) : null}
    </div>
  );
};
