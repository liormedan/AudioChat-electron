import React from 'react';
import { useUIStore } from '../../stores';
import { Button } from '../ui/button';
import { Moon, Sun } from 'lucide-react';

export const Header: React.FC = () => {
  const { theme, setTheme } = useUIStore();

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
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
      </div>
    </header>
  );
};