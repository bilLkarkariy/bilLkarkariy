import {continueRender, delayRender, staticFile} from 'remotion';

const ARABIC_RANGE = 'U+0600-06FF, U+0750-077F, U+08A0-08FF, U+FB50-FDFF, U+FE70-FEFF';
// À même taille de police, l'arabe d'Amiri paraît plus petit que le latin : +10 % à la place de Garamond,
// +30 % à la place de Plex Mono (les petites étiquettes en capitales espacées). Hauteurs de ligne
// ramenées à celles de Garamond pour que les blocs gardent leur place.
const ARABIC_METRICS = (sizeAdjust: string) => ({sizeAdjust, ascentOverride: '100%', descentOverride: '30%'}) as FontFaceDescriptors;

const faces: [string, string, FontFaceDescriptors][] = [
  ['Garamond', 'fonts/EBGaramond.ttf', {weight: '400 800', style: 'normal'}],
  ['Garamond', 'fonts/EBGaramond-Italic.ttf', {weight: '400 800', style: 'italic'}],
  ['Plex Mono', 'fonts/PlexMono-Light.ttf', {weight: '300'}],
  ['Plex Mono', 'fonts/PlexMono-Regular.ttf', {weight: '400'}],
  ['Plex Mono', 'fonts/PlexMono-Medium.ttf', {weight: '500'}],
  ['Amiri Quran', 'fonts/AmiriQuran-Regular.ttf', {weight: '400'}], // le verset (texte uthmani)
  ['Amiri', 'fonts/Amiri-Regular.ttf', {weight: '400'}], // les mots arabes (khalwa, dhikr)
  // Version arabe : les lettres arabes écrites en « Garamond » ou en « Plex Mono » s'affichent en Amiri
  // (plage Unicode arabe seulement : le français et l'anglais ne changent pas). Mêmes graisses et styles
  // que les faces latines ci-dessus, sinon le navigateur ne les associe pas. Amiri n'existe ici qu'en
  // romain : déclaré aussi pour l'italique et le gras, rien n'est penché ni grossi à la main.
  ...([
    ['Garamond', '400 800', 'normal'],
    ['Garamond', '400 800', 'italic'],
    ['Plex Mono', '300', 'normal'],
    ['Plex Mono', '400', 'normal'],
    ['Plex Mono', '500', 'normal'],
  ] as const).map(([family, weight, style]): [string, string, FontFaceDescriptors] => [
    family,
    'fonts/Amiri-Regular.ttf',
    {weight, style, unicodeRange: ARABIC_RANGE, ...ARABIC_METRICS(family === 'Plex Mono' ? '130%' : '110%')},
  ]),
];

const handle = delayRender('Chargement des polices');
Promise.all(
  faces.map(([family, src, desc]) =>
    new FontFace(family, `url(${staticFile(src)})`, desc).load().then((f) => {
      document.fonts.add(f);
    }),
  ),
).then(() => continueRender(handle));
