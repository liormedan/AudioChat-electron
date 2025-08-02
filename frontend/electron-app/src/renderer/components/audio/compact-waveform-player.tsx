import React, { useEffect, useRef, useState, useCallback } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Slider } from '../ui/slider';
import { Play, Pause, Square, Volume2, FileAudio } from 'lucide-react';
import { cn } from '../../lib/utils';
import './compact-waveform-player.css';

interface CompactWaveformPlayerProps {
  audioFile: File | null;
  audioUrl: string | null;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
  height?: number;
  waveformHeight?: number;
  controlsHeight?: number;
  infoHeight?: number;
  showSpectrogram?: boolean;
  waveColor?: string;
  progressColor?: string;
}

export const CompactWaveformPlayer: React.FC<CompactWaveformPlayerProps> = ({
  audioFile,
  audioUrl,
  onTimeUpdate,
  onPlayStateChange,
  height = 300,
  waveformHeight = 120,
  controlsHeight = 60,
  infoHeight = 120,
  showSpectrogram = false, // Always false for compact mode
  waveColor = '#6b7280',
  progressColor = '#3b82f6'
}) => {
  const waveformRef = useRef<HTMLDivElement>(null);
  const wavesurfer = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);

  const initializeWaveSurfer = useCallback(() => {
    if (!waveformRef.current) return;

    // Destroy existing instance
    if (wavesurfer.current) {
      wavesurfer.current.destroy();
      wavesurfer.current = null;
    }

    try {
      // Initialize WaveSurfer with compact settings
      wavesurfer.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: waveColor,
        progressColor: progressColor,
        cursorColor: progressColor,
        barWidth: 1,
        barRadius: 0,
        height: waveformHeight,
        normalize: true,
        mediaControls: false,
        responsive: true,
      });
    } catch (error) {
      console.error('Failed to initialize WaveSurfer:', error);
      return;
    }

    // Event listeners
    wavesurfer.current.on('ready', () => {
      setIsLoading(false);
      const dur = wavesurfer.current?.getDuration() || 0;
      setDuration(dur);
      onTimeUpdate?.(0, dur);
    });

    wavesurfer.current.on('audioprocess', () => {
      const current = wavesurfer.current?.getCurrentTime() || 0;
      setCurrentTime(current);
      onTimeUpdate?.(current, duration);
    });

    wavesurfer.current.on('play', () => {
      setIsPlaying(true);
      onPlayStateChange?.(true);
    });

    wavesurfer.current.on('pause', () => {
      setIsPlaying(false);
      onPlayStateChange?.(false);
    });

    wavesurfer.current.on('finish', () => {
      setIsPlaying(false);
      setCurrentTime(0);
      onPlayStateChange?.(false);
    });

    return () => {
      wavesurfer.current?.destroy();
    };
  }, [waveformHeight, waveColor, progressColor, onTimeUpdate, onPlayStateChange]);

  // Initialize WaveSurfer when component mounts
  useEffect(() => {
    initializeWaveSurfer();
    return () => {
      if (wavesurfer.current) {
        wavesurfer.current.destroy();
      }
    };
  }, [initializeWaveSurfer]);

  useEffect(() => {
    if (audioUrl && wavesurfer.current) {
      setIsLoading(true);
      try {
        wavesurfer.current.load(audioUrl);
      } catch (error) {
        console.error('Failed to load audio:', error);
        setIsLoading(false);
      }
    }
  }, [audioUrl]);

  useEffect(() => {
    if (wavesurfer.current) {
      wavesurfer.current.setVolume(volume);
    }
  }, [volume]);

  const handlePlayPause = () => {
    if (wavesurfer.current && audioUrl) {
      try {
        wavesurfer.current.playPause();
      } catch (error) {
        console.error('Error playing/pausing:', error);
      }
    }
  };

  const handleStop = () => {
    if (wavesurfer.current && audioUrl) {
      try {
        wavesurfer.current.stop();
        setCurrentTime(0);
      } catch (error) {
        console.error('Error stopping:', error);
      }
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + sizes[i];
  };

  const getFileName = (fileName: string, maxLength: number = 25) => {
    if (fileName.length <= maxLength) return fileName;
    const extension = fileName.split('.').pop();
    const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
    const truncated = nameWithoutExt.substring(0, maxLength - extension!.length - 4) + '...';
    return `${truncated}.${extension}`;
  };

  return (
    <Card className="w-full compact-waveform-player" style={{ height }}>
      <CardContent className="p-3 h-full flex flex-col">
        {/* File Info Section */}
        <div className="flex-shrink-0 mb-3" style={{ height: `${infoHeight}px` }}>
          {audioFile ? (
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <FileAudio className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-sm truncate" title={audioFile.name}>
                    {getFileName(audioFile.name)}
                  </p>
                  <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                    <span>{formatFileSize(audioFile.size)}</span>
                    <span>•</span>
                    <span>{formatTime(duration)}</span>
                    <span>•</span>
                    <span>{audioFile.type.split('/')[1]?.toUpperCase() || 'AUDIO'}</span>
                  </div>
                </div>
              </div>
              
              {/* Progress indicator */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{formatTime(currentTime)}</span>
                  <span>{duration > 0 ? Math.round((currentTime / duration) * 100) : 0}%</span>
                  <span>{formatTime(duration)}</span>
                </div>
                <div className="w-full bg-muted rounded-full h-1">
                  <div
                    className="bg-primary h-1 rounded-full transition-all duration-100"
                    style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <FileAudio className="h-6 w-6 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No audio file selected</p>
              </div>
            </div>
          )}
        </div>

        {/* Waveform Section */}
        <div className="flex-1 relative mb-3">
          <div 
            ref={waveformRef} 
            className={cn(
              "w-full border rounded bg-muted/20",
              isLoading && "opacity-50"
            )}
            style={{ height: `${waveformHeight}px` }}
          >
            {!audioUrl && (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <div className="text-center">
                  <div className="w-full h-8 bg-muted rounded mb-2 opacity-30"></div>
                  <p className="text-xs">Waveform will appear here</p>
                </div>
              </div>
            )}
          </div>
          
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/80 rounded">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary"></div>
                <span className="text-xs text-muted-foreground">Loading...</span>
              </div>
            </div>
          )}
        </div>

        {/* Controls Section */}
        <div className="flex-shrink-0" style={{ height: `${controlsHeight}px` }}>
          <div className="flex items-center justify-between space-x-2">
            {/* Playback Controls */}
            <div className="flex items-center space-x-1">
              <Button 
                size="sm" 
                variant="outline" 
                onClick={handlePlayPause}
                disabled={!audioUrl || isLoading}
                className="h-8 w-8 p-0"
              >
                {isPlaying ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
              </Button>
              
              <Button 
                size="sm" 
                variant="outline" 
                onClick={handleStop}
                disabled={!audioUrl || isLoading}
                className="h-8 w-8 p-0"
              >
                <Square className="h-3 w-3" />
              </Button>
            </div>

            {/* Volume Control */}
            <div className="flex items-center space-x-2 flex-1 max-w-[120px]">
              <Volume2 className="h-3 w-3 text-muted-foreground flex-shrink-0" />
              <Slider
                value={[volume]}
                onValueChange={(value) => setVolume(value[0] || 0.7)}
                max={1}
                min={0}
                step={0.1}
                className="flex-1"
                disabled={!audioUrl || isLoading}
              />
              <span className="text-xs text-muted-foreground w-8 text-right">
                {Math.round(volume * 100)}%
              </span>
            </div>

            {/* Status */}
            <div className="text-xs text-muted-foreground">
              {isLoading ? 'Loading...' : isPlaying ? 'Playing' : audioUrl ? 'Ready' : 'No file'}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};