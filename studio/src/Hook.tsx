import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {ARoll} from './components/ARoll';
import {Grain, Paper} from './components/Paper';
import {at, DURATION, VO_SRC} from './cues';
import {Card} from './scenes/Card';
import {Dots} from './scenes/Dots';
import {Maquette} from './scenes/Maquette';
import {Plan} from './scenes/Plan';
import {Study} from './scenes/Study';
import {C} from './theme';

// ── Script de montage (hook + début de l'expérience), accroché aux mots ────────────────────────────
const cut1 = at('s2') - 3; // A-roll -> maquette, juste avant « Seul »
const planIn = at('s4') - 10; // la maquette, vue de dessus, devient le plan
const xfade = 14;
const dotsIn = at('s6') - 5; // « Deux hommes sur trois »
const aroll2 = at('s8') - 3; // « Et je suis presque sûr… » : face caméra
const cardIn = at('s9') - 3; // « C'est une étude publiée dans Science »
const studyIn = at('s13') - 8; // « Université de Virginie » : chapitre 01
const black = at('s19', undefined, 'end') + 75; // le minuteur tourne 2 s, puis coupe sèche

const plan = {
  dot: at('s4', 'toi') - planIn,
  wander: at('s4', 'pensées') - planIn,
  button: at('s5', 'bouton') - planIn,
  zaps: [at('s5', 'décharge') - planIn, at('s5', 'électrique') - planIn],
  push: at('s5', undefined, 'end') + 4 - planIn,
  pushLen: 40,
};
const dots = {
  presses: [at('s6', 'appuyé') - dotsIn, at('s6', 'appuyé') + 8 - dotsIn],
  pct: at('s6', undefined, 'end') + 4 - dotsIn,
  before: at('s7', 'juste') - dotsIn,
  pay: at('s7', 'paieraient') - dotsIn,
};
const card = {
  scroll: at('s10') - cardIn,
  mark: at('s10', 'phrase') - cardIn,
  button: at('s11', 'bouton') - cardIn,
  redact: at('s12') - cardIn,
  extra: at('s12', "d'exercice") - cardIn,
  end: studyIn - cardIn,
};
const study = {
  place: at('s13', 'Université') - studyIn,
  students: at('s14', 'étudiants') - studyIn,
  walk1: [at('s14', 'entrent') - studyIn, at('s15', 'déposer') - studyIn] as [number, number],
  phone: at('s16', 'téléphone') - studyIn,
  pen: at('s16', 'stylos') - studyIn,
  walk2: [at('s17', 'Rien') - studyIn, at('s17', 'écrire', 'end') + 20 - studyIn] as [number, number],
  door: at('s17', 'écrire', 'end') + 24 - studyIn,
  slip: at('s18', 'consigne') - studyIn,
  words: ['reste', 'assis', 'ne', "t'endors", 'pas', 'occupe-toi', 'avec', 'tes', 'pensées'].map((w) => at('s18', w) - studyIn),
  timer: at('s19', 'Quinze') - studyIn,
  count: at('s19', undefined, 'end') + 6 - studyIn,
};

const sfx: [string, number, number][] = [
  ['phone_down', 14, 0.9],
  ['pencil', planIn + 2, 0.55],
  ['tick', at('s4', 'toi'), 0.7],
  ['pencil', at('s4', 'pensées'), 0.4],
  ['tick', at('s5', 'bouton'), 0.9],
  ['zap', at('s5', 'décharge'), 0.6],
  ['zap', at('s5', 'électrique'), 0.35],
  ['tick', dotsIn + 1, 0.5],
  ['tick', dotsIn + 5, 0.5],
  ['tick', dotsIn + 9, 0.5],
  ['button_click', dotsIn + dots.presses[0], 0.95],
  ['button_click', dotsIn + dots.presses[1], 0.85],
  ['sub', dotsIn + dots.pct, 0.38],
  ['paper', cardIn, 0.8],
  ['tick', cardIn + card.mark, 0.6],
  ['marker', cardIn + card.redact, 0.42],
  ['pencil', studyIn + 2, 0.45],
  ['tick', studyIn + study.students + 3, 0.4],
  ['tick', studyIn + study.students + 6, 0.4],
  ['tick', studyIn + study.students + 9, 0.4],
  ['tick', studyIn + study.phone + 12, 0.7],
  ['tick', studyIn + study.pen + 12, 0.7],
  ['door', studyIn + study.door, 0.8],
  ['paper', studyIn + study.slip, 0.7],
  ['clock', studyIn + study.count + 30, 0.6],
  ['clock', studyIn + study.count + 60, 0.6],
];

const Fade: React.FC<{from: number; len: number; out?: boolean; children: React.ReactNode}> = ({from, len, out, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [from, from + len], out ? [1, 0] : [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

export const HOOK_DURATION = Math.max(DURATION, black + 15);

export const Hook: React.FC = () => (
  <AbsoluteFill style={{background: C.paper}}>
    <Paper grid={0.8} />

    <Sequence from={cut1} durationInFrames={planIn + xfade - cut1}>
      <Fade from={planIn - cut1} len={xfade} out>
        <Maquette reachTop={planIn - cut1} phone={at('s3', 'téléphone') - cut1} read={at('s3', 'lire') - cut1} />
      </Fade>
    </Sequence>

    <Sequence from={planIn} durationInFrames={dotsIn + 6 - planIn}>
      <Fade from={dotsIn - planIn} len={6} out>
        <Plan {...plan} />
      </Fade>
    </Sequence>

    <Sequence from={dotsIn} durationInFrames={aroll2 - dotsIn}>
      <Dots {...dots} />
    </Sequence>

    <Sequence from={cardIn} durationInFrames={studyIn - cardIn}>
      <Card {...card} />
    </Sequence>

    <Sequence from={studyIn} durationInFrames={black - studyIn}>
      <Study {...study} />
    </Sequence>

    {/* face caméra : emplacements à remplacer par les rushes */}
    <Sequence from={0} durationInFrames={cut1}>
      <ARoll shot="PLAN SERRÉ · il retourne son téléphone sur le bureau" line="« Quinze minutes. »" />
    </Sequence>
    <Sequence from={aroll2} durationInFrames={cardIn - aroll2}>
      <ARoll shot="REGARD CAMÉRA" line="« Et je suis presque sûr que toi aussi, tu aurais appuyé. »" />
    </Sequence>

    <Sequence from={black}>
      <AbsoluteFill style={{background: C.night}} />
    </Sequence>

    <Grain />

    {/* son */}
    <Audio src={staticFile(VO_SRC)} />
    {sfx.map(([name, f, v], i) => (
      <Sequence key={i} from={f} durationInFrames={60}>
        <Audio src={staticFile(`sfx/${name}.wav`)} volume={v} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
