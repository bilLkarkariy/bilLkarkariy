import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F, ROOM, S, px, py} from '../theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.bezier(0.65, 0, 0.35, 1);

type P = [number, number];

/** Position le long d'une polyligne (en mètres), paramétrée par la longueur. */
function along(pts: P[], t: number): P {
  const segs = pts.slice(1).map((p, i) => Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]));
  const total = segs.reduce((a, b) => a + b, 0);
  let d = Math.max(0, Math.min(1, t)) * total;
  for (let i = 0; i < segs.length; i++) {
    if (d <= segs[i] || i === segs.length - 1) {
      const u = segs[i] ? d / segs[i] : 0;
      return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u];
    }
    d -= segs[i];
  }
  return pts[pts.length - 1];
}

const QUEUE: P[] = [
  [-2.55, -2.15],
  [-2.1, -2.15],
  [-1.65, -2.15],
];
const START: P = [-1.2, -2.15];
const TRAY: P = [0.25, -2.2];
const INSIDE: P[] = [TRAY, [1.4, -2.2], [1.4, -1.05], [ROOM.chair.x, ROOM.chair.y]];

const Phone: React.FC<{x: number; y: number; s?: number}> = ({x, y, s = 1}) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <rect x={-11} y={-19} width={22} height={38} rx={4} fill={C.sheet} stroke={C.ink} strokeWidth={2} />
    <circle cx={9} cy={-17} r={5} fill={C.red} />
  </g>
);

const Pen: React.FC<{x: number; y: number; s?: number}> = ({x, y, s = 1}) => (
  <g transform={`translate(${x} ${y}) rotate(-35) scale(${s})`}>
    <rect x={-20} y={-3} width={34} height={6} fill={C.sheet} stroke={C.ink} strokeWidth={1.8} />
    <path d="M 14 -3 L 22 0 L 14 3 Z" fill={C.ink} />
  </g>
);

export type StudyCues = {
  place: number; // « Université »
  students: number; // « étudiants »
  walk1: [number, number]; // « entrent » -> « déposer »
  phone: number; // « téléphone »
  pen: number; // « stylos »
  walk2: [number, number]; // « Rien » -> dans la pièce
  door: number; // la porte se ferme
  slip: number; // « La consigne »
  words: number[]; // apparition de chaque mot de la consigne
  timer: number; // « Quinze »
  count: number; // fin de « minutes » : le compte à rebours part
};

const CONSIGNE = [['Reste', 'assis.'], ['Ne', "t'endors", 'pas.'], ['Occupe-toi', 'avec', 'tes', 'pensées.']];

