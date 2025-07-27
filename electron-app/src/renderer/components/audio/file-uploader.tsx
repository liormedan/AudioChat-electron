import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Music, Upload, X, FileAudio } from 'lucide-react';
import { cn } from '../../lib/utils';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClearFile: () => void;
  accept?: Record<string, string[]>;
  maxSize?: number;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  onFileSelect,
  selectedFile,
  onClearFile,
  accept = {
    'audio/*': ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
  },
  maxSize = 100 * 1024 * 1024 // 100MB
}) => {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);
    
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0]?.code === 'file-too-large') {
        setError(`File is too large. Maximum size is ${Math.round(maxSize / (1024 * 1024))}MB`);
      } else if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Invalid file type. Please select an audio file.');
      } else {
        setError('File upload failed. Please try again.');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect, maxSize]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    return <FileAudio className="h-5 w-5" />;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Upload className="h-5 w-5" />
          <span>Upload Audio File</span>
        </CardTitle>
        <CardDescription>
          Drag and drop an audio file or click to browse. Supported formats: MP3, WAV, FLAC, OGG, M4A, AAC
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!selectedFile ? (
          <div
            {...getRootProps()}
            className={cn(
              "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
              isDragActive && !isDragReject && "border-primary bg-primary/5",
              isDragReject && "border-destructive bg-destructive/5",
              !isDragActive && "border-muted-foreground/25 hover:border-muted-foreground/50"
            )}
          >
            <input {...getInputProps()} />
            <Music className={cn(
              "h-12 w-12 mx-auto mb-4",
              isDragActive && !isDragReject && "text-primary",
              isDragReject && "text-destructive",
              !isDragActive && "text-muted-foreground"
            )} />
            
            {isDragActive ? (
              <p className="text-primary font-medium">
                {isDragReject ? "File type not supported" : "Drop your audio file here"}
              </p>
            ) : (
              <>
                <p className="text-muted-foreground mb-4">
                  Drop your audio files here or click to browse
                </p>
                <Button variant="outline">
                  Browse Files
                </Button>
              </>
            )}
          </div>
        ) : (
          <div className="border rounded-lg p-4 bg-muted/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getFileIcon(selectedFile.name)}
                <div>
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearFile}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
        
        {error && (
          <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};