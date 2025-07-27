import React from 'react';
import { Card, CardContent } from '../ui/card';
import { FileAudio, Clock, Volume2 } from 'lucide-react';
import { useAudioChatStore } from '../../stores/audio-chat-store';

export const AudioContextIndicator: React.FC = () => {
  const { selectedFile, duration, chatMessages } = useAudioChatStore();

  if (!selectedFile) {
    return null;
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const formatFileSize = (bytes: number) => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  const audioMessages = chatMessages.filter(msg => msg.type !== 'system').length;

  return (
    <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
      <CardContent className="p-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <FileAudio className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            <span className="font-medium text-sm">{selectedFile.name}</span>
          </div>
          
          {duration > 0 && (
            <div className="flex items-center space-x-1 text-sm text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{formatTime(duration)}</span>
            </div>
          )}
          
          {selectedFile.metadata && (
            <div className="flex items-center space-x-1 text-sm text-muted-foreground">
              <Volume2 className="h-3 w-3" />
              <span>{formatFileSize(selectedFile.metadata.size)}</span>
            </div>
          )}
          
          {audioMessages > 0 && (
            <div className="text-sm text-blue-600 dark:text-blue-400">
              {audioMessages} chat message{audioMessages !== 1 ? 's' : ''}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};