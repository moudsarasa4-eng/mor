import React, {useMemo} from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {Grano} from '../componentes/Grano';
import {Titular} from '../componentes/Texto';
import {pulso, resorte, tween} from '../lib/anim';
import {Efectos, Musica} from '../lib/audio';
import {FUENTE} from '../lib/fuentes';

// DEMO 3 — "Punto Pádel" (NEGOCIO FICTICIO). 480 cuadros, 120 BPM (1 tiempo = 15 cuadros). Cancha 3D nocturna.
export const PADEL_DUR = 480;
const CELESTE = '#19E3FF';
const LIMA = '#C8FF2E';

type V3 = [number, number, number];
const lerp3 = (a: V3, b: V3, t: number): V3 => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

const INICIO_CAM: V3 = [0, 1.35, 13.2];
const INICIO_MIRA: V3 = [0, 1.1, 0];

const camaraEn = (f: number): {pos: V3; mira: V3} => {
  if (f < 60) return {pos: lerp3(INICIO_CAM, [0.4, 1.25, 11.8], f / 60), mira: INICIO_MIRA};
  if (f < 180) {
    const a = 0.55 + ((f - 60) / 120) * 0.35;
    return {pos: [2.5 + Math.sin(a) * 9, 7.5, 4 + Math.cos(a) * 9], mira: [2.5, 0, 4.5]};
  }
  if (f < 300) {
    const a = -0.55 - ((f - 180) / 120) * 0.35;
    return {pos: [-2.5 + Math.sin(a) * 9, 7.5, 4 + Math.cos(a) * 9], mira: [-2.5, 0, 4.5]};
  }
  if (f < 390) {
    const k = Math.floor((f - 300) / 15) % 4;
    const ang: {pos: V3; mira: V3}[] = [
      {pos: [7, 2.2, 0.5], mira: [0, 1, 0]},
      {pos: [0, 2.0, 12], mira: [0, 1, 0]},
      {pos: [-6.5, 5, -9], mira: [0, 0.8, 2]},
      {pos: [0, 14, 0.01], mira: [0, 0, 0]},
    ];
    return ang[k];
  }
  if (f < 450) return {pos: lerp3([0, 12, 9], [0, 16, 5], (f - 390) / 60), mira: [0, 0, 0]};
  const t = ease((f - 450) / 30);
  return {pos: lerp3([0, 16, 5], INICIO_CAM, t), mira: lerp3([0, 0, 0], INICIO_MIRA, t)};
};

const pelotaEn = (f: number): V3 => {
  const ff = f >= 450 ? f - 480 : f;
  if (ff < 0) return [-1, 2.6, -9];
  if (ff < 28) {
    const t = ff / 28;
    return [-1 + 1.6 * t, 2.6 - 1.4 * t + Math.sin(t * Math.PI) * 0.8, -9 + 19 * t];
  }
  if (ff < 60) {
    const t = (ff - 28) / 32;
    return [0.6 + 1.4 * t, 1.2 + Math.sin(t * Math.PI) * 2.6, 10 - 15 * t];
  }
  if (f >= 300 && f < 390) {
    const k = Math.floor((f - 300) / 15);
    const t = ((f - 300) % 15) / 15;
    const ida = k % 2 === 0;
    const z0 = ida ? 7 : -7;
    const x0 = ((k * 37) % 5) - 2;
    const x1 = (((k + 1) * 37) % 5) - 2;
    return [x0 + (x1 - x0) * t, 0.4 + Math.sin(t * Math.PI) * 2.2, z0 + (ida ? -14 : 14) * t];
  }
  if (f < 300) {
    const t = ((f - 60) % 60) / 60;
    return [Math.sin(f / 20) * 3, 0.5 + Math.abs(Math.sin(t * Math.PI * 2)) * 1.8, Math.cos(f / 24) * 7];
  }
  return [0, 0.5, 0];
};

const Camara: React.FC<{f: number}> = ({f}) => {
  const {camera} = useThree();
  const c = camaraEn(f);
  camera.position.set(...c.pos);
  camera.lookAt(new THREE.Vector3(...c.mira));
  camera.updateProjectionMatrix();
  return null;
};

const Linea: React.FC<{x: number; z: number; w: number; d: number}> = ({x, z, w, d}) => (
  <mesh position={[x, 0.012, z]}>
    <boxGeometry args={[w, 0.01, d]} />
    <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.5} />
  </mesh>
);

