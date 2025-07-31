import { create } from 'zustand';

// Define the types for our state
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp?: string;
}

interface Session {
  id: string;
  title: string;
  messages: Message[];
  createdAt?: string;
  updatedAt?: string;
  isArchived?: boolean;
  metadata?: Record<string, any>;
}

interface ChatState {
  sessions: Session[];
  activeSessionId: string | null;
  isBotTyping: boolean; // New state for typing indicator
  addMessage: (sessionId: string, message: Message) => void;
  createSession: (title: string) => string; // Return session ID
  setActiveSession: (sessionId: string) => void;
  setIsBotTyping: (isTyping: boolean) => void; // New action for typing indicator
  updateSession: (sessionId: string, updates: Partial<Session>) => void;
  deleteSession: (sessionId: string) => void;
  archiveSession: (sessionId: string) => void;
  searchSessions: (query: string) => Session[];
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  isBotTyping: false, // Initialize to false

  // Action to add a message to a session
  addMessage: (sessionId, message) =>
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === sessionId
          ? { 
              ...session, 
              messages: [...session.messages, message],
              updatedAt: new Date().toISOString()
            }
          : session
      ),
    })),

  // Action to create a new session
  createSession: (title) => {
    const sessionId = `session-${Date.now()}`;
    const now = new Date().toISOString();
    
    set((state) => {
      const newSession: Session = {
        id: sessionId,
        title,
        messages: [],
        createdAt: now,
        updatedAt: now,
        isArchived: false,
        metadata: {}
      };
      return { 
        sessions: [...state.sessions, newSession],
        activeSessionId: sessionId
      };
    });
    
    return sessionId;
  },

  // Action to set the active session
  setActiveSession: (sessionId) => set({ activeSessionId: sessionId }),

  // New action to set bot typing status
  setIsBotTyping: (isTyping: boolean) => set({ isBotTyping: isTyping }),

  // Action to update a session
  updateSession: (sessionId, updates) =>
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === sessionId
          ? { 
              ...session, 
              ...updates,
              updatedAt: new Date().toISOString()
            }
          : session
      ),
    })),

  // Action to delete a session
  deleteSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((session) => session.id !== sessionId),
      activeSessionId: state.activeSessionId === sessionId ? null : state.activeSessionId
    })),

  // Action to archive/unarchive a session
  archiveSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === sessionId
          ? { 
              ...session, 
              isArchived: !session.isArchived,
              updatedAt: new Date().toISOString()
            }
          : session
      ),
    })),

  // Action to search sessions
  searchSessions: (query) => {
    const state = get();
    const lowerQuery = query.toLowerCase();
    
    return state.sessions.filter((session) =>
      session.title.toLowerCase().includes(lowerQuery) ||
      session.messages.some((message) =>
        message.text.toLowerCase().includes(lowerQuery)
      )
    );
  },
}));