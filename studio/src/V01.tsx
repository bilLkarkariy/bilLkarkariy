import React from 'react';
import {AbsoluteFill, Audio, getInputProps, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {hl} from './captures';
import {ARoll, FACELESS} from './components/ARoll';
import {Citation} from './components/Citation';
import {Lift, Shot3D, WindowLight} from './components/Light';
import {Music} from './components/Music';
import {Grain, Paper} from './components/Paper';
import {createCues, LEAD} from './cues';
import {isRTL, Lang, LanguageProvider, RtlType, translator} from './i18n';
import {Dots} from './scenes/Dots';
import {Maquette} from './scenes/Maquette';
import {Cit, citSfx, Fade, Sfx} from './montage/kit';
import {getP3} from './montage/p3';
import {getP4} from './montage/p4';
import {getP5} from './montage/p5';
import {getFaceless} from './montage/faceless';
import {Countdown, Groups, Lab, Static} from './scenes/Part2';
import {Plan} from './scenes/Plan';
import {Study} from './scenes/Study';
import {C, F} from './theme';

const makeV01 = (lang: Lang) => {
const {at, vo} = createCues(lang);
const tx = translator(lang);
const {P3, P3Back, P3Front, P3_SFX} = getP3(lang);
const {P4, P4Front, P4_SFX, VERSE_SILENCE} = getP4(lang);
const {P5, P5Front, P5_END, P5_SFX} = getP5(lang);
const Faceless = getFaceless(lang);

// ── Vidéo 1 : hook + « 01 · L'expérience » (ici), puis les parties suivantes (src/montage/p*.tsx).
//    Tout est accroché aux mots de la voix.

// hook
const cut1 = at('p1', 'Seul') - 3; // A-roll -> maquette
// (en anglais et en arabe sans face caméra, aucun visage : la maquette ouvre la vidéo dès la première image)
const mIn = FACELESS && lang !== 'fr' ? 0 : cut1;
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
const p3In = at('p20') - 4; // la partie 3 prend le relais

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
    sub: {text: tx("« Juste penser : le défi de l'esprit livré à lui-même »"), at: at('p6', 'étude') - docIn},
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
        note: {at: at('p6', 'Science') - docIn - 1, kicker: tx("PUBLIÉE DANS"), big: 'Science', text: tx("le 4 juillet 2014"), y: -40},
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
    // la promesse : on ne doit pas pouvoir lire la phrase (ni « Without such training » juste avant,
    // qui vendrait la chute) : page floutée, dernière phrase caviardée avant même que la feuille se pose
    veil: 7,
    marks: [
      {
        i: 0,
        at: at('p6', 'dernière') - finIn,
        tone: 'ink',
        redact: -40,
        note: {
          at: at('p6', 'phrase') - finIn,
          kicker: tx("LA DERNIÈRE PHRASE"),
          text: tx("presque personne ne la cite"),
          chips: [{t: tx("CHANGE LE SENS DU BOUTON"), at: at('p6', 'bouton') - finIn, dot: true}],
          until: at('p6', 'Tu') - finIn - 2,
          y: -10,
        },
      },
    ],
    notes: [
      {
        at: at('p6', 'fin') - finIn,
        kicker: tx("TU L'AURAS"),
        big: tx("À la fin"),
        chips: [{t: tx("+ 2 MIN D'EXERCICE"), at: at('p6', "d'exercice") - finIn}],
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
        note: {at: at('p9', 'paierais') - methIn, kicker: tx("LA QUESTION"), text: tx("Combien paierais-tu pour ne plus jamais la sentir ?")},
      },
    ],
    notes: [{at: at('p9', 'garde') - methIn, kicker: tx("ON NE GARDE QUE CEUX QUI DISENT"), big: tx("« Je paierais »"), tone: 'red'}],
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
          kicker: tx("UN SEUL HOMME"),
          count: {to: 190, dur: 24},
          text: tx("décharges en quinze minutes"),
          until: at('p13', 'quarante-deux') - resIn - 2,
        },
      },
      {i: hl('pmc_resultats', '67% of men'), at: at('p13', 'petits') - resIn},
      {
        i: hl('pmc_resultats', '25% of women'),
        at: at('p13', 'groupes') - resIn,
        note: {
          at: at('p13', 'quarante-deux') - resIn,
          kicker: tx("18 HOMMES + 24 FEMMES"),
          big: '42',
          text: tx("personnes en tout"),
          until: at('p13', 'tous') - resIn - 4,
        },
      },
      {
        i: hl('pmc_resultats', 'only include'),
        at: at('p13', 'tous') - resIn,
        note: {at: at('p13', 'dire') - resIn, kicker: tx("JUSTE AVANT"), text: tx("Tous avaient dit : je paierais pour ne plus la sentir.")},
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
        note: {at: at('p15', 'dix') - vagIn, kicker: tx("NEUF SUR DIX"), count: {to: 89, fmt: (n) => `${n} %`}, text: tx("ont l'esprit qui part ailleurs")},
      },
      {
        i: hl('pmc_vagabondage', 'difficult to concentrate'),
        at: at('p15', 'moitié') - vagIn,
        note: {at: at('p15', 'trouvent') - vagIn, kicker: tx("PLUS DE LA MOITIÉ"), big: tx("57,5 %"), text: tx("trouvent dur de se concentrer")},
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
          kicker: tx("32 %"),
          big: tx("1 sur 3"),
          text: tx("a triché"),
          chips: [
            {t: tx("MUSIQUE"), at: at('p16', 'musique') - domIn},
            {t: tx("TÉLÉPHONE"), at: at('p16', 'téléphone') - domIn},
            {t: tx("SE LEVER"), at: at('p16', 'lève') - domIn},
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
        note: {at: at('p17', 'soixante-dix-sept') - e9In, kicker: tx("PAS QUE DES ÉTUDIANTS"), big: tx("18 → 77 ans"), until: at('p17', 'même') - e9In - 4},
      },
      {
        i: hl('pmc_etude9', 'The results were similar'),
        at: at('p17', 'même') - e9In,
        note: {at: at('p17', 'résultat') - e9In, big: tx("Même résultat"), text: tx("qu'avec les étudiants"), until: at('p17', 'Aucun') - e9In - 4},
      },
      {
        i: hl('pmc_etude9', "participants' age"),
        at: at('p17', 'Aucun') - e9In,
        note: {at: at('p17', "l'âge") - e9In, big: tx("Aucun lien"), text: tx("avec l'âge")},
      },
      {
        i: hl('pmc_etude9', 'smart phones'),
        at: at('p17', 'fréquence') - e9In,
        note: {at: at('p17', 'fréquence') - e9In + 4, text: tx("… ni avec le temps passé sur le smartphone")},
      },
    ],
  },
  // p19 : « Le plus étrange, c'est ça. »
  {
    from: prepIn,
    to: p3In + 8,
    cap: 'pmc_preparation',
    ...SHEET,
    y: 250,
    out: p3In - 10 - prepIn,
    tag: TAG + ' · ÉTUDES 1 À 7',
    marks: [
      {
        i: hl('pmc_preparation', 'first spent'),
        at: at('p19', 'quelques') - prepIn,
        note: {
          at: at('p19', 'préparer') - prepIn,
          kicker: tx("AVANT DE COMMENCER"),
          text: tx("quelques minutes pour préparer à quoi penser"),
          chips: [
            {t: tx("UN VOYAGE"), at: at('p19', 'voyage') - prepIn},
            {t: tx("UN SOUVENIR"), at: at('p19', 'souvenir') - prepIn},
            {t: tx("UN PROJET"), at: at('p19', 'projet') - prepIn},
          ],
          until: at('p19', 'Ça', 'start', 1) - prepIn - 2, // le 2e « ça » : « Ça n'a rien changé »
        },
      },
      {
        i: hl('pmc_preparation', 'none reliably'),
        at: at('p19', 'Ça', 'start', 1) - prepIn,
        note: {at: at('p19', 'rien') - prepIn, big: tx("Rien changé."), text: tx("Aucune version n'a rendu le moment plus agréable.")},
      },
    ],
  },
];

