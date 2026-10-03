import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {hl} from './captures';
import {ARoll} from './components/ARoll';
import {Citation, CitationProps} from './components/Citation';
import {Lift, Shot3D, WindowLight} from './components/Light';
import {Grain, Paper} from './components/Paper';
import {at, DURATION, LEAD, VO_SRC} from './cues';
import {Dots} from './scenes/Dots';
import {Maquette} from './scenes/Maquette';
import {Countdown, Groups, Lab, Static} from './scenes/Part2';
import {Plan} from './scenes/Plan';
import {Study} from './scenes/Study';
import {C, F} from './theme';

// ── Vidéo 1, POC 0:00 → 2:27 : hook + « 01 · L'expérience », accroché aux mots de la voix ──────

// hook
const cut1 = at('p1', 'Seul') - 3; // A-roll -> maquette
const planIn = at('p2') - 10; // la maquette, vue de dessus, devient le plan
const xfade = 14;
const dotsIn = at('p3') - 5; // « Deux hommes sur trois »
const aroll2 = at('p5') - 3; // « Et je suis presque sûr… » : face caméra
const docIn = at('p6') - 3; // « C'est une étude publiée dans Science »
const finIn = at('p6', 'Sa') - 4; // « Sa dernière phrase »
const studyIn = at('p7') - 8; // « Université de Virginie »
// partie 2
const staticIn = at('p9') - 4; // « Avant de laisser les gens seuls »
const methIn = at('p9', 'demande') - 8; // « On leur demande : combien tu paierais »
const aloneIn = at('p10') - 4; // « Puis on les laisse seuls »
const groupsIn = at('p11') - 4; // « Chez les hommes, douze sur dix-huit »
const resIn = at('p12') - 4; // « Un homme a appuyé cent quatre-vingt-dix fois »
const aroll3 = at('p14') - 10; // « Tu te dis peut-être » : face caméra
const vagIn = at('p15') - 6; // « Dans les versions sans bouton »
const homeIn = at('p16') - 6; // « c'est le labo, c'est intimidant »
const salonIn = at('p16', 'chez') - 3; // « chez les gens. Sur leur canapé » : la maquette du salon (3D)
const domIn = at('p16', 'Un') - 4; // « Un sur trois triche »
const e9In = at('p17') - 6; // « Et ce n'est pas qu'une affaire d'étudiants »
const lastIn = at('p18') - 4; // « Et le plus étrange, ce n'est pas ce bouton »
const prepIn = at('p19') - 1; // coupe franche sur « Le plus étrange, c'est ça »
const endF = at('p19', undefined, 'end') + 40;

const plan = {
  dot: at('p2', 'toi') - planIn,
  wander: at('p2', 'pensées') - planIn,
  button: at('p2', 'bouton') - planIn,
  zaps: [at('p2', 'décharge') - planIn, at('p2', 'électrique') - planIn],
  push: at('p2', undefined, 'end') + 4 - planIn,
  pushLen: 40,
};
const dots = {
  presses: [at('p3', 'appuyé') - dotsIn, at('p3', 'appuyé') + 8 - dotsIn],
  pct: at('p3', undefined, 'end') + 4 - dotsIn,
  before: at('p4', 'juste') - dotsIn,
  pay: at('p4', 'paieraient') - dotsIn,
};
const study = {
  place: at('p7', 'Université') - studyIn,
  students: at('p7', 'étudiants') - studyIn,
  walk1: [at('p7', 'entrent') - studyIn, at('p7', 'déposer') - studyIn] as [number, number],
  phone: at('p7', 'téléphone') - studyIn,
  pen: at('p7', 'stylos') - studyIn,
  walk2: [at('p7', 'Rien') - studyIn, at('p7', 'écrire', 'end') + 20 - studyIn] as [number, number],
  door: at('p7', 'écrire', 'end') + 24 - studyIn,
  slip: at('p8', 'consigne') - studyIn,
  words: ['reste', 'assis', 'ne', "t'endors", 'pas', 'occupe-toi', 'avec', 'tes', 'pensées'].map((w) => at('p8', w) - studyIn),
  timer: at('p8', 'Quinze') - studyIn,
  count: at('p8', undefined, 'end') + 6 - studyIn,
};

// ── les vraies pages : chaque passage anglais se surligne, sa traduction sort dans la marge ──────
type Cit = {from: number; to: number} & CitationProps;
const SHEET = {x: 110, width: 1100};
const TAG = 'SCIENCE · 2014 · WILSON ET AL.';

