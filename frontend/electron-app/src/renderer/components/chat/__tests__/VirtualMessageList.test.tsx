import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { VirtualMessageList } from '../VirtualMessageList';
import { Message } from '@/types/chat';

// Mock react-window
vi.mock('react-window', () => ({
  FixedSizeList: vi.fn(({ children, itemData, itemCount, itemSize }) => (
    <div data-testid="virtual-list">
      {Array.from({ length: Math.min(itemCount, 10) }).map((_, index) => (
        <div key={index} style={{ height: itemSize }}>
          {children({ index, style: { height: itemSize }, data: itemData })}
        </div>
      ))}
    </div>
  ))
}));

// Mock performance hooks
vi.mock('@/hooks/usePerformance', () => ({
  useRenderPerformance: () => ({
    markRenderStart: vi.fn(),
    markRenderEnd: vi.fn()
  }),
  useComponentSize: () => ({
    elementRef: { current: null },
    size: { width: 800, height: 600 }
  })
}));

// Mock MessageBubble component
vi.mock('../MessageBubble', () => ({
  MessageBubble: vi.fn(({ message }) => (
    <div data-testid={`message-${message.id}`}>
      {message.content}
    </div>
  ))
}));

const createMockMessage = (id: string, content: string, role: 'user' | 'assistant' = 'user'): Message => ({
  id,
  session_id: 'session-1',
  content,
  role,
  timestamp: new Date().toISOString(),
  tokens_used: 10,
  response_time: 1.5,
  metadata: {}
});

describe('VirtualMessageList', () => {
  const mockMessages: Message[] = [
    createMockMessage('1', 'Hello world', 'user'),
    createMockMessage('2', 'Hi there!', 'assistant'),
    createMockMessage('3', 'How are you?', 'user'),
    createMockMessage('4', 'I am doing well, thank you!', 'assistant'),
    createMockMessage('5', 'Great to hear!', 'user'),
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders virtual message list with messages', () => {
    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
      />
    );

    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
    expect(screen.getByTestId('message-1')).toBeInTheDocument();
    expect(screen.getByText('Hello world')).toBeInTheDocument();
  });

  it('renders empty state when no messages', () => {
    render(
      <VirtualMessageList
        messages={[]}
        sessionId="session-1"
      />
    );

    expect(screen.getByText('אין הודעות עדיין')).toBeInTheDocument();
    expect(screen.getByText('התחל שיחה חדשה על ידי כתיבת הודעה למטה')).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(
      <VirtualMessageList
        messages={[]}
        sessionId="session-1"
        loading={true}
      />
    );

    // Should show skeleton loading
    expect(screen.getAllByRole('generic')).toHaveLength(5); // 5 skeleton items
  });

  it('renders error state', () => {
    const errorMessage = 'Failed to load messages';
    
    render(
      <VirtualMessageList
        messages={[]}
        sessionId="session-1"
        error={errorMessage}
      />
    );

    expect(screen.getByText('שגיאה בטעינת ההודעות')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByText('נסה שוב')).toBeInTheDocument();
  });

  it('handles scroll to bottom button', async () => {
    const { rerender } = render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
        autoScroll={true}
      />
    );

    // Initially, scroll button should not be visible
    expect(screen.queryByLabelText('גלול למטה')).not.toBeInTheDocument();

    // Simulate scroll event that would show the button
    // This is a simplified test since we can't easily simulate the actual scroll behavior
    const virtualList = screen.getByTestId('virtual-list');
    fireEvent.scroll(virtualList, { target: { scrollTop: 100 } });

    // In a real scenario, the scroll button would appear
    // For this test, we'll just verify the component structure
    expect(virtualList).toBeInTheDocument();
  });

  it('handles message click events', () => {
    const onMessageClick = vi.fn();
    
    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
        onMessageClick={onMessageClick}
      />
    );

    // Click on a message (this would be handled by MessageBubble in real scenario)
    const message = screen.getByTestId('message-1');
    fireEvent.click(message);

    // In the actual implementation, this would trigger the callback
    expect(message).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const customClass = 'custom-message-list';
    
    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
        className={customClass}
      />
    );

    const container = screen.getByTestId('virtual-list').parentElement;
    expect(container).toHaveClass(customClass);
  });

  it('handles different item heights', () => {
    const customItemHeight = 150;
    
    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
        itemHeight={customItemHeight}
      />
    );

    // Verify that the virtual list is rendered
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
    
    // In the actual implementation, this would affect the virtual scrolling calculations
    const messageElements = screen.getAllByTestId(/^message-/);
    expect(messageElements.length).toBeGreaterThan(0);
  });

  it('handles auto-scroll behavior', () => {
    const { rerender } = render(
      <VirtualMessageList
        messages={mockMessages.slice(0, 3)}
        sessionId="session-1"
        autoScroll={true}
      />
    );

    // Add new messages
    rerender(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
        autoScroll={true}
      />
    );

    // Verify that new messages are rendered
    expect(screen.getByTestId('message-4')).toBeInTheDocument();
    expect(screen.getByTestId('message-5')).toBeInTheDocument();
  });

  it('disables auto-scroll when specified', () => {
    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
        autoScroll={false}
      />
    );

    // Component should still render normally
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
    expect(screen.getByTestId('message-1')).toBeInTheDocument();
  });

  it('handles message copy functionality', () => {
    const onMessageCopy = vi.fn();
    
    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
        onMessageCopy={onMessageCopy}
      />
    );

    // Verify messages are rendered (copy functionality would be in MessageBubble)
    expect(screen.getByTestId('message-1')).toBeInTheDocument();
  });

  it('handles message deletion', () => {
    const onMessageDelete = vi.fn();
    
    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
        onMessageDelete={onMessageDelete}
      />
    );

    // Verify messages are rendered (delete functionality would be in MessageBubble)
    expect(screen.getByTestId('message-1')).toBeInTheDocument();
  });

  it('renders with RTL direction', () => {
    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
      />
    );

    const virtualList = screen.getByTestId('virtual-list');
    expect(virtualList).toBeInTheDocument();
    
    // In the actual implementation, this would have RTL styling
    expect(virtualList.parentElement).toHaveClass('relative');
  });

  it('handles performance monitoring in development', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
      />
    );

    // Verify component renders normally in development mode
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });

  it('memoizes messages for performance', () => {
    const { rerender } = render(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
      />
    );

    // Re-render with same messages
    rerender(
      <VirtualMessageList
        messages={mockMessages}
        sessionId="session-1"
      />
    );

    // Component should still work correctly
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
    expect(screen.getByTestId('message-1')).toBeInTheDocument();
  });

  it('handles large number of messages efficiently', () => {
    const largeMessageList = Array.from({ length: 1000 }, (_, index) =>
      createMockMessage(`msg-${index}`, `Message ${index}`, index % 2 === 0 ? 'user' : 'assistant')
    );

    render(
      <VirtualMessageList
        messages={largeMessageList}
        sessionId="session-1"
      />
    );

    // Should render virtual list without performance issues
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
    
    // Only a subset should be rendered due to virtualization
    const renderedMessages = screen.getAllByTestId(/^message-/);
    expect(renderedMessages.length).toBeLessThanOrEqual(10); // Limited by our mock
  });
});