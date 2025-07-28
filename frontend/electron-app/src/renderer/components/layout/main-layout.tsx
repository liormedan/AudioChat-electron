import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './sidebar';

export const MainLayout: React.FC = () => {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 p-4 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
};
