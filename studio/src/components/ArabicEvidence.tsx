import {translator} from '../i18n';
// Version arabe : les transcriptions françaises de Pascal (texte imprimé) deviennent une feuille où la
// phrase est composée en arabe, à la place de la transcription. Le manuscrit autographe reste à côté.
// Pas de faux fac-similé : c'est une feuille blanche, sans en-tête ; la source reste dans la description.
import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {C, F} from '../theme';
import type {CitationProps} from './Citation';

const tx = translator('ar');
const quotes: Record<string, string> = {
  pascal_chambre: tx('pascal.chamber'),
  pascal_solitude: tx('pascal.solitude'),
};
export const ARABIC_QUOTES = new Set(Object.keys(quotes));
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const ArabicEvidence: React.FC<CitationProps> = (p) => {
  const f = useCurrentFrame();
  const quote = quotes[p.cap];
  const s = interpolate(f, [0, 12], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const e = p.out === undefined ? 0 : interpolate(f, [p.out, p.out + 12], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  // le passage se surligne en or au moment du premier trait de feutre (comme sur la transcription)
  const markAt = p.marks?.[0]?.at ?? 12;
  const mark = interpolate(f, [markAt, markAt + 14], [0, 1], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        left: p.x,
        top: p.y,
        width: p.width,
        padding: '44px 56px',
        background: C.sheet,
        boxShadow: '18px 30px 40px rgba(20,18,15,0.18), 3px 5px 6px rgba(20,18,15,0.22)',
        opacity: s * (1 - e),
        transform: `translateY(${(1 - s) * -24 - e * 40}px) rotate(${p.tilt ?? 0}deg)`,
        direction: 'rtl',
        fontFamily: F.serif,
        fontSize: 52,
        lineHeight: 1.7,
        color: C.ink,
      }}
    >
      <span
        style={{
          background: `rgba(200,150,46,${(0.38 * mark).toFixed(3)})`,
          boxDecorationBreak: 'clone',
          WebkitBoxDecorationBreak: 'clone',
          padding: '0 6px',
        }}
      >
        «{quote}»
      </span>
    </div>
  );
};
