# Chat Components Documentation

## Overview

This document provides comprehensive documentation for all chat-related React components, including their props, usage examples, and integration patterns.

## Core Components

### ChatInterface

The main chat interface component that orchestrates the entire chat experience.

**Location:** `frontend/electron-app/src/renderer/components/chat/chat-interface.tsx`

#### Props

```typescript
interface ChatInterfaceProps {
  sessionId?: string;                    // Current session ID
  onSessionChange?: (sessionId: string) => void;  // Session change callback
  className?: string;                    // Additional CSS classes
  autoFocus?: boolean;                   // Auto-focus input on mount
  showSidebar?: boolean;                 // Show/hide session sidebar
  streamingEnabled?: boolean;            // Enable streaming responses
}
```

#### Usage

```typescript
import { ChatInterface } from '@/components/chat/chat-interface';

// Basic usage
<ChatInterface />

// With session management
<ChatInterface 
  sessionId="sess_123"
  onSessionChange={(id) => console.log('Session changed:', id)}
  showSidebar={true}
  streamingEnabled={true}
/>

// Custom styling
<ChatInterface 
  className="h-full bg-gray-50"
  autoFocus={true}
/>
```

#### Features

- Real-time message display with streaming support
- Integrated session management
- Keyboard shortcuts (Ctrl+Enter to send)
- Auto-scroll to latest messages
- Message copy functionality
- Responsive design

#### State Management

The component uses the chat store for state management:

```typescript
const {
  messages,
  currentSession,
  isLoading,
  sendMessage,
  createSession
} = useChatStore();
```

### MessageList

Displays chat messages with virtual scrolling for performance.

**Location:** `frontend/electron-app/src/renderer/components/chat/message-list.tsx`

#### Props

```typescript
interface MessageListProps {
  sessionId: string;                     // Session to display messages for
  messages?: Message[];                  // Optional message override
  autoScroll?: boolean;                  // Auto-scroll to bottom
  virtualScrolling?: boolean;            // Enable virtual scrolling
  itemHeight?: number;                   // Height of each message item
  maxHeight?: string;                    // Maximum container height
  onMessageAction?: (messageId: string, action: string) => void;
  className?: string;
}
```

#### Usage

```typescript
import { MessageList } from '@/components/chat/message-list';

// Basic usage
<MessageList sessionId="sess_123" />

// With custom configuration
<MessageList 
  sessionId="sess_123"
  autoScroll={true}
  virtualScrolling={true}
  itemHeight={80}
  maxHeight="600px"
  onMessageAction={(id, action) => {
    if (action === 'copy') {
      // Handle copy action
    }
  }}
/>

// With custom messages
<MessageList 
  sessionId="sess_123"
  messages={customMessages}
  className="border rounded-lg"
/>
```

#### Features

- Virtual scrolling for large conversations
- Markdown rendering with syntax highlighting
- Message actions (copy, delete, edit)
- Typing indicators
- Loading states
- Message timestamps
- User/Assistant message styling

#### Message Actions

```typescript
const handleMessageAction = (messageId: string, action: string) => {
  switch (action) {
    case 'copy':
      navigator.clipboard.writeText(message.content);
      break;
    case 'delete':
      deleteMessage(messageId);
      break;
    case 'edit':
      setEditingMessage(messageId);
      break;
  }
};
```

### InputArea

Message input component with markdown support and keyboard shortcuts.

**Location:** `frontend/electron-app/src/renderer/components/chat/input-area.tsx`

#### Props

```typescript
interface InputAreaProps {
  onSendMessage: (message: string) => void;  // Message send callback
  disabled?: boolean;                        // Disable input
  placeholder?: string;                      // Input placeholder
  maxLength?: number;                        // Maximum message length
  showMarkdownPreview?: boolean;             // Show markdown preview
  autoResize?: boolean;                      // Auto-resize textarea
  shortcuts?: boolean;                       // Enable keyboard shortcuts
  className?: string;
}
```

#### Usage

```typescript
import { InputArea } from '@/components/chat/input-area';

// Basic usage
<InputArea 
  onSendMessage={(message) => sendMessage(message)}
/>

// With full configuration
<InputArea 
  onSendMessage={handleSendMessage}
  disabled={isLoading}
  placeholder="Type your message... (Ctrl+Enter to send)"
  maxLength={4000}
  showMarkdownPreview={true}
  autoResize={true}
  shortcuts={true}
  className="border-t bg-white"
/>
```

