import {useText} from '../i18n';
import React, {useMemo} from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F} from '../theme';

// Scènes dessinées de la partie 3 (le film qui part en vrille, Harvard, Pascal) :
// papier, encre, une personne = un point. Rouge = la fuite ; l'écran du téléphone, une lumière froide.

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.bezier(0.65, 0, 0.35, 1);
const SCREEN = '#CFE0FF'; // la lumière d'un écran
const SCREEN_GLOW = 'rgba(160,196,255,';

const Mono: React.FC<{x: number; y: number; o?: number; size?: number; color?: string; align?: 'left' | 'center'; children: React.ReactNode}> = ({
  x,
  y,
  o = 1,
  size = 20,
  color = C.ink,
  align = 'center',
  children,
}) => (
  <div
    style={{
      position: 'absolute',
      left: align === 'center' ? x - 500 : x,
      width: align === 'center' ? 1000 : undefined,
      top: y,
      textAlign: align,
      opacity: o,
      fontFamily: F.mono,
      fontSize: size,
      letterSpacing: '0.16em',
      color,
      whiteSpace: 'nowrap',
    }}
  >
    {children}
  </div>
);

/** Gribouillis : une marche au hasard lissée, qui part dans tous les sens (Catmull-Rom → Bézier). */
function scribble(seed: string, x0: number, y0: number, n: number, step: number, turn: number, box: [number, number, number, number]) {
  let x = x0;
  let y = y0;
  let a = random(seed) * Math.PI * 2;
  const P: [number, number][] = [[x, y]];
  for (let i = 0; i < n; i++) {
    a += (random(`${seed}-a${i}`) - 0.5) * turn;
    const s = step * (0.6 + random(`${seed}-s${i}`) * 0.8);
    let nx = x + Math.cos(a) * s;
    let ny = y + Math.sin(a) * s;
    if (nx < box[0] || nx > box[2]) {
      a = Math.PI - a;
      nx = Math.max(box[0], Math.min(box[2], nx));
    }
    if (ny < box[1] || ny > box[3]) {
      a = -a;
      ny = Math.max(box[1], Math.min(box[3], ny));
    }
    x = nx;
    y = ny;
    P.push([x, y]);
  }
  let d = `M ${P[0][0]} ${P[0][1]}`;
  for (let i = 0; i < P.length - 1; i++) {
    const p0 = P[Math.max(0, i - 1)];
    const p1 = P[i];
    const p2 = P[i + 1];
    const p3 = P[Math.min(P.length - 1, i + 2)];
    d += ` C ${p1[0] + (p2[0] - p0[0]) / 6} ${p1[1] + (p2[1] - p0[1]) / 6}, ${p2[0] - (p3[0] - p1[0]) / 6} ${p2[1] - (p3[1] - p1[1]) / 6}, ${p2[0]} ${p2[1]}`;
  }
  return d;
}

/** Un téléphone vu de face, écran allumé (glow de 0 à 1). */
const Phone: React.FC<{x: number; y: number; w?: number; glow: number; rot?: number; children?: React.ReactNode}> = ({x, y, w = 120, glow, rot = 0, children}) => {
  
  const h = w * 2.05;
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot})`}>
      {glow > 0 && <ellipse cx={0} cy={0} rx={w * 2.2} ry={h * 1.3} fill={`url(#screenGlow)`} opacity={glow} />}
      <rect x={-w / 2} y={-h / 2} width={w} height={h} rx={w * 0.16} fill={C.ink} />
      <rect x={-w / 2 + 7} y={-h / 2 + 7} width={w - 14} height={h - 14} rx={w * 0.11} fill={SCREEN} opacity={0.15 + 0.85 * glow} />
      {children}
    </g>
  );
};

const Defs: React.FC = () => (
  <defs>
    <radialGradient id="screenGlow">
      <stop offset="0%" stopColor={`${SCREEN_GLOW}0.55)`} />
      <stop offset="60%" stopColor={`${SCREEN_GLOW}0.12)`} />
      <stop offset="100%" stopColor={`${SCREEN_GLOW}0)`} />
    </radialGradient>
  </defs>
);

