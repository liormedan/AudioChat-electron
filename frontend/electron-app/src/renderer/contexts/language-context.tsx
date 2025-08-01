import React, { createContext, useContext, useState } from 'react';

export type TextDirection = 'ltr' | 'rtl';

interface LanguageContextValue {
  language: string;
  direction: TextDirection;
  setLanguage: (lang: string) => void;
}

const LanguageContext = createContext<LanguageContextValue>({
  language: 'en',
  direction: 'ltr',
  setLanguage: () => {},
});

const rtlLanguages = ['ar', 'he', 'fa', 'ur'];

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState('en');

  const direction: TextDirection = rtlLanguages.includes(language) ? 'rtl' : 'ltr';

  return (
    <LanguageContext.Provider value={{ language, direction, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
