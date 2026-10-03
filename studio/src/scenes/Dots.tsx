import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F} from '../theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export type DotsCues = {presses: number[]; pct: number; before: number; pay: number};

/** « Deux hommes sur trois ont appuyé. » Chaque personne = un point, comme partout. */
export const Dots: React.FC<DotsCues> = ({presses, pct, before, pay}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const xs = [760, 960, 1160];
  const y = 560;

  const pctIn = interpolate(frame, [pct, pct + 9], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const beforeIn = interpolate(frame, [before, before + 8], [0, 1], clamp);
  const payIn = interpolate(frame, [pay, pay + 10], [0, 1], clamp);
  const bracket = interpolate(frame, [before, before + 14], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});

  const {durationInFrames} = useVideoConfig();
  const drift = interpolate(frame, [0, durationInFrames], [1, 1.035]);
  return (
    <AbsoluteFill style={{transform: `scale(${drift})`}}>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        {xs.map((x, i) => {
          const s = spring({frame: frame - i * 4, fps, config: {damping: 13, stiffness: 160}});
          const p = presses[i];
          const pressed = p !== undefined && frame >= p;
          const ring = p === undefined ? 0 : interpolate(frame, [p, p + 14], [0, 1], clamp);
          const squash = p === undefined ? 1 : 1 - 0.18 * interpolate(frame, [p, p + 2, p + 8], [0, 1, 0], clamp);
          return (
            <g key={i}>
              {pressed && ring < 1 && (
                <circle cx={x} cy={y} r={40 + ring * 46} fill="none" stroke={C.red} strokeWidth={3 * (1 - ring)} />
              )}
              <circle cx={x} cy={y} r={38 * s * squash} fill={pressed ? C.red : C.ink} />
            </g>
          );
        })}
        {/* accolade : « tous avaient dit qu'ils paieraient » */}
        <path
          d={`M 730 ${y - 78} L 730 ${y - 92} L 1190 ${y - 92} L 1190 ${y - 78}`}
          fill="none"
          stroke={C.ink}
          strokeWidth={1.6}
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - bracket}
        />
      </svg>
      <div
        style={{
          position: 'absolute',
          top: y - 160,
          width: '100%',
          textAlign: 'center',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'baseline',
          gap: 18,
        }}
      >
        <span style={{opacity: beforeIn, fontFamily: F.mono, fontSize: 20, letterSpacing: '0.16em', color: C.inkSoft}}>
          JUSTE AVANT
        </span>
        <span style={{opacity: payIn, fontFamily: F.serif, fontStyle: 'italic', fontSize: 42, color: C.ink}}>
          prêts à payer pour ne plus jamais la sentir
        </span>
      </div>
      <div
        style={{
          position: 'absolute',
          top: 690,
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'baseline',
          gap: 26,
          opacity: pctIn,
          transform: `translateY(${(1 - pctIn) * 18}px)`,
        }}
      >
        <span style={{fontFamily: F.mono, fontWeight: 500, fontSize: 150, color: C.ink, letterSpacing: '-0.02em'}}>
          67<span style={{marginLeft: '0.08em'}}>%</span>
        </span>
        <span style={{fontFamily: F.serif, fontStyle: 'italic', fontSize: 50, color: C.ink}}>des hommes</span>
      </div>
    </AbsoluteFill>
  );
};