// ── p20 / p27 : la pellicule. Le scénariste écrit les images, le spectateur les regarde ; ─────────
//    quand le scénariste fatigue, le film part dans tous les sens. Le téléphone le coupe.
export type FilmCues = {tired: number; chaos: number; cut?: number; out?: number};

const CELL = 360; // une image de la pellicule
const STRIP_H = 270;

export const FilmStrip: React.FC<FilmCues> = ({tired, chaos, cut, out}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 18, stiffness: 90}});
  const cutAt = cut ?? Infinity;
  // la pellicule défile, de plus en plus vite ; à la coupe, elle s'arrête net
  const scrollAt = (f: number) => {
    let s = 0;
    for (let k = 0; k < Math.min(f, cutAt); k++) s += 5 + 9 * interpolate(k, [chaos, chaos + 40], [0, 1], clamp);
    return s;
  };
  const scroll = scrollAt(frame);
  const wob = interpolate(frame, [tired, tired + 30], [0, 1], clamp); // le trait du scénariste tremble
  const vrille = Math.min(interpolate(frame, [chaos, chaos + 45], [0, 1], {...clamp, easing: Easing.in(Easing.quad)}), cut !== undefined && frame >= cut ? 0.25 : 1);
  const t = frame / fps;
  // forme de la bande : droite, puis une onde qui grandit et s'emballe
  const waveY = (x: number) => 540 + vrille * (Math.sin(x / 140 - t * 7) * 120 + Math.sin(x / 61 + t * 3) * 40);
  const slope = (x: number) => (Math.atan2(waveY(x + 4) - waveY(x - 4), 8) * 180) / Math.PI;
  const PEN_X = 1240;
  const EYE_X = 640;
  const cells = [];
  const first = Math.floor((scroll - 200) / CELL);
  for (let i = first; i < first + 8; i++) {
    const cx = i * CELL - scroll + CELL / 2 + 80;
    if (cx < -CELL || cx > 1920 + CELL) continue;
    cells.push({i, cx});
  }
  const cutO = cut === undefined ? 0 : interpolate(frame, [cut - 8, cut], [0, 1], {...clamp, easing: inOut});
  const fall = cut === undefined ? 0 : interpolate(frame, [cut, cut + 30], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  const scr = useMemo(() => scribble('vrille', PEN_X, 540, 120, 70, 1.9, [60, 80, 1860, 1000]), []);
  const scrP = interpolate(frame, [chaos, chaos + 45], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  const scrDraw = Math.min(scrP, cut !== undefined ? interpolate(cut, [chaos, chaos + 45], [0, 1], {...clamp, easing: Easing.out(Easing.quad)}) : 1); // coupé net
  // la bande elle-même, d'un seul tenant le long de l'onde (les images se posent dessus)
  const band = (x0: number, x1: number, dy: number, rot: number) => {
    const pts: string[] = [];
    for (let x = x0; x <= x1; x += 16) pts.push(`${x} ${waveY(x) + dy}`);
    return <path d={`M ${pts.join(' L ')}`} fill="none" stroke={C.ink} strokeWidth={STRIP_H} transform={rot ? `rotate(${rot} 960 540)` : undefined} />;
  };
  const o = out === undefined ? 1 : interpolate(frame, [out, out + 10], [1, 0], clamp);
  return (
    <AbsoluteFill style={{opacity: o * Math.min(1, enter * 1.4)}}>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Defs />
        <g transform={`translate(0 ${(1 - enter) * 300})`}>
          {cut === undefined ? band(-40, 1960, 0, 0) : [band(-40, 960, 0, 0), band(960, 1960, fall * 700, fall * 18)]}
          {cells.map(({i, cx}) => {
            const right = cx > 960; // à droite de la coupe : la pellicule tombe
            const dy = cut !== undefined && right ? fall * 700 : 0;
            const rot = cut !== undefined && right ? fall * 18 : 0;
            const y = waveY(cx) + dy;
            // le dessin de l'image : écrit quand elle passe sous le crayon
            const drawn = interpolate(cx, [PEN_X - 120, PEN_X + 40], [1, 0], clamp);
            const j = wob * (i % 2 ? 1 : -1);
            const jit = (k: number) => (random(`j${i}-${k}`) - 0.5) * 26 * wob;
            const walker = ((i * 37) % 100) / 100;
            return (
              <g key={i} transform={`translate(${cx} ${y}) rotate(${slope(cx) + rot})`}>
                <rect x={-CELL / 2} y={-STRIP_H / 2} width={CELL + 1} height={STRIP_H} fill={C.ink} />
                {[0, 1, 2, 3, 4, 5].map((k) => (
                  <g key={k}>
                    <rect x={-CELL / 2 + 18 + k * 58} y={-STRIP_H / 2 + 12} width={28} height={18} rx={4} fill={C.paper} />
                    <rect x={-CELL / 2 + 18 + k * 58} y={STRIP_H / 2 - 30} width={28} height={18} rx={4} fill={C.paper} />
                  </g>
                ))}
                <rect x={-CELL / 2 + 16} y={-STRIP_H / 2 + 44} width={CELL - 32} height={STRIP_H - 88} rx={6} fill={C.sheet} />
                {/* une plage : l'horizon, le soleil, quelqu'un qui marche (l'exemple de l'article) */}
                <g stroke={C.ink} strokeWidth={3} fill="none" strokeLinecap="round" opacity={drawn}>
                  <path d={`M ${-CELL / 2 + 40} ${30 + jit(1)} Q 0 ${22 + jit(2) + j * 10} ${CELL / 2 - 40} ${30 + jit(3)}`} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - drawn} />
                  <circle cx={70 + jit(4)} cy={-30 + jit(5)} r={20 + wob * 6} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - drawn} />
                  <path d={`M ${-CELL / 2 + 60} ${62 + jit(6)} q 30 -10 60 0 t 60 0 t 60 0 t 60 0`} strokeWidth={2} opacity={0.6} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - drawn} />
                </g>
                <circle cx={-120 + walker * 200 + jit(7)} cy={14} r={11 * drawn} fill={C.ink} />
              </g>
            );
          })}
          {/* le crayon du scénariste, l'œil du spectateur */}
          <g transform={`translate(${PEN_X + (random(`p${Math.floor(frame / 2)}`) - 0.5) * 18 * wob} ${waveY(PEN_X) - STRIP_H / 2 - 90}) rotate(${28 + wob * 14 * Math.sin(frame * 0.9)})`} opacity={1 - vrille * 0.6}>
            <rect x={-9} y={-120} width={18} height={110} fill={C.sheet} stroke={C.ink} strokeWidth={2.5} />
            <path d="M -9 -10 L 0 16 L 9 -10 Z" fill={C.sheet} stroke={C.ink} strokeWidth={2.5} strokeLinejoin="round" />
            <path d="M -3 6 L 0 16 L 3 6 Z" fill={C.ink} />
            <rect x={-9} y={-132} width={18} height={14} fill={C.ink} />
          </g>
          <g transform={`translate(${EYE_X} ${waveY(EYE_X) - STRIP_H / 2 - 70})`} opacity={1 - vrille * 0.6}>
            <path d="M -46 0 Q 0 -34 46 0 Q 0 34 -46 0 Z" fill={C.sheet} stroke={C.ink} strokeWidth={2.5} />
            <circle cx={(random(`e${Math.floor(frame / 3)}`) - 0.5) * 16 * vrille} cy={0} r={13} fill={C.ink} />
          </g>
          {/* quand le scénariste lâche : le trait s'échappe des images */}
          {frame >= chaos && (
            <path d={scr} fill="none" stroke={C.ink} strokeWidth={4} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - scrDraw} />
          )}
          {/* le téléphone tombe et coupe la pellicule */}
          {cut !== undefined && cutO > 0 && (
            <Phone x={960} y={interpolate(cutO, [0, 1], [-260, 540])} w={150} glow={interpolate(frame, [cut, cut + 10], [0, 1], clamp)}>
              <circle cx={56} cy={-136} r={17 * spring({frame: frame - cut - 6, fps, config: {damping: 9, stiffness: 220}})} fill={C.red} />
            </Phone>
          )}
        </g>
      </svg>
      <Mono x={PEN_X} y={waveY(PEN_X) - STRIP_H / 2 - 270} o={(1 - vrille) * interpolate(frame, [6, 14], [0, 1], clamp)}>{tx("SCÉNARISTE")}</Mono>
      <Mono x={EYE_X} y={waveY(EYE_X) - STRIP_H / 2 - 150} o={(1 - vrille) * interpolate(frame, [10, 18], [0, 1], clamp)}>{tx("SPECTATEUR")}</Mono>
    </AbsoluteFill>
  );
};

