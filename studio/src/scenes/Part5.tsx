import {useRtl, useText} from '../i18n';
import {Ltr} from '../i18n/rtl';
import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F} from '../theme';

// Scènes de la partie 5 : l'exercice (cinq étapes, racontées, sans minuteur à l'écran),
// l'envie de se lever, le bouton qu'on a dans la poche, la fin.

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.bezier(0.65, 0, 0.35, 1);
const SCREEN = '#CFE0FF';
const q = (frame: number, a: number, len = 8) => interpolate(frame, [a, a + len], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
const draw = (frame: number, a: number, len = 16) => interpolate(frame, [a, a + len], [0, 1], {...clamp, easing: inOut});

/** Lignes alignées à gauche, mot à mot (de droite à gauche : alignées à droite sur le bord de la colonne). */
const RTL_EDGE = 1920 - 760; // bord droit de la colonne de texte, avant les dessins (x ≥ 800)
export const Lines: React.FC<{x: number; y: number; lines: {t: string; at: number; size?: number; italic?: boolean; mono?: boolean; color?: string; out?: number}[]; gap?: number}> = ({
  x,
  y,
  lines,
  gap = 1.32,
}) => {
  const rtl = useRtl();
  const frame = useCurrentFrame();
  let top = y;
  return (
    <AbsoluteFill>
      {lines.map((l, i) => {
        const size = l.size ?? 52;
        const t = top;
        top += size * gap * (rtl ? 1.3 : 1); // le nastaliq a besoin de plus d'interligne
        const o = l.out === undefined ? 1 : interpolate(frame, [l.out, l.out + 8], [1, 0], clamp);
        return (
          <div key={i} style={{position: 'absolute', ...(rtl ? {right: RTL_EDGE} : {left: x}), top: t, opacity: o, whiteSpace: 'nowrap'}}>
            {l.t.split(' ').map((w, k) => {
              const v = q(frame, l.at + k * 2.5, 7);
              return (
                <span
                  key={k}
                  style={{
                    display: 'inline-block',
                    ...(rtl ? {marginLeft: '0.26em'} : {marginRight: '0.26em'}),
                    opacity: v,
                    transform: `translateY(${(1 - v) * 14}px)`,
                    fontFamily: l.mono ? F.mono : F.serif,
                    fontStyle: l.italic ? 'italic' : 'normal',
                    letterSpacing: l.mono ? '0.16em' : undefined,
                    fontSize: size,
                    color: l.color ?? C.ink,
                  }}
                >
                  {w}
                </span>
              );
            })}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Le cadre d'une étape : le numéro, la ligne d'or, « L'EXERCICE · n / 5 ». */
export const StepNum: React.FC<{n: number; out?: number}> = ({n, out}) => {
  const tx = useText();
  const rtl = useRtl();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, config: {damping: 14, stiffness: 140}});
  const o = out === undefined ? 1 : interpolate(frame, [out, out + 8], [1, 0], clamp);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <div style={{position: 'absolute', ...(rtl ? {right: RTL_EDGE} : {left: 150}), top: 150, fontFamily: F.mono, fontSize: 20, letterSpacing: '0.2em', color: C.inkSoft, opacity: q(frame, 2)}}>{tx("L’EXERCICE ·")}{' '}<Ltr rtl={rtl}>{n} / 5</Ltr>
      </div>
      <div style={{position: 'absolute', ...(rtl ? {right: RTL_EDGE - 10} : {left: 140}), top: 190, fontFamily: F.serif, fontSize: 300, lineHeight: 1, color: C.ink, opacity: s, transform: `translateY(${(1 - s) * 40}px)`}}>{n}</div>
      <div style={{position: 'absolute', ...(rtl ? {right: RTL_EDGE} : {left: 150}), top: 520, width: 150 * draw(frame, 6, 14), height: 3, background: C.gold}} />
    </AbsoluteFill>
  );
};

const Phone: React.FC<{x: number; y: number; w?: number; glow?: number; rot?: number; down?: boolean}> = ({x, y, w = 40, glow = 0, rot = 0, down}) => {
  
  const h = w * 2.05;
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot})`}>
      {glow > 0 && <ellipse rx={w * 2.4} ry={h * 1.4} fill="url(#glow5)" opacity={glow} />}
      <rect x={-w / 2} y={-h / 2} width={w} height={h} rx={w * 0.16} fill={C.ink} />
      {!down && <rect x={-w / 2 + 4} y={-h / 2 + 4} width={w - 8} height={h - 8} rx={w * 0.11} fill={SCREEN} opacity={0.2 + 0.8 * glow} />}
    </g>
  );
};

const Glow: React.FC = () => (
  <defs>
    <radialGradient id="glow5">
      <stop offset="0%" stopColor="rgba(160,196,255,0.5)" />
      <stop offset="100%" stopColor="rgba(160,196,255,0)" />
    </radialGradient>
    <radialGradient id="gold5">
      <stop offset="0%" stopColor="rgba(221,170,74,0.55)" />
      <stop offset="100%" stopColor="rgba(221,170,74,0)" />
    </radialGradient>
  </defs>
);

// ── 1 · le téléphone dans une autre pièce ; un minuteur, qui sonnera de loin ─────────────────────
export const StepPhone: React.FC<{phone: number; other: number; notNext: number; timer: number; ring: number}> = ({phone, other, notNext, timer, ring}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const walls = draw(frame, 2, 22);
  const A = {x: 800, y: 330, w: 520, h: 420}; // ta pièce
  const B = {x: 1360, y: 330, w: 380, h: 420}; // l'autre pièce
  const move = interpolate(frame, [other, other + 22], [0, 1], {...clamp, easing: inOut});
  const px = interpolate(move, [0, 0.5, 1], [A.x + 360, A.x + A.w + 20, B.x + 190]);
  const py = interpolate(move, [0, 0.5, 1], [A.y + 250, A.y + 330, B.y + 180]);
  const ps = spring({frame: frame - phone, fps, config: {damping: 13, stiffness: 180}});
  const ghost = q(frame, notNext, 8);
  const x = draw(frame, notNext + 10, 10);
  const tm = spring({frame: frame - timer, fps, config: {damping: 12, stiffness: 200}});
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Glow />
        <g fill="none" stroke={C.ink} strokeWidth={10} opacity={walls}>
          <path d={`M ${A.x} ${A.y} H ${B.x + B.w} V ${A.y + A.h} H ${A.x} Z`} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - walls} />
          <path d={`M ${A.x + A.w + 20} ${A.y} V ${A.y + 280}`} />
        </g>
        <circle cx={A.x + 200} cy={A.y + 230} r={30 * q(frame, 8, 8)} fill={C.ink} />
        {/* « pas retourné à côté de toi » */}
        <g opacity={ghost * (1 - draw(frame, notNext + 50, 10))}>
          <Phone x={A.x + 290} y={A.y + 240} w={36} rot={90} down />
          <path d={`M ${A.x + 250} ${A.y + 200} L ${A.x + 330} ${A.y + 280} M ${A.x + 330} ${A.y + 200} L ${A.x + 250} ${A.y + 280}`} stroke={C.red} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - x} />
        </g>
        <g opacity={Math.min(1, ps * 2)}>
          <Phone x={px} y={py} w={40} rot={move * 70} glow={0.3} />
        </g>
        {/* le minuteur, et le son qui viendra de loin */}
        <g transform={`translate(${B.x + 120} ${B.y + 90}) scale(${tm})`}>
          <circle r={30} fill={C.sheet} stroke={C.ink} strokeWidth={3} />
          <line x1={0} y1={0} x2={0} y2={-20} stroke={C.ink} strokeWidth={3} />
          <line x1={0} y1={0} x2={14} y2={6} stroke={C.ink} strokeWidth={3} />
          <rect x={-6} y={-40} width={12} height={8} fill={C.ink} />
        </g>
        {frame >= ring &&
          [0, 1, 2].map((k) => {
            const r = ((frame - ring + k * 10) % 30) / 30;
            return <circle key={k} cx={B.x + 120} cy={B.y + 90} r={40 + r * 120} fill="none" stroke={C.ink} strokeWidth={2} opacity={(1 - r) * 0.7} />;
          })}
      </svg>
      <div style={{position: 'absolute', left: A.x + 150, top: A.y + A.h + 24, fontFamily: F.mono, fontSize: 18, letterSpacing: '0.16em', color: C.ink, opacity: walls}}>{tx("TOI")}</div>
      <div style={{position: 'absolute', left: B.x + 80, top: A.y + A.h + 24, fontFamily: F.mono, fontSize: 18, letterSpacing: '0.16em', color: C.ink, opacity: walls}}>{tx("UNE AUTRE PIÈCE")}</div>
    </AbsoluteFill>
  );
};

// ── 2 · une chaise suffit ───────────────────────────────────────────────────────────────────────
export const StepChair: React.FC<{sit: number}> = ({sit}) => {
  
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const d = draw(frame, 2, 20);
  const s = spring({frame: frame - sit, fps, config: {damping: 10, stiffness: 160}});
  const X = 1280;
  const Y = 700;
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path
          d={`M ${X - 120} ${Y} V ${Y - 200} M ${X - 120} ${Y - 200} H ${X + 120} M ${X + 120} ${Y - 200} V ${Y} M ${X - 120} ${Y - 200} L ${X - 140} ${Y - 470}`}
          fill="none"
          stroke={C.ink}
          strokeWidth={8}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - d}
        />
        <line x1={X - 400} y1={Y + 4} x2={X + 400} y2={Y + 4} stroke={C.ink} strokeWidth={2} opacity={d} />
        <circle cx={X - 10} cy={interpolate(s, [0, 1], [Y - 520, Y - 260])} r={44} fill={C.ink} opacity={Math.min(1, s * 3)} />
      </svg>
    </AbsoluteFill>
  );
};

// ── 3 · regarder le bruit passer, comme des voitures sous la fenêtre ───────────────────────────
type Bubble = {t: string; at: number; lane: number; dur?: number};
export const StepNoise: React.FC<{bubbles: Bubble[]; flood: number; still: number}> = ({bubbles, flood, still}) => {
  
  const frame = useCurrentFrame();
  const win = {x: 860, y: 230, w: 940, h: 520};
  const d = draw(frame, 2, 18);
  // le volume : une foule de petites pensées, à des hauteurs et des vitesses différentes
  const crowd = Array.from({length: 22}, (_, k) => ({t: '…', at: flood + Math.round(k * 2.2 + random(`fa${k}`) * 4), lane: random(`fl${k}`) * 3.6, dur: 45 + Math.round(random(`fd${k}`) * 50)}));
  const all = [...bubbles, ...crowd];
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <defs>
          <clipPath id="vitre">
            <rect x={win.x} y={win.y} width={win.w} height={win.h} />
          </clipPath>
        </defs>
        <g clipPath="url(#vitre)">
          {all.map((b, i) => {
            if (frame < b.at) return null;
            const u = (frame - b.at) / (b.dur ?? 120);
            if (u > 1) return null;
            const w = b.t.length * 17 + 60;
            const x = win.x + win.w + 20 - u * (win.w + w + 60);
            const y = win.y + 90 + b.lane * 110 + (random(`b${i}`) - 0.5) * 20;
            return (
              <g key={i} transform={`translate(${x} ${y})`}>
                <rect x={0} y={-34} width={w} height={68} rx={34} fill={C.sheet} stroke={C.ink} strokeWidth={2.5} />
                <text x={w / 2} y={10} textAnchor="middle" fontFamily="Garamond, serif" fontStyle="italic" fontSize={30} fill={C.ink}>
                  {b.t}
                </text>
              </g>
            );
          })}
        </g>
        <g fill="none" stroke={C.ink} strokeWidth={6} opacity={d}>
          <rect x={win.x} y={win.y} width={win.w} height={win.h} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - d} />
          <line x1={win.x + win.w / 2} y1={win.y} x2={win.x + win.w / 2} y2={win.y + win.h} strokeWidth={4} />
          <line x1={win.x} y1={win.y + win.h + 30} x2={win.x + win.w} y2={win.y + win.h + 30} strokeWidth={3} />
        </g>
        {/* toi, devant la fenêtre : tu ne chasses rien */}
        <circle cx={win.x + win.w / 2} cy={win.y + win.h + 120} r={40 * q(frame, 6)} fill={C.ink} />
        <circle cx={win.x + win.w / 2} cy={win.y + win.h + 120} r={58} fill="none" stroke={C.gold} strokeWidth={3} opacity={q(frame, still, 10)} />
      </svg>
    </AbsoluteFill>
  );
};

// ── 4 · un seul point : la respiration, ou un mot ───────────────────────────────────────────────
export const StepPoint: React.FC<{point: number; breath: number; word: number; ar: number; arGloss: number}> = ({point, breath, word, ar, arGloss}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - point, fps, config: {damping: 12, stiffness: 170}});
  const b = frame >= breath ? 1 + 0.25 * Math.sin(((frame - breath) / 75) * Math.PI * 2 - Math.PI / 2) * 0.5 + 0.125 : 1;
  const X = 1300;
  const Y = 380;
  const arO = q(frame, ar, 10);
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Glow />
        <circle cx={X} cy={Y} r={160 * s * b} fill="url(#gold5)" />
        <circle cx={X} cy={Y} r={22 * s * b} fill={C.gold} />
        {frame >= breath &&
          [0, 1].map((k) => {
            const r = (((frame - breath) / 75 + k * 0.5) % 1);
            return <circle key={k} cx={X} cy={Y} r={30 + r * 140} fill="none" stroke={C.gold} strokeWidth={2} opacity={(1 - r) * 0.6 * (1 - arO * 0.6)} />;
          })}
      </svg>
      <div style={{position: 'absolute', left: X - 400, width: 800, top: Y + 150, textAlign: 'center', opacity: q(frame, word) * (1 - arO)}}>
        <span style={{fontFamily: F.serif, fontStyle: 'italic', fontSize: 46, color: C.ink}}>{tx("un mot, répété, lentement")}</span>
      </div>
      <div style={{position: 'absolute', left: X - 500, width: 1000, top: Y + 120, textAlign: 'center', opacity: arO, direction: 'rtl', fontFamily: F.arabic, fontSize: 120, color: C.gold, lineHeight: 1.3}}>
        أستغفر الله
      </div>
      <div style={{position: 'absolute', left: X - 500, width: 1000, top: Y + 300, textAlign: 'center', opacity: arO, fontFamily: F.mono, fontSize: 24, letterSpacing: '0.3em', color: C.ink}}>{tx("ASTAGHFIRULLĀH")}</div>
      <div style={{position: 'absolute', left: X - 500, width: 1000, top: Y + 346, textAlign: 'center', opacity: q(frame, arGloss), fontFamily: F.serif, fontStyle: 'italic', fontSize: 44, color: C.ink}}>{tx("je demande pardon à Dieu")}</div>
    </AbsoluteFill>
  );
};

// ── 5 · tu pars, tu reviens, sans te juger ──────────────────────────────────────────────────────
export const StepReturn: React.FC<{away: number; back: number; judge: number}> = ({away, back, judge}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  const X = 1300;
  const Y = 480;
  const out = interpolate(frame, [away, back], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  const ret = interpolate(frame, [back, back + 20], [0, 1], {...clamp, easing: inOut});
  const t = out * (1 - ret);
  const dx = 330 * t;
  const dy = -160 * t + Math.sin(frame / 6) * 18 * t;
  const pulse = frame >= back + 20 ? interpolate(frame, [back + 20, back + 40], [1, 0], clamp) : 0;
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Glow />
        <circle cx={X} cy={Y} r={150} fill="url(#gold5)" />
        <circle cx={X} cy={Y} r={22 + pulse * 10} fill={C.gold} />
        <circle cx={X} cy={Y} r={40 + pulse * 80} fill="none" stroke={C.gold} strokeWidth={2} opacity={pulse} />
        {/* le chemin d'aller, en pointillé : on le voit, sans le juger */}
        <path d={`M ${X - 70} ${Y + 20} Q ${X + 120} ${Y - 260} ${X + 260} ${Y - 150}`} fill="none" stroke={C.inkSoft} strokeWidth={2} strokeDasharray="6 10" opacity={out * 0.8} />
        <circle cx={X - 70 + dx} cy={Y + 20 + dy} r={30} fill={C.ink} />
      </svg>
      <div style={{position: 'absolute', left: X - 300, width: 600, top: Y + 200, textAlign: 'center', opacity: q(frame, judge), fontFamily: F.mono, fontSize: 26, letterSpacing: '0.24em', color: C.ink}}>{tx("SANS TE JUGER")}</div>
    </AbsoluteFill>
  );
};

// ── p60 : au bout de quarante secondes, l'envie de se lever ────────────────────────────────────
export const Urge: React.FC<{t40: [number, number]; itch: number; chips: {t: string; at: number}[]}> = ({t40, itch, chips}) => {
  
  const frame = useCurrentFrame();
  const X = 760;
  const Y = 520;
  const p = interpolate(frame, [t40[0], t40[1]], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  const sec = Math.round(p * 40);
  const it = q(frame, itch, 10);
  const jx = (random(`u${Math.floor(frame / 2)}`) - 0.5) * 16 * it + it * 30;
  const jy = (random(`v${Math.floor(frame / 2)}`) - 0.5) * 10 * it;
  const R = 200;
  const a = p * Math.PI * 2 * (40 / 120); // 40 s sur un cadran de 2 min
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <circle cx={X} cy={Y} r={R} fill="none" stroke={C.inkFaint} strokeWidth={6} />
        <path d={`M ${X} ${Y - R} A ${R} ${R} 0 ${a > Math.PI ? 1 : 0} 1 ${X + R * Math.sin(a)} ${Y - R * Math.cos(a)}`} fill="none" stroke={C.red} strokeWidth={6} strokeLinecap="round" opacity={p > 0 ? 1 : 0} />
        <circle cx={X + jx} cy={Y + jy} r={50} fill={C.ink} />
        {it > 0 && <path d={`M ${X + 90} ${Y} h ${120 * it} m -24 -18 l 24 18 l -24 18`} stroke={C.red} strokeWidth={4} fill="none" strokeLinecap="round" />}
      </svg>
      <div style={{position: 'absolute', left: X - 200, width: 400, top: Y + R + 30, textAlign: 'center', fontFamily: F.mono, fontSize: 30, letterSpacing: '0.12em', color: C.ink, opacity: q(frame, t40[0] - 6)}}>
        {`0:${String(sec).padStart(2, '0')}`}
      </div>
      {chips.map((c, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: 1130,
            top: 340 + i * 110,
            opacity: q(frame, c.at, 6),
            transform: `translateX(${(1 - q(frame, c.at, 8)) * -30}px)`,
            fontFamily: F.mono,
            fontSize: 24,
            letterSpacing: '0.14em',
            color: C.ink,
            border: `2px solid ${C.ink}`,
            padding: '12px 22px',
            background: C.sheet,
          }}
        >
          {c.t}
        </div>
      ))}
    </AbsoluteFill>
  );
};

// ── p61 : « Ce moment-là, c'est le bouton de l'étude. » Chaque retour compte ─────────────────────
export const Reps: React.FC<{button: number; count: number; per?: number}> = ({button, count, per = 7}) => {
  const tx = useText();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - button, fps, config: {damping: 9, stiffness: 200}});
  const pulse = 1 + 0.08 * Math.sin((frame - button) / 4) * q(frame, button);
  const n = frame < count ? 0 : Math.min(15, 1 + Math.floor((frame - count) / per));
  const out = q(frame, count - 10, 10);
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <g transform={`translate(${interpolate(out, [0, 1], [960, 420])} 300) scale(${s * pulse * (1 - out * 0.4)})`}>
          <circle r={110} fill={C.sheet} stroke={C.ink} strokeWidth={4} />
          <circle r={74} fill={C.red} />
        </g>
        {/* les retours, comptés comme des répétitions */}
        {Array.from({length: n}, (_, k) => {
          const g = Math.floor(k / 5);
          const i = k % 5;
          const x = 760 + g * 220 + i * 34;
          const d = draw(frame, count + k * per, 5);
          return i < 4 ? (
            <line key={k} x1={x} y1={260} x2={x} y2={260 + 120 * d} stroke={C.ink} strokeWidth={7} strokeLinecap="round" />
          ) : (
            <line key={k} x1={x - 150} y1={350} x2={x - 150 + 170 * d} y2={350 - 60 * d} stroke={C.gold} strokeWidth={7} strokeLinecap="round" />
          );
        })}
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 460, textAlign: 'center', fontFamily: F.mono, fontSize: 22, letterSpacing: '0.2em', color: C.ink, opacity: q(frame, button + 6) * (1 - out)}}>{tx("LE BOUTON DE L’ÉTUDE")}</div>
    </AbsoluteFill>
  );
};

// ── p63 : le bouton, tu l'as dans ta poche ──────────────────────────────────────────────────────
export const ButtonPhone: React.FC<{morph: number; warm: number}> = ({morph, warm}) => {
  
  const frame = useCurrentFrame();
  const m = interpolate(frame, [morph, morph + 20], [0, 1], {...clamp, easing: inOut});
  const glow = q(frame, warm, 16);
  const W = 240;
  const H = W * 2.05;
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <Glow />
        <ellipse cx={960} cy={540} rx={500} ry={560} fill="url(#glow5)" opacity={glow} />
        <g opacity={m}>
          <rect x={960 - W / 2} y={540 - H / 2} width={W} height={H} rx={36} fill={C.ink} />
          <rect x={960 - W / 2 + 12} y={540 - H / 2 + 12} width={W - 24} height={H - 24} rx={26} fill={SCREEN} opacity={0.3 + 0.7 * glow} />
        </g>
        {/* le bouton rouge rétrécit jusqu'à la pastille de notification */}
        <circle cx={interpolate(m, [0, 1], [960, 960 + W / 2 - 14])} cy={interpolate(m, [0, 1], [540, 540 - H / 2 + 14])} r={interpolate(m, [0, 1], [110, 26])} fill={C.red} />
      </svg>
    </AbsoluteFill>
  );
};

// ── L'écran de fin (les éléments YouTube se posent sur les cadres) ──────────────────────────────
export const EndCard: React.FC = () => {
  const tx = useText();
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{opacity: q(frame, 0, 14)}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 150, textAlign: 'center', fontFamily: F.mono, fontSize: 22, letterSpacing: '0.3em', color: C.inkSoft}}>{tx("PROCHAINE VIDÉO")}</div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 200, textAlign: 'center', fontFamily: F.serif, fontStyle: 'italic', fontSize: 58, color: C.ink}}>{tx("Pourquoi « ne penser à rien » marche si mal")}</div>
      <div style={{position: 'absolute', left: 300, top: 360, width: 720, height: 405, border: `2px dashed ${C.inkSoft}`}} />
      <div style={{position: 'absolute', left: 1180, top: 440, width: 250, height: 250, borderRadius: 125, border: `2px dashed ${C.inkSoft}`}} />
      <div style={{position: 'absolute', left: 1180, top: 720, width: 250, textAlign: 'center', fontFamily: F.mono, fontSize: 18, letterSpacing: '0.2em', color: C.ink}}>BILLKARKARIY</div>
    </AbsoluteFill>
  );
};
