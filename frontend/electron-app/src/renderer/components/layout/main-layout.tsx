import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './sidebar';
import { Header } from './header';

export const MainLayout: React.FC = () => {
  return (
    <div className="flex h-screen">
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
