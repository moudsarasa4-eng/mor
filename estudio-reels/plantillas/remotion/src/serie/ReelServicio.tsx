import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {Celular} from '../componentes/Celular';
import {resorte, tween} from '../lib/anim';
import {LUJO, Monograma} from './BocetoPremium';

// Reels premium por servicio: Carta QR, Perfil, Historias. 24 s (720 cuadros), sin audio.
// Franja segura 288–1440. Estructura: gancho 0–3 · problema 3–8 · solución 8–15 · precio 15–19 · cierre 19–24.
export const SERV_DUR = 720;
const A = 288;

const Sello: React.FC = () => (
  <div style={{position: 'absolute', top: A + 16, left: 0, right: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 22, zIndex: 40}}>
    <div style={{width: 90, height: 2, background: LUJO.linea}} />
    <span style={{fontFamily: LUJO.sans, fontWeight: 700, fontSize: 28, letterSpacing: '0.38em', color: LUJO.oro}}>VIRALIZA · ESTUDIO</span>
    <div style={{width: 90, height: 2, background: LUJO.linea}} />
  </div>
);

/** Título serif que entra con fundido + leve subida (lento, elegante). */
const T: React.FC<{l: {t: string; oro?: boolean}[][]; en: number; hasta?: number; top: number; tam?: number}> = ({l, en, hasta, top, tam = 104}) => {
  const f = useCurrentFrame();
  if (f < en || (hasta !== undefined && f >= hasta)) return null;
  const a = en === 0 ? 1 : tween(f, [en, en + 10], [0, 1]);
  const s = hasta !== undefined ? tween(f, [hasta - 6, hasta], [1, 0]) : 1;
  return (
    <div style={{position: 'absolute', top, left: 80, right: 80, textAlign: 'center', fontFamily: LUJO.serif, fontWeight: 700, fontSize: tam, lineHeight: 1.08, color: LUJO.marfil, opacity: a * s, transform: `translateY(${(1 - a) * 30}px)`}}>
      {l.map((linea, i) => (
        <div key={i}>
          {linea.map((w, j) => (
            <span key={j} style={{color: w.oro ? LUJO.oro : undefined, fontStyle: w.oro ? 'italic' : 'normal', margin: '0 0.1em'}}>{w.t}</span>
          ))}
        </div>
      ))}
    </div>
  );
};
const Chico: React.FC<{t: string; top: number; en: number}> = ({t, top, en}) => {
  const f = useCurrentFrame();
  return <div style={{position: 'absolute', top, left: 0, right: 0, textAlign: 'center', fontFamily: LUJO.sans, fontWeight: 700, fontSize: 32, letterSpacing: '0.32em', color: LUJO.piedra, opacity: tween(f, [en, en + 10], [0, 1])}}>{t}</div>;
};

const Precio: React.FC<{p: string; det: string}> = ({p, det}) => (
  <>
    <T en={450} top={A + 200} tam={92} l={[[{t: 'Listo en'}, {t: '48 horas.', oro: true}]]} />
    <T en={470} top={A + 470} tam={150} l={[[{t: p, oro: false}]]} />
    <Chico en={490} top={A + 700} t={det} />
  </>
);

