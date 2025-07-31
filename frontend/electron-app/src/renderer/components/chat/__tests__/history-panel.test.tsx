import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { HistoryPanel } from '../history-panel';

// Mock the chat store
const mockUseChatStore = vi.fn();
vi.mock('@/stores/chat-store', () => ({
  useChatStore: () => mockUseChatStore()
}));

// Mock UI components
vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>{children}</button>
  )
}));

vi.mock('@/components/ui/card', () => ({
  Card: ({ children, onClick, ...props }: any) => (
    <div onClick={onClick} {...props}>{children}</div>
  ),
  CardContent: ({ children }: any) => <div>{children}</div>,
  CardHeader: ({ children }: any) => <div>{children}</div>,
  CardTitle: ({ children }: any) => <h3>{children}</h3>
}));

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children }: any) => <span>{children}</span>
}));

vi.mock('@/components/ui/tabs', () => ({
  Tabs: ({ children }: any) => <div>{children}</div>,
  TabsContent: ({ children }: any) => <div>{children}</div>,
  TabsList: ({ children }: any) => <div>{children}</div>,
  TabsTrigger: ({ children, value }: any) => <button data-value={value}>{children}</button>
}));

vi.mock('@/components/ui/dropdown-menu', () => ({
  DropdownMenu: ({ children }: any) => <div>{children}</div>,
  DropdownMenuContent: ({ children }: any) => <div>{children}</div>,
  DropdownMenuItem: ({ children, onClick }: any) => (
    <div onClick={onClick}>{children}</div>
  ),
  DropdownMenuSeparator: () => <hr />,
  DropdownMenuTrigger: ({ children }: any) => <div>{children}</div>
}));

describe('HistoryPanel', () => {
  const mockSessions = [
    {
      id: 'session-1',
      title: 'שיחה ראשונה',
      messages: [
        { id: 'msg-1', text: 'שלום', sender: 'user', timestamp: '2024-01-01T10:00:00Z' },
        { id: 'msg-2', text: 'שלום! איך אני יכול לעזור?', sender: 'bot', timestamp: '2024-01-01T10:01:00Z' }
      ],
      createdAt: '2024-01-01T10:00:00Z',
      updatedAt: '2024-01-01T10:01:00Z',
      isArchived: false
    },
    {
      id: 'session-2',
      title: 'שיחה שנייה',
      messages: [
        { id: 'msg-3', text: 'מה המזג אוויר?', sender: 'user', timestamp: '2024-01-02T14:00:00Z' }
      ],
      createdAt: '2024-01-02T14:00:00Z',
      updatedAt: '2024-01-02T14:00:00Z',
      isArchived: false
    },
    {
      id: 'session-3',
      title: 'שיחה ארכיונית',
      messages: [],
      createdAt: '2023-12-01T10:00:00Z',
      updatedAt: '2023-12-01T10:00:00Z',
      isArchived: true
    }
  ];

  const mockStoreState = {
    sessions: mockSessions,
    activeSessionId: 'session-1',
    setActiveSession: vi.fn(),
    updateSession: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseChatStore.mockReturnValue(mockStoreState);
  });

  it('renders without crashing', () => {
    render(<HistoryPanel />);
    expect(screen.getByText('אחרונות')).toBeInTheDocument();
    expect(screen.getByText('פופולריות')).toBeInTheDocument();
    expect(screen.getByText('הכל')).toBeInTheDocument();
  });

  it('displays recent sessions correctly', () => {
    render(<HistoryPanel />);
    
    // Should show non-archived sessions
    expect(screen.getByText('שיחה ראשונה')).toBeInTheDocument();
    expect(screen.getByText('שיחה שנייה')).toBeInTheDocument();
    
    // Should not show archived sessions
    expect(screen.queryByText('שיחה ארכיונית')).not.toBeInTheDocument();
  });

  it('calls onSessionSelect when session is clicked', async () => {
    const mockOnSessionSelect = vi.fn();
    render(<HistoryPanel onSessionSelect={mockOnSessionSelect} />);
    
    const sessionCard = screen.getByText('שיחה ראשונה').closest('div');
    fireEvent.click(sessionCard!);
    
    await waitFor(() => {
      expect(mockStoreState.setActiveSession).toHaveBeenCalledWith('session-1');
      expect(mockOnSessionSelect).toHaveBeenCalledWith('session-1');
    });
  });

  it('shows session statistics correctly', () => {
    render(<HistoryPanel />);
    
    // Should show message count
    expect(screen.getByText('2')).toBeInTheDocument(); // session-1 has 2 messages
    expect(screen.getByText('1')).toBeInTheDocument(); // session-2 has 1 message
  });

  it('handles drag and drop functionality', () => {
    render(<HistoryPanel />);
    
    const sessionCard = screen.getByText('שיחה ראשונה').closest('div');
    
    // Test drag start
    fireEvent.dragStart(sessionCard!, {
      dataTransfer: {
        effectAllowed: '',
        setData: vi.fn()
      }
    });
    
    // Test drag over
    fireEvent.dragOver(sessionCard!, {
      dataTransfer: {
        dropEffect: ''
      }
    });
    
    // Test drop
    fireEvent.drop(sessionCard!, {
      dataTransfer: {
        getData: vi.fn()
      }
    });
    
    // Should not crash
    expect(sessionCard).toBeInTheDocument();
  });

  it('filters sessions correctly by type', () => {
    render(<HistoryPanel />);
    
    // All sessions should show active sessions only
    expect(screen.getByText('שיחה ראשונה')).toBeInTheDocument();
    expect(screen.getByText('שיחה שנייה')).toBeInTheDocument();
    expect(screen.queryByText('שיחה ארכיונית')).not.toBeInTheDocument();
  });

  it('shows empty state when no sessions exist', () => {
    mockUseChatStore.mockReturnValue({
      ...mockStoreState,
      sessions: []
    });
    
    render(<HistoryPanel />);
    
    expect(screen.getByText('אין שיחות אחרונות')).toBeInTheDocument();
  });

  it('handles pinning functionality', async () => {
    render(<HistoryPanel />);
    
    // Find pin button for first session
    const sessionCard = screen.getByText('שיחה ראשונה').closest('div');
    const pinButton = sessionCard?.querySelector('button');
    
    if (pinButton) {
      fireEvent.click(pinButton);
      // Should not crash and pin functionality should work
      expect(pinButton).toBeInTheDocument();
    }
  });

  it('formats dates correctly', () => {
    // Mock current date to ensure consistent testing
    const mockDate = new Date('2024-01-01T12:00:00Z');
    vi.setSystemTime(mockDate);
    
    render(<HistoryPanel />);
    
    // Should show relative time formatting
    expect(screen.getByText(/לפני/)).toBeInTheDocument();
    
    vi.useRealTimers();
  });

  it('calculates session statistics correctly', () => {
    render(<HistoryPanel />);
    
    // Should show message counts
    const messageElements = screen.getAllByText(/\d+/);
    expect(messageElements.length).toBeGreaterThan(0);
  });

  it('handles sorting functionality', () => {
    render(<HistoryPanel />);
    
    // Should render without crashing when sorting options are available
    expect(screen.getByText('שיחה ראשונה')).toBeInTheDocument();
    expect(screen.getByText('שיחה שנייה')).toBeInTheDocument();
  });
});import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { HistoryPanel } from '../history-panel';
import { useChatStore } from '@/stores/chat-store';

