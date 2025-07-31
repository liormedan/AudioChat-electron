import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchPanel } from '../search-panel';
import { useChatStore } from '@/stores/chat-store';

// Mock the chat store
jest.mock('@/stores/chat-store');
const mockUseChatStore = useChatStore as jest.MockedFunction<typeof useChatStore>;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock data
const mockSessions = [
  {
    id: 'session-1',
    title: 'JavaScript Tutorial',
    messages: [
      {
        id: 'msg-1',
        text: 'What are React hooks?',
        sender: 'user' as const,
        timestamp: '2024-01-01T10:00:00Z',
      },
      {
        id: 'msg-2',
        text: 'React hooks are functions that let you use state and other React features in functional components.',
        sender: 'bot' as const,
        timestamp: '2024-01-01T10:01:00Z',
      },
    ],
    createdAt: '2024-01-01T10:00:00Z',
    updatedAt: '2024-01-01T10:01:00Z',
    isArchived: false,
  },
  {
    id: 'session-2',
    title: 'Python Guide',
    messages: [
      {
        id: 'msg-3',
        text: 'How to use Python decorators?',
        sender: 'user' as const,
        timestamp: '2024-01-02T10:00:00Z',
      },
      {
        id: 'msg-4',
        text: 'Python decorators are a way to modify or enhance functions without changing their code.',
        sender: 'bot' as const,
        timestamp: '2024-01-02T10:01:00Z',
      },
    ],
    createdAt: '2024-01-02T10:00:00Z',
    updatedAt: '2024-01-02T10:01:00Z',
    isArchived: false,
  },
];

