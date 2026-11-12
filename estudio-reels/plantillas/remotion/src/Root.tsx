import React from 'react';
import {Composition} from 'remotion';
import {cargarFuentes} from './lib/fuentes';
import {Barberia, BarberiaCruda, BARBERIA_DUR, BARBERIA_CRUDA_DUR} from './demos/Barberia';
import {Resto, RESTO_DUR} from './demos/Resto';
import {Padel, PADEL_DUR} from './demos/Padel';
import {ReelEstudio, ESTUDIO_DUR} from './estudio/ReelEstudio';
import {ReelRecordar, RECORDAR_DUR} from './estudio/ReelRecordar';
import {ReelExamen, EXAMEN_DUR} from './estudio/ReelExamen';
import {Reel1Estetica, R1_DUR} from './serie/Reel1Estetica';
import {Reel2Gimnasios, Reel3Odontologia, Reel4Gastronomia, Reel5Inmobiliarias, R_DUR} from './serie/Reels2a5';
import {Boceto} from './serie/Boceto';
import {ReelEditor, duracionEditor, REEL1, REEL2, REEL3, REEL4} from './editor/ReelEditor';
import {ReelNegocio, esquemaNegocio, ejemploNegocio, duracionNegocio} from './plantilla/ReelNegocio';
import {ReelVendedor, VENDEDOR_DUR, esquemaVendedor, propsDueno, propsAnuncios} from './vendedor/ReelVendedor';

cargarFuentes();
const base = {fps: 30, width: 1080, height: 1920};

export const Root: React.FC = () => (
  <>
    <Composition id="Barberia" component={Barberia} durationInFrames={BARBERIA_DUR} {...base} defaultProps={{conAudio: true}} />
    <Composition id="BarberiaCruda" component={BarberiaCruda} durationInFrames={BARBERIA_CRUDA_DUR} {...base} />
    <Composition id="Resto" component={Resto} durationInFrames={RESTO_DUR} {...base} defaultProps={{conAudio: true}} />
    <Composition id="Padel" component={Padel} durationInFrames={PADEL_DUR} {...base} defaultProps={{conAudio: true}} />
    <Composition id="ReelVendedor" component={ReelVendedor} durationInFrames={VENDEDOR_DUR} {...base} schema={esquemaVendedor} defaultProps={propsDueno} />
    <Composition id="ReelVendedorAnuncios" component={ReelVendedor} durationInFrames={VENDEDOR_DUR} {...base} schema={esquemaVendedor} defaultProps={propsAnuncios} />
    <Composition id="ReelNegocio" component={ReelNegocio} durationInFrames={duracionNegocio(ejemploNegocio)} {...base} schema={esquemaNegocio} defaultProps={ejemploNegocio}
      calculateMetadata={({props}) => ({durationInFrames: duracionNegocio(props)})} />
    <Composition id="ReelEstudio" component={ReelEstudio} durationInFrames={ESTUDIO_DUR} {...base} />
    <Composition id="ReelRecordar" component={ReelRecordar} durationInFrames={RECORDAR_DUR} {...base} />
    <Composition id="ReelExamen" component={ReelExamen} durationInFrames={EXAMEN_DUR} {...base} />
    <Composition id="Editor1" component={ReelEditor} durationInFrames={duracionEditor(REEL1)} {...base} defaultProps={REEL1} />
    <Composition id="Editor2" component={ReelEditor} durationInFrames={duracionEditor(REEL2)} {...base} defaultProps={REEL2} />
    <Composition id="Editor3" component={ReelEditor} durationInFrames={duracionEditor(REEL3)} {...base} defaultProps={REEL3} />
    <Composition id="Editor4" component={ReelEditor} durationInFrames={duracionEditor(REEL4)} {...base} defaultProps={REEL4} />
    <Composition id="Reel1Estetica" component={Reel1Estetica} durationInFrames={R1_DUR} {...base} />
    <Composition id="Reel2Gimnasios" component={Reel2Gimnasios} durationInFrames={R_DUR} {...base} />
    <Composition id="Reel3Odontologia" component={Reel3Odontologia} durationInFrames={R_DUR} {...base} />
    <Composition id="Reel4Gastronomia" component={Reel4Gastronomia} durationInFrames={R_DUR} {...base} />
    <Composition id="Reel5Inmobiliarias" component={Reel5Inmobiliarias} durationInFrames={R_DUR} {...base} />
    <Composition id="Boceto" component={Boceto} durationInFrames={1} fps={30} width={1600} height={3400} />
  </>
);