#### Features

- Auto-resizing textarea
- Markdown preview
- Character counter
- Keyboard shortcuts:
  - `Ctrl+Enter` - Send message
  - `Shift+Enter` - New line
  - `Ctrl+/` - Toggle markdown preview
- File attachment support (future)
- Emoji picker (future)

#### Keyboard Shortcuts

```typescript
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault();
    handleSendMessage();
  } else if (e.ctrlKey && e.key === '/') {
    e.preventDefault();
    toggleMarkdownPreview();
  }
};
```

### SessionManager

Manages chat sessions with creation, editing, and organization features.

**Location:** `frontend/electron-app/src/renderer/components/chat/session-manager.tsx`

#### Props

```typescript
interface SessionManagerProps {
  currentSessionId?: string;             // Currently active session
  onSessionSelect: (sessionId: string) => void;  // Session selection callback
  onSessionCreate?: (session: ChatSession) => void;  // Session creation callback
  onSessionDelete?: (sessionId: string) => void;     // Session deletion callback
  showArchived?: boolean;                // Show archived sessions
  searchEnabled?: boolean;               // Enable session search
  className?: string;
}
```

#### Usage

```typescript
import { SessionManager } from '@/components/chat/session-manager';

// Basic usage
<SessionManager 
  onSessionSelect={(id) => setCurrentSession(id)}
/>

// Full configuration
<SessionManager 
  currentSessionId={currentSession?.id}
  onSessionSelect={handleSessionSelect}
  onSessionCreate={handleSessionCreate}
  onSessionDelete={handleSessionDelete}
  showArchived={true}
  searchEnabled={true}
  className="w-80 border-r"
/>
```

#### Features

- Session list with search and filtering
- Create new sessions with custom titles
- Edit session titles inline
- Archive/unarchive sessions
- Delete sessions with confirmation
- Drag-and-drop reordering
- Session statistics (message count, last activity)

#### Session Actions

```typescript
const sessionActions = [
  {
    label: 'Rename',
    icon: 'edit',
    action: (sessionId) => startRenaming(sessionId)
  },
  {
    label: 'Archive',
    icon: 'archive',
    action: (sessionId) => archiveSession(sessionId)
  },
  {
    label: 'Delete',
    icon: 'trash',
    action: (sessionId) => deleteSession(sessionId),
    dangerous: true
  }
];
```

### HistoryPanel

Sidebar component for quick access to recent sessions and search.

**Location:** `frontend/electron-app/src/renderer/components/chat/history-panel.tsx`

#### Props

```typescript
interface HistoryPanelProps {
  isOpen: boolean;                       // Panel visibility
  onToggle: () => void;                  // Toggle panel callback
  onSessionSelect: (sessionId: string) => void;  // Session selection
  currentSessionId?: string;             // Currently active session
  maxRecentSessions?: number;            // Number of recent sessions to show
  showSearch?: boolean;                  // Show search functionality
  className?: string;
}
```

#### Usage

```typescript
import { HistoryPanel } from '@/components/chat/history-panel';

<HistoryPanel 
  isOpen={showHistory}
  onToggle={() => setShowHistory(!showHistory)}
  onSessionSelect={handleSessionSelect}
  currentSessionId={currentSession?.id}
  maxRecentSessions={10}
  showSearch={true}
/>
```

#### Features

- Recent sessions quick access
- Session search with highlighting
- Favorite sessions
- Session categories/tags
- Collapsible sections
- Keyboard navigation

### SearchPanel

Advanced search functionality for messages and sessions.

**Location:** `frontend/electron-app/src/renderer/components/chat/search-panel.tsx`

#### Props

```typescript
interface SearchPanelProps {
  isOpen: boolean;                       // Panel visibility
  onClose: () => void;                   // Close panel callback
  onResultSelect: (result: SearchResult) => void;  // Result selection
  searchScope?: 'messages' | 'sessions' | 'all';   // Search scope
  filters?: SearchFilters;               // Search filters
  className?: string;
}

interface SearchFilters {
  dateRange?: { start: Date; end: Date };
  sessionIds?: string[];
  messageTypes?: MessageType[];
  models?: string[];
}
```

#### Usage

```typescript
import { SearchPanel } from '@/components/chat/search-panel';

<SearchPanel 
  isOpen={showSearch}
  onClose={() => setShowSearch(false)}
  onResultSelect={handleResultSelect}
  searchScope="all"
  filters={{
    dateRange: { start: lastWeek, end: now },
    messageTypes: ['text']
  }}
/>
```

