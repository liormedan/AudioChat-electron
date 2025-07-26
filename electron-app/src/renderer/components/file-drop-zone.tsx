import React, { useCallback, useState } from 'react';
import { Button } from './ui/button';
import { Music } from 'lucide-react';
import { cn } from '../lib/utils';

interface FileDropZoneProps {
  onFiles: (files: FileList) => void;
}

export const FileDropZone: React.FC<FileDropZoneProps> = ({ onFiles }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        onFiles(e.dataTransfer.files);
      }
    },
    [onFiles]
  );

  const handleBrowse = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'audio/*';
    input.onchange = () => {
      if (input.files) onFiles(input.files);
    };
    input.click();
  };

  return (
    <div
      className={cn(
        'border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center transition-colors',
        isDragging && 'bg-muted/50'
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      data-testid="file-drop-zone"
    >
      <Music className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
      <p className="text-muted-foreground mb-4">
        Drop your audio files here or click to browse
      </p>
      <Button onClick={handleBrowse}>Browse Files</Button>
    </div>
  );
};
