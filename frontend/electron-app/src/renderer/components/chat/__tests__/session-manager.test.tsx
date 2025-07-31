import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { SessionManager } from '../session-manager';
import { useChatStore } from '@/stores/chat-store';

// Mock the chat store
vi.mock('@/stores/chat-store', () => ({
  useChatStore: vi.fn()
}));

// Mock UI components
vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>{children}</button>
  )
}));

vi.mock('@/components/ui/input', () => ({
  Input: ({ onChange, ...props }: any) => (
    <input onChange={onChange} {...props} />
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

vi.mock('@/components/ui/dropdown-menu', () => ({
  DropdownMenu: ({ children }: any) => <div>{children}</div>,
  DropdownMenuContent: ({ children }: any) => <div>{children}</div>,
  DropdownMenuItem: ({ children, onClick }: any) => (
    <div onClick={onClick}>{children}</div>
  ),
  DropdownMenuSeparator: () => <hr />,
  DropdownMenuTrigger: ({ children }: any) => <div>{children}</div>
}));

vi.mock('@/components/ui/dialog', () => ({
  Dialog: ({ children, open }: any) => open ? <div>{children}</div> : null,
  DialogContent: ({ children }: any) => <div>{children}</div>,
  DialogDescription: ({ children }: any) => <p>{children}</p>,
  DialogFooter: ({ children }: any) => <div>{children}</div>,
  DialogHeader: ({ children }: any) => <div>{children}</div>,
  DialogTitle: ({ children }: any) => <h2>{children}</h2>,
  DialogTrigger: ({ children }: any) => <div>{children}</div>
}));

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children }: any) => <span>{children}</span>
}));

describe('SessionManager', () => {
  const mockStore = {
    sessions: [
      {
        id: 'session-1',
        title: 'Test Session 1',
        messages: [
          { id: 'msg-1', text: 'Hello', sender: 'user' },
          { id: 'msg-2', text: 'Hi there!', sender: 'bot' }
        ],
        createdAt: '2024-01-01T10:00:00Z',
        updatedAt: '2024-01-01T10:05:00Z',
        isArchived: false,
        metadata: {}
      },
      {
        id: 'session-2',
        title: 'Archived Session',
        messages: [
          { id: 'msg-3', text: 'Old message', sender: 'user' }
        ],
        createdAt: '2024-01-01T09:00:00Z',
        updatedAt: '2024-01-01T09:05:00Z',
        isArchived: true,
        metadata: {}
      }
    ],
    activeSessionId: 'session-1',
    createSession: vi.fn().mockReturnValue('new-session-id'),
    setActiveSession: vi.fn(),
    deleteSession: vi.fn(),
    updateSession: vi.fn(),
    archiveSession: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useChatStore as any).mockReturnValue(mockStore);
  });

  it('renders session manager with sessions list', () => {
    render(<SessionManager />);
    
    expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    expect(screen.getByText('Archived Session')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('חיפוש שיחות...')).toBeInTheDocument();
    expect(screen.getByText('שיחה חדשה')).toBeInTheDocument();
  });

  it('filters sessions by search query', () => {
    render(<SessionManager />);
    
    const searchInput = screen.getByPlaceholderText('חיפוש שיחות...');
    fireEvent.change(searchInput, { target: { value: 'Test' } });
    
    expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    // Archived session should still be visible if it matches search
  });

  it('filters sessions by type (active/archived)', () => {
    render(<SessionManager />);
    
    // Click on archived filter
    const archivedButton = screen.getByText(/ארכיון/);
    fireEvent.click(archivedButton);
    
    // Should show archived sessions
    expect(screen.getByText('Archived Session')).toBeInTheDocument();
  });

  it('creates new session when dialog is submitted', async () => {
    render(<SessionManager />);
    
    // Open create dialog
    const createButton = screen.getByText('שיחה חדשה');
    fireEvent.click(createButton);
    
    // Fill in title
    const titleInput = screen.getByPlaceholderText('כותרת השיחה...');
    fireEvent.change(titleInput, { target: { value: 'New Test Session' } });
    
    // Submit
    const submitButton = screen.getByText('יצירה');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockStore.createSession).toHaveBeenCalledWith('New Test Session');
    });
  });

  it('selects session when clicked', () => {
    const onSessionSelect = vi.fn();
    render(<SessionManager onSessionSelect={onSessionSelect} />);
    
    const sessionCard = screen.getByText('Test Session 1').closest('div');
    fireEvent.click(sessionCard!);
    
    expect(mockStore.setActiveSession).toHaveBeenCalledWith('session-1');
    expect(onSessionSelect).toHaveBeenCalledWith('session-1');
  });

  it('deletes session when delete is confirmed', async () => {
    render(<SessionManager />);
    
    // Find and click the more options button (assuming it's rendered)
    // This is a simplified test - in reality you'd need to open the dropdown first
    const deleteButton = screen.getByText('מחיקה');
    fireEvent.click(deleteButton);
    
    await waitFor(() => {
      expect(mockStore.deleteSession).toHaveBeenCalled();
    });
  });

  it('archives/unarchives session', async () => {
    render(<SessionManager />);
    
    // Find and click archive button
    const archiveButton = screen.getByText('העברה לארכיון');
    fireEvent.click(archiveButton);
    
    await waitFor(() => {
      expect(mockStore.archiveSession).toHaveBeenCalled();
    });
  });

  it('updates session title when edit is submitted', async () => {
    render(<SessionManager />);
    
    // Open edit dialog (simplified)
    const editButton = screen.getByText('עריכת כותרת');
    fireEvent.click(editButton);
    
    // Fill in new title
    const titleInput = screen.getByPlaceholderText('כותרת השיחה...');
    fireEvent.change(titleInput, { target: { value: 'Updated Title' } });
    
    // Submit
    const saveButton = screen.getByText('שמירה');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(mockStore.updateSession).toHaveBeenCalledWith(
        expect.any(String),
        { title: 'Updated Title' }
      );
    });
  });

  it('shows empty state when no sessions match search', () => {
    const emptyStore = { ...mockStore, sessions: [] };
    (useChatStore as any).mockReturnValue(emptyStore);
    
    render(<SessionManager />);
    
    expect(screen.getByText('אין שיחות עדיין')).toBeInTheDocument();
  });

  it('shows session metadata correctly', () => {
    render(<SessionManager />);
    
    // Should show message count
    expect(screen.getByText('2 הודעות')).toBeInTheDocument();
    expect(screen.getByText('1 הודעות')).toBeInTheDocument();
    
    // Should show last message preview
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
    expect(screen.getByText('Old message')).toBeInTheDocument();
  });

  it('handles keyboard shortcuts in dialogs', () => {
    render(<SessionManager />);
    
    // Open create dialog
    const createButton = screen.getByText('שיחה חדשה');
    fireEvent.click(createButton);
    
    // Fill in title
    const titleInput = screen.getByPlaceholderText('כותרת השיחה...');
    fireEvent.change(titleInput, { target: { value: 'New Session' } });
    
    // Press Enter
    fireEvent.keyDown(titleInput, { key: 'Enter' });
    
    expect(mockStore.createSession).toHaveBeenCalledWith('New Session');
  });
});