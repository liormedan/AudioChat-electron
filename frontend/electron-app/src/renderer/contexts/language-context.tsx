add-language-support-to-electron-app
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useUserStore } from '../stores';

type Language = 'en' | 'he';

interface LanguageContextValue {
  language: Language;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextValue>({
  language: 'he',
  setLanguage: () => undefined,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { updateUserPreferences } = useUserStore();
  const [language, setLanguageState] = useState<Language>(() => {
    const stored = localStorage.getItem('language') as Language | null;
    return stored || 'he';
  });

  useEffect(() => {
    localStorage.setItem('language', language);
    updateUserPreferences({ language });
  }, [language, updateUserPreferences]);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>



      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
