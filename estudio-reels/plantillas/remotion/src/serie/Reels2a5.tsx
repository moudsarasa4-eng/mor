import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {Celular} from '../componentes/Celular';
import {resorte, tween} from '../lib/anim';
import {FUENTE} from '../lib/fuentes';
import {ARRIBA, Cierre, Contador, Corte, Emoji, Feed, Frase, Marca, Paleta, Partida, Planes} from './Serie';

// Misma estructura que el Reel 1: gancho → problema → SOY EDITOR DE REELS → anuncio de ejemplo en el celular
// → VOS TRABAJÁS, YO EDITO → cierre. Duración 27 s (810 cuadros).
export const R_DUR = 810;

const Tel: React.FC<{children: React.ReactNode; y: number; cuenta?: string; color?: string; desc?: string; ui?: boolean}> = ({children, y, cuenta = 'tunegocio.ejemplo', color = '#555', desc = '', ui = true}) => (
  <div style={{position: 'absolute', left: 540 - 240, top: y, filter: 'drop-shadow(0 30px 40px rgba(0,0,0,0.3))'}}>
    <Celular ancho={480} ejemplo ui={ui ? {cuenta, inicial: cuenta.slice(0, 2).toUpperCase(), colorAvatar: color, descripcion: desc} : null}>
      {children}
    </Celular>
  </div>
);

const Linea: React.FC<{p: Paleta; desde: number}> = ({p, desde}) => {
  const f = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: 90, right: 90, top: ARRIBA + 760, height: 230, borderRadius: 30, background: 'rgba(127,127,127,0.12)', padding: 24}}>
      {[0, 1, 2].map((q) => (
        <div key={q} style={{display: 'flex', gap: 8, marginBottom: 14, height: 46}}>
          {Array.from({length: 8}).map((_, k) => (
            <div key={k} style={{flex: 1 + ((k * 5 + q * 3) % 3), borderRadius: 10, background: q === 1 ? p.texto : p.acento, opacity: k <= (f - desde) / 6 ? 0.9 : 0.15}} />
          ))}
        </div>
      ))}
      <div style={{position: 'absolute', top: 10, bottom: 10, left: 24 + ((f - desde) * 10) % 860, width: 6, borderRadius: 3, background: p.texto}} />
    </div>
  );
};

/** Bloques comunes 7–10 s, 18–22 s, cierre y empalme. */
const Comunes: React.FC<{p: Paleta; palabra: string; gancho: React.ReactNode}> = ({p, palabra, gancho}) => {
  const f = useCurrentFrame();
  return (
    <>
      {f >= 240 && f < 330 ? (
        <>
          <Frase p={p} en={240} tam={140} y={ARRIBA + 330} lineas={[['SOY'], [{t: 'EDITOR', acento: true}], ['DE', 'REELS']]} />
          <Linea p={p} desde={240} />
        </>
      ) : null}
      {f >= 570 && f < 690 ? <Planes p={p} en={570} /> : null}
      <Cierre p={p} palabra={palabra} en={690} dur={120} />
      <Corte en={[90, 240, 330, 570, 690]} color={p.acento} />
      <Marca p={p} />
      {f >= R_DUR - 8 ? <AbsoluteFill style={{background: p.fondo, opacity: tween(f, [R_DUR - 8, R_DUR - 4], [0, 1])}}>{gancho}</AbsoluteFill> : null}
    </>
  );
};

const subt = (t: number, txt: string, color: string, acento: string) => (
  <div style={{position: 'absolute', top: 1560, left: 0, right: 0, textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 800, fontSize: 56, color}}>
    {txt.split(' ').map((w, i) => (
      <span key={i} style={{opacity: t % 80 >= i * 8 ? 1 : 0, background: i === 1 ? acento : 'transparent', color: i === 1 ? '#fff' : undefined, padding: '0 10px', borderRadius: 10, marginRight: 8}}>{w}</span>
    ))}
  </div>
);
const grande = (lines: {t: string; c?: string}[], tam = 130, top = 420) => (
  <div style={{position: 'absolute', top, left: 40, right: 40, textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: tam, lineHeight: 1.02, textTransform: 'uppercase'}}>
    {lines.map((l, i) => (
      <div key={i} style={{color: l.c}}>{l.t}</div>
    ))}
  </div>
);

