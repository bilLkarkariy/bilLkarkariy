import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F, ROOM, S, px, py} from '../theme';

// Scènes dessinées de la partie 2 (L'expérience, suite). Même langage que le hook :
// papier, encre, une personne = un point, rouge = la fuite.

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.bezier(0.65, 0, 0.35, 1);
const after = (frame: number, z: number, len: number, v: number) => (frame < z ? 0 : interpolate(frame, [z, z + len], [v, 0], clamp));

function zapPath(seed: string, x0: number, y0: number, x1: number, y1: number, amp = 30) {
  const n = 8;
  const nx = -(y1 - y0);
  const ny = x1 - x0;
  const len = Math.hypot(nx, ny) || 1;
  let d = `M ${x0} ${y0}`;
  for (let i = 1; i < n; i++) {
    const t = i / n;
    const off = (random(`${seed}-${i}`) - 0.5) * amp;
    d += ` L ${x0 + (x1 - x0) * t + (nx / len) * off} ${y0 + (y1 - y0) * t + (ny / len) * off}`;
  }
  return d + ` L ${x1} ${y1}`;
}

const Label: React.FC<{x: number; y: number; o: number; children: React.ReactNode; size?: number; align?: 'left' | 'center'}> = ({
  x,
  y,
  o,
  children,
  size = 20,
  align = 'left',
}) => (
  <div
    style={{
      position: 'absolute',
      left: align === 'center' ? x - 400 : x,
      width: align === 'center' ? 800 : undefined,
      textAlign: align,
      top: y,
      opacity: o,
      fontFamily: F.mono,
      fontSize: size,
      letterSpacing: '0.16em',
      color: C.ink,
      whiteSpace: 'nowrap',
    }}
  >
    {children}
  </div>
);

// ── p9 : la décharge d'essai, « comme de l'électricité statique » ───────────────────────────────
export type StaticCues = {shock: number; handle: number; label: number; spark: number};

export const Static: React.FC<StaticCues> = ({shock, handle, label, spark}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const me = {x: 700, y: 560};
  const box = {x: 1180, y: 560};
  const dotS = spring({frame, fps, config: {damping: 13}});
  const cable = interpolate(frame, [4, 20], [0, 1], {...clamp, easing: inOut});
  const boxO = interpolate(frame, [8, 16], [0, 1], clamp) * interpolate(frame, [handle, handle + 8], [1, 0], clamp);
  const zapOn = frame >= shock && frame < shock + 9;
  const hit = after(frame, shock, 10, 1);
  const flash = after(frame, shock, 5, 0.22) + after(frame, spark, 5, 0.18);
  const ring = interpolate(frame, [shock, shock + 16], [0, 1], clamp);
  const hS = spring({frame: frame - handle, fps, config: {damping: 14}});
  const sparkOn = frame >= spark && frame < spark + 10;
  const tagO = interpolate(frame, [shock + 4, shock + 12], [0, 1], clamp) * interpolate(frame, [handle, handle + 6], [1, 0], clamp);
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <defs>
          <filter id="glow2" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {/* le câble et l'appareil */}
        <g opacity={boxO}>
          <path
            d={`M ${me.x + 40} ${me.y} C ${me.x + 200} ${me.y + 90}, ${box.x - 220} ${box.y + 90}, ${box.x - 70} ${box.y}`}
            fill="none"
            stroke={C.ink}
            strokeWidth={2}
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - cable}
          />
          <rect x={box.x - 70} y={box.y - 48} width={140} height={96} fill={C.sheet} stroke={C.ink} strokeWidth={2} />
          <circle cx={box.x - 22} cy={box.y} r={20} fill="none" stroke={C.ink} strokeWidth={2} />
          <line x1={box.x - 22} y1={box.y} x2={box.x - 10} y2={box.y - 14} stroke={C.ink} strokeWidth={2} />
          <rect x={box.x + 14} y={box.y - 18} width={38} height={10} fill={C.ink} />
          <rect x={box.x + 14} y={box.y + 4} width={26} height={10} fill={C.inkFaint} />
        </g>
        {zapOn && (
          <path
            d={zapPath(`s${Math.floor(frame / 2)}`, box.x - 70, box.y, me.x + 30, me.y)}
            fill="none"
            stroke={C.red}
            strokeWidth={3}
            strokeLinejoin="bevel"
            filter="url(#glow2)"
          />
        )}
        {frame >= shock && ring < 1 && <circle cx={me.x} cy={me.y} r={40 + ring * 60} fill="none" stroke={C.red} strokeWidth={3 * (1 - ring)} />}
        {/* une poignée de porte, en coupe : le petit choc qu'on connaît tous */}
        <g transform={`translate(${box.x} ${box.y}) scale(${hS})`} opacity={hS}>
          <rect x={-22} y={-90} width={44} height={180} rx={6} fill={C.sheet} stroke={C.ink} strokeWidth={2} />
          <circle cx={0} cy={-6} r={13} fill={C.sheet} stroke={C.ink} strokeWidth={2} />
          <path d="M 0 -18 L -150 -18 Q -168 -18 -168 0 L -168 6 Q -168 12 -160 12 L -10 12" fill={C.sheet} stroke={C.ink} strokeWidth={2} />
          <circle cx={0} cy={50} r={7} fill="none" stroke={C.ink} strokeWidth={2} />
        </g>
        {sparkOn &&
          [0, 1, 2, 3, 4].map((i) => {
            const a = (i / 5) * Math.PI * 2 + random(`a${Math.floor(frame / 2)}-${i}`);
            const x0 = box.x - 178;
            const y0 = box.y - 4;
            return (
              <path
                key={i}
                d={zapPath(`k${Math.floor(frame / 2)}-${i}`, x0, y0, x0 + Math.cos(a) * 46, y0 + Math.sin(a) * 46, 14)}
                fill="none"
                stroke={C.red}
                strokeWidth={2.5}
                filter="url(#glow2)"
              />
            );
          })}
        <circle cx={me.x} cy={me.y} r={34 * dotS * (1 + 0.3 * hit)} fill={C.ink} />
      </svg>
      <Label x={me.x} y={me.y + 70} o={dotS} align="center" size={18}>
        PARTICIPANT
      </Label>
      <Label x={me.x} y={me.y - 120} o={tagO} align="center">
        1 DÉCHARGE D'ESSAI
      </Label>
      <Label x={box.x - 84} y={box.y + 120} o={interpolate(frame, [label, label + 8], [0, 1], clamp)} align="center">
        ≈ ÉLECTRICITÉ STATIQUE
      </Label>
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    </AbsoluteFill>
  );
};

