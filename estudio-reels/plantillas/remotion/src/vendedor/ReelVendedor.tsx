import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {z} from 'zod';
import {Celular, medidasCelular, UIReel} from '../componentes/Celular';
import {Grano} from '../componentes/Grano';
import {Titular} from '../componentes/Texto';
import {pulso, resorte, tween} from '../lib/anim';
import {Efectos, Musica} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// REEL VENDEDOR — 900 cuadros (30 s), música 120 BPM (1 tiempo = 15 cuadros). Los demos de adentro son
// los MP4 reales renderizados aparte (public/demos/*.mp4), sin sonido.
export const VENDEDOR_DUR = 900;
const VERDE = '#2BEA7A';
const CELESTE = '#58C7FF';

export const esquemaVendedor = z.object({
  fraseFuerte: z.array(z.string()).length(3),
  palabraVerde: z.string(),
  subFrase: z.string(),
  editor: z.object({nombre: z.string(), usuario: z.string(), iniciales: z.string()}),
});
export type PropsVendedor = z.infer<typeof esquemaVendedor>;

const UI: Record<string, UIReel> = {
  barberia: {cuenta: 'barberiafilo.ejemplo', inicial: 'BF', colorAvatar: '#B8862F', descripcion: 'El corte que más piden este mes 💈 Turnos por mensaje', audio: 'Audio original'},
  resto: {cuenta: 'brasaviva.ejemplo', inicial: 'BV', colorAvatar: '#E8432E', descripcion: '¿Cuál pedís primero? 1, 2 o 3 🍔', audio: 'Audio original'},
  padel: {cuenta: 'puntopadel.ejemplo', inicial: 'PP', colorAvatar: '#1F5FD6', descripcion: '¿Sos de drive o de revés? 🎾', audio: 'Audio original'},
  malo: {cuenta: 'mi.local', inicial: 'ML', colorAvatar: '#555', descripcion: 'video', audio: 'Audio original'},
};
const DUR: Record<string, number> = {barberia: 560, resto: 504, padel: 480, malo: 120};

/** Video demo dentro del celular: en el cuadro `desde` del reel muestra el cuadro `inicio` del demo. */
const Demo: React.FC<{cual: string; desde: number; inicio: number}> = ({cual, desde, inicio}) => {
  const archivo = cual === 'malo' ? 'barberia-cruda' : cual;
  const trim = ((inicio % DUR[cual]) + DUR[cual]) % DUR[cual];
  return (
    <Sequence from={desde} layout="none">
      <OffthreadVideo src={staticFile(`demos/${archivo}.mp4`)} muted trimBefore={trim} style={{width: 1080, height: 1920}} />
    </Sequence>
  );
};

type Pose = {x: number; y: number; ancho: number; rotY?: number; rotX?: number; rotZ?: number; op?: number};

const Tel: React.FC<{p: Pose; children: React.ReactNode}> = ({p, children}) => {
  const {alto} = medidasCelular(p.ancho);
  return (
    <div
      style={{
        position: 'absolute',
        left: p.x - p.ancho / 2,
        top: p.y - alto / 2,
        opacity: p.op ?? 1,
        transform: `perspective(2600px) rotateY(${p.rotY ?? 0}deg) rotateX(${p.rotX ?? 0}deg) rotateZ(${p.rotZ ?? 0}deg)`,
      }}
    >
      {children}
    </div>
  );
};

const progresoDe = (cual: string, f: number, desde: number, inicio: number) => (((f - desde + inicio) % DUR[cual]) + DUR[cual]) % DUR[cual] / DUR[cual];

