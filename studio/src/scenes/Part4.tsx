import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import carte from '../data/carte_ghazali.json';
import {C, F} from '../theme';

// Scènes de la partie 4 (la pièce sans meuble, la khalwa, al-Ghazali, le dhikr, le verset).
// L'or = le centre, le point fixe. Les mots arabes s'écrivent de droite à gauche.

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.bezier(0.65, 0, 0.35, 1);
const rise = (frame: number, at: number, len = 7) => {
  const q = interpolate(frame, [at, at + len], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  return {opacity: q, transform: `translateY(${(1 - q) * 16}px)`};
};

// ── Typographie animée : des lignes dont les mots sortent sur la voix ────────────────────────────
export type Line = {
  t: string;
  at: number; // premier mot
  y: number;
  size?: number;
  italic?: boolean;
  mono?: boolean;
  color?: string;
  gold?: string[]; // mots en or
  red?: string[]; // mots en rouge
  stagger?: number; // images entre deux mots
  strike?: number; // barré au feutre rouge
  out?: number;
};

export const Kinetic: React.FC<{lines: Line[]}> = ({lines}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      {lines.map((l, i) => {
        const words = l.t.split(' ');
        const size = l.size ?? 64;
        const o = l.out === undefined ? 1 : interpolate(frame, [l.out, l.out + 8], [1, 0], clamp);
        const strike = l.strike === undefined ? 0 : interpolate(frame, [l.strike, l.strike + 10], [0, 1], {...clamp, easing: inOut});
        return (
          <div key={i} style={{position: 'absolute', left: 0, right: 0, top: l.y, textAlign: 'center', opacity: o}}>
            <span style={{position: 'relative', display: 'inline-block'}}>
              {words.map((w, k) => {
                const bare = w.replace(/[.,:;!?«»]/g, '');
                const color = l.gold?.includes(bare) ? C.gold : l.red?.includes(bare) ? C.red : l.color ?? C.ink;
                return (
                  <span
                    key={k}
                    style={{
                      ...rise(frame, l.at + k * (l.stagger ?? 2.5)),
                      display: 'inline-block',
                      marginRight: '0.26em',
                      fontFamily: l.mono ? F.mono : F.serif,
                      fontStyle: l.italic ? 'italic' : 'normal',
                      fontSize: size,
                      letterSpacing: l.mono ? '0.16em' : '-0.005em',
                      color,
                    }}
                  >
                    {w}
                  </span>
                );
              })}
              {l.strike !== undefined && (
                <div
                  style={{
                    position: 'absolute',
                    left: -10,
                    right: 0,
                    top: size * 0.6,
                    height: size * 0.08,
                    borderRadius: size * 0.04,
                    background: C.red,
                    transformOrigin: '0 50%',
                    transform: `scaleX(${strike}) rotate(-1deg)`,
                  }}
                />
              )}
            </span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ── Un mot arabe, écrit de droite à gauche, sa translittération, son sens ──────────────────────
export const ArabicWord: React.FC<{ar: string; latin: string; gloss?: string; at: number; latinAt?: number; glossAt?: number; y?: number; out?: number; size?: number}> = ({
  ar,
  latin,
  gloss,
  at,
  latinAt,
  glossAt,
  y = 300,
  out,
  size = 230,
}) => {
  const frame = useCurrentFrame();
  const w = interpolate(frame, [at, at + 26], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const o = out === undefined ? 1 : interpolate(frame, [out, out + 10], [1, 0], clamp);
  // la ligne d'or sous le mot : elle part de la droite, comme l'écriture
  const rule = interpolate(frame, [at + 14, at + 34], [0, 1], {...clamp, easing: inOut});
  return (
    <AbsoluteFill style={{opacity: o}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: y,
          textAlign: 'center',
          fontFamily: F.arabic,
          fontSize: size,
          lineHeight: 1.25,
          color: C.gold,
          direction: 'rtl',
          WebkitMaskImage: `linear-gradient(to left, #000 ${w * 100}%, transparent ${w * 100 + 8}%)`,
          filter: 'drop-shadow(2px 4px 4px rgba(30,28,24,0.18))',
        }}
      >
        {ar}
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <line x1={960 + 260} y1={y + size * 1.36} x2={960 + 260 - 520 * rule} y2={y + size * 1.36} stroke={C.gold} strokeWidth={2} />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: y + size * 1.36 + 30, textAlign: 'center', ...rise(frame, latinAt ?? at + 18)}}>
        <span style={{fontFamily: F.mono, fontSize: 30, letterSpacing: '0.42em', color: C.ink}}>{latin}</span>
      </div>
      {gloss && (
        <div style={{position: 'absolute', left: 0, right: 0, top: y + size * 1.36 + 90, textAlign: 'center', ...rise(frame, glossAt ?? at + 30)}}>
          <span style={{fontFamily: F.serif, fontStyle: 'italic', fontSize: 52, color: C.ink}}>{gloss}</span>
        </div>
      )}
    </AbsoluteFill>
  );
};

// ── La carte : Bagdad, puis la route vers Damas ─────────────────────────────────────────────────
type MapCues = {
  draw: number; // les côtes et les fleuves s'encrent
  cam: {f: number; x: number; y: number; k: number}[]; // la caméra : centre et échelle, par image
  bagdad?: number;
  bagdadSub?: {t: string; at: number};
  damas?: number;
  route?: [number, number]; // le trajet se trace
  routeLabel?: {t: string; at: number};
};

// la terre en papier chaud, l'eau en bleu-gris doux (comme une carte ancienne lavée à l'aquarelle)
const LAND = '#EFE6D2';
const SEA = '#C9D7DB';
const SEA_EDGE = '#DCE5E6';
const WATER = '#4E7690';

export const GhazaliMap: React.FC<MapCues> = ({draw, cam, bagdad, bagdadSub, damas, route, routeLabel}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ink = interpolate(frame, [draw, draw + 40], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  const i = cam.findIndex((c) => c.f > frame);
  const a = cam[Math.max(0, (i < 0 ? cam.length : i) - 1)];
  const b = i < 0 ? a : cam[i];
  const q = a === b ? 0 : inOut((frame - a.f) / (b.f - a.f));
  const cx = a.x + (b.x - a.x) * q;
  const cy = a.y + (b.y - a.y) * q;
  const k = a.k + (b.k - a.k) * q;
  const [bx, by] = carte.cities.bagdad;
  const [dx, dy] = carte.cities.damas;
  // le trajet : une courbe douce, du Tigre à Damas (pas un itinéraire précis)
  const mx = (bx + dx) / 2;
  const my = Math.min(by, dy) - 150;
  const rP = route ? interpolate(frame, [route[0], route[1]], [0, 1], {...clamp, easing: inOut}) : 0;
  const city = (x: number, y: number, at: number | undefined, label: string, sub?: {t: string; at: number}) => {
    if (at === undefined || frame < at - 2) return null;
    const s = spring({frame: frame - at, fps, config: {damping: 11, stiffness: 200}});
    return (
      <g transform={`translate(${x} ${y})`}>
        <circle r={(16 + 30 * interpolate(frame, [at, at + 24], [0, 1], clamp)) / k} fill="none" stroke={C.gold} strokeWidth={2 / k} opacity={1 - interpolate(frame, [at, at + 24], [0, 1], clamp)} />
        <circle r={(11 * s) / k} fill={C.gold} />
        <text x={22 / k} y={-14 / k} fontFamily="'Plex Mono', monospace" fontSize={26 / k} letterSpacing={4 / k} fill={C.ink} opacity={s}>
          {label}
        </text>
        {sub && (
          <text x={22 / k} y={26 / k} fontFamily="Garamond, serif" fontStyle="italic" fontSize={40 / k} fill={C.ink} opacity={interpolate(frame, [sub.at, sub.at + 8], [0, 1], clamp)}>
            {sub.t}
          </text>
        )}
      </g>
    );
  };
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <g transform={`translate(960 540) scale(${k}) translate(${-cx} ${-cy})`}>
          {/* la mer d'abord, puis les terres posées dessus : on voit tout de suite où est l'eau */}
          <rect x={-3000} y={-3000} width={8000} height={8000} fill={SEA} opacity={ink} />
          {carte.coast.map((d, j) => (
            <path key={`h${j}`} d={d} fill="none" stroke={SEA_EDGE} strokeWidth={22 / k} strokeLinejoin="round" opacity={ink} />
          ))}
          {carte.land.map((d, j) => (
            <path key={`t${j}`} d={d} fill={LAND} fillRule="evenodd" opacity={ink} />
          ))}
          {carte.coast.map((d, j) => (
            <path key={`c${j}`} d={d} fill="none" stroke={C.ink} strokeWidth={2.2 / k} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - ink} />
          ))}
          {carte.lakes.map((d, j) => (
            <path key={`l${j}`} d={d} fill={SEA} stroke={WATER} strokeWidth={1.4 / k} opacity={ink} />
          ))}
          {Object.entries(carte.rivers).flatMap(([, ds]) =>
            ds.map((d, j) => (
              <path key={`r${d.length}-${j}`} d={d} fill="none" stroke={WATER} strokeWidth={3.2 / k} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - ink} />
            )),
          )}
          {carte.seas.map((m) => (
            <text key={m.t} x={m.x} y={m.y} textAnchor="middle" fontFamily="Garamond, serif" fontStyle="italic" fontSize={m.s / k} letterSpacing={3 / k} fill={WATER} opacity={ink} transform={`rotate(${m.a} ${m.x} ${m.y})`}>
              {m.t}
            </text>
          ))}
          {carte.riverLabels.map((m) => (
            <text key={m.t} x={m.x} y={m.y} dy={-14 / k} textAnchor="middle" fontFamily="Garamond, serif" fontStyle="italic" fontSize={32 / k} fill={WATER} stroke={LAND} strokeWidth={6 / k} paintOrder="stroke" opacity={ink} transform={`rotate(${m.a} ${m.x} ${m.y})`}>
              {m.t}
            </text>
          ))}
          {carte.regions.map((m) => (
            <text key={m.t} x={m.x} y={m.y} textAnchor="middle" fontFamily="'Plex Mono', monospace" fontSize={20 / k} letterSpacing={9 / k} fill={C.inkSoft} opacity={0.7 * ink}>
              {m.t}
            </text>
          ))}
          {route && (
            <path
              d={`M ${bx} ${by} Q ${mx} ${my} ${dx} ${dy}`}
              fill="none"
              stroke={C.gold}
              strokeWidth={4 / k}
              strokeDasharray={`${14 / k} ${10 / k}`}
              strokeDashoffset={0}
              style={{clipPath: `inset(0 0 0 ${(1 - rP) * 100}%)`}}
            />
          )}
          {city(bx, by, bagdad, 'BAGDAD', bagdadSub)}
          {city(dx, dy, damas, 'DAMAS')}
        </g>
      </svg>
      {routeLabel && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 820, textAlign: 'center', ...rise(frame, routeLabel.at)}}>
          <span style={{fontFamily: F.serif, fontStyle: 'italic', fontSize: 48, color: C.ink}}>{routeLabel.t}</span>
        </div>
      )}
    </AbsoluteFill>
  );
};