const sfx: Sfx[] = [
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
  ['etincelle', at('p9', 'statique'), 0.5],
  ['door', at('p10', 'seuls'), 0.8],
  ['tick', at('p10', 'bouton'), 0.9],
  ['clock', at('p10', 'seuls') + 30, 0.45],
  ['clock', at('p10', 'seuls') + 60, 0.45],
  ['clock', at('p10', 'seuls') + 90, 0.45],
  ...[0, 5, 10, 15].map((d) => ['button_click', at('p11', 'douze') + d, 0.6] as [string, number, number]),
  ...[0, 5].map((d) => ['button_click', at('p11', 'six') + d, 0.6] as [string, number, number]),
  ['sub', at('p11', 'dix-huit'), 0.3],
  ['pencil', at('p16', 'chez'), 0.45],
  ['canape', at('p16', 'canapé') + 4, 0.7], // le pion touche le canapé ~4 images après le mot
  ['tick', lastIn + 2, 0.8],
  ...citSfx(cits),
  ...P3_SFX,
  ...P4_SFX,
  ...P5_SFX,
];

// bruitages ElevenLabs (tools/sfx_el.py, script/sfx_v01.json) ; les autres restent synthétisés (tools/sfx.py).
// Pour revenir au son synthétisé, retirer sa ligne.
const SON: Record<string, string> = {
  paper: 'el/papier_pose',
  fiche: 'el/fiche',
  button_click: 'el/bouton',
  zap: 'el/decharge',
  etincelle: 'el/etincelle',
  door: 'el/porte',
  clock: 'el/horloge',
  canape: 'el/canape',
  phone_down: 'el/telephone',
  // noms français des mêmes sons (parties 3 à 5)
  porte: 'el/porte',
  horloge: 'el/horloge',
  bouton: 'el/bouton',
  // (les noms ci-dessous n'existent qu'en version ElevenLabs)
  projecteur: 'el/projecteur',
  pellicule_vrille: 'el/pellicule_vrille',
  ciseaux: 'el/ciseaux',
  poche: 'el/poche',
  notification: 'el/notification',
  ascenseur: 'el/ascenseur',
  compteur: 'el/compteur',
  nuit: 'el/nuit',
  souffle_ecran: 'el/souffle_ecran',
  manuscrit: 'el/manuscrit',
  toc_mur: 'el/toc_mur',
  timelapse: 'el/timelapse',
  bille: 'el/bille',
  chapelet: 'el/chapelet',
  carillon: 'el/carillon',
  calame: 'el/calame',
  crayon_carte: 'el/crayon_carte',
  voiture: 'el/voiture',
  respiration: 'el/respiration',
  craie: 'el/craie',
  arrachage: 'el/arrachage',
};

