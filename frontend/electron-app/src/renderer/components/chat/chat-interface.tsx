import React, { useRef, useEffect } from 'react';
import { SessionSidebar } from './session-sidebar';
import { MessageList } from './message-list';
import { InputArea } from './input-area';

export const ChatInterface: React.FC = () => {
  const messageEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom of the message list
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  });

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Session Sidebar - visible on medium and larger screens */}
      <div className="hidden md:flex">
        <SessionSidebar />
      </div>
      
      {/* Main Chat Area */}
      <div className="flex flex-col flex-grow w-full md:w-auto">
        <MessageList />
        <div ref={messageEndRef} />
        <InputArea />
      </div>
    </div>
  );
};