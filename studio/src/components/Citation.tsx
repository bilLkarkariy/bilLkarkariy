import React from 'react';
import {Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CAP, Rect} from '../captures';
import {C, F} from '../theme';

// Une vraie page (capture) posée sur le papier, sans zoom : la page reste nette.
// Le passage cité se surligne au feutre, mot à mot sur la voix, et une fiche
// en français (« ce que ça dit ») sort dans la marge, reliée au passage.
// Les textes des fiches sont dans le montage : la version anglaise n'aura qu'à les changer.

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.bezier(0.65, 0, 0.35, 1);

export type Tone = 'red' | 'gold' | 'ink';
const TONE: Record<Tone, {mark: string; accent: string}> = {
  red: {mark: 'rgba(215,38,30,0.26)', accent: '#EC4B40'},
  gold: {mark: 'rgba(200,150,46,0.38)', accent: '#DDAA4A'},
  ink: {mark: 'rgba(34,33,30,0.14)', accent: '#EEEBE4'},
};
const CARD_INK = '#EEEBE4';

export type Note = {
  at: number;
  kicker?: string; // petite ligne en capitales (contexte)
  big?: string; // le chiffre ou les mots qui comptent
  count?: {to: number; from?: number; dur?: number; fmt?: (n: number) => string}; // le grand chiffre défile
  text?: string; // ce que ça veut dire, en une phrase
  chips?: {t: string; at: number; dot?: boolean}[]; // petites étiquettes qui sortent une à une (dot : pastille rouge = le bouton)
  y?: number; // haut de la fiche, en px depuis le haut de la feuille (sinon : à hauteur du passage)
  until?: number; // la fiche s'efface
  tone?: Tone;
};

export type Mark = {
  i: number; // numéro du passage (voir hl())
  at: number; // le feutre part
  tone?: Tone;
  note?: Note;
  redact?: number; // caviardé au feutre noir
};

export type CitationProps = {
  cap: string;
  x: number; // coin haut gauche de la feuille, à l'écran
  y: number;
  width: number; // largeur affichée (la capture fait 2,5× : jamais agrandie au-delà)
  crop?: number; // hauteur gardée, en px CSS de la page
  tilt?: number;
  tag?: string; // ligne d'archive au-dessus de la feuille
  sub?: {text: string; at: number}; // traduction sous la feuille (ex. le titre)
  marks?: Mark[];
  notes?: Note[]; // fiches sans passage
  notesX?: number; // relatif à la feuille (défaut : à droite)
  notesW?: number;
  out?: number; // la feuille repart
  dim?: number; // 0 à 1 : le reste de la page s'efface quand on surligne
  veil?: number; // flou de la page (px) : on voit que c'est la vraie page, sans pouvoir la lire
  inset?: number; // marge de papier autour de la capture (px), pour les captures prises sans marge
  zIndexNotes?: number;
};

const lineDur = (r: Rect) => Math.max(5, Math.min(16, Math.round(r.w / 34)));

const CHIP_FONT = 17;
const chipW = (c: {t: string; dot?: boolean}) => c.t.length * CHIP_FONT * 0.72 + 28 + (c.dot ? 24 : 0);

/** Hauteur estimée d'une fiche (pour empiler sans chevauchement). */
const noteH = (n: Note, w: number) => {
  const inner = w - 64;
  const perLine = Math.floor(inner / 15.5);
  let rows = 0;
  let used = Infinity;
  for (const c of n.chips ?? []) {
    if (used + 12 + chipW(c) > inner) {
      rows++;
      used = chipW(c);
    } else used += 12 + chipW(c);
  }
  return (
    46 +
    (n.kicker ? 30 : 0) +
    (n.big || n.count ? 92 : 0) +
    (n.text ? Math.ceil(n.text.length / perLine) * 42 : 0) +
    (rows ? 14 + rows * 44 : 0)
  );
};

