import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { persist } from 'zustand/middleware/persist';
import { Message, ChatSession } from '@/types/chat';

// Performance-optimized selectors
export interface ChatSelectors {
  // Message selectors
  getMessagesBySession: (sessionId: string) => Message[];
  getRecentMessages: (limit?: number) => Message[];
  getMessageById: (messageId: string) => Message | undefined;
  getMessagesCount: () => number;
  getMessagesByDateRange: (startDate: Date, endDate: Date) => Message[];
  
  // Session selectors
  getActiveSession: () => ChatSession | undefined;
  getSessionById: (sessionId: string) => ChatSession | undefined;
  getRecentSessions: (limit?: number) => ChatSession[];
  getSessionsCount: () => number;
  
  // Search selectors
  searchMessages: (query: string, sessionId?: string) => Message[];
  getMessagesByRole: (role: string, sessionId?: string) => Message[];
  
  // Performance selectors
  getLoadingStates: () => Record<string, boolean>;
  getErrorStates: () => Record<string, string | null>;
}

interface ChatState {
  // Core data
  messages: Record<string, Message>; // Normalized by message ID
  sessions: Record<string, ChatSession>; // Normalized by session ID
  messagesBySession: Record<string, string[]>; // Session ID -> Message IDs
  
  // UI state
  activeSessionId: string | null;
  selectedMessageId: string | null;
  
  // Loading states
  loading: {
    messages: boolean;
    sessions: boolean;
    sending: boolean;
  };
  
  // Error states
  errors: {
    messages: string | null;
    sessions: string | null;
    sending: string | null;
  };
  
  // Performance optimization
  lastUpdated: number;
  messageCache: Map<string, Message[]>;
  searchCache: Map<string, Message[]>;
}

interface ChatActions {
  // Message actions
  addMessage: (message: Message) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  deleteMessage: (messageId: string) => void;
  setMessages: (messages: Message[]) => void;
  clearMessages: (sessionId?: string) => void;
  
  // Session actions
  addSession: (session: ChatSession) => void;
  updateSession: (sessionId: string, updates: Partial<ChatSession>) => void;
  deleteSession: (sessionId: string) => void;
  setSessions: (sessions: ChatSession[]) => void;
  setActiveSession: (sessionId: string | null) => void;
  
  // UI actions
  setSelectedMessage: (messageId: string | null) => void;
  
  // Loading actions
  setLoading: (key: keyof ChatState['loading'], value: boolean) => void;
  setError: (key: keyof ChatState['errors'], value: string | null) => void;
  
  // Cache management
  clearCache: () => void;
  invalidateCache: (type?: 'messages' | 'search') => void;
}

type ChatStore = ChatState & ChatActions & ChatSelectors;

// Create memoized selectors
const createSelectors = (state: ChatState): ChatSelectors => {
  // Cache for expensive computations
  const messageCache = state.messageCache;
  const searchCache = state.searchCache;
  
  return {
    getMessagesBySession: (sessionId: string) => {
      const cacheKey = `session_${sessionId}`;
      if (messageCache.has(cacheKey)) {
        return messageCache.get(cacheKey)!;
      }
      
      const messageIds = state.messagesBySession[sessionId] || [];
      const messages = messageIds
        .map(id => state.messages[id])
        .filter(Boolean)
        .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      
      messageCache.set(cacheKey, messages);
      return messages;
    },
    
    getRecentMessages: (limit = 50) => {
      const cacheKey = `recent_${limit}`;
      if (messageCache.has(cacheKey)) {
        return messageCache.get(cacheKey)!;
      }
      
      const messages = Object.values(state.messages)
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, limit);
      
      messageCache.set(cacheKey, messages);
      return messages;
    },
    
    getMessageById: (messageId: string) => {
      return state.messages[messageId];
    },
    
    getMessagesCount: () => {
      return Object.keys(state.messages).length;
    },
    
    getMessagesByDateRange: (startDate: Date, endDate: Date) => {
      const cacheKey = `date_${startDate.getTime()}_${endDate.getTime()}`;
      if (messageCache.has(cacheKey)) {
        return messageCache.get(cacheKey)!;
      }
      
      const messages = Object.values(state.messages)
        .filter(message => {
          const messageDate = new Date(message.timestamp);
          return messageDate >= startDate && messageDate <= endDate;
        })
        .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      
      messageCache.set(cacheKey, messages);
      return messages;
    },
    
    getActiveSession: () => {
      return state.activeSessionId ? state.sessions[state.activeSessionId] : undefined;
    },
    
    getSessionById: (sessionId: string) => {
      return state.sessions[sessionId];
    },
    
    getRecentSessions: (limit = 20) => {
      return Object.values(state.sessions)
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, limit);
    },
    
    getSessionsCount: () => {
      return Object.keys(state.sessions).length;
    },
    
    searchMessages: (query: string, sessionId?: string) => {
      const cacheKey = `search_${query}_${sessionId || 'all'}`;
      if (searchCache.has(cacheKey)) {
        return searchCache.get(cacheKey)!;
      }
      
      const searchLower = query.toLowerCase();
      let messages = Object.values(state.messages);
      
      if (sessionId) {
        const sessionMessageIds = state.messagesBySession[sessionId] || [];
        messages = sessionMessageIds.map(id => state.messages[id]).filter(Boolean);
      }
      
      const results = messages
        .filter(message => 
          message.content.toLowerCase().includes(searchLower)
        )
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      
      searchCache.set(cacheKey, results);
      return results;
    },
    
    getMessagesByRole: (role: string, sessionId?: string) => {
      const cacheKey = `role_${role}_${sessionId || 'all'}`;
      if (messageCache.has(cacheKey)) {
        return messageCache.get(cacheKey)!;
      }
      
      let messages = Object.values(state.messages);
      
      if (sessionId) {
        const sessionMessageIds = state.messagesBySession[sessionId] || [];
        messages = sessionMessageIds.map(id => state.messages[id]).filter(Boolean);
      }
      
      const results = messages
        .filter(message => message.role === role)
        .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      
      messageCache.set(cacheKey, results);
      return results;
    },
    
    getLoadingStates: () => state.loading,
    getErrorStates: () => state.errors,
  };
};