const cits: Cit[] = [
  // hook : la revue et le titre, puis la dernière phrase (caviardée : promesse de fin)
  {
    from: docIn,
    to: finIn + 14,
    cap: 'pmc_titre',
    ...SHEET,
    y: 440,
    tilt: -0.5,
    sub: {text: "« Juste penser : le défi de l'esprit livré à lui-même »", at: at('p6', 'étude') - docIn},
    out: finIn - docIn,
  },
  {
    from: docIn + 5,
    to: finIn + 14,
    cap: 'pmc_revue',
    x: SHEET.x + 20,
    width: 1060,
    y: 330,
    tilt: 0.4,
    tag: 'ARCHIVE PUBMED CENTRAL · PMC4330241',
    dim: 0.35,
    marks: [
      {
        i: 0,
        at: at('p6', 'Science') - docIn - 5,
        tone: 'ink',
        note: {at: at('p6', 'Science') - docIn - 1, kicker: 'PUBLIÉE DANS', big: 'Science', text: 'le 4 juillet 2014', y: -40},
      },
    ],
    notesX: 1150,
    out: finIn - docIn - 5,
  },
  {
    from: finIn,
    to: studyIn,
    cap: 'pmc_fin',
    ...SHEET,
    y: 360,
    tilt: 0.5,
    tag: TAG + ' · DERNIER PARAGRAPHE',
    marks: [
      {
        i: 0,
        at: at('p6', 'dernière') - finIn,
        tone: 'ink',
        redact: at('p6', 'Tu') - finIn,
        note: {
          at: at('p6', 'phrase') - finIn,
          kicker: 'LA DERNIÈRE PHRASE',
          text: 'presque personne ne la cite',
          chips: [{t: 'CHANGE LE SENS DU BOUTON', at: at('p6', 'bouton') - finIn, dot: true}],
          until: at('p6', 'Tu') - finIn - 2,
          y: -10,
        },
      },
    ],
    notes: [
      {
        at: at('p6', 'fin') - finIn,
        kicker: "TU L'AURAS",
        big: 'À la fin',
        chips: [{t: "+ 2 MIN D'EXERCICE", at: at('p6', "d'exercice") - finIn}],
        tone: 'red',
        y: 20,
      },
    ],
  },
  // p9 : la question posée avant
  {
    from: methIn,
    to: aloneIn,
    cap: 'pmc_methode',
    ...SHEET,
    y: 290,
    out: aloneIn - methIn - 12,
    tag: TAG + ' · ÉTUDE 10 · AVANT DE LES LAISSER SEULS',
    marks: [
      {
        i: hl('pmc_methode', 'how much'),
        at: at('p9', 'combien') - methIn,
        note: {at: at('p9', 'paierais') - methIn, kicker: 'LA QUESTION', text: 'Combien paierais-tu pour ne plus jamais la sentir ?'},
      },
    ],
    notes: [{at: at('p9', 'garde') - methIn, kicker: 'ON NE GARDE QUE CEUX QUI DISENT', big: '« Je paierais »', tone: 'red'}],
  },
  // p12-p13 : les résultats
  {
    from: resIn,
    to: aroll3,
    cap: 'pmc_resultats',
    ...SHEET,
    y: 330,
    crop: 214,
    tag: TAG + ' · ÉTUDE 10 · RÉSULTATS',
    marks: [
      {
        i: hl('pmc_resultats', 'one outlier'),
        at: at('p12', 'appuyé') - resIn,
        note: {
          at: at('p12', 'cent') - resIn,
          kicker: 'UN SEUL HOMME',
          count: {to: 190, dur: 24},
          text: 'décharges en quinze minutes',
          until: at('p13', 'quarante-deux') - resIn - 2,
        },
      },
      {i: hl('pmc_resultats', '67% of men'), at: at('p13', 'petits') - resIn},
      {
        i: hl('pmc_resultats', '25% of women'),
        at: at('p13', 'groupes') - resIn,
        note: {
          at: at('p13', 'quarante-deux') - resIn,
          kicker: '18 HOMMES + 24 FEMMES',
          big: '42',
          text: 'personnes en tout',
          until: at('p13', 'tous') - resIn - 4,
        },
      },
      {
        i: hl('pmc_resultats', 'only include'),
        at: at('p13', 'tous') - resIn,
        note: {at: at('p13', 'dire') - resIn, kicker: 'JUSTE AVANT', text: 'Tous avaient dit : je paierais pour ne plus la sentir.'},
      },
    ],
  },
  // p15 : sans bouton
  {
    from: vagIn,
    to: homeIn,
    cap: 'pmc_vagabondage',
    ...SHEET,
    y: 380,
    out: homeIn - vagIn - 12,
    tag: TAG + ' · ÉTUDES 1 À 6 · SANS BOUTON',
    marks: [
      {
        i: hl('pmc_vagabondage', 'their mind wandered'),
        at: at('p15', 'neuf') - vagIn,
        note: {at: at('p15', 'dix') - vagIn, kicker: 'NEUF SUR DIX', count: {to: 89, fmt: (n) => `${n} %`}, text: "ont l'esprit qui part ailleurs"},
      },
      {
        i: hl('pmc_vagabondage', 'difficult to concentrate'),
        at: at('p15', 'moitié') - vagIn,
        note: {at: at('p15', 'trouvent') - vagIn, kicker: 'PLUS DE LA MOITIÉ', big: '57,5 %', text: 'trouvent dur de se concentrer'},
      },
    ],
  },
  // p16 : à la maison
  {
    from: domIn,
    to: e9In,
    cap: 'pmc_domicile',
    ...SHEET,
    y: 300,
    out: e9In - domIn - 12,
    tag: TAG + ' · ÉTUDE 7 · À LA MAISON',
    marks: [
      {
        i: hl('pmc_domicile', '32%'),
        at: at('p16', 'trois') - domIn,
        note: {
          at: at('p16', 'triche') - domIn,
          kicker: '32 %',
          big: '1 sur 3',
          text: 'a triché',
          chips: [
            {t: 'MUSIQUE', at: at('p16', 'musique') - domIn},
            {t: 'TÉLÉPHONE', at: at('p16', 'téléphone') - domIn},
            {t: 'SE LEVER', at: at('p16', 'lève') - domIn},
          ],
        },
      },
      {i: hl('pmc_domicile', 'listening'), at: at('p16', 'musique') - domIn},
      {i: hl('pmc_domicile', 'getting up'), at: at('p16', 'lève') - domIn - 6},
    ],
  },
  // p17 : pas que des étudiants
  {
    from: e9In,
    to: lastIn,
    cap: 'pmc_etude9',
    ...SHEET,
    y: 360,
    out: lastIn - e9In - 12,
    tag: TAG + ' · ÉTUDE 9 · MARCHÉ, ÉGLISE, CHEZ EUX',
    marks: [
      {
        i: hl('pmc_etude9', 'ranged in age'),
        at: at('p17', 'dix-huit') - e9In,
        note: {at: at('p17', 'soixante-dix-sept') - e9In, kicker: 'PAS QUE DES ÉTUDIANTS', big: '18 → 77 ans', until: at('p17', 'même') - e9In - 4},
      },
      {
        i: hl('pmc_etude9', 'The results were similar'),
        at: at('p17', 'même') - e9In,
        note: {at: at('p17', 'résultat') - e9In, big: 'Même résultat', text: "qu'avec les étudiants", until: at('p17', 'Aucun') - e9In - 4},
      },
      {
        i: hl('pmc_etude9', "participants' age"),
        at: at('p17', 'Aucun') - e9In,
        note: {at: at('p17', "l'âge") - e9In, big: 'Aucun lien', text: "avec l'âge"},
      },
      {
        i: hl('pmc_etude9', 'smart phones'),
        at: at('p17', 'fréquence') - e9In,
        note: {at: at('p17', 'fréquence') - e9In + 4, text: '… ni avec le temps passé sur le smartphone'},
      },
    ],
  },
  // p19 : « Le plus étrange, c'est ça. »
  {
    from: prepIn,
    to: endF + 20,
    cap: 'pmc_preparation',
    ...SHEET,
    y: 250,
    tag: TAG + ' · ÉTUDES 1 À 7',
    marks: [
      {
        i: hl('pmc_preparation', 'first spent'),
        at: at('p19', 'quelques') - prepIn,
        note: {
          at: at('p19', 'préparer') - prepIn,
          kicker: 'AVANT DE COMMENCER',
          text: 'quelques minutes pour préparer à quoi penser',
          chips: [
            {t: 'UN VOYAGE', at: at('p19', 'voyage') - prepIn},
            {t: 'UN SOUVENIR', at: at('p19', 'souvenir') - prepIn},
            {t: 'UN PROJET', at: at('p19', 'projet') - prepIn},
          ],
          until: at('p19', 'Ça', 'start', 1) - prepIn - 2, // le 2e « ça » : « Ça n'a rien changé »
        },
      },
      {
        i: hl('pmc_preparation', 'none reliably'),
        at: at('p19', 'Ça', 'start', 1) - prepIn,
        note: {at: at('p19', 'rien') - prepIn, big: 'Rien changé.', text: "Aucune version n'a rendu le moment plus agréable."},
      },
    ],
  },
];