// ── Le chapelet : répéter un nom, encore et encore ──────────────────────────────────────────────
export const Tasbih: React.FC<{at: number; beats: number[]; n?: number; out?: number}> = ({at, beats, n = 33, out}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const R = 330;
  const cx = 960;
  const cy = 300;
  const o = (out === undefined ? 1 : interpolate(frame, [out, out + 10], [1, 0], clamp)) * interpolate(frame, [at, at + 10], [0, 1], clamp);
  // une perle de plus à chaque battement, et entre deux battements la main continue, régulière
  const counted = (f: number) => {
    let c = 0;
    for (let i = 0; i < beats.length; i++) if (f >= beats[i]) c = i + 1;
    if (beats.length && f > beats[beats.length - 1]) c += Math.floor((f - beats[beats.length - 1]) / 9);
    return Math.min(n, c);
  };
  const cnt = counted(frame);
  const thread = interpolate(frame, [at, at + 24], [0, 1], {...clamp, easing: inOut});
  return (
    <AbsoluteFill style={{opacity: o}}>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 0 ${cx + R} ${cy}`} fill="none" stroke={C.inkSoft} strokeWidth={2} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - thread} />
        {Array.from({length: n}, (_, i) => {
          const t = Math.PI - (i / (n - 1)) * Math.PI;
          const x = cx + Math.cos(t) * R;
          const y = cy + Math.sin(t) * R;
          const appear = spring({frame: frame - at - 6 - i, fps, config: {damping: 14, stiffness: 200}});
          const lit = i < cnt;
          const pop = lit ? spring({frame: frame - (beats[i] ?? beats[beats.length - 1] + (i - beats.length + 1) * 9), fps, config: {damping: 9, stiffness: 260}}) : 0;
          return <circle key={i} cx={x} cy={y} r={15 * appear * (1 + 0.25 * (1 - pop) * (lit ? 1 : 0))} fill={lit ? C.gold : C.sheet} stroke={C.ink} strokeWidth={lit ? 0 : 2} />;
        })}
        {/* le gland du chapelet */}
        <path d={`M ${cx} ${cy + R + 16} l 0 40 M ${cx - 12} ${cy + R + 60} l 12 50 l 12 -50 Z`} stroke={C.ink} strokeWidth={2} fill={C.gold} opacity={thread} />
      </svg>
    </AbsoluteFill>
  );
};

// ── Le verset : pas d'animation (un fondu), pas de son dessous ──────────────────────────────────
export const Verse: React.FC<{out: number}> = ({out}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 14, out, out + 14], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill style={{opacity: o, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{fontFamily: F.mono, fontSize: 20, letterSpacing: '0.24em', color: C.inkSoft, marginBottom: 46}}>CORAN · SOURATE 13 (AR-RAʿD) · VERSET 28</div>
      <div style={{fontFamily: F.quran, fontSize: 52, color: C.inkSoft, direction: 'rtl', lineHeight: 1.6}}>ٱلَّذِينَ ءَامَنُوا۟ وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ ٱللَّهِ ۗ</div>
      <div style={{fontFamily: F.quran, fontSize: 112, color: C.ink, direction: 'rtl', lineHeight: 1.7, marginTop: 6}}>أَلَا بِذِكْرِ ٱللَّهِ تَطْمَئِنُّ ٱلْقُلُوبُ</div>
      <div style={{width: 120, height: 2, background: C.gold, margin: '40px 0 36px'}} />
      <div style={{fontFamily: F.serif, fontStyle: 'italic', fontSize: 48, color: C.ink}}>« C'est par le rappel de Dieu que les cœurs s'apaisent. »</div>
    </AbsoluteFill>
  );
};
