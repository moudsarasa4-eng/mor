import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Celular} from '../componentes/Celular';
import {FUENTE} from '../lib/fuentes';

// IDENTIDAD PREMIUM de @viraliza.tu.perfil.arg
export const LUJO = {
  fondo: '#0F0E0C', // negro cálido
  marfil: '#F2ECE2', // texto principal
  oro: '#C9A96E', // acento champagne (una sola palabra por pantalla)
  piedra: '#8C857A', // texto secundario
  linea: 'rgba(201,169,110,0.45)',
  serif: FUENTE.playfair,
  sans: FUENTE.inter,
};

export const Monograma: React.FC<{tam?: number; texto?: boolean}> = ({tam = 110, texto = true}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: tam * 0.28}}>
    <div style={{width: tam, height: tam, borderRadius: '50%', border: `${Math.max(2, tam * 0.025)}px solid ${LUJO.oro}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: LUJO.serif, fontStyle: 'italic', fontWeight: 700, fontSize: tam * 0.56, color: LUJO.oro, lineHeight: 1}}>V</div>
    {texto ? (
      <div style={{lineHeight: 1}}>
        <div style={{fontFamily: LUJO.sans, fontWeight: 600, fontSize: tam * 0.36, letterSpacing: '0.42em', color: LUJO.marfil}}>VIRALIZA</div>
        <div style={{fontFamily: LUJO.serif, fontStyle: 'italic', fontWeight: 700, fontSize: tam * 0.26, color: LUJO.oro, marginTop: tam * 0.08, letterSpacing: '0.04em'}}>tu perfil · estudio de reels</div>
      </div>
    ) : null}
  </div>
);

/** Sello fijo: línea fina + nombre, discreto. */
const Sello: React.FC = () => (
  <div style={{position: 'absolute', top: 320, left: 0, right: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 22}}>
    <div style={{width: 90, height: 2, background: LUJO.linea}} />
    <span style={{fontFamily: LUJO.sans, fontWeight: 600, fontSize: 30, letterSpacing: '0.38em', color: LUJO.oro}}>VIRALIZA · REELS</span>
    <div style={{width: 90, height: 2, background: LUJO.linea}} />
  </div>
);

/** Título editorial: serif grande, una palabra en itálica dorada. */
const Titulo: React.FC<{l: {t: string; oro?: boolean}[][]; top: number; tam?: number; chico?: string}> = ({l, top, tam = 118, chico}) => (
  <div style={{position: 'absolute', top, left: 90, right: 90, textAlign: 'center'}}>
    <div style={{fontFamily: LUJO.serif, fontWeight: 700, fontSize: tam, lineHeight: 1.06, color: LUJO.marfil, letterSpacing: '-0.01em'}}>
      {l.map((linea, i) => (
        <div key={i}>
          {linea.map((w, j) => (
            <span key={j} style={{color: w.oro ? LUJO.oro : undefined, fontStyle: w.oro ? 'italic' : 'normal', margin: '0 0.12em'}}>{w.t}</span>
          ))}
        </div>
      ))}
    </div>
    {chico ? <div style={{marginTop: 40, fontFamily: LUJO.sans, fontWeight: 500, fontSize: 36, letterSpacing: '0.3em', color: LUJO.piedra}}>{chico}</div> : null}
  </div>
);

const Cuadro: React.FC<{children: React.ReactNode; nota: string}> = ({children, nota}) => (
  <div style={{width: 300}}>
    <div style={{width: 300, height: 533, overflow: 'hidden', borderRadius: 14, position: 'relative', border: '1px solid #3a352c'}}>
      <div style={{width: 1080, height: 1920, transform: 'scale(0.2778)', transformOrigin: '0 0', position: 'absolute', background: LUJO.fondo}}>
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 35%, rgba(201,169,110,0.10) 0%, rgba(0,0,0,0) 60%)'}} />
        {children}
        <Sello />
        <div style={{position: 'absolute', top: 288, left: 0, right: 0, borderTop: '5px dashed #3fa9f5', opacity: 0.6}} />
        <div style={{position: 'absolute', top: 1440, left: 0, right: 0, borderTop: '5px dashed #3fa9f5', opacity: 0.6}} />
      </div>
    </div>
    <div style={{fontFamily: LUJO.sans, fontWeight: 500, fontSize: 18, color: '#9a9488', marginTop: 8, lineHeight: 1.3}}>{nota}</div>
  </div>
);

const Cierre: React.FC<{palabra: string}> = ({palabra}) => (
  <>
    <div style={{position: 'absolute', top: 470, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}><Monograma tam={130} /></div>
    <Titulo top={760} tam={96} l={[[{t: 'Escribime'}], [{t: `"${palabra}"`, oro: true}]]} />
    <div style={{position: 'absolute', top: 1080, left: 200, right: 200, padding: '26px 0', border: `2px solid ${LUJO.oro}`, textAlign: 'center', fontFamily: LUJO.sans, fontWeight: 600, fontSize: 38, letterSpacing: '0.3em', color: LUJO.oro}}>PRIMER REEL SIN CARGO</div>
    <div style={{position: 'absolute', top: 1250, left: 0, right: 0, textAlign: 'center', fontFamily: LUJO.sans, fontWeight: 500, fontSize: 36, letterSpacing: '0.08em', color: LUJO.piedra}}>@viraliza.tu.perfil.arg</div>
  </>
);

const Tel: React.FC<{a: string; b: string}> = ({a, b}) => (
  <div style={{position: 'absolute', left: 310, top: 600}}>
    <Celular ancho={460} ejemplo ui={{cuenta: 'tumarca.ejemplo', colorAvatar: LUJO.oro}}>
      <AbsoluteFill style={{background: '#16130F', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
        <div style={{fontFamily: LUJO.sans, fontWeight: 600, fontSize: 52, letterSpacing: '0.4em', color: LUJO.oro}}>{a}</div>
        <div style={{fontFamily: LUJO.serif, fontWeight: 700, fontStyle: 'italic', fontSize: 170, color: LUJO.marfil, marginTop: 30}}>{b}</div>
      </AbsoluteFill>
    </Celular>
  </div>
);

const Planes: React.FC = () => (
  <>
    <Titulo top={430} tam={86} l={[[{t: 'Planes'}, {t: 'mensuales', oro: true}]]} />
    {[['ESENCIAL', '4 reels', '$25.000'], ['PROFESIONAL', '10 reels', '$50.000'], ['SIGNATURE', '20 reels', '$100.000']].map(([n, r, p], i) => (
      <div key={n} style={{position: 'absolute', left: 110, right: 110, top: 600 + i * 260, height: 220, borderTop: `1px solid ${LUJO.linea}`, borderBottom: i === 2 ? `1px solid ${LUJO.linea}` : 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        <div>
          <div style={{fontFamily: LUJO.sans, fontWeight: 600, fontSize: 40, letterSpacing: '0.3em', color: i === 1 ? LUJO.oro : LUJO.marfil}}>{n}</div>
          <div style={{fontFamily: LUJO.serif, fontStyle: 'italic', fontWeight: 700, fontSize: 40, color: LUJO.piedra, marginTop: 10}}>{r} por mes{i === 1 ? ' · recomendado' : ''}</div>
        </div>
        <div style={{fontFamily: LUJO.serif, fontWeight: 700, fontSize: 76, color: i === 1 ? LUJO.oro : LUJO.marfil}}>{p}</div>
      </div>
    ))}
  </>
);

const FILAS: {titulo: string; idea: string; cuadros: {el: React.ReactNode; nota: string}[]}[] = [
  {
    titulo: 'A · Tu marca merece más', idea: 'Elegancia + incomodidad: lo que tu marca vale vs. lo que muestra.',
    cuadros: [
      {el: <Titulo top={640} l={[[{t: 'Tu marca'}], [{t: 'merece'}], [{t: 'más que', oro: false}, {t: 'una foto.', oro: true}]]} />, nota: '0–3 s · aparece completo, lento'},
      {el: <><div style={{position: 'absolute', left: 300, right: 300, top: 620, height: 600, background: '#1F1C17', border: '1px solid #3a352c'}} /><Titulo top={1250} tam={70} l={[[{t: 'Una foto'}, {t: 'más', oro: true}, {t: 'del montón.'}]]} /></>, nota: '3–8 s · foto quieta, se desvanece'},
      {el: <><Titulo top={420} tam={80} l={[[{t: 'Así se'}, {t: 'percibe', oro: true}]]} /><Tel a="NUEVA" b="Colección" /></>, nota: '8–18 s · anuncio de ejemplo, cortes suaves'},
      {el: <Cierre palabra="MARCA" />, nota: '18–25 s · cierre de marca'},
    ],
  },
  {
    titulo: 'B · Mismo material', idea: 'Antes/después sobrio: gris vs. edición cuidada.',
    cuadros: [
      {el: <Titulo top={640} l={[[{t: 'Mismo material.'}], [{t: 'Otra', oro: false}, {t: 'percepción.', oro: true}]]} />, nota: '0–3 s · gancho'},
      {el: <><div style={{position: 'absolute', left: 90, width: 430, top: 560, height: 820, background: '#2A2722', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', paddingBottom: 30, fontFamily: LUJO.sans, letterSpacing: '0.3em', fontSize: 34, color: LUJO.piedra}}>ANTES</div><div style={{position: 'absolute', right: 90, width: 430, top: 560, height: 820, background: '#1A160F', border: `2px solid ${LUJO.oro}`, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', paddingBottom: 30, fontFamily: LUJO.sans, letterSpacing: '0.3em', fontSize: 34, color: LUJO.oro}}>DESPUÉS</div></>, nota: '3–12 s · pantalla partida, línea dorada que barre'},
      {el: <Titulo top={620} tam={96} l={[[{t: 'Ritmo.'}], [{t: 'Narrativa.'}], [{t: 'Intención.', oro: true}]]} />, nota: '12–17 s · una palabra cada 2 s'},
      {el: <Planes />, nota: '17–23 s · planes'},
    ],
  },
  {
    titulo: 'C · El primer segundo', idea: 'Autoridad: el dato que todo dueño ignora.',
    cuadros: [
      {el: <Titulo top={640} l={[[{t: 'El primer'}], [{t: 'segundo', oro: true}], [{t: 'decide.'}]]} />, nota: '0–3 s · gancho'},
      {el: <><div style={{position: 'absolute', left: 140, right: 140, top: 820, height: 4, background: '#2A2722'}}><div style={{width: '22%', height: '100%', background: LUJO.oro}} /></div><Titulo top={900} tam={70} l={[[{t: 'Después,'}, {t: 'ya se fueron.', oro: true}]]} /></>, nota: '3–8 s · barra de progreso que se corta'},
      {el: <Titulo top={640} tam={96} l={[[{t: 'Diseño cada'}], [{t: 'segundo.', oro: true}]]} />, nota: '8–12 s · propuesta'},
      {el: <Cierre palabra="REEL" />, nota: 'cierre'},
    ],
  },
  {
    titulo: 'D · Las marcas que crecen', idea: 'Aspiracional: pertenecer al grupo que se muestra.',
    cuadros: [
      {el: <Titulo top={640} l={[[{t: 'Las marcas'}], [{t: 'que crecen'}], [{t: 'se muestran.', oro: true}]]} />, nota: '0–3 s · gancho'},
      {el: <><Titulo top={560} tam={80} l={[[{t: 'Ellas:', oro: true}, {t: 'reels.'}]]} /><Titulo top={900} tam={80} l={[[{t: 'Vos:'}, {t: 'fotos.'}]]} /></>, nota: '3–9 s · contraste en dos líneas'},
      {el: <><Titulo top={420} tam={80} l={[[{t: 'Tu'}, {t: 'momento', oro: true}]]} /><Tel a="EDICIÓN" b="Limitada" /></>, nota: '9–18 s · anuncio de ejemplo'},
      {el: <Planes />, nota: 'planes + cierre'},
    ],
  },
  {
    titulo: 'E · Signature', idea: 'Oferta directa, tono de concierge.',
    cuadros: [
      {el: <Titulo top={620} tam={110} l={[[{t: 'Vos atendés.'}], [{t: 'Yo cuido'}], [{t: 'tu imagen.', oro: true}]]} />, nota: '0–3 s · gancho'},
      {el: <Titulo top={640} tam={96} l={[[{t: 'Guion.'}, {t: 'Edición.'}], [{t: 'Portada.'}, {t: 'Estrategia.', oro: true}]]} chico="TODO INCLUIDO" />, nota: '3–8 s · qué incluye'},
      {el: <Planes />, nota: '8–16 s · los 3 planes'},
      {el: <Cierre palabra="SIGNATURE" />, nota: 'cierre'},
    ],
  },
];

export const BocetoPremium: React.FC = () => (
  <AbsoluteFill style={{background: '#0B0A08', padding: 40, color: LUJO.marfil}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 50, marginBottom: 30}}>
      <Monograma tam={110} />
      <div style={{flex: 1}}>
        <div style={{fontFamily: LUJO.serif, fontWeight: 700, fontSize: 40}}>Identidad <span style={{fontStyle: 'italic', color: LUJO.oro}}>premium</span> · igual en todos los reels</div>
        <div style={{display: 'flex', gap: 18, marginTop: 12}}>
          {[['#0F0E0C', 'Negro cálido'], ['#F2ECE2', 'Marfil'], ['#C9A96E', 'Champagne'], ['#8C857A', 'Piedra']].map(([c, n]) => (
            <div key={c} style={{display: 'flex', alignItems: 'center', gap: 8}}><div style={{width: 38, height: 38, borderRadius: '50%', background: c, border: '1px solid #4a443a'}} /><span style={{fontFamily: LUJO.sans, fontSize: 19, fontWeight: 500}}>{n}</span></div>
          ))}
        </div>
        <div style={{fontFamily: LUJO.sans, fontSize: 19, color: '#9a9488', marginTop: 10}}>Playfair Display (títulos, 1 palabra en itálica dorada) + Inter espaciada (detalles) · sin emojis · movimientos lentos · mucho aire · sello "VIRALIZA · REELS"</div>
      </div>
    </div>
    {FILAS.map((fila) => (
      <div key={fila.titulo} style={{display: 'flex', gap: 22, marginBottom: 26, alignItems: 'flex-start'}}>
        <div style={{width: 200}}>
          <div style={{fontFamily: LUJO.serif, fontWeight: 700, fontStyle: 'italic', fontSize: 30, color: LUJO.oro, lineHeight: 1.1}}>{fila.titulo}</div>
          <div style={{fontFamily: LUJO.sans, fontWeight: 500, fontSize: 19, color: '#bbb3a6', marginTop: 10}}>{fila.idea}</div>
        </div>
        {fila.cuadros.map((c, i) => <Cuadro key={i} nota={c.nota}>{c.el}</Cuadro>)}
      </div>
    ))}
  </AbsoluteFill>
);
