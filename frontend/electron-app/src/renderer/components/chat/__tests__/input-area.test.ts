/** @jsxImportSource react */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { InputArea } from '@/components/chat/input-area';
import { useChatStore } from '@/stores/chat-store';
import { chatApiService } from '@/services/chat-api-service';
import { vi } from 'vitest';

// Mock chatApiService
vi.mock('@/services/chat-api-service', () => ({
  chatApiService: {
    streamMessage: vi.fn(() => Promise.resolve()),
  },
}));

describe('InputArea', () => {
  beforeEach(() => {
    // Reset the store and mocks before each test
    useChatStore.setState({ sessions: [], activeSessionId: null });
    vi.clearAllMocks();
  });

  it('should render the textarea and send button', () => {
    render(<InputArea />);
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Send/i })).toBeInTheDocument();
    expect(screen.getByText('0 characters')).toBeInTheDocument();
  });

  it('should update message on textarea change', () => {
    render(<InputArea />);
    const textarea = screen.getByPlaceholderText('Type your message...') as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: 'Hello world' } });
    expect(textarea.value).toBe('Hello world');
    expect(screen.getByText('11 characters')).toBeInTheDocument();
  });

  it('should send message on button click if session is active', async () => {
    useChatStore.setState({
      sessions: [
        { id: 'session-1', title: 'Test Session', messages: [] },
      ],
      activeSessionId: 'session-1',
    });
    render(<InputArea />);
    const textarea = screen.getByPlaceholderText('Type your message...') as HTMLTextAreaElement;
    const sendButton = screen.getByRole('button', { name: /Send/i });

    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    // Expect message to be added optimistically
    expect(useChatStore.getState().sessions[0].messages.length).toBe(2); // User message + bot placeholder
    expect(useChatStore.getState().sessions[0].messages[0].text).toBe('Test message');
    expect(textarea.value).toBe(''); // Input should be cleared
    expect(chatApiService.streamMessage).toHaveBeenCalledWith('session-1', 'Test message', expect.any(Function));
  });

  it('should send message on Ctrl+Enter', async () => {
    useChatStore.setState({
      sessions: [
        { id: 'session-1', title: 'Test Session', messages: [] },
      ],
      activeSessionId: 'session-1',
    });
    render(<InputArea />);
    const textarea = screen.getByPlaceholderText('Type your message...') as HTMLTextAreaElement;

    fireEvent.change(textarea, { target: { value: 'Another message' } });
    fireEvent.keyDown(textarea, { key: 'Enter', ctrlKey: true });

    expect(useChatStore.getState().sessions[0].messages.length).toBe(2); // User message + bot placeholder
    expect(useChatStore.getState().sessions[0].messages[0].text).toBe('Another message');
    expect(textarea.value).toBe('');
    expect(chatApiService.streamMessage).toHaveBeenCalledWith('session-1', 'Another message', expect.any(Function));
  });

  it('should not send message if textarea is empty', async () => {
    useChatStore.setState({
      sessions: [
        { id: 'session-1', title: 'Test Session', messages: [] },
      ],
      activeSessionId: 'session-1',
    });
    render(<InputArea />);
    const sendButton = screen.getByRole('button', { name: /Send/i });

    fireEvent.click(sendButton);

    expect(useChatStore.getState().sessions[0].messages.length).toBe(0);
    expect(chatApiService.streamMessage).not.toHaveBeenCalled();
  });

  it('should not send message if no active session', async () => {
    render(<InputArea />);
    const textarea = screen.getByPlaceholderText('Type your message...') as HTMLTextAreaElement;
    const sendButton = screen.getByRole('button', { name: /Send/i });

    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    expect(useChatStore.getState().sessions.length).toBe(0);
    expect(chatApiService.streamMessage).not.toHaveBeenCalled();
  });

  it('should toggle markdown preview', async () => {
    render(<InputArea />);
    const textarea = screen.getByPlaceholderText('Type your message...') as HTMLTextAreaElement;
    const previewButton = screen.getByRole('button', { name: /Show Preview/i });

    fireEvent.change(textarea, { target: { value: '# Hello Markdown' } });
    expect(screen.queryByText('Hello Markdown')).not.toBeInTheDocument();

    fireEvent.click(previewButton);
    expect(screen.getByRole('heading', { level: 1, name: 'Hello Markdown' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Hide Preview/i })).toBeInTheDocument();

    fireEvent.click(previewButton);
    expect(screen.queryByText('Hello Markdown')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Show Preview/i })).toBeInTheDocument();
  });
});