const Cierre: React.FC<{palabra: string}> = ({palabra}) => {
  const f = useCurrentFrame();
  if (f < 570) return null;
  const a = tween(f, [570, 584], [0, 1]) * tween(f, [708, 718], [1, 0]);
  return (
    <AbsoluteFill style={{opacity: a}}>
      <div style={{position: 'absolute', top: A + 160, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}><Monograma tam={120} /></div>
      <T en={0} top={A + 400} tam={96} l={[[{t: 'Escribime'}], [{t: `"${palabra}"`, oro: true}]]} />
      <div style={{position: 'absolute', top: A + 700, left: 190, right: 190, padding: '24px 0', border: `2px solid ${LUJO.oro}`, textAlign: 'center', fontFamily: LUJO.sans, fontWeight: 700, fontSize: 34, letterSpacing: '0.3em', color: LUJO.oro}}>RESPUESTA EN EL DÍA</div>
      <div style={{position: 'absolute', top: A + 880, left: 0, right: 0, textAlign: 'center', fontFamily: LUJO.sans, fontWeight: 500, fontSize: 36, color: LUJO.piedra}}>@viraliza.tu.perfil.arg</div>
    </AbsoluteFill>
  );
};

const Base: React.FC<{children: React.ReactNode; gancho: React.ReactNode}> = ({children, gancho}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: LUJO.fondo, overflow: 'hidden'}}>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, rgba(201,169,110,0.10) 0%, rgba(0,0,0,0) 60%)'}} />
      {children}
      <Sello />
      {/* empalme: los últimos cuadros vuelven al gancho */}
      {f >= SERV_DUR - 6 ? <AbsoluteFill style={{background: LUJO.fondo, opacity: tween(f, [SERV_DUR - 6, SERV_DUR - 2], [0, 1])}}>{gancho}<Sello /></AbsoluteFill> : null}
    </AbsoluteFill>
  );
};

