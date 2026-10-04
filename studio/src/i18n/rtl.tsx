import React from 'react';
import {Lang, isRtl} from '.';

// Versions de droite à gauche (ourdou) : un seul cadre autour de la composition, sans toucher au français ni à
// l'anglais (ils ne passent jamais par ici).
// - dir="rtl" : sens de lecture, alignement de départ à droite, mots et puces qui s'enchaînent de droite à gauche ;
//   deux nombres séparés (« 07 / 40 », « 0:07 / 0:20 », « 12 / 18 ») passent par <Ltr> pour ne pas s'inverser ;
// - les polices latines du montage (Garamond, Plex Mono) passent la main à Noto Nastaliq Urdu pour l'écriture
//   arabe (les chiffres et le latin restent dans leur police) ; pas d'italique ni d'interlettrage forcé : le nastaliq
//   est une écriture liée, l'espacement des lettres la casserait ;
// - les étiquettes SVG (carte) gardent leur point d'ancrage à gauche du texte, comme en français.
export const URDU = "'Noto Nastaliq Urdu'";

const css = (scope: string) => `
.${scope} * { letter-spacing: normal !important; font-style: normal !important; }
.${scope} [style*="Garamond"], .${scope} [font-family*="Garamond"] { font-family: 'Garamond', ${URDU}, serif !important; }
.${scope} [style*="Plex Mono"], .${scope} [font-family*="Plex Mono"] { font-family: 'Plex Mono', ${URDU}, monospace !important; }
.${scope} svg text { direction: ltr; }
`;

/** Un nombre composé (« 07 / 40 ») lu de gauche à droite au milieu de l'ourdou ; ailleurs, le texte tel quel. */
export const Ltr: React.FC<{rtl: boolean; children: React.ReactNode}> = ({rtl, children}) =>
  rtl ? <span style={{direction: 'ltr', unicodeBidi: 'isolate'}}>{children}</span> : <>{children}</>;

export const RtlScope: React.FC<{lang: Lang; children: React.ReactNode}> = ({lang, children}) => {
  if (!isRtl(lang)) return <>{children}</>;
  const scope = `rtl-${lang}`;
  return (
    <div className={scope} dir="rtl" lang={lang} style={{position: 'absolute', inset: 0}}>
      <style>{css(scope)}</style>
      {children}
    </div>
  );
};