// ── p11-p12 : 18 hommes, 24 femmes, puis un seul homme ──────────────────────────────────────────
export type GroupsCues = {men: number; menN: number; women: number; womenN: number};

const grid = (n: number, cols: number, cx: number, cy: number, gap: number) =>
  Array.from({length: n}, (_, i) => {
    const r = Math.floor(i / cols);
    const c = i % cols;
    const rows = Math.ceil(n / cols);
    return {x: cx + (c - (cols - 1) / 2) * gap, y: cy + (r - (rows - 1) / 2) * gap};
  });

const pick = (n: number, k: number, seed: string) =>
  new Set(
    Array.from({length: n}, (_, i) => i)
      .sort((a, b) => random(`${seed}${a}`) - random(`${seed}${b}`))
      .slice(0, k),
  );

export const Groups: React.FC<GroupsCues> = ({men, menN, women, womenN}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const M = grid(18, 6, 560, 560, 74);
  const W = grid(24, 6, 1360, 560, 74);
  const mRed = pick(18, 12, 'h');
  const wRed = pick(24, 6, 'f');
  const order = (set: Set<number>) => [...set].sort((a, b) => a - b);
  const dot = (p: {x: number; y: number}, i: number, red: boolean, at: number, rank: number, key: string) => {
    const s = spring({frame: frame - i * 0.8, fps, config: {damping: 14, stiffness: 170}});
    const on = red && frame >= at + rank * 1.5;
    const ring = on ? interpolate(frame, [at + rank * 1.5, at + rank * 1.5 + 12], [0, 1], clamp) : 1;
    return (
      <g key={key}>
        {on && ring < 1 && <circle cx={p.x} cy={p.y} r={24 + ring * 26} fill="none" stroke={C.red} strokeWidth={2.4 * (1 - ring)} />}
        <circle cx={p.x} cy={p.y} r={22 * s} fill={on ? C.red : C.ink} opacity={on ? 1 : 0.85} />
      </g>
    );
  };
  const mOrder = order(mRed);
  const wOrder = order(wRed);
  const numIn = (f: number) => interpolate(frame, [f, f + 8], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const num = (f: number, x: number, a: number, b: number) => (
    <div
      style={{
        position: 'absolute',
        left: x - 300,
        width: 600,
        top: 770,
        textAlign: 'center',
        opacity: numIn(f),
        transform: `translateY(${(1 - numIn(f)) * 16}px)`,
      }}
    >
      <span style={{fontFamily: F.mono, fontWeight: 500, fontSize: 96, color: C.ink}}>
        <span style={{color: C.red}}>{a}</span>
        <span style={{color: C.inkSoft}}> / {b}</span>
      </span>
    </div>
  );
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        {M.map((p, i) => dot(p, i, mRed.has(i), men, mOrder.indexOf(i), `m${i}`))}
        {W.map((p, i) => dot(p, i + 6, wRed.has(i), women, wOrder.indexOf(i), `w${i}`))}
      </svg>
      <Label x={560} y={350} o={interpolate(frame, [0, 8], [0, 1], clamp)} align="center">
        HOMMES
      </Label>
      <Label x={1360} y={310} o={interpolate(frame, [6, 14], [0, 1], clamp)} align="center">
        FEMMES
      </Label>
      {num(menN, 560, 12, 18)}
      {num(womenN, 1360, 6, 24)}
    </AbsoluteFill>
  );
};

// ── p16 : « c'est le labo, c'est intimidant » (le salon qui suit est en 3D : tools/plans3d.py salon) ─
export const Lab: React.FC<{intimidating: number}> = ({intimidating}) => {
  const frame = useCurrentFrame();
  const hw = ROOM.w / 2;
  const hd = ROOM.d / 2;
  const t = ROOM.wall;
  const walls = [
    [-hw - t, hd, hw + t, hd + t],
    [-hw - t, -hd - t, -hw, hd],
    [hw, -hd - t, hw + t, hd],
    [-hw, -hd - t, ROOM.door[0], -hd],
    [ROOM.door[1], -hd - t, hw, -hd],
  ];
  const k = 0.82;
  const o = interpolate(frame, [0, 8], [0, 1], clamp);
  const cam = interpolate(frame, [intimidating, intimidating + 10], [0, 1], clamp);
  const eye = interpolate(frame, [intimidating + 6, intimidating + 30], [0, 1], {...clamp, easing: inOut});
  const lens = {x: px(hw - 0.25), y: py(hd - 0.25)};
  const me = {x: px(ROOM.chair.x), y: py(ROOM.chair.y)};
  return (
    <AbsoluteFill style={{opacity: o}}>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <g transform={`translate(960 560) scale(${k}) translate(-960 -540)`}>
          {walls.map(([x0, y0, x1, y1], i) => (
            <rect key={i} x={px(x0)} y={py(y1)} width={(x1 - x0) * S} height={(y1 - y0) * S} fill={C.ink} />
          ))}
          <line x1={px(ROOM.door[1])} y1={py(-hd)} x2={px(ROOM.door[0])} y2={py(-hd)} stroke={C.ink} strokeWidth={6} />
          <g fill="none" stroke={C.ink} strokeWidth={2}>
            <rect x={px(ROOM.table.x - ROOM.table.w / 2)} y={py(ROOM.table.y + ROOM.table.d / 2)} width={ROOM.table.w * S} height={ROOM.table.d * S} />
            <rect
              x={px(ROOM.chair.x - ROOM.chair.s / 2)}
              y={py(ROOM.chair.y + ROOM.chair.s / 2)}
              width={ROOM.chair.s * S}
              height={ROOM.chair.s * S}
            />
          </g>
          {/* la caméra au plafond, et son champ qui balaie la pièce jusqu'au participant */}
          <g opacity={cam}>
            <path
              d={`M ${lens.x - 30} ${lens.y + 4} L ${me.x - 60} ${me.y - 30} L ${me.x + 50} ${me.y + 60} Z`}
              fill={C.ink}
              opacity={0.07 * eye}
            />
            <g transform={`translate(${lens.x} ${lens.y}) rotate(38)`}>
              <rect x={-18} y={-11} width={36} height={22} fill={C.sheet} stroke={C.ink} strokeWidth={2} />
              <path d="M -18 -5 L -32 -12 L -32 12 L -18 5" fill={C.sheet} stroke={C.ink} strokeWidth={2} />
              <circle cx={11} cy={-5} r={3.5} fill={C.red} opacity={Math.floor(frame / 12) % 2 ? 1 : 0.35} />
            </g>
          </g>
          <circle cx={me.x} cy={me.y} r={15} fill={C.ink} />
        </g>
      </svg>
      <Label x={64} y={52} o={o}>
        LABO · UNIVERSITÉ DE VIRGINIE
      </Label>
    </AbsoluteFill>
  );
};

/** Le minuteur de la consigne, en bas à droite, qui continue de tourner. */
export const Countdown: React.FC<{left: number; o?: number}> = ({left, o = 1}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const l = Math.max(0, left - Math.floor(frame / fps));
  return (
    <div
      style={{
        position: 'absolute',
        right: 64,
        bottom: 52,
        fontFamily: F.mono,
        fontSize: 44,
        fontWeight: 500,
        color: C.ink,
        opacity: o * interpolate(frame, [6, 14], [0, 1], clamp),
        letterSpacing: '0.04em',
      }}
    >
      {String(Math.floor(l / 60)).padStart(2, '0')}:{String(l % 60).padStart(2, '0')}
    </div>
  );
};
