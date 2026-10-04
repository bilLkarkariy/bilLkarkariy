import {useLang, useText} from '../i18n';
import React from 'react';
import {AbsoluteFill, getInputProps, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import rendered from '../data/renders3d.json';

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

// --props '{"no3d":true}' : tous les plans 3D en carton ; '{"no3d":["vide","khalwa"]}' : seulement ceux-là
const NO3D_PROP = getInputProps().no3d as boolean | string[] | undefined;
const no3d = (dir: string) => (Array.isArray(NO3D_PROP) ? NO3D_PROP.includes(dir) : Boolean(NO3D_PROP));

/**
 * Plan 3D rendu par tools/plans3d.py (public/3d/<dir>/f0001.png…), une image sur `step` :
 * on fond les deux voisines (mouvements lents, ça ne se voit pas).
 */
export const Shot3D: React.FC<{dir: string; frames: number; step?: number; label?: string; children?: React.ReactNode}> = ({
  dir,
  frames,
  step = 2,
  label,
  children,
}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  // (si la voix a bougé depuis le rendu, on s'arrête sur la dernière image rendue)
  const done = (rendered as Record<string, {frames: number; step: number}>)[dir];
  // (le pas réellement rendu prime : un plan recalculé image par image n'a plus rien à fondre)
  if (done?.step) step = Math.min(step, done.step);
  const last = 1 + Math.floor((Math.min(frames, done?.frames ?? frames) - 1) / step) * step;
  const n = Math.min(last, frame + 1);
  const n0 = 1 + Math.floor((n - 1) / step) * step;
  const n1 = Math.min(last, n0 + step);
  const t = n1 === n0 ? 0 : (n - n0) / step;
  const file = (k: number) => staticFile(`3d/${dir}/f${String(k).padStart(4, '0')}.png`);
  return (
    <AbsoluteFill>
      {(useLang() === 'en' || no3d(dir)) ? (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 18, color: '#22211E', textAlign: 'center'}}>
          <div style={{fontFamily: "'Plex Mono', monospace", fontSize: 20, letterSpacing: '0.16em', background: '#F2D64B', padding: '6px 12px'}}>{tx("PLAN 3D · EN COURS DE RENDU")}</div>
          <div style={{fontFamily: "'Garamond', serif", fontStyle: 'italic', fontSize: 40, maxWidth: 1300}}>{label ?? dir}</div>
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
