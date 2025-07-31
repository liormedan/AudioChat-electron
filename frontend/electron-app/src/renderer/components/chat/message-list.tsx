

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useChatStore } from '@/stores/chat-store';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { coldarkDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { FixedSizeList } from 'react-window';

// Component to render a single message row in the virtualized list
const MessageRow = ({ index, style, data }: any) => {
  const message = data.messages[index];
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  }, [message.text]);

  return (
    <div style={style}>
      <div
        key={message.id}
        className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
      >
        <div
          className={`max-w-xs px-4 py-2 rounded-lg ${message.sender === 'user'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-300 text-gray-800'
          }`}
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={coldarkDark}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {message.text}
          </ReactMarkdown>
          {message.sender === 'bot' && (
            <button
              onClick={handleCopy}
              className="mt-2 text-xs text-gray-600 hover:text-gray-800"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export const MessageList: React.FC = () => {
  const activeSessionId = useChatStore((state) => state.activeSessionId);
  const sessions = useChatStore((state) => state.sessions);
  const isBotTyping = useChatStore((state) => state.isBotTyping);

  const activeSession = sessions.find((session) => session.id === activeSessionId);
  const messages = activeSession ? activeSession.messages : [];

  const listRef = useRef<FixedSizeList>(null);

  // Auto-scroll to the bottom when new messages arrive or bot starts typing
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollToItem(messages.length - 1, 'auto');
    }
  }, [messages.length, isBotTyping]);

  return (
    <div className="flex-grow bg-white" style={{ height: '100%', width: '100%' }}>
      {messages.length === 0 ? (
        <div className="text-center text-gray-500 p-4">No messages yet. Start a conversation!</div>
      ) : (
        <FixedSizeList
          height={500} // This height needs to be dynamic based on parent container
          itemCount={messages.length + (isBotTyping ? 1 : 0)} // Add space for typing indicator
          itemSize={100} // This size needs to be dynamic based on message content
          width="100%"
          ref={listRef}
          itemData={{ messages }}
        >
          {MessageRow}
        </FixedSizeList>
      )}
      {isBotTyping && (
        <div className="flex justify-start p-4">
          <div className="max-w-xs px-4 py-2 rounded-lg bg-gray-300 text-gray-800">
            Typing...
          </div>
        </div>
      )}
    </div>
  );
};