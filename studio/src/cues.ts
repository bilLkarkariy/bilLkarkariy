// Repères sémantiques : même montage, un alignement indépendant par langue.
import frVO from './data/v01.vo.json';
import enVO from './data/v01_en.vo.json';
import arVO from './data/v01_ar.vo.json';
import groups from './data/v01_en.groups.json';
import anchors from './data/v01_en.anchors.json';
import arGroups from './data/v01_ar.groups.json';
import arAnchors from './data/v01_ar.anchors.json';
import type {Lang} from './i18n';

export const FPS = 30;
export const LEAD = 24;
export type Word = {w: string; start: number; end: number};
export type Seg = {id: string; text: string; start: number; end: number; words: Word[]};
export type Voice = {audio: string | null; duration: number; segments: Seg[]; estimated?: boolean;
  silences?: {kind: string; start: number; end: number}[]};
export const voices: Record<Lang, Voice> = {fr: frVO, en: enVO, ar: arVO};
// (arabe : harakat, hamza et tatweel tombent, ٱ ة ى deviennent ا ه ي ; rien ne change pour le français et l'anglais)
export const norm = (s: string) => s.normalize('NFD').replace(/[̀-ًͯ-ٰٟـ]/g, '').toLowerCase()
  .replace(/ٱ/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
  .replace(/[^a-z0-9ء-غف-ي]/g, '');
export const toF = (s: number) => Math.round(s * FPS);

type Anchor = string | {phrase: string; nth: number};
// Version française : les mots du montage sont ceux de la voix. Autres langues : paragraphes p… regroupés
// (src/data/v01_<langue>.groups.json) et repères (clé = le mot français, src/data/v01_<langue>.anchors.json).
const targetsFor: Partial<Record<Lang, Record<string, Record<string, Anchor>>>> = {en: anchors, ar: arAnchors};
const groupsFor: Partial<Record<Lang, Record<string, string[]>>> = {en: groups, ar: arGroups};

export const createCues = (lang: Lang = 'fr') => {
  const vo = voices[lang];
  const seg = (id: string): Seg => {
    const direct = vo.segments.find((s) => s.id === id);
    if (direct) return direct;
    const ids = groupsFor[lang]?.[id];
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
    const code = lang.toUpperCase();
    const target = targetsFor[lang]?.[id]?.[`${w}|${nth}`];
    if (!target) throw new Error(`Repère ${code} non traduit : ${id} « ${w} » #${nth}`);
    const phrase = typeof target === 'string' ? target : target.phrase;
    const occurrence = typeof target === 'string' ? 0 : target.nth;
    const tokens = phrase.split(' ').map(norm);
    const matches = words.map((_, i) => i).filter((i) => tokens.every((token, j) => norm(words[i + j]?.w ?? '') === token));
    const i = matches[occurrence];
    if (i === undefined) throw new Error(`Repère ${code} introuvable : ${id} « ${phrase} » #${occurrence}`);
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
