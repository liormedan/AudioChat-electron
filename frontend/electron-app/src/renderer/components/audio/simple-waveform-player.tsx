import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Slider } from '../ui/slider';
import { Play, Pause, Square, SkipBack, SkipForward, Volume2, Radio } from 'lucide-react';

interface SimpleWaveformPlayerProps {
  audioFile: File | null;
  audioUrl: string | null;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
}

export const SimpleWaveformPlayer: React.FC<SimpleWaveformPlayerProps> = ({
  audioFile,
  audioUrl,
  onTimeUpdate,
  onPlayStateChange
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);
  const [audioData, setAudioData] = useState<number[]>([]);

  // Load audio and create simple waveform
  useEffect(() => {
    if (audioUrl && audioRef.current) {
      setIsLoading(true);
      audioRef.current.src = audioUrl;
      
      audioRef.current.onloadedmetadata = () => {
        const dur = audioRef.current?.duration || 0;
        setDuration(dur);
        setIsLoading(false);
        onTimeUpdate?.(0, dur);
        
        // Create simple waveform visualization
        createSimpleWaveform();
      };

      audioRef.current.ontimeupdate = () => {
        const current = audioRef.current?.currentTime || 0;
        setCurrentTime(current);
        onTimeUpdate?.(current, duration);
        drawWaveform();
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

  // Redraw waveform when time changes
  useEffect(() => {
    if (audioData.length > 0) {
      drawWaveform();
    }
  }, [currentTime, audioData]);

  const createSimpleWaveform = () => {
    // Create a more realistic waveform pattern
    const samples = 300;
    const data = [];
    
    for (let i = 0; i < samples; i++) {
      // Create a more natural waveform pattern
      const t = i / samples;
      const amplitude = Math.sin(t * Math.PI * 4) * 0.3 + 
                       Math.sin(t * Math.PI * 12) * 0.2 + 
                       Math.sin(t * Math.PI * 24) * 0.1 + 
                       (Math.random() - 0.5) * 0.2;
      data.push(Math.abs(amplitude) * 0.8 + 0.1);
    }
    
    setAudioData(data);
    setTimeout(() => drawWaveform(), 100); // Small delay to ensure canvas is ready
  };

  const drawWaveform = () => {
    const canvas = canvasRef.current;
    if (!canvas || audioData.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size to match display size
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const width = rect.width;
    const height = rect.height;
    const barWidth = width / audioData.length;
    const progress = duration > 0 ? currentTime / duration : 0;

    // Clear canvas with dark background
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, width, height);

    // Draw waveform bars
    audioData.forEach((value, index) => {
      const barHeight = value * height * 0.7;
      const x = index * barWidth;
      const y = (height - barHeight) / 2;

      // Color based on progress
      if (index / audioData.length <= progress) {
        ctx.fillStyle = '#3b82f6'; // Progress color (blue)
      } else {
        ctx.fillStyle = '#4a5568'; // Wave color (gray)
      }

      ctx.fillRect(x, y, Math.max(1, barWidth - 0.5), barHeight);
    });

    // Draw progress line
    const progressX = progress * width;
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(progressX, 0);
    ctx.lineTo(progressX, height);
    ctx.stroke();
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

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!audioRef.current || !canvasRef.current || duration === 0) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const progress = x / rect.width;
    const newTime = progress * duration;
    
    audioRef.current.currentTime = newTime;
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
        {/* Waveform Canvas */}
        <div className="relative">
          <canvas
            ref={canvasRef}
            className={`w-full border rounded cursor-pointer bg-gray-900 ${isLoading ? 'opacity-50' : ''}`}
            onClick={handleCanvasClick}
            style={{ height: '80px', width: '100%' }}
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