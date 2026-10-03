// Direction artistique « La pièce » : papier, encre, et deux couleurs qui ont un sens.
export const C = {
  paper: '#E8E6E0', // papier froid (science)
  paperWarm: '#EEE6D6', // papier chaud (tradition), à partir de Pascal
  sheet: '#F6F5F1', // feuille de document
  ink: '#22211E',
  inkSoft: 'rgba(34,33,30,0.55)',
  inkFaint: 'rgba(34,33,30,0.18)',
  bars: '#CFCBC2', // lignes de texte abstraites
  red: '#D7261E', // la fuite : bouton, porte, notification
  gold: '#C8962E', // le centre : point fixe, rappel
  night: '#0E0E0D',
};

export const F = {
  serif: "'Garamond', 'EB Garamond', serif",
  mono: "'Plex Mono', 'IBM Plex Mono', monospace",
};

// Plan de la pièce : mêmes valeurs que tools/maquette.py (1 m = 1920 / 7.2 px)
export const ROOM = {
  w: 4.0,
  d: 3.0,
  wall: 0.15,
  door: [0.95, 1.85] as const,
  table: {x: 0.35, y: 0.62, w: 0.9, d: 0.5},
  chair: {x: 0.35, y: 0.05, s: 0.44},
  button: {x: 0.6, y: 0.66, r: 0.055},
};
export const S = 1920 / 7.2;
export const px = (x: number) => 960 + x * S;
export const py = (y: number) => 540 - y * S;
