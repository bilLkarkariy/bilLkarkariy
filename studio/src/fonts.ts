import {continueRender, delayRender, staticFile} from 'remotion';

const faces: [string, string, FontFaceDescriptors][] = [
  ['Garamond', 'fonts/EBGaramond.ttf', {weight: '400 800', style: 'normal'}],
  ['Garamond', 'fonts/EBGaramond-Italic.ttf', {weight: '400 800', style: 'italic'}],
  ['Plex Mono', 'fonts/PlexMono-Light.ttf', {weight: '300'}],
  ['Plex Mono', 'fonts/PlexMono-Regular.ttf', {weight: '400'}],
  ['Plex Mono', 'fonts/PlexMono-Medium.ttf', {weight: '500'}],
  ['Amiri Quran', 'fonts/AmiriQuran-Regular.ttf', {weight: '400'}], // le verset (texte uthmani)
  ['Amiri', 'fonts/Amiri-Regular.ttf', {weight: '400'}], // les mots arabes (khalwa, dhikr)
];

// L'ourdou (nastaliq), relais de Garamond et Plex Mono dans les versions de droite à gauche (src/i18n/rtl.tsx).
// Ses métriques d'origine (1,90 em au-dessus, 0,60 em dessous) doubleraient la hauteur des lignes : on les ramène
// près de celles de Garamond, les hampes débordent sans être coupées. Si le fichier manque (pas encore posé sur
// le Mac), les autres versions ne doivent pas attendre : ce chargement-là ne bloque jamais le rendu.
const optional: [string, string, FontFaceDescriptors][] = [
  ['Noto Nastaliq Urdu', 'fonts/NotoNastaliqUrdu-Regular.ttf', {weight: '400', ascentOverride: '130%', descentOverride: '50%', lineGapOverride: '0%'}],
];

const load = ([family, src, desc]: [string, string, FontFaceDescriptors]) =>
  new FontFace(family, `url(${staticFile(src)})`, desc).load().then((f) => {
    document.fonts.add(f);
  });

const handle = delayRender('Chargement des polices');
Promise.all([
  ...faces.map(load),
  ...optional.map((face) => load(face).catch(() => console.warn(`Police absente : ${face[1]}`))),
]).then(() => continueRender(handle));