// Create the store with performance optimizations
export const useOptimizedChatStore = create<ChatStore>()(
  subscribeWithSelector(
    persist(
      immer((set, get) => ({
        // Initial state
        messages: {},
        sessions: {},
        messagesBySession: {},
        activeSessionId: null,
        selectedMessageId: null,
        loading: {
          messages: false,
          sessions: false,
          sending: false,
        },
        errors: {
          messages: null,
          sessions: null,
          sending: null,
        },
        lastUpdated: Date.now(),
        messageCache: new Map(),
        searchCache: new Map(),
        
        // Selectors (computed on each get)
        ...createSelectors(get()),
        
        // Actions
        addMessage: (message: Message) =>
          set((state) => {
            state.messages[message.id] = message;
            
            if (!state.messagesBySession[message.session_id]) {
              state.messagesBySession[message.session_id] = [];
            }
            
            if (!state.messagesBySession[message.session_id].includes(message.id)) {
              state.messagesBySession[message.session_id].push(message.id);
            }
            
            state.lastUpdated = Date.now();
            state.messageCache.clear();
            state.searchCache.clear();
          }),
        
        updateMessage: (messageId: string, updates: Partial<Message>) =>
          set((state) => {
            if (state.messages[messageId]) {
              Object.assign(state.messages[messageId], updates);
              state.lastUpdated = Date.now();
              state.messageCache.clear();
              state.searchCache.clear();
            }
          }),
        
        deleteMessage: (messageId: string) =>
          set((state) => {
            const message = state.messages[messageId];
            if (message) {
              delete state.messages[messageId];
              
              const sessionMessages = state.messagesBySession[message.session_id];
              if (sessionMessages) {
                const index = sessionMessages.indexOf(messageId);
                if (index > -1) {
                  sessionMessages.splice(index, 1);
                }
              }
              
              if (state.selectedMessageId === messageId) {
                state.selectedMessageId = null;
              }
              
              state.lastUpdated = Date.now();
              state.messageCache.clear();
              state.searchCache.clear();
            }
          }),
        
        setMessages: (messages: Message[]) =>
          set((state) => {
            state.messages = {};
            state.messagesBySession = {};
            
            messages.forEach((message) => {
              state.messages[message.id] = message;
              
              if (!state.messagesBySession[message.session_id]) {
                state.messagesBySession[message.session_id] = [];
              }
              
              state.messagesBySession[message.session_id].push(message.id);
            });
            
            state.lastUpdated = Date.now();
            state.messageCache.clear();
            state.searchCache.clear();
          }),
        
        clearMessages: (sessionId?: string) =>
          set((state) => {
            if (sessionId) {
              const messageIds = state.messagesBySession[sessionId] || [];
              messageIds.forEach((id) => {
                delete state.messages[id];
              });
              delete state.messagesBySession[sessionId];
            } else {
              state.messages = {};
              state.messagesBySession = {};
            }
            
            state.lastUpdated = Date.now();
            state.messageCache.clear();
            state.searchCache.clear();
          }),
        
        addSession: (session: ChatSession) =>
          set((state) => {
            state.sessions[session.id] = session;
            state.lastUpdated = Date.now();
          }),
        
        updateSession: (sessionId: string, updates: Partial<ChatSession>) =>
          set((state) => {
            if (state.sessions[sessionId]) {
              Object.assign(state.sessions[sessionId], updates);
              state.lastUpdated = Date.now();
            }
          }),
        
        deleteSession: (sessionId: string) =>
          set((state) => {
            delete state.sessions[sessionId];
            
            // Clear messages for this session
            const messageIds = state.messagesBySession[sessionId] || [];
            messageIds.forEach((id) => {
              delete state.messages[id];
            });
            delete state.messagesBySession[sessionId];
            
            if (state.activeSessionId === sessionId) {
              state.activeSessionId = null;
            }
            
            state.lastUpdated = Date.now();
            state.messageCache.clear();
            state.searchCache.clear();
          }),
        
        setSessions: (sessions: ChatSession[]) =>
          set((state) => {
            state.sessions = {};
            sessions.forEach((session) => {
              state.sessions[session.id] = session;
            });
            state.lastUpdated = Date.now();
          }),
        
        setActiveSession: (sessionId: string | null) =>
          set((state) => {
            state.activeSessionId = sessionId;
          }),
        
        setSelectedMessage: (messageId: string | null) =>
          set((state) => {
            state.selectedMessageId = messageId;
          }),
        
        setLoading: (key: keyof ChatState['loading'], value: boolean) =>
          set((state) => {
            state.loading[key] = value;
          }),
        
        setError: (key: keyof ChatState['errors'], value: string | null) =>
          set((state) => {
            state.errors[key] = value;
          }),
        
        clearCache: () =>
          set((state) => {
            state.messageCache.clear();
            state.searchCache.clear();
          }),
        
        invalidateCache: (type?: 'messages' | 'search') =>
          set((state) => {
            if (!type || type === 'messages') {
              state.messageCache.clear();
            }
            if (!type || type === 'search') {
              state.searchCache.clear();
            }
          }),
      })),
      {
        name: 'optimized-chat-store',
        partialize: (state) => ({
          messages: state.messages,
          sessions: state.sessions,
          messagesBySession: state.messagesBySession,
          activeSessionId: state.activeSessionId,
        }),
        onRehydrateStorage: () => (state) => {
          if (state) {
            // Reinitialize non-serializable data
            state.messageCache = new Map();
            state.searchCache = new Map();
            state.lastUpdated = Date.now();
          }
        },
      }
    )
  )
);

