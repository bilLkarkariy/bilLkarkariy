import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {Paper} from '../components/Paper';
import {createCues} from '../cues';
import {Lang} from '../i18n';
import {Kinetic} from '../scenes/Part4';

/**
 * --props '{"faceless":true}' : Billel n'apparaît qu'au tout début (« Quinze minutes »).
 * Les autres fenêtres face caméra deviennent du texte sur papier, sous la lumière de la fenêtre.
 * Les fenêtres 6 (la veste) et 7 (l'invitation) restent vides : rushes et passage au crayon posés au montage.
 * Bornes identiques aux <ARoll> de V01.tsx, p3.tsx et p5.tsx. En anglais et en arabe, les mots de calage passent par
 * src/data/v01_en.anchors.json et v01_ar.anchors.json (clé = le mot français).
 */
type Line = React.ComponentProps<typeof Kinetic>['lines'][number];

const makeFaceless = (lang: Lang) => {
  const {at} = createCues(lang);
  // (français, anglais, arabe : mêmes repères, une ligne par langue)
  const pick = <T,>(fr: T, en: T, ar: T): T => (lang === 'en' ? en : lang === 'ar' ? ar : fr);
  const w2 = at('p5') - 3;
  const w3 = at('p14') - 10;
  const w4 = at('p22') - 6;
  const w5 = at('p33') - 6;
  const w8 = at('p66') - 6;
  const w9 = at('p68') - 2;
  const L = (id: string, w: string, from: number, nth = 0) => at(id, w, 'start', nth) - from;

  const Page: React.FC<{from: number; to: number; lines: Line[]}> = ({from, to, lines}) => (
    <Sequence from={from} durationInFrames={to - from}>
      <AbsoluteFill>
        <Paper grid={0.8} />
        <Kinetic lines={lines} />
      </AbsoluteFill>
    </Sequence>
  );

  const Faceless: React.FC = () => (
    <>
      {/* 2 · « Et je suis presque sûr que toi aussi, tu aurais appuyé. » */}
      <Page
        from={w2}
        to={at('p6') - 3}
        lines={[
          {t: pick('Je suis presque sûr que toi aussi,', 'I’m pretty sure', 'وأنا شبه متأكد أنك أنت أيضًا'), at: L('p5', 'presque', w2) - 2, y: 420, size: 54, italic: true},
          {t: pick('tu aurais appuyé.', 'you would have pressed it too.', 'كنت ستضغط عليه.'), at: L('p5', 'tu', w2) - 2, y: 520, size: pick(110, 92, 110), red: pick(['appuyé.'], ['pressed'], ['ستضغط'])},
        ]}
      />

      {/* 3 · « Tu te dis peut-être : des étudiants, dans un labo… » */}
      <Page
        from={w3}
        to={at('p15') - 6}
        lines={[
          {t: pick('« des étudiants, dans un labo… »', '“students in a lab?”', '«طلاب في مختبر؟»'), at: L('p14', 'des', w3) - 2, y: 380, size: 64, italic: true},
          {t: pick('ÇA NE PROUVE PAS GRAND-CHOSE ?', 'THAT DOESN’T TELL US MUCH', 'هذا لا يثبت الكثير'), at: L('p14', 'ça', w3), y: 520, size: 34, mono: true, stagger: 3},
          {t: pick('Les chercheurs se sont posé la même question.', 'The researchers wondered about that too.', 'والباحثون طرحوا السؤال نفسه.'), at: L('p14', 'les', w3) - 2, y: 660, size: 48, italic: true, gold: pick(['même'], ['too.'], ['نفسه'])},
        ]}
      />

      {/* 4 · « Question. … c'était quand ? » puis 2 s de silence : la question reste seule */}
      <Page
        from={w4}
        to={at('p23') - 8}
        lines={[
          {t: pick('QUESTION', 'QUESTION', 'سؤال'), at: L('p22', 'question', w4) - 2, y: 270, size: 28, mono: true, stagger: 4},
          {t: pick('Cinq minutes sans rien faire.', 'Five minutes doing nothing.', 'خمس دقائق دون أن تفعل شيئًا.'), at: L('p22', 'cinq', w4) - 2, y: 380, size: 72, italic: true},
          {t: pick('SANS ÉCRAN · SANS MUSIQUE · SANS PARLER', 'NO SCREEN · NO MUSIC · NO CONVERSATION', 'بلا شاشة · بلا موسيقى · بلا كلام'), at: L('p22', 'écran', w4) - 6, y: 510, size: 30, mono: true, stagger: 6},
          {t: pick('C’était quand ?', 'When was it?', 'متى كان ذلك؟'), at: L('p22', "c'était", w4) - 2, y: 680, size: 130, gold: pick(['quand'], ['When'], ['متى'])},
        ]}
      />

      {/* 5 · « …c'est quoi ? » « Je crois qu'on se trompe de problème… un esprit qui n'a pas de centre. » */}
      <Page
        from={w5}
        to={at('p35') - 4}
        lines={[
          {t: pick('Si le téléphone n’est pas la cause…', 'If the phone isn’t the cause…', 'فإذا لم يكن الهاتف هو السبب…'), at: L('p33', 'si', w5) - 2, y: 420, size: 60, italic: true, out: L('p34', 'je', w5) - 6},
          {t: pick('c’est quoi ?', 'what is?', 'فما هو؟'), at: L('p33', "c'est", w5) - 2, y: 540, size: 130, out: L('p34', 'je', w5) - 6},
          {t: pick('On se trompe de problème.', 'We’re looking at the wrong problem.', 'نخطئ في تحديد المشكلة.'), at: L('p34', "qu'on", w5) - 4, y: 360, size: 64, italic: true},
          {t: pick('Pas d’être seul.', 'Not being alone.', 'لا أن تكون وحدك.'), at: L('p34', 'pas', w5) - 2, y: 480, size: 72, italic: true, strike: L('p34', "c'est", w5) + 2},
          {t: pick('Seul avec un esprit sans centre.', 'Alone with a mind that has no centre.', 'وحدك مع عقلٍ لا مركز له.'), at: L('p34', 'esprit', w5) - 4, y: 610, size: pick(76, 68, 72), gold: pick(['centre.'], ['centre.'], ['مركز'])},
        ]}
      />

      {/* 8 · « Non entraîné. Tout est dans ce mot. Ça veut dire que ça s'entraîne. » puis p67 jusqu'à « meublé » */}
      <Page
        from={w8}
        to={at('p67', 'meublé') - 10}
        lines={[
          {t: pick('Non entraîné.', 'Untutored.', 'غير المدرَّب.'), at: L('p66', 'non', w8) - 2, y: 380, size: 130, italic: true, out: L('p67', 'tu', w8) - 6},
          {t: pick('TOUT EST DANS CE MOT', 'THAT’S THE KEY WORD', 'كل شيء في هذه الكلمة'), at: L('p66', 'tout', w8) - 2, y: 600, size: 30, mono: true, stagger: 4, out: L('p67', 'tu', w8) - 6},
          {t: pick('Ça s’entraîne.', 'Something you can learn.', 'يمكن تدريبه.'), at: L('p66', "s'entraîne", w8) - 4, y: 700, size: 90, gold: pick(['s’entraîne.'], ['learn.'], ['تدريبه']), out: L('p67', 'tu', w8) - 6},
          {t: pick('Tu n’as pas un problème avec la solitude.', 'You don’t have a problem with solitude.', 'ليست لديك مشكلة مع الوحدة.'), at: L('p67', 'tu', w8) - 2, y: 480, size: 60, italic: true},
        ]}
      />

      {/* 9 · « Prochaine vidéo : … » jusqu'à l'écran de fin */}
      <Page
        from={w9}
        to={at('p68', undefined, 'end') + 20}
        lines={[
          {t: pick('PROCHAINE VIDÉO', 'NEXT TIME', 'في الفيديو القادم'), at: L('p68', 'prochaine', w9), y: 330, size: 28, mono: true, stagger: 4},
          {t: pick('Pourquoi « ne penser à rien »', 'Why trying to think about nothing', 'لماذا تفشل إلى هذا الحد'), at: L('p68', 'pourquoi', w9) - 2, y: 450, size: 70, italic: true, red: pick<string[] | undefined>(undefined, undefined, ['تفشل'])},
          {t: pick('marche si mal.', 'works so badly.', 'محاولةُ ألّا تفكر في شيء.'), at: L('p68', 'marche', w9) - 2, y: 545, size: 70, italic: true, red: pick(['mal.'], ['badly.'], [])},
          {t: pick('Et ce que les soufis font à la place.', 'And what Sufis do instead.', 'وما الذي يفعله الصوفية بدلًا من ذلك.'), at: L('p68', 'et', w9) - 2, y: 680, size: 48, gold: pick(['soufis'], ['Sufis'], ['الصوفية'])},
        ]}
      />
    </>
  );
  return Faceless;
};

const cache: Partial<Record<Lang, React.FC>> = {};
export const getFaceless = (lang: Lang) => (cache[lang] ??= makeFaceless(lang));