// ── p21 : la file d'attente à la boulangerie ────────────────────────────────────────────────────
export type QueueCues = {file: number; three: number; you: number; hand: number; decide: number};

export const Queue: React.FC<QueueCues> = ({file, three, you, hand, decide}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const draw = (s: number, len = 16) => interpolate(frame, [s, s + len], [0, 1], {...clamp, easing: inOut});
  const GROUND = 660;
  const shop = draw(0, 22);
  const people = [1260, 1100, 940];
  const me = {x: 720, y: GROUND - 46};
  const pop = (s: number) => spring({frame: frame - s, fps, config: {damping: 11, stiffness: 190}});
  const phoneS = spring({frame: frame - hand, fps, config: {damping: 13, stiffness: 160}});
  const glow = interpolate(frame, [hand + 4, hand + 14], [0, 1], clamp);
  const bubble = spring({frame: frame - decide, fps, config: {damping: 12, stiffness: 170}});
  // l'attente : les autres avancent d'un cran, très lentement
  const creep = interpolate(frame, [three, three + 120], [0, 1], clamp) * 14;
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Defs />
        {/* la boutique : vitrine, store festonné, comptoir */}
        <g stroke={C.ink} strokeWidth={3} fill="none" strokeLinejoin="round" opacity={shop}>
          <line x1={120} y1={GROUND} x2={1800} y2={GROUND} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - shop} />
          <path d={`M 1400 ${GROUND} V 240 H 1760 V ${GROUND}`} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - shop} />
          <path d="M 1380 240 L 1400 170 H 1760 L 1780 240" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - shop} />
          <path
            d={`M 1380 240 ${[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(() => `a 20 20 0 0 0 40 0`).join(' ')}`}
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - shop}
          />
          <rect x={1440} y={370} width={280} height={150} strokeWidth={2.5} opacity={shop} />
          <path d={`M 1470 500 q 30 -50 60 0 M 1550 500 q 30 -60 70 0 M 1640 500 q 20 -40 50 0`} strokeWidth={2.5} opacity={shop} />
        </g>
        <foreignObject x={1400} y={178} width={360} height={60}>
          <div style={{fontFamily: F.mono, fontSize: 22, letterSpacing: '0.24em', textAlign: 'center', color: C.ink, opacity: shop, lineHeight: '60px'}}>{tx("BOULANGERIE")}</div>
        </foreignObject>
        {/* trois personnes devant toi */}
        {people.map((x, k) => {
          const s = pop(file + 4 + k * 4);
          return (
            <g key={k} transform={`translate(${x + creep} ${GROUND - 46})`}>
              <circle r={34 * s} fill={C.ink} />
            </g>
          );
        })}
        {/* toi */}
        <g transform={`translate(${me.x + creep * 0.6} ${me.y})`}>
          <circle r={34 * pop(you - 4)} fill={C.ink} />
          <circle r={50 * pop(you)} fill="none" stroke={C.ink} strokeWidth={2} strokeDasharray="4 7" opacity={pop(you)} />
          {/* la main est déjà dans la poche : le téléphone sort, s'allume */}
          <g opacity={Math.min(1, phoneS * 2)} transform={`translate(${46 * phoneS} ${-40 - 70 * phoneS})`}>
            <Phone x={0} y={0} w={44} glow={glow} rot={-8} />
          </g>
          {/* … et la décision arrive après coup */}
          <g transform={`translate(-70 ${-150}) scale(${bubble})`} opacity={bubble}>
            <circle cx={30} cy={64} r={6} fill="none" stroke={C.ink} strokeWidth={2} />
            <circle cx={16} cy={40} r={10} fill="none" stroke={C.ink} strokeWidth={2} />
            <ellipse cx={-26} cy={-6} rx={64} ry={42} fill={C.sheet} stroke={C.ink} strokeWidth={2.5} />
            <text x={-26} y={10} textAnchor="middle" fontFamily="Garamond, serif" fontSize={48} fill={C.ink}>
              {tx("?")}
            </text>
          </g>
        </g>
      </svg>
      {people.map((x, k) => (
        <Mono key={k} x={x + creep} y={GROUND + 26} size={18} o={interpolate(frame, [three + k * 6, three + k * 6 + 6], [0, 1], clamp)}>
          {String(3 - k)}
        </Mono>
      ))}
      <Mono x={me.x} y={GROUND + 26} size={18} o={interpolate(frame, [you, you + 6], [0, 1], clamp)}>{tx("TOI")}</Mono>
    </AbsoluteFill>
  );
};