export const Study: React.FC<StudyCues> = (c) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const draw = (start: number, len = 14) => interpolate(frame, [start, start + len], [0, 1], {...clamp, easing: inOut});

  const k = 0.74;
  const focus = {x: px(0), y: py(-0.66)};
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
  const wallsO = draw(0, 10);
  const corridor = draw(4, 16);

  // le participant
  const w1 = interpolate(frame, c.walk1, [0, 1], {...clamp, easing: inOut});
  const w2 = interpolate(frame, c.walk2, [0, 1], {...clamp, easing: inOut});
  const me: P = frame < c.walk2[0] ? along([START, TRAY], w1) : along(INSIDE, w2);
  const meS = spring({frame: frame - c.students, fps, config: {damping: 14}});

  // ses affaires : du point vers le casier
  const fly = (at: number, to: P) => {
    const u = interpolate(frame, [at, at + 12], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
    const from: P = [TRAY[0], TRAY[1] + 0.05];
    const x = from[0] + (to[0] - from[0]) * u;
    const y = from[1] + (to[1] - from[1]) * u + Math.sin(u * Math.PI) * 0.18;
    return {x: px(x), y: py(y), o: frame >= at ? 1 : 0};
  };
  const phone = fly(c.phone, [0.02, -2.63]);
  const pen = fly(c.pen, [0.42, -2.63]);

  // la porte se referme derrière lui
  const close = interpolate(frame, [c.door, c.door + 10], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
  const doorR = (ROOM.door[1] - ROOM.door[0]) * S;
  const hinge = {x: px(ROOM.door[1]), y: py(-hd)};
  const ang = (Math.PI / 2) * (1 - close) + Math.PI * close; // 90° ouvert -> 180° fermé
  const leaf = {x: hinge.x + Math.cos(ang) * doorR, y: hinge.y - Math.sin(ang) * doorR};

  // consigne + minuteur
  const slipIn = interpolate(frame, [c.slip, c.slip + 14], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const lift = interpolate(frame, [c.timer, c.timer + 12], [0, 1], {...clamp, easing: inOut});
  const planDim = interpolate(slipIn, [0, 1], [1, 0.22]);
  const timerIn = interpolate(frame, [c.timer, c.timer + 8], [0, 1], clamp);
  const left = 15 * 60 - Math.max(0, Math.floor((frame - c.count) / fps));
  const mm = String(Math.floor(left / 60)).padStart(2, '0');
  const ss = String(left % 60).padStart(2, '0');

  const labelO = interpolate(frame, [c.place, c.place + 8], [0, 1], clamp);
  let wi = 0;

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{opacity: planDim}}>
        <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
          <defs>
            {/* le couloir s'efface sur les côtés */}
            <linearGradient id="inkFade" gradientUnits="userSpaceOnUse" x1={px(-4.2)} x2={px(4.2)} y1={0} y2={0}>
              <stop offset="0" stopColor={C.ink} stopOpacity="0" />
              <stop offset="0.22" stopColor={C.ink} stopOpacity="1" />
              <stop offset="0.78" stopColor={C.ink} stopOpacity="1" />
              <stop offset="1" stopColor={C.ink} stopOpacity="0" />
            </linearGradient>
          </defs>
          <g transform={`translate(960 545) scale(${k}) translate(${-focus.x} ${-focus.y})`}>
            <g opacity={wallsO}>
              {walls.map(([x0, y0, x1, y1], i) => (
                <rect key={i} x={px(x0)} y={py(y1)} width={(x1 - x0) * S} height={(y1 - y0) * S} fill={C.ink} />
              ))}
            </g>
            {/* couloir */}
            <g opacity={corridor}>
              <rect x={px(-4.2)} y={py(-2.8)} width={8.4 * S} height={0.15 * S} fill="url(#inkFade)" />
              <line x1={px(-4.2)} x2={px(-hw - t)} y1={py(-hd - t)} y2={py(-hd - t)} stroke="url(#inkFade)" strokeWidth={2} />
              <line x1={px(hw + t)} x2={px(4.2)} y1={py(-hd - t)} y2={py(-hd - t)} stroke="url(#inkFade)" strokeWidth={2} />
            </g>
            {/* casier à l'entrée */}
            <g opacity={corridor}>
              <rect x={px(-0.2)} y={py(-2.5)} width={0.85 * S} height={0.3 * S} fill={C.sheet} stroke={C.ink} strokeWidth={2} />
            </g>
            {/* porte */}
            <g fill="none" stroke={C.ink}>
              <path
                d={`M ${px(ROOM.door[0])} ${hinge.y} A ${doorR} ${doorR} 0 0 1 ${hinge.x} ${hinge.y - doorR}`}
                strokeWidth={1.4}
                strokeDasharray="5 6"
                opacity={0.6 * wallsO * (1 - close)}
              />
              <line x1={hinge.x} y1={hinge.y} x2={leaf.x} y2={leaf.y} strokeWidth={close > 0.98 ? 6 : 2} opacity={wallsO} />
            </g>
            {/* table + chaise (pas encore de bouton) */}
            <g fill="none" stroke={C.ink} strokeWidth={2} opacity={wallsO}>
              <rect
                x={px(ROOM.table.x - ROOM.table.w / 2)}
                y={py(ROOM.table.y + ROOM.table.d / 2)}
                width={ROOM.table.w * S}
                height={ROOM.table.d * S}
              />
              <rect
                x={px(ROOM.chair.x - ROOM.chair.s / 2)}
                y={py(ROOM.chair.y + ROOM.chair.s / 2)}
                width={ROOM.chair.s * S}
                height={ROOM.chair.s * S}
              />
              <line
                x1={px(ROOM.chair.x - ROOM.chair.s / 2)}
                x2={px(ROOM.chair.x + ROOM.chair.s / 2)}
                y1={py(ROOM.chair.y - ROOM.chair.s / 2) - 7}
                y2={py(ROOM.chair.y - ROOM.chair.s / 2) - 7}
                strokeWidth={5}
              />
            </g>
            {/* affaires déposées */}
            {phone.o > 0 && <Phone x={phone.x} y={phone.y} />}
            {pen.o > 0 && <Pen x={pen.x} y={pen.y} />}
            {/* la file d'attente, puis le participant */}
            {QUEUE.map(([x, y], i) => {
              const s = spring({frame: frame - c.students - 3 * (i + 1), fps, config: {damping: 14}});
              return <circle key={i} cx={px(x)} cy={py(y)} r={15 * s} fill={C.ink} opacity={0.35} />;
            })}
            <circle cx={px(me[0])} cy={py(me[1])} r={16 * meS} fill={C.ink} />
          </g>
        </svg>
      </AbsoluteFill>

      {/* chapitre + lieu */}
      <div style={{position: 'absolute', left: 64, top: 52, fontFamily: F.mono, color: C.ink}}>
        <div style={{fontSize: 20, letterSpacing: '0.18em', fontWeight: 500, opacity: draw(0, 10)}}>01 · L'EXPÉRIENCE</div>
        <div style={{fontSize: 18, letterSpacing: '0.14em', marginTop: 10, color: C.inkSoft, opacity: labelO * planDim}}>
          UNIVERSITÉ DE VIRGINIE · ÉTATS-UNIS
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: (px(-0.2) - focus.x) * k + 960 - 118,
          top: (py(-2.65) - focus.y) * k + 545 - 10,
          fontFamily: F.mono,
          fontSize: 15,
          letterSpacing: '0.16em',
          color: C.inkSoft,
          opacity: corridor * planDim,
        }}
      >
        AFFAIRES
      </div>

      {/* la consigne, mot à mot sur la voix */}
      <div
        style={{
          position: 'absolute',
          left: 960 - 470,
          width: 940,
          top: 300 - lift * 120,
          opacity: slipIn,
          transform: `translateY(${(1 - slipIn) * 60}px) rotate(-0.6deg)`,
          background: C.sheet,
          boxShadow: '0 24px 50px rgba(30,28,24,0.16), 0 2px 6px rgba(30,28,24,0.1)',
          padding: '34px 56px 40px',
        }}
      >
        <div
          style={{
            fontFamily: F.mono,
            fontSize: 17,
            letterSpacing: '0.2em',
            color: C.inkSoft,
            borderBottom: `1.5px solid ${C.ink}`,
            paddingBottom: 12,
            marginBottom: 22,
          }}
        >
          CONSIGNE
        </div>
        {CONSIGNE.map((line, li) => (
          <div key={li} style={{fontFamily: F.mono, fontSize: 46, lineHeight: 1.32, color: C.ink, display: 'flex', gap: '0.55em'}}>
            {line.map((w) => {
              const at = c.words[wi++];
              return (
                <span key={w} style={{opacity: interpolate(frame, [at - 1, at + 3], [0, 1], clamp)}}>
                  {w}
                </span>
              );
            })}
          </div>
        ))}
      </div>
      <div
        style={{
          position: 'absolute',
          width: '100%',
          top: 690,
          textAlign: 'center',
          fontFamily: F.mono,
          fontWeight: 500,
          fontSize: 170,
          letterSpacing: '0.02em',
          color: C.ink,
          opacity: timerIn,
        }}
      >
        {mm}:{ss}
      </div>
    </AbsoluteFill>
  );
};