// ======================================================================== REEL 2 — GIMNASIOS
const P2: Paleta = {fondo: '#0A0A0A', texto: '#FFFFFF', acento: '#B6FF2E'};
const Anuncio2: React.FC<{t: number}> = ({t}) => {
  const {fps} = useVideoConfig();
  const fase = t < 80 ? 0 : t < 160 ? 1 : 2;
  return (
    <AbsoluteFill style={{background: '#0A0A0A'}}>
      {fase === 0 ? (
        <>
          {grande([{t: 'CLASE DE', c: '#fff'}, {t: '7 AM', c: '#B6FF2E'}], 150)}
          {[0, 1, 2, 3, 4].map((i) => {
            const h = 200 + 260 * Math.abs(Math.sin((t + i * 7) / 6));
            return <div key={i} style={{position: 'absolute', left: 200 + i * 150, bottom: 520, width: 90, height: h, borderRadius: 20, background: '#B6FF2E', opacity: 0.85}} />;
          })}
        </>
      ) : fase === 1 ? (
        <>
          {grande([{t: 'PRIMERA', c: '#fff'}, {t: 'SEMANA', c: '#fff'}, {t: 'GRATIS', c: '#B6FF2E'}], 140)}
          <div style={{position: 'absolute', top: 1050, left: 0, right: 0, textAlign: 'center', fontSize: 260, transform: `scale(${0.6 + 0.4 * resorte(t, fps, 90, 'rebote')})`}}>💪</div>
        </>
      ) : (
        <>
          {grande([{t: 'RESERVÁ', c: '#fff'}, {t: 'TU LUGAR', c: '#B6FF2E'}], 140)}
          <div style={{position: 'absolute', top: 1000, left: 0, right: 0, textAlign: 'center'}}>
            <span style={{display: 'inline-block', background: '#B6FF2E', color: '#0A0A0A', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 70, padding: '30px 60px', borderRadius: 60, transform: `scale(${1 + 0.06 * Math.sin(t / 3)})`}}>ESCRIBINOS</span>
          </div>
        </>
      )}
      {subt(t, fase === 0 ? 'arrancá el día' : fase === 1 ? 'sin compromiso' : 'cupos por clase', '#fff', '#5A8A00')}
    </AbsoluteFill>
  );
};
const Gancho2: React.FC<{f: number}> = ({f}) => {
  const q = 'DÓNDE ENTRENAR';
  const n = Math.min(q.length, Math.max(0, Math.floor((f - 8) / 2)));
  return (
    <>
      <Frase p={P2} en={0} tam={100} y={ARRIBA + 270} lineas={[[{t: 'ENERO:', acento: true}, 'TODOS'], ['BUSCAN', 'DÓNDE', 'ENTRENAR.']]} />
      <div style={{position: 'absolute', left: 120, right: 120, top: ARRIBA + 520, height: 120, borderRadius: 60, background: '#1C1C1C', border: '3px solid #333', display: 'flex', alignItems: 'center', padding: '0 40px', gap: 24, fontFamily: FUENTE.inter, fontWeight: 700, fontSize: 52, color: '#fff'}}>
        <span>🔍</span>
        <span>{q.slice(0, n).toLowerCase()}</span>
        <span style={{width: 4, height: 60, background: '#B6FF2E', opacity: f % 20 < 10 ? 1 : 0}} />
      </div>
      {f >= 50 ? <Frase p={P2} en={50} tam={110} y={ARRIBA + 850} lineas={[['¿TE', {t: 'ENCUENTRAN?', acento: true, golpe: true}]]} /> : null}
    </>
  );
};
export const Reel2Gimnasios: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: P2.fondo, overflow: 'hidden'}}>
      {f < 90 ? <Gancho2 f={f} /> : null}
      {f >= 90 && f < 240 ? (
        <>
          <Frase p={P2} en={90} tam={92} y={ARRIBA + 170} lineas={[['ÚLTIMO', 'POSTEO:'], [{t: 'HACE', acento: true}, {t: 'MESES.', acento: true}]]} />
          <div style={{position: 'absolute', left: 220, right: 220, top: ARRIBA + 330, height: 640, borderRadius: 40, background: '#2A2A2A'}}>
            <Emoji e="🕸️" x={320} y={240} tam={260} esc={0.6 + 0.4 * resorte(f, fps, 110, 'pop')} />
            {f >= 160 ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 420, color: '#FF4D5E', transform: `scale(${1 + 0.5 * Math.exp(-(f - 160) / 4)})`}}>✗</div> : null}
          </div>
        </>
      ) : null}
      {f >= 330 && f < 570 ? (
        <>
          <Frase p={P2} en={330} hasta={450} tam={70} y={ARRIBA + 175} lineas={[['ESTO', 'ES', 'LO', 'QUE'], [{t: 'VENDÉS.', acento: true}]]} />
          <Frase p={P2} en={450} tam={70} y={ARRIBA + 175} lineas={[[{t: 'MOSTRALO.', acento: true}]]} />
          <div style={{transform: `translateY(${(1 - resorte(f, fps, 330, 'pop')) * 900}px)`}}>
            <Tel y={ARRIBA + 280} cuenta="tugym.ejemplo" color="#5A8A00" desc="Clase de las 7 💪">
              <Anuncio2 t={f - 330} />
            </Tel>
          </div>
        </>
      ) : null}
      {/* 9–? bloque extra entre 240 y 330 lo ocupa "SOY EDITOR"; ENERGÍA/CLASE/RESULTADO va dentro del anuncio */}
      <Comunes p={P2} palabra="ENERO" gancho={<Gancho2 f={0} />} />
    </AbsoluteFill>
  );
};