// ── p26 : l'ascenseur. Vingt secondes : le plafond, le sol, puis l'écran ────────────────────────
export type ElevatorCues = {twenty: number; ceiling: number; floor: number; screen: number};

export const Elevator: React.FC<ElevatorCues> = ({twenty, ceiling, floor, screen}) => {
  
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const draw = (s: number, len = 16) => interpolate(frame, [s, s + len], [0, 1], {...clamp, easing: inOut});
  const box = {x: 660, y: 150, w: 600, h: 780};
  const cab = draw(0, 20);
  const me = {x: 960, y: 640};
  const look = (s: number, len = 8) => interpolate(frame, [s, s + len], [0, 1], {...clamp, easing: inOut});
  const up = look(ceiling) * (1 - look(floor));
  const down = look(floor) * (1 - look(screen));
  const toPhone = look(screen);
  const eyeX = toPhone * 14;
  const eyeY = -up * 24 + down * 24 + toPhone * 16;
  const headY = -up * 12 + down * 10 + toPhone * 6;
  const phoneS = spring({frame: frame - screen + 4, fps, config: {damping: 13, stiffness: 160}});
  const glow = interpolate(frame, [screen, screen + 10], [0, 1], clamp);
  const ceilingLit = interpolate(frame, [ceiling, ceiling + 6, floor, floor + 6], [0, 1, 1, 0], clamp);
  const floorLit = interpolate(frame, [floor, floor + 6, screen, screen + 6], [0, 1, 1, 0], clamp);
  // le temps qui passe : vingt secondes, et l'étage
  const prog = interpolate(frame, [twenty, durationInFrames - 6], [0, 1], clamp);
  const lvl = prog > 0.98 ? '4' : '3';
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Defs />
        <g stroke={C.ink} strokeWidth={3} fill="none" opacity={cab}>
          <rect x={box.x} y={box.y} width={box.w} height={box.h} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - cab} />
          {/* plafonnier, plancher, main courante */}
          <line x1={box.x + 160} y1={box.y + 26} x2={box.x + box.w - 160} y2={box.y + 26} strokeWidth={6} opacity={0.3 + 0.7 * ceilingLit} />
          <line x1={box.x} y1={box.y + box.h - 60} x2={box.x + box.w} y2={box.y + box.h - 60} strokeWidth={2} opacity={0.4 + 0.6 * floorLit} />
          <line x1={box.x + 30} y1={box.y + 420} x2={box.x + box.w - 30} y2={box.y + 420} strokeWidth={2} opacity={0.5} />
        </g>
        {/* le cadran d'étage */}
        <g opacity={cab}>
          <rect x={box.x + box.w / 2 - 70} y={box.y - 96} width={140} height={70} rx={8} fill={C.ink} />
          <text x={box.x + box.w / 2 - 22} y={box.y - 46} textAnchor="middle" fontFamily="'Plex Mono', monospace" fontSize={40} fill={C.red}>
            {lvl}
          </text>
          <path d={`M ${box.x + box.w / 2 + 22} ${box.y - 48} l 14 -18 l 14 18`} stroke={C.red} strokeWidth={3} fill="none" opacity={frame % 20 < 12 ? 1 : 0.3} />
          <rect x={box.x} y={box.y + box.h + 30} width={box.w} height={4} fill={C.inkFaint} />
          <rect x={box.x} y={box.y + box.h + 30} width={box.w * prog} height={4} fill={C.ink} />
        </g>
        {/* toi : un point, deux yeux qui cherchent où se poser */}
        {/* le tableau de boutons */}
        <g opacity={cab}>
          <rect x={box.x + box.w - 90} y={box.y + 330} width={50} height={190} rx={6} fill="none" stroke={C.ink} strokeWidth={2} />
          {[0, 1, 2, 3, 4, 5].map((k) => (
            <circle key={k} cx={box.x + box.w - 65} cy={box.y + 356 + k * 28} r={8} fill={k === 1 ? C.red : 'none'} stroke={C.ink} strokeWidth={2} />
          ))}
        </g>
        <g transform={`translate(${me.x} ${me.y + headY})`}>
          <circle r={74 * draw(4, 10)} fill={C.ink} />
          <circle cx={-22 + eyeX} cy={-12 + eyeY} r={9} fill={C.sheet} opacity={draw(8, 6)} />
          <circle cx={22 + eyeX} cy={-12 + eyeY} r={9} fill={C.sheet} opacity={draw(8, 6)} />
        </g>
        <g opacity={Math.min(1, phoneS * 2)}>
          <Phone x={me.x + 60} y={me.y + 140 - 40 * phoneS} w={70} glow={glow} rot={-12} />
        </g>
      </svg>
      <Mono x={box.x + box.w / 2} y={box.y + box.h + 50} size={18} o={interpolate(frame, [twenty, twenty + 8], [0, 1], clamp)}>
        {`0:${String(Math.round(prog * 20)).padStart(2, '0')} / 0:20`}
      </Mono>
    </AbsoluteFill>
  );
};

