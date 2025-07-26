import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './sidebar';
import { useUIStore } from '../../stores/ui-store';
import { cn } from '../../lib/utils';

export const MainLayout: React.FC = () => {
  const { sidebarCollapsed } = useUIStore();

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content Area */}
      <main 
        className={cn(
          "flex-1 flex flex-col transition-all duration-300 ease-in-out",
          sidebarCollapsed ? "ml-16" : "ml-64"
        )}
      >
        {/* Content */}
        <div className="flex-1 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
};