// Performance monitoring hook
export const useChatStorePerformance = () => {
  const messagesCount = useOptimizedChatStore((state) => state.getMessagesCount());
  const sessionsCount = useOptimizedChatStore((state) => state.getSessionsCount());
  const lastUpdated = useOptimizedChatStore((state) => state.lastUpdated);
  const cacheSize = useOptimizedChatStore((state) => ({
    messages: state.messageCache.size,
    search: state.searchCache.size,
  }));

  return {
    messagesCount,
    sessionsCount,
    lastUpdated,
    cacheSize,
    memoryUsage: {
      messages: messagesCount * 0.5, // Rough estimate in KB
      sessions: sessionsCount * 0.2,
      cache: (cacheSize.messages + cacheSize.search) * 0.1,
    },
  };
};

// Selector hooks for better performance
export const useMessages = (sessionId?: string) => {
  return useOptimizedChatStore((state) => 
    sessionId ? state.getMessagesBySession(sessionId) : state.getRecentMessages()
  );
};

export const useSessions = (limit?: number) => {
  return useOptimizedChatStore((state) => state.getRecentSessions(limit));
};

export const useActiveSession = () => {
  return useOptimizedChatStore((state) => state.getActiveSession());
};

export const useSearchMessages = (query: string, sessionId?: string) => {
  return useOptimizedChatStore((state) => 
    query.trim() ? state.searchMessages(query, sessionId) : []
  );
};

// Batch update hook for performance
export const useBatchUpdates = () => {
  const store = useOptimizedChatStore();
  
  return {
    batchAddMessages: (messages: Message[]) => {
      store.setMessages([...Object.values(store.messages), ...messages]);
    },
    
    batchUpdateMessages: (updates: Array<{ id: string; updates: Partial<Message> }>) => {
      updates.forEach(({ id, updates: messageUpdates }) => {
        store.updateMessage(id, messageUpdates);
      });
    },
    
    batchDeleteMessages: (messageIds: string[]) => {
      messageIds.forEach((id) => {
        store.deleteMessage(id);
      });
    },
  };
};