#### Features

- Full-text search across messages
- Advanced filters (date, session, model, type)
- Search result highlighting
- Search history
- Saved searches
- Export search results

### SettingsPanel

Configuration panel for chat parameters and preferences.

**Location:** `frontend/electron-app/src/renderer/components/chat/settings-panel.tsx`

#### Props

```typescript
interface SettingsPanelProps {
  isOpen: boolean;                       // Panel visibility
  onClose: () => void;                   // Close panel callback
  currentModel?: LLMModel;               // Currently active model
  onModelChange?: (modelId: string) => void;  // Model change callback
  onParameterChange?: (params: ModelParameters) => void;  // Parameter change
  showAdvanced?: boolean;                // Show advanced settings
  className?: string;
}

interface ModelParameters {
  temperature: number;
  maxTokens: number;
  topP: number;
  topK?: number;
  repetitionPenalty?: number;
}
```

#### Usage

```typescript
import { SettingsPanel } from '@/components/chat/settings-panel';

<SettingsPanel 
  isOpen={showSettings}
  onClose={() => setShowSettings(false)}
  currentModel={activeModel}
  onModelChange={handleModelChange}
  onParameterChange={handleParameterChange}
  showAdvanced={true}
/>
```

#### Features

- Model selection with status indicators
- Parameter sliders with real-time preview
- Preset configurations (Creative, Balanced, Precise, Code)
- Custom parameter profiles
- Import/export settings
- Reset to defaults

#### Parameter Presets

```typescript
const presets = {
  creative: {
    temperature: 0.9,
    maxTokens: 2048,
    topP: 0.95
  },
  balanced: {
    temperature: 0.7,
    maxTokens: 1024,
    topP: 0.9
  },
  precise: {
    temperature: 0.3,
    maxTokens: 512,
    topP: 0.8
  },
  code: {
    temperature: 0.1,
    maxTokens: 2048,
    topP: 0.95
  }
};
```

### PerformanceMonitor

Real-time performance metrics display for chat operations.

**Location:** `frontend/electron-app/src/renderer/components/chat/performance-monitor.tsx`

#### Props

```typescript
interface PerformanceMonitorProps {
  isVisible: boolean;                    // Monitor visibility
  position?: 'top-right' | 'bottom-right' | 'bottom-left';  // Position
  showMetrics?: string[];                // Metrics to display
  updateInterval?: number;               // Update frequency (ms)
  className?: string;
}
```

#### Usage

```typescript
import { PerformanceMonitor } from '@/components/chat/performance-monitor';

<PerformanceMonitor 
  isVisible={showPerformance}
  position="top-right"
  showMetrics={['responseTime', 'tokensPerSecond', 'memoryUsage']}
  updateInterval={1000}
/>
```

#### Features

- Real-time response time tracking
- Token usage statistics
- Memory usage monitoring
- Model performance comparison
- Cost tracking (for cloud models)
- Performance alerts

## Utility Components

### MessageBubble

Individual message display component with actions.

#### Props

```typescript
interface MessageBubbleProps {
  message: Message;                      // Message data
  showActions?: boolean;                 // Show message actions
  onAction?: (messageId: string, action: string) => void;  // Action callback
  className?: string;
}
```

#### Usage

```typescript
<MessageBubble 
  message={message}
  showActions={true}
  onAction={handleMessageAction}
/>
```

### VirtualMessageList

Optimized message list with virtual scrolling.

#### Props

```typescript
interface VirtualMessageListProps {
  messages: Message[];                   // Messages to display
  itemHeight: number;                    // Height of each item
  containerHeight: number;               // Container height
  onScroll?: (scrollTop: number) => void;  // Scroll callback
}
```

### LoadingIndicator

Typing/loading indicator for chat responses.

#### Props

```typescript
interface LoadingIndicatorProps {
  type?: 'typing' | 'thinking' | 'processing';  // Indicator type
  message?: string;                      // Custom loading message
  animated?: boolean;                    // Enable animations
}
```

## Integration Patterns

### Basic Chat Setup

