import React, {createContext, useContext} from 'react';
import {fr} from './fr';
import {en} from './en';
import {ur} from './ur';

export type Lang = 'fr' | 'en' | 'ur';
export const LanguageContext = createContext<Lang>('fr');
export const LanguageProvider = LanguageContext.Provider;
export const useLang = () => useContext(LanguageContext);
const dictionaries: Record<Lang, Record<keyof typeof fr, string>> = {fr, en, ur};
export const translator = (lang: Lang) => (key: string): string => {
  const dictionary = dictionaries[lang];
  if (!Object.prototype.hasOwnProperty.call(dictionary, key)) throw new Error(`Texte sans traduction : ${key}`);
  return dictionary[key as keyof typeof fr];
};
export const useText = () => translator(useLang());

// Écritures de droite à gauche (ourdou ; l'arabe suivra le même chemin).
const RTL: readonly string[] = ['ur', 'ar'];
export const isRtl = (lang: Lang) => RTL.includes(lang);
export const useRtl = () => isRtl(useLang());