const Bandeja: React.FC<{f: number; ancho: number; desde: number}> = ({f, ancho, desde}) => {
  const {fps} = useVideoConfig();
  const {ws, videoH} = medidasCelular(ancho);
  const u = ws / 100;
  const msjs = [
    {n: 'Sofi', c: '#F59E1B', t: 'Hola! ¿Hacen delivery?'},
    {n: 'Martín', c: '#58C7FF', t: '¿Precio de la doble cheddar?'},
    {n: 'Caro', c: '#E8432E', t: '¿Tienen mesa para 4 a las 21?'},
    {n: 'Nico', c: '#2BEA7A', t: 'Vi el reel, ¿abren los lunes?'},
  ];
  return (
    <div style={{position: 'absolute', inset: 0, width: ws, height: videoH, background: '#0E0F13', fontFamily: FUENTE.inter, color: '#fff'}}>
      <div style={{position: 'absolute', top: 15 * u, left: 5 * u, right: 5 * u, display: 'flex', alignItems: 'center', gap: 3 * u}}>
        <div style={{width: 10 * u, height: 10 * u, borderRadius: '50%', background: '#E8432E', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 4 * u}}>BV</div>
        <div>
          <div style={{fontWeight: 800, fontSize: 5 * u}}>Mensajes</div>
          <div style={{fontWeight: 500, fontSize: 3.2 * u, opacity: 0.6}}>Brasa Viva · ejemplo</div>
        </div>
      </div>
      {msjs.map((m, i) => {
        const en = desde + 12 + i * 25;
        const s = resorte(f, fps, en, 'pop');
        // los nuevos entran arriba y empujan a los anteriores
        const llegados = msjs.filter((_, j) => f >= desde + 12 + j * 25).length;
        if (f < en) return null;
        const pos = llegados - 1 - i;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: 4 * u,
              right: 4 * u,
              top: 32 * u + pos * 19 * u,
              height: 16 * u,
              borderRadius: 4 * u,
              background: pos === 0 ? '#1C2A22' : '#17181E',
              border: `${0.3 * u}px solid ${pos === 0 ? VERDE : 'rgba(255,255,255,0.08)'}`,
              display: 'flex',
              alignItems: 'center',
              gap: 3 * u,
              padding: `0 ${3.5 * u}px`,
              transform: `translateY(${(1 - s) * -10 * u}px) scale(${0.9 + 0.1 * s})`,
              opacity: Math.min(1, s * 2),
            }}
          >
            <div style={{width: 10 * u, height: 10 * u, borderRadius: '50%', background: m.c, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 4.4 * u, color: '#0E0F13'}}>{m.n[0]}</div>
            <div style={{flex: 1, minWidth: 0}}>
              <div style={{fontWeight: 800, fontSize: 4 * u}}>{m.n}</div>
              <div style={{fontWeight: 500, fontSize: 3.6 * u, opacity: 0.85, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{m.t}</div>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 1.4 * u}}>
              <div style={{fontSize: 2.8 * u, opacity: 0.6}}>ahora</div>
              <div style={{width: 3 * u, height: 3 * u, borderRadius: '50%', background: VERDE}} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

const Fondo: React.FC<{f: number; gris: number}> = ({f, gris}) => (
  <AbsoluteFill style={{background: '#0A0A0F'}}>
    <div style={{position: 'absolute', left: 140 + Math.sin(f / 60) * 120, top: 300 + Math.cos(f / 80) * 100, width: 900, height: 900, borderRadius: '50%', background: VERDE, opacity: 0.13 * (1 - gris), filter: 'blur(160px)'}} />
    <div style={{position: 'absolute', left: -200 + Math.cos(f / 70) * 100, top: 1100 + Math.sin(f / 50) * 120, width: 900, height: 900, borderRadius: '50%', background: CELESTE, opacity: 0.11 * (1 - gris), filter: 'blur(170px)'}} />
    <AbsoluteFill style={{background: '#2a2a2a', opacity: 0.45 * gris}} />
  </AbsoluteFill>
);

const Perfil: React.FC<{f: number; props: PropsVendedor}> = ({f, props}) => {
  const {fps} = useVideoConfig();
  const s = resorte(f, fps, 690, 'suave');
  const salida = tween(f, [810, 824], [1, 0]);
  const tap = f >= 762 && f < 790 ? (f - 762) / 28 : -1;
  const pulsoBtn = f >= 750 ? 1 + 0.05 * pulso(f, 15) : 1;
  return (
    <div style={{position: 'absolute', left: 90, top: 560, width: 900, opacity: s * salida, transform: `translateY(${(1 - s) * 200 + (1 - salida) * -120}px)`, fontFamily: FUENTE.inter, color: '#fff'}}>
      <div style={{background: '#14141B', border: '2px solid #2A2A35', borderRadius: 54, padding: 50, boxShadow: '0 40px 100px rgba(0,0,0,0.5)'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 40}}>
          <div style={{width: 190, height: 190, borderRadius: '50%', padding: 7, background: `linear-gradient(135deg, ${VERDE}, ${CELESTE})`}}>
            <div style={{width: '100%', height: '100%', borderRadius: '50%', background: '#22232c', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 64}}>{props.editor.iniciales}</div>
          </div>
          <div>
            <div style={{fontWeight: 900, fontSize: 58, letterSpacing: '-0.02em'}}>{props.editor.nombre}</div>
            <div style={{fontWeight: 600, fontSize: 38, opacity: 0.6}}>{props.editor.usuario}</div>
          </div>
        </div>
        <div style={{marginTop: 34, fontSize: 40, lineHeight: 1.35, fontWeight: 600}}>
          Editor de reels para negocios
          <div style={{opacity: 0.65, fontWeight: 500, fontSize: 34}}>Guion · edición · subtítulos · portada</div>
          <div style={{color: VERDE, fontWeight: 800}}>Vos atendés. Yo hago tus reels.</div>
        </div>
        <div style={{display: 'flex', gap: 20, marginTop: 36}}>
          <div style={{flex: 1, position: 'relative', textAlign: 'center', background: VERDE, color: '#04130a', fontWeight: 900, fontSize: 44, padding: '24px 0', borderRadius: 24, transform: `scale(${pulsoBtn})`, overflow: 'hidden'}}>
            Mensaje
            {tap >= 0 ? <div style={{position: 'absolute', left: '50%', top: '50%', width: 600 * tap, height: 600 * tap, marginLeft: -300 * tap, marginTop: -300 * tap, borderRadius: '50%', background: 'rgba(255,255,255,0.45)', opacity: 1 - tap}} /> : null}
          </div>
          <div style={{flex: 1, textAlign: 'center', border: '3px solid #3a3a46', fontWeight: 800, fontSize: 44, padding: '21px 0', borderRadius: 24}}>Seguir</div>
        </div>
        <div style={{display: 'flex', gap: 14, marginTop: 36}}>
          {(['barberia', 'resto', 'padel'] as const).map((c, i) => (
            <div key={c} style={{flex: 1, height: 470, borderRadius: 18, overflow: 'hidden', position: 'relative', background: '#000'}}>
              <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transform: `scale(${264 / 1080})`, transformOrigin: '0 0'}}>
                <Demo cual={c} desde={690} inicio={[400, 0, 300][i]} />
              </div>
              <div style={{position: 'absolute', left: 10, top: 10, fontSize: 18, fontWeight: 800, letterSpacing: '0.12em', background: 'rgba(0,0,0,0.6)', padding: '4px 10px', borderRadius: 8}}>EJEMPLO</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const Flecha: React.FC<{f: number}> = ({f}) => {
  const p = tween(f, [828, 850], [0, 1]);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
      <path d="M 700 1180 C 640 1420, 420 1500, 230 1600" stroke={VERDE} strokeWidth={22} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} style={{filter: `drop-shadow(0 0 20px ${VERDE})`}} />
      {p > 0.95 ? <path d="M 300 1540 L 222 1604 L 318 1640" stroke={VERDE} strokeWidth={22} fill="none" strokeLinecap="round" strokeLinejoin="round" /> : null}
    </svg>
  );
};

export const ReelVendedor: React.FC<PropsVendedor> = (props) => {
  const f = useCurrentFrame();
  const beat = pulso(f, 15);

  // ---------------- poses por escena
  const s1 = (ff: number): Pose => ({x: 540, y: 1370, ancho: 700, rotY: tween(ff, [0, 60], [-14, -8]), rotX: 6, rotZ: 2});
  const grillaOn = resorte(f, 30, 150, 'pop');
  const zoom = resorte(f, 30, 270, 'suave');
  const abanico = resorte(f, 30, 540, 'pop');
  const fanPose = (i: number): Pose => ({x: [175, 410, 670, 905][i], y: [1330, 1250, 1250, 1330][i], ancho: 300, rotZ: [-14, -5, 5, 14][i], rotY: 0});

  const resalteT = (a: number) => tween(f, [a, a + 8], [0, 1]) * tween(f, [a + 40, a + 46], [1, 0]);
  const gris = f >= 60 && f < 150 ? tween(f, [60, 66], [0, 1]) : 0;

  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <Fondo f={f} gris={gris} />

      {/* S1 — ¿Tus reels se ven así? (y el cierre del loop 880–900) */}
      {(f < 60 || f >= 880) && (
        <Tel p={f >= 880 ? {...s1(0), y: tween(f, [880, 896], [2200, 1370])} : s1(f)}>
          <Celular ancho={700} ui={UI.barberia} progreso={progresoDe('barberia', f >= 880 ? f - 900 : f, 0, 30)}>
            <Demo cual="barberia" desde={f >= 880 ? 880 : 0} inicio={f >= 880 ? 10 : 30} />
          </Celular>
        </Tel>
      )}
      {f < 60 ? (
        <Titular top={250} tam={124} fuente={FUENTE.inter} peso={900} hasta={60} lineas={[[{t: '¿Tus reels', en: -6}], [{t: 'se ven', en: -4}, {t: 'así?', en: -2, color: VERDE}]]} />
      ) : null}

      {/* S2 — ¿O así? (mismo video, sin editar) */}
      {f >= 60 && f < 150 ? (
        <>
          <Tel p={{x: 540, y: 1370, ancho: 700, rotY: 10, rotX: 6, rotZ: -2}}>
            <Celular ancho={700} ui={UI.malo} progreso={(f - 60) / 120}>
              <Demo cual="malo" desde={60} inicio={0} />
            </Celular>
          </Tel>
          <Titular top={300} tam={150} fuente={FUENTE.inter} peso={900} color="#d6d6d6" hasta={150} lineas={[[{t: '¿O así?', en: 61}]]} />
        </>
      ) : null}

      {/* S3 — grilla: gancho, subtítulos, ritmo */}
      {f >= 150 && f < 290 ? (
        <>
          {(['barberia', 'resto', 'padel'] as const).map((c, i) => {
            const enZoom = i === 1 ? zoom : 0;
            const base: Pose = {x: [190, 540, 890][i], y: 1130, ancho: i === 1 ? 330 : 300};
            const sale = i !== 1 ? zoom : 0;
            const p: Pose = {
              x: base.x + (i === 1 ? 0 : (i === 0 ? -1 : 1) * 700 * sale),
              y: base.y + (1 - grillaOn) * 900 + enZoom * 110,
              ancho: base.ancho + enZoom * 310,
              rotZ: (i - 1) * 4 * (1 - enZoom),
            };
            const activo = f < 200 ? 0 : f < 235 ? 1 : 2;
            const res =
              i === 0 && f < 200
                ? {x: 60, y: 210, w: 960, h: 560, t: resalteT(152), etiqueta: '0–3 s'}
                : i === 1 && f >= 200 && f < 235
                  ? {x: 90, y: 1460, w: 900, h: 220, t: resalteT(200)}
                  : i === 2 && f >= 235 && f < 270
                    ? {x: 20, y: 20, w: 1040, h: 1880, t: resalteT(235) * (0.6 + 0.4 * beat)}
                    : null;
            return (
              <Tel key={c} p={p}>
                <Celular ancho={p.ancho} ui={UI[c]} apagado={f < 270 && activo !== i ? 0.45 : 0} resaltar={res} progreso={progresoDe(c, f, 150, [0, 234, 215][i])}>
                  <Demo cual={c} desde={150} inicio={[0, 234, 215][i]} />
                </Celular>
              </Tel>
            );
          })}
          {f < 200 ? <Titular top={300} tam={110} fuente={FUENTE.inter} peso={900} hasta={200} lineas={[[{t: 'Gancho en', en: 151}], [{t: '3 segundos', en: 155, color: VERDE}]]} /> : null}
          {f >= 200 && f < 235 ? <Titular top={330} tam={130} fuente={FUENTE.inter} peso={900} hasta={235} lineas={[[{t: 'Subtítulos', en: 200, color: VERDE}]]} /> : null}
          {f >= 235 && f < 270 ? <Titular top={330} tam={150} fuente={FUENTE.inter} peso={900} hasta={270} lineas={[[{t: 'Ritmo', en: 235, color: VERDE}]]} /> : null}
        </>
      ) : null}

      {/* S4 + S5 — hasta el final… y te escriban */}
      {f >= 290 && f < 548 ? (
        <Tel p={{x: 540, y: 1240 - (f >= 520 ? tween(f, [520, 548], [0, 0]) : 0), ancho: 640, rotY: Math.sin(f / 40) * 3}}>
          <Celular ancho={640} ui={UI.resto} progreso={progresoDe('resto', f, 150, 234)} mezclaPantalla={tween(f, [420, 432], [0, 1])} pantalla={<Bandeja f={f} ancho={640} desde={420} />}>
            <Demo cual="resto" desde={150} inicio={234} />
          </Celular>
        </Tel>
      ) : null}
      {f >= 280 && f < 420 ? (
        <Titular top={250} tam={104} fuente={FUENTE.inter} peso={900} hasta={420}
          lineas={[[{t: 'Hechos', en: 285}, {t: 'para que', en: 300}], [{t: 'los vean', en: 315}], [{t: 'hasta el final', en: 345, color: VERDE}]]} />
      ) : null}
      {f >= 420 && f < 540 ? <Titular top={300} tam={140} fuente={FUENTE.inter} peso={900} hasta={540} lineas={[[{t: 'y te', en: 425}, {t: 'escriban', en: 429, color: VERDE}]]} /> : null}

      {/* S6 — abanico */}
      {f >= 540 && f < 700 ? (
        <>
          <AbsoluteFill style={{background: `radial-gradient(circle at 50% 66%, ${VERDE}55 0%, rgba(43,234,122,0) 45%)`, opacity: tween(f, [540, 550], [0, 1]) * (0.75 + 0.25 * beat)}} />
          {(['barberia', 'resto', 'padel', 'chat'] as const).map((c, i) => {
            const fin = fanPose(i);
            const p: Pose = {...fin, x: 540 + (fin.x - 540) * abanico, y: 1290 + (fin.y - 1290) * abanico + (1 - abanico) * 120, rotZ: (fin.rotZ ?? 0) * abanico, op: tween(f, [690, 700], [1, 0])};
            return (
              <Tel key={c} p={p}>
                {c === 'chat' ? (
                  <Celular ancho={300} mezclaPantalla={1} pantalla={<Bandeja f={f} ancho={300} desde={420} />} />
                ) : (
                  <Celular ancho={300} ui={UI[c]} progreso={progresoDe(c, f, 540, [160, 72, 60][i])}>
                    <Demo cual={c} desde={540} inicio={[160, 72, 60][i]} />
                  </Celular>
                )}
              </Tel>
            );
          })}
          <Titular top={260} tam={118} fuente={FUENTE.inter} peso={900} entrada="golpe" hasta={690} interlineado={1.04}
            lineas={props.fraseFuerte.map((l, i) => l.split(' ').map((w, j) => ({t: w, en: 548 + i * 15 + j * 3, color: w === props.palabraVerde ? VERDE : undefined})))} />
          {props.subFrase ? <Titular top={690} tam={64} fuente={FUENTE.inter} peso={800} hasta={690} lineas={[[{t: props.subFrase, en: 600, color: VERDE}]]} /> : null}
        </>
      ) : null}

      {/* S7 — te los hago yo / escribime */}
      {f >= 690 && f < 830 ? <Perfil f={f} props={props} /> : null}
      {f >= 690 && f < 750 ? <Titular top={300} tam={110} fuente={FUENTE.inter} peso={900} hasta={750} lineas={[[{t: 'Te los', en: 692}, {t: 'hago yo', en: 696, color: VERDE}]]} /> : null}
      {f >= 750 && f < 810 ? <Titular top={300} tam={130} fuente={FUENTE.inter} peso={900} hasta={810} lineas={[[{t: 'Escribime', en: 750, color: VERDE}]]} /> : null}

      {/* S8 — link en el perfil */}
      {f >= 810 && f < 884 ? (
        <>
          <Titular top={760} tam={130} fuente={FUENTE.inter} peso={900} hasta={884} lineas={[[{t: 'Link en', en: 814}], [{t: 'el perfil', en: 818, color: VERDE}]]} />
          <Flecha f={f} />
        </>
      ) : null}

      <Grano opacidad={0.05} vineta={0.5} />
      <Musica archivo="musica-vendedor.wav" volumen={0.8} />
      <Efectos
        eventos={[
          {en: 1, sfx: 'pop', vol: 0.35},
          {en: 60, sfx: 'womp', vol: 0.5},
          {en: 148, sfx: 'whoosh', vol: 0.5}, {en: 152, sfx: 'pop', vol: 0.4}, {en: 200, sfx: 'pop', vol: 0.4}, {en: 235, sfx: 'pop', vol: 0.4},
          {en: 268, sfx: 'whoosh', vol: 0.45},
          {en: 285, sfx: 'pop-suave', vol: 0.35}, {en: 300, sfx: 'pop-suave', vol: 0.35}, {en: 315, sfx: 'pop-suave', vol: 0.35}, {en: 345, sfx: 'pop', vol: 0.4},
          {en: 418, sfx: 'swipe', vol: 0.5},
          {en: 432, sfx: 'ding', vol: 0.4}, {en: 457, sfx: 'ding', vol: 0.4}, {en: 482, sfx: 'ding', vol: 0.4}, {en: 507, sfx: 'ding', vol: 0.4},
          {en: 548, sfx: 'golpe', vol: 0.45}, {en: 563, sfx: 'golpe', vol: 0.45}, {en: 578, sfx: 'golpe', vol: 0.45},
          {en: 688, sfx: 'whoosh', vol: 0.45}, {en: 750, sfx: 'pop', vol: 0.4}, {en: 765, sfx: 'click', vol: 0.6},
          {en: 808, sfx: 'whoosh', vol: 0.45}, {en: 814, sfx: 'pop', vol: 0.4},
          {en: 878, sfx: 'swipe', vol: 0.45},
        ]}
      />
    </AbsoluteFill>
  );
};

export const propsDueno: PropsVendedor = {
  fraseFuerte: ['GANÁ VENTAS', 'VIRALIZANDO', 'TUS REELS'],
  palabraVerde: 'VENTAS',
  subFrase: '',
  editor: {nombre: 'Tu Nombre', usuario: '@tu.usuario', iniciales: 'TN'},
};
export const propsAnuncios: PropsVendedor = {
  fraseFuerte: ['REELS HECHOS', 'PARA QUE TE', 'COMPARTAN'],
  palabraVerde: 'COMPARTAN',
  subFrase: '(y te escriban)',
  editor: propsDueno.editor,
};
