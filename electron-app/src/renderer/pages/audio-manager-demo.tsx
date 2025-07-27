import React from 'react';
import { AudioWorkspace } from '../components/audio/audio-workspace';

export const AudioManagerDemo: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Audio File Manager Demo</h1>
        <p className="text-muted-foreground">
          Demonstration of the AudioFileManager component for managing multiple audio files
        </p>
      </div>

      <AudioWorkspace />
    </div>
  );
};