// Prises multiples (tools/sfx_el.py, "variants") : chaque occurrence prend la prise suivante, dans l'ordre du
// temps, avec un léger écart de hauteur et de volume. Jamais deux fois exactement le même son : rien de mécanique.
// Prises choisies sans raie étroite (pas de couinement) et sans double coup.
const POOL: Record<string, {takes: string[]; gain: number; max?: number; fadeIn?: number}> = {
  marker: {takes: ['frotte_1', 'glisse_2', 'frotte_4', 'glisse_6', 'frotte_2', 'frotte_6'], gain: 1, fadeIn: 2},
  fiche: {takes: ['carte_1', 'carte_4', 'carte_2', 'carte_6', 'carte_3', 'carte_5'], gain: 0.8},
  tick: {takes: ['tape_3', 'tape_10', 'tape_4', 'tape_12', 'tape_7', 'tape_8'], gain: 0.2, max: 6},
};
const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const rnd = (n: number, k: number) => (((Math.sin(n * 12.9898 + k * 78.233) * 43758.5453) % 1) + 1) % 1;
/** --props '{"sfxOff":[[de, à], …]}' : bruitages coupés sur ces images (passages remplacés au montage, qui ont les leurs). */
const SFX_OFF = (getInputProps().sfxOff ?? []) as [number, number][];
const played = (() => {
  const seen: Record<string, number> = {};
  return [...sfx]
    .filter(([, f]) => !SFX_OFF.some(([a, b]) => f >= a && f < b))
    .sort((a, b) => a[1] - b[1])
    .map(([name, f, v, max]) => {
      const pool = POOL[name];
      if (!pool) return {src: `sfx/${SON[name] ?? name}.wav`, f, v, len: max ?? 60, tone: 1, fadeIn: 0};
      const n = (seen[name] = (seen[name] ?? -1) + 1);
      return {
        src: `sfx/el/${pool.takes[n % pool.takes.length]}.wav`,
        f,
        v: v * pool.gain * (0.85 + 0.3 * rnd(n, 1)),
        len: Math.min(max ?? 60, pool.max ?? 60),
        tone: 0.96 + 0.08 * rnd(n, 2),
        fadeIn: pool.fadeIn ?? 0,
      };
    });
})();

const V01_DURATION = P5_END; // (la voix finit à DURATION ; l'écran de fin dure 6 s de plus)

