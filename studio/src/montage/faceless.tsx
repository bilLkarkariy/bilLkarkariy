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
 * Bornes identiques aux <ARoll> de V01.tsx, p3.tsx et p5.tsx. En anglais et en ourdou, les mots de calage passent par
 * src/data/v01_<langue>.anchors.json (clé = le mot français).
 */
type Line = React.ComponentProps<typeof Kinetic>['lines'][number];

const makeFaceless = (lang: Lang) => {
  const {at} = createCues(lang);
  // T(français, anglais, ourdou)
  const T = <V,>(fr: V, en: V, ur: V): V => (lang === 'en' ? en : lang === 'ur' ? ur : fr);
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
          {t: T('Je suis presque sûr que toi aussi,', 'I’m pretty sure', 'مجھے تقریباً یقین ہے'), at: L('p5', 'presque', w2) - 2, y: 420, size: 54, italic: true},
          {t: T('tu aurais appuyé.', 'you would have pressed it too.', 'کہ آپ بھی اسے دبا دیتے۔'), at: L('p5', 'tu', w2) - 2, y: 520, size: T(110, 92, 92), red: T(['appuyé.'], ['pressed'], ['دبا'])},
        ]}
      />

      {/* 3 · « Tu te dis peut-être : des étudiants, dans un labo… » */}
      <Page
        from={w3}
        to={at('p15') - 6}
        lines={[
          {t: T('« des étudiants, dans un labo… »', '“students in a lab?”', '“لیب میں طلبہ؟”'), at: L('p14', 'des', w3) - 2, y: 380, size: 64, italic: true},
          {t: T('ÇA NE PROUVE PAS GRAND-CHOSE ?', 'THAT DOESN’T TELL US MUCH', 'اس سے کچھ خاص ثابت نہیں ہوتا'), at: L('p14', 'ça', w3), y: 520, size: 34, mono: true, stagger: 3},
          {t: T('Les chercheurs se sont posé la même question.', 'The researchers wondered about that too.', 'محققین نے بھی یہی سوال اٹھایا۔'), at: L('p14', 'les', w3) - 2, y: 660, size: 48, italic: true, gold: T(['même'], ['too.'], ['یہی'])},
        ]}
      />

      {/* 4 · « Question. … c'était quand ? » puis 2 s de silence : la question reste seule */}
      <Page
        from={w4}
        to={at('p23') - 8}
        lines={[
          {t: T('QUESTION', 'QUESTION', 'سوال'), at: L('p22', 'question', w4) - 2, y: 270, size: 28, mono: true, stagger: 4},
          {t: T('Cinq minutes sans rien faire.', 'Five minutes doing nothing.', 'پانچ منٹ، کچھ کیے بغیر۔'), at: L('p22', 'cinq', w4) - 2, y: 380, size: 72, italic: true},
          {t: T('SANS ÉCRAN · SANS MUSIQUE · SANS PARLER', 'NO SCREEN · NO MUSIC · NO CONVERSATION', 'نہ اسکرین · نہ موسیقی · نہ بات چیت'), at: L('p22', 'écran', w4) - 6, y: 510, size: 30, mono: true, stagger: 6},
          {t: T('C’était quand ?', 'When was it?', 'وہ کب تھا؟'), at: L('p22', "c'était", w4) - 2, y: 680, size: 130, gold: T(['quand'], ['When'], ['کب'])},
        ]}
      />

      {/* 5 · « …c'est quoi ? » « Je crois qu'on se trompe de problème… un esprit qui n'a pas de centre. » */}
      <Page
        from={w5}
        to={at('p35') - 4}
        lines={[
          {t: T('Si le téléphone n’est pas la cause…', 'If the phone isn’t the cause…', 'اگر فون وجہ نہیں ہے…'), at: L('p33', 'si', w5) - 2, y: 420, size: 60, italic: true, out: L('p34', 'je', w5) - 6},
          {t: T('c’est quoi ?', 'what is?', 'تو پھر کیا ہے؟'), at: L('p33', "c'est", w5) - 2, y: 540, size: 130, out: L('p34', 'je', w5) - 6},
          {t: T('On se trompe de problème.', 'We’re looking at the wrong problem.', 'ہم غلط مسئلے کو دیکھ رہے ہیں۔'), at: L('p34', "qu'on", w5) - 4, y: 360, size: 64, italic: true},
          {t: T('Pas d’être seul.', 'Not being alone.', 'اکیلا ہونا مسئلہ نہیں۔'), at: L('p34', 'pas', w5) - 2, y: 480, size: 72, italic: true, strike: L('p34', "c'est", w5) + 2},
          {t: T('Seul avec un esprit sans centre.', 'Alone with a mind that has no centre.', 'ایسے ذہن کے ساتھ اکیلا، جس کا کوئی مرکز نہیں۔'), at: L('p34', 'esprit', w5) - 4, y: 610, size: T(76, 68, 64), gold: T(['centre.'], ['centre.'], ['مرکز'])},
        ]}
      />

      {/* 8 · « Non entraîné. Tout est dans ce mot. Ça veut dire que ça s'entraîne. » puis p67 jusqu'à « meublé » */}
      <Page
        from={w8}
        to={at('p67', 'meublé') - 10}
        lines={[
          {t: T('Non entraîné.', 'Untutored.', 'غیر تربیت یافتہ۔'), at: L('p66', 'non', w8) - 2, y: 380, size: 130, italic: true, out: L('p67', 'tu', w8) - 6},
          {t: T('TOUT EST DANS CE MOT', 'THAT’S THE KEY WORD', 'ساری بات اسی لفظ میں ہے'), at: L('p66', 'tout', w8) - 2, y: 600, size: 30, mono: true, stagger: 4, out: L('p67', 'tu', w8) - 6},
          {t: T('Ça s’entraîne.', 'Something you can learn.', 'اس کی تربیت ہو سکتی ہے۔'), at: L('p66', "s'entraîne", w8) - 4, y: 700, size: 90, gold: T(['s’entraîne.'], ['learn.'], ['تربیت']), out: L('p67', 'tu', w8) - 6},
          {t: T('Tu n’as pas un problème avec la solitude.', 'You don’t have a problem with solitude.', 'آپ کو تنہائی سے کوئی مسئلہ نہیں۔'), at: L('p67', 'tu', w8) - 2, y: 480, size: 60, italic: true},
        ]}
      />

      {/* 9 · « Prochaine vidéo : … » jusqu'à l'écran de fin */}
      <Page
        from={w9}
        to={at('p68', undefined, 'end') + 20}
        lines={[
          {t: T('PROCHAINE VIDÉO', 'NEXT TIME', 'اگلی ویڈیو'), at: L('p68', 'prochaine', w9), y: 330, size: 28, mono: true, stagger: 4},
          {t: T('Pourquoi « ne penser à rien »', 'Why trying to think about nothing', '“کچھ نہ سوچنے” کی کوشش'), at: L('p68', 'pourquoi', w9) - 2, y: 450, size: 70, italic: true},
          {t: T('marche si mal.', 'works so badly.', 'اتنی بری طرح کیوں ناکام ہوتی ہے؟'), at: L('p68', 'marche', w9) - 2, y: 545, size: 70, italic: true, red: T(['mal.'], ['badly.'], ['ناکام'])},
          {t: T('Et ce que les soufis font à la place.', 'And what Sufis do instead.', 'اور صوفیا اس کے بجائے کیا کرتے ہیں۔'), at: L('p68', 'et', w9) - 2, y: 680, size: 48, gold: T(['soufis'], ['Sufis'], ['صوفیا'])},
        ]}
      />
    </>
  );
  return Faceless;
};

const cache: Partial<Record<Lang, React.FC>> = {};
export const getFaceless = (lang: Lang) => (cache[lang] ??= makeFaceless(lang));
