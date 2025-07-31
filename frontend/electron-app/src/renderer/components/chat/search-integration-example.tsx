import React, { useState } from 'react';
import { SearchPanel } from './search-panel';
import { MessageList } from './message-list';
import { useChatStore } from '@/stores/chat-store';
import { Button } from '@/components/ui/button';
import { Search, X } from 'lucide-react';

/**
 * Example component showing how to integrate SearchPanel with the chat interface
 * This demonstrates how to handle search result selection and navigation
 */
export const SearchIntegrationExample: React.FC = () => {
  const { sessions, setActiveSession } = useChatStore();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [highlightedMessageId, setHighlightedMessageId] = useState<string | null>(null);

  // Handle search result selection
  const handleSearchResultSelect = (sessionId: string, messageId: string) => {
    // Switch to the session containing the result
    setActiveSession(sessionId);
    
    // Highlight the specific message
    setHighlightedMessageId(messageId);
    
    // Close search panel
    setIsSearchOpen(false);
    
    // Scroll to the message (in a real implementation, you'd pass this to MessageList)
    setTimeout(() => {
      const messageElement = document.getElementById(`message-${messageId}`);
      if (messageElement) {
        messageElement.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
        
        // Clear highlight after a few seconds
        setTimeout(() => {
          setHighlightedMessageId(null);
        }, 3000);
      }
    }, 100);
  };

  return (
    <div className="flex h-full">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header with search toggle */}
        <div className="flex items-center justify-between p-4 border-b">
          <h1 className="text-lg font-semibold">Chat Interface</h1>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsSearchOpen(!isSearchOpen)}
            className="flex items-center gap-2"
          >
            {isSearchOpen ? (
              <>
                <X className="h-4 w-4" />
                סגור חיפוש
              </>
            ) : (
              <>
                <Search className="h-4 w-4" />
                חיפוש
              </>
            )}
          </Button>
        </div>

        {/* Message list area */}
        <div className="flex-1 overflow-hidden">
          <MessageList 
            highlightedMessageId={highlightedMessageId}
            onMessageHighlightClear={() => setHighlightedMessageId(null)}
          />
        </div>
      </div>

      {/* Search panel sidebar */}
      {isSearchOpen && (
        <div className="w-96 border-l bg-background">
          <div className="h-full overflow-hidden">
            <SearchPanel
              onResultSelect={handleSearchResultSelect}
              className="h-full"
            />
          </div>
        </div>
      )}
    </div>
  );
};

// Example of how to extend MessageList to support highlighting
interface ExtendedMessageListProps {
  highlightedMessageId?: string | null;
  onMessageHighlightClear?: () => void;
}

const MessageListWithHighlight: React.FC<ExtendedMessageListProps> = ({
  highlightedMessageId,
  onMessageHighlightClear
}) => {
  const { sessions, activeSessionId } = useChatStore();
  
  const activeSession = sessions.find(s => s.id === activeSessionId);
  
  if (!activeSession) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        בחר שיחה להצגת הודעות
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full p-4 space-y-4 overflow-y-auto">
      {activeSession.messages.map((message) => (
        <div
          key={message.id}
          id={`message-${message.id}`}
          className={`p-3 rounded-lg max-w-[80%] transition-all duration-300 ${
            message.sender === 'user'
              ? 'bg-primary text-primary-foreground ml-auto'
              : 'bg-muted'
          } ${
            highlightedMessageId === message.id
              ? 'ring-2 ring-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
              : ''
          }`}
        >
          <div className="text-sm">{message.text}</div>
          <div className="text-xs opacity-70 mt-1">
            {new Date(message.timestamp || '').toLocaleTimeString('he-IL')}
          </div>
        </div>
      ))}
    </div>
  );
};