// le son des pages : feuille qui se pose, feutre, petit clic quand une fiche sort
const citSfx: [string, number, number][] = cits.flatMap((c) => [
  ['paper', c.from, 0.55] as [string, number, number],
  ...(c.marks ?? []).map((m) => ['marker', c.from + m.at, 0.3] as [string, number, number]),
  ...(c.marks ?? []).filter((m) => m.redact !== undefined).map((m) => ['marker', c.from + (m.redact as number), 0.45] as [string, number, number]),
  ...[...(c.marks ?? []).flatMap((m) => (m.note ? [m.note] : [])), ...(c.notes ?? [])].map((n) => ['tick', c.from + n.at, 0.4] as [string, number, number]),
]);

const sfx: [string, number, number][] = [
  // hook
  ['phone_down', 14, 0.9],
  ['pencil', planIn + 2, 0.55],
  ['tick', at('p2', 'toi'), 0.7],
  ['pencil', at('p2', 'pensées'), 0.4],
  ['tick', at('p2', 'bouton'), 0.9],
  ['zap', at('p2', 'décharge'), 0.6],
  ['zap', at('p2', 'électrique'), 0.35],
  ['tick', dotsIn + 1, 0.5],
  ['tick', dotsIn + 5, 0.5],
  ['tick', dotsIn + 9, 0.5],
  ['button_click', dotsIn + dots.presses[0], 0.95],
  ['button_click', dotsIn + dots.presses[1], 0.85],
  ['sub', dotsIn + dots.pct, 0.38],
  ['pencil', studyIn + 2, 0.45],
  ['tick', studyIn + study.students + 3, 0.4],
  ['tick', studyIn + study.students + 6, 0.4],
  ['tick', studyIn + study.students + 9, 0.4],
  ['tick', studyIn + study.phone + 12, 0.7],
  ['tick', studyIn + study.pen + 12, 0.7],
  ['door', studyIn + study.door, 0.8],
  ['paper', studyIn + study.slip, 0.7],
  ['clock', studyIn + study.count + 30, 0.6],
  // partie 2
  ['zap', at('p9', 'décharge'), 0.55],
  ['zap', at('p9', 'statique'), 0.3],
  ['door', at('p10', 'seuls'), 0.8],
  ['tick', at('p10', 'bouton'), 0.9],
  ['clock', at('p10', 'seuls') + 30, 0.45],
  ['clock', at('p10', 'seuls') + 60, 0.45],
  ['clock', at('p10', 'seuls') + 90, 0.45],
  ...[0, 5, 10, 15].map((d) => ['button_click', at('p11', 'douze') + d, 0.6] as [string, number, number]),
  ...[0, 5].map((d) => ['button_click', at('p11', 'six') + d, 0.6] as [string, number, number]),
  ['sub', at('p11', 'dix-huit'), 0.3],
  ['pencil', at('p16', 'chez'), 0.45],
  ['tick', at('p16', 'canapé'), 0.6],
  ['tick', lastIn + 2, 0.8],
  ...citSfx,
];