// ── p28 / p31 : le compteur des années (2025 → 1670, puis 1670 → 2025 : « plus de 350 ans ») ────
export type YearsCues = {from: number; to: number; start: number; len: number; label?: string; labelAt?: number; sub?: string; subAt?: number; out?: number};

const Digit: React.FC<{v: number; size: number}> = ({v, size}) => (
  <div style={{height: size, overflow: 'hidden', display: 'inline-block', width: size * 0.62, position: 'relative'}}>
    <div style={{transform: `translateY(${-v * size}px)`}}>
      {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0].map((d, i) => (
        <div key={i} style={{height: size, lineHeight: `${size}px`, textAlign: 'center'}}>
          {d}
        </div>
      ))}
    </div>
  </div>
);

export const Years: React.FC<YearsCues> = ({from, to, start, len, label, labelAt = 0, sub, subAt = 0, out}) => {
  
  const frame = useCurrentFrame();
  const q = interpolate(frame, [start, start + len], [0, 1], {...clamp, easing: inOut});
  const y = from + (to - from) * q;
  const size = 230;
  // compteur kilométrique : chaque chiffre roule en continu sur le précédent
  const digits = [1000, 100, 10, 1].map((p) => {
    const v = (y / p) % 10;
    const frac = p === 1 ? v : Math.floor(v) + Math.max(0, ((y % p) - (p - 1)) / 1);
    return Math.min(9.999, frac) % 10;
  });
  const o = interpolate(frame, [0, 8], [0, 1], clamp) * (out === undefined ? 1 : interpolate(frame, [out, out + 10], [1, 0], clamp));
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: o}}>
      <div style={{fontFamily: F.serif, fontSize: size, color: C.ink, display: 'flex', fontVariantNumeric: 'lining-nums tabular-nums', lineHeight: 1}}>
        {digits.map((d, i) => (
          <Digit key={i} v={d} size={size} />
        ))}
      </div>
      {label && (
        <div style={{fontFamily: F.mono, fontSize: 24, letterSpacing: '0.2em', color: C.ink, marginTop: 34, opacity: interpolate(frame, [labelAt, labelAt + 8], [0, 1], clamp)}}>
          {label}
        </div>
      )}
      {sub && (
        <div
          style={{
            fontFamily: F.serif,
            fontStyle: 'italic',
            fontSize: 64,
            color: C.red,
            marginTop: 18,
            opacity: interpolate(frame, [subAt, subAt + 8], [0, 1], clamp),
            transform: `translateY(${interpolate(frame, [subAt, subAt + 10], [16, 0], {...clamp, easing: Easing.out(Easing.cubic)})}px)`,
          }}
        >
          {sub}
        </div>
      )}
    </AbsoluteFill>
  );
};