// ======================================================================= CARTA QR
const CartaPapel: React.FC<{f: number}> = ({f}) => {
  const items = [['Milanesa napolitana', '8.900', '10.400'], ['Ravioles', '7.200', '8.600'], ['Flan casero', '3.100', '3.800'], ['Limonada', '2.500', '3.200']];
  return (
    <div style={{position: 'absolute', left: 170, right: 170, top: A + 360, height: 760, background: '#EDE3CF', transform: 'rotate(-3deg)', padding: '60px 56px', boxShadow: '0 30px 60px rgba(0,0,0,0.5)', fontFamily: LUJO.serif, color: '#3a2d1c'}}>
      <div style={{fontSize: 56, fontWeight: 700, textAlign: 'center', marginBottom: 40, fontStyle: 'italic'}}>Carta</div>
      {items.map(([n, p, q], i) => {
        const t = tween(f, [100 + i * 22, 112 + i * 22], [0, 1]);
        return (
          <div key={n} style={{display: 'flex', justifyContent: 'space-between', fontSize: 40, marginBottom: 46, alignItems: 'baseline'}}>
            <span>{n}</span>
            <span style={{position: 'relative'}}>
              ${p}
              <span style={{position: 'absolute', left: -6, top: '52%', height: 5, width: `${110 * t}%`, background: '#1d3fa8', transform: 'rotate(-6deg)'}} />
              {t > 0.9 ? <span style={{position: 'absolute', left: -40, top: -46, fontFamily: 'cursive', color: '#1d3fa8', fontSize: 38, transform: 'rotate(-8deg)'}}>{q}</span> : null}
            </span>
          </div>
        );
      })}
    </div>
  );
};
const CartaDigital: React.FC<{f: number}> = ({f}) => {
  const cambio = f >= 360;
  const items = [['Milanesa napolitana', cambio ? '10.400' : '8.900'], ['Ravioles de la casa', '8.600'], ['Flan casero', '3.800'], ['Limonada', '3.200']];
  return (
    <div style={{position: 'absolute', left: 300, top: A + 300}}>
      <Celular ancho={480} ejemplo={false}>
        <AbsoluteFill style={{background: '#16130F', padding: '200px 70px', fontFamily: LUJO.sans, color: LUJO.marfil}}>
          <div style={{fontFamily: LUJO.serif, fontStyle: 'italic', fontSize: 110, color: LUJO.oro, textAlign: 'center'}}>Carta</div>
          <div style={{textAlign: 'center', letterSpacing: '0.3em', fontSize: 34, color: LUJO.piedra, marginBottom: 80}}>TU RESTÓ · EJEMPLO</div>
          {items.map(([n, p], i) => (
            <div key={n} style={{display: 'flex', alignItems: 'center', gap: 34, padding: '34px 0', borderBottom: `2px solid ${LUJO.linea}`}}>
              <div style={{width: 150, height: 150, borderRadius: 20, background: ['#5a3a22', '#6b4a2a', '#8a6a3a', '#a08a4a'][i]}} />
              <div style={{flex: 1, fontSize: 52, fontWeight: 700}}>{n}</div>
              <div style={{fontSize: 56, fontWeight: 700, color: i === 0 && f >= 360 && f < 380 ? LUJO.oro : LUJO.marfil, transform: `scale(${i === 0 && f >= 360 ? 1 + 0.3 * Math.exp(-(f - 360) / 5) : 1})`}}>${p}</div>
            </div>
          ))}
        </AbsoluteFill>
      </Celular>
    </div>
  );
};
const QR: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => (
  <svg width={tam} height={tam} viewBox="0 0 21 21" style={{position: 'absolute', left: x, top: y, background: LUJO.marfil, padding: tam * 0.05}}>
    {Array.from({length: 21 * 21}).map((_, i) => {
      const cx = i % 21, cy = Math.floor(i / 21);
      const finder = (a: number, b: number) => cx >= a && cx < a + 7 && cy >= b && cy < b + 7 && (cx === a || cx === a + 6 || cy === b || cy === b + 6 || (cx >= a + 2 && cx <= a + 4 && cy >= b + 2 && cy <= b + 4));
      const zona = (cx < 8 && cy < 8) || (cx > 12 && cy < 8) || (cx < 8 && cy > 12);
      const on = zona ? finder(0, 0) || finder(14, 0) || finder(0, 14) : (cx * 7 + cy * 13 + cx * cy) % 3 === 0;
      return on ? <rect key={i} x={cx} y={cy} width={1} height={1} fill={LUJO.fondo} /> : null;
    })}
  </svg>
);
const GanchoCarta = <T en={0} top={A + 330} tam={108} l={[[{t: '¿Todavía'}], [{t: 'tachás precios'}], [{t: 'con birome?', oro: true}]]} />;
export const ReelCarta: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Base gancho={GanchoCarta}>
      {f < 90 ? GanchoCarta : null}
      {f >= 90 && f < 240 ? (
        <>
          <T en={90} top={A + 130} tam={72} l={[[{t: 'Cada aumento,'}, {t: 'otra carta.', oro: true}]]} />
          <CartaPapel f={f} />
        </>
      ) : null}
      {f >= 240 && f < 450 ? (
        <>
          <T en={240} hasta={360} top={A + 130} tam={72} l={[[{t: 'Tu carta en el'}, {t: 'celular.', oro: true}]]} />
          <T en={360} top={A + 130} tam={72} l={[[{t: 'Cambiás un precio'}, {t: 'en un minuto.', oro: true}]]} />
          <CartaDigital f={f} />
          {f >= 300 ? <div style={{opacity: tween(f, [300, 312], [0, 1])}}><QR x={90} y={A + 860} tam={200} /></div> : null}
        </>
      ) : null}
      {f >= 450 && f < 570 ? <Precio p="$35.000" det="CON FOTOS · TU MARCA · SIN APP" /> : null}
      <Cierre palabra="CARTA" />
    </Base>
  );
};

