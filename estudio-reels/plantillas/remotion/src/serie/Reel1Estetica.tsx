import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {Celular} from '../componentes/Celular';
import {resorte, tween} from '../lib/anim';
import {FUENTE} from '../lib/fuentes';
import {ARRIBA, Cierre, Corte, Feed, Frase, Paleta} from './Serie';

export const R1_DUR = 780; // 26 s
const P: Paleta = {fondo: '#FCE4EC', texto: '#111111', acento: '#E6007E'};

// ---------------------------------------------------------------- pseudo-anuncio (HTML) dentro del celular
// Coordenadas 1080x1920; `t` = cuadro local del anuncio.
const AnuncioUnas: React.FC<{t: number}> = ({t}) => {
  const {fps} = useVideoConfig();
  const colores = ['#E6007E', '#FF6FAE', '#B5179E', '#FFB3D1', '#E6007E'];
  const fase = t < 75 ? 0 : t < 150 ? 1 : 2;
  return (
    <AbsoluteFill style={{background: fase === 1 ? '#111' : '#FFF0F6', fontFamily: FUENTE.inter, textTransform: 'uppercase'}}>
      {fase === 0 ? (
        <>
          <div style={{position: 'absolute', top: 360, left: 0, right: 0, textAlign: 'center', fontWeight: 900, fontSize: 130, color: '#111', lineHeight: 1}}>
            <div style={{transform: `scale(${0.6 + 0.4 * resorte(t, fps, 0, 'pop')})`}}>3 HORAS</div>
            <div style={{color: '#E6007E', transform: `scale(${0.6 + 0.4 * resorte(t, fps, 8, 'pop')})`}}>EN 15 SEG</div>
          </div>
          {/* mano estilizada: 5 uñas que se pintan una por una */}
          <div style={{position: 'absolute', top: 900, left: 190, width: 700, height: 600, display: 'flex', gap: 34, alignItems: 'flex-end', justifyContent: 'center'}}>
            {[300, 380, 420, 380, 260].map((h, i) => {
              const pin = tween(t, [16 + i * 10, 26 + i * 10], [0, 1]);
              return (
                <div key={i} style={{width: 110, height: h, borderRadius: '55px 55px 30px 30px', background: '#F2C7A5', position: 'relative'}}>
                  <div style={{position: 'absolute', left: 14, right: 14, top: 14, height: 120, borderRadius: '42px 42px 20px 20px', background: `linear-gradient(180deg, ${colores[i]} ${pin * 100}%, #F7DCC8 ${pin * 100}%)`, boxShadow: pin > 0.9 ? 'inset 8px 8px 0 rgba(255,255,255,0.35)' : 'none'}} />
                </div>
              );
            })}
          </div>
        </>
      ) : fase === 1 ? (
        <>
          <div style={{position: 'absolute', top: 380, left: 0, right: 0, textAlign: 'center', fontWeight: 900, fontSize: 96, color: '#fff', lineHeight: 1.05}}>
            <div>SEMIPERMANENTE</div>
            <div style={{color: '#FF6FAE'}}>QUE DURA</div>
            <div style={{fontSize: 210, color: '#E6007E', transform: `scale(${1 + 0.15 * Math.exp(-(t - 95) / 4)})`}}>{Math.min(21, Math.max(1, Math.round((t - 85) / 2)))} DÍAS</div>
          </div>
          {Array.from({length: 18}).map((_, i) => (
            <div key={i} style={{position: 'absolute', left: (i * 137) % 1000, top: 1250 + ((i * 53 + t * 4) % 500), width: 18, height: 18, borderRadius: '50%', background: '#FF6FAE', opacity: 0.7}} />
          ))}
        </>
      ) : (
        <div style={{position: 'absolute', top: 420, left: 60, right: 60, textAlign: 'center'}}>
          <div style={{fontWeight: 900, fontSize: 120, color: '#111', lineHeight: 1}}>TURNOS</div>
          <div style={{fontWeight: 900, fontSize: 120, color: '#E6007E', lineHeight: 1}}>POR MENSAJE</div>
          <div style={{marginTop: 80, display: 'inline-block', background: '#E6007E', color: '#fff', fontWeight: 900, fontSize: 70, padding: '30px 60px', borderRadius: 60, transform: `scale(${1 + 0.06 * Math.sin(t / 3)})`}}>RESERVÁ ACÁ</div>
        </div>
      )}
      {/* subtítulo palabra por palabra */}
      <div style={{position: 'absolute', top: 1560, left: 0, right: 0, textAlign: 'center', fontWeight: 800, fontSize: 56, color: fase === 1 ? '#fff' : '#111', textTransform: 'none'}}>
        {(fase === 0 ? 'mirá cómo queda' : fase === 1 ? 'sin descascarar' : 'link en el perfil').split(' ').map((w, i) => (
          <span key={i} style={{opacity: t % 75 >= i * 8 ? 1 : 0, background: i === 1 ? '#E6007E' : 'transparent', color: i === 1 ? '#fff' : undefined, padding: '0 10px', borderRadius: 10, marginRight: 8}}>{w}</span>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Tel: React.FC<{children: React.ReactNode; y: number; ancho?: number; rot?: number; ui?: boolean}> = ({children, y, ancho = 480, rot = 0, ui = true}) => (
  <div style={{position: 'absolute', left: 540 - ancho / 2, top: y, transform: `rotate(${rot}deg)`, filter: 'drop-shadow(0 30px 40px rgba(120,0,60,0.25))'}}>
    <Celular ancho={ancho} ejemplo ui={ui ? {cuenta: 'tuestudio.ejemplo', inicial: 'TE', colorAvatar: '#E6007E', descripcion: '3 horas de trabajo en 15 segundos 💅'} : null}>
      {children}
    </Celular>
  </div>
);

export const Reel1Estetica: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: P.fondo, overflow: 'hidden'}}>
      {/* 0–3: gancho */}
      {f < 90 ? <Frase p={P} en={0} tam={128} lineas={[['TU', 'TRABAJO'], ['ES', 'HERMOSO.']]} y={ARRIBA + 300} /> : null}
      {f >= 40 && f < 90 ? <Frase p={P} en={40} tam={112} lineas={[['TU', 'INSTAGRAM', {t: 'NO.', acento: true, golpe: true}]]} y={ARRIBA + 720} /> : null}

      {/* 3–7: así se ve hoy: foto quieta en un feed gris */}
      {f >= 90 && f < 210 ? (
        <>
          <Frase p={P} en={90} hasta={150} tam={100} y={ARRIBA + 90} lineas={[['FOTO.', 'FOTO.', 'FOTO.']]} paso={10} />
          <Frase p={P} en={150} tam={100} y={ARRIBA + 90} lineas={[['NADIE', {t: 'FRENA.', acento: true}]]} />
          <Tel y={ARRIBA + 210} ui={false}>
            <AbsoluteFill style={{background: '#EDEDF0'}}>
              <Feed desde={90} vel={40} />
            </AbsoluteFill>
          </Tel>
        </>
      ) : null}

      {/* 7–10: quién soy */}
      {f >= 210 && f < 300 ? (
        <>
          <Frase p={P} en={210} tam={140} y={ARRIBA + 330} lineas={[['SOY'], [{t: 'EDITOR', acento: true}], ['DE', 'REELS']]} />
          {/* línea de tiempo de edición */}
          <div style={{position: 'absolute', left: 90, right: 90, top: ARRIBA + 760, height: 230, borderRadius: 30, background: '#fff', padding: 24, boxShadow: '0 20px 40px rgba(120,0,60,0.12)'}}>
            {[0, 1, 2].map((p) => (
              <div key={p} style={{display: 'flex', gap: 8, marginBottom: 14, height: 46}}>
                {Array.from({length: 8}).map((_, k) => (
                  <div key={k} style={{flex: 1 + ((k * 5 + p * 3) % 3), borderRadius: 10, background: ['#E6007E', '#FF6FAE', '#111'][p], opacity: k <= (f - 210) / 6 ? 0.9 : 0.15}} />
                ))}
              </div>
            ))}
            <div style={{position: 'absolute', top: 10, bottom: 10, left: 24 + ((f - 210) * 10) % 860, width: 6, borderRadius: 3, background: '#111'}} />
          </div>
        </>
      ) : null}

      {/* 10–18: así se vería: pseudo-anuncio dentro del celular */}
      {f >= 300 && f < 540 ? (
        <>
          <Frase p={P} en={300} hasta={420} tam={88} y={ARRIBA + 120} lineas={[['ASÍ', 'SE', 'VERÍA'], ['TU', {t: 'REEL', acento: true}]]} />
          <Frase p={P} en={420} tam={88} y={ARRIBA + 120} lineas={[['MISMO', 'TRABAJO.'], ['OTRA', {t: 'CLIENTA.', acento: true}]]} />
          <div style={{transform: `translateY(${(1 - resorte(f, fps, 300, 'pop')) * 900}px)`}}>
            <Tel y={ARRIBA + 250}>
              <AnuncioUnas t={f - 300} />
            </Tel>
          </div>
        </>
      ) : null}

      {/* 18–22: la propuesta */}
      {f >= 540 && f < 660 ? (
        <>
          <Frase p={P} en={540} tam={140} y={ARRIBA + 330} lineas={[['VOS'], ['TRABAJÁS.']]} />
          <Frase p={P} en={585} tam={140} y={ARRIBA + 760} lineas={[['YO', {t: 'EDITO'}], ['TUS', {t: 'REELS.', acento: true}]]} />
        </>
      ) : null}

      {/* 22–26: cierre */}
      <Cierre p={P} palabra="UÑAS" en={660} dur={120} />
      <Corte en={[90, 210, 300, 540, 660]} color={P.acento} />
      {f >= R1_DUR - 8 ? (
        <AbsoluteFill style={{background: P.fondo, opacity: tween(f, [R1_DUR - 8, R1_DUR - 4], [0, 1])}}>
          <Frase p={P} en={R1_DUR - 4} tam={128} lineas={[['TU', 'TRABAJO'], ['ES', 'HERMOSO.']]} y={ARRIBA + 300} />
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