const Component: React.FC = () => {
  const frame = useCurrentFrame();
  // pendant le verset (hors français) : ni grain ni lumière qui bouge, aucun bruitage ; en arabe, la voix dit le verset
  const verse = lang !== 'fr' && frame >= VERSE_SILENCE[0] && frame < VERSE_SILENCE[1];
  return (
  <AbsoluteFill style={{background: C.paper}}>
    <Paper grid={0.8} />
    <P3Back />

    <Sequence from={mIn} durationInFrames={planIn + xfade - mIn}>
      <Fade from={planIn - mIn} len={xfade} out>
        <Maquette reachTop={planIn - mIn} phone={at('p1', 'téléphone') - mIn} read={at('p1', 'lire') - mIn} />
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
        <Shot3D dir="seuls" frames={groupsIn - aloneIn + 2} label={tx("La maquette en contre-jour : un soleil rasant entre par la porte jusqu'à la chaise. La porte se ferme, la lumière se referme, il ne reste que le bouton rouge qui s'allume.")}>
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
        <Shot3D dir="salon" frames={domIn - salonIn + 2} label={tx("Le salon en maquette, le soir, une lampe chaude. Sur « canapé », le participant tombe dans le canapé.")}>
          <div style={{position: 'absolute', left: 64, top: 52, fontFamily: F.mono, fontSize: 20, letterSpacing: '0.16em', color: C.ink, ...(isRTL(lang) ? {direction: 'rtl'} : {})}}>{tx("CHEZ EUX · EN LIGNE, SEULS")}</div>
        </Shot3D>
      </Fade>
    </Sequence>

    <Sequence from={lastIn} durationInFrames={prepIn - lastIn}>
      <Shot3D dir="bouton" frames={prepIn - lastIn + 2} label={tx("Gros plan sur le bouton rouge, le participant flou derrière. Sur « bouton », la lumière tombe.")} />
    </Sequence>

    {cits.map(({from, to, sound, ...p}, i) => (
      <Sequence key={i} from={from} durationInFrames={to - from}>
        <Citation {...p} />
      </Sequence>
    ))}

    {/* partie 3 : le scénariste fatigué, Harvard, les écrans, Pascal */}
    <P3 />
    <P4 />
    <P5 />

    {FACELESS && <Faceless />}

    {/* la lumière de la fenêtre, sur tout ce qui est posé sur le bureau */}
    {!verse && <WindowLight />}

    {/* face caméra : emplacements à remplacer par les rushes */}
    {mIn > 0 && (
      <Sequence from={0} durationInFrames={cut1}>
        <ARoll shot={tx("PLAN SERRÉ · il retourne son téléphone sur le bureau")} line={tx("« Quinze minutes. »")} />
      </Sequence>
    )}
    {!FACELESS && (
      <>
        <Sequence from={aroll2} durationInFrames={docIn - aroll2}>
          <ARoll shot={tx("REGARD CAMÉRA")} line={tx("« Et je suis presque sûr que toi aussi, tu aurais appuyé. »")} />
        </Sequence>
        <Sequence from={aroll3} durationInFrames={vagIn - aroll3}>
          <ARoll shot={tx("REGARD CAMÉRA · la relance")} line={tx("« Tu te dis peut-être : des étudiants, dans un labo, ça ne prouve pas grand-chose. »")} />
        </Sequence>
      </>
    )}
    <P3Front />
    <P4Front />
    <P5Front />

    {!verse && <Grain />}

    {/* son */}
    {vo.audio && <Sequence from={LEAD}>
      <Audio src={staticFile(vo.audio)} volume={verse && lang === 'en' ? 0 : 1} />
    </Sequence>}
    {/* musique (ElevenLabs, tools/sfx_el.py music) : la science, rien sous la pièce vide, la khalwa, la voie */}
    <Music
      silence={[VERSE_SILENCE]}
      cues={[
        {src: 'music/science_270s.mp3', from: cut1, to: Math.min(cut1 + 270 * 30, at('p35') + 30), fadeIn: 45, fadeOut: 75},
        {src: 'music/soufi_khalwa_130s.mp3', from: at('p41') - 10, to: at('p54') - 6, gain: 0.24, fadeIn: 60},
        {src: 'music/voie_165s.mp3', from: at('p54') - 30, to: V01_DURATION, gain: 0.22, fadeIn: 60, fadeOut: 90},
      ]}
    />
    {played.map((s, i) => (
      <Sequence key={i} from={s.f} durationInFrames={s.len}>
        <Audio
          src={staticFile(s.src)}
          toneFrequency={s.tone}
          volume={(lf) =>
            (lang !== 'fr' && s.f + lf >= VERSE_SILENCE[0] && s.f + lf < VERSE_SILENCE[1] ? 0 : s.v) *
            (s.fadeIn ? interpolate(lf, [0, s.fadeIn], [0.35, 1], CLAMP) : 1) *
            interpolate(lf, [s.len - 3, s.len], [1, 0], CLAMP)
          }
        />
      </Sequence>
    ))}
  </AbsoluteFill>
);

};
return {Component, duration: V01_DURATION};
};
const versions = {fr: makeV01('fr'), en: makeV01('en'), ar: makeV01('ar')};
export const durationFor = (lang: Lang) => versions[lang].duration;
export const V01_DURATION = durationFor('fr');
export const V01: React.FC<{lang?: Lang}> = ({lang = 'fr'}) => {
  const {Component} = versions[lang];
  return <LanguageProvider value={lang}><RtlType /><Component /></LanguageProvider>;
};
