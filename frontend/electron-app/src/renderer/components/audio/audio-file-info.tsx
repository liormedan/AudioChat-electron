import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { FileAudio, Clock, HardDrive, FileType } from 'lucide-react';

interface AudioFileInfoProps {
  file: File;
  duration?: number;
}

export const AudioFileInfo: React.FC<AudioFileInfoProps> = ({ file, duration }) => {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number) => {
    if (!seconds || seconds === 0) return 'Unknown';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const getFileExtension = (filename: string) => {
    return filename.split('.').pop()?.toUpperCase() || 'Unknown';
  };

  const getAudioFormat = (mimeType: string) => {
    const formats: Record<string, string> = {
      'audio/mpeg': 'MP3',
      'audio/wav': 'WAV',
      'audio/flac': 'FLAC',
      'audio/ogg': 'OGG',
      'audio/mp4': 'M4A',
      'audio/aac': 'AAC'
    };
    return formats[mimeType] || getFileExtension(file.name);
  };

  const getQualityBadge = (size: number, duration: number) => {
    if (!duration || duration === 0) return null;
    
    const bitrate = (size * 8) / duration / 1000; // kbps approximation
    
    if (bitrate > 256) return <Badge variant="default">High Quality</Badge>;
    if (bitrate > 128) return <Badge variant="secondary">Standard Quality</Badge>;
    return <Badge variant="outline">Basic Quality</Badge>;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileAudio className="h-4 w-4" />
          <span>File Information</span>
        </CardTitle>
        <CardDescription>
          Details about your uploaded audio file
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* File Name */}
          <div className="space-y-2">
            <div className="font-medium text-sm">File Name</div>
            <div className="text-sm text-muted-foreground break-all">
              {file.name}
            </div>
          </div>

          {/* File Stats Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-sm font-medium">
                <HardDrive className="h-3 w-3" />
                <span>Size</span>
              </div>
              <div className="text-sm text-muted-foreground">
                {formatFileSize(file.size)}
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-sm font-medium">
                <Clock className="h-3 w-3" />
                <span>Duration</span>
              </div>
              <div className="text-sm text-muted-foreground">
                {formatDuration(duration || 0)}
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-sm font-medium">
                <FileType className="h-3 w-3" />
                <span>Format</span>
              </div>
              <div className="text-sm text-muted-foreground">
                {getAudioFormat(file.type)}
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium">Quality</div>
              <div>
                {getQualityBadge(file.size, duration || 0) || (
                  <Badge variant="outline">Unknown</Badge>
                )}
              </div>
            </div>
          </div>

          {/* Last Modified */}
          <div className="space-y-2">
            <div className="font-medium text-sm">Last Modified</div>
            <div className="text-sm text-muted-foreground">
              {new Date(file.lastModified).toLocaleString()}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};