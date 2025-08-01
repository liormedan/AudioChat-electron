import React, { createContext, useContext, useState } from 'react';
import en from '../locales/en.json';
import he from '../locales/he.json';

export type Locale = 'en' | 'he';

const translations = { en, he } as const;

interface LocaleProviderState {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
  direction: 'ltr' | 'rtl';
}

const LocaleProviderContext = createContext<LocaleProviderState | undefined>(undefined);

interface LocaleProviderProps {
  children: React.ReactNode;
  defaultLocale?: Locale;
}

export const LocaleProvider: React.FC<LocaleProviderProps> = ({ children, defaultLocale = 'en' }) => {
  const [locale, setLocale] = useState<Locale>(defaultLocale);

  const t = (key: string): string => {
    const keys = key.split('.');
    let result: any = translations[locale];
    for (const k of keys) {
      result = result?.[k];
      if (result === undefined) return key;
    }
    return typeof result === 'string' ? result : key;
  };

  const direction: 'ltr' | 'rtl' = locale === 'he' ? 'rtl' : 'ltr';

  return (
    <LocaleProviderContext.Provider value={{ locale, setLocale, t, direction }}>
      {children}
    </LocaleProviderContext.Provider>
  );
};

export const useLocale = () => {
  const context = useContext(LocaleProviderContext);
  if (!context) {
    throw new Error('useLocale must be used within a LocaleProvider');
  }
  return context;
};