export const NoteCard: React.FC<{n: Note; x: number; y: number; w: number; tone: Tone}> = ({n, x, y, w, tone}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const a = frame - n.at;
  if (a < 0) return null;
  const sp = spring({frame: a, fps, config: {damping: 13, stiffness: 190, mass: 0.7}});
  const o = interpolate(a, [0, 4], [0, 1], clamp) * (n.until === undefined ? 1 : interpolate(frame, [n.until, n.until + 8], [1, 0], clamp));
  const t = TONE[n.tone ?? tone];
  const big =
    n.count !== undefined
      ? (n.count.fmt ?? String)(
          Math.round(
            interpolate(a, [4, 4 + (n.count.dur ?? 20)], [n.count.from ?? 0, n.count.to], {...clamp, easing: Easing.out(Easing.cubic)}),
          ),
        )
      : n.big;
  const words = n.text ? n.text.split(' ') : [];
  const rise = (d: number) => {
    const q = interpolate(a, [d, d + 6], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
    return {opacity: q, transform: `translateY(${(1 - q) * 14}px)`, display: 'inline-block'} as React.CSSProperties;
  };
  const textAt = (n.kicker ? 3 : 0) + (big ? 5 : 2);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        opacity: o,
        transform: `perspective(1400px) translateX(${(1 - sp) * -24}px) rotateY(${(1 - sp) * -78}deg)`,
        transformOrigin: '0% 50%',
        background: C.ink,
        color: CARD_INK,
        padding: '22px 30px 24px 34px',
        boxShadow: '16px 26px 40px rgba(20,18,15,0.30), 2px 4px 8px rgba(20,18,15,0.22)',
      }}
    >
      <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 6, background: t.accent}} />
      {n.kicker && (
        <div style={{...rise(2), fontFamily: F.mono, fontSize: 16, letterSpacing: '0.16em', color: 'rgba(238,235,228,0.6)', marginBottom: 8}}>
          {n.kicker}
        </div>
      )}
      {big && (
        <div
          style={{
            fontFamily: F.serif,
            fontWeight: 500,
            fontSize: big.length > 9 ? 66 : 84,
            lineHeight: 1,
            color: t.accent,
            letterSpacing: '-0.01em',
            marginBottom: 6,
          }}
        >
          <span style={rise(n.kicker ? 4 : 2)}>{big}</span>
        </div>
      )}
      {n.text && (
        <div style={{fontFamily: F.serif, fontStyle: 'italic', fontSize: 36, lineHeight: 1.16}}>
          {words.map((wd, i) => (
            <span key={i} style={{...rise(textAt + i * 1.3), marginRight: '0.26em'}}>
              {wd}
            </span>
          ))}
        </div>
      )}
      {n.chips && (
        <div style={{display: 'flex', gap: 12, marginTop: 14, flexWrap: 'wrap'}}>
          {n.chips.map((c, i) => {
            const cs = spring({frame: frame - c.at, fps, config: {damping: 11, stiffness: 220, mass: 0.6}});
            return (
              <span
                key={i}
                style={{
                  fontFamily: F.mono,
                  fontSize: CHIP_FONT,
                  letterSpacing: '0.12em',
                  whiteSpace: 'nowrap',
                  padding: '7px 14px',
                  border: `1.5px solid rgba(238,235,228,0.7)`,
                  opacity: frame >= c.at ? 1 : 0,
                  transform: `scale(${0.6 + 0.4 * cs})`,
                  display: 'inline-block',
                }}
              >
                {c.dot && (
                  <span style={{display: 'inline-block', width: 14, height: 14, borderRadius: 7, background: C.red, marginRight: 10, verticalAlign: '-1px'}} />
                )}
                {c.t}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
};

export const Citation: React.FC<CitationProps> = (p) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const meta = CAP[p.cap];
  if (!meta) throw new Error(`capture inconnue : ${p.cap}`);
  const k = p.width / meta.w;
  const W = p.width;
  const H = (p.crop ?? meta.h) * k;
  const cut = meta.cutout === true; // objet détouré : pas de feuille, l'ombre a la forme du papier
  const I = cut ? 0 : p.inset ?? 0; // la feuille déborde de la capture de I px de chaque côté
  const src = staticFile(`captures/${p.cap}.png`);
  const shape: React.CSSProperties = cut
    ? {WebkitMaskImage: `url(${src})`, WebkitMaskSize: `${W}px ${meta.h * k}px`, WebkitMaskRepeat: 'no-repeat'}
    : {};
  const SW = W + 2 * I;
  const SH = H + 2 * I;
  const marks = p.marks ?? [];

  // entrée : la feuille glisse et se pose ; sortie : elle remonte et s'efface
  const s = spring({frame, fps, config: {damping: 17, stiffness: 120, mass: 0.9}});
  const o = interpolate(frame, [0, 5], [0, 1], clamp);
  const e = p.out === undefined ? 0 : interpolate(frame, [p.out, p.out + 12], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  const tilt = p.tilt ?? -0.6;
  const drift = interpolate(frame, [0, durationInFrames], [0, -14]);
  // hauteur au-dessus du bureau : 1 quand elle tombe, 0 posée ; elle se soulève pour repartir
  const h = 1 - s;
  const air = Math.max(h, e * 0.8);
  const box = {position: 'absolute', left: p.x - I, top: p.y - I, width: SW, height: SH} as const;
  const sheet3d: React.CSSProperties = {
    ...box,
    opacity: o * (1 - e),
    transform: `translateY(${drift - e * 40}px) translateZ(${air * 240}px) rotateX(${h * 22 - e * 6}deg) rotateZ(${tilt - h * 3 + e * 2}deg)`,
    transformOrigin: '50% 50%',
  };
  const flat = `translateY(${drift - e * 40}px) rotate(${tilt}deg)`;
  // ombres sur le bureau (lumière de la fenêtre, en haut à gauche) : nette posée, large et douce en l'air
  const shadow = (dx: number, dy: number, blur: number, a: number): React.CSSProperties => ({
    ...box,
    background: 'rgb(30,28,24)',
    opacity: a * o * (1 - e * 0.8),
    filter: `blur(${blur}px)`,
    transform: `translate(${dx}px, ${dy}px) ${flat} scale(${1 + air * 0.05})`,
  });

  // le reste de la page s'efface dès le premier coup de feutre
  const first = marks.length ? Math.min(...marks.map((m) => m.at)) : Infinity;
  const dimO = marks.length ? (p.dim ?? 0.5) * interpolate(frame, [first, first + 10], [0, 1], clamp) : 0;
  const started = marks.filter((m) => frame >= m.at);
  const maskId = `dim-${p.cap}`;

  // fiches : à hauteur de leur passage, empilées sans se chevaucher
  const notesX = p.notesX ?? SW + 70;
  const notesW = p.notesW ?? 540;
  const placed: {n: Note; y: number; h: number; tone: Tone; mid?: number; top?: number; bot?: number}[] = [];
  const all = [
    ...marks.filter((m) => m.note).map((m) => {
      const r = meta.highlights[m.i].rects;
      const top = r[0].y * k + I;
      const bot = (r[r.length - 1].y + r[r.length - 1].h) * k + I;
      return {n: m.note as Note, tone: m.note?.tone ?? m.tone ?? 'red', mid: (top + bot) / 2, top, bot};
    }),
    ...(p.notes ?? []).map((n) => ({n, tone: n.tone ?? ('ink' as Tone), mid: undefined, top: undefined, bot: undefined})),
  ].sort((a, b) => a.n.at - b.n.at);
  // la place de chaque fiche est fixée à son apparition : sous les fiches encore là à ce moment
  // (une fiche qui s'efface laisse sa place à la suivante, qui pivote par-dessus)
  for (const it of all) {
    let y = it.n.y ?? (it.mid !== undefined ? it.mid - 46 : 0);
    for (const q of placed) {
      const stays = q.n.until === undefined || q.n.until > it.n.at;
      if (stays) y = Math.max(y, q.y + q.h + 18);
    }
    placed.push({...it, y, h: noteH(it.n, notesW)});
  }

  return (
    <div style={{position: 'absolute', inset: 0, perspective: 2600, perspectiveOrigin: `${p.x + W / 2}px 42%`}}>
      {[shadow(18 + air * 70, 30 + air * 110, 26 + air * 30, 0.16), shadow(3 + air * 60, 5 + air * 90, 2.5 + air * 34, 0.26 * (1 - air * 0.5))].map(
        (st, i) =>
          cut ? (
            <div key={i} style={{...st, background: 'none'}}>
              <Img src={src} style={{width: W, height: meta.h * k, display: 'block', filter: 'brightness(0)'}} />
            </div>
          ) : (
            <div key={i} style={st} />
          ),
      )}
      <div style={sheet3d}>
      {p.tag && (
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: -40,
            fontFamily: F.mono,
            fontSize: 16,
            letterSpacing: '0.16em',
            color: C.inkSoft,
            whiteSpace: 'nowrap',
            opacity: interpolate(frame, [4, 12], [0, 1], clamp),
          }}
        >
          {p.tag}
        </div>
      )}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: cut ? 'none' : C.sheet,
          overflow: 'hidden',
          ...shape,
        }}
      >
        <div style={{position: 'absolute', left: I, top: I, width: W, height: H, overflow: 'hidden'}}>
        <Img
          src={src}
          style={{
            width: W,
            height: meta.h * k,
            display: 'block',
            mixBlendMode: cut ? 'normal' : 'multiply',
            filter: `${cut ? 'contrast(1.04)' : 'grayscale(1) contrast(1.08)'}${p.veil ? ` blur(${p.veil}px)` : ''}`,
          }}
        />
        {p.crop !== undefined && p.crop < meta.h && (
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 70, background: `linear-gradient(transparent, ${C.sheet})`}} />
        )}
        <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
          <defs>
            <mask id={maskId}>
              <rect width={W} height={H} fill="#fff" />
              {started.flatMap((m) =>
                meta.highlights[m.i].rects.map((r, j) => (
                  <rect key={`${m.i}-${m.at}-${j}`} x={r.x * k - 6} y={r.y * k - 5} width={r.w * k + 12} height={r.h * k + 10} rx={4} fill="#000" />
                )),
              )}
            </mask>
          </defs>
          <rect width={W} height={H} fill={C.sheet} opacity={dimO} mask={`url(#${maskId})`} />
        </svg>
        {/* feutre : ligne après ligne, à la vitesse d'une main */}
        <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'multiply'}}>
          {marks.map((m, mi) => {
            let t0 = m.at;
            return meta.highlights[m.i].rects.map((r, j) => {
              const d = lineDur(r);
              const q = interpolate(frame, [t0, t0 + d], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
              t0 += d;
              if (q <= 0) return null;
              return (
                <rect
                  key={`${mi}-${j}`}
                  x={r.x * k - 4}
                  y={r.y * k + r.h * k * 0.06}
                  width={(r.w * k + 8) * q}
                  height={r.h * k * 0.92}
                  rx={3}
                  fill={TONE[m.tone ?? 'red'].mark}
                />
              );
            });
          })}
        </svg>
        {/* caviardage */}
        <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
          {marks
            .filter((m) => m.redact !== undefined)
            .flatMap((m) => {
              let t0 = m.redact as number;
              return meta.highlights[m.i].rects.map((r, j) => {
                const q = interpolate(frame, [t0, t0 + 10], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
                t0 += 9;
                return (
                  <rect key={`r${m.i}-${j}`} x={r.x * k - 5} y={r.y * k - 3} width={(r.w * k + 10) * q} height={r.h * k + 6} fill={C.ink} />
                );
              });
            })}
        </svg>
        </div>
        {/* lumière de la fenêtre sur toute la feuille, marge comprise */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(125deg, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0) 38%, rgba(40,36,30,0.06) 100%)',
            mixBlendMode: 'soft-light',
          }}
        />
      </div>

      {p.sub && (
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: SH + 26,
            width: W,
            fontFamily: F.serif,
            fontStyle: 'italic',
            fontSize: 38,
            color: C.ink,
          }}
        >
          {p.sub.text.split(' ').map((wd, i) => {
            const q = interpolate(frame, [p.sub!.at + i * 1.5, p.sub!.at + i * 1.5 + 6], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
            return (
              <span key={i} style={{display: 'inline-block', marginRight: '0.26em', opacity: q, transform: `translateY(${(1 - q) * 12}px)`}}>
                {wd}
              </span>
            );
          })}
        </div>
      )}
      </div>
      <div style={{...box, opacity: 1 - e, transform: flat}}>
      {/* crochet dans la marge + trait vers la fiche */}
      <svg width={SW + notesX + 40} height={SH + 600} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', pointerEvents: 'none'}}>
        {placed.map((it, i) => {
          if (it.mid === undefined || frame < it.n.at - 8) return null;
          const gone = it.n.until === undefined ? 1 : interpolate(frame, [it.n.until, it.n.until + 8], [1, 0], clamp);
          const b = interpolate(frame, [it.n.at - 8, it.n.at], [0, 1], {...clamp, easing: inOut});
          const bx = SW + 16;
          const cy = it.y + 40;
          return (
            <g key={i} opacity={gone} fill="none" stroke={C.ink} strokeWidth={1.6}>
              <path
                d={`M ${bx - 8} ${(it.top as number) - 2} L ${bx} ${(it.top as number) - 2} L ${bx} ${(it.bot as number) + 2} L ${bx - 8} ${(it.bot as number) + 2}`}
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - b}
              />
              <path
                d={`M ${bx} ${it.mid} C ${bx + 30} ${it.mid}, ${notesX - 30} ${cy}, ${notesX} ${cy}`}
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - b}
              />
              <circle cx={bx} cy={it.mid} r={3.5 * b} fill={C.ink} stroke="none" />
            </g>
          );
        })}
      </svg>

      {placed.map((it, i) => (
        <NoteCard key={i} n={it.n} x={notesX} y={it.y} w={notesW} tone={it.tone} />
      ))}

      </div>
    </div>
  );
};
