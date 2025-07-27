import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Slider } from '../ui/slider';
import { Play, Pause, Square, SkipBack, SkipForward, Volume2, Radio } from 'lucide-react';

interface BasicAudioPlayerProps {
  audioFile: File | null;
  audioUrl: string | null;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
}

export const BasicAudioPlayer: React.FC<BasicAudioPlayerProps> = ({
  audioFile,
  audioUrl,
  onTimeUpdate,
  onPlayStateChange
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const waveformRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);

  // Load audio
  useEffect(() => {
    if (audioUrl && audioRef.current) {
      setIsLoading(true);
      audioRef.current.src = audioUrl;
      
      audioRef.current.onloadedmetadata = () => {
        const dur = audioRef.current?.duration || 0;
        setDuration(dur);
        setIsLoading(false);
        onTimeUpdate?.(0, dur);
        createWaveformBars();
      };

      audioRef.current.ontimeupdate = () => {
        const current = audioRef.current?.currentTime || 0;
        setCurrentTime(current);
        onTimeUpdate?.(current, duration);
        updateWaveformProgress();
      };

      audioRef.current.onplay = () => {
        setIsPlaying(true);
        onPlayStateChange?.(true);
      };

      audioRef.current.onpause = () => {
        setIsPlaying(false);
        onPlayStateChange?.(false);
      };

      audioRef.current.onended = () => {
        setIsPlaying(false);
        setCurrentTime(0);
        onPlayStateChange?.(false);
      };
    }
  }, [audioUrl]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  const createWaveformBars = () => {
    if (!waveformRef.current) return;

    // Clear existing bars
    waveformRef.current.innerHTML = '';

    // Create 100 bars for waveform visualization
    const numBars = 100;
    for (let i = 0; i < numBars; i++) {
      const bar = document.createElement('div');
      bar.className = 'waveform-bar';
      
      // Random height for each bar (simulating waveform)
      const height = Math.random() * 60 + 10; // 10-70px height
      
      bar.style.cssText = `
        width: calc(100% / ${numBars} - 1px);
        height: ${height}px;
        background-color: #6b7280;
        display: inline-block;
        margin-right: 1px;
        border-radius: 1px;
        transition: background-color 0.3s ease;
        cursor: pointer;
      `;
      
      // Add click handler for seeking
      bar.addEventListener('click', () => {
        if (audioRef.current && duration > 0) {
          const newTime = (i / numBars) * duration;
          audioRef.current.currentTime = newTime;
        }
      });
      
      waveformRef.current.appendChild(bar);
    }
  };

  const updateWaveformProgress = () => {
    if (!waveformRef.current || duration === 0) return;

    const progress = currentTime / duration;
    const bars = waveformRef.current.children;
    
    for (let i = 0; i < bars.length; i++) {
      const bar = bars[i] as HTMLElement;
      if (i / bars.length <= progress) {
        bar.style.backgroundColor = '#3b82f6'; // Blue for played
      } else {
        bar.style.backgroundColor = '#6b7280'; // Gray for unplayed
      }
    }
  };

  const handlePlayPause = () => {
    if (!audioRef.current) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
  };

  const handleStop = () => {
    if (!audioRef.current) return;
    
    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    setCurrentTime(0);
  };

  const handleSkipBack = () => {
    if (!audioRef.current) return;
    
    audioRef.current.currentTime = Math.max(0, audioRef.current.currentTime - 10);
  };

  const handleSkipForward = () => {
    if (!audioRef.current) return;
    
    audioRef.current.currentTime = Math.min(duration, audioRef.current.currentTime + 10);
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const getFileInfo = () => {
    if (!audioFile) return null;
    
    const sizeInMB = (audioFile.size / (1024 * 1024)).toFixed(2);
    return {
      name: audioFile.name,
      size: `${sizeInMB} MB`,
      type: audioFile.type || 'Unknown'
    };
  };

  const fileInfo = getFileInfo();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Radio className="h-5 w-5" />
          <span>Audio Player</span>
        </CardTitle>
        <CardDescription>
          {fileInfo ? (
            <div className="flex items-center space-x-4 text-sm">
              <span>{fileInfo.name}</span>
              <span>•</span>
              <span>{fileInfo.size}</span>
              <span>•</span>
              <span>{formatTime(duration)}</span>
            </div>
          ) : (
            'Upload an audio file to play'
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Waveform Container */}
        <div className="relative">
          <div
            ref={waveformRef}
            className={`w-full border rounded p-2 bg-gray-900 ${isLoading ? 'opacity-50' : ''}`}
            style={{ 
              height: '80px', 
              display: 'flex', 
              alignItems: 'end',
              overflow: 'hidden'
            }}
          />
          
          {!audioUrl && (
            <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <Radio className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Upload an audio file to see waveform</p>
              </div>
            </div>
          )}
          
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/80 rounded">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                <span className="text-sm text-muted-foreground">Loading audio...</span>
              </div>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-2">
          <Button 
            size="sm" 
            variant="outline" 
            onClick={handleSkipBack}
            disabled={!audioUrl || isLoading}
            title="Skip back 10s"
          >
            <SkipBack className="h-4 w-4" />
          </Button>
          
          <Button 
            size="sm" 
            variant="outline" 
            onClick={handlePlayPause}
            disabled={!audioUrl || isLoading}
          >
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          
          <Button 
            size="sm" 
            variant="outline" 
            onClick={handleStop}
            disabled={!audioUrl || isLoading}
          >
            <Square className="h-4 w-4" />
          </Button>
          
          <Button 
            size="sm" 
            variant="outline" 
            onClick={handleSkipForward}
            disabled={!audioUrl || isLoading}
            title="Skip forward 10s"
          >
            <SkipForward className="h-4 w-4" />
          </Button>

          {/* Time Display */}
          <div className="flex-1 text-center">
            <span className="text-sm text-muted-foreground">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          {/* Volume Control */}
          <div className="flex items-center space-x-2 min-w-[120px]">
            <Volume2 className="h-4 w-4 text-muted-foreground" />
            <Slider
              value={[volume]}
              onValueChange={(value) => setVolume(value[0] || 0.7)}
              max={1}
              min={0}
              step={0.1}
              className="flex-1"
            />
            <span className="text-xs text-muted-foreground w-8">
              {Math.round(volume * 100)}%
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Progress</span>
            <span>{duration > 0 ? Math.round((currentTime / duration) * 100) : 0}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-1">
            <div
              className="bg-primary h-1 rounded-full transition-all duration-100"
              style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
            />
          </div>
        </div>

        {/* Hidden audio element */}
        <audio ref={audioRef} style={{ display: 'none' }} />
      </CardContent>
    </Card>
  );
};