// ======================================================================== REEL 3 — ODONTOLOGÍA
const P3: Paleta = {fondo: '#FFFFFF', texto: '#0B2545', acento: '#3BB3F0'};
const Anuncio3: React.FC<{t: number}> = ({t}) => {
  const fase = t < 80 ? 0 : t < 160 ? 1 : 2;
  return (
    <AbsoluteFill style={{background: '#EAF6FD'}}>
      {fase === 0 ? (
        <>
          {grande([{t: '¿DUELE', c: '#0B2545'}, {t: 'UN ARREGLO?', c: '#3BB3F0'}], 120)}
          <div style={{position: 'absolute', top: 980, left: 0, right: 0, textAlign: 'center', fontSize: 280}}>🦷</div>
        </>
      ) : fase === 1 ? (
        <>
          {grande([{t: 'TE LO', c: '#0B2545'}, {t: 'EXPLICO', c: '#3BB3F0'}, {t: 'EN 30 SEG', c: '#0B2545'}], 120)}
          <div style={{position: 'absolute', top: 1050, left: 160, right: 160, height: 26, borderRadius: 13, background: '#CBE6F6'}}>
            <div style={{width: `${Math.min(100, ((t - 80) / 70) * 100)}%`, height: '100%', borderRadius: 13, background: '#3BB3F0'}} />
          </div>
        </>
      ) : (
        <>
          {grande([{t: 'PEDÍ', c: '#0B2545'}, {t: 'TU TURNO', c: '#3BB3F0'}], 140)}
          <div style={{position: 'absolute', top: 1000, left: 0, right: 0, textAlign: 'center'}}>
            <span style={{display: 'inline-block', background: '#3BB3F0', color: '#fff', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 70, padding: '30px 60px', borderRadius: 60}}>POR MENSAJE</span>
          </div>
        </>
      )}
      {subt(t, fase === 0 ? 'la pregunta de siempre' : fase === 1 ? 'sin vueltas' : 'link en el perfil', '#0B2545', '#3BB3F0')}
    </AbsoluteFill>
  );
};
const Gancho3: React.FC<{f: number}> = ({f}) => {
  const {fps} = useVideoConfig();
  return (
    <>
      <Frase p={P3} en={0} tam={112} y={ARRIBA + 230} lineas={[['NADIE', 'MIRA'], ['TU', {t: 'CARTEL.', tachar: 20}]]} />
      {f >= 40 ? <Frase p={P3} en={40} tam={112} y={ARRIBA + 560} lineas={[['MIRAN', {t: 'ESTO', acento: true}]]} /> : null}
      <Emoji e="📱" x={540} y={ARRIBA + 900} tam={300} esc={f >= 40 ? 0.4 + 0.6 * resorte(f, fps, 40, 'rebote') : 0} />
    </>
  );
};
export const Reel3Odontologia: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dudas = ['MIEDO', 'PRECIO', 'DESCONFIANZA'];
  return (
    <AbsoluteFill style={{background: P3.fondo, overflow: 'hidden'}}>
      {f < 90 ? <Gancho3 f={f} /> : null}
      {f >= 90 && f < 240 ? (
        <div style={{position: 'absolute', top: ARRIBA + 200, left: 0, right: 0}}>
          {dudas.map((d, i) => {
            const s = resorte(f, fps, 90 + i * 25, 'pop');
            const tach = tween(f, [180 + i * 15, 188 + i * 15], [0, 1]);
            return (
              <div key={d} style={{textAlign: 'center', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 104, color: P3.texto, marginBottom: 70, opacity: Math.min(1, s * 2), transform: `scale(${0.6 + 0.4 * s})`, position: 'relative'}}>
                <span style={{position: 'relative'}}>
                  {d}<span style={{color: P3.acento}}>?</span>
                  {tach > 0 ? <span style={{position: 'absolute', left: '-4%', top: '50%', height: 16, width: `${108 * tach}%`, background: P3.acento, borderRadius: 8}} /> : null}
                </span>
              </div>
            );
          })}
        </div>
      ) : null}
      {f >= 330 && f < 570 ? (
        <>
          <Frase p={P3} en={330} hasta={450} tam={70} y={ARRIBA + 175} lineas={[['TU', 'CARA.', 'TU', 'FORMA'], ['DE', {t: 'EXPLICAR.', acento: true}]]} />
          {f >= 450 ? (
            <>
              <Frase p={P3} en={450} tam={70} y={ARRIBA + 175} lineas={[['OTRO', 'CONSULTORIO'], ['YA', 'LO', {t: 'HACE.', acento: true}]]} />
            </>
          ) : null}
          <div style={{transform: `translateY(${(1 - resorte(f, fps, 330, 'pop')) * 900}px)`}}>
            <Tel y={ARRIBA + 280} cuenta="tuconsultorio.ejemplo" color="#3BB3F0" desc="¿Duele un arreglo? 🦷">
              <Anuncio3 t={f - 330} />
            </Tel>
          </div>
        </>
      ) : null}
      <Comunes p={P3} palabra="TURNO" gancho={<Gancho3 f={0} />} />
    </AbsoluteFill>
  );
};

