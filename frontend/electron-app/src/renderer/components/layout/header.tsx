import React from 'react';
import { useUIStore } from '../../stores';
import { Button } from '../ui/button';
import { Moon, Sun } from 'lucide-react';
import { useLanguage } from '../../contexts/language-context';
import { useTranslation } from '../../lib/i18n';

export const Header: React.FC = () => {
  const { theme, setTheme } = useUIStore();
  const { language, setLanguage } = useLanguage();
  const { t } = useTranslation();

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const toggleLanguage = () => {
    setLanguage(language === 'he' ? 'en' : 'he');
  };

  return (
    <header className="flex items-center justify-between p-4 border-b">
      <div>
        {/* Add any other header content here */}
      </div>
      <div>
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
        <Button variant="ghost" size="icon" onClick={toggleLanguage} className="ml-2">
          {t('toggle_language')}
        </Button>
      </div>
    </header>
  );
};