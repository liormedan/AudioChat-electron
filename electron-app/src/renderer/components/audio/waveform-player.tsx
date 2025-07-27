import React, { useEffect, useRef, useState, useCallback } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Slider } from '../ui/slider';
import { Play, Pause, Square, SkipBack, SkipForward, Volume2, Radio, Scissors, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

interface WaveformPlayerProps {
  audioFile: File | null;
  audioUrl: string | null;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
  onRegionSelect?: (start: number, end: number) => void;
  showSpectrogram?: boolean;
  enableRegions?: boolean;
  waveformHeight?: number;
  waveColor?: string;
  progressColor?: string;
}

export const WaveformPlayer: React.FC<WaveformPlayerProps> = ({
  audioFile,
  audioUrl,
  onTimeUpdate,
  onPlayStateChange,
  onRegionSelect,
  showSpectrogram = false,
  enableRegions = true,
  waveformHeight = 80,
  waveColor = '#6b7280',
  progressColor = '#3b82f6'
}) => {
  const waveformRef = useRef<HTMLDivElement>(null);
  const spectrogramRef = useRef<HTMLDivElement>(null);
  const wavesurfer = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [selectedRegion, setSelectedRegion] = useState<{start: number, end: number} | null>(null);

  const initializeWaveSurfer = useCallback(() => {
    if (!waveformRef.current) return;

    // Destroy existing instance
    if (wavesurfer.current) {
      wavesurfer.current.destroy();
      wavesurfer.current = null;
    }

    try {
      // Initialize WaveSurfer
      wavesurfer.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: waveColor,
        progressColor: progressColor,
        cursorColor: progressColor,
        barWidth: 2,
        barRadius: 1,
        height: showSpectrogram ? waveformHeight + 40 : waveformHeight,
        normalize: true,
        mediaControls: false,
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

    // Click to select regions (simplified implementation)
    wavesurfer.current.on('click', (relativeX: number) => {
      if (enableRegions && wavesurfer.current) {
        const duration = wavesurfer.current.getDuration();
        const clickTime = relativeX * duration;
        
        // Simple region selection: 5 seconds around click
        const start = Math.max(0, clickTime - 2.5);
        const end = Math.min(duration, clickTime + 2.5);
        
        setSelectedRegion({ start, end });
        onRegionSelect?.(start, end);
      }
    });

    return () => {
      wavesurfer.current?.destroy();
    };
  }, [enableRegions, showSpectrogram, onRegionSelect, waveformHeight, waveColor, progressColor]);

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

  useEffect(() => {
    if (wavesurfer.current) {
      wavesurfer.current.setPlaybackRate(playbackRate);
    }
  }, [playbackRate]);

  useEffect(() => {
    if (wavesurfer.current) {
      wavesurfer.current.zoom(zoom);
    }
  }, [zoom]);

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

  const handleSkipBack = () => {
    if (wavesurfer.current && audioUrl && duration > 0) {
      try {
        const current = wavesurfer.current.getCurrentTime();
        wavesurfer.current.seekTo(Math.max(0, current - 10) / duration);
      } catch (error) {
        console.error('Error skipping back:', error);
      }
    }
  };

  const handleSkipForward = () => {
    if (wavesurfer.current && audioUrl && duration > 0) {
      try {
        const current = wavesurfer.current.getCurrentTime();
        wavesurfer.current.seekTo(Math.min(duration, current + 10) / duration);
      } catch (error) {
        console.error('Error skipping forward:', error);
      }
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.5, 10));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.5, 1));
  };

  const handleZoomReset = () => {
    setZoom(1);
  };

  const handleClearRegions = () => {
    setSelectedRegion(null);
  };

  const handlePlayRegion = () => {
    if (selectedRegion && wavesurfer.current) {
      wavesurfer.current.play(selectedRegion.start, selectedRegion.end);
    }
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
          <span>Audio Waveform Player</span>
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
            'Upload an audio file to see the waveform'
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Waveform Container */}
        <div className="relative space-y-2">
          <div 
            ref={waveformRef} 
            className={`w-full border rounded ${isLoading ? 'opacity-50' : ''}`}
            style={{ minHeight: showSpectrogram ? `${waveformHeight + 40}px` : `${waveformHeight}px` }}
          >
            {!audioUrl && (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <div className="text-center">
                  <Radio className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Upload an audio file to see waveform</p>
                </div>
              </div>
            )}
          </div>
          
          {/* Spectrogram Container */}
          {showSpectrogram && audioUrl && (
            <div 
              ref={spectrogramRef}
              className="w-full border rounded"
              style={{ height: '100px' }}
            />
          )}
          
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/80 rounded">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                <span className="text-sm text-muted-foreground">Loading waveform...</span>
              </div>
            </div>
          )}
          
          {/* Region Info */}
          {selectedRegion && (
            <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
              Selected: {formatTime(selectedRegion.start)} - {formatTime(selectedRegion.end)} 
              ({formatTime(selectedRegion.end - selectedRegion.start)} duration)
            </div>
          )}
        </div>

        {/* Main Controls */}
        <div className="flex items-center space-x-2 flex-wrap gap-2">
          <div className="flex items-center space-x-1">
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
          </div>

          {/* Region Controls */}
          {enableRegions && (
            <div className="flex items-center space-x-1">
              <Button 
                size="sm" 
                variant="outline" 
                onClick={handlePlayRegion}
                disabled={!selectedRegion || isLoading}
                title="Play selected region"
              >
                <Scissors className="h-4 w-4" />
              </Button>
              
              <Button 
                size="sm" 
                variant="outline" 
                onClick={handleClearRegions}
                disabled={!selectedRegion || isLoading}
                title="Clear regions"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* Zoom Controls */}
          <div className="flex items-center space-x-1">
            <Button 
              size="sm" 
              variant="outline" 
              onClick={handleZoomOut}
              disabled={!audioUrl || isLoading || zoom <= 1}
              title="Zoom out"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            
            <Button 
              size="sm" 
              variant="outline" 
              onClick={handleZoomReset}
              disabled={!audioUrl || isLoading || zoom === 1}
              title="Reset zoom"
            >
              1x
            </Button>
            
            <Button 
              size="sm" 
              variant="outline" 
              onClick={handleZoomIn}
              disabled={!audioUrl || isLoading || zoom >= 10}
              title="Zoom in"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
          </div>

          {/* Time Display */}
          <div className="flex-1 text-center min-w-[120px]">
            <span className="text-sm text-muted-foreground">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>
        </div>

        {/* Secondary Controls */}
        <div className="flex items-center space-x-4">
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

          {/* Playback Speed */}
          <div className="flex items-center space-x-2 min-w-[120px]">
            <span className="text-xs text-muted-foreground">Speed:</span>
            <Slider
              value={[playbackRate]}
              onValueChange={(value) => setPlaybackRate(value[0] || 1)}
              max={2}
              min={0.25}
              step={0.25}
              className="flex-1"
            />
            <span className="text-xs text-muted-foreground w-8">
              {playbackRate}x
            </span>
          </div>
        </div>

        {/* Progress Bar (Alternative view) */}
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
      </CardContent>
    </Card>
  );
};