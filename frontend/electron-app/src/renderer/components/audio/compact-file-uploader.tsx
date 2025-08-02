import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Music, X, FileAudio, Plus } from 'lucide-react';
import { cn } from '../../lib/utils';
import './compact-file-uploader.css';

interface CompactFileUploaderProps {
  onFileSelect: (file: File) => void;
  selectedFiles: File[];
  onRemoveFile: (index: number) => void;
  onClearAll: () => void;
  accept?: Record<string, string[]>;
  maxSize?: number;
  dragDropOnly?: boolean;
  maxHeight?: number;
}

export const CompactFileUploader: React.FC<CompactFileUploaderProps> = ({
  onFileSelect,
  selectedFiles = [],
  onRemoveFile,
  onClearAll,
  accept = {
    'audio/*': ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
  },
  maxSize = 100 * 1024 * 1024, // 100MB
  dragDropOnly = true,
  maxHeight = 200
}) => {
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('0');

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);
    
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0]?.code === 'file-too-large') {
        setError(`File too large. Max ${Math.round(maxSize / (1024 * 1024))}MB`);
      } else if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Invalid file type');
      } else {
        setError('Upload failed');
      }
      return;
    }

    acceptedFiles.forEach(file => {
      onFileSelect(file);
    });

    // Switch to the last uploaded file tab
    if (acceptedFiles.length > 0) {
      setActiveTab((selectedFiles.length + acceptedFiles.length - 1).toString());
    }
  }, [onFileSelect, maxSize, selectedFiles.length]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: true
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + sizes[i];
  };

  const getFileName = (fileName: string, maxLength: number = 15) => {
    if (fileName.length <= maxLength) return fileName;
    const extension = fileName.split('.').pop();
    const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
    const truncated = nameWithoutExt.substring(0, maxLength - extension!.length - 4) + '...';
    return `${truncated}.${extension}`;
  };

  return (
    <Card className="w-full compact-file-uploader" style={{ height: maxHeight }}>
      <CardContent className="p-2 h-full flex flex-col">
        {selectedFiles.length === 0 ? (
          // Empty state - drag and drop area
          <div
            {...getRootProps()}
            className={cn(
              "flex-1 border-2 border-dashed rounded-md flex flex-col items-center justify-center cursor-pointer transition-colors text-center p-4",
              isDragActive && !isDragReject && "border-primary bg-primary/5",
              isDragReject && "border-destructive bg-destructive/5",
              !isDragActive && "border-muted-foreground/25 hover:border-muted-foreground/50"
            )}
          >
            <input {...getInputProps()} />
            <Music className={cn(
              "h-8 w-8 mb-2",
              isDragActive && !isDragReject && "text-primary",
              isDragReject && "text-destructive",
              !isDragActive && "text-muted-foreground"
            )} />
            
            {isDragActive ? (
              <p className={cn(
                "text-sm font-medium",
                isDragReject ? "text-destructive" : "text-primary"
              )}>
                {isDragReject ? "Invalid file type" : "Drop files here"}
              </p>
            ) : (
              <div>
                <p className="text-sm text-muted-foreground mb-1">
                  Drop audio files here
                </p>
                <p className="text-xs text-muted-foreground">
                  MP3, WAV, FLAC, OGG, M4A, AAC
                </p>
                {!dragDropOnly && (
                  <Button variant="outline" size="sm" className="mt-2">
                    Browse
                  </Button>
                )}
              </div>
            )}
          </div>
        ) : (
          // Files uploaded - show tabs
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <TabsList className="h-7 p-0.5">
                {selectedFiles.map((file, index) => (
                  <TabsTrigger 
                    key={index} 
                    value={index.toString()}
                    className="h-6 px-2 text-xs flex items-center gap-1"
                  >
                    <FileAudio className="h-3 w-3" />
                    {getFileName(file.name, 8)}
                  </TabsTrigger>
                ))}
                <div
                  {...getRootProps()}
                  className="h-6 px-2 rounded-sm hover:bg-muted cursor-pointer flex items-center"
                >
                  <input {...getInputProps()} />
                  <Plus className="h-3 w-3" />
                </div>
              </TabsList>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearAll}
                className="h-6 px-2 text-xs text-muted-foreground hover:text-foreground"
              >
                Clear All
              </Button>
            </div>

            <div className="flex-1 overflow-hidden">
              {selectedFiles.map((file, index) => (
                <TabsContent 
                  key={index} 
                  value={index.toString()} 
                  className="h-full m-0 data-[state=active]:flex flex-col"
                >
                  <div className="flex-1 border rounded-md p-3 bg-muted/20 flex flex-col justify-between">
                    <div>
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2 min-w-0 flex-1">
                          <FileAudio className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                          <div className="min-w-0 flex-1">
                            <p className="font-medium text-sm truncate" title={file.name}>
                              {file.name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onRemoveFile(index)}
                          className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground flex-shrink-0"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="text-xs text-muted-foreground">
                      Ready for processing
                    </div>
                  </div>
                </TabsContent>
              ))}
            </div>
          </Tabs>
        )}
        
        {error && (
          <div className="mt-2 p-2 bg-destructive/10 border border-destructive/20 rounded text-xs text-destructive">
            {error}
          </div>
        )}
      </CardContent>
    </Card>
  );
};