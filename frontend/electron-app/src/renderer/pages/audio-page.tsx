import React, { useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { MessageSquare, Loader2, Send, FileAudio, ExternalLink } from 'lucide-react';
import { FileUploader } from '../components/audio/file-uploader';
import { SimpleWaveformPlayer } from '../components/audio/simple-waveform-player';
import { CommandSuggestions } from '../components/audio/command-suggestions';
import { AudioFileInfo } from '../components/audio/audio-file-info';
import { AudioWorkspace } from '../components/audio/audio-workspace';
import { AudioContextIndicator } from '../components/audio/audio-context-indicator';
import { AudioMetadataViewer } from '../components/audio/audio-metadata-viewer';
import { useAudioChatStore, type AudioFile } from '../stores/audio-chat-store';
import { useNavigate } from 'react-router-dom';

export const AudioPage: React.FC = () => {
  const navigate = useNavigate();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  // Use shared store
  const {
    selectedFile,
    isPlaying,
    currentTime,
    duration,
    chatMessages,
    currentMessage,
    isProcessing,
    isUploading,
    uploadProgress,
    setSelectedFile,
    addUploadedFile,
    setPlayingState,
    setCurrentTime,
    setDuration,
    setCurrentMessage,
    selectFileAndNotifyChat,
    sendAudioCommand,
    uploadFileToServer
  } = useAudioChatStore();
  


  useEffect(() => {
    if (selectedFile?.url) {
      audioRef.current = new Audio(selectedFile.url);
      audioRef.current.onloadedmetadata = () => {
        setDuration(audioRef.current?.duration || 0);
      };
      audioRef.current.ontimeupdate = () => {
        setCurrentTime(audioRef.current?.currentTime || 0);
      };
      audioRef.current.onended = () => {
        setPlayingState(false);
        setCurrentTime(0);
      };
    }
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, [selectedFile?.url, setDuration, setCurrentTime, setPlayingState]);

  const createAudioFile = (file: File): AudioFile => ({
    id: Date.now().toString(),
    file,
    name: file.name,
    url: URL.createObjectURL(file),
    metadata: {
      size: file.size,
      type: file.type,
      lastModified: file.lastModified
    }
  });

  const handleFileSelect = async (file: File) => {
    // Create local audio file first
    const localAudioFile = createAudioFile(file);
    addUploadedFile(localAudioFile);
    selectFileAndNotifyChat(localAudioFile);
    setPlayingState(false);
    setCurrentTime(0);
    setDuration(0);
    
    // Upload to server in background
    const uploadedFile = await uploadFileToServer(file);
    if (uploadedFile) {
      // Update the selected file with server info
      addUploadedFile(uploadedFile);
      selectFileAndNotifyChat(uploadedFile);
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setPlayingState(false);
    setCurrentTime(0);
    setDuration(0);
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;
    
    const command = currentMessage;
    setCurrentMessage('');
    await sendAudioCommand(command);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
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
      <div className="space-y-4">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Audio Chat Studio</h1>
          <p className="text-muted-foreground">
            Upload audio files and edit them using natural language commands
          </p>
        </div>
        <AudioContextIndicator />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Left Column - File Management */}
        <div className="space-y-6">
          <AudioWorkspace />
        </div>

        {/* Middle Column - File Upload and Player */}
        <div className="space-y-6">
          {/* File Upload Area */}
          <FileUploader
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            onClearFile={handleClearFile}
          />

          {/* Simple Waveform Player */}
          <SimpleWaveformPlayer
            audioFile={selectedFile?.file || null}
            audioUrl={selectedFile?.url || null}
            onTimeUpdate={(current, dur) => {
              setCurrentTime(current);
              setDuration(dur);
            }}
            onPlayStateChange={setPlayingState}
          />

          {/* File Information */}
          {selectedFile && (
            <AudioFileInfo
              file={selectedFile.file}
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
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-5 w-5" />
                  <span>Audio Editing Chat</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/chat')}
                  className="flex items-center space-x-1"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span>Full Chat</span>
                </Button>
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
                {isUploading && (
                  <div className="flex justify-start">
                    <div className="bg-blue-100 dark:bg-blue-900 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                        <span>Uploading file... {Math.round(uploadProgress)}%</span>
                      </div>
                      <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-2 mt-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
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
                  onKeyDown={handleKeyDown}
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

        {/* Far Right Column - Metadata Analysis */}
        <div className="space-y-6">
          <AudioMetadataViewer 
            fileId={selectedFile?.serverFileId || null}
            fileName={selectedFile?.name}
          />
        </div>
      </div>
    </div>
  );
};