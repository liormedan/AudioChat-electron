
import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChatInterface } from '@/components/chat/chat-interface';

describe('ChatInterface', () => {
  it('should render the main components', () => {
    render(<ChatInterface />);
    expect(screen.getByText('Session Sidebar')).toBeInTheDocument();
    expect(screen.getByText('No messages yet. Start a conversation!')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
  });
});