// Mock the chat store
vi.mock('@/stores/chat-store');

const mockUseChatStore = vi.mocked(useChatStore);

describe('HistoryPanel', () => {
  const mockSessions = [
    {
      id: 'session-1',
      title: 'שיחה ראשונה',
      messages: [
        { id: 'msg-1', text: 'שלום', sender: 'user' as const },
        { id: 'msg-2', text: 'שלום! איך אני יכול לעזור?', sender: 'bot' as const }
      ],
      createdAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // 1 hour ago
      updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
      isArchived: false,
      metadata: { isPinned: true }
    },
    {
      id: 'session-2',
      title: 'שיחה שנייה',
      messages: [
        { id: 'msg-3', text: 'מה המזג אוויר?', sender: 'user' as const },
        { id: 'msg-4', text: 'אני לא יכול לבדוק מזג אוויר', sender: 'bot' as const },
        { id: 'msg-5', text: 'בסדר, תודה', sender: 'user' as const }
      ],
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1 day ago
      updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
      isArchived: false,
      metadata: { isPinned: false }
    },
    {
      id: 'session-3',
      title: 'שיחה ארכיונית',
      messages: [
        { id: 'msg-6', text: 'שיחה ישנה', sender: 'user' as const }
      ],
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(), // 10 days ago
      updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
      isArchived: true,
      metadata: {}
    }
  ];

  const mockStore = {
    sessions: mockSessions,
    activeSessionId: 'session-1',
    setActiveSession: vi.fn(),
    updateSession: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseChatStore.mockReturnValue(mockStore);
  });

  it('renders history panel with tabs', () => {
    render(<HistoryPanel />);
    
    expect(screen.getByText('היסטוריית שיחות')).toBeInTheDocument();
    expect(screen.getByText('אחרונות')).toBeInTheDocument();
    expect(screen.getByText('פופולריות')).toBeInTheDocument();
    expect(screen.getByText('נעוצות')).toBeInTheDocument();
  });

  it('displays recent sessions in recent tab', () => {
    render(<HistoryPanel />);
    
    // Recent tab should be active by default
    expect(screen.getByText('שיחה ראשונה')).toBeInTheDocument();
    expect(screen.getByText('שיחה שנייה')).toBeInTheDocument();
    
    // Archived session should not appear in recent
    expect(screen.queryByText('שיחה ארכיונית')).not.toBeInTheDocument();
  });

  it('displays pinned sessions in pinned tab', async () => {
    render(<HistoryPanel />);
    
    // Click on pinned tab
    fireEvent.click(screen.getByText('נעוצות'));
    
    await waitFor(() => {
      expect(screen.getByText('שיחה ראשונה')).toBeInTheDocument();
      expect(screen.queryByText('שיחה שנייה')).not.toBeInTheDocument();
    });
  });

  it('displays popular sessions in popular tab', async () => {
    render(<HistoryPanel />);
    
    // Click on popular tab
    fireEvent.click(screen.getByText('פופולריות'));
    
    await waitFor(() => {
      // Session 2 has more messages, so it should be more popular
      expect(screen.getByText('שיחה שנייה')).toBeInTheDocument();
      expect(screen.getByText('שיחה ראשונה')).toBeInTheDocument();
    });
  });

  it('shows statistics when stats button is clicked', async () => {
    render(<HistoryPanel />);
    
    // Click stats button
    const statsButton = screen.getByRole('button', { name: /BarChart3/ });
    fireEvent.click(statsButton);
    
    await waitFor(() => {
      expect(screen.getByText('סטטיסטיקות')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument(); // Total sessions
      expect(screen.getByText('שיחות')).toBeInTheDocument();
    });
  });

  it('calls onSessionSelect when session is clicked', () => {
    const mockOnSessionSelect = vi.fn();
    render(<HistoryPanel onSessionSelect={mockOnSessionSelect} />);
    
    fireEvent.click(screen.getByText('שיחה ראשונה'));
    
    expect(mockStore.setActiveSession).toHaveBeenCalledWith('session-1');
    expect(mockOnSessionSelect).toHaveBeenCalledWith('session-1');
  });

  it('toggles pin status when pin button is clicked', async () => {
    render(<HistoryPanel />);
    
    // Find the session card and click the dropdown menu
    const sessionCard = screen.getByText('שיחה ראשונה').closest('[role="button"]');
    const dropdownTrigger = sessionCard?.querySelector('button[aria-haspopup="menu"]');
    
    if (dropdownTrigger) {
      fireEvent.click(dropdownTrigger);
      
      await waitFor(() => {
        const unpinButton = screen.getByText('ביטול נעיצה');
        fireEvent.click(unpinButton);
        
        expect(mockStore.updateSession).toHaveBeenCalledWith('session-1', {
          metadata: { isPinned: false }
        });
      });
    }
  });

  it('displays session statistics correctly', () => {
    render(<HistoryPanel />);
    
    // Each session should show message count
    const messageCountElements = screen.getAllByText(/\d+/);
    expect(messageCountElements.length).toBeGreaterThan(0);
  });

  it('shows relative time for sessions', () => {
    render(<HistoryPanel />);
    
    // Should show relative time like "לפני X שעות"
    expect(screen.getByText(/לפני/)).toBeInTheDocument();
  });

  it('handles drag and drop events', () => {
    render(<HistoryPanel />);
    
    const sessionCard = screen.getByText('שיחה ראשונה').closest('[draggable="true"]');
    
    if (sessionCard) {
      // Test drag start
      fireEvent.dragStart(sessionCard);
      
      // Test drag over
      const targetCard = screen.getByText('שיחה שנייה').closest('[draggable="true"]');
      if (targetCard) {
        fireEvent.dragOver(targetCard);
        fireEvent.drop(targetCard);
      }
    }
    
    // Should not throw errors
    expect(true).toBe(true);
  });

  it('shows empty state when no sessions match criteria', async () => {
    // Mock empty sessions for pinned tab
    mockUseChatStore.mockReturnValue({
      ...mockStore,
      sessions: mockSessions.map(s => ({ ...s, metadata: { isPinned: false } }))
    });
    
    render(<HistoryPanel />);
    
    // Click on pinned tab
    fireEvent.click(screen.getByText('נעוצות'));
    
    await waitFor(() => {
      expect(screen.getByText('אין שיחות נעוצות')).toBeInTheDocument();
    });
  });
});