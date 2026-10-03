// Vraies pages capturées par tools/capture.py : image dans public/captures/,
// rectangles des passages (px CSS de la page) dans src/data/captures/.
import pmc_domicile from './data/captures/pmc_domicile.json';
import pmc_etude9 from './data/captures/pmc_etude9.json';
import pmc_fin from './data/captures/pmc_fin.json';
import pmc_methode from './data/captures/pmc_methode.json';
import pmc_preparation from './data/captures/pmc_preparation.json';
import pmc_resultats from './data/captures/pmc_resultats.json';
import pmc_revue from './data/captures/pmc_revue.json';
import pmc_titre from './data/captures/pmc_titre.json';
import pmc_vagabondage from './data/captures/pmc_vagabondage.json';

export type Rect = {x: number; y: number; w: number; h: number};
export type CapMeta = {id: string; w: number; h: number; highlights: {text: string; rects: Rect[]}[]};

export const CAP: Record<string, CapMeta> = {
  pmc_revue,
  pmc_titre,
  pmc_methode,
  pmc_resultats,
  pmc_vagabondage,
  pmc_domicile,
  pmc_etude9,
  pmc_preparation,
  pmc_fin,
};

/** Numéro d'un passage par son texte (évite les indices magiques dans le montage). */
export const hl = (cap: string, text: string) => {
  const i = CAP[cap].highlights.findIndex((h) => h.text === text || h.text.startsWith(text));
  if (i < 0) throw new Error(`passage inconnu dans ${cap} : ${text}`);
  return i;
};
