import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {CitationProps, lineDur} from '../components/Citation';
import {CAP} from '../captures';

// Outils communs aux parties du montage (src/V01.tsx, src/montage/p*.tsx).

/** Une vraie page posée sur le bureau, de l'image `from` à l'image `to` (absolues). `sound` : bruit de pose. */
export type Cit = {from: number; to: number; sound?: string} & CitationProps;

/** Un bruitage : [nom, image, volume, durée max en images (coupé en fondu)]. */
export type Sfx = [string, number, number, number?];

/** Le son des pages : feuille (ou manuscrit) qui se pose, un frottement par ligne surlignée (de la longueur
 *  du trait), une carte qui glisse quand une fiche sort. */
export const citSfx = (cits: Cit[]): Sfx[] =>
  cits.flatMap((c) => [
    [c.sound ?? 'paper', c.from, 0.55] as Sfx,
    ...(c.marks ?? []).flatMap((m) => {
      let t0 = c.from + m.at;
      return CAP[c.cap].highlights[m.i].rects.map((r) => {
        const d = lineDur(r);
        const s: Sfx = ['marker', t0, 0.2, d + 3];
        t0 += d;
        return s;
      });
    }),
    ...(c.marks ?? [])
      .filter((m) => m.redact !== undefined && m.redact >= 0)
      .flatMap((m) => CAP[c.cap].highlights[m.i].rects.map((_, j) => ['marker', c.from + (m.redact as number) + j * 9, 0.3, 12] as Sfx)),
    ...[...(c.marks ?? []).flatMap((m) => (m.note ? [m.note] : [])), ...(c.notes ?? [])].map((n) => ['fiche', c.from + n.at, 0.45] as Sfx),
  ]);

export const Fade: React.FC<{from: number; len: number; out?: boolean; children: React.ReactNode}> = ({from, len, out, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [from, from + len], out ? [1, 0] : [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};
