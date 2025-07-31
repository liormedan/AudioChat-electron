
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { chatApiService } from '@/services/chat-api-service';

// Mock the global fetch function
global.fetch = vi.fn();

describe('chatApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch sessions successfully', async () => {
    const mockSessions = [{ id: '1', title: 'Test Session' }];
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockSessions),
    });

    const sessions = await chatApiService.getSessions();
    expect(sessions).toEqual(mockSessions);
    expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/chat/sessions');
  });

  it('should send a message successfully', async () => {
    const mockMessage = { id: '1', text: 'Hello', sender: 'user' };
    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockMessage),
    });

    const message = await chatApiService.sendMessage('session-1', 'Hello');
    expect(message).toEqual(mockMessage);
    expect(fetch).toHaveBeenCalledWith('http://localhost:5000/api/chat/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id: 'session-1', message: 'Hello' }),
    });
  });
});
