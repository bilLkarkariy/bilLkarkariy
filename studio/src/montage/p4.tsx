import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {hl} from '../captures';
import {ARoll} from '../components/ARoll';
import {Citation, NoteCard} from '../components/Citation';
import {Lift, Shot3D} from '../components/Light';
import {at} from '../cues';
import {ArabicWord, GhazaliMap, Kinetic, Tasbih, Verse} from '../scenes/Part4';
import {C, F} from '../theme';
import {Cit, citSfx, Fade, Sfx} from './kit';

// ── Partie 4 (4:28 → 7:29) : la pièce sans meuble, la khalwa, al-Ghazali, le dhikr, le verset ─────
//    p35 → p53. Trois plans 3D (tools/plans3d.py : vide, khalwa, dhikr) ; les vraies pages :
//    Wilson (PMC), al-Ghazali (trad. Watt), la photo de Damas (1914), les fondements de la Karkariya.

const smooth = (u: number) => {
  const v = Math.max(0, Math.min(1, u));
  return v * v * (3 - 2 * v);
};

// plans 3D : mêmes bornes que tools/plans3d.py (t0, N)
const videIn = at('p35') - 4;
const videN = at('p36', undefined, 'end') + 24 - videIn;
const khalwaIn = at('p44') - 6;
const khalwaN = at('p44', undefined, 'end') + 24 - khalwaIn;
const dhikrIn = at('p51', "L'idée") - 6;
const dhikrN = at('p51', undefined, 'end') + 30 - dhikrIn;

const p37In = at('p37') - 8;
const techIn = at('p39') - 6;
const siecleIn = at('p40', 'Derrière') - 4;
const motIn = at('p41') - 4;
const p45In = at('p45') - 6;
const ghzIn = at('p46', 'Al-Ghazali') - 4;
const langueIn = at('p47') - 4;
const coeurIn = at('p47', 'Les') - 6;
const routeIn = at('p48') - 6;
const photoIn = at('p48', 'minaret') - 10;
const minaretIn = at('p48', 'enferme') - 8;
const p49In = at('p49') - 4;
const p50In = at('p50') - 4;
const verseIn = at('p52') - 10;
const aroll6 = at('p53') - 6;
const fondIn = at('p53', 'Et') - 4;
export const P4_END = at('p54') - 6;

const WATT = 'AL-GHAZĀLĪ · « DELIVERANCE FROM ERROR » · TRAD. W. M. WATT';

