import React, { createContext, useContext, useEffect, useState } from 'react';

export type Direction = 'ltr' | 'rtl';

interface LanguageProviderProps {
  children: React.ReactNode;
  defaultLang?: string;
  defaultDir?: Direction;
  storageKey?: string;
}

interface LanguageContextValue {
  language: string;
  direction: Direction;
  setLanguage: (lang: string, dir?: Direction) => void;
}

const initialState: LanguageContextValue = {
  language: 'he',
  direction: 'rtl',
  setLanguage: () => null,
};

const LanguageContext = createContext<LanguageContextValue>(initialState);

export const LanguageProvider: React.FC<LanguageProviderProps> = ({
  children,
  defaultLang = 'he',
  defaultDir = 'rtl',
  storageKey = 'app-language',
}) => {
  const [language, setLanguageState] = useState<string>(
    () => localStorage.getItem(storageKey) || defaultLang,
  );
  const [direction, setDirectionState] = useState<Direction>(
    () => (localStorage.getItem(`${storageKey}-dir`) as Direction) || defaultDir,
  );

  useEffect(() => {
    localStorage.setItem(storageKey, language);
    localStorage.setItem(`${storageKey}-dir`, direction);
    document.documentElement.lang = language;
    document.documentElement.dir = direction;
  }, [language, direction]);

  const setLanguage = (lang: string, dir?: Direction) => {
    setLanguageState(lang);
    setDirectionState(dir ?? (lang === 'he' ? 'rtl' : 'ltr'));
  };

  return (
    <LanguageContext.Provider value={{ language, direction, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
