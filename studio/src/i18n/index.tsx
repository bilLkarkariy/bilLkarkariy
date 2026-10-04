import React, {createContext, useContext} from 'react';
import {fr} from './fr';
import {en} from './en';
import {ar} from './ar';

export type Lang = 'fr' | 'en' | 'ar';
const dictionaries: Record<Lang, Record<keyof typeof fr, string>> = {fr, en, ar};
export const LanguageContext = createContext<Lang>('fr');
export const LanguageProvider = LanguageContext.Provider;
export const useLang = () => useContext(LanguageContext);
export const translator = (lang: Lang) => (key: string): string => {
  const dictionary = dictionaries[lang];
  if (!Object.prototype.hasOwnProperty.call(dictionary, key)) throw new Error(`Texte sans traduction : ${key}`);
  return dictionary[key as keyof typeof fr];
};
export const useText = () => translator(useLang());

// Écriture de droite à gauche (arabe). Pour le français et l'anglais, ces aides n'ajoutent rien :
// le HTML reste identique au caractère près.
export const isRTL = (lang: Lang) => lang === 'ar';
export const useRTL = () => isRTL(useLang());
/** Style à étaler sur un bloc de texte : `direction: rtl` en arabe, rien sinon. */
export const useDir = (): React.CSSProperties => (useRTL() ? {direction: 'rtl'} : {});
/** Texte sans lettre arabe (chiffres, signes) : il garde son sens de lecture de gauche à droite. */
export const hasArabic = (s: string) => /[\u0600-\u06ff]/.test(s);
/** Comme useDir, sauf pour un texte fait seulement de chiffres et de signes (« 0:04 / 0:20 »). */
export const useDirFor = (text: React.ReactNode): React.CSSProperties => {
  const dir = useDir();
  return typeof text === 'string' && !hasArabic(text) ? {} : dir;
};
/** Un groupe de chiffres (« 1 / 5 ») qui doit rester dans l'ordre de gauche à droite au milieu de l'arabe. */
export const Ltr: React.FC<{children: React.ReactNode}> = ({children}) =>
  useRTL() ? <span style={{direction: 'ltr', unicodeBidi: 'isolate', display: 'inline-block'}}>{children}</span> : <>{children}</>;
/** Arabe : pas d'interlettrage (il casse les liaisons entre les lettres). Rien pour les autres langues. */
export const RtlType: React.FC = () => (useRTL() ? <style>{'*{letter-spacing:0 !important}'}</style> : null);
