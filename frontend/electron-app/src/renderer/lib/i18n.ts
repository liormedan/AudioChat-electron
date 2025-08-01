import { dictionaries } from '../locales';
import { useLanguage } from '../contexts/language-context';

export const t = (key: string, lang: string): string => {
  const dict = dictionaries[lang] || {};
  return dict[key] || key;
};

export const useTranslation = () => {
  const { language } = useLanguage();

  return {
    t: (key: string) => t(key, language),
    language,
  };
};