const Vidrio: React.FC<{pos: V3; size: [number, number]; rotY?: number}> = ({pos, size, rotY = 0}) => (
  <group position={pos} rotation={[0, rotY, 0]}>
    <mesh>
      <planeGeometry args={size} />
      <meshStandardMaterial color="#9fd8ff" transparent opacity={0.1} side={THREE.DoubleSide} />
    </mesh>
    <mesh position={[0, size[1] / 2, 0]}>
      <boxGeometry args={[size[0], 0.05, 0.05]} />
      <meshStandardMaterial color="#222831" />
    </mesh>
  </group>
);

const Neon: React.FC<{pos: V3; largo: number; color: string; intensidad: number; rotY?: number}> = ({pos, largo, color, intensidad, rotY = 0}) => (
  <group position={pos} rotation={[0, rotY, 0]}>
    <mesh>
      <boxGeometry args={[0.06, 0.06, largo]} />
      <meshBasicMaterial color={color} />
    </mesh>
    <mesh>
      <boxGeometry args={[0.35, 0.35, largo + 0.3]} />
      <meshBasicMaterial color={color} transparent opacity={0.18 * intensidad} blending={THREE.AdditiveBlending} depthWrite={false} />
    </mesh>
    <mesh>
      <boxGeometry args={[0.9, 0.9, largo + 0.8]} />
      <meshBasicMaterial color={color} transparent opacity={0.06 * intensidad} blending={THREE.AdditiveBlending} depthWrite={false} />
    </mesh>
  </group>
);

const Escena: React.FC<{f: number}> = ({f}) => {
  const drive = f >= 60 && f < 180 ? 1 + pulso(f, 15) : 0.35;
  const reves = f >= 180 && f < 300 ? 1 + pulso(f, 15) : 0.35;
  const rally = f >= 300 && f < 390 ? 1 + pulso(f, 15) * 1.5 : 1;
  const p = pelotaEn(f);
  const estela = useMemo(() => Array.from({length: 10}), []);
  return (
    <>
      <Camara f={f} />
      <color attach="background" args={['#050A1F']} />
      <fog attach="fog" args={['#050A1F', 18, 48]} />
      <ambientLight intensity={0.55} />
      <hemisphereLight args={['#6fa8ff', '#0a0f2a', 0.8]} />
      <directionalLight position={[6, 14, 8]} intensity={1.4} />
      <directionalLight position={[-6, 12, -8]} intensity={0.8} color="#9ecbff" />
      {/* suelo y cancha */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
        <planeGeometry args={[80, 80]} />
        <meshStandardMaterial color="#0A1030" />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[10, 20]} />
        <meshStandardMaterial color="#1F5FD6" roughness={0.9} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[2.5, 0.006, 5]}>
        <planeGeometry args={[5, 10]} />
        <meshBasicMaterial color={CELESTE} transparent opacity={f >= 60 && f < 180 ? 0.22 * drive : 0} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-2.5, 0.006, 5]}>
        <planeGeometry args={[5, 10]} />
        <meshBasicMaterial color={LIMA} transparent opacity={f >= 180 && f < 300 ? 0.2 * reves : 0} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      <Linea x={0} z={-10} w={10} d={0.06} />
      <Linea x={0} z={10} w={10} d={0.06} />
      <Linea x={-5} z={0} w={0.06} d={20} />
      <Linea x={5} z={0} w={0.06} d={20} />
      <Linea x={0} z={6.95} w={10} d={0.05} />
      <Linea x={0} z={-6.95} w={10} d={0.05} />
      <Linea x={0} z={0} w={0.05} d={13.9} />
      {/* red */}
      <mesh position={[0, 0.45, 0]}>
        <boxGeometry args={[10, 0.88, 0.02]} />
        <meshStandardMaterial color="#0b0f1a" transparent opacity={0.6} />
      </mesh>
      <mesh position={[0, 0.9, 0]}>
        <boxGeometry args={[10, 0.06, 0.05]} />
        <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.4} />
      </mesh>
      {/* vidrios */}
      <Vidrio pos={[0, 1.5, -10]} size={[10, 3]} />
      <Vidrio pos={[0, 1.5, 10]} size={[10, 3]} />
      {[-5, 5].map((x) =>
        [-8, 8].map((z) => <Vidrio key={`${x}${z}`} pos={[x, 1.5, z]} size={[4, 3]} rotY={Math.PI / 2} />),
      )}
      {[-5, 5].map((x) => (
        <mesh key={x} position={[x, 1.5, 0]}>
          <boxGeometry args={[0.02, 3, 12]} />
          <meshStandardMaterial color="#1a2238" transparent opacity={0.35} wireframe />
        </mesh>
      ))}
      {/* postes de luz */}
      {[[-6, -10], [6, -10], [-6, 10], [6, 10], [-6, 0], [6, 0]].map(([x, z], i) => (
        <group key={i} position={[x, 0, z]}>
          <mesh position={[0, 3.5, 0]}>
            <boxGeometry args={[0.12, 7, 0.12]} />
            <meshStandardMaterial color="#1b2133" />
          </mesh>
          <mesh position={[0, 7.05, 0]}>
            <boxGeometry args={[0.9, 0.18, 0.5]} />
            <meshBasicMaterial color="#ffffff" />
          </mesh>
          <mesh position={[0, 7.05, 0]}>
            <sphereGeometry args={[1.1, 16, 16]} />
            <meshBasicMaterial color="#cfe6ff" transparent opacity={0.12} blending={THREE.AdditiveBlending} depthWrite={false} />
          </mesh>
        </group>
      ))}
      {/* neón: drive (derecha) y revés (izquierda) */}
      <Neon pos={[5.15, 0.05, 0]} largo={20} color={CELESTE} intensidad={drive * rally} />
      <Neon pos={[-5.15, 0.05, 0]} largo={20} color={LIMA} intensidad={reves * rally} />
      <Neon pos={[0, 0.05, 10.15]} largo={10.3} color="#ffffff" intensidad={0.4 * rally} rotY={Math.PI / 2} />
      {/* pelota + estela */}
      {estela.map((_, i) => {
        const q = pelotaEn(f - i * 0.6);
        return (
          <mesh key={i} position={q}>
            <sphereGeometry args={[0.09 * (1 - i / 12), 12, 12]} />
            <meshBasicMaterial color={LIMA} transparent opacity={i === 0 ? 1 : 0.35 * (1 - i / 10)} blending={i === 0 ? THREE.NormalBlending : THREE.AdditiveBlending} depthWrite={i === 0} />
          </mesh>
        );
      })}
      <mesh position={p}>
        <sphereGeometry args={[0.32, 16, 16]} />
        <meshBasicMaterial color={LIMA} transparent opacity={0.18} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
    </>
  );
};

