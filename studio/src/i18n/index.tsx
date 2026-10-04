import React, {createContext, useContext} from 'react';
import {fr} from './fr';
import {en} from './en';

export type Lang = 'fr' | 'en';
export const LanguageContext = createContext<Lang>('fr');
export const LanguageProvider = LanguageContext.Provider;
export const useLang = () => useContext(LanguageContext);
export const translator = (lang: Lang) => (key: string): string => {
  const dictionary = lang === 'en' ? en : fr;
  if (!Object.prototype.hasOwnProperty.call(dictionary, key)) throw new Error(`Texte sans traduction : ${key}`);
  return dictionary[key as keyof typeof fr];
};
export const useText = () => translator(useLang());
