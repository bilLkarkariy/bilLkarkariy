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
 * Bornes identiques aux <ARoll> de V01.tsx, p3.tsx et p5.tsx. En anglais, les mots de calage passent par
 * src/data/v01_en.anchors.json (clé = le mot français).
 */
type Line = React.ComponentProps<typeof Kinetic>['lines'][number];

const makeFaceless = (lang: Lang) => {
  const {at} = createCues(lang);
  const en = lang === 'en';
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
          {t: en ? 'I’m pretty sure' : 'Je suis presque sûr que toi aussi,', at: L('p5', 'presque', w2) - 2, y: 420, size: 54, italic: true},
          {t: en ? 'you would have pressed it too.' : 'tu aurais appuyé.', at: L('p5', 'tu', w2) - 2, y: 520, size: en ? 92 : 110, red: en ? ['pressed'] : ['appuyé.']},
        ]}
      />

      {/* 3 · « Tu te dis peut-être : des étudiants, dans un labo… » */}
      <Page
        from={w3}
        to={at('p15') - 6}
        lines={[
          {t: en ? '“students in a lab?”' : '« des étudiants, dans un labo… »', at: L('p14', 'des', w3) - 2, y: 380, size: 64, italic: true},
          {t: en ? 'THAT DOESN’T TELL US MUCH' : 'ÇA NE PROUVE PAS GRAND-CHOSE ?', at: L('p14', 'ça', w3), y: 520, size: 34, mono: true, stagger: 3},
          {t: en ? 'The researchers wondered about that too.' : 'Les chercheurs se sont posé la même question.', at: L('p14', 'les', w3) - 2, y: 660, size: 48, italic: true, gold: en ? ['too.'] : ['même']},
        ]}
      />

      {/* 4 · « Question. … c'était quand ? » puis 2 s de silence : la question reste seule */}
      <Page
        from={w4}
        to={at('p23') - 8}
        lines={[
          {t: 'QUESTION', at: L('p22', 'question', w4) - 2, y: 270, size: 28, mono: true, stagger: 4},
          {t: en ? 'Five minutes doing nothing.' : 'Cinq minutes sans rien faire.', at: L('p22', 'cinq', w4) - 2, y: 380, size: 72, italic: true},
          {t: en ? 'NO SCREEN · NO MUSIC · NO CONVERSATION' : 'SANS ÉCRAN · SANS MUSIQUE · SANS PARLER', at: L('p22', 'écran', w4) - 6, y: 510, size: 30, mono: true, stagger: 6},
          {t: en ? 'When was it?' : 'C’était quand ?', at: L('p22', "c'était", w4) - 2, y: 680, size: 130, gold: en ? ['When'] : ['quand']},
        ]}
      />

      {/* 5 · « …c'est quoi ? » « Je crois qu'on se trompe de problème… un esprit qui n'a pas de centre. » */}
      <Page
        from={w5}
        to={at('p35') - 4}
        lines={[
          {t: en ? 'If the phone isn’t the cause…' : 'Si le téléphone n’est pas la cause…', at: L('p33', 'si', w5) - 2, y: 420, size: 60, italic: true, out: L('p34', 'je', w5) - 6},
          {t: en ? 'what is?' : 'c’est quoi ?', at: L('p33', "c'est", w5) - 2, y: 540, size: 130, out: L('p34', 'je', w5) - 6},
          {t: en ? 'We’re looking at the wrong problem.' : 'On se trompe de problème.', at: L('p34', "qu'on", w5) - 4, y: 360, size: 64, italic: true},
          {t: en ? 'Not being alone.' : 'Pas d’être seul.', at: L('p34', 'pas', w5) - 2, y: 480, size: 72, italic: true, strike: L('p34', "c'est", w5) + 2},
          {t: en ? 'Alone with a mind that has no centre.' : 'Seul avec un esprit sans centre.', at: L('p34', 'esprit', w5) - 4, y: 610, size: en ? 68 : 76, gold: ['centre.']},
        ]}
      />

      {/* 8 · « Non entraîné. Tout est dans ce mot. Ça veut dire que ça s'entraîne. » puis p67 jusqu'à « meublé » */}
      <Page
        from={w8}
        to={at('p67', 'meublé') - 10}
        lines={[
          {t: en ? 'Untutored.' : 'Non entraîné.', at: L('p66', 'non', w8) - 2, y: 380, size: 130, italic: true, out: L('p67', 'tu', w8) - 6},
          {t: en ? 'THAT’S THE KEY WORD' : 'TOUT EST DANS CE MOT', at: L('p66', 'tout', w8) - 2, y: 600, size: 30, mono: true, stagger: 4, out: L('p67', 'tu', w8) - 6},
          {t: en ? 'Something you can learn.' : 'Ça s’entraîne.', at: L('p66', "s'entraîne", w8) - 4, y: 700, size: 90, gold: en ? ['learn.'] : ['s’entraîne.'], out: L('p67', 'tu', w8) - 6},
          {t: en ? 'You don’t have a problem with solitude.' : 'Tu n’as pas un problème avec la solitude.', at: L('p67', 'tu', w8) - 2, y: 480, size: 60, italic: true},
        ]}
      />

      {/* 9 · « Prochaine vidéo : … » jusqu'à l'écran de fin */}
      <Page
        from={w9}
        to={at('p68', undefined, 'end') + 20}
        lines={[
          {t: en ? 'NEXT TIME' : 'PROCHAINE VIDÉO', at: L('p68', 'prochaine', w9), y: 330, size: 28, mono: true, stagger: 4},
          {t: en ? 'Why trying to think about nothing' : 'Pourquoi « ne penser à rien »', at: L('p68', 'pourquoi', w9) - 2, y: 450, size: 70, italic: true},
          {t: en ? 'works so badly.' : 'marche si mal.', at: L('p68', 'marche', w9) - 2, y: 545, size: 70, italic: true, red: en ? ['badly.'] : ['mal.']},
          {t: en ? 'And what Sufis do instead.' : 'Et ce que les soufis font à la place.', at: L('p68', 'et', w9) - 2, y: 680, size: 48, gold: en ? ['Sufis'] : ['soufis']},
        ]}
      />
    </>
  );
  return Faceless;
};

const cache: Partial<Record<Lang, React.FC>> = {};
export const getFaceless = (lang: Lang) => (cache[lang] ??= makeFaceless(lang));