// ======================================================================== REEL 4 — GASTRONOMÍA
const P4: Paleta = {fondo: '#5A0F1F', texto: '#FFF4E0', acento: '#FFD23F'};
const Anuncio4: React.FC<{t: number}> = ({t}) => {
  const {fps} = useVideoConfig();
  const fase = t < 80 ? 0 : t < 160 ? 1 : 2;
  const em = ['🧀', '🔥', '🍝'];
  return (
    <AbsoluteFill style={{background: '#2B0A10'}}>
      {fase === 0 ? (
        <>
          {grande([{t: 'SALE DE', c: '#FFF4E0'}, {t: 'LA COCINA', c: '#FFD23F'}], 130)}
          <div style={{position: 'absolute', top: 980, left: 0, right: 0, textAlign: 'center', fontSize: 300, transform: `scale(${0.7 + 0.3 * resorte(t, fps, 10, 'rebote')})`}}>🍝</div>
          {[0, 1, 2].map((i) => (
            <div key={i} style={{position: 'absolute', left: 420 + i * 90, top: 900 - ((t * 4 + i * 40) % 160), width: 16, height: 80, borderRadius: 8, background: '#fff', opacity: 0.35}} />
          ))}
        </>
      ) : fase === 1 ? (
        <>
          {grande([{t: 'GRATINADA', c: '#FFD23F'}, {t: 'AL MOMENTO', c: '#FFF4E0'}], 120)}
          {em.map((e, i) => (
            <div key={i} style={{position: 'absolute', top: 980 + i * 10, left: 140 + i * 280, fontSize: 200, transform: `scale(${0.5 + 0.5 * resorte(t, fps, 85 + i * 10, 'suave')})`}}>{e}</div>
          ))}
        </>
      ) : (
        <>
          {grande([{t: 'RESERVÁ', c: '#FFF4E0'}, {t: 'TU MESA', c: '#FFD23F'}], 140)}
          <div style={{position: 'absolute', top: 1000, left: 0, right: 0, textAlign: 'center'}}>
            <span style={{display: 'inline-block', background: '#FFD23F', color: '#2B0A10', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 70, padding: '30px 60px', borderRadius: 60}}>POR MENSAJE</span>
          </div>
        </>
      )}
      {subt(t, fase === 0 ? 'el plato estrella' : fase === 1 ? 'mirá ese queso' : 'link en el perfil', '#FFF4E0', '#B5122B')}
    </AbsoluteFill>
  );
};
const Gancho4: React.FC<{f: number}> = ({f}) => {
  const flash = f >= 30 && f < 60 ? Math.exp(-(f - 30) / 6) : 0;
  return (
    <>
      <Frase p={P4} en={0} tam={112} y={ARRIBA + 260} lineas={[['TU', 'PLATO'], [{t: 'ESTRELLA', acento: true}]]} />
      {f >= 30 ? <Frase p={P4} en={30} tam={112} y={ARRIBA + 680} lineas={[['❌', 'FOTO', 'CON'], ['FLASH']]} /> : null}
      {flash > 0 ? <AbsoluteFill style={{background: '#fff', opacity: flash}} /> : null}
    </>
  );
};
export const Reel4Gastronomia: React.FC = () => {
  const f = useCurrentFrame();
  const gris = f >= 120 && f < 160;
  return (
    <AbsoluteFill style={{background: gris ? '#D9D9D4' : P4.fondo, overflow: 'hidden'}}>
      {f < 90 ? <Gancho4 f={f} /> : null}
      {f >= 90 && f < 240 ? (
        <Frase p={gris ? {...P4, texto: '#555', acento: '#777'} : P4} en={90} tam={110} y={ARRIBA + 450} lineas={[['CON', 'FLASH,', 'TODO'], ['PARECE', 'COMIDA'], ['DE', {t: 'HOSPITAL.', acento: true}]]} />
      ) : null}
      {f >= 330 && f < 570 ? (
        <>
          <Frase p={P4} en={330} hasta={450} tam={70} y={ARRIBA + 175} lineas={[['EL', 'HAMBRE', 'ENTRA'], ['POR', 'LOS', {t: 'OJOS.', acento: true}]]} />
          {f >= 450 ? <Frase p={P4} en={450} tam={70} y={ARRIBA + 175} lineas={[['COCINA', 'PEOR.'], ['TIENE', {t: 'FILA.', acento: true}]]} /> : null}
          <div style={{transform: `translateY(${(1 - resorte(f, 30, 330, 'pop')) * 900}px)`}}>
            <Tel y={ARRIBA + 280} cuenta="turesto.ejemplo" color="#B5122B" desc="El plato estrella 🍝">
              <Anuncio4 t={f - 330} />
            </Tel>
          </div>
        </>
      ) : null}
      <Comunes p={P4} palabra="PLATO" gancho={<Gancho4 f={0} />} />
    </AbsoluteFill>
  );
};

