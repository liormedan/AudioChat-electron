import React, { useState, useRef, useEffect } from 'react';
import './gemini-chat.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface GeminiChatProps {
  apiKey?: string;
  onApiKeyChange?: (key: string) => void;
}

const GeminiChat: React.FC<GeminiChatProps> = ({ apiKey, onApiKeyChange }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentApiKey, setCurrentApiKey] = useState(apiKey || '');
  const [showApiKeyInput, setShowApiKeyInput] = useState(!apiKey);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleApiKeySubmit = async () => {
    if (!currentApiKey.trim()) {
      alert('אנא הכנס מפתח API');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/api/llm/set-api-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider_name: 'Google',
          api_key: currentApiKey
        })
      });

      const result = await response.json();

      if (result.success) {
        setShowApiKeyInput(false);
        onApiKeyChange?.(currentApiKey);

        // Test connection
        const testResponse = await fetch('http://127.0.0.1:8000/api/llm/test-connection', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            provider_name: 'Google'
          })
        });

        const testResult = await testResponse.json();

        if (testResult.success) {
          addMessage('assistant', 'שלום! אני Gemini, מוכן לעזור לך. איך אני יכול לסייע?');
        } else {
          alert('מפתח ה-API נשמר אבל החיבור נכשל. אנא בדוק את המפתח.');
        }
      } else {
        alert('שגיאה בשמירת מפתח ה-API');
      }
    } catch (error) {
      console.error('Error setting API key:', error);
      alert('שגיאה בחיבור לשרת');
    }
  };

  const addMessage = (role: 'user' | 'assistant', content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      role,
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    addMessage('user', userMessage);
    setIsLoading(true);

    try {
      // Prepare messages for API
      const apiMessages = [...messages, { role: 'user', content: userMessage }].map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await fetch('http://127.0.0.1:8000/api/gemini/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: apiMessages,
          temperature: 0.7,
          max_tokens: 2048
        })
      });

      const result = await response.json();

      if (result.success) {
        addMessage('assistant', result.content);
      } else {
        addMessage('assistant', result.content || 'מצטער, אירעה שגיאה. אנא נסה שוב.');
        console.error('Gemini API error:', result.error);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage('assistant', 'מצטער, לא הצלחתי להתחבר לשרת. אנא בדוק את החיבור.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  if (showApiKeyInput) {
    return (
      <div className="gemini-chat-container">
        <div className="api-key-setup">
          <h3>🔑 הגדרת מפתח Gemini API</h3>
          <p>כדי להתחיל לשוחח עם Gemini, אנא הכנס את מפתח ה-API שלך:</p>
          <div className="api-key-input-group">
            <input
              type="password"
              value={currentApiKey}
              onChange={(e) => setCurrentApiKey(e.target.value)}
              placeholder="הכנס מפתח Gemini API..."
              className="api-key-input"
              onKeyPress={(e) => e.key === 'Enter' && handleApiKeySubmit()}
            />
            <button onClick={handleApiKeySubmit} className="api-key-submit">
              שמור והתחבר
            </button>
          </div>
          <div className="api-key-help">
            <p>
              <strong>איך להשיג מפתח API:</strong>
            </p>
            <ol>
              <li>עבור ל-<a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a></li>
              <li>התחבר עם חשבון Google שלך</li>
              <li>לחץ על "Create API Key"</li>
              <li>העתק את המפתח והדבק אותו כאן</li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="gemini-chat-container">
      <div className="chat-header">
        <div className="header-title">
          <h2>🤖 Gemini Chat</h2>
          <span className="status-indicator">מחובר</span>
        </div>
        <div className="header-actions">
          <button onClick={clearChat} className="clear-button" title="נקה שיחה">
            🗑️
          </button>
          <button
            onClick={() => setShowApiKeyInput(true)}
            className="settings-button"
            title="הגדרות API"
          >
            ⚙️
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>ברוך הבא לצ'אט עם Gemini! 🎉</h3>
            <p>אני כאן לעזור לך עם כל שאלה או משימה. פשוט כתוב הודעה למטה.</p>
            <div className="example-prompts">
              <p><strong>דוגמאות למה אתה יכול לשאול:</strong></p>
              <ul>
                <li>כתוב לי קוד Python לניתוח נתונים</li>
                <li>הסבר לי על בינה מלאכותית</li>
                <li>עזור לי לכתוב מייל מקצועי</li>
                <li>תן לי רעיונות לפרויקט חדש</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-time">
                {message.timestamp.toLocaleTimeString('he-IL')}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <div className="input-group">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="כתוב הודעה ל-Gemini..."
            className="message-input"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeminiChat;