

import React from 'react';
import { render, screen } from '@testing-library/react';
import { MessageList } from '@/components/chat/message-list';
import { useChatStore } from '@/stores/chat-store';

describe('MessageList', () => {
  it('should display no messages when the session is empty', () => {
    useChatStore.setState({ sessions: [], activeSessionId: null });
    render(<MessageList />);
    expect(screen.getByText('No messages yet. Start a conversation!')).toBeInTheDocument();
  });

  it('should display messages for the active session', () => {
    useChatStore.setState({
      sessions: [
        {
          id: 'session-1',
          title: 'Test Session',
          messages: [
            { id: '1', text: 'Hello from user', sender: 'user' },
            { id: '2', text: 'Hello from bot', sender: 'bot' },
          ],
        },
      ],
      activeSessionId: 'session-1',
    });
    render(<MessageList />);
    expect(screen.getByText('Hello from user')).toBeInTheDocument();
    expect(screen.getByText('Hello from bot')).toBeInTheDocument();
  });

  it('should render markdown content', () => {
    useChatStore.setState({
      sessions: [
        {
          id: 'session-2',
          title: 'Markdown Test',
          messages: [
            { id: '3', text: '# Heading\n\n**Bold text**\n\n```javascript\nconsole.log(\"Hello\");\n```', sender: 'bot' },
          ],
        },
      ],
      activeSessionId: 'session-2',
    });
    render(<MessageList />);
    expect(screen.getByRole('heading', { level: 1, name: 'Heading' })).toBeInTheDocument();
    expect(screen.getByText('Bold text')).toBeInTheDocument();
    expect(screen.getByText('console.log(\"Hello\");')).toBeInTheDocument();
  });
});