const cits: Cit[] = [
  // p39-p40 : « sans entraînement… la méditation, et d'autres techniques » (la dernière phrase reste cachée)
  {
    from: techIn,
    to: siecleIn + 8,
    cap: 'pmc_techniques',
    x: 110,
    width: 1100,
    y: 330,
    tilt: -0.4,
    tag: 'SCIENCE · 2014 · WILSON ET AL. · DERNIER PARAGRAPHE',
    out: siecleIn - 6 - techIn,
    dim: 0.6,
    marks: [
      {i: hl('pmc_techniques', 'The untutored'), at: 0, tone: 'ink', redact: -40},
      {
        i: hl('pmc_techniques', 'Without such training'),
        at: at('p39', 'sans') - techIn,
        note: {
          at: at('p39', 'entraînement') - techIn,
          kicker: 'LES AUTEURS LE DISENT',
          text: 'Sans entraînement, on préfère faire plutôt que penser',
          until: at('p39', 'citent') - 2 - techIn,
          y: -60,
        },
      },
      {
        i: hl('pmc_techniques', 'meditation'),
        at: at('p39', 'méditation') - techIn,
        note: {
          at: at('p39', 'méditation') + 2 - techIn,
          kicker: 'ILS CITENT',
          chips: [
            {t: 'LA MÉDITATION', at: at('p39', 'méditation') + 2 - techIn},
            {t: "D'AUTRES TECHNIQUES", at: at('p39', 'techniques') - techIn},
          ],
          until: at('p40', 'Deux') - 2 - techIn,
          y: -60,
        },
      },
      {
        i: hl('pmc_techniques', 'meditation'),
        at: at('p40', "D'autres") - techIn,
        tone: 'gold',
        note: {at: at('p40', 'Deux') - techIn, kicker: '« OTHER TECHNIQUES »', big: 'Deux mots', text: 'dans un article scientifique', tone: 'gold', y: -60},
      },
    ],
  },
  // p46 : Bagdad, trois cents étudiants
  {
    from: ghzIn,
    to: langueIn + 8,
    cap: 'ghazali_baghdad',
    x: 110,
    width: 1100,
    inset: 34,
    y: 420,
    tilt: -0.5,
    tag: WATT,
    out: langueIn - 6 - ghzIn,
    notes: [
      {at: 6, kicker: 'ABŪ ḤĀMID AL-GHAZĀLĪ · 1058-1111', text: 'un professeur célèbre', until: at('p46', 'Trois') - 2 - ghzIn, y: -150},
    ],
    marks: [
      {
        i: 0,
        at: at('p46', 'Trois') - ghzIn,
        note: {at: at('p46', 'cents') - ghzIn, kicker: 'À BAGDAD', count: {to: 300, dur: 18}, text: 'étudiants : une carrière au sommet', y: -150},
      },
    ],
  },
  // p47 : la langue desséchée, les médecins, le cœur
  {
    from: langueIn,
    to: coeurIn + 8,
    cap: 'ghazali_langue',
    x: 110,
    width: 1100,
    inset: 34,
    y: 400,
    tilt: 0.4,
    tag: WATT,
    out: coeurIn - 6 - langueIn,
    marks: [
      {
        i: hl('ghazali_langue', 'my tongue would not'),
        at: at('p47', 'mot') - langueIn,
        note: {at: at('p47', 'sort') - langueIn, kicker: 'IL VEUT FAIRE COURS', text: '« ma langue ne prononçait plus un seul mot »', until: at('p47', 'langue') - 2 - langueIn, y: -140},
      },
      {
        i: hl('ghazali_langue', 'God caused'),
        at: at('p47', 'langue') - langueIn,
        note: {at: at('p47', 'desséchée') - langueIn, kicker: 'IL LE RACONTE LUI-MÊME', text: '« Dieu dessécha ma langue : je ne pouvais plus enseigner »', y: -140},
      },
    ],
  },
  {
    from: coeurIn,
    to: routeIn + 8,
    cap: 'ghazali_coeur',
    x: 110,
    width: 1100,
    inset: 34,
    y: 440,
    tilt: -0.4,
    tag: WATT,
    out: routeIn - 6 - coeurIn,
    marks: [
      {
        i: hl('ghazali_coeur', 'the doctors'),
        at: at('p47', 'médecins') - coeurIn,
        note: {at: at('p47', 'renoncent') - coeurIn, kicker: 'LES MÉDECINS', text: 'renoncent à le soigner', until: at('p47', 'Ça') - 2 - coeurIn, y: -160},
      },
      {
        i: hl('ghazali_coeur', 'This trouble'),
        at: at('p47', 'Ça') - coeurIn,
        note: {at: at('p47', 'cœur') - coeurIn, kicker: 'DISENT-ILS', big: '« Ça vient du cœur »', y: -160},
      },
    ],
  },
  // p48 : la photo de Damas (1914), puis son récit : le minaret
  {
    from: photoIn,
    to: p49In + 6,
    cap: 'photo_omeyyades',
    x: 150,
    width: 820,
    y: 70,
    tilt: -1.8,
    tag: 'DAMAS · LA MOSQUÉE DES OMEYYADES · PHOTOGRAPHIE DE 1914',
    out: p49In - 6 - photoIn,
  },
  {
    from: minaretIn,
    to: p49In + 6,
    cap: 'ghazali_minaret',
    x: 360,
    width: 1100,
    inset: 34,
    y: 760,
    tilt: 0.6,
    tag: WATT,
    out: p49In - 6 - minaretIn,
    notesX: 760,
    notesW: 560,
    marks: [
      {
        i: 0,
        at: at('p48', 'enferme') - minaretIn,
        note: {at: at('p48', 'Toute') - minaretIn, kicker: 'IL LE RACONTE', text: '« je montais au minaret de la mosquée toute la journée, et je m’y enfermais »', y: -560},
      },
    ],
  },
  // p53 : les fondements de la Karkariya : la retraite, et le Nom
  {
    from: fondIn,
    to: P4_END + 8,
    cap: 'karkariya_fondements',
    x: 220,
    width: 760,
    y: 260,
    tilt: -0.6,
    tag: 'M. F. AL-KARKARI · THE FOUNDATIONS OF THE KARKARIYA ORDER',
    out: P4_END - 6 - fondIn,
    marks: [
      {i: hl('karkariya_fondements', 'the Patched Cloak'), at: at('p53', 'fondements') - fondIn, tone: 'ink'},
      {
        i: hl('karkariya_fondements', 'the Spiritual Retreat'),
        at: at('p53', 'retraite') - fondIn,
        tone: 'gold',
        note: {at: at('p53', 'retraite') + 2 - fondIn, kicker: 'AL-KHALWA', big: 'La retraite', tone: 'gold'},
      },
      {
        i: hl('karkariya_fondements', 'the Singular Name'),
        at: at('p53', 'Nom') - fondIn,
        tone: 'gold',
        note: {at: at('p53', 'Nom') + 2 - fondIn, kicker: 'AL-ISM AL-MUFRAD', big: 'Le Nom', tone: 'gold'},
      },
    ],
    notes: [{at: at('p53', 'fondements') - fondIn, kicker: 'PARMI LES FONDEMENTS DE LA VOIE', text: 'ces deux-là', until: at('p53', 'retraite') - 2 - fondIn}],
  },
];

