
const API_BASE_URL = 'http://localhost:5000/api/chat';

// Type definitions for the API responses
interface Session {
  id: string;
  title: string;
  // Add other session properties as needed
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  // Add other message properties as needed
}

export const chatApiService = {
  async getSessions(): Promise<Session[]> {
    const response = await fetch(`${API_BASE_URL}/sessions`);
    if (!response.ok) {
      throw new Error('Failed to fetch sessions');
    }
    return response.json();
  },

  async sendMessage(sessionId: string, message: string): Promise<Message> {
    const response = await fetch(`${API_BASE_URL}/send`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    return response.json();
  },

  async streamMessage(sessionId: string, message: string, onChunk: (chunk: string) => void): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/stream`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id: sessionId, message }),
    });

    if (!response.body) {
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      const chunk = decoder.decode(value);
      onChunk(chunk);
    }
  },
};