// ======================================================================= PERFIL
const Busqueda: React.FC<{f: number}> = ({f}) => {
  const q = 'uñas palermo';
  const n = Math.min(q.length, Math.max(0, Math.floor((f - 100) / 3)));
  return (
    <div style={{position: 'absolute', left: 120, right: 120, top: A + 360}}>
      <div style={{height: 120, borderRadius: 60, background: '#1E1B16', border: `2px solid ${LUJO.linea}`, display: 'flex', alignItems: 'center', padding: '0 44px', fontFamily: LUJO.sans, fontSize: 50, color: LUJO.marfil, gap: 20}}>
        <span style={{color: LUJO.piedra}}>Buscar</span><span>{q.slice(0, n)}</span><span style={{width: 4, height: 56, background: LUJO.oro, opacity: f % 20 < 10 ? 1 : 0}} />
      </div>
      {[0, 1, 2, 3].map((i) => (
        <div key={i} style={{display: 'flex', alignItems: 'center', gap: 26, marginTop: 40, opacity: tween(f, [150 + i * 8, 160 + i * 8], [0, 1])}}>
          <div style={{width: 100, height: 100, borderRadius: '50%', background: '#2A2620'}} />
          <div><div style={{width: 340, height: 30, borderRadius: 15, background: '#2A2620'}} /><div style={{width: 220, height: 24, borderRadius: 12, background: '#221F1A', marginTop: 14}} /></div>
        </div>
      ))}
    </div>
  );
};
const PerfilMock: React.FC<{f: number; bueno: boolean}> = ({bueno}) => (
  <div style={{position: 'absolute', left: 300, top: A + 290}}>
    <Celular ancho={480} ejemplo={false}>
      <AbsoluteFill style={{background: '#16130F', padding: '190px 60px', fontFamily: LUJO.sans, color: LUJO.marfil}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 40}}>
          <div style={{width: 200, height: 200, borderRadius: '50%', border: `6px solid ${bueno ? LUJO.oro : '#3a352c'}`, background: '#2A2620'}} />
          <div style={{fontSize: 46, fontWeight: 700}}>{bueno ? 'Estudio Lila | Uñas Palermo' : 'lila_23'}</div>
        </div>
        <div style={{marginTop: 50, fontSize: 44, lineHeight: 1.45, color: bueno ? LUJO.marfil : LUJO.piedra}}>
          {bueno ? (
            <>
              Uñas semipermanentes y kapping<br />📍 Palermo · Lun a Sáb<br /><span style={{color: LUJO.oro}}>Turnos por WhatsApp 👇</span>
            </>
          ) : (
            <>✨ amor por lo que hago ✨<br />🌸💅🌸</>
          )}
        </div>
        <div style={{display: 'flex', gap: 30, marginTop: 70}}>
          {(bueno ? ['Turnos', 'Precios', 'Trabajos', 'Ubicación'] : ['', '', '', '']).map((h, i) => (
            <div key={i} style={{textAlign: 'center'}}>
              <div style={{width: 150, height: 150, borderRadius: '50%', border: `4px solid ${bueno ? LUJO.oro : '#3a352c'}`, background: bueno ? '#1F1B14' : '#2A2620'}} />
              <div style={{fontSize: 30, marginTop: 12, color: LUJO.piedra}}>{h}</div>
            </div>
          ))}
        </div>
      </AbsoluteFill>
    </Celular>
  </div>
);
const GanchoPerfil = <T en={0} top={A + 330} tam={104} l={[[{t: 'Buscaron tu rubro'}], [{t: 'en tu barrio.'}], [{t: 'No apareciste.', oro: true}]]} />;
export const ReelPerfil: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Base gancho={GanchoPerfil}>
      {f < 90 ? GanchoPerfil : null}
      {f >= 90 && f < 240 ? (
        <>
          <T en={90} top={A + 130} tam={72} l={[[{t: 'Instagram es un'}, {t: 'buscador.', oro: true}]]} />
          <Busqueda f={f} />
        </>
      ) : null}
      {f >= 240 && f < 345 ? (
        <>
          <T en={240} top={A + 130} tam={72} l={[[{t: 'Así te'}, {t: 'ven hoy.', oro: false}]]} />
          <PerfilMock f={f} bueno={false} />
        </>
      ) : null}
      {f >= 345 && f < 450 ? (
        <>
          <T en={345} top={A + 130} tam={72} l={[[{t: 'Así te'}, {t: 'encuentran.', oro: true}]]} />
          <PerfilMock f={f} bueno />
        </>
      ) : null}
      {f >= 450 && f < 570 ? <Precio p="$15.000" det="NOMBRE · BIO · DESTACADAS · LINK" /> : null}
      <Cierre palabra="PERFIL" />
    </Base>
  );
};

