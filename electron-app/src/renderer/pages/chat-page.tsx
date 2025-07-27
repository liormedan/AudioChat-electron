import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { MessageSquare, FileAudio, ArrowLeft, Loader2, Send } from 'lucide-react';
import { useAudioChatStore } from '../stores/audio-chat-store';
import { AudioContextIndicator } from '../components/audio/audio-context-indicator';
import { useNavigate } from 'react-router-dom';

export const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  
  // General chat state (separate from audio chat)
  const [generalConversation, setGeneralConversation] = useState<{ role: string; content: string }[]>([
    { role: 'assistant', content: 'Hello! How can I help you today?' },
  ]);
  const [generalChatInput, setGeneralChatInput] = useState<string>('');
  const [isGeneralChatProcessing, setIsGeneralChatProcessing] = useState<boolean>(false);
  
  // Audio chat state from shared store
  const {
    selectedFile,
    chatMessages,
    currentMessage,
    isProcessing,
    setCurrentMessage,
    sendAudioCommand
  } = useAudioChatStore();

  // Scroll to the bottom of the chat history
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [generalConversation, chatMessages]);

  const handleGeneralChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const userInput = generalChatInput.trim();
    if (!userInput) return;

    const newUserMessage = { role: 'user', content: userInput };
    setGeneralConversation((prev) => [...prev, newUserMessage]);
    setGeneralChatInput('');
    setIsGeneralChatProcessing(true);

    // Add a loading indicator
    const loadingMessage = { role: 'assistant', content: 'Thinking...' };
    setGeneralConversation((prev) => [...prev, loadingMessage]);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/llm/chat/completion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...generalConversation, newUserMessage] }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const aiResponse = await response.json();
      
      // Remove loading indicator and add AI response
      setGeneralConversation((prev) => {
        const newConv = prev.slice(0, -1); // Remove loading message
        return [...newConv, { role: 'assistant', content: aiResponse.content }];
      });

    } catch (error: any) {
      console.error('Error during chat completion:', error);
      setGeneralConversation((prev) => {
        const newConv = prev.slice(0, -1); // Remove loading message
        return [...newConv, { role: 'assistant', content: `Sorry, an error occurred: ${error.message}` }];
      });
    } finally {
      setIsGeneralChatProcessing(false);
    }
  };

  const handleAudioChatSubmit = async () => {
    if (!currentMessage.trim()) return;
    
    const command = currentMessage;
    setCurrentMessage('');
    await sendAudioCommand(command);
  };

  const handleKeyDown = (e: React.KeyboardEvent, isAudioChat: boolean = false) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (isAudioChat) {
        handleAudioChatSubmit();
      } else {
        handleGeneralChatSubmit(e as any);
      }
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-4">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/audio')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Audio</span>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Full Chat Interface</h1>
            <p className="text-muted-foreground">
              Extended chat interface with both general and audio-specific conversations
            </p>
          </div>
        </div>
        <AudioContextIndicator />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Audio Chat Section */}
        <Card className="h-[600px] flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileAudio className="h-5 w-5" />
              <span>Audio Editing Chat</span>
            </CardTitle>
            <CardDescription>
              {selectedFile 
                ? `Working with: ${selectedFile.name}`
                : 'No audio file selected - go to Audio page to select a file'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-2">
              {chatMessages.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <FileAudio className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No audio chat history</p>
                  <p className="text-sm">Select an audio file to start editing with AI commands</p>
                </div>
              ) : (
                chatMessages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.type === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : message.type === 'system'
                          ? 'bg-blue-100 dark:bg-blue-900 border border-blue-200 dark:border-blue-800'
                          : 'bg-muted'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Processing your command...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex space-x-2">
              <Input
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, true)}
                placeholder={selectedFile ? "Type your audio editing command..." : "Select an audio file first"}
                disabled={!selectedFile || isProcessing}
                className="flex-1"
              />
              <Button
                onClick={handleAudioChatSubmit}
                disabled={!selectedFile || !currentMessage.trim() || isProcessing}
                size="sm"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* General Chat Section */}
        <Card className="h-[600px] flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span>General AI Chat</span>
            </CardTitle>
            <CardDescription>
              Chat with your AI assistant about anything
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <div ref={chatHistoryRef} className="flex-1 overflow-y-auto space-y-4 mb-4 p-2">
              {generalConversation.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isGeneralChatProcessing && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <form onSubmit={handleGeneralChatSubmit} className="flex space-x-2">
              <Input
                value={generalChatInput}
                onChange={(e) => setGeneralChatInput(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, false)}
                placeholder="Type your message..."
                disabled={isGeneralChatProcessing}
                className="flex-1"
              />
              <Button 
                type="submit" 
                disabled={!generalChatInput.trim() || isGeneralChatProcessing}
                size="sm"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};