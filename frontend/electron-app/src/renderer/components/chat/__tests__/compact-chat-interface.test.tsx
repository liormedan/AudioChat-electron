import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CompactChatInterface } from '../compact-chat-interface';

// Mock react-window
jest.mock('react-window', () => ({
  FixedSizeList: ({ children, itemCount, itemData }: any) => (
    <div data-testid="virtual-list">
      {Array.from({ length: itemCount }).map((_, index) => 
        children({ index, style: {}, data: itemData })
      )}
    </div>
  ),
}));

describe('CompactChatInterface', () => {
  const mockMessages = [
    {
      id: '1',
      text: 'Hello, how can I help you?',
      sender: 'bot' as const,
      timestamp: new Date('2024-01-01T10:00:00Z')
    },
    {
      id: '2',
      text: 'I need help with audio editing',
      sender: 'user' as const,
      timestamp: new Date('2024-01-01T10:01:00Z')
    }
  ];

  const defaultProps = {
    messages: mockMessages,
    onSendMessage: jest.fn(),
    onCommandSelect: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default height of 400px', () => {
    const { container } = render(<CompactChatInterface {...defaultProps} />);
    
    const card = container.querySelector('.compact-chat-interface');
    expect(card).toHaveStyle({ height: '400px' });
  });

  it('renders with custom height', () => {
    const { container } = render(<CompactChatInterface {...defaultProps} height={350} />);
    
    const card = container.querySelector('.compact-chat-interface');
    expect(card).toHaveStyle({ height: '350px' });
  });

  it('displays messages correctly', () => {
    render(<CompactChatInterface {...defaultProps} />);
    
    expect(screen.getByText('Hello, how can I help you?')).toBeInTheDocument();
    expect(screen.getByText('I need help with audio editing')).toBeInTheDocument();
  });

  it('shows empty state when no messages', () => {
    render(<CompactChatInterface {...defaultProps} messages={[]} />);
    
    expect(screen.getByText('No messages yet')).toBeInTheDocument();
    expect(screen.getByText('Start a conversation below')).toBeInTheDocument();
  });

  it('limits messages to maxMessages prop', () => {
    const manyMessages = Array.from({ length: 15 }, (_, i) => ({
      id: i.toString(),
      text: `Message ${i}`,
      sender: 'user' as const,
      timestamp: new Date()
    }));

    render(
      <CompactChatInterface 
        {...defaultProps} 
        messages={manyMessages}
        maxMessages={10}
      />
    );

    // Should only display the last 10 messages
    expect(screen.getByText('Message 14')).toBeInTheDocument(); // Last message
    expect(screen.getByText('Message 5')).toBeInTheDocument(); // 10th from last
    expect(screen.queryByText('Message 4')).not.toBeInTheDocument(); // 11th from last
  });

  it('sends message when send button is clicked', async () => {
    const user = userEvent.setup();
    render(<CompactChatInterface {...defaultProps} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button');
    
    await user.type(input, 'Test message');
    await user.click(sendButton);
    
    expect(defaultProps.onSendMessage).toHaveBeenCalledWith('Test message');
  });

  it('sends message when Enter is pressed', async () => {
    const user = userEvent.setup();
    render(<CompactChatInterface {...defaultProps} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    
    await user.type(input, 'Test message{enter}');
    
    expect(defaultProps.onSendMessage).toHaveBeenCalledWith('Test message');
  });

  it('does not send message when Shift+Enter is pressed', async () => {
    const user = userEvent.setup();
    render(<CompactChatInterface {...defaultProps} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    
    await user.type(input, 'Test message{shift>}{enter}{/shift}');
    
    expect(defaultProps.onSendMessage).not.toHaveBeenCalled();
  });

  it('shows command suggestions when enabled', () => {
    render(<CompactChatInterface {...defaultProps} showSuggestions={true} />);
    
    expect(screen.getByText('Quick Commands')).toBeInTheDocument();
    expect(screen.getByText('Increase volume by 20%')).toBeInTheDocument();
  });

  it('hides command suggestions when disabled', () => {
    render(<CompactChatInterface {...defaultProps} showSuggestions={false} />);
    
    expect(screen.queryByText('Quick Commands')).not.toBeInTheDocument();
  });

  it('calls onCommandSelect when suggestion is clicked', async () => {
    const user = userEvent.setup();
    render(<CompactChatInterface {...defaultProps} showSuggestions={true} />);
    
    const suggestion = screen.getByText('Increase volume by 20%');
    await user.click(suggestion);
    
    expect(defaultProps.onCommandSelect).toHaveBeenCalledWith('Increase volume by 20%');
    expect(defaultProps.onSendMessage).toHaveBeenCalledWith('Increase volume by 20%');
  });

  it('shows typing indicator when isTyping is true', () => {
    render(<CompactChatInterface {...defaultProps} isTyping={true} />);
    
    expect(screen.getByText('Typing...')).toBeInTheDocument();
  });

  it('disables input and buttons when disabled prop is true', () => {
    render(<CompactChatInterface {...defaultProps} disabled={true} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button');
    
    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  it('expands/collapses suggestions when toggle button is clicked', async () => {
    const user = userEvent.setup();
    render(<CompactChatInterface {...defaultProps} showSuggestions={true} />);
    
    // Initially shows limited suggestions
    expect(screen.getByText('Increase volume by 20%')).toBeInTheDocument();
    
    // Find and click the expand button
    const expandButton = screen.getByRole('button', { name: /chevron/i });
    await user.click(expandButton);
    
    // Should show more suggestions after expanding
    expect(screen.getByText('Extract 1:00 to 2:30')).toBeInTheDocument();
  });

  it('clears input after sending message', async () => {
    const user = userEvent.setup();
    render(<CompactChatInterface {...defaultProps} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button');
    
    await user.type(input, 'Test message');
    expect(input).toHaveValue('Test message');
    
    await user.click(sendButton);
    
    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('formats timestamps correctly', () => {
    const messageWithTime = [{
      id: '1',
      text: 'Test message',
      sender: 'bot' as const,
      timestamp: new Date('2024-01-01T14:30:00Z')
    }];

    render(<CompactChatInterface {...defaultProps} messages={messageWithTime} />);
    
    // Should show formatted time (format may vary based on locale)
    expect(screen.getByText(/\d{1,2}:\d{2}/)).toBeInTheDocument();
  });

  it('uses virtual scrolling for performance', () => {
    render(<CompactChatInterface {...defaultProps} />);
    
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
  });
});