import React, {useMemo} from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F, ROOM, S, px, py} from '../theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.bezier(0.65, 0, 0.35, 1);

/** Trajectoire de l'esprit qui vagabonde : marche aléatoire lissée, dans la pièce. */
function wanderPath(seed: string, x0: number, y0: number, n = 140) {
  let x = x0;
  let y = y0;
  let a = random(seed) * Math.PI * 2;
  const pts: [number, number][] = [[x, y]];
  for (let i = 0; i < n; i++) {
    a += (random(`${seed}-a${i}`) - 0.5) * 1.3;
    const step = 0.06 + random(`${seed}-s${i}`) * 0.05;
    let nx = x + Math.cos(a) * step;
    let ny = y + Math.sin(a) * step;
    const mx = ROOM.w / 2 - 0.22;
    const my = ROOM.d / 2 - 0.22;
    if (Math.abs(nx) > mx) {
      a = Math.PI - a;
      nx = Math.sign(nx) * mx;
    }
    if (Math.abs(ny) > my) {
      a = -a;
      ny = Math.sign(ny) * my;
    }
    x = nx;
    y = ny;
    pts.push([x, y]);
  }
  // Catmull-Rom -> Bézier
  const P = pts.map(([u, v]) => [px(u), py(v)]);
  let d = `M ${P[0][0]} ${P[0][1]}`;
  for (let i = 0; i < P.length - 1; i++) {
    const p0 = P[Math.max(0, i - 1)];
    const p1 = P[i];
    const p2 = P[i + 1];
    const p3 = P[Math.min(P.length - 1, i + 2)];
    d += ` C ${p1[0] + (p2[0] - p0[0]) / 6} ${p1[1] + (p2[1] - p0[1]) / 6}, ${p2[0] - (p3[0] - p1[0]) / 6} ${
      p2[1] - (p3[1] - p1[1]) / 6
    }, ${p2[0]} ${p2[1]}`;
  }
  return d;
}

function zapPath(seed: string, x0: number, y0: number, x1: number, y1: number) {
  const n = 9;
  const nx = -(y1 - y0);
  const ny = x1 - x0;
  const len = Math.hypot(nx, ny);
  let d = `M ${x0} ${y0}`;
  for (let i = 1; i < n; i++) {
    const t = i / n;
    const off = (random(`${seed}-${i}`) - 0.5) * 34;
    d += ` L ${x0 + (x1 - x0) * t + (nx / len) * off} ${y0 + (y1 - y0) * t + (ny / len) * off}`;
  }
  return d + ` L ${x1} ${y1}`;
}

export type PlanCues = {
  dot: number; // « toi »
  wander: number; // « pensées »
  button: number; // « bouton »
  zaps: number[]; // « décharge », « électrique »
  push: number; // début du silence
  pushLen: number;
};