// ======================================================================= HISTORIAS
const Historia: React.FC<{i: number; buena: boolean; x: number; y: number; esc: number}> = ({i, buena, x, y, esc}) => {
  const malos = [['#FF4FA3', 'Comic Sans MS, cursive', 'PROMO!!!'], ['#2EC4FF', 'Impact, sans-serif', 'nuevo'], ['#7CFF4F', 'Courier New, monospace', 'Abierto'], ['#FFC93C', 'Georgia, serif', 'gracias!!'], ['#B04FFF', 'Arial, sans-serif', '¿?']];
  const buenos = ['PROMO', 'NOVEDAD', 'TESTIMONIO', 'HORARIOS', 'PREGUNTA'];
  const [c, fam, txt] = malos[i];
  return (
    <div style={{position: 'absolute', left: x, top: y, width: 300, height: 533, borderRadius: 26, overflow: 'hidden', transform: `scale(${esc})`, boxShadow: '0 20px 40px rgba(0,0,0,0.5)', background: buena ? '#16130F' : c, border: buena ? `3px solid ${LUJO.oro}` : 'none'}}>
      {buena ? (
        <>
          <div style={{position: 'absolute', top: 40, left: 0, right: 0, textAlign: 'center', fontFamily: LUJO.sans, fontWeight: 700, fontSize: 20, letterSpacing: '0.35em', color: LUJO.oro}}>TU MARCA</div>
          <div style={{position: 'absolute', top: 120, left: 30, right: 30, height: 230, background: '#2A2620'}} />
          <div style={{position: 'absolute', top: 380, left: 0, right: 0, textAlign: 'center', fontFamily: LUJO.serif, fontStyle: 'italic', fontWeight: 700, fontSize: 40, color: LUJO.marfil}}>{buenos[i]}</div>
          <div style={{position: 'absolute', bottom: 40, left: 90, right: 90, height: 2, background: LUJO.oro}} />
        </>
      ) : (
        <div style={{position: 'absolute', top: 180 + (i % 2) * 90, left: 20, right: 20, textAlign: 'center', fontFamily: fam, fontSize: 64, color: '#fff', transform: `rotate(${(i - 2) * 7}deg)`, textShadow: '3px 3px 0 #000'}}>{txt}</div>
      )}
    </div>
  );
};
const GanchoHist = <T en={0} top={A + 330} tam={100} l={[[{t: 'Tus historias'}], [{t: 'parecen de'}], [{t: 'cinco marcas.', oro: true}]]} />;
export const ReelHistorias: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pos = [[70, A + 230], [390, A + 230], [710, A + 230], [230, A + 650], [550, A + 650]];
  return (
    <Base gancho={GanchoHist}>
      {f < 90 ? GanchoHist : null}
      {f >= 90 && f < 450 ? (
        <>
          <T en={90} hasta={240} top={A + 110} tam={70} l={[[{t: 'Una tipografía'}, {t: 'por día.', oro: true}]]} />
          <T en={240} hasta={345} top={A + 110} tam={70} l={[[{t: 'Cinco plantillas.'}, {t: 'Tu marca.', oro: true}]]} />
          <T en={345} top={A + 110} tam={70} l={[[{t: 'Cambiás la foto'}, {t: 'y subís.', oro: true}]]} />
          {pos.map(([x, y], i) => {
            const buena = f >= 240 + i * 8;
            const s = resorte(f, fps, buena ? 240 + i * 8 : 92 + i * 8, 'pop');
            return <Historia key={i} i={i} buena={buena} x={x} y={y} esc={0.74 * (0.85 + 0.15 * s)} />;
          })}
        </>
      ) : null}
      {f >= 450 && f < 570 ? <Precio p="$20.000" det="5 PLANTILLAS · LISTAS PARA USAR" /> : null}
      <Cierre palabra="HISTORIAS" />
    </Base>
  );
};
