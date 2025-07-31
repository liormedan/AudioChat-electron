import React, { useRef, useState, useEffect } from 'react';
import { useChatStore } from '@/stores/chat-store';
import { chatApiService } from '@/services/chat-api-service';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

export const InputArea: React.FC = () => {
  const [message, setMessage] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const activeSessionId = useChatStore((state) => state.activeSessionId);
  const addMessage = useChatStore((state) => state.addMessage);
  const setIsBotTyping = useChatStore((state) => state.setIsBotTyping); // Get the new action

  const handleSendMessage = async () => {
    if (message.trim() === '' || !activeSessionId) return;

    const userMessage = { id: `msg-${Date.now()}-user`, text: message, sender: 'user' as const };
    addMessage(activeSessionId, userMessage);
    setMessage('');

    try {
      // Optimistic update: Add a placeholder for the bot's response
      const botPlaceholderId = `msg-${Date.now()}-bot-placeholder`;
      addMessage(activeSessionId, { id: botPlaceholderId, text: 'Typing...', sender: 'bot' as const });
      setIsBotTyping(true); // Set bot typing to true

      await chatApiService.streamMessage(activeSessionId, message, (chunk) => {
        // This part would update the bot's message in real-time
        // For now, we'll just replace the placeholder with the full response once done
        console.log('Received chunk:', chunk);
      });

      // After streaming, fetch the actual message or update the placeholder
      // For simplicity, we'll just add a static bot response for now
      const botResponse = { id: `msg-${Date.now()}-bot`, text: `Echo: ${message}`, sender: 'bot' as const };
      // In a real app, you'd replace the placeholder with the actual streamed content
      // For now, we'll just add a new message and rely on the chat store to handle updates
      addMessage(activeSessionId, botResponse);

    } catch (error) {
      console.error('Error sending message:', error);
      // Handle error: maybe remove the optimistic update or show an error message
    } finally {
      setIsBotTyping(false); // Set bot typing to false after completion or error
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const charCount = message.length;

  return (
    <div className="p-4 border-t bg-white flex flex-col space-y-2">
      <div className="flex items-end space-x-2">
        <textarea
          ref={textareaRef}
          className="flex-grow resize-none overflow-hidden p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type your message..."
          rows={1}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          onClick={handleSendMessage}
          disabled={!activeSessionId || message.trim() === ''}
        >
          Send
        </button>
      </div>
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{charCount} characters</span>
        <button
          className="text-blue-500 hover:underline"
          onClick={() => setShowPreview(!showPreview)}
        >
          {showPreview ? 'Hide Preview' : 'Show Preview'}
        </button>
      </div>
      {showPreview && message.trim() !== '' && (
        <div className="p-2 border rounded-lg bg-gray-50">
          <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
            {message}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
};