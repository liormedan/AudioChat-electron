import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Music, Upload, Play, Pause, Square, Mic } from 'lucide-react';

export const AudioPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [transcriptionResult, setTranscriptionResult] = useState<string | null>(null);
  const [isTranscribing, setIsTranscribing] = useState<boolean>(false);

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
      setTranscriptionResult(null); // Clear previous transcription
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

  const handleTranscribe = async () => {
    if (!selectedFile) return;

    setIsTranscribing(true);
    setTranscriptionResult(null);

    try {
      const reader = new FileReader();
      reader.readAsDataURL(selectedFile);
      reader.onloadend = async () => {
        const base64Audio = reader.result?.toString().split(', ')[1]; // Get base64 part
        if (!base64Audio) {
          setTranscriptionResult('Error: Could not read audio file.');
          setIsTranscribing(false);
          return;
        }

        try {
          const response = await fetch('http://127.0.0.1:5000/api/audio/transcribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audio_base64: base64Audio }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
          }

          const result = await response.json();
          setTranscriptionResult(result.transcription);
        } catch (error: any) {
          console.error('Error transcribing audio:', error);
          setTranscriptionResult(`Error transcribing: ${error.message}`);
        } finally {
          setIsTranscribing(false);
        }
      };
      reader.onerror = (error) => {
        console.error('FileReader error:', error);
        setTranscriptionResult('Error reading file.');
        setIsTranscribing(false);
      };
    } catch (error: any) {
      console.error('Error initiating transcription:', error);
      setTranscriptionResult(`Error: ${error.message}`);
      setIsTranscribing(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Audio Processing</h1>
        <p className="text-muted-foreground">
          Process, edit, and analyze your audio files
        </p>
      </div>

      {/* File Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Upload Audio File</span>
          </CardTitle>
          <CardDescription>
            Drag and drop an audio file or click to browse
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileChange}
              className="hidden"
              id="audio-upload"
            />
            <label htmlFor="audio-upload" className="cursor-pointer block">
              <Music className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground mb-4">
                {selectedFile ? selectedFile.name : 'Drop your audio files here or click to browse'}
              </p>
              <Button asChild>
                <span className="cursor-pointer">Browse Files</span>
              </Button>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Audio Player */}
      <Card>
        <CardHeader>
          <CardTitle>Audio Player</CardTitle>
          <CardDescription>
            Control playback and preview your audio
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <Button size="sm" variant="outline" onClick={handlePlayPause} disabled={!audioUrl}>
                {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              </Button>
              <Button size="sm" variant="outline" onClick={handleStop} disabled={!audioUrl}>
                <Square className="h-4 w-4" />
              </Button>
              <div className="flex-1 bg-muted rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${(currentTime / duration) * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Processing Options */}
      <Card>
        <CardHeader>
          <CardTitle>Processing Options</CardTitle>
          <CardDescription>
            Configure audio processing parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Button onClick={handleTranscribe} disabled={!selectedFile || isTranscribing}>
              {isTranscribing ? (
                <>
                  <Loader className="animate-spin mr-2" size={16} /> Transcribing...
                </>
              ) : (
                <>
                  <Mic className="mr-2" size={16} /> Transcribe Audio
                </>
              )}
            </Button>
            {transcriptionResult && (
              <div className="mt-4 p-4 border rounded-lg bg-muted/20">
                <h3 className="text-lg font-semibold mb-2">Transcription Result:</h3>
                <p className="text-muted-foreground whitespace-pre-wrap">{transcriptionResult}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};