
import { useChatStore } from '@/stores/chat-store';

describe('useChatStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useChatStore.setState({
      sessions: [],
      activeSessionId: null,
      isBotTyping: false
    });
  });

  it('should create a new session', () => {
    const { createSession, sessions } = useChatStore.getState();
    expect(sessions.length).toBe(0);
    
    const sessionId = createSession('Test Session');
    const { sessions: newSessions, activeSessionId } = useChatStore.getState();
    
    expect(newSessions.length).toBe(1);
    expect(newSessions[0].title).toBe('Test Session');
    expect(newSessions[0].id).toBe(sessionId);
    expect(newSessions[0].isArchived).toBe(false);
    expect(newSessions[0].createdAt).toBeDefined();
    expect(newSessions[0].updatedAt).toBeDefined();
    expect(activeSessionId).toBe(sessionId);
  });

  it('should add a message to a session', () => {
    const { createSession, addMessage } = useChatStore.getState();
    const sessionId = createSession('Test Session');
    
    addMessage(sessionId, { 
      id: '1', 
      text: 'Hello', 
      sender: 'user',
      timestamp: new Date().toISOString()
    });
    
    const { sessions } = useChatStore.getState();
    expect(sessions[0].messages.length).toBe(1);
    expect(sessions[0].messages[0].text).toBe('Hello');
    expect(sessions[0].updatedAt).toBeDefined();
  });

  it('should set active session', () => {
    const { createSession, setActiveSession } = useChatStore.getState();
    const sessionId = createSession('Test Session');
    
    setActiveSession(sessionId);
    const { activeSessionId } = useChatStore.getState();
    
    expect(activeSessionId).toBe(sessionId);
  });

  it('should update session', () => {
    const { createSession, updateSession } = useChatStore.getState();
    const sessionId = createSession('Test Session');
    
    updateSession(sessionId, { title: 'Updated Title' });
    const { sessions } = useChatStore.getState();
    
    expect(sessions[0].title).toBe('Updated Title');
    expect(sessions[0].updatedAt).toBeDefined();
  });

  it('should delete session', () => {
    const { createSession, deleteSession } = useChatStore.getState();
    const sessionId = createSession('Test Session');
    
    deleteSession(sessionId);
    const { sessions, activeSessionId } = useChatStore.getState();
    
    expect(sessions.length).toBe(0);
    expect(activeSessionId).toBe(null);
  });

  it('should archive and unarchive session', () => {
    const { createSession, archiveSession } = useChatStore.getState();
    const sessionId = createSession('Test Session');
    
    // Archive session
    archiveSession(sessionId);
    let { sessions } = useChatStore.getState();
    expect(sessions[0].isArchived).toBe(true);
    
    // Unarchive session
    archiveSession(sessionId);
    ({ sessions } = useChatStore.getState());
    expect(sessions[0].isArchived).toBe(false);
  });

  it('should search sessions by title', () => {
    const { createSession, searchSessions } = useChatStore.getState();
    createSession('JavaScript Tutorial');
    createSession('Python Guide');
    createSession('React Components');
    
    const results = searchSessions('script');
    expect(results.length).toBe(1);
    expect(results[0].title).toBe('JavaScript Tutorial');
  });

  it('should search sessions by message content', () => {
    const { createSession, addMessage, searchSessions } = useChatStore.getState();
    const sessionId = createSession('Test Session');
    
    addMessage(sessionId, {
      id: '1',
      text: 'How to use React hooks?',
      sender: 'user',
      timestamp: new Date().toISOString()
    });
    
    const results = searchSessions('hooks');
    expect(results.length).toBe(1);
    expect(results[0].id).toBe(sessionId);
  });

  it('should set bot typing status', () => {
    const { setIsBotTyping } = useChatStore.getState();
    
    setIsBotTyping(true);
    let { isBotTyping } = useChatStore.getState();
    expect(isBotTyping).toBe(true);
    
    setIsBotTyping(false);
    ({ isBotTyping } = useChatStore.getState());
    expect(isBotTyping).toBe(false);
  });

  it('should handle deleting active session', () => {
    const { createSession, deleteSession } = useChatStore.getState();
    const sessionId1 = createSession('Session 1');
    // sessionId1 is now active
    
    deleteSession(sessionId1);
    
    const { sessions, activeSessionId } = useChatStore.getState();
    expect(sessions.length).toBe(0);
    expect(activeSessionId).toBe(null);
  });


});
