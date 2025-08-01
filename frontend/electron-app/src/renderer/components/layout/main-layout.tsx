import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './sidebar';
import { Header } from './header';
import { useLanguage } from '../../contexts/language-context';

export const MainLayout: React.FC = () => {
  const { direction } = useLanguage();

  return (
    <div className={`flex h-screen ${direction === 'rtl' ? 'flex-row-reverse' : ''}`}>
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 p-4 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
