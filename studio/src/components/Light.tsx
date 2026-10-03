import React from 'react';
import {AbsoluteFill, getInputProps, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// La lumière de la pièce : une fenêtre en haut à gauche. Le soleil glisse lentement
// sur le bureau pendant toute la vidéo, ses montants posent une ombre floue sur le papier.
export const WindowLight: React.FC<{strength?: number}> = ({strength = 1}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const drift = interpolate(frame, [0, durationInFrames], [0, 320]);
  // fenêtre à deux battants, imposte : les vitres sont des trous dans l'ombre
  const panes = [
    [70, 70, 560, 900],
    [690, 70, 560, 900],
    [70, 1030, 560, 420],
    [690, 1030, 560, 420],
  ];
  const holes = panes.map(([x, y, w, h]) => `M ${x} ${y} h ${w} v ${h} h ${-w} Z`).join(' ');
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill
        style={{
          background: 'radial-gradient(ellipse 85% 95% at 16% 8%, rgba(255,234,200,0.6), rgba(255,234,200,0) 62%)',
          mixBlendMode: 'soft-light',
          opacity: strength,
        }}
      />
      <AbsoluteFill
        style={{
          background: 'radial-gradient(ellipse 95% 85% at 92% 100%, rgba(38,32,26,0.2), rgba(38,32,26,0) 70%)',
          mixBlendMode: 'multiply',
          opacity: strength,
        }}
      />
      <svg width={1920} height={1080} style={{position: 'absolute', mixBlendMode: 'multiply', opacity: 0.1 * strength, filter: 'blur(16px)'}}>
        <g transform={`translate(${-420 + drift} -300) skewX(-30) rotate(6) scale(1.25)`}>
          <path d={`M -2000 -2000 H 4000 V 4000 H -2000 Z ${holes}`} fill="rgb(40,34,28)" fillRule="evenodd" />
        </g>
      </svg>
    </AbsoluteFill>
  );
};

/** Les éléments dessinés sont des papiers découpés posés sur le bureau : ils portent une ombre. */
export const Lift: React.FC<{children: React.ReactNode; d?: number}> = ({children, d = 1}) => (
  <AbsoluteFill style={{filter: `drop-shadow(${4 * d}px ${7 * d}px ${5 * d}px rgba(30,28,24,0.22))`}}>{children}</AbsoluteFill>
);

const NO3D = Boolean(getInputProps().no3d);

/**
 * Plan 3D rendu par tools/plans3d.py (public/3d/<dir>/f0001.png…), une image sur `step` :
 * on fond les deux voisines (mouvements lents, ça ne se voit pas).
 */
export const Shot3D: React.FC<{dir: string; frames: number; step?: number; children?: React.ReactNode}> = ({dir, frames, step = 2, children}) => {
  const frame = useCurrentFrame();
  const last = 1 + Math.floor((frames - 1) / step) * step;
  const n = Math.min(last, frame + 1);
  const n0 = 1 + Math.floor((n - 1) / step) * step;
  const n1 = Math.min(last, n0 + step);
  const t = n1 === n0 ? 0 : (n - n0) / step;
  const file = (k: number) => staticFile(`3d/${dir}/f${String(k).padStart(4, '0')}.png`);
  return (
    <AbsoluteFill>
      {NO3D ? (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontFamily: 'monospace', fontSize: 40, color: '#999'}}>
          3D · {dir} · {n}
        </AbsoluteFill>
      ) : (
        <AbsoluteFill style={{isolation: 'isolate'}}>
          <Img src={file(n0)} style={{position: 'absolute', opacity: 1 - t}} />
          {t > 0.001 && <Img src={file(n1)} style={{position: 'absolute', opacity: t, mixBlendMode: 'plus-lighter'}} />}
        </AbsoluteFill>
      )}
      {children}
    </AbsoluteFill>
  );
};
