
import React from 'react';
import { SessionManager } from './session-manager';

interface SessionSidebarProps {
  onSessionSelect?: (sessionId: string) => void;
  className?: string;
}

export const SessionSidebar: React.FC<SessionSidebarProps> = ({
  onSessionSelect,
  className = ''
}) => {
  return (
    <div className={`w-64 p-4 border-r bg-background ${className}`}>
      <div className="mb-4">
        <h2 className="text-lg font-semibold">שיחות</h2>
      </div>
      <SessionManager 
        onSessionSelect={onSessionSelect}
        className="h-full"
      />
    </div>
  );
};
