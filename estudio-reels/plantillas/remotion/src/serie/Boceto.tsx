import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Celular} from '../componentes/Celular';
import {Logo, MARCA, Sello} from './Marca';

// Tablero de bocetos: identidad + 5 plantillas agresivas (4 cuadros clave cada una).
const T = MARCA.fuente;
const Big: React.FC<{l: {t: string; c?: string; fondo?: string; tachar?: boolean}[][]; top: number; tam: number}> = ({l, top, tam}) => (
  <div style={{position: 'absolute', top, left: 50, right: 50, textAlign: 'center', fontFamily: T, fontWeight: 900, fontSize: tam, lineHeight: 1.0, letterSpacing: '-0.03em', color: MARCA.blanco}}>
    {l.map((linea, i) => (
      <div key={i}>
        {linea.map((w, j) => (
          <span key={j} style={{color: w.c, background: w.fondo, padding: w.fondo ? '0 0.12em' : 0, borderRadius: 12, margin: '0 0.1em', textDecoration: w.tachar ? `line-through ${MARCA.rojo} 0.12em` : 'none'}}>{w.t}</span>
        ))}
      </div>
    ))}
  </div>
);
const L = MARCA.lima, R = MARCA.rojo;

const Cuadro: React.FC<{children: React.ReactNode; nota: string}> = ({children, nota}) => (
  <div style={{width: 300}}>
    <div style={{width: 300, height: 533, overflow: 'hidden', borderRadius: 18, position: 'relative', border: '2px solid #333'}}>
      <div style={{width: 1080, height: 1920, transform: 'scale(0.2778)', transformOrigin: '0 0', position: 'absolute', background: MARCA.negro}}>
        <AbsoluteFill style={{backgroundImage: `radial-gradient(circle at 50% 120%, ${L}22 0%, transparent 55%)`}} />
        {children}
        <Sello />
        {/* guías de franja segura */}
        <div style={{position: 'absolute', top: 288, left: 0, right: 0, borderTop: '6px dashed #3fa9f5'}} />
        <div style={{position: 'absolute', top: 1440, left: 0, right: 0, borderTop: '6px dashed #3fa9f5'}} />
      </div>
    </div>
    <div style={{fontFamily: T, fontWeight: 600, fontSize: 19, color: '#aaa', marginTop: 8, lineHeight: 1.25}}>{nota}</div>
  </div>
);

