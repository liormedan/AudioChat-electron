import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { MessageSquare, Loader2, Send, FileAudio } from 'lucide-react';
import { FileUploader } from '../components/audio/file-uploader';
import { SimpleWaveformPlayer } from '../components/audio/simple-waveform-player';
import { CommandSuggestions } from '../components/audio/command-suggestions';
import { AudioFileInfo } from '../components/audio/audio-file-info';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audioFile?: string;
  processingStatus?: 'pending' | 'processing' | 'completed' | 'error';
}

export const AudioPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  
  // Chat-related state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  


  useEffect(() => {
    if (audioUrl) {
      audioRef.current = new Audio(audioUrl);
      audioRef.current.onloadedmetadata = () => {
        setDuration(audioRef.current?.duration || 0);
      };
      audioRef.current.ontimeupdate = () => {
        setCurrentTime(audioRef.current?.currentTime || 0);
      };
      audioRef.current.onended = () => {
        setIsPlaying(false);
        setCurrentTime(0);
      };
    }
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, [audioUrl]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setAudioUrl(URL.createObjectURL(file));
      setIsPlaying(false);
      setCurrentTime(0);
      setDuration(0);
      // Clear previous transcription if needed
    }
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setCurrentTime(0);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setAudioUrl(URL.createObjectURL(file));
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    
    // Add file to uploaded files list
    setUploadedFiles(prev => [...prev, file]);
    
    // Add system message about file upload
    const systemMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'assistant',
      content: `Audio file "${file.name}" uploaded successfully! You can now give me editing commands like:
      
• "Remove background noise"
• "Increase volume by 20%"
• "Cut the first 30 seconds"
• "Add fade in and fade out effects"
• "Normalize the audio"

What would you like me to do with this audio?`,
      timestamp: new Date(),
      audioFile: file.name
    };
    
    setChatMessages(prev => [...prev, systemMessage]);
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setAudioUrl(null);
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || !selectedFile) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsProcessing(true);

    try {
      // Here we'll call the backend to process the audio command
      const response = await fetch('http://127.0.0.1:5000/api/audio/process-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          command: currentMessage,
          filename: selectedFile.name 
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: result.response || 'Audio processing completed successfully!',
        timestamp: new Date(),
        processingStatus: 'completed'
      };

      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Error processing command:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Sorry, I couldn't process that command. Error: ${error.message}`,
        timestamp: new Date(),
        processingStatus: 'error'
      };

      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCommandSelect = (command: string) => {
    setCurrentMessage(command);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Audio Chat Studio</h1>
        <p className="text-muted-foreground">
          Upload audio files and edit them using natural language commands
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - File Upload and Player */}
        <div className="space-y-6">
          {/* File Upload Area */}
          <FileUploader
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            onClearFile={handleClearFile}
          />

          {/* Simple Waveform Player */}
          <SimpleWaveformPlayer
            audioFile={selectedFile}
            audioUrl={audioUrl}
            onTimeUpdate={(current, dur) => {
              setCurrentTime(current);
              setDuration(dur);
            }}
            onPlayStateChange={setIsPlaying}
          />

          {/* File Information */}
          {selectedFile && (
            <AudioFileInfo
              file={selectedFile}
              duration={duration}
            />
          )}
        </div>

        {/* Right Column - Chat Interface */}
        <div className="space-y-6">
          {/* Command Suggestions */}
          {selectedFile && (
            <CommandSuggestions
              onCommandSelect={handleCommandSelect}
              disabled={isProcessing}
            />
          )}

          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5" />
                <span>Audio Editing Chat</span>
              </CardTitle>
              <CardDescription>
                Give me commands to edit your audio file
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-2">
                {chatMessages.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    <FileAudio className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Upload an audio file to start editing with AI commands</p>
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

              {/* Chat Input */}
              <div className="flex space-x-2">
                <Input
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={selectedFile ? "Type your editing command..." : "Upload an audio file first"}
                  disabled={!selectedFile || isProcessing}
                  className="flex-1"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!selectedFile || !currentMessage.trim() || isProcessing}
                  size="sm"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};