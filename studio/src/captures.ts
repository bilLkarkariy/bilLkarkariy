// Vraies pages capturées par tools/capture.py (web) et tools/pdfcap.py (PDF) : image dans public/captures/,
// rectangles des passages (px CSS de la page) dans src/data/captures/.
import arcep_2025 from './data/captures/arcep_2025.json';
import ghazali_baghdad from './data/captures/ghazali_baghdad.json';
import ghazali_coeur from './data/captures/ghazali_coeur.json';
import ghazali_langue from './data/captures/ghazali_langue.json';
import ghazali_minaret from './data/captures/ghazali_minaret.json';
import karkariya_fondements from './data/captures/karkariya_fondements.json';
import kg_figure from './data/captures/kg_figure.json';
import kg_methode from './data/captures/kg_methode.json';
import kg_page from './data/captures/kg_page.json';
import kg_resultats from './data/captures/kg_resultats.json';
import mm_3h from './data/captures/mm_3h.json';
import mm_mobile from './data/captures/mm_mobile.json';
import pascal_chambre from './data/captures/pascal_chambre.json';
import pascal_solitude from './data/captures/pascal_solitude.json';
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
  arcep_2025,
  ghazali_baghdad,
  ghazali_coeur,
  ghazali_langue,
  ghazali_minaret,
  karkariya_fondements,
  kg_figure,
  kg_methode,
  kg_page,
  kg_resultats,
  mm_3h,
  mm_mobile,
  pascal_chambre,
  pascal_solitude,
  pmc_domicile,
  pmc_etude9,
  pmc_fin,
  pmc_methode,
  pmc_preparation,
  pmc_resultats,
  pmc_revue,
  pmc_titre,
  pmc_vagabondage,
};

/** Numéro d'un passage par son texte (évite les indices magiques dans le montage). */
export const hl = (cap: string, text: string) => {
  const i = CAP[cap].highlights.findIndex((h) => h.text === text || h.text.startsWith(text));
  if (i < 0) throw new Error(`passage inconnu dans ${cap} : ${text}`);
  return i;
};