// la khalwa : les jours et les nuits en accéléré (mêmes valeurs que tools/plans3d.py)
const jours0 = at('p44', 'quarante') - khalwaIn + 1;
const jours1 = at('p44', 'Exactement') - khalwaIn + 1;
const sunH = (lf: number) => Math.sin(2 * Math.PI * (0.18 + 3 * smooth((lf + 1 - jours0) / (jours1 - jours0))));

/** Le bureau s'assombrit derrière la maquette (la porte-écran ; les nuits de la khalwa). */
const Dusk: React.FC<{curve: (f: number) => number}> = ({curve}) => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{background: C.night, opacity: curve(frame)}} />;
};

const KhalwaHud: React.FC = () => {
  const frame = useCurrentFrame();
  const u = smooth((frame + 1 - jours0) / (jours1 - jours0));
  const day = Math.max(1, Math.round(1 + 39 * u));
  const fuy = at('p44', 'Virginie') - khalwaIn;
  const night = 1 - Math.max(0, sunH(frame));
  const ink = `rgba(${Math.round(34 + 200 * night)},${Math.round(33 + 197 * night)},${Math.round(30 + 194 * night)},1)`;
  return (
    <>
      <div style={{position: 'absolute', left: 64, top: 52, fontFamily: F.mono, fontSize: 20, letterSpacing: '0.16em', color: ink, opacity: interpolate(frame, [jours0 - 10, jours0], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        KHALWA · JOUR {String(day).padStart(2, '0')} / 40
      </div>
      <div style={{position: 'absolute', left: 64, top: 86, fontFamily: F.mono, fontSize: 20, letterSpacing: '0.16em', color: C.red, opacity: interpolate(frame, [fuy, fuy + 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        VIRGINIE · 15 MINUTES
      </div>
    </>
  );
};

/** Poussée lente sur un tirage photo (le minaret). */
const Push: React.FC<{len: number; to: number; ox: number; oy: number; children: React.ReactNode}> = ({len, to, ox, oy, children}) => {
  const frame = useCurrentFrame();
  const k = interpolate(frame, [0, len], [1, to], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{transform: `scale(${k})`, transformOrigin: `${ox}px ${oy}px`}}>{children}</AbsoluteFill>;
};

export const P4_SFX: Sfx[] = [
  ['paper', at('p35', 'chaise') + 2, 0.5],
  ['paper', at('p35', 'table') + 2, 0.5],
  ['toc_mur', at('p35', 'touches') + 10, 0.6],
  ['toc_mur', at('p35', 'murs') + 18, 0.6],
  ['souffle_ecran', at('p36', 'téléphone') - 4, 0.6],
  ['marker', at('p37', 'caractère') + 4, 0.5],
  ['calame', at('p42', 'khalwa') - 4, 0.45],
  ['porte', at('p44', 'volontairement'), 0.55],
  ['timelapse', jours0 + khalwaIn, 0.55],
  ['crayon_carte', at('p45', 'Écoute'), 0.35],
  ['tick', at('p46', 'Bagdad'), 0.6],
  ['crayon_carte', at('p48', 'part'), 0.35],
  ['tick', at('p48', 'Damas'), 0.6],
  ['fiche', at('p49', 'livre'), 0.45],
  ['fiche', at('p49', 'réponse'), 0.45],
  ['fiche', at('p49', 'revenir'), 0.45],
  ['calame', at('p50', 'dhikr') - 4, 0.45],
  ['chapelet', at('p51', 'nom'), 0.5],
  ['bille', at('p51', 'meuble') + 8, 0.6],
  ['carillon', at('p51', 'fixe') + 2, 0.4],
  ['carillon', at('p51', 'ramènes') + 16, 0.35],
  ['carillon', at('p51', 'ramènes', 'start', 1) + 18, 0.35],
  ...citSfx(cits),
];

/** Ce qui est posé sur le bureau (sous la lumière de la fenêtre). */
export const P4: React.FC = () => (
  <>
    {/* p35-p36 : la pièce sans meuble ; « le téléphone, c'est la porte » : le bureau s'éteint */}
    <Sequence from={videIn} durationInFrames={videN + 10}>
      <Fade from={videN} len={10} out>
        <Dusk curve={(f) => interpolate(f, [at('p36', 'téléphone') - 6 - videIn, at('p36', 'téléphone') + 12 - videIn], [0, 0.82], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
        <Shot3D dir="vide" frames={videN} label="La maquette sans meubles : la chaise et la table disparaissent sur leurs mots, le pion entre, tourne, touche les murs, cherche la porte. Sur « téléphone », tout s'éteint et la porte s'allume comme un écran." />
      </Fade>
    </Sequence>

    {/* p37-p38 */}
    <Sequence from={p37In} durationInFrames={techIn - p37In}>
      <Kinetic
        lines={[
          {t: 'un défaut de caractère', at: at('p37', 'défaut') - 2 - p37In, y: 400, size: 76, italic: true, strike: at('p37', 'caractère') + 4 - p37In, out: at('p37', 'On') - 6 - p37In},
          {t: 'Personne ne t’a appris à habiter cette pièce.', at: at('p37', 'Personne') - p37In, y: 540, size: 60, gold: ['habiter'], out: at('p37', 'On') - 6 - p37In},
          {t: 'REMPLIR TON ATTENTION', at: at('p37', 'remplir') - p37In, y: 440, size: 40, mono: true, out: at('p38') - 6 - p37In},
          {t: 'JAMAIS Y RESTER', at: at('p37', 'Jamais') - p37In, y: 530, size: 40, mono: true, red: ['JAMAIS'], out: at('p38') - 6 - p37In},
          {t: 'Comme un muscle qu’on n’a jamais entraîné.', at: at('p38', 'muscle') - 4 - p37In, y: 490, size: 62, italic: true},
        ]}
      />
    </Sequence>

    {/* p40 : « Derrière ces deux mots, il y a des siècles… être seul sans fuir » */}
    <Sequence from={siecleIn} durationInFrames={motIn - siecleIn}>
      <Kinetic
        lines={[
          {t: 'Derrière ces deux mots,', at: at('p40', 'Derrière') - siecleIn, y: 380, size: 56, italic: true, out: at('p40', 'Des', 'start', 1) - 6 - siecleIn},
          {t: 'des siècles.', at: at('p40', 'siècles') - 4 - siecleIn, y: 470, size: 130, gold: ['siècles.'], out: at('p40', 'Des', 'start', 1) - 6 - siecleIn},
          {t: 'Des traditions entières, une seule chose :', at: at('p40', 'Des', 'start', 1) - siecleIn, y: 400, size: 52, italic: true},
          {t: 'être seul sans fuir.', at: at('p40', 'être') - 2 - siecleIn, y: 490, size: 120, gold: ['seul'], red: ['fuir.', 'fuir']},
        ]}
      />
    </Sequence>

    {/* p41-p43 : « littéralement, solitude » ; khalwa */}
    <Sequence from={motIn} durationInFrames={khalwaIn + 8 - motIn}>
      <Fade from={khalwaIn - motIn} len={8} out>
        <Kinetic
          lines={[
            {t: 'Un mot qui veut dire, littéralement :', at: at('p41', 'Un', 'start', 1) - motIn, y: 390, size: 52, italic: true, out: at('p42', 'khalwa') - 10 - motIn},
            {t: '« solitude »', at: at('p41', 'solitude') - 2 - motIn, y: 480, size: 130, italic: true, out: at('p42', 'khalwa') - 10 - motIn},
            {t: 'le soufisme, la tradition intérieure de l’islam', at: at('p43', 'soufisme') - motIn, y: 780, size: 46, italic: true},
            {t: 'LE CŒUR · L’ATTENTION', at: at('p43', 'cœur') - 2 - motIn, y: 870, size: 26, mono: true, stagger: 8},
          ]}
        />
        <ArabicWord ar="خلوة" latin="KHALWA" gloss="la retraite spirituelle" at={at('p42', 'khalwa') - 6 - motIn} glossAt={at('p42', 'retraite') - motIn} y={130} />
      </Fade>
    </Sequence>

    {/* p44 : la khalwa en 3D, les jours et les nuits */}
    <Sequence from={khalwaIn} durationInFrames={khalwaN}>
      <Dusk curve={(f) => 0.62 * Math.pow(1 - Math.max(0, sunH(f)), 1.4)} />
      <Shot3D dir="khalwa" frames={khalwaN} label="Le pion entre et ferme la porte lui-même ; une petite lumière d'or au centre. Sur « quarante jours », le soleil tourne au-dessus de la maquette : jours et nuits en accéléré.">
        <KhalwaHud />
      </Shot3D>
    </Sequence>

    {/* p45-p46 : « Écoute l'histoire… » Bagdad, 1095 */}
    <Sequence from={p45In} durationInFrames={ghzIn + 8 - p45In}>
      <Fade from={ghzIn - p45In} len={8} out>
        <Lift>
          <GhazaliMap
            draw={at('p45', 'Écoute') - p45In}
            cam={[
              {f: 0, x: 960, y: 540, k: 1},
              {f: at('p45', 'Écoute') + 20 - p45In, x: 960, y: 540, k: 1},
              {f: at('p46', 'Bagdad') - p45In, x: 1240, y: 570, k: 1.8},
            ]}
            bagdad={at('p46', 'Bagdad') - p45In}
            bagdadSub={{t: '1095', at: at('p46', 'mille') - p45In}}
          />
        </Lift>
        <Kinetic lines={[{t: 'Pourquoi quelqu’un ferait ça de son plein gré ?', at: 4, y: 470, size: 60, italic: true, out: at('p45', 'Écoute') - 8 - p45In}]} />
      </Fade>
    </Sequence>

    {/* p48 : il part ; près de deux ans à Damas */}
    <Sequence from={routeIn} durationInFrames={photoIn + 10 - routeIn}>
      <Fade from={photoIn - routeIn} len={10} out>
        <Lift>
          <GhazaliMap
            draw={-60}
            cam={[
              {f: 0, x: 1240, y: 570, k: 1.8},
              {f: at('p48', 'Damas') - routeIn, x: 943, y: 520, k: 1.2},
              {f: photoIn - routeIn, x: 700, y: 545, k: 1.6},
            ]}
            bagdad={-30}
            damas={at('p48', 'Damas') - routeIn}
            route={[at('p48', 'part') - routeIn, at('p48', 'Damas') - routeIn]}
            routeLabel={{t: 'près de deux ans à Damas', at: at('p48', 'deux') - routeIn}}
          />
        </Lift>
      </Fade>
    </Sequence>

    {cits.map(({from, to, sound, ...p}, i) => (
      <Sequence key={i} from={from} durationInFrames={to - from}>
        {p.cap === 'photo_omeyyades' ? (
          <Push len={to - from} to={1.1} ox={470} oy={200}>
            <Citation {...p} />
          </Push>
        ) : (
          <Citation {...p} />
        )}
      </Sequence>
    ))}

    {/* p49 : pas un éloge de la fuite ; l'Iḥyāʾ, livre 16 ; l'intention */}
    <Sequence from={p49In} durationInFrames={p50In - p49In}>
      <Kinetic lines={[{t: 'Ce n’est pas un éloge de la fuite.', at: 4, y: 470, size: 66, italic: true, red: ['fuite.'], out: at('p49', 'Il') - 6 - p49In}]} />
      <Lift>
        <NoteCard
          n={{
            at: at('p49', 'livre') - p49In,
            kicker: 'IḤYĀʾ ʿULŪM AL-DĪN · LIVRE 16',
            big: 'La retraite',
            text: 'Kitāb ādāb al-ʿuzla',
            chips: [
              {t: 'VIVRE AU MILIEU DES GENS', at: at('p49', 'vivre') - p49In},
              {t: 'OU SE RETIRER ?', at: at('p49', 'retirer') - p49In},
            ],
          }}
          x={250}
          y={260}
          w={640}
          tone="ink"
        />
        <NoteCard n={{at: at('p49', 'réponse') - p49In, kicker: 'SA RÉPONSE', big: 'Ça dépend', text: 'et d’abord de l’intention.'}} x={1010} y={260} w={620} tone="gold" />
        <NoteCard n={{at: at('p49', 'revenir') - 4 - p49In, kicker: 'ET LUI-MÊME', text: 'a fini par revenir enseigner.'}} x={1010} y={600} w={620} tone="ink" />
      </Lift>
    </Sequence>

    {/* p50-p51 : « on fait le dhikr » ; répéter un nom, encore et encore */}
    <Sequence from={p50In} durationInFrames={dhikrIn + 8 - p50In}>
      <Fade from={dhikrIn - p50In} len={8} out>
        <Kinetic
          lines={[
            {t: 'Seul dans une pièce fermée, on fait quoi ?', at: at('p50', 'seul') - p50In, y: 470, size: 60, italic: true, out: at('p50', 'Dans', 'start', 1) - 6 - p50In},
            {t: 'répéter un nom. Encore, et encore.', at: at('p51', 'répéter') - p50In, y: 760, size: 56, italic: true, gold: ['nom.']},
            {t: 'AILLEURS : MANTRA', at: at('p51', 'mantra') - 4 - p50In, y: 860, size: 24, mono: true, stagger: 6},
          ]}
        />
        <ArabicWord ar="ذكر" latin="DHIKR" gloss="le rappel" at={at('p50', 'dhikr') - 8 - p50In} glossAt={at('p51', 'rappel') - p50In} y={150} out={at('p51', 'Concrètement') - 6 - p50In} />
        <Lift>
          <Tasbih
            at={at('p51', 'Concrètement') - p50In}
            beats={[at('p51', 'nom') - p50In, at('p51', 'Encore') - p50In, at('p51', 'encore', 'start', 1) - p50In]}
          />
        </Lift>
      </Fade>
    </Sequence>

    {/* p51 : le point fixe (3D) */}
    <Sequence from={dhikrIn} durationInFrames={dhikrN}>
      <Shot3D dir="dhikr" frames={dhikrN} label="La pièce nue. Sur « meuble », le point d'or se pose au centre ; le pion s'en éloigne (« l'esprit part ») et y revient, deux fois." />
    </Sequence>

    {/* p52 : le verset. Aucun mouvement, aucun son dessous. */}
    <Sequence from={verseIn} durationInFrames={aroll6 - verseIn}>
      <Verse out={aroll6 - verseIn - 14} />
    </Sequence>
  </>
);

/** Au premier plan : le face caméra. */
export const P4Front: React.FC = () => (
  <Sequence from={aroll6} durationInFrames={fondIn - aroll6}>
    <ARoll shot="PLAN TAILLE · la veste visible" line="« La voie que je suis s'appelle la Karkariya. […] Cette veste rapiécée, c'est son habit. »" />
  </Sequence>
);

/** Fenêtre où rien ne doit jouer (le verset) : la musique s'y coupe. */
export const VERSE_SILENCE: [number, number] = [verseIn, aroll6];