const Fade: React.FC<{from: number; len: number; out?: boolean; children: React.ReactNode}> = ({from, len, out, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [from, from + len], out ? [1, 0] : [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

export const V01_DURATION = Math.min(DURATION, endF + 20);

export const V01: React.FC = () => (
  <AbsoluteFill style={{background: C.paper}}>
    <Paper grid={0.8} />

    <Sequence from={cut1} durationInFrames={planIn + xfade - cut1}>
      <Fade from={planIn - cut1} len={xfade} out>
        <Maquette reachTop={planIn - cut1} phone={at('p1', 'téléphone') - cut1} read={at('p1', 'lire') - cut1} />
      </Fade>
    </Sequence>

    <Sequence from={planIn} durationInFrames={dotsIn + 6 - planIn}>
      <Fade from={dotsIn - planIn} len={6} out>
        <Lift><Plan {...plan} /></Lift>
      </Fade>
    </Sequence>

    <Sequence from={dotsIn} durationInFrames={aroll2 - dotsIn}>
      <Lift><Dots {...dots} /></Lift>
    </Sequence>

    <Sequence from={studyIn} durationInFrames={staticIn - studyIn}>
      <Lift><Study {...study} /></Lift>
    </Sequence>

    <Sequence from={staticIn} durationInFrames={methIn - staticIn + 8}>
      <Fade from={methIn - staticIn} len={8} out>
        <Lift>
          <Static
            shock={at('p9', 'décharge') - staticIn}
            handle={at('p9', 'Comme') - staticIn}
            label={at('p9', "d'électricité") - staticIn}
            spark={at('p9', 'statique') - staticIn}
          />
        </Lift>
      </Fade>
    </Sequence>

    <Sequence from={aloneIn} durationInFrames={groupsIn - aloneIn + 8}>
      <Fade from={groupsIn - aloneIn} len={8} out>
        {/* 3D : soleil rasant par la porte, la porte se ferme, il ne reste que le bouton */}
        <Shot3D dir="seuls" frames={groupsIn - aloneIn + 2}>
          <Countdown left={15 * 60 - 13} />
        </Shot3D>
      </Fade>
    </Sequence>

    <Sequence from={groupsIn} durationInFrames={resIn - groupsIn + 8}>
      <Fade from={resIn - groupsIn} len={8} out>
        <Lift>
          <Groups
            men={at('p11', 'douze') - groupsIn}
            menN={at('p11', 'dix-huit') - groupsIn}
            women={at('p11', 'six') - groupsIn}
            womenN={at('p11', 'vingt-quatre') - groupsIn}
          />
        </Lift>
      </Fade>
    </Sequence>

    <Sequence from={homeIn} durationInFrames={salonIn - homeIn + 8}>
      <Fade from={salonIn - homeIn} len={8} out>
        <Lift>
          <Lab intimidating={at('p16', 'intimidant') - homeIn} />
        </Lift>
      </Fade>
    </Sequence>

    <Sequence from={salonIn} durationInFrames={domIn - salonIn + 8}>
      <Fade from={domIn - salonIn} len={8} out>
        <Shot3D dir="salon" frames={domIn - salonIn + 2}>
          <div style={{position: 'absolute', left: 64, top: 52, fontFamily: F.mono, fontSize: 20, letterSpacing: '0.16em', color: C.ink}}>
            CHEZ EUX · EN LIGNE, SEULS
          </div>
        </Shot3D>
      </Fade>
    </Sequence>

    <Sequence from={lastIn} durationInFrames={prepIn - lastIn}>
      <Shot3D dir="bouton" frames={prepIn - lastIn + 2} />
    </Sequence>

    {cits.map(({from, to, ...p}, i) => (
      <Sequence key={i} from={from} durationInFrames={to - from}>
        <Citation {...p} />
      </Sequence>
    ))}

    {/* la lumière de la fenêtre, sur tout ce qui est posé sur le bureau */}
    <WindowLight />

    {/* face caméra : emplacements à remplacer par les rushes */}
    <Sequence from={0} durationInFrames={cut1}>
      <ARoll shot="PLAN SERRÉ · il retourne son téléphone sur le bureau" line="« Quinze minutes. »" />
    </Sequence>
    <Sequence from={aroll2} durationInFrames={docIn - aroll2}>
      <ARoll shot="REGARD CAMÉRA" line="« Et je suis presque sûr que toi aussi, tu aurais appuyé. »" />
    </Sequence>
    <Sequence from={aroll3} durationInFrames={vagIn - aroll3}>
      <ARoll shot="REGARD CAMÉRA · la relance" line="« Tu te dis peut-être : des étudiants, dans un labo, ça ne prouve pas grand-chose. »" />
    </Sequence>

    <Sequence from={endF}>
      <Fade from={0} len={15}>
        <AbsoluteFill style={{background: C.night}} />
      </Fade>
    </Sequence>

    <Grain />

    {/* son */}
    <Sequence from={LEAD}>
      <Audio src={staticFile(VO_SRC)} />
    </Sequence>
    {sfx.map(([name, f, v], i) => (
      <Sequence key={i} from={f} durationInFrames={60}>
        <Audio src={staticFile(`sfx/${name}.wav`)} volume={v} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
