// Repères sémantiques : même montage, deux alignements indépendants.
import frVO from './data/v01.vo.json';
import enVO from './data/v01_en.vo.json';
import groups from './data/v01_en.groups.json';
import anchors from './data/v01_en.anchors.json';
import type {Lang} from './i18n';

export const FPS = 30;
export const LEAD = 24;
export type Word = {w: string; start: number; end: number};
export type Seg = {id: string; text: string; start: number; end: number; words: Word[]};
export type Voice = {audio: string | null; duration: number; segments: Seg[]; estimated?: boolean;
  silences?: {kind: string; start: number; end: number}[]};
export const voices: Record<Lang, Voice> = {fr: frVO, en: enVO};
export const norm = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
export const toF = (s: number) => Math.round(s * FPS);

type Anchor = string | {phrase: string; nth: number};
const targets = anchors as Record<string, Record<string, Anchor>>;
const englishGroups = groups as Record<string, string[]>;

export const createCues = (lang: Lang = 'fr') => {
  const vo = voices[lang];
  const seg = (id: string): Seg => {
    const direct = vo.segments.find((s) => s.id === id);
    if (direct) return direct;
    const ids = lang === 'en' ? englishGroups[id] : undefined;
    if (!ids) throw new Error(`Segment inconnu (${lang}) : ${id}`);
    const parts = ids.map((sid) => {
      const s = vo.segments.find((s) => s.id === sid);
      if (!s) throw new Error(`Segment manquant (${lang}) : ${sid}`);
      return s;
    });
    return {id, text: parts.map((s) => s.text).join(' '), start: parts[0].start,
      end: parts[parts.length - 1].end, words: parts.flatMap((s) => s.words)};
  };
  const word = (id: string, w: string, nth = 0): Word => {
    const words = seg(id).words;
    if (lang === 'fr') {
      const found = words.filter((x) => norm(x.w) === norm(w))[nth];
      if (!found) throw new Error(`Mot introuvable : ${id} « ${w} » #${nth}`);
      return found;
    }
    const target = targets[id]?.[`${w}|${nth}`];
    if (!target) throw new Error(`Repère EN non traduit : ${id} « ${w} » #${nth}`);
    const phrase = typeof target === 'string' ? target : target.phrase;
    const occurrence = typeof target === 'string' ? 0 : target.nth;
    const tokens = phrase.split(' ').map(norm);
    const matches = words.map((_, i) => i).filter((i) => tokens.every((token, j) => norm(words[i + j]?.w ?? '') === token));
    const i = matches[occurrence];
    if (i === undefined) throw new Error(`Repère EN introuvable : ${id} « ${phrase} » #${occurrence}`);
    return {w: phrase, start: words[i].start, end: words[i + tokens.length - 1].end};
  };
  const at = (id: string, w?: string, edge: 'start' | 'end' = 'start', nth = 0) =>
    LEAD + toF(w ? word(id, w, nth)[edge] : seg(id)[edge]);
  return {at, seg, word, vo, duration: LEAD + toF(vo.duration)};
};

// Compatibilité des outils et de la version FR existants.
export const {at, seg, word} = createCues('fr');
export const DURATION = LEAD + toF(frVO.duration);
export const VO_SRC = frVO.audio;
