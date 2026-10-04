import React from 'react';
import {Audio, interpolate, Sequence, staticFile} from 'remotion';
import {voices} from '../cues';
import {Lang, useLang} from '../i18n';
import {LEAD, toF} from '../cues';

// La musique s'efface sous la voix, mot à mot (attaque rapide, retour lent),
// et se tait complètement dans les fenêtres `silence` (le verset).

const envelope = (lang: Lang) => {
const vo = voices[lang];
const words = (vo.segments as {words: {start: number; end: number}[]}[]).flatMap((s) => s.words);
const N = LEAD + toF(vo.duration) + 600;
const speaking = new Float32Array(N);
for (const w of words) {
  for (let f = Math.max(0, LEAD + toF(w.start) - 5); f < Math.min(N, LEAD + toF(w.end) + 8); f++) speaking[f] = 1;
}
// enveloppe : descend en 6 images, remonte en 24
const env = new Float32Array(N);
{
  let v = 0;
  for (let f = 0; f < N; f++) {
    const target = speaking[f];
    v += target > v ? (target - v) / 6 : (target - v) / 24;
    env[f] = v;
  }
}

return {env, N};
};
const envelopes = {fr: envelope('fr'), en: envelope('en'), ur: envelope('ur')};

export type Cue = {src: string; from: number; to: number; gain?: number; fadeIn?: number; fadeOut?: number; startFrom?: number};

export const Music: React.FC<{cues: Cue[]; duck?: number; silence?: [number, number][]}> = ({cues, duck = 0.32, silence = []}) => {
  const {env, N} = envelopes[useLang()];
  return (
  <>
    {cues.map((c, i) => (
      <Sequence key={i} from={c.from} durationInFrames={c.to - c.from}>
        <Audio
          src={staticFile(c.src)}
          startFrom={c.startFrom ?? 0}
          volume={(lf) => {
            const f = c.from + lf;
            const fade = interpolate(lf, [0, c.fadeIn ?? 30, c.to - c.from - (c.fadeOut ?? 45), c.to - c.from], [0, 1, 1, 0], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            const mute = silence.reduce(
              (m, [a, b]) => Math.min(m, interpolate(f, [a - 30, a, b, b + 30], [1, 0, 0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})),
              1,
            );
            const d = 1 - (1 - duck) * (env[Math.min(N - 1, Math.max(0, f))] ?? 0);
            return (c.gain ?? 0.22) * fade * d * mute;
          }}
        />
      </Sequence>
    ))}
  </>
);
};
