// Le montage est indexé sur le texte : chaque événement visuel est accroché à
// un mot du script (src/data/*.vo.json, produit par tools/vo.py). Quand Billel
// enregistre sa vraie prise, on relance l'alignement et tout se recale.
import vo from './data/hook.vo.json';

export const FPS = 30;

type Word = {w: string; start: number; end: number};
type Seg = {id: string; text: string; start: number; end: number; words: Word[]};

const segments = vo.segments as Seg[];

const norm = (s: string) =>
  s
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '');

export const seg = (id: string): Seg => {
  const s = segments.find((x) => x.id === id);
  if (!s) throw new Error(`segment inconnu : ${id}`);
  return s;
};

export const word = (id: string, w: string, nth = 0): Word => {
  const m = seg(id).words.filter((x) => norm(x.w) === norm(w));
  if (!m[nth]) throw new Error(`mot introuvable : ${id} « ${w} »`);
  return m[nth];
};

export const toF = (s: number) => Math.round(s * FPS);

/** Image où commence (ou finit) un segment, ou un mot de ce segment. */
export const at = (id: string, w?: string, edge: 'start' | 'end' = 'start', nth = 0) =>
  toF(w ? word(id, w, nth)[edge] : seg(id)[edge]);

export const DURATION = toF(vo.duration);
export const VO_SRC = vo.audio;
