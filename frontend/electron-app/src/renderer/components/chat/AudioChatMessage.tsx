import React, { useRef, useEffect, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, Volume2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Slider } from '../ui/slider';

interface AudioChatMessageProps {
  audioUrl: string;
  fileName: string;
}

export const AudioChatMessage: React.FC<AudioChatMessageProps> = ({ audioUrl, fileName }) => {
  const waveformRef = useRef<HTMLDivElement>(null);
  const wavesurfer = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.5);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    if (waveformRef.current) {
      wavesurfer.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: '#A8A29E', // gray-400
        progressColor: '#8B5CF6', // violet-500
        cursorColor: '#7C3AED', // violet-600
        barWidth: 2,
        barRadius: 3,
        height: 50,
        normalize: true,
      });

      wavesurfer.current.load(audioUrl);

      wavesurfer.current.on('ready', () => {
        setDuration(wavesurfer.current?.getDuration() || 0);
        wavesurfer.current?.setVolume(volume);
      });

      wavesurfer.current.on('play', () => setIsPlaying(true));
      wavesurfer.current.on('pause', () => setIsPlaying(false));
      wavesurfer.current.on('timeupdate', (time) => setCurrentTime(time));
      wavesurfer.current.on('finish', () => setIsPlaying(false));
    }

    return () => {
      wavesurfer.current?.destroy();
    };
  }, [audioUrl]);

  const handlePlayPause = () => {
    if (wavesurfer.current) {
      wavesurfer.current.playPause();
    }
  };

  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0] ?? 0.5;
    setVolume(newVolume);
    if (wavesurfer.current) {
      wavesurfer.current.setVolume(newVolume);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="w-full bg-card p-3 rounded-lg shadow-sm border border-border hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-foreground truncate" title={fileName}>
          {fileName}
        </span>
        <span className="text-xs text-muted-foreground font-mono">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>
      <div ref={waveformRef} className="w-full mb-2"></div>
      <div className="flex items-center space-x-3">
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={handlePlayPause}
          className="hover:bg-primary/10"
        >
          {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
        </Button>
        <Volume2 className="h-4 w-4 text-muted-foreground" />
        <Slider
          value={[volume]}
          max={1}
          step={0.01}
          onValueChange={handleVolumeChange}
          className="w-[100px]"
        />
        <span className="text-xs text-muted-foreground ml-2">
          {Math.round(volume * 100)}%
        </span>
      </div>
    </div>
  );
};