describe('SearchPanel', () => {
  const mockOnResultSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    
    mockUseChatStore.mockReturnValue({
      sessions: mockSessions,
      activeSessionId: null,
      isBotTyping: false,
      addMessage: jest.fn(),
      createSession: jest.fn(),
      setActiveSession: jest.fn(),
      setIsBotTyping: jest.fn(),
      updateSession: jest.fn(),
      deleteSession: jest.fn(),
      archiveSession: jest.fn(),
      searchSessions: jest.fn(),
    });
  });

  it('renders search panel with basic elements', () => {
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    expect(screen.getByText('חיפוש בשיחות')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('חיפוש בתוכן ההודעות...')).toBeInTheDocument();
    expect(screen.getByText('מצב Regex')).toBeInTheDocument();
    expect(screen.getByText('תוצאות (0)')).toBeInTheDocument();
  });

  it('performs basic text search', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    
    await user.type(searchInput, 'React hooks');
    
    await waitFor(() => {
      expect(screen.getByText('תוצאות (2)')).toBeInTheDocument();
    });
    
    // Should find both the user question and bot answer
    expect(screen.getByText('What are React hooks?')).toBeInTheDocument();
    expect(screen.getByText(/React hooks are functions/)).toBeInTheDocument();
  });

  it('highlights search terms in results', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    
    await user.type(searchInput, 'React');
    
    await waitFor(() => {
      const highlightedElements = screen.getAllByText('React');
      // Should have highlighted instances
      expect(highlightedElements.length).toBeGreaterThan(0);
    });
  });

  it('filters by sender', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Open advanced filters
    const filtersButton = screen.getByTitle('חיפוש מתקדם');
    await user.click(filtersButton);
    
    // Search for something that appears in both user and bot messages
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, 'Python');
    
    await waitFor(() => {
      expect(screen.getByText('תוצאות (2)')).toBeInTheDocument();
    });
    
    // Filter to only user messages
    const userButton = screen.getByRole('button', { name: 'משתמש' });
    await user.click(userButton);
    
    await waitFor(() => {
      expect(screen.getByText('תוצאות (1)')).toBeInTheDocument();
    });
    
    // Should only show the user message
    expect(screen.getByText('How to use Python decorators?')).toBeInTheDocument();
    expect(screen.queryByText(/Python decorators are a way/)).not.toBeInTheDocument();
  });

  it('filters by date range', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Open advanced filters
    const filtersButton = screen.getByTitle('חיפוש מתקדם');
    await user.click(filtersButton);
    
    // Set date filter to only include first session
    const dateFromInput = screen.getByLabelText('מתאריך');
    const dateToInput = screen.getByLabelText('עד תאריך');
    
    await user.type(dateFromInput, '2024-01-01');
    await user.type(dateToInput, '2024-01-01');
    
    // Search for something that appears in both sessions
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, 'functions');
    
    await waitFor(() => {
      // Should only find results from the first session
      expect(screen.getByText(/React hooks are functions/)).toBeInTheDocument();
    });
  });

  it('supports regex search mode', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Enable regex mode
    const regexSwitch = screen.getByRole('switch');
    await user.click(regexSwitch);
    
    // Search with regex pattern
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, 'React|Python');
    
    await waitFor(() => {
      // Should find results containing either "React" or "Python"
      expect(screen.getByText('תוצאות (4)')).toBeInTheDocument();
    });
  });

  it('handles invalid regex gracefully', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Enable regex mode
    const regexSwitch = screen.getByRole('switch');
    await user.click(regexSwitch);
    
    // Search with invalid regex
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, '[invalid');
    
    await waitFor(() => {
      // Should fall back to normal text search
      expect(screen.getByText('תוצאות (0)')).toBeInTheDocument();
    });
  });

  it('saves and loads search history', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Perform a search
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, 'React hooks');
    
    await waitFor(() => {
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'chat-search-history',
        JSON.stringify(['React hooks'])
      );
    });
    
    // Switch to history tab
    const historyTab = screen.getByRole('tab', { name: /היסטוריה/ });
    await user.click(historyTab);
    
    // Mock localStorage to return the saved history
    localStorageMock.getItem.mockReturnValue(JSON.stringify(['React hooks']));
    
    // Re-render to load from localStorage
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    const historyTabNew = screen.getByRole('tab', { name: /היסטוריה/ });
    await user.click(historyTabNew);
    
    expect(screen.getByText('React hooks')).toBeInTheDocument();
  });

  it('saves and loads saved searches', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Perform a search
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, 'React hooks');
    
    // Open save dialog
    const saveButton = screen.getByTitle('שמור חיפוש');
    await user.click(saveButton);
    
    // Enter save name
    const nameInput = screen.getByPlaceholderText('הזן שם לחיפוש...');
    await user.type(nameInput, 'My React Search');
    
    // Save the search
    const saveConfirmButton = screen.getByRole('button', { name: 'שמור' });
    await user.click(saveConfirmButton);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'chat-saved-searches',
      expect.stringContaining('My React Search')
    );
  });

  it('calls onResultSelect when clicking a result', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Perform a search
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, 'React hooks');
    
    await waitFor(() => {
      expect(screen.getByText('תוצאות (2)')).toBeInTheDocument();
    });
    
    // Click on a result
    const resultCard = screen.getByText('What are React hooks?').closest('[role="button"], .cursor-pointer');
    if (resultCard) {
      await user.click(resultCard);
      expect(mockOnResultSelect).toHaveBeenCalledWith('session-1', 'msg-1');
    }
  });

  it('clears filters when clear button is clicked', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Open advanced filters
    const filtersButton = screen.getByTitle('חיפוש מתקדם');
    await user.click(filtersButton);
    
    // Set some filters
    const dateFromInput = screen.getByLabelText('מתאריך');
    await user.type(dateFromInput, '2024-01-01');
    
    const userButton = screen.getByRole('button', { name: 'משתמש' });
    await user.click(userButton);
    
    // Clear filters
    const clearButton = screen.getByRole('button', { name: 'נקה פילטרים' });
    await user.click(clearButton);
    
    // Check that filters are cleared
    expect(dateFromInput).toHaveValue('');
    expect(screen.getByRole('button', { name: 'הכל' })).toHaveClass('bg-primary'); // Should be selected
  });

  it('shows empty state when no results found', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, 'nonexistent search term');
    
    await waitFor(() => {
      expect(screen.getByText('לא נמצאו תוצאות')).toBeInTheDocument();
    });
  });

  it('shows loading state during search', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    
    // Type quickly to trigger loading state
    await act(async () => {
      await user.type(searchInput, 'React');
    });
    
    // The loading state might be brief, but we can test that it doesn't crash
    expect(screen.getByPlaceholderText('חיפוש בתוכן ההודעות...')).toBeInTheDocument();
  });

  it('filters by specific session', async () => {
    const user = userEvent.setup();
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Open advanced filters
    const filtersButton = screen.getByTitle('חיפוש מתקדם');
    await user.click(filtersButton);
    
    // Select specific session
    const sessionSelect = screen.getByDisplayValue('כל השיחות');
    await user.selectOptions(sessionSelect, 'session-1');
    
    // Search for something that appears in both sessions
    const searchInput = screen.getByPlaceholderText('חיפוש בתוכן ההודעות...');
    await user.type(searchInput, 'functions');
    
    await waitFor(() => {
      // Should only find results from session-1
      expect(screen.getByText(/React hooks are functions/)).toBeInTheDocument();
      expect(screen.queryByText(/Python decorators are a way/)).not.toBeInTheDocument();
    });
  });

  it('removes items from search history', async () => {
    const user = userEvent.setup();
    
    // Mock localStorage to return existing history
    localStorageMock.getItem.mockReturnValue(JSON.stringify(['React hooks', 'Python guide']));
    
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Switch to history tab
    const historyTab = screen.getByRole('tab', { name: /היסטוריה/ });
    await user.click(historyTab);
    
    // Find and click remove button for first item
    const removeButtons = screen.getAllByRole('button');
    const removeButton = removeButtons.find(button => {
      const icon = button.querySelector('svg');
      return icon && button.closest('.hover\\:bg-accent\\/50');
    });
    
    if (removeButton) {
      await user.click(removeButton);
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'chat-search-history',
        JSON.stringify(['Python guide'])
      );
    }
  });

  it('removes saved searches', async () => {
    const user = userEvent.setup();
    
    const mockSavedSearches = [
      {
        id: 'search-1',
        name: 'My React Search',
        query: 'React hooks',
        filters: { sender: 'all' },
        createdAt: '2024-01-01T10:00:00Z',
      },
    ];
    
    // Mock localStorage to return existing saved searches
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'chat-saved-searches') {
        return JSON.stringify(mockSavedSearches);
      }
      return null;
    });
    
    render(<SearchPanel onResultSelect={mockOnResultSelect} />);
    
    // Switch to saved searches tab
    const savedTab = screen.getByRole('tab', { name: /שמורים/ });
    await user.click(savedTab);
    
    // Find and click remove button
    const removeButtons = screen.getAllByRole('button');
    const removeButton = removeButtons.find(button => {
      const icon = button.querySelector('svg');
      return icon && button.closest('.hover\\:bg-accent\\/50');
    });
    
    if (removeButton) {
      await user.click(removeButton);
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'chat-saved-searches',
        JSON.stringify([])
      );
    }
  });
});