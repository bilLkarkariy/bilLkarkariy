import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {hl} from '../captures';
import {ARoll, FACELESS} from '../components/ARoll';
import {Citation, NoteCard} from '../components/Citation';
import {Lift} from '../components/Light';
import {Paper} from '../components/Paper';
import {createCues} from '../cues';
import {isRtl, Lang, translator} from '../i18n';
import {DayTicks, Elevator, FilmStrip, Night, PocketDoor, Queue, Years} from '../scenes/Part3';
import {Cit, citSfx, Fade, Sfx} from './kit';

const makeP3 = (lang: Lang) => {
const {at} = createCues(lang);
const tx = translator(lang);

// ── Partie 3 (2:27 → 4:28) : le scénariste fatigué, Harvard 2010, les écrans, Pascal ─────────────
//    p20 → p34. Les vraies pages : Wilson (PMC), Killingsworth & Gilbert (Science 2010, PDF),
//    Médiamétrie, Arcep, le manuscrit de Pascal (BnF) et sa transcription.

const filmIn = at('p20', 'film') - 4;
const queueIn = at('p21') - 4;
const aroll4 = at('p22') - 6; // « Question. … c'était quand ? » + 2 s de silence
const kgIn = at('p23') - 8;
const methIn = at('p23', 'sonner') - 6;
const resIn = at('p24') - 8;
const titleIn = at('p25', 'Leur') - 6;
const liftIn = at('p26') - 4;
const cutIn = at('p27') - 4;
const mmIn = at('p27', 'France') - 6;
const mm2In = at('p27', 'dont') - 6;
const sessIn = at('p27', 'Médiamétrie') - 4;
const arcepIn = at('p27', 'Et') - 6;
const warmIn = at('p28') - 4; // le papier se réchauffe : on quitte la science pour la tradition
const yearsIn = at('p28') + 2;
const pascalIn = at('p29', 'siècle') - 6; // (le compteur s'arrête sur 1670 pendant « Blaise Pascal »)
const ro210In = at('p30', 'quelques') - 4;
const years2In = at('p31') - 4;
const pocketIn = at('p31', 'téléphone') - 6;
const nightIn = at('p32') - 6;
const aroll5 = at('p33') - 6;
const P3_END = at('p35') - 4; // (la pièce vide prend le relais, src/montage/p4.tsx)

const SHEET = {x: 110, width: 1100};
const KG = 'SCIENCE · 2010 · KILLINGSWORTH & GILBERT';
const fr = (n: number) => n.toLocaleString(lang === 'fr' ? 'fr-FR' : 'en-GB').replace(/\s/g, ' ');

const cits: Cit[] = [
  // p20 : « Penser seul, c'est être en même temps le scénariste et le spectateur du film »
  {
    from: at('p20') - 4,
    to: filmIn + 8,
    cap: 'pmc_scenariste',
    ...SHEET,
    y: 380,
    crop: 150,
    tilt: -0.4,
    tag: 'SCIENCE · 2014 · WILSON ET AL. · ÉTUDES 1 À 7',
    out: filmIn - 6 - (at('p20') - 4),
    marks: [
      {
        i: hl('pmc_scenariste', 'a “script writer”'),
        at: at('p20', 'image') - (at('p20') - 4),
        tone: 'ink',
        note: {
          at: at('p20', 'ça') - (at('p20') - 4),
          kicker: tx("L'IMAGE DES AUTEURS"),
          text: tx("Penser seul, c’est tenir deux rôles à la fois"),
          chips: [
            {t: tx("SCÉNARISTE"), at: at('p20', 'scénariste') - (at('p20') - 4)},
            {t: tx("SPECTATEUR"), at: at('p20', 'spectateur') - (at('p20') - 4)},
          ],
        },
      },
      {i: hl('pmc_scenariste', 'choose a topic'), at: at('p20', 'scénariste') - (at('p20') - 4), tone: 'gold'},
      {i: hl('pmc_scenariste', 'decide what'), at: at('p20', 'scénariste') + 10 - (at('p20') - 4), tone: 'gold'},
      {i: hl('pmc_scenariste', 'then mentally'), at: at('p20', 'spectateur') - (at('p20') - 4), tone: 'gold'},
    ],
  },
  // p23 : Harvard, 2010
  {
    from: kgIn,
    to: methIn + 8,
    cap: 'kg_page',
    x: 210,
    width: 700,
    y: 60,
    tilt: -0.8,
    tag: 'SCIENCE · 12 NOVEMBRE 2010',
    out: methIn - 6 - kgIn,
    dim: 0.3,
    marks: [
      {i: hl('kg_page', '12 NOVEMBER'), at: at('p23', 'dix') - kgIn, tone: 'ink'},
      {
        i: hl('kg_page', 'Harvard'),
        at: at('p23', 'Harvard') - kgIn,
        note: {at: at('p23', 'Harvard') + 4 - kgIn, kicker: tx("DEUX CHERCHEURS"), big: tx("Harvard"), text: tx("en 2010"), y: 560},
      },
    ],
  },
  {
    from: methIn,
    to: resIn + 8,
    cap: 'kg_methode',
    x: 250,
    width: 640,
    y: 110,
    tilt: 0.6,
    tag: KG + ' · MÉTHODE',
    out: resIn - 6 - methIn,
    notesX: 720,
    marks: [
      {
        i: hl('kg_methode', 'contacts participants'),
        at: at('p23', 'sonner') - methIn,
        note: {
          at: at('p23', 'téléphone') - methIn,
          kicker: tx("UNE APPLI SUR LEUR iPHONE"),
          text: tx("Le téléphone sonne à des moments pris au hasard"),
          until: at('p23', 'deux', 'start', 2) - 2 - methIn,
        },
      },
      {
        i: hl('kg_methode', '2250 adults'),
        at: at('p23', 'deux', 'start', 2) - methIn,
        note: {
          at: at('p23', 'deux', 'start', 2) + 2 - methIn,
          kicker: tx("ADULTES"),
          count: {to: 2250, from: 0, dur: 26, fmt: fr},
          text: tx("personnes"),
          until: at('p23', 'Trois') - 2 - methIn,
          y: 120,
        },
      },
      {i: hl('kg_methode', 'What are you doing'), at: at('p23', "qu'est-ce") - methIn},
      {i: hl('kg_methode', 'How are you feeling'), at: at('p23', 'comment') - methIn},
    ],
    notes: [
      {
        at: at('p23', 'Trois') - methIn,
        kicker: tx("TROIS QUESTIONS"),
        chips: [
          {t: tx("QU'EST-CE QUE TU FAIS ?"), at: at('p23', "qu'est-ce") - methIn},
          {t: tx("COMMENT TU TE SENS ?"), at: at('p23', 'comment') - methIn},
          {t: tx("TU PENSES À CE QUE TU FAIS ?"), at: at('p23', 'penses') - methIn, dot: true},
        ],
        tone: 'red',
        y: 160,
      },
    ],
  },
  // p24-p25 : près d'une fois sur deux, non ; et on est moins heureux
  {
    from: resIn,
    to: titleIn + 8,
    cap: 'kg_resultats',
    x: 300,
    width: 560,
    y: 110,
    tilt: -0.5,
    tag: KG + ' · RÉSULTATS',
    out: titleIn - 6 - resIn,
    notesX: 640,
    marks: [
      {i: hl('kg_resultats', 'Are you thinking'), at: 6, tone: 'ink'},
      {
        i: hl('kg_resultats', 'Mind wandering occurred'),
        at: at('p24', 'fois') - resIn,
        note: {
          at: at('p24', 'deux') - resIn,
          kicker: tx("TU PENSES À CE QUE TU FAIS ? « NON »"),
          count: {to: 469, dur: 22, fmt: (n) => `${(n / 10).toFixed(1).replace('.', lang === 'fr' ? ',' : '.')}${isRtl(lang) ? '%' : ' %'}`},
          text: tx("du temps : près d’une fois sur deux"),
          until: at('p25', 'moins') - 2 - resIn,
          y: 140,
        },
      },
      {
        i: hl('kg_resultats', 'people were less happy'),
        at: at('p25', 'ailleurs') - resIn,
        note: {at: at('p25', 'moins') - resIn, kicker: tx("QUAND L'ESPRIT EST AILLEURS"), big: tx("Moins heureux"), y: 520},
      },
    ],
  },
  {
    from: titleIn,
    to: liftIn + 8,
    cap: 'kg_page',
    ...SHEET,
    y: 300,
    crop: 168,
    tilt: 0.4,
    tag: KG + ' · LE TITRE',
    out: liftIn - 6 - titleIn,
    marks: [{i: hl('kg_page', 'A Wandering Mind'), at: at('p25', 'article') - titleIn}],
    sub: {text: tx("« Un esprit qui vagabonde est un esprit malheureux »"), at: at('p25', 'Un') - titleIn},
  },
  // p27 : les écrans, en France
  {
    from: mmIn,
    to: sessIn + 8,
    cap: 'mm_3h',
    x: 150,
    width: 1000,
    inset: 34,
    y: 300,
    tilt: -0.5,
    tag: "MÉDIAMÉTRIE · L'ANNÉE INTERNET 2025",
    out: sessIn - 6 - mmIn,
    marks: [
      {
        i: 0,
        at: at('p27', 'plus') - mmIn,
        note: {at: at('p27', 'heures') - mmIn, kicker: tx("EN FRANCE, CHAQUE JOUR"), big: tx("+ de 3 h"), text: tx("en ligne : un record"), y: -40},
      },
    ],
  },
  {
    from: mm2In,
    to: sessIn + 8,
    cap: 'mm_mobile',
    x: 190,
    width: 1000,
    inset: 34,
    y: 620,
    tilt: 0.6,
    out: sessIn - 6 - mm2In,
    marks: [{i: 0, at: at('p27', 'quatre-vingts') - mm2In, note: {at: at('p27', 'mobile') - mm2In, big: tx("80 %"), text: tx("du temps sur Internet : sur mobile"), y: -20}}],
  },
  {
    from: arcepIn,
    to: warmIn + 14,
    cap: 'arcep_2025',
    x: 200,
    width: 900,
    inset: 36,
    y: 420,
    tilt: -0.4,
    tag: 'ARCEP · BAROMÈTRE DU NUMÉRIQUE 2025',
    out: warmIn - arcepIn,
    marks: [
      {
        i: 0,
        at: at('p27', 'quatre') - arcepIn,
        note: {at: at('p27', 'Français') - arcepIn, kicker: tx("42 % DES FRANÇAIS"), big: tx("4 sur 10"), text: tx("trouvent qu’ils passent trop de temps devant les écrans"), y: -60},
      },
    ],
  },
  // p29-p30 : Pascal, le manuscrit (BnF) et sa transcription
  {
    from: pascalIn,
    to: ro210In + 10,
    cap: 'pascal_ro139',
    x: 150,
    width: 560,
    y: 150,
    tilt: -1.6,
    tag: 'BLAISE PASCAL · PENSÉES · MANUSCRIT AUTOGRAPHE',
    out: ro210In - pascalIn,
    dim: 0,
    sound: 'manuscrit',
    marks: [
      {i: 0, at: at('p29', 'Tout') - pascalIn, tone: 'gold'},
      {i: 1, at: at('p29', 'vient') - pascalIn, tone: 'gold'},
    ],
  },
  {
    from: at('p29', 'Tout') - 12,
    to: ro210In + 10,
    cap: 'pascal_chambre',
    x: 800,
    width: 1020,
    inset: 32,
    y: 470,
    tilt: 0.7,
    tag: 'TRANSCRIPTION · PENSEESDEPASCAL.FR',
    out: ro210In - (at('p29', 'Tout') - 12),
    dim: 0.35,
    marks: [{i: 0, at: 12, tone: 'gold'}],
  },
  {
    from: ro210In,
    to: years2In + 8,
    cap: 'pascal_ro210',
    x: 190,
    width: 560,
    y: 130,
    tilt: 1.3,
    tag: '… QUELQUES LIGNES PLUS LOIN',
    out: years2In - 6 - ro210In,
    dim: 0,
    sound: 'manuscrit',
    marks: [{i: 0, at: at('p30', 'De') - ro210In, tone: 'gold'}],
  },
  {
    from: at('p30', 'De') - 12,
    to: years2In + 8,
    cap: 'pascal_solitude',
    x: 800,
    width: 1020,
    inset: 32,
    y: 520,
    tilt: -0.5,
    tag: 'TRANSCRIPTION · PENSEESDEPASCAL.FR',
    out: years2In - 6 - (at('p30', 'De') - 12),
    dim: 0.35,
    marks: [{i: 0, at: 12, tone: 'gold'}],
  },
];

const P3_SFX: Sfx[] = [
  ['projecteur', filmIn + 2, 0.35],
  ['pellicule_vrille', at('p20', 'part'), 0.5],
  ['tick', queueIn + 10, 0.4],
  ['tick', queueIn + 14, 0.4],
  ['tick', queueIn + 18, 0.4],
  ['poche', at('p21', 'poche') - 6, 0.7],
  ['notification', at('p21', 'poche') + 6, 0.35],
  ['ascenseur', liftIn + 4, 0.45],
  ['souffle_ecran', at('p26', 'écran') - 4, 0.5],
  ['projecteur', cutIn + 2, 0.3],
  ['ciseaux', at('p27', 'coupe'), 0.8],
  ['fiche', sessIn + 6, 0.45],
  ['compteur', at('p28', 'smartphone'), 0.6],
  ['compteur', years2In + 6, 0.6],
  ['porte', at('p31', 'ouverte'), 0.35],
  ['nuit', nightIn + 4, 0.55],
  ['souffle_ecran', at('p32', "l'écran") - 6, 0.55],
  ...citSfx(cits),
];

/** Sous tout le reste : le papier se réchauffe à partir de Pascal. */
const P3Back: React.FC = () => (
  <Sequence from={warmIn}>
    <Fade from={0} len={24}>
      <Paper warm />
    </Fade>
  </Sequence>
);

/** Ce qui est posé sur le bureau (sous la lumière de la fenêtre). */
const P3: React.FC = () => (
  <>
    {/* p20 : la pellicule ; quand le scénariste fatigue, le film part dans tous les sens */}
    <Sequence from={filmIn} durationInFrames={queueIn + 8 - filmIn}>
      <Fade from={queueIn - filmIn} len={8} out>
        <Lift>
          <FilmStrip tired={at('p20', 'fatigue') - filmIn} chaos={at('p20', 'part') - filmIn} />
        </Lift>
      </Fade>
    </Sequence>

    <Sequence from={queueIn} durationInFrames={aroll4 - queueIn}>
      <Lift>
        <Queue
          file={at('p21', 'File') - queueIn}
          three={at('p21', 'trois') - queueIn}
          you={at('p21', 'toi') - queueIn}
          hand={at('p21', 'poche') - 8 - queueIn}
          decide={at('p21', 'décidé') - queueIn}
        />
      </Lift>
    </Sequence>

    <Sequence from={liftIn} durationInFrames={cutIn - liftIn}>
      <Lift>
        <Elevator
          twenty={at('p26', 'Vingt') - liftIn}
          ceiling={at('p26', 'plafond') - liftIn}
          floor={at('p26', 'sol') - liftIn}
          screen={at('p26', 'écran') - 4 - liftIn}
        />
      </Lift>
    </Sequence>

    {/* p27 : « Le téléphone coupe le film avant qu'il parte en vrille » */}
    <Sequence from={cutIn} durationInFrames={mmIn + 8 - cutIn}>
      <Fade from={mmIn - cutIn} len={8} out>
        <Lift>
          <FilmStrip tired={0} chaos={4} cut={at('p27', 'coupe') + 4 - cutIn} />
        </Lift>
      </Fade>
    </Sequence>

    {/* Médiamétrie : la page « 20 sessions » n'est plus en ligne, la fiche seule */}
    <Sequence from={sessIn} durationInFrames={arcepIn + 6 - sessIn}>
      <Fade from={arcepIn - sessIn - 6} len={10} out>
        <AbsoluteFill>
          <NoteCard
            n={{at: 6, kicker: tx("MÉDIAMÉTRIE · CHAQUE JOUR"), count: {to: 20, dur: 24, fmt: (n) => `≈ ${n}`}, text: tx("sessions sur smartphone")}}
            x={690}
            y={250}
            w={540}
            tone="red"
          />
          <Lift>
            <DayTicks start={10} />
          </Lift>
        </AbsoluteFill>
      </Fade>
    </Sequence>

    {/* p28 : 2025 → 1670 ; p31 : 1670 → 2025 */}
    <Sequence from={yearsIn} durationInFrames={pascalIn + 8 - yearsIn}>
      <Lift>
        <Years
          from={2025}
          to={1670}
          start={at('p28', 'smartphone') - yearsIn}
          len={at('p29', 'Blaise') - at('p28', 'smartphone')}
          label={tx("BLAISE PASCAL · PENSÉES · 1670")}
          labelAt={at('p29', 'Blaise') - yearsIn}
          out={pascalIn - yearsIn - 2}
        />
      </Lift>
    </Sequence>

    {cits.map(({from, to, sound, ...p}, i) => (
      <Sequence key={i} from={from} durationInFrames={to - from}>
        <Citation {...p} />
      </Sequence>
    ))}

    <Sequence from={years2In} durationInFrames={pocketIn + 8 - years2In}>
      <Lift>
        <Years
          from={1670}
          to={2025}
          start={6}
          len={at('p31', 'ans') - years2In}
          sub={tx("plus de 350 ans")}
          subAt={at('p31', 'ans') - years2In}
          out={pocketIn - years2In - 4}
        />
      </Lift>
    </Sequence>

    <Sequence from={pocketIn} durationInFrames={nightIn + 8 - pocketIn}>
      <Fade from={nightIn - pocketIn} len={8} out>
        <Lift>
          <PocketDoor
            phone={6}
            door={at('p31', 'fuite') - pocketIn}
            pocket={at('p31', 'poche') - 10 - pocketIn}
            open={at('p31', 'ouverte') - pocketIn}
          />
        </Lift>
      </Fade>
    </Sequence>
  </>
);

/** Au premier plan (au-dessus de la lumière de la fenêtre) : la nuit, le face caméra. */
const P3Front: React.FC = () => (
  <>
    <Sequence from={nightIn} durationInFrames={aroll5 - nightIn}>
      <Night
        wake={at('p32', 'réveilles') - nightIn}
        spin={at('p32', 'tourne') - nightIn}
        reflex={at('p32', 'Premier') - nightIn}
        screen={at('p32', "l'écran") - nightIn}
      />
    </Sequence>
    {!FACELESS && (
      <Sequence from={aroll4} durationInFrames={kgIn - aroll4}>
        <ARoll shot={tx("GROS PLAN · regard caméra, 2 s de silence")} line={tx("« Question. La dernière fois que t'es resté cinq minutes sans rien faire… c'était quand ? »")} />
      </Sequence>
    )}
    {!FACELESS && (
      <Sequence from={aroll5} durationInFrames={P3_END - aroll5}>
        <ARoll shot={tx("3/4 PUIS FACE · la bascule")} line={tx("« Je crois qu'on se trompe de problème. »")} />
      </Sequence>
    )}
  </>
);

return {P3, P3Back, P3Front, P3_SFX, P3_END};
};
const versions = {fr: makeP3('fr'), en: makeP3('en'), ur: makeP3('ur')};
export const getP3 = (lang: Lang) => versions[lang];
export const {P3, P3Back, P3Front, P3_SFX, P3_END} = versions.fr;
