import React, { useState } from 'react';
import { FileUploader } from './file-uploader';
import { AudioFileManager, AudioFileData } from './audio-file-manager';
import { AudioFileInfo } from './audio-file-info';
import { useAudioFiles } from '../../hooks/use-audio-files';
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
import { Upload, List, Info } from 'lucide-react';

export const AudioWorkspace: React.FC = () => {
  const {
    files,
    selectedFile,
    addFile,
    removeFile,
    selectFile,
    clearSelection,
    setFilePlayingState
  } = useAudioFiles();

  const [currentUploadFile, setCurrentUploadFile] = useState<File | null>(null);
  const [infoDialogFile, setInfoDialogFile] = useState<AudioFileData | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileSelect = async (file: File) => {
    setCurrentUploadFile(file);
  };

  const handleFileUpload = async () => {
    if (!currentUploadFile) return;

    setIsUploading(true);
    try {
      const audioFile = await addFile(currentUploadFile);
      selectFile(audioFile.id);
      setCurrentUploadFile(null);
      
      toast({
        title: "File uploaded successfully",
        description: `${audioFile.name} has been added to your workspace.`,
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
    // In a real implementation, this would integrate with an audio player
    setFilePlayingState(fileId, true);
    
    // Simulate stopping playback after some time (for demo purposes)
    setTimeout(() => {
      setFilePlayingState(fileId, false);
    }, 3000);
  };

  const handleFilePause = (fileId: string) => {
    setFilePlayingState(fileId, false);
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

  return (
    <div className="space-y-6">
      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="upload" className="flex items-center space-x-2">
            <Upload className="h-4 w-4" />
            <span>Upload</span>
          </TabsTrigger>
          <TabsTrigger value="manage" className="flex items-center space-x-2">
            <List className="h-4 w-4" />
            <span>Manage Files</span>
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
            selectedFileId={selectedFile?.id}
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