// ======================================================================== REEL 5 — INMOBILIARIAS
const P5: Paleta = {fondo: '#0B1D3A', texto: '#FFFFFF', acento: '#FF8A1F'};
const Anuncio5: React.FC<{t: number}> = ({t}) => {
  const fase = t < 80 ? 0 : t < 160 ? 1 : 2;
  const p = tween(t, [84, 150], [0, 1]);
  return (
    <AbsoluteFill style={{background: '#0B1D3A'}}>
      {fase === 0 ? (
        <>
          {grande([{t: '3 AMBIENTES', c: '#fff'}, {t: 'CON LUZ', c: '#FF8A1F'}], 120)}
          <div style={{position: 'absolute', top: 960, left: 240, width: 600, height: 420, background: '#FF8A1F', opacity: 0.18 + 0.12 * Math.sin(t / 5), borderRadius: 20}} />
          <div style={{position: 'absolute', top: 1060, left: 0, right: 0, textAlign: 'center', fontSize: 220}}>☀️</div>
        </>
      ) : fase === 1 ? (
        <>
          {grande([{t: 'RECORRELO', c: '#fff'}, {t: 'EN 20 SEG', c: '#FF8A1F'}], 120)}
          <svg width={1080} height={700} style={{position: 'absolute', top: 900}} viewBox="0 0 1080 700">
            <rect x={140} y={40} width={800} height={600} fill="none" stroke="#fff" strokeWidth={10} />
            <line x1={540} y1={40} x2={540} y2={360} stroke="#fff" strokeWidth={10} />
            <line x1={140} y1={360} x2={780} y2={360} stroke="#fff" strokeWidth={10} />
            <path d="M 220 560 L 220 200 L 460 200 L 460 520 L 860 520 L 860 120" stroke="#FF8A1F" strokeWidth={14} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} />
          </svg>
        </>
      ) : (
        <>
          {grande([{t: 'COORDINÁ', c: '#fff'}, {t: 'TU VISITA', c: '#FF8A1F'}], 130)}
          <div style={{position: 'absolute', top: 1000, left: 0, right: 0, textAlign: 'center'}}>
            <span style={{display: 'inline-block', background: '#FF8A1F', color: '#0B1D3A', fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 70, padding: '30px 60px', borderRadius: 60}}>POR MENSAJE</span>
          </div>
        </>
      )}
      {subt(t, fase === 0 ? 'así se vive' : fase === 1 ? 'sin gran angular' : 'link en el perfil', '#fff', '#C25E00')}
    </AbsoluteFill>
  );
};
const Gancho5: React.FC<{f: number}> = ({f}) => (
  <>
    <AbsoluteFill style={{opacity: f < 50 ? 1 : 0}}>
      <Feed desde={0} vel={70} color="#3A4A66" />
    </AbsoluteFill>
    {f >= 50 ? <div style={{position: 'absolute', left: 290, right: 290, top: ARRIBA + 330, height: 560, borderRadius: 36, background: P5.acento, transform: `scale(${0.5 + 0.5 * Math.min(1, (f - 50) / 8)})`}} /> : null}
    <Frase p={P5} en={0} tam={100} y={ARRIBA + 180} lineas={[['12', 'FOTOS', '=', 'SCROLL.']]} />
    {f >= 50 ? <Frase p={P5} en={50} tam={104} y={ARRIBA + 1020} lineas={[['1', 'REEL', '=', {t: 'CONSULTAS.', acento: true}]]} /> : null}
  </>
);
export const Reel5Inmobiliarias: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const avisos = ['GRAN ANGULAR.', 'LIVING VACÍO.', '"EXCELENTE OPORTUNIDAD".'];
  return (
    <AbsoluteFill style={{background: P5.fondo, overflow: 'hidden'}}>
      {f < 90 ? <Gancho5 f={f} /> : null}
      {f >= 90 && f < 240 ? (
        <div style={{position: 'absolute', top: ARRIBA + 130, left: 110, right: 110}}>
          {avisos.map((a, i) => {
            const s = resorte(f, fps, 90 + i * 30, 'pop');
            return (
              <div key={i} style={{background: '#25385A', borderRadius: 30, padding: '40px 40px', marginBottom: 40, opacity: Math.min(1, s * 2), transform: `translateX(${(1 - s) * 400}px)`, display: 'flex', gap: 30, alignItems: 'center'}}>
                <div style={{width: 160, height: 120, borderRadius: 16, background: '#3A4A66'}} />
                <div style={{fontFamily: FUENTE.inter, fontWeight: 900, fontSize: 52, color: i === 2 ? P5.acento : '#fff', lineHeight: 1.05}}>{a}</div>
              </div>
            );
          })}
        </div>
      ) : null}
      {f >= 330 && f < 570 ? (
        <>
          <Frase p={P5} en={330} hasta={450} tam={70} y={ARRIBA + 175} lineas={[['LO', 'QUE', 'LA', 'FOTO'], ['ESCONDE,', 'EL', 'REEL'], ['LO', {t: 'MUESTRA.', acento: true}]]} />
          {f >= 450 ? <Frase p={P5} en={450} tam={70} y={ARRIBA + 175} lineas={[['TU', 'PROPIETARIO', 'TAMBIÉN'], ['MIRA', {t: 'INSTAGRAM', acento: true}, '👀']]} /> : null}
          <div style={{transform: `translateY(${(1 - resorte(f, fps, 330, 'pop')) * 900}px)`}}>
            <Tel y={ARRIBA + 280} cuenta="tuinmobiliaria.ejemplo" color="#FF8A1F" desc="3 ambientes con luz ☀️">
              <Anuncio5 t={f - 330} />
            </Tel>
          </div>
        </>
      ) : null}
      <Comunes p={P5} palabra="PROPIEDAD" gancho={<Gancho5 f={0} />} />
    </AbsoluteFill>
  );
};

export const _usar = [Partida, Contador];
