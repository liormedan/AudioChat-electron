import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { MessageSquare } from 'lucide-react';

export const ChatPage: React.FC = () => {
  const [conversation, setConversation] = useState<{ role: string; content: string }[]>([
    { role: 'assistant', content: 'Hello! How can I help you today?' },
  ]);
  const [chatInput, setChatInput] = useState<string>('');
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  // Scroll to the bottom of the chat history
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [conversation]);

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const userInput = chatInput.trim();
    if (!userInput) return;

    const newUserMessage = { role: 'user', content: userInput };
    setConversation((prev) => [...prev, newUserMessage]);
    setChatInput('');

    // Add a loading indicator
    const loadingMessage = { role: 'assistant', content: 'Thinking...' };
    setConversation((prev) => [...prev, loadingMessage]);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/llm/chat/completion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...conversation, newUserMessage] }), // Send full conversation
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const aiResponse = await response.json();
      
      // Remove loading indicator and add AI response
      setConversation((prev) => {
        const newConv = prev.slice(0, -1); // Remove loading message
        return [...newConv, { role: 'assistant', content: aiResponse.content }];
      });

    } catch (error: any) {
      console.error('Error during chat completion:', error);
      setConversation((prev) => {
        const newConv = prev.slice(0, -1); // Remove loading message
        return [...newConv, { role: 'assistant', content: `Sorry, an error occurred: ${error.message}` }];
      });
    }
  };

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>AI Chat</span>
          </CardTitle>
          <CardDescription>
            Chat with your AI assistant about audio processing
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col h-[400px] border rounded-lg bg-muted/20">
            <div ref={chatHistoryRef} className="flex-1 p-4 overflow-y-auto space-y-4">
              {conversation.map((msg, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg max-w-[80%] ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white self-end ml-auto'
                      : 'bg-gray-700 text-white self-start mr-auto'
                  }`}
                >
                  {msg.content}
                </div>
              ))}
            </div>
            <form onSubmit={handleChatSubmit} className="flex p-4 border-t border-gray-600">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 p-2 rounded-lg bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Button type="submit" className="ml-2 bg-blue-600 hover:bg-blue-700">
                Send
              </Button>
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};