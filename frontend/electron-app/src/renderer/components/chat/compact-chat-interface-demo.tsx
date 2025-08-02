import React, { useState, useCallback } from 'react';
import { CompactChatInterface } from './compact-chat-interface';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { Trash2, MessageSquare } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export const CompactChatInterfaceDemo: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I can help you with audio editing tasks.',
      sender: 'bot',
      timestamp: new Date(Date.now() - 300000)
    },
    {
      id: '2',
      text: 'Can you increase the volume of my audio file?',
      sender: 'user',
      timestamp: new Date(Date.now() - 240000)
    },
    {
      id: '3',
      text: 'Sure! I can increase the volume by 20%. Would you like me to proceed?',
      sender: 'bot',
      timestamp: new Date(Date.now() - 180000)
    }
  ]);
  
  const [isTyping, setIsTyping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);
  const [maxMessages, setMaxMessages] = useState(10);

  const handleSendMessage = useCallback((messageText: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newMessage]);
    
    // Simulate bot response
    setIsTyping(true);
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: `I understand you want to: "${messageText}". I'll help you with that!`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1500);
  }, []);

  const handleCommandSelect = useCallback((command: string) => {
    console.log('Command selected:', command);
    // Command is automatically sent as a message via handleSendMessage
  }, []);

  const clearMessages = () => {
    setMessages([]);
  };

  const addSampleMessages = () => {
    const sampleMessages: Message[] = [
      {
        id: `sample-${Date.now()}-1`,
        text: 'Remove background noise from my recording',
        sender: 'user',
        timestamp: new Date()
      },
      {
        id: `sample-${Date.now()}-2`,
        text: 'I\'ll apply noise reduction to your audio. This will help clean up any unwanted background sounds.',
        sender: 'bot',
        timestamp: new Date(Date.now() + 1000)
      },
      {
        id: `sample-${Date.now()}-3`,
        text: 'Perfect! Can you also add a fade in effect?',
        sender: 'user',
        timestamp: new Date(Date.now() + 2000)
      }
    ];
    
    setMessages(prev => [...prev, ...sampleMessages]);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Compact Chat Interface Demo</CardTitle>
          <CardDescription>
            A compact chat interface with 400px fixed height, virtual scrolling, and command suggestions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Controls */}
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <Switch
                id="suggestions"
                checked={showSuggestions}
                onCheckedChange={setShowSuggestions}
              />
              <Label htmlFor="suggestions">Show Suggestions</Label>
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch
                id="autoscroll"
                checked={autoScroll}
                onCheckedChange={setAutoScroll}
              />
              <Label htmlFor="autoscroll">Auto Scroll</Label>
            </div>
            
            <Button onClick={addSampleMessages} variant="outline" size="sm">
              <MessageSquare className="h-4 w-4 mr-2" />
              Add Sample Messages
            </Button>
            
            <Button onClick={clearMessages} variant="outline" size="sm">
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Messages
            </Button>
          </div>

          {/* Chat Interface */}
          <CompactChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            onCommandSelect={handleCommandSelect}
            height={400}
            maxMessages={maxMessages}
            showSuggestions={showSuggestions}
            autoScroll={autoScroll}
            isTyping={isTyping}
          />
        </CardContent>
      </Card>

      {/* Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Chat Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="font-medium">Total Messages:</p>
              <p className="text-muted-foreground">{messages.length}</p>
            </div>
            <div>
              <p className="font-medium">Displayed Messages:</p>
              <p className="text-muted-foreground">{Math.min(messages.length, maxMessages)}</p>
            </div>
            <div>
              <p className="font-medium">User Messages:</p>
              <p className="text-muted-foreground">
                {messages.filter(m => m.sender === 'user').length}
              </p>
            </div>
            <div>
              <p className="font-medium">Bot Messages:</p>
              <p className="text-muted-foreground">
                {messages.filter(m => m.sender === 'bot').length}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Component Specifications */}
      <Card>
        <CardHeader>
          <CardTitle>Component Specifications</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Total Height:</span>
              <span className="font-mono">400px</span>
            </div>
            <div className="flex justify-between">
              <span>Chat Area:</span>
              <span className="font-mono">~260px (65%)</span>
            </div>
            <div className="flex justify-between">
              <span>Input Area:</span>
              <span className="font-mono">60px</span>
            </div>
            <div className="flex justify-between">
              <span>Suggestions Area:</span>
              <span className="font-mono">~80px (20%)</span>
            </div>
            <div className="flex justify-between">
              <span>Max Visible Messages:</span>
              <span className="font-mono">{maxMessages}</span>
            </div>
            <div className="flex justify-between">
              <span>Virtual Scrolling:</span>
              <span className="text-green-600">Enabled</span>
            </div>
            <div className="flex justify-between">
              <span>Performance Optimized:</span>
              <span className="text-green-600">Yes</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Messages */}
      {messages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Messages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {messages.slice(-5).map((message) => (
                <div key={message.id} className="text-sm">
                  <div className="flex items-center justify-between">
                    <span className={`font-medium ${
                      message.sender === 'user' ? 'text-blue-600' : 'text-green-600'
                    }`}>
                      {message.sender === 'user' ? 'User' : 'Bot'}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-muted-foreground truncate">{message.text}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};