export const Plan: React.FC<PlanCues> = ({dot, wander, button, zaps, push, pushLen}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const draw = (start: number, len = 16) => interpolate(frame, [start, start + len], [0, 1], {...clamp, easing: inOut});

  const hw = ROOM.w / 2;
  const hd = ROOM.d / 2;
  const t = ROOM.wall;
  const {table: tb, chair: ch, button: bt} = ROOM;
  const me = {x: px(ch.x), y: py(ch.y)};
  const btn = {x: px(bt.x), y: py(bt.y)};

  // caméra : poussée lente sur le bouton pendant le silence
  const k = interpolate(frame, [push, push + pushLen], [1, 2.5], {...clamp, easing: inOut});
  const fx = interpolate(frame, [push, push + pushLen], [960, btn.x], {...clamp, easing: inOut});
  const fy = interpolate(frame, [push, push + pushLen], [540, btn.y], {...clamp, easing: inOut});

  const walls = [
    [-hw - t, hd, hw + t, hd + t],
    [-hw - t, -hd - t, -hw, hd],
    [hw, -hd - t, hw + t, hd],
    [-hw, -hd - t, ROOM.door[0], -hd],
    [ROOM.door[1], -hd - t, hw, -hd],
  ];
  const wallsO = draw(0, 8);
  const wallFill = draw(10, 14);
  const furn = draw(2, 18);
  const doorR = (ROOM.door[1] - ROOM.door[0]) * S;
  const hinge = {x: px(ROOM.door[1]), y: py(-hd)};

  const dotS = spring({frame: frame - dot, fps, config: {damping: 12, stiffness: 180}});
  const wanderP = interpolate(frame, [wander, button + 10], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  const btnS = spring({frame: frame - button, fps, config: {damping: 9, stiffness: 200}});
  const path = useMemo(() => wanderPath('esprit', ch.x, ch.y), [ch.x, ch.y]);

  const zapOn = zaps.find((z) => frame >= z && frame < z + 11);
  const after = (z: number, len: number, v: number) => (frame < z ? 0 : interpolate(frame, [z, z + len], [v, 0], clamp));
  const flash = Math.max(...zaps.map((z, i) => after(z, 5, i === 0 ? 0.3 : 0.15)));
  const hit = Math.max(...zaps.map((z) => after(z, 10, 1)));
  const wanderFade = interpolate(frame, [push, push + pushLen * 0.6], [0.55, 0.16], clamp);

  const callout = draw(push + pushLen * 0.45, 18);
  const labelO = interpolate(frame, [push + pushLen * 0.7, push + pushLen * 0.7 + 8], [0, 1], clamp);

  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <g transform={`translate(960 540) scale(${k}) translate(${-fx} ${-fy})`}>
          {/* murs en poché */}
          {/* le contour reprend le trait de la maquette, puis le mur se remplit */}
          <g opacity={wallsO}>
            {walls.map(([x0, y0, x1, y1], i) => (
              <rect
                key={i}
                x={px(x0)}
                y={py(y1)}
                width={(x1 - x0) * S}
                height={(y1 - y0) * S}
                fill={C.ink}
                fillOpacity={wallFill}
                stroke={C.ink}
                strokeWidth={1.5}
              />
            ))}
          </g>
          {/* porte : battant + arc */}
          <g fill="none" stroke={C.ink} strokeWidth={1.6}>
            <path d={`M ${hinge.x} ${hinge.y} L ${hinge.x} ${hinge.y - doorR}`} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - furn} />
            <path
              d={`M ${px(ROOM.door[0])} ${hinge.y} A ${doorR} ${doorR} 0 0 1 ${hinge.x} ${hinge.y - doorR}`}
              pathLength={1}
              strokeDasharray="0.012 0.012"
              strokeDashoffset={0}
              opacity={furn * 0.7}
            />
          </g>
          {/* table + chaise */}
          <g fill="none" stroke={C.ink} strokeWidth={2}>
            <rect
              x={px(tb.x - tb.w / 2)}
              y={py(tb.y + tb.d / 2)}
              width={tb.w * S}
              height={tb.d * S}
              pathLength={1}
              strokeDasharray={1}
              strokeDashoffset={1 - furn}
            />
            <rect
              x={px(ch.x - ch.s / 2)}
              y={py(ch.y + ch.s / 2)}
              width={ch.s * S}
              height={ch.s * S}
              pathLength={1}
              strokeDasharray={1}
              strokeDashoffset={1 - furn}
            />
            <line
              x1={px(ch.x - ch.s / 2)}
              x2={px(ch.x + ch.s / 2)}
              y1={py(ch.y - ch.s / 2) - 7}
              y2={py(ch.y - ch.s / 2) - 7}
              strokeWidth={5}
              opacity={furn}
            />
          </g>
          {/* l'esprit qui part */}
          <path
            d={path}
            fill="none"
            stroke={C.ink}
            strokeWidth={1.6}
            strokeOpacity={wanderFade}
            strokeLinecap="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - wanderP}
          />
          {/* le bouton : seule couleur de l'image */}
          <g transform={`translate(${btn.x} ${btn.y}) scale(${btnS})`}>
            <rect x={-24} y={-19} width={48} height={38} fill={C.sheet} stroke={C.ink} strokeWidth={1.6} />
            <circle r={bt.r * S} fill={C.red} />
          </g>
          {/* décharge */}
          {zapOn !== undefined && (
            <path
              d={zapPath(`z${Math.floor(frame / 2)}`, btn.x, btn.y, me.x, me.y)}
              fill="none"
              stroke={C.red}
              strokeWidth={3}
              strokeLinejoin="bevel"
              filter="url(#glow)"
            />
          )}
          {/* toi */}
          <circle cx={me.x} cy={me.y} r={15 * dotS * (1 + 0.35 * hit)} fill={C.ink} />
          {/* détail A */}
          <circle
            cx={btn.x}
            cy={btn.y}
            r={36}
            fill="none"
            stroke={C.ink}
            strokeWidth={1.2}
            strokeDasharray="5 5"
            opacity={callout}
            transform={`rotate(${-90 + 360 * (1 - callout)} ${btn.x} ${btn.y})`}
          />
        </g>
      </svg>
      {/* légende du détail, hors zoom pour rester nette */}
      <div
        style={{
          position: 'absolute',
          left: 960 + 36 * 2.5 + 30,
          top: 540 - 20,
          opacity: labelO,
          fontFamily: F.mono,
          fontSize: 22,
          letterSpacing: '0.12em',
          color: C.ink,
          display: 'flex',
          alignItems: 'center',
          gap: 14,
        }}
      >
        <div style={{width: 40, height: 1.5, background: C.ink}} />1 PRESSION = 1 DÉCHARGE
      </div>
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    </AbsoluteFill>
  );
};
