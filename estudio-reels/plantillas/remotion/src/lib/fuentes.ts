// Fuentes locales (licencia SIL OFL: uso comercial permitido). Se cargan antes de renderizar.
import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

const lista: {family: string; file: string; weight: string; style?: 'normal' | 'italic'}[] = [
  {family: 'Inter', file: 'inter-latin-500-normal', weight: '500'},
  {family: 'Inter', file: 'inter-latin-600-normal', weight: '600'},
  {family: 'Inter', file: 'inter-latin-700-normal', weight: '700'},
  {family: 'Inter', file: 'inter-latin-800-normal', weight: '800'},
  {family: 'Inter', file: 'inter-latin-900-normal', weight: '900'},
  {family: 'Bebas Neue', file: 'bebas-neue-latin-400-normal', weight: '400'},
  {family: 'Playfair Display', file: 'playfair-display-latin-700-normal', weight: '700'},
  {family: 'Playfair Display', file: 'playfair-display-latin-700-italic', weight: '700', style: 'italic'},
  {family: 'Playfair Display', file: 'playfair-display-latin-800-italic', weight: '800', style: 'italic'},
  {family: 'Rubik', file: 'rubik-latin-500-normal', weight: '500'},
  {family: 'Rubik', file: 'rubik-latin-700-normal', weight: '700'},
  {family: 'Rubik', file: 'rubik-latin-800-normal', weight: '800'},
  {family: 'Rubik', file: 'rubik-latin-900-normal', weight: '900'},
  {family: 'Barlow Condensed', file: 'barlow-condensed-latin-600-normal', weight: '600'},
  {family: 'Barlow Condensed', file: 'barlow-condensed-latin-700-normal', weight: '700'},
  {family: 'Barlow Condensed', file: 'barlow-condensed-latin-800-normal', weight: '800'},
  {family: 'Barlow Condensed', file: 'barlow-condensed-latin-800-italic', weight: '800', style: 'italic'},
  {family: 'Barlow Condensed', file: 'barlow-condensed-latin-900-italic', weight: '900', style: 'italic'},
];

let cargadas = false;
export const cargarFuentes = () => {
  if (cargadas) return;
  cargadas = true;
  for (const f of lista) {
    loadFont({
      family: f.family,
      url: staticFile(`fonts/${f.file}.woff2`),
      weight: f.weight,
      style: f.style ?? 'normal',
    }).catch((e) => console.error('No se pudo cargar la fuente', f.file, e));
  }
};

export const FUENTE = {
  inter: 'Inter, sans-serif',
  bebas: '"Bebas Neue", Impact, sans-serif',
  playfair: '"Playfair Display", Georgia, serif',
  rubik: 'Rubik, sans-serif',
  barlow: '"Barlow Condensed", sans-serif',
};
