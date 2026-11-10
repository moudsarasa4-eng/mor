import React from 'react';
import {Composition} from 'remotion';
import {cargarFuentes} from './lib/fuentes';
import {Barberia, BarberiaCruda, BARBERIA_DUR, BARBERIA_CRUDA_DUR} from './demos/Barberia';
import {Resto, RESTO_DUR} from './demos/Resto';
import {Padel, PADEL_DUR} from './demos/Padel';
import {ReelEstudio, ESTUDIO_DUR} from './estudio/ReelEstudio';
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
  </>
);
