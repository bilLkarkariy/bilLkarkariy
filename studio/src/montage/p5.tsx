import React from 'react';
import {Sequence} from 'remotion';
import {ARoll, FACELESS} from '../components/ARoll';
import {Citation} from '../components/Citation';
import {Lift, Shot3D} from '../components/Light';
import {createCues} from '../cues';
import {Lang, translator} from '../i18n';
import {DayTicks} from '../scenes/Part3';
import {Kinetic} from '../scenes/Part4';
import {ButtonPhone, EndCard, Lines, Reps, StepChair, StepNoise, StepNum, StepPhone, StepPoint, StepReturn, Urge} from '../scenes/Part5';
import {Cit, citSfx, Fade, Sfx} from './kit';

const makeP5 = (lang: Lang) => {
const {at} = createCues(lang);
const tx = translator(lang);

// ── Partie 5 (7:29 → fin) : l'exercice, l'envie de se lever, le bouton dans la poche, ──────────
//    la dernière phrase de l'étude (enfin lisible), la pièce meublée. p54 → p68.
//    L'exercice est raconté : aucun minuteur à l'écran, aucun silence de deux minutes.

const aroll7 = at('p54') - 6; // « Je ne vais pas te demander… deux minutes »
const s1 = at('p55') - 8;
const s2 = at('p56') - 6;
const s3 = at('p57') - 6;
const s4 = at('p58') - 6;
const s5 = at('p59') - 6;
const urgeIn = at('p60') - 6;
const repsIn = at('p61') - 6;
const pocketIn = at('p62') - 6;
const finIn = at('p64') - 6;
const aroll8 = at('p66') - 6;
const meubleeIn = at('p67', 'meublé') - 10; // = t0 de tools/plans3d.py meublee
const meubleeN = at('p68') + 30 - meubleeIn;
const aroll9 = at('p68') - 2;
const endIn = at('p68', undefined, 'end') + 20;
const P5_END = endIn + 6 * 30; // l'écran de fin : 6 s pour les éléments YouTube

const L = (id: string, w: string, from: number, nth = 0) => at(id, w, 'start', nth) - from;

const cits: Cit[] = [
  // p64-p65 : la dernière phrase, promise depuis le début : le flou se lève, le caviardage s'arrache
  {
    from: finIn,
    to: aroll8 + 6,
    cap: 'pmc_fin',
    x: 110,
    width: 1100,
    y: 360,
    tilt: 0.5,
    tag: 'SCIENCE · 2014 · WILSON ET AL. · DERNIER PARAGRAPHE',
    veil: 7,
    veilOff: L('p65', "L'esprit", finIn) - 10,
    dim: 0.55,
    marks: [
      {
        i: 0,
        at: L('p65', "L'esprit", finIn) + 6,
        tone: 'gold',
        redact: -40,
        unredact: L('p65', "L'esprit", finIn) - 6,
        note: {
          at: L('p65', 'non', finIn),
          kicker: tx("LA DERNIÈRE PHRASE DE L’ÉTUDE"),
          text: tx("« L’esprit non entraîné n’aime pas être seul avec lui-même. »"),
          tone: 'gold',
          y: -40,
        },
      },
    ],
  },
];

const P5_SFX: Sfx[] = [
  ...[s1, s2, s3, s4, s5].map((f) => ['tick', f + 4, 0.6] as Sfx),
  ['poche', at('p55', 'téléphone'), 0.6],
  ['porte', at('p55', 'autre') + 22, 0.3],
  ['horloge', at('p55', 'minuteur'), 0.5],
  ['notification', at('p55', 'sonnera'), 0.2],
  ['toc_mur', at('p56', 'Assieds-toi') + 8, 0.5],
  ['voiture', at('p57', 'Faut') - 10, 0.25],
  ['notification', at('p57', 'Faut') + 4, 0.3],
  ['voiture', at('p57', "J'ai") - 10, 0.25],
  ['voiture', at('p57', 'voitures'), 0.45],
  ['respiration', at('p58', 'respiration') - 6, 0.45],
  ['carillon', at('p58', 'point'), 0.3],
  ['carillon', at('p59', 'reviens') + 20, 0.35],
  ...[0, 1, 2, 3, 4].map((k) => ['horloge', at('p60', 'vite') + k * 30, 0.3] as Sfx),
  ['bouton', at('p61', 'bouton'), 0.8],
  ...Array.from({length: 12}, (_, k) => ['craie', at('p61', 'Chaque') + k * 7, 0.35] as Sfx),
  ['bouton', at('p62', 'bouton'), 0.6],
  ['notification', at('p63', 'poche') + 10, 0.45],
  ['arrachage', at('p65', "L'esprit") - 6, 0.7],
  ['carillon', at('p65', 'seul'), 0.35],
  ['carillon', meubleeIn + 10, 0.3],
  ...citSfx(cits),
];

const P5: React.FC = () => (
  <>
    {/* 1 · le téléphone dans une autre pièce */}
    <Sequence from={s1} durationInFrames={s2 - s1}>
      <Fade from={s2 - s1 - 8} len={8} out>
        <StepNum n={1} />
        <Lines
          x={150}
          y={600}
          lines={[
            {t: tx("Ton téléphone"), at: L('p55', 'Ton', s1)},
            {t: tx("dans une autre pièce."), at: L('p55', 'autre', s1)},
            {t: tx("Pas retourné à côté de toi."), at: L('p55', 'Pas', s1), size: 36, italic: true},
            {t: tx("Un minuteur ? Lance-le avant."), at: L('p55', 'minuteur', s1), size: 36, italic: true},
          ]}
        />
        <Lift>
          <StepPhone
            phone={L('p55', 'téléphone', s1)}
            other={L('p55', 'autre', s1)}
            notNext={L('p55', 'Pas', s1)}
            timer={L('p55', 'minuteur', s1)}
            ring={L('p55', 'sonnera', s1)}
          />
        </Lift>
      </Fade>
    </Sequence>

    {/* 2 · une chaise suffit */}
    <Sequence from={s2} durationInFrames={s3 - s2}>
      <Fade from={s3 - s2 - 8} len={8} out>
        <StepNum n={2} />
        <Lines
          x={150}
          y={600}
          lines={[
            {t: tx("Assieds-toi."), at: L('p56', 'Assieds-toi', s2)},
            {t: tx("Rien d’héroïque."), at: L('p56', 'Rien', s2), size: 40, italic: true},
            {t: tx("Une chaise suffit."), at: L('p56', 'Une', s2), size: 40, italic: true},
          ]}
        />
        <Lift>
          <StepChair sit={L('p56', 'Assieds-toi', s2)} />
        </Lift>
      </Fade>
    </Sequence>

    {/* 3 · regarder le bruit */}
    <Sequence from={s3} durationInFrames={s4 - s3}>
      <Fade from={s4 - s3 - 8} len={8} out>
        <StepNum n={3} />
        <Lines
          x={150}
          y={600}
          lines={[
            {t: tx("Une minute :"), at: L('p57', 'Pendant', s3)},
            {t: tx("regarde le bruit."), at: L('p57', 'regarde', s3)},
            {t: tx("Tu ne chasses rien."), at: L('p57', 'Tu', s3), size: 36, italic: true},
            {t: tx("Tu remarques."), at: L('p57', 'Tu', s3, 1), size: 36, italic: true},
          ]}
        />
        <Lift>
          <StepNoise
            bubbles={[
              {t: tx("« Faut que je réponde à ce message. »"), at: L('p57', 'Faut', s3) - 14, lane: 0},
              {t: tx("« J’ai oublié le pain. »"), at: L('p57', "J'ai", s3) - 14, lane: 2},
              {t: tx("« Et demain, la réunion… »"), at: L('p57', 'voitures', s3) - 20, lane: 1},
              {t: tx("« Il faut que je rappelle… »"), at: L('p57', 'fenêtre', s3) - 14, lane: 3},
            ]}
            flood={L('p57', 'surpris', s3) - 16}
            still={L('p57', 'chasses', s3)}
          />
        </Lift>
      </Fade>
    </Sequence>

    {/* 4 · un seul point : la respiration, ou un mot (chez nous : Astaghfirullāh) */}
    <Sequence from={s4} durationInFrames={s5 - s4}>
      <Fade from={s5 - s4 - 8} len={8} out>
        <StepNum n={4} />
        <Lines
          x={150}
          y={600}
          lines={[
            {t: tx("Un seul point :"), at: L('p58', 'Pose', s4)},
            {t: tx("ta respiration,"), at: L('p58', 'Ta', s4), size: 40, italic: true},
            {t: tx("ou un mot qui compte pour toi."), at: L('p58', 'Ou', s4), size: 40, italic: true},
          ]}
        />
        <StepPoint
          point={L('p58', 'point', s4)}
          breath={L('p58', 'respiration', s4)}
          word={L('p58', 'répété', s4)}
          ar={L('p58', 'Astaghfiroullah', s4) - 4}
          arGloss={L('p58', 'demande', s4)}
        />
      </Fade>
    </Sequence>

    {/* 5 · tu pars, tu reviens, sans te juger */}
    <Sequence from={s5} durationInFrames={urgeIn - s5}>
      <Fade from={urgeIn - s5 - 8} len={8} out>
        <StepNum n={5} />
        <Lines
          x={150}
          y={600}
          lines={[
            {t: tx("Tu pars."), at: L('p59', 'pars', s5)},
            {t: tx("Tu reviens."), at: L('p59', 'reviens', s5)},
          ]}
        />
        <StepReturn away={L('p59', 'pars', s5)} back={L('p59', 'reviens', s5)} judge={L('p59', 'Sans', s5)} />
      </Fade>
    </Sequence>

    {/* p60 : quarante secondes, et l'envie de se lever */}
    <Sequence from={urgeIn} durationInFrames={repsIn - urgeIn}>
      <Fade from={repsIn - urgeIn - 8} len={8} out>
        <Kinetic lines={[{t: tx("CE QUI VA PROBABLEMENT SE PASSER"), at: 4, y: 130, size: 24, mono: true, stagger: 3}]} />
        <Lift>
          <Urge
            t40={[L('p60', 'vite', urgeIn), L('p60', 'secondes', urgeIn)]}
            itch={L('p60', 'envie', urgeIn)}
            chips={[
              {t: tx("TE LEVER"), at: L('p60', 'lever', urgeIn)},
              {t: tx("VÉRIFIER UN TRUC"), at: L('p60', 'Vérifier', urgeIn)},
              {t: tx("LE TÉLÉPHONE…"), at: L('p60', 'téléphone', urgeIn)},
              {t: tx("« JUSTE POUR L’HEURE »"), at: L('p60', 'juste', urgeIn)},
            ]}
          />
        </Lift>
      </Fade>
    </Sequence>

    {/* p61 : c'est le bouton de l'étude ; chaque retour compte */}
    <Sequence from={repsIn} durationInFrames={pocketIn - repsIn}>
      <Fade from={pocketIn - repsIn - 8} len={8} out>
        <Lift>
          <Reps button={L('p61', 'bouton', repsIn)} count={L('p61', 'Chaque', repsIn)} />
        </Lift>
        <Kinetic
          lines={[
            {t: tx("Tu n’as pas raté l’exercice."), at: L('p61', 'Tu', repsIn), y: 560, size: 54, italic: true, out: L('p61', 'Chaque', repsIn) - 8},
            {t: tx("C’est ça, l’exercice."), at: L('p61', "C'est", repsIn), y: 650, size: 72, gold: [tx("l’exercice.")], out: L('p61', 'Chaque', repsIn) - 8},
            {t: tx("chaque retour compte"), at: L('p61', 'Chaque', repsIn), y: 560, size: 54, italic: true},
            {t: tx("CE SOIR · 2 MIN   DEMAIN · 3 MIN"), at: L('p61', 'Deux', repsIn), y: 700, size: 30, mono: true, stagger: 5},
          ]}
        />
      </Fade>
    </Sequence>

    {/* p62-p63 : revenons au bouton : il est dans ta poche */}
    <Sequence from={pocketIn} durationInFrames={finIn + 6 - pocketIn}>
      <Fade from={finIn - pocketIn - 2} len={8} out>
        <Lift>
          <ButtonPhone morph={L('p63', 'poche', pocketIn) - 10} warm={L('p63', 'bien', pocketIn)} />
        </Lift>
        <Kinetic
          lines={[
            {t: tx("Le bouton, tu l’as dans ta poche."), at: L('p63', 'Mais', pocketIn), y: 90, size: 52, italic: true, red: [tx("bouton,")], out: L('p63', 'Lui', pocketIn) - 6},
            {t: tx("Lui ne fait pas mal. Il fait même du bien."), at: L('p63', 'Lui', pocketIn), y: 90, size: 52, italic: true, out: L('p63', "C'est", pocketIn) - 6},
            {t: tx("une vingtaine de fois par jour, sans y penser"), at: L('p63', 'vingtaine', pocketIn) - 4, y: 90, size: 52, italic: true},
          ]}
        />
        <Lift>
          <DayTicks start={L('p63', 'vingtaine', pocketIn)} y={940} />
        </Lift>
      </Fade>
    </Sequence>

    {cits.map(({from, to, sound, ...p}, i) => (
      <Sequence key={i} from={from} durationInFrames={to - from}>
        <Citation {...p} />
      </Sequence>
    ))}

    {/* « Tu n'as juste jamais meublé la pièce » : la pièce meublée (3D, une image sur trois) */}
    <Sequence from={meubleeIn} durationInFrames={aroll9 - meubleeIn}>
      <Shot3D dir="meublee" frames={meubleeN} step={3} label={tx("La même pièce, lumière dorée : le pion assis près du point d'or. La caméra s'élève.")} />
    </Sequence>

    <Sequence from={endIn}>
      <EndCard />
    </Sequence>
  </>
);

const P5Front: React.FC = () => (
  <>
    {!FACELESS && (
      <Sequence from={aroll7} durationInFrames={s1 - aroll7}>
        <ARoll shot={tx("PLAN POITRINE · proche, une invitation")} line={tx("« Je ne vais pas te demander trois jours, encore moins quarante. Ce soir, je te demande deux minutes. »")} />
      </Sequence>
    )}
    {!FACELESS && (
      <Sequence from={aroll8} durationInFrames={meubleeIn - aroll8}>
        <ARoll shot={tx("GROS PLAN SERRÉ · le plus calme")} line={tx("« Non entraîné. Tout est dans ce mot. Ça veut dire que ça s'entraîne. »")} />
      </Sequence>
    )}
    {!FACELESS && (
      <Sequence from={aroll9} durationInFrames={endIn - aroll9}>
        <ARoll shot={tx("PLAN POITRINE · plus léger, petit sourire")} line={tx("« Prochaine vidéo : pourquoi essayer de ne penser à rien marche si mal… »")} />
      </Sequence>
    )}
  </>
);

return {P5, P5Front, P5_SFX, P5_END};
};
const versions = {fr: makeP5('fr'), en: makeP5('en'), ur: makeP5('ur')};
export const getP5 = (lang: Lang) => versions[lang];
export const {P5, P5Front, P5_SFX, P5_END} = versions.fr;