```typescript
import { 
  ChatInterface,
  SessionManager,
  HistoryPanel,
  SettingsPanel 
} from '@/components/chat';

export const ChatApp: React.FC = () => {
  const [currentSession, setCurrentSession] = useState<string>();
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className="flex h-screen">
      <SessionManager 
        currentSessionId={currentSession}
        onSessionSelect={setCurrentSession}
        className="w-80"
      />
      
      <div className="flex-1 flex flex-col">
        <ChatInterface 
          sessionId={currentSession}
          onSessionChange={setCurrentSession}
        />
      </div>

      <HistoryPanel 
        isOpen={showHistory}
        onToggle={() => setShowHistory(!showHistory)}
        onSessionSelect={setCurrentSession}
        currentSessionId={currentSession}
      />

      <SettingsPanel 
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />
    </div>
  );
};
```

### Custom Message Handling

```typescript
const CustomChatInterface: React.FC = () => {
  const { sendMessage, messages } = useChatStore();

  const handleCustomMessage = async (content: string) => {
    // Pre-process message
    const processedContent = preprocessMessage(content);
    
    // Send with custom metadata
    await sendMessage(sessionId, processedContent, {
      source: 'custom-interface',
      timestamp: Date.now()
    });
    
    // Post-process response
    postProcessResponse();
  };

  return (
    <div>
      <MessageList 
        sessionId={sessionId}
        onMessageAction={handleMessageAction}
      />
      <InputArea 
        onSendMessage={handleCustomMessage}
        placeholder="Enter your custom message..."
      />
    </div>
  );
};
```

### Advanced Search Integration

```typescript
const AdvancedChatSearch: React.FC = () => {
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [filters, setFilters] = useState<SearchFilters>({});

  const handleSearch = async (query: string) => {
    const results = await searchMessages(query, filters);
    setSearchResults(results);
  };

  return (
    <SearchPanel 
      isOpen={true}
      onClose={() => {}}
      onResultSelect={(result) => {
        // Navigate to message
        navigateToMessage(result.messageId);
      }}
      filters={filters}
    />
  );
};
```

## Testing Components

### Unit Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from '@/components/chat/chat-interface';

describe('ChatInterface', () => {
  test('renders chat interface correctly', () => {
    render(<ChatInterface />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByText('Send')).toBeInTheDocument();
  });

  test('sends message on button click', async () => {
    const mockSendMessage = jest.fn();
    render(<ChatInterface onSendMessage={mockSendMessage} />);
    
    const input = screen.getByRole('textbox');
    const sendButton = screen.getByText('Send');
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    expect(mockSendMessage).toHaveBeenCalledWith('Test message');
  });
});
```

### Integration Tests

```typescript
import { render, screen } from '@testing-library/react';
import { ChatApp } from '@/components/chat-app';
import { ChatProvider } from '@/providers/chat-provider';

describe('Chat Integration', () => {
  test('full chat flow works correctly', async () => {
    render(
      <ChatProvider>
        <ChatApp />
      </ChatProvider>
    );

    // Test session creation
    const newSessionButton = screen.getByText('New Chat');
    fireEvent.click(newSessionButton);

    // Test message sending
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByText('Send'));

    // Verify message appears
    await screen.findByText('Hello');
  });
});
```

## Performance Considerations

### Virtual Scrolling

For large message lists, use virtual scrolling:

```typescript
import { VirtualMessageList } from '@/components/chat/virtual-message-list';

<VirtualMessageList 
  messages={messages}
  itemHeight={80}
  containerHeight={600}
/>
```

### Memoization

Optimize re-renders with React.memo:

```typescript
export const MessageBubble = React.memo<MessageBubbleProps>(({ 
  message, 
  onAction 
}) => {
  // Component implementation
}, (prevProps, nextProps) => {
  return prevProps.message.id === nextProps.message.id &&
         prevProps.message.content === nextProps.message.content;
});
```

### Debounced Search

Implement debounced search for better performance:

```typescript
import { useDebouncedCallback } from 'use-debounce';

const SearchInput: React.FC = () => {
  const debouncedSearch = useDebouncedCallback(
    (query: string) => {
      performSearch(query);
    },
    300
  );

  return (
    <input 
      onChange={(e) => debouncedSearch(e.target.value)}
      placeholder="Search messages..."
    />
  );
};
```

## Accessibility

All components follow WCAG 2.1 guidelines:

- Proper ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management

```typescript
<button
  aria-label="Send message"
  aria-describedby="send-button-help"
  onKeyDown={handleKeyDown}
>
  Send
</button>
<div id="send-button-help" className="sr-only">
  Press Ctrl+Enter to send message quickly
</div>
```