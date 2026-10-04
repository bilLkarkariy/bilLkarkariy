// Shorts 9:16 : un passage du montage 16:9, posé comme une feuille sur le papier, avec un titre
// au-dessus et les mots de la voix en grand en dessous (le mot dit s'allume en or).
// Rendu : npx remotion render out/bundle short-bouton out/short-bouton.mp4 --props='{"clean":true}'
import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {isRtl, Lang, translator} from './i18n';
import {RtlScope} from './i18n/rtl';
import {createCues, voices, LEAD, toF} from './cues';
import {C, F} from './theme';
import {V01} from './V01';

type Word = {w: string; start: number; end: number};
type Seg = {id: string; words: Word[]};

const W = 1080;
const K = W / 1920; // le 16:9 garde toute sa largeur : rien n'est rogné (les documents sont souvent à gauche)
const VIDEO_Y = 620;
const END = 75; // carton final, en images

export const getShorts = (lang: Lang = 'fr') => {
const {at} = createCues(lang);
const tx = translator(lang);
return [
  {
    id: 'short-bouton',
    title: [tx("Quinze minutes seul."), tx("Ou une décharge.")],
    from: at('p1') - LEAD,
    to: at('p13', undefined, 'end') + 18,
  },
  {
    id: 'short-pascal',
    title: [tx("Le téléphone"), tx("n’a rien inventé.")],
    from: at('p28') - 6,
    to: at('p36', undefined, 'end') + 24,
  },
  {
    id: 'short-exercice',
    title: [tx("Deux minutes,"), tx("ce soir.")],
    from: at('p54') - 6,
    to: at('p61', undefined, 'end') + 18,
  },
].map((s) => ({...s, id: s.id + (lang === 'fr' ? '' : `-${lang}`)}));
};
export const SHORTS = getShorts('fr');

/** Les mots de la voix, par petits groupes : coupés sur un silence ou tous les 3 mots. */
const groupsFor = (lang: Lang): Word[][] => {
  const out: Word[][] = [];
  for (const s of voices[lang].segments as Seg[]) {
    let cur: Word[] = [];
    for (const w of s.words) {
      if (cur.length && (cur.length >= 3 || w.start - cur[cur.length - 1].end > 0.3)) {
        out.push(cur);
        cur = [];
      }
      cur.push(w);
    }
    if (cur.length) out.push(cur);
  }
  return out;
};
const captionGroups = {fr: groupsFor('fr'), en: groupsFor('en'), ur: groupsFor('ur')};

const Captions: React.FC<{from: number; lang: Lang}> = ({from, lang}) => {
  const GROUPS = captionGroups[lang];
  const f = useCurrentFrame() + from; // image dans la vidéo longue
  const g = GROUPS.find((x, i) => {
    const a = LEAD + toF(x[0].start);
    const b = i + 1 < GROUPS.length ? LEAD + toF(GROUPS[i + 1][0].start) : a + 45;
    return f >= a && f < Math.min(b, LEAD + toF(x[x.length - 1].end) + 12);
  });
  if (!g) return null;
  return (
    <div
      style={{
        position: 'absolute',
        top: VIDEO_Y + 1080 * K + 90,
        left: 60,
        right: 60,
        textAlign: 'center',
        fontFamily: F.serif,
        fontSize: 84,
        lineHeight: 1.12,
        color: C.ink,
        ...(isRtl(lang) ? {lineHeight: 1.9, top: VIDEO_Y + 1080 * K + 60} : {}),
      }}
    >
      {g.map((w, i) => {
        const on = f >= LEAD + toF(w.start);
        return (
          <span key={i} style={{color: on ? C.ink : C.inkFaint, transition: 'none'}}>
            {i ? ' ' : ''}
            {w.w}
          </span>
        );
      })}
    </div>
  );
};

export const Short: React.FC<{from: number; to: number; title: string[]; lang?: Lang}> = ({from, to, title, lang = 'fr'}) => {
  const tx = translator(lang);
  const frame = useCurrentFrame();
  const len = to - from;
  const fadeOut = interpolate(frame, [len - 10, len], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const endIn = interpolate(frame, [len, len + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <RtlScope lang={lang}>
    <AbsoluteFill style={{background: C.paperWarm}}>
      <div style={{opacity: fadeOut}}>
        <div
          style={{
            position: 'absolute',
            top: 250,
            left: 70,
            right: 70,
            fontFamily: F.serif,
            fontSize: 92,
            lineHeight: 1.05,
            color: C.ink,
            textAlign: 'center',
            ...(isRtl(lang) ? {top: 190, lineHeight: 1.75} : {}),
          }}
        >
          {title.map((t, i) => (
            <div key={i} style={{fontStyle: i ? 'italic' : 'normal'}}>
              {t}
            </div>
          ))}
        </div>
        <div
          style={{
            position: 'absolute',
            top: VIDEO_Y,
            left: 0,
            width: 1920,
            height: 1080,
            transform: `scale(${K})`,
            transformOrigin: '0 0',
            overflow: 'hidden',
            boxShadow: '0 30px 80px rgba(0,0,0,0.25)',
          }}
        >
          <Sequence from={-from} durationInFrames={to}>
            <V01 lang={lang} />
          </Sequence>
        </div>
        <Sequence durationInFrames={len}>
          <Captions from={from} lang={lang} />
        </Sequence>
      </div>
      <AbsoluteFill
        style={{
          opacity: endIn,
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
          padding: 90,
          fontFamily: F.serif,
          color: C.ink,
        }}
      >
        <div style={{fontFamily: F.mono, fontSize: 30, letterSpacing: '0.18em', color: C.inkSoft}}>{tx("LA VIDÉO COMPLÈTE")}</div>
        <div style={{fontSize: 76, lineHeight: isRtl(lang) ? 1.9 : 1.1, marginTop: 40}}>{tx("Pourquoi tu n’arrives plus à rester seul avec toi-même")}</div>
        <div style={{width: 120, height: 3, background: C.gold, margin: '60px auto'}} />
        <div style={{fontFamily: F.mono, fontSize: 34, letterSpacing: '0.12em'}}>bilLkarkariy</div>
      </AbsoluteFill>
    </AbsoluteFill>
    </RtlScope>
  );
};

export const SHORT_END = END;