// ── p31 : « Il l'a mise dans ta poche, ouverte jour et nuit. » La porte est dans le téléphone ─────
export type PocketCues = {phone: number; door: number; pocket: number; open: number};

export const PocketDoor: React.FC<PocketCues> = ({phone, door, pocket, open}) => {
  
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const draw = (s: number, len = 16) => interpolate(frame, [s, s + len], [0, 1], {...clamp, easing: inOut});
  const ph = spring({frame: frame - phone, fps, config: {damping: 15, stiffness: 120}});
  const sink = interpolate(frame, [pocket, pocket + 18], [0, 1], {...clamp, easing: inOut});
  const swing = interpolate(frame, [door, door + 14], [0, 0.35], {...clamp, easing: inOut}) + interpolate(frame, [open, open + 16], [0, 0.55], {...clamp, easing: inOut});
  // jour et nuit : le ciel derrière la porte tourne
  const cyc = interpolate(frame, [open, open + 50], [0, 2], clamp);
  const day = 0.5 + 0.5 * Math.cos(cyc * Math.PI * 2);
  const W = 300;
  const H = W * 2.05;
  const cx = 960;
  const cy = 540 + sink * 170;
  const dw = 150;
  const dh = 300;
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Defs />
        <g opacity={Math.min(1, ph * 1.5)} transform={`translate(0 ${(1 - ph) * 140})`}>
          <ellipse cx={cx} cy={cy} rx={W * 1.4} ry={H * 0.8} fill="url(#screenGlow)" opacity={swing * 1.2} />
          <rect x={cx - W / 2} y={cy - H / 2} width={W} height={H} rx={42} fill={C.ink} />
          <rect x={cx - W / 2 + 14} y={cy - H / 2 + 14} width={W - 28} height={H - 28} rx={30} fill={C.sheet} />
          {/* derrière la porte : le jour, la nuit, le jour… */}
          <rect x={cx - dw / 2} y={cy - dh / 2 + 40} width={dw} height={dh} fill={day > 0.5 ? SCREEN : '#2B3550'} />
          <circle cx={cx - dw / 2 + dw * (0.2 + 0.6 * (cyc % 1))} cy={cy - dh / 2 + 120 - Math.sin((cyc % 1) * Math.PI) * 60} r={18} fill={day > 0.5 ? '#F3C26B' : '#E8E6E0'} opacity={cyc > 0 ? 1 : 0} />
          {/* le battant (vu de face, il pivote sur sa charnière gauche) */}
          <g transform={`translate(${cx - dw / 2} ${cy - dh / 2 + 40}) scale(${1 - swing * 1.1} 1)`}>
            <rect x={0} y={0} width={dw} height={dh} fill={C.sheet} stroke={C.ink} strokeWidth={3} />
            <circle cx={dw - 22} cy={dh / 2 + 10} r={7} fill={C.ink} />
          </g>
          <rect x={cx - dw / 2} y={cy - dh / 2 + 40} width={dw} height={dh} fill="none" stroke={C.ink} strokeWidth={4} opacity={draw(door - 10, 12)} />
        </g>
        {/* la poche : le téléphone y glisse, la porte reste ouverte */}
        <g stroke={C.ink} strokeWidth={3} fill={C.paperWarm} strokeLinejoin="round" opacity={draw(pocket - 6, 10)}>
          <path d={`M ${cx - 300} 700 L ${cx + 300} 700 L ${cx + 270} 1000 Q ${cx} 1060 ${cx - 270} 1000 Z`} />
          <path d={`M ${cx - 280} 724 L ${cx + 280} 724`} strokeDasharray="10 9" strokeWidth={2} fill="none" />
        </g>
      </svg>
    </AbsoluteFill>
  );
};

