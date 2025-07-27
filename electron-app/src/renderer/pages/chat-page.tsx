import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { MessageSquare, FileAudio, ArrowLeft, Loader2, Send, Upload, Play, Pause, Volume2, BarChart3, Info } from 'lucide-react';
import { useAudioChatStore } from '../stores/audio-chat-store';
import { AudioContextIndicator } from '../components/audio/audio-context-indicator';
import { AudioMetadataService } from '../services/audio-metadata-service';
import { useNavigate } from 'react-router-dom';

export const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // General chat state (separate from audio chat)
  const [generalConversation, setGeneralConversation] = useState<{ role: string; content: string }[]>([
    { role: 'assistant', content: 'Hello! How can I help you today?' },
  ]);
  const [generalChatInput, setGeneralChatInput] = useState<string>('');
  const [isGeneralChatProcessing, setIsGeneralChatProcessing] = useState<boolean>(false);
  
  // Audio metadata service
  const [metadataService] = useState(() => new AudioMetadataService());
  const [showMetadata, setShowMetadata] = useState<boolean>(false);
  const [audioMetadata, setAudioMetadata] = useState<any>(null);
  
  // Audio chat state from shared store
  const {
    selectedFile,
    uploadedFiles,
    chatMessages,
    currentMessage,
    isProcessing,
    isUploading,
    uploadProgress,
    setCurrentMessage,
    sendAudioCommand,
    uploadFileToServer,
    addUploadedFile,
    selectFileAndNotifyChat,
    setSelectedFile
  } = useAudioChatStore();

  // Scroll to the bottom of the chat history
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [generalConversation, chatMessages]);

  // Load metadata when file is selected
  useEffect(() => {
    if (selectedFile?.serverFileId) {
      loadAudioMetadata(selectedFile.serverFileId);
    }
  }, [selectedFile]);

  const loadAudioMetadata = async (fileId: string) => {
    try {
      const summary = await metadataService.getAudioSummary(fileId);
      if (summary.success) {
        setAudioMetadata(summary);
      }
    } catch (error) {
      console.error('Failed to load metadata:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const uploadedFile = await uploadFileToServer(file);
    if (uploadedFile) {
      addUploadedFile(uploadedFile);
      selectFileAndNotifyChat(uploadedFile);
    }
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = Array.from(e.dataTransfer.files);
    const audioFile = files.find(file => file.type.startsWith('audio/'));
    
    if (audioFile) {
      const uploadedFile = await uploadFileToServer(audioFile);
      if (uploadedFile) {
        addUploadedFile(uploadedFile);
        selectFileAndNotifyChat(uploadedFile);
      }
    }
  };

  const getQuickCommands = () => [
    "Show me the audio metadata",
    "Remove background noise",
    "Increase volume by 20%",
    "Normalize the audio",
    "Add fade in and fade out effects",
    "Cut the first 30 seconds",
    "Extract the middle 2 minutes",
    "Convert to mono",
    "Apply low-pass filter",
    "Analyze the frequency spectrum"
  ];

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
    
    const command = currentMessage.trim().toLowerCase();
    setCurrentMessage('');
    
    // Handle metadata commands locally
    if (command.includes('metadata') || command.includes('show me') || command.includes('analyze')) {
      await handleMetadataCommand(command);
    } else {
      await sendAudioCommand(currentMessage);
    }
  };

  const handleMetadataCommand = async (command: string) => {
    if (!selectedFile?.serverFileId) {
      return;
    }

    const { addChatMessage, setProcessing } = useAudioChatStore.getState();

    try {
      const userMessage = {
        id: Date.now().toString(),
        type: 'user' as const,
        content: command,
        timestamp: new Date()
      };
      
      // Add user message to chat
      addChatMessage(userMessage);

      // Add processing indicator
      const processingMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant' as const,
        content: '🔍 Analyzing audio file... This may take a moment.',
        timestamp: new Date(),
        processingStatus: 'processing' as const
      };
      addChatMessage(processingMessage);
      setProcessing(true);

      // Get comprehensive metadata
      const metadata = await metadataService.getAdvancedMetadata(selectedFile.serverFileId, true);
      
      // Remove processing message
      const currentMessages = useAudioChatStore.getState().chatMessages;
      const filteredMessages = currentMessages.filter(msg => msg.id !== processingMessage.id);
      useAudioChatStore.setState({ chatMessages: filteredMessages });
      
      if (metadata.success) {
        const formatted = metadataService.formatMetadataForDisplay(metadata);
        let response = `📊 **Audio Analysis Complete**\n\n`;
        response += `**File:** ${metadata.file_info.file_name}\n`;
        response += `**Size:** ${metadata.file_info.file_size_mb} MB\n`;
        response += `**Duration:** ${metadata.audio_properties.duration_formatted}\n\n`;
        
        Object.entries(formatted).forEach(([category, data]) => {
          if (typeof data === 'object' && data !== null && category !== 'File Information') {
            response += `**${category}:**\n`;
            Object.entries(data).forEach(([key, value]) => {
              response += `• ${key}: ${value}\n`;
            });
            response += '\n';
          }
        });

        const assistantMessage = {
          id: Date.now().toString(),
          type: 'assistant' as const,
          content: response,
          timestamp: new Date(),
          processingStatus: 'completed' as const
        };
        
        addChatMessage(assistantMessage);
      } else {
        const errorMessage = {
          id: Date.now().toString(),
          type: 'assistant' as const,
          content: `❌ **Analysis Failed**\n\nError: ${metadata.error}\n\nPlease try again or check if the file is properly uploaded.`,
          timestamp: new Date(),
          processingStatus: 'error' as const
        };
        
        addChatMessage(errorMessage);
      }
    } catch (error) {
      console.error('Error handling metadata command:', error);
      
      const errorMessage = {
        id: Date.now().toString(),
        type: 'assistant' as const,
        content: `❌ **Unexpected Error**\n\n${error instanceof Error ? error.message : 'Unknown error occurred'}\n\nPlease try again.`,
        timestamp: new Date(),
        processingStatus: 'error' as const
      };
      
      const { addChatMessage } = useAudioChatStore.getState();
      addChatMessage(errorMessage);
    } finally {
      setProcessing(false);
    }
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
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileAudio className="h-5 w-5" />
                <span>Audio Editing Chat</span>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="audio/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                >
                  <Upload className="h-4 w-4 mr-1" />
                  Upload
                </Button>
                {selectedFile && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowMetadata(!showMetadata)}
                  >
                    <Info className="h-4 w-4 mr-1" />
                    Info
                  </Button>
                )}
              </div>
            </CardTitle>
            <CardDescription className="space-y-2">
              {selectedFile ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span>Working with: <strong>{selectedFile.name}</strong></span>
                    <div className="flex items-center space-x-2">
                      <Badge variant={selectedFile.serverFileId ? "default" : "secondary"}>
                        {selectedFile.serverFileId ? "Uploaded" : "Local"}
                      </Badge>
                      {isProcessing && (
                        <Badge variant="outline" className="animate-pulse">
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                          Processing
                        </Badge>
                      )}
                    </div>
                  </div>
                  {audioMetadata && (
                    <div className="text-sm text-muted-foreground flex items-center space-x-4">
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {audioMetadata.duration}
                      </span>
                      <span className="flex items-center">
                        <Volume2 className="h-3 w-3 mr-1" />
                        {audioMetadata.file_size}
                      </span>
                      <span className="flex items-center">
                        <BarChart3 className="h-3 w-3 mr-1" />
                        {audioMetadata.tempo}
                      </span>
                    </div>
                  )}
                  {isUploading && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="flex items-center">
                          <Upload className="h-3 w-3 mr-1 animate-bounce" />
                          Uploading...
                        </span>
                        <span>{Math.round(uploadProgress)}%</span>
                      </div>
                      <Progress value={uploadProgress} className="h-2" />
                    </div>
                  )}
                </div>
              ) : (
                <div 
                  className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-4 text-center cursor-pointer hover:border-muted-foreground/50 transition-colors"
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <FileAudio className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Drop an audio file here or click to upload
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Supports: MP3, WAV, FLAC, OGG, AAC, M4A
                  </p>
                </div>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-2">
              {chatMessages.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <FileAudio className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No audio chat history</p>
                  {selectedFile ? (
                    <div className="mt-4 space-y-2">
                      <p className="text-sm font-medium">Try these commands:</p>
                      <div className="flex flex-wrap gap-2 justify-center">
                        {getQuickCommands().slice(0, 4).map((command, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentMessage(command)}
                            className="text-xs"
                          >
                            {command}
                          </Button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm">Upload an audio file to start editing with AI commands</p>
                  )}
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
                      <p className="whitespace-pre-wrap text-sm">{message.content}</p>
                      <div className="flex items-center justify-between mt-2">
                        <p className="text-xs opacity-70">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                        {message.processingStatus && (
                          <Badge 
                            variant={message.processingStatus === 'completed' ? 'default' : 
                                   message.processingStatus === 'error' ? 'destructive' : 'secondary'}
                            className="text-xs"
                          >
                            {message.processingStatus}
                          </Badge>
                        )}
                      </div>
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

            {/* Quick Commands */}
            {selectedFile && chatMessages.length > 0 && (
              <div className="mb-2">
                <div className="flex flex-wrap gap-1">
                  {getQuickCommands().slice(0, 6).map((command, index) => (
                    <Button
                      key={index}
                      variant="ghost"
                      size="sm"
                      onClick={() => setCurrentMessage(command)}
                      className="text-xs h-6 px-2"
                    >
                      {command.length > 20 ? command.substring(0, 20) + '...' : command}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex space-x-2">
              <Input
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, true)}
                placeholder={selectedFile ? "Type your audio editing command..." : "Upload an audio file first"}
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