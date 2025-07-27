import React, { useState } from 'react';
import { FileUploader } from './file-uploader';
import { AudioFileManager, AudioFileData } from './audio-file-manager';
import { AudioFileInfo } from './audio-file-info';
import { useAudioStore } from '../../stores/audio-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { toast } from '../ui/use-toast';
import { Upload, List, Info, Trash2 } from 'lucide-react';

export const AudioWorkspaceWithStore: React.FC = () => {
  const {
    files,
    selectedFileId,
    addFile,
    removeFile,
    selectFile,
    clearSelection,
    setPlayingFile,
    clearAllFiles,
    getSelectedFile
  } = useAudioStore();

  const [currentUploadFile, setCurrentUploadFile] = useState<File | null>(null);
  const [infoDialogFile, setInfoDialogFile] = useState<AudioFileData | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const selectedFile = getSelectedFile();

  const generateFileId = () => {
    return `audio-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  const getFileFormat = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    const mimeTypeMap: Record<string, string> = {
      'audio/mpeg': 'MP3',
      'audio/wav': 'WAV',
      'audio/flac': 'FLAC',
      'audio/ogg': 'OGG',
      'audio/mp4': 'M4A',
      'audio/aac': 'AAC'
    };
    
    return mimeTypeMap[file.type] || extension?.toUpperCase() || 'Unknown';
  };

  const estimateQuality = (file: File, duration?: number) => {
    if (!duration || duration === 0) return undefined;
    
    const bitrate = (file.size * 8) / duration / 1000; // kbps approximation
    
    if (bitrate > 256) return 'high';
    if (bitrate > 128) return 'standard';
    return 'basic';
  };

  const getAudioDuration = (file: File): Promise<number> => {
    return new Promise((resolve) => {
      const audio = new Audio();
      const url = URL.createObjectURL(file);
      
      audio.addEventListener('loadedmetadata', () => {
        URL.revokeObjectURL(url);
        resolve(audio.duration);
      });
      
      audio.addEventListener('error', () => {
        URL.revokeObjectURL(url);
        resolve(0);
      });
      
      audio.src = url;
    });
  };

  const handleFileSelect = async (file: File) => {
    setCurrentUploadFile(file);
  };

  const handleFileUpload = async () => {
    if (!currentUploadFile) return;

    setIsUploading(true);
    try {
      const id = generateFileId();
      const format = getFileFormat(currentUploadFile);
      const duration = await getAudioDuration(currentUploadFile);
      const quality = estimateQuality(currentUploadFile, duration);
      
      const audioFileData: AudioFileData = {
        id,
        file: currentUploadFile,
        name: currentUploadFile.name,
        size: currentUploadFile.size,
        duration,
        format,
        lastModified: new Date(currentUploadFile.lastModified),
        isPlaying: false,
        metadata: {
          quality,
          bitrate: duration > 0 ? Math.round((currentUploadFile.size * 8) / duration / 1000) : undefined,
          sampleRate: undefined,
          channels: undefined,
        }
      };

      addFile(audioFileData);
      selectFile(audioFileData.id);
      setCurrentUploadFile(null);
      
      toast({
        title: "File uploaded successfully",
        description: `${audioFileData.name} has been added to your workspace.`,
      });
    } catch (error) {
      toast({
        title: "Upload failed",
        description: "There was an error uploading your file. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleClearUpload = () => {
    setCurrentUploadFile(null);
  };

  const handleFileManagerSelect = (file: AudioFileData) => {
    selectFile(file.id);
  };

  const handleFileDelete = (fileId: string) => {
    const fileToDelete = files.find(f => f.id === fileId);
    removeFile(fileId);
    
    if (fileToDelete) {
      toast({
        title: "File deleted",
        description: `${fileToDelete.name} has been removed from your workspace.`,
      });
    }
  };

  const handleFilePlay = (fileId: string) => {
    setPlayingFile(fileId);
    
    // Simulate stopping playback after some time (for demo purposes)
    setTimeout(() => {
      setPlayingFile(null);
    }, 3000);
  };

  const handleFilePause = (fileId: string) => {
    setPlayingFile(null);
  };

  const handleFileDownload = (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    if (file) {
      // Create download link
      const url = URL.createObjectURL(file.file);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Download started",
        description: `${file.name} is being downloaded.`,
      });
    }
  };

  const handleFileInfo = (file: AudioFileData) => {
    setInfoDialogFile(file);
  };

  const handleClearAllFiles = () => {
    clearAllFiles();
    toast({
      title: "All files cleared",
      description: "All audio files have been removed from your workspace.",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Audio Workspace</h2>
          <p className="text-muted-foreground">
            Manage your audio files with advanced file management features
          </p>
        </div>
        {files.length > 0 && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleClearAllFiles}
            className="text-destructive hover:text-destructive"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Clear All
          </Button>
        )}
      </div>

      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="upload" className="flex items-center space-x-2">
            <Upload className="h-4 w-4" />
            <span>Upload</span>
          </TabsTrigger>
          <TabsTrigger value="manage" className="flex items-center space-x-2">
            <List className="h-4 w-4" />
            <span>Manage Files ({files.length})</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-4">
          <FileUploader
            onFileSelect={handleFileSelect}
            selectedFile={currentUploadFile}
            onClearFile={handleClearUpload}
          />
          
          {currentUploadFile && (
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={handleClearUpload}>
                Cancel
              </Button>
              <Button 
                onClick={handleFileUpload} 
                disabled={isUploading}
              >
                {isUploading ? 'Uploading...' : 'Add to Workspace'}
              </Button>
            </div>
          )}
        </TabsContent>

        <TabsContent value="manage" className="space-y-4">
          <AudioFileManager
            files={files}
            selectedFileId={selectedFileId}
            onFileSelect={handleFileManagerSelect}
            onFileDelete={handleFileDelete}
            onFilePlay={handleFilePlay}
            onFilePause={handleFilePause}
            onFileDownload={handleFileDownload}
            onFileInfo={handleFileInfo}
          />
        </TabsContent>
      </Tabs>

      {/* Selected File Info Panel */}
      {selectedFile && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Info className="h-5 w-5" />
              <span>Selected File</span>
            </CardTitle>
            <CardDescription>
              Information about the currently selected audio file
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AudioFileInfo 
              file={selectedFile.file} 
              duration={selectedFile.duration} 
            />
          </CardContent>
        </Card>
      )}

      {/* File Info Dialog */}
      <Dialog open={!!infoDialogFile} onOpenChange={() => setInfoDialogFile(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>File Information</DialogTitle>
            <DialogDescription>
              Detailed information about the selected audio file
            </DialogDescription>
          </DialogHeader>
          {infoDialogFile && (
            <AudioFileInfo 
              file={infoDialogFile.file} 
              duration={infoDialogFile.duration} 
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};