// ── p32 : trois heures du matin ─────────────────────────────────────────────────────────────────
export type NightCues = {wake: number; spin: number; reflex: number; screen: number};

export const Night: React.FC<NightCues> = ({wake, spin, reflex, screen}) => {
  
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dark = interpolate(frame, [0, 12], [0, 1], clamp);
  const draw = (s: number, len = 16) => interpolate(frame, [s, s + len], [0, 1], {...clamp, easing: inOut});
  const LINE = 'rgba(232,230,224,0.75)';
  const head = {x: 760, y: 610};
  const eyes = interpolate(frame, [wake, wake + 6], [0, 1], clamp);
  const spinA = interpolate(frame, [spin, spin + 60], [0, 1], clamp);
  // ça tourne : une spirale qui s'enroule au-dessus de la tête, sans fin
  const ph = (frame - spin) * 0.22;
  const loops = Array.from({length: 120}, (_, k) => {
    const t = (k / 119) * Math.PI * 7;
    return `${head.x - 150 + t * 14 + Math.cos(t + ph) * 44} ${head.y - 210 + Math.sin(t + ph) * 30}`;
  }).join(' L ');
  const phoneS = spring({frame: frame - reflex, fps, config: {damping: 14, stiffness: 150}});
  const glow = interpolate(frame, [screen - 6, screen + 6], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: C.night, opacity: dark * 0.94}} />
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Defs />
        {/* la lumière de l'écran sur le lit */}
        <ellipse cx={1100} cy={620} rx={900} ry={520} fill="url(#screenGlow)" opacity={glow * 1.3} />
        {/* le lit, l'oreiller */}
        <g stroke={LINE} strokeWidth={3} fill="none" opacity={draw(2, 18)}>
          <path d="M 520 560 V 800 M 520 700 H 1500 V 800 M 520 640 H 1500" />
          <rect x={590} y={570} width={200} height={70} rx={30} />
        </g>
        {/* la couverture et toi */}
        <path d="M 820 640 Q 1000 580 1180 640 T 1500 640" stroke={LINE} strokeWidth={3} fill="none" opacity={draw(6, 18)} />
        <circle cx={head.x} cy={head.y} r={42} fill="#3A3833" stroke={LINE} strokeWidth={2} opacity={draw(4, 10)} />
        <circle cx={head.x - 12} cy={head.y - 8} r={6 * eyes} fill="#E8E6E0" />
        <circle cx={head.x + 12} cy={head.y - 8} r={6 * eyes} fill="#E8E6E0" />
        {/* ça tourne dans ta tête */}
        <path d={`M ${loops}`} stroke={LINE} strokeWidth={2.5} fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - spinA} opacity={1 - glow * 0.7} />
        {/* le téléphone, sur la table de nuit */}
        <g opacity={Math.min(1, phoneS * 2)}>
          <Phone x={1360} y={520 - 30 * phoneS} w={64} glow={glow} rot={8} />
        </g>
      </svg>
      <Mono x={1360} y={190} size={64} color={`rgba(232,230,224,${0.25 + 0.6 * draw(0, 10)})`}>
        03:00
      </Mono>
    </AbsoluteFill>
  );
};