const Rasgos: React.FC<{f: number; desde: number; titulo: string; color: string; items: string[]}> = ({f, desde, titulo, color, items}) => {
  const {fps} = useVideoConfig();
  if (f < desde || f >= desde + 120) return null;
  const sal = tween(f, [desde + 113, desde + 120], [1, 0]);
  return (
    <AbsoluteFill style={{opacity: sal}}>
      <Titular top={250} tam={250} fuente={FUENTE.barlow} peso={900} color={color} tracking="0.01em" inclinacion={-8} entrada="golpe"
        sombra={`0 0 40px ${color}99, 0 10px 30px rgba(0,0,0,0.6)`} lineas={[[{t: titulo, en: desde + 1, italica: true}]]} />
      <div style={{position: 'absolute', top: 1180, left: 90, right: 90, display: 'flex', flexDirection: 'column', gap: 26}}>
        {items.map((it, i) => {
          const s = resorte(f, fps, desde + 12 + i * 30, 'pop');
          return (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 24, opacity: Math.min(1, s * 2), transform: `translateX(${(1 - s) * -120}px)`}}>
              <div style={{width: 26, height: 26, borderRadius: '50%', background: color, boxShadow: `0 0 20px ${color}`}} />
              <div style={{fontFamily: FUENTE.barlow, fontWeight: 800, fontStyle: 'italic', fontSize: 84, color: '#fff', textTransform: 'uppercase', textShadow: '0 6px 24px rgba(0,0,0,0.75)'}}>{it}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const Padel: React.FC<{conAudio?: boolean}> = ({conAudio = true}) => {
  const f = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const flash = f >= 300 && f < 390 ? Math.exp(-(((f - 300) % 15) / 2)) * 0.25 : 0;
  return (
    <AbsoluteFill style={{background: '#050A1F'}}>
      <ThreeCanvas width={width} height={height} camera={{fov: 52, position: INICIO_CAM}} gl={{antialias: true}}>
        <Escena f={f} />
      </ThreeCanvas>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,10,31,0.75) 0%, rgba(5,10,31,0) 32%, rgba(5,10,31,0) 55%, rgba(5,10,31,0.7) 100%)'}} />
      {flash ? <AbsoluteFill style={{background: '#fff', opacity: flash}} /> : null}
      {f < 60 || f >= 470 ? (
        <Titular top={260} tam={158} fuente={FUENTE.barlow} peso={900} color="#fff" tracking="0" inclinacion={-8} interlineado={0.9} hasta={f >= 470 ? undefined : 60}
          sombra="0 10px 40px rgba(0,0,0,0.7)"
          lineas={[
            [{t: '¿SOS DE', en: f >= 470 ? 470 : -8, italica: true}, {t: 'DRIVE', en: f >= 470 ? 472 : -6, italica: true, color: CELESTE}],
            [{t: 'O DE', en: f >= 470 ? 474 : -4, italica: true}, {t: 'REVÉS?', en: f >= 470 ? 476 : -2, italica: true, color: LIMA}],
          ]}
        />
      ) : null}
      <Rasgos f={f} desde={60} titulo="DRIVE" color={CELESTE} items={['Arma el punto', 'Devuelve todo', 'Nunca se queja']} />
      <Rasgos f={f} desde={180} titulo="REVÉS" color={LIMA} items={['Define con el remate', "Dice 'mía' a todo", 'Festeja como final']} />
      {f >= 300 && f < 390 ? (
        <Titular top={270} tam={130} fuente={FUENTE.barlow} peso={900} color="#fff" tracking="0" inclinacion={-8} interlineado={0.95} hasta={390}
          sombra="0 10px 40px rgba(0,0,0,0.8)"
          lineas={[[{t: 'MANDÁSELO A', en: 301, italica: true}], [{t: 'TU COMPAÑERO', en: 306, italica: true, color: LIMA}], [{t: 'y que confiese cuál es', en: 330, italica: true, rel: 0.5}]]} />
      ) : null}
      {f >= 390 && f < 468 ? (
        <AbsoluteFill style={{opacity: tween(f, [458, 468], [1, 0])}}>
          <Titular top={330} tam={200} fuente={FUENTE.barlow} peso={900} color="#fff" tracking="0.02em" inclinacion={-8} interlineado={0.86}
            sombra={`0 0 50px ${CELESTE}88`}
            lineas={[[{t: 'PUNTO', en: 392, italica: true}], [{t: 'PÁDEL', en: 396, italica: true, color: LIMA}]]} />
          <Titular top={1140} tam={88} fuente={FUENTE.barlow} peso={800} color="#fff" tracking="0.02em" lineas={[[{t: 'Reservá por mensaje', en: 404}]]} sombra="0 6px 24px rgba(0,0,0,0.8)" />
          <div style={{position: 'absolute', top: 1270, left: '50%', transform: `translateX(-50%) scale(${0.7 + 0.3 * tween(f, [410, 418], [0, 1])})`, opacity: tween(f, [410, 416], [0, 1]), background: LIMA, color: '#07101f', fontFamily: FUENTE.barlow, fontWeight: 900, fontSize: 60, padding: '16px 48px', borderRadius: 80, whiteSpace: 'nowrap', boxShadow: `0 0 40px ${LIMA}88`}}>
            LINK EN EL PERFIL
          </div>
        </AbsoluteFill>
      ) : null}
      <Grano opacidad={0.05} vineta={0.5} />
      {conAudio ? (
        <>
          <Musica archivo="musica-padel.wav" volumen={0.75} />
          <Efectos
            eventos={[
              {en: 28, sfx: 'pelota', vol: 0.6},
              {en: 58, sfx: 'whoosh', vol: 0.4}, {en: 61, sfx: 'golpe', vol: 0.45},
              {en: 72, sfx: 'pop', vol: 0.35}, {en: 102, sfx: 'pop', vol: 0.35}, {en: 132, sfx: 'pop', vol: 0.35},
              {en: 178, sfx: 'whoosh', vol: 0.4}, {en: 181, sfx: 'golpe', vol: 0.45},
              {en: 192, sfx: 'pop', vol: 0.35}, {en: 222, sfx: 'pop', vol: 0.35}, {en: 252, sfx: 'pop', vol: 0.35},
              ...[300, 315, 330, 345, 360, 375].map((en) => ({en, sfx: 'pelota', vol: 0.55})),
              {en: 390, sfx: 'golpe', vol: 0.5}, {en: 450, sfx: 'whoosh', vol: 0.45},
            ]}
          />
        </>
      ) : null}
    </AbsoluteFill>
  );
};

export const _usarInterpolate = interpolate; // evita advertencia de import sin uso
