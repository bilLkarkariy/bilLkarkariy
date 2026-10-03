import React from 'react';
import {AbsoluteFill, Easing, interpolate, interpolateColors, random, useCurrentFrame} from 'remotion';
import {C, F} from '../theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.bezier(0.65, 0, 0.35, 1);

// Fiche recomposée de l'article (titre, revue, date exacts ; corps abstrait).
const W = 1040;
const H = 1500;
const COL = 420;
const GAP = 40;
const LINE = 30;
const BODY_Y = 640;
const ROWS = 26;
// la dernière phrase : fin de la ligne 24 + toute la ligne 25 de la colonne 2
const LAST = [
  {row: 24, x0: 0.42, x1: 1},
  {row: 25, x0: 0, x1: 0.62},
];
const lastY = BODY_Y + 24 * LINE;
const target = {x: 80 + COL + GAP + COL * 0.5, y: lastY + LINE * 0.6};

function bars(col: number, lastColor: string) {
  const out: React.ReactNode[] = [];
  for (let r = 0; r < ROWS; r++) {
    const isLast = col === 1 && r >= 24;
    const paraEnd = random(`p${col}-${r}`) < 0.12;
    const w = isLast ? (r === 24 ? 1 : 0.62) : paraEnd ? 0.35 + random(`w${col}-${r}`) * 0.4 : 0.9 + random(`w${col}-${r}`) * 0.1;
    out.push(
      <rect
        key={`${col}-${r}`}
        x={80 + col * (COL + GAP)}
        y={BODY_Y + r * LINE}
        width={COL * w}
        height={9}
        rx={2}
        fill={isLast ? lastColor : C.bars}
      />,
    );
  }
  return out;
}

export type CardCues = {scroll: number; mark: number; button: number; redact: number; end: number; extra: number};