// ── p27 : « une vingtaine de sessions sur smartphone par jour » : la journée, et chaque session ─────
export const DayTicks: React.FC<{start: number; n?: number; y?: number}> = ({start, n = 20, y = 760}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const X0 = 300;
  const X1 = 1620;
  const Y = y;
  const ruler = interpolate(frame, [start - 10, start + 6], [0, 1], {...clamp, easing: inOut});
  // des heures plausibles, surtout le jour (7 h → 23 h), une la nuit
  const hours = useMemo(
    () => Array.from({length: n}, (_, k) => (k === n - 1 ? 3.1 : 7 + (16 * (k + random(`h${k}`) * 0.8)) / (n - 1))).sort((a, b) => a - b),
    [n],
  );
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <line x1={X0} y1={Y} x2={X0 + (X1 - X0) * ruler} y2={Y} stroke={C.ink} strokeWidth={2} />
        {[0, 6, 12, 18, 24].map((h) => (
          <line key={h} x1={X0 + ((X1 - X0) * h) / 24} y1={Y - 8} x2={X0 + ((X1 - X0) * h) / 24} y2={Y + 8} stroke={C.ink} strokeWidth={2} opacity={ruler} />
        ))}
        {hours.map((h, k) => {
          const s = spring({frame: frame - start - k * 2, fps, config: {damping: 10, stiffness: 240}});
          const x = X0 + ((X1 - X0) * h) / 24;
          return <rect key={k} x={x - 7} y={Y - 50 * s} width={14} height={30 * s} rx={3} fill={C.red} opacity={Math.min(1, s * 2)} />;
        })}
      </svg>
      {[0, 6, 12, 18, 24].map((h) => (
        <Mono key={h} x={X0 + ((X1 - X0) * h) / 24} y={Y + 22} size={16} o={ruler}>
          {tx('{h} H').replace('{h}', String(h))}
        </Mono>
      ))}
    </AbsoluteFill>
  );
};
