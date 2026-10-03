import React from 'react';
import {AbsoluteFill, Easing, getInputProps, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {C, F} from '../theme';

// Rendu Blender : f0001..f0150. STEP = 2 tant que seules les images impaires
// existent ; on fond alors les deux voisines (mouvement lent, ça ne se voit pas).
const STEP = 2;
const LAST = 149;
const TOP_REACHED = 137; // index où la caméra est exactement à la verticale

const file = (n: number) => staticFile(`3d/maquette/f${String(n).padStart(4, '0')}.png`);

const Frames: React.FC<{idx: number}> = ({idx}) => {
  const n = Math.min(LAST, idx + 1);
  const n0 = Math.min(LAST, 1 + Math.floor((n - 1) / STEP) * STEP);
  const n1 = Math.min(LAST, n0 + STEP);
  const t = n1 === n0 ? 0 : (n - n0) / STEP;
  return (
    <AbsoluteFill style={{isolation: 'isolate'}}>
      <Img src={file(n0)} style={{position: 'absolute', opacity: 1 - t}} />
      {t > 0.001 && <Img src={file(n1)} style={{position: 'absolute', opacity: t, mixBlendMode: 'plus-lighter'}} />}
    </AbsoluteFill>
  );
};

const Tag: React.FC<{label: string; from: number; strikeAt: number; y: number}> = ({label, from, strikeAt, y}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [from, from + 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const strike = interpolate(frame, [strikeAt, strikeAt + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div style={{position: 'absolute', left: 1572, top: y, opacity: o, display: 'flex', alignItems: 'center', gap: 14}}>
      <div style={{width: 30, height: 1.5, background: C.inkSoft}} />
      <div style={{position: 'relative', fontFamily: F.mono, fontSize: 21, letterSpacing: '0.14em', color: C.ink}}>
        {label}
        <div
          style={{
            position: 'absolute',
            left: -4,
            top: '52%',
            height: 2.5,
            width: `calc(${strike * 100}% + 8px)`,
            background: C.ink,
          }}
        />
      </div>
    </div>
  );
};

/**
 * Maquette 3D (axonométrie -> vue de dessus) + annotations d'architecte.
 * reachTop : image locale où la vue de dessus doit être atteinte.
 */
export const Maquette: React.FC<{reachTop: number; phone: number; read: number}> = ({reachTop, phone, read}) => {
  const frame = useCurrentFrame();
  const idx = interpolate(frame, [0, reachTop], [0, TOP_REACHED], {extrapolateRight: 'clamp'});
  const cart = interpolate(frame, [6, 16], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      {getInputProps().noMaquette ? null : <Frames idx={idx} />}
      <Tag label="TÉLÉPHONE" from={phone - 4} strikeAt={phone + 6} y={430} />
      <Tag label="LECTURE" from={read - 4} strikeAt={read + 6} y={490} />
      {/* cartouche */}
      <div
        style={{
          position: 'absolute',
          right: 34,
          bottom: 28,
          opacity: cart,
          border: `1.5px solid ${C.ink}`,
          fontFamily: F.mono,
          color: C.ink,
          display: 'grid',
          gridTemplateColumns: 'auto auto',
        }}
      >
        <div style={{padding: '8px 14px', fontSize: 15, letterSpacing: '0.12em', borderRight: `1.5px solid ${C.ink}`}}>
          SEUL · SANS RIEN
        </div>
        <div style={{padding: '2px 14px', fontSize: 30, fontWeight: 500, letterSpacing: '0.04em'}}>15:00</div>
      </div>
    </AbsoluteFill>
  );
};
