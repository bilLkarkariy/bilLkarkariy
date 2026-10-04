import {useRtl, useText} from '../i18n';
// Les seules captures françaises du montage deviennent des fiches dans la langue de la vidéo (anglais, ourdou).
// Pas de faux fac-similé : les citations sont composées comme du texte, les sources restent en description.
import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {C, F} from '../theme';
import {CitationProps, NoteCard} from './Citation';

const QUOTES: Record<string, string> = {
  pascal_chambre: 'pascal.chamber',
  pascal_solitude: 'pascal.solitude',
};
export const ENGLISH_ONLY_CAPTURES = new Set(['mm_3h', 'mm_mobile', 'arcep_2025', 'pascal_ro139', 'pascal_ro210', ...Object.keys(QUOTES)]);

export const EnglishEvidence: React.FC<CitationProps> = (p) => {
  const tx = useText();
  const rtl = useRtl();
  const f = useCurrentFrame();
  const fade = p.out === undefined ? 1 : interpolate(f, [p.out, p.out + 12], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // Les transcriptions EN occupent le centre ; pas de manuscrit FR derrière.
  if (p.cap.startsWith('pascal_ro')) return null;
  const quote = QUOTES[p.cap] && tx(QUOTES[p.cap]);
  if (quote) return <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity: fade * interpolate(f, [0, 10], [0, 1], {extrapolateRight: 'clamp'})}}>
    <div style={{fontFamily: F.serif, fontSize: 74, fontStyle: 'italic', lineHeight: 1.22, color: C.ink, width: 1480, textAlign: 'center', ...(rtl ? {fontSize: 70, lineHeight: 1.95} : {})}}>“{quote}”</div>
  </AbsoluteFill>;
  const n = p.marks?.find((m) => m.note)?.note;
  if (!n) return null;
  const mobile = p.cap === 'mm_mobile';
  return <AbsoluteFill style={{opacity: fade}}><NoteCard n={{...n, y: undefined}} x={mobile ? 1040 : p.cap === 'arcep_2025' ? 580 : 200} y={320} w={mobile ? 610 : 740} tone={mobile ? 'gold' : 'ink'} /></AbsoluteFill>;
};
