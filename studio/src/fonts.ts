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

const handle = delayRender('Chargement des polices');
Promise.all(
  faces.map(([family, src, desc]) =>
    new FontFace(family, `url(${staticFile(src)})`, desc).load().then((f) => {
      document.fonts.add(f);
    }),
  ),
).then(() => continueRender(handle));