const Cierre: React.FC<{palabra: string}> = ({palabra}) => (
  <>
    <div style={{position: 'absolute', top: 470, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}><Logo tam={150} /></div>
    <Big top={760} tam={100} l={[[{t: 'ESCRIBIME'}], [{t: `"${palabra}"`, c: L}]]} />
    <div style={{position: 'absolute', top: 1040, left: 90, right: 90, padding: '30px 0', borderRadius: 30, background: L, color: MARCA.negro, textAlign: 'center', fontFamily: T, fontWeight: 900, fontSize: 84}}>PRIMER REEL GRATIS</div>
    <div style={{position: 'absolute', top: 1220, left: 0, right: 0, textAlign: 'center', fontFamily: T, fontWeight: 800, fontSize: 48, color: '#fff'}}>@viraliza.tu.perfil.arg</div>
  </>
);
const TelEj: React.FC<{titulo: string; color?: string}> = ({titulo, color = L}) => (
  <div style={{position: 'absolute', left: 300, top: 560}}>
    <Celular ancho={480} ejemplo ui={{cuenta: 'tunegocio.ejemplo', colorAvatar: color}}>
      <AbsoluteFill style={{background: '#151515', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontFamily: T, fontWeight: 900, fontSize: 130, color: '#fff', lineHeight: 1}}>
        <div>{titulo.split('|').map((x, i) => <div key={i} style={{color: i ? color : '#fff'}}>{x}</div>)}</div>
      </AbsoluteFill>
    </Celular>
  </div>
);
const Planes: React.FC = () => (
  <>
    <Big top={420} tam={80} l={[[{t: 'PLANES'}, {t: 'POR MES', c: L}]]} />
    {[['BÁSICO', '4 REELS', '$25.000'], ['MEDIO', '10 REELS', '$50.000'], ['PREMIUM', '20 REELS', '$100.000']].map(([n, r, p], i) => (
      <div key={n} style={{position: 'absolute', left: 80, right: 80, top: 560 + i * 280, height: 240, borderRadius: 30, background: i === 1 ? L : '#1A1A1A', border: `4px solid ${L}`, color: i === 1 ? MARCA.negro : '#fff', fontFamily: T, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 40px'}}>
        <div><div style={{fontWeight: 900, fontSize: 60}}>{n}</div><div style={{fontWeight: 700, fontSize: 36}}>{r}</div></div>
        <div style={{fontWeight: 900, fontSize: 70}}>{p}</div>
        {i === 1 ? <div style={{position: 'absolute', top: -24, right: 36, background: '#fff', color: MARCA.negro, fontWeight: 900, fontSize: 28, padding: '6px 18px', borderRadius: 20}}>RECOMENDADO</div> : null}
      </div>
    ))}
  </>
);

const FILAS: {titulo: string; idea: string; cuadros: {el: React.ReactNode; nota: string}[]}[] = [
  {
    titulo: 'A · CONFRONTACIÓN', idea: 'Golpe directo al orgullo. Sacudón + palabra roja.',
    cuadros: [
      {el: <Big top={560} tam={150} l={[[{t: 'TU'}], [{t: 'INSTAGRAM'}], [{t: 'ESTÁ', c: R}, {t: 'MUERTO.', c: R}]]} />, nota: '0–3 s · "MUERTO" entra de golpe + sacudón'},
      {el: <><div style={{position: 'absolute', left: 240, right: 240, top: 600, height: 560, borderRadius: 36, background: '#222', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 260}}>💀</div><Big top={1220} tam={80} l={[[{t: 'ÚLTIMO POSTEO:'}, {t: 'HACE MESES', c: R}]]} /></>, nota: '3–8 s · problema visible'},
      {el: <><Big top={420} tam={90} l={[[{t: 'ASÍ SE'}, {t: 'REVIVE', c: L}]]} /><TelEj titulo="TU|NEGOCIO" /></>, nota: '8–18 s · anuncio de ejemplo animado'},
      {el: <Cierre palabra="REEL" />, nota: '18–25 s · cierre fijo de marca'},
    ],
  },
  {
    titulo: 'B · ANTES / DESPUÉS', idea: 'Mismo material, distinta edición. Rojo vs lima.',
    cuadros: [
      {el: <Big top={600} tam={140} l={[[{t: 'MISMO'}, {t: 'VIDEO.'}], [{t: 'OTRA', c: L}, {t: 'PLATA.', c: L}]]} />, nota: '0–3 s · gancho'},
      {el: <><div style={{position: 'absolute', left: 60, width: 460, top: 420, height: 980, borderRadius: 30, background: '#2a2a2a', border: `6px solid ${R}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T, fontWeight: 900, fontSize: 90, color: R}}>ANTES</div><div style={{position: 'absolute', right: 60, width: 460, top: 420, height: 980, borderRadius: 30, background: '#161616', border: `6px solid ${L}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T, fontWeight: 900, fontSize: 90, color: L}}>DESPUÉS</div></>, nota: '3–12 s · pantalla partida con los dos'},
      {el: <Big top={560} tam={110} l={[[{t: 'GANCHO.'}], [{t: 'SUBTÍTULOS.'}], [{t: 'RITMO.', c: L}]]} />, nota: '12–17 s · qué cambia (1 palabra c/2 s)'},
      {el: <Planes />, nota: '17–22 s · planes'},
    ],
  },
  {
    titulo: 'C · EL SCROLL TE COBRA', idea: 'Feed gris que pasa rápido; tu post desaparece.',
    cuadros: [
      {el: <Big top={600} tam={130} l={[[{t: 'TE'}, {t: 'SCROLLEARON.', c: R}]]} />, nota: '0–3 s · gancho + feed rapidísimo'},
      {el: <>{[0, 1, 2].map((i) => <div key={i} style={{position: 'absolute', left: 160, right: 160, top: 360 + i * 360, height: 320, borderRadius: 30, background: '#2a2a2a'}} />)}<Big top={1240} tam={70} l={[[{t: 'EN'}, {t: '1 SEGUNDO', c: R}]]} /></>, nota: '3–8 s · rectángulos grises volando'},
      {el: <Big top={600} tam={120} l={[[{t: 'UN REEL'}], [{t: 'LOS FRENA.', c: L}]]} />, nota: '8–12 s · el feed se congela en lima'},
      {el: <Cierre palabra="FRENO" />, nota: 'cierre'},
    ],
  },
  {
    titulo: 'D · TU COMPETENCIA YA LO HACE', idea: 'Comparación sin nombrar a nadie.',
    cuadros: [
      {el: <Big top={600} tam={130} l={[[{t: 'TU'}, {t: 'COMPETENCIA'}], [{t: 'YA SUBE', c: R}, {t: 'REELS.', c: R}]]} />, nota: '0–3 s · gancho'},
      {el: <><div style={{position: 'absolute', left: 60, right: 60, top: 420, height: 470, borderRadius: 30, background: '#2a2a2a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T, fontWeight: 900, fontSize: 100, color: '#888'}}>VOS: FOTOS</div><div style={{position: 'absolute', left: 60, right: 60, top: 930, height: 470, borderRadius: 30, background: L, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T, fontWeight: 900, fontSize: 100, color: MARCA.negro}}>ELLOS: REELS</div></>, nota: '3–9 s · bloques'},
      {el: <><Big top={420} tam={90} l={[[{t: 'TU'}, {t: 'TURNO', c: L}]]} /><TelEj titulo="ESTO|VENDÉS" /></>, nota: '9–18 s · anuncio de ejemplo'},
      {el: <Planes />, nota: 'planes + cierre'},
    ],
  },
  {
    titulo: 'E · OFERTA SIN VUELTAS', idea: 'Precio de entrada como gancho.',
    cuadros: [
      {el: <Big top={560} tam={150} l={[[{t: '$25.000', c: L}], [{t: '4 REELS.'}], [{t: 'CERO', c: R}, {t: 'EXCUSAS.', c: R}]]} />, nota: '0–3 s · precio como gancho'},
      {el: <Big top={600} tam={110} l={[[{t: 'VOS'}, {t: 'GRABÁS.'}], [{t: 'YO', c: L}, {t: 'EDITO.', c: L}]]} />, nota: '3–7 s · propuesta'},
      {el: <Planes />, nota: '7–15 s · los 3 planes'},
      {el: <Cierre palabra="PLAN" />, nota: 'cierre'},
    ],
  },
];

export const Boceto: React.FC = () => (
  <AbsoluteFill style={{background: '#111', padding: 40, fontFamily: T, color: '#fff'}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 40, marginBottom: 30}}>
      <Logo tam={110} />
      <div style={{flex: 1}}>
        <div style={{fontWeight: 900, fontSize: 40}}>IDENTIDAD · igual en todos los reels</div>
        <div style={{display: 'flex', gap: 16, marginTop: 12}}>
          {[['#0A0A0A', 'NEGRO fondo'], ['#C6FF00', 'LIMA acento'], ['#FFFFFF', 'BLANCO texto'], ['#FF2E4D', 'ROJO solo "lo malo"']].map(([c, n]) => (
            <div key={c} style={{display: 'flex', alignItems: 'center', gap: 8}}><div style={{width: 40, height: 40, borderRadius: 10, background: c, border: '2px solid #444'}} /><span style={{fontSize: 20, fontWeight: 700}}>{n}</span></div>
          ))}
        </div>
        <div style={{fontSize: 20, color: '#aaa', marginTop: 10}}>Inter Black en MAYÚSCULAS · máx. 7 palabras · 1 palabra en lima · sello "EDITOR DE REELS" fijo arriba · cierre con logo + palabra + PRIMER REEL GRATIS</div>
      </div>
    </div>
    {FILAS.map((fila) => (
      <div key={fila.titulo} style={{display: 'flex', gap: 22, marginBottom: 26, alignItems: 'flex-start'}}>
        <div style={{width: 200}}>
          <div style={{fontWeight: 900, fontSize: 30, color: L, lineHeight: 1.05}}>{fila.titulo}</div>
          <div style={{fontWeight: 600, fontSize: 20, color: '#bbb', marginTop: 10}}>{fila.idea}</div>
        </div>
        {fila.cuadros.map((c, i) => <Cuadro key={i} nota={c.nota}>{c.el}</Cuadro>)}
      </div>
    ))}
  </AbsoluteFill>
);
