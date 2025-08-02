import React, { useState } from 'react';
import { CompactWaveformPlayer } from './compact-waveform-player';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Upload } from 'lucide-react';

export const CompactWaveformPlayerDemo: React.FC = () => {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleFileSelect = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'audio/*';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        setAudioFile(file);
        
        // Clean up previous URL
        if (audioUrl) {
          URL.revokeObjectURL(audioUrl);
        }
        
        // Create new URL
        const url = URL.createObjectURL(file);
        setAudioUrl(url);
      }
    };
    input.click();
  };

  const handleTimeUpdate = (current: number, dur: number) => {
    setCurrentTime(current);
    setDuration(dur);
  };

  const handlePlayStateChange = (playing: boolean) => {
    setIsPlaying(playing);
  };

  const clearFile = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioFile(null);
    setAudioUrl(null);
    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(false);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Compact Waveform Player Demo</CardTitle>
          <CardDescription>
            A compact waveform player with 300px total height, 120px waveform, and minimal controls
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Button onClick={handleFileSelect} variant="outline">
              <Upload className="h-4 w-4 mr-2" />
              Select Audio File
            </Button>
            {audioFile && (
              <Button onClick={clearFile} variant="outline">
                Clear File
              </Button>
            )}
          </div>

          <CompactWaveformPlayer
            audioFile={audioFile}
            audioUrl={audioUrl}
            onTimeUpdate={handleTimeUpdate}
            onPlayStateChange={handlePlayStateChange}
            height={300}
            waveformHeight={120}
            controlsHeight={60}
            infoHeight={120}
          />
        </CardContent>
      </Card>

      {audioFile && (
        <Card>
          <CardHeader>
            <CardTitle>Player State</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-medium">File Info:</p>
                <p className="text-muted-foreground">{audioFile.name}</p>
                <p className="text-muted-foreground">
                  {(audioFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
              <div>
                <p className="font-medium">Playback State:</p>
                <p className="text-muted-foreground">
                  Status: {isPlaying ? 'Playing' : 'Paused'}
                </p>
                <p className="text-muted-foreground">
                  Time: {Math.floor(currentTime)}s / {Math.floor(duration)}s
                </p>
                <p className="text-muted-foreground">
                  Progress: {duration > 0 ? Math.round((currentTime / duration) * 100) : 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Component Specifications</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Total Height:</span>
              <span className="font-mono">300px</span>
            </div>
            <div className="flex justify-between">
              <span>Waveform Height:</span>
              <span className="font-mono">120px</span>
            </div>
            <div className="flex justify-between">
              <span>Controls Height:</span>
              <span className="font-mono">60px</span>
            </div>
            <div className="flex justify-between">
              <span>Info Height:</span>
              <span className="font-mono">120px</span>
            </div>
            <div className="flex justify-between">
              <span>Spectrogram:</span>
              <span className="text-muted-foreground">Disabled (compact mode)</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};