export const Card: React.FC<CardCues> = ({scroll, mark, button, redact, end, extra}) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [0, 16], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const m = interpolate(frame, [scroll, scroll + 38], [0, 1], {...clamp, easing: inOut});
  const k = interpolate(m, [0, 1], [0.92, 1.55]) * interpolate(frame, [redact, end], [1, 1.06], clamp);
  const fx = interpolate(m, [0, 1], [W / 2, target.x]);
  const fy = interpolate(m, [0, 1], [470, target.y]);
  const tx = 960 - fx * k;
  const ty = 540 - fy * k + (1 - enter) * 500;

  const markP = interpolate(frame, [mark, mark + 12], [0, 1], {...clamp, easing: inOut});
  const btnP = interpolate(frame, [button, button + 10], [0, 1], clamp);
  const lastInk = interpolateColors(markP, [0, 1], [C.bars, '#7D786F']);
  const red = LAST.map((_, i) =>
    interpolate(frame, [redact + i * 9, redact + i * 9 + 11], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)}),
  );
  const extraO = interpolate(frame, [extra, extra + 8], [0, 1], clamp);
  const finO = interpolate(frame, [redact + 18, redact + 26], [0, 1], clamp);

  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute',
          width: W,
          height: H,
          transformOrigin: '0 0',
          transform: `translate(${tx}px, ${ty}px) scale(${k})`,
          opacity: enter,
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: C.sheet,
            boxShadow: '0 30px 60px rgba(30,28,24,0.18), 0 2px 6px rgba(30,28,24,0.12)',
          }}
        />
        <div style={{position: 'absolute', left: 80, right: 80, top: 78, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline'}}>
          <span style={{fontFamily: F.serif, fontSize: 40, letterSpacing: '0.32em', fontWeight: 500, color: C.ink}}>SCIENCE</span>
          <span style={{fontFamily: F.mono, fontSize: 19, letterSpacing: '0.12em', color: C.ink}}>4 JUILLET 2014</span>
        </div>
        <div style={{position: 'absolute', left: 80, right: 80, top: 142, height: 2, background: C.ink}} />
        <div style={{position: 'absolute', left: 80, top: 166, fontFamily: F.mono, fontSize: 17, letterSpacing: '0.12em', color: C.inkSoft}}>
          VOL. 345 · N° 6192 · P. 75-77
        </div>
        <div style={{position: 'absolute', left: 80, right: 80, top: 222, fontFamily: F.serif, fontWeight: 500, fontSize: 66, lineHeight: 1.04, color: C.ink}}>
          Just think: The challenges of the disengaged mind
        </div>
        <div style={{position: 'absolute', left: 80, right: 80, top: 400, fontFamily: F.serif, fontStyle: 'italic', fontSize: 27, color: C.ink}}>
          Timothy D. Wilson, David A. Reinhard, Erin C. Westgate, Daniel T. Gilbert et al.
        </div>
        <svg width={W + 400} height={H} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
          {[0, 1, 2, 3, 4].map((r) => (
            <rect key={r} x={80} y={478 + r * 26} width={(W - 160) * (r === 4 ? 0.55 : 1)} height={11} rx={2} fill="#BDB8AE" />
          ))}
          {bars(0, C.bars)}
          {bars(1, lastInk)}
          {/* repère : la dernière phrase */}
          <path
            d={`M ${80 + 2 * COL + GAP + 34} ${lastY - 8} L ${80 + 2 * COL + GAP + 46} ${lastY - 8} L ${80 + 2 * COL + GAP + 46} ${lastY + LINE + 18} L ${80 + 2 * COL + GAP + 34} ${lastY + LINE + 18}`}
            fill="none"
            stroke={C.ink}
            strokeWidth={1.4}
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - markP}
          />
          <line
            x1={80 + 2 * COL + GAP + 46}
            x2={80 + 2 * COL + GAP + 46 + 70 * markP}
            y1={lastY + LINE / 2 + 5}
            y2={lastY + LINE / 2 + 5}
            stroke={C.ink}
            strokeWidth={1.4}
          />
          {/* le bouton, relié à la phrase */}
          <g opacity={btnP}>
            <line
              x1={80 + 2 * COL + GAP + 120}
              x2={80 + 2 * COL + GAP + 120}
              y1={lastY + LINE / 2 + 20}
              y2={lastY + LINE / 2 + 20 + 70 * btnP}
              stroke={C.ink}
              strokeWidth={1.2}
              strokeDasharray="4 4"
            />
            <rect x={80 + 2 * COL + GAP + 104} y={lastY + LINE / 2 + 94} width={32} height={26} fill={C.sheet} stroke={C.ink} strokeWidth={1.2} />
            <circle cx={80 + 2 * COL + GAP + 120} cy={lastY + LINE / 2 + 107} r={9} fill={C.red} />
          </g>
          {/* caviardage : on garde la promesse jusqu'à la fin */}
          {LAST.map((l, i) => (
            <rect
              key={i}
              x={80 + COL + GAP + COL * l.x0 - 4}
              y={BODY_Y + l.row * LINE - 8}
              width={(COL * (l.x1 - l.x0) + 8) * red[i]}
              height={25}
              fill={C.ink}
            />
          ))}
        </svg>
        <div
          style={{
            position: 'absolute',
            left: 80 + 2 * COL + GAP + 124,
            top: lastY + LINE / 2 - 6,
            fontFamily: F.mono,
            fontSize: 14,
            letterSpacing: '0.14em',
            color: C.ink,
            whiteSpace: 'nowrap',
            opacity: markP,
          }}
        >
          DERNIÈRE PHRASE
        </div>
        <div
          style={{
            position: 'absolute',
            left: 80 + COL + GAP,
            top: BODY_Y + ROWS * LINE + 16,
            fontFamily: F.mono,
            fontSize: 14,
            letterSpacing: '0.14em',
            color: C.ink,
            whiteSpace: 'nowrap',
            display: 'flex',
            gap: 22,
          }}
        >
          <span style={{opacity: finO}}>→ À LA FIN</span>
          <span style={{opacity: extraO}}>+ 2 MIN D'EXERCICE</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
