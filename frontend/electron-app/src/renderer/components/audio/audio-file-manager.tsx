import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  FileAudio, 
  Trash2, 
  Play, 
  Pause, 
  Download, 
  Info, 
  FolderOpen,
  Search,
  Filter,
  MoreVertical,
  Clock,
  HardDrive
} from 'lucide-react';
import { Input } from '../ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../ui/alert-dialog';
import { cn } from '../../lib/utils';

export interface AudioFileData {
  id: string;
  file: File;
  name: string;
  size: number;
  duration?: number;
  format: string;
  lastModified: Date;
  isPlaying?: boolean;
  metadata?: {
    bitrate?: number;
    sampleRate?: number;
    channels?: number;
    quality?: 'high' | 'standard' | 'basic';
  };
}

interface AudioFileManagerProps {
  files: AudioFileData[];
  onFileSelect?: (file: AudioFileData) => void;
  onFileDelete?: (fileId: string) => void;
  onFilePlay?: (fileId: string) => void;
  onFilePause?: (fileId: string) => void;
  onFileDownload?: (fileId: string) => void;
  onFileInfo?: (file: AudioFileData) => void;
  selectedFileId?: string;
  className?: string;
}

export const AudioFileManager: React.FC<AudioFileManagerProps> = ({
  files,
  onFileSelect,
  onFileDelete,
  onFilePlay,
  onFilePause,
  onFileDownload,
  onFileInfo,
  selectedFileId,
  className
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'size' | 'duration' | 'modified'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<string | null>(null);

  const formatFileSize = useCallback((bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  const formatDuration = useCallback((seconds?: number) => {
    if (!seconds || seconds === 0) return '--:--';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  }, []);

  const getQualityBadge = useCallback((file: AudioFileData) => {
    const quality = file.metadata?.quality;
    if (!quality) return null;
    
    const variants = {
      high: 'default',
      standard: 'secondary',
      basic: 'outline'
    } as const;
    
    return (
      <Badge variant={variants[quality]} className="text-xs">
        {quality.charAt(0).toUpperCase() + quality.slice(1)}
      </Badge>
    );
  }, []);

  // Filter and sort files
  const filteredAndSortedFiles = React.useMemo(() => {
    let filtered = files.filter(file =>
      file.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    filtered.sort((a, b) => {
      let aValue: string | number;
      let bValue: string | number;

      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'size':
          aValue = a.size;
          bValue = b.size;
          break;
        case 'duration':
          aValue = a.duration || 0;
          bValue = b.duration || 0;
          break;
        case 'modified':
          aValue = a.lastModified.getTime();
          bValue = b.lastModified.getTime();
          break;
        default:
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      } else {
        return sortOrder === 'asc' ? (aValue as number) - (bValue as number) : (bValue as number) - (aValue as number);
      }
    });

    return filtered;
  }, [files, searchQuery, sortBy, sortOrder]);

  const handleDeleteClick = useCallback((fileId: string) => {
    setFileToDelete(fileId);
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(() => {
    if (fileToDelete && onFileDelete) {
      onFileDelete(fileToDelete);
    }
    setDeleteDialogOpen(false);
    setFileToDelete(null);
  }, [fileToDelete, onFileDelete]);

  const handleSortChange = useCallback((newSortBy: typeof sortBy) => {
    if (newSortBy === sortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  }, [sortBy, sortOrder]);

  if (files.length === 0) {
    return (
      <Card className={className}>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FolderOpen className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-muted-foreground text-center">
            No audio files loaded yet
          </p>
          <p className="text-sm text-muted-foreground text-center mt-2">
            Upload some audio files to get started
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileAudio className="h-5 w-5" />
              <span>Audio Files</span>
              <Badge variant="secondary">{files.length}</Badge>
            </div>
          </CardTitle>
          <CardDescription>
            Manage your uploaded audio files
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Search and Filter Controls */}
          <div className="flex items-center space-x-2 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Sort
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => handleSortChange('name')}>
                  Name {sortBy === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSortChange('size')}>
                  Size {sortBy === 'size' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSortChange('duration')}>
                  Duration {sortBy === 'duration' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleSortChange('modified')}>
                  Modified {sortBy === 'modified' && (sortOrder === 'asc' ? '↑' : '↓')}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* File List */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredAndSortedFiles.map((file) => (
              <div
                key={file.id}
                className={cn(
                  "border rounded-lg p-3 transition-colors cursor-pointer hover:bg-muted/50",
                  selectedFileId === file.id && "bg-primary/10 border-primary"
                )}
                onClick={() => onFileSelect?.(file)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <FileAudio className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="font-medium truncate">{file.name}</p>
                        {getQualityBadge(file)}
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <HardDrive className="h-3 w-3" />
                          <span>{formatFileSize(file.size)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="h-3 w-3" />
                          <span>{formatDuration(file.duration)}</span>
                        </div>
                        <span className="uppercase">{file.format}</span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-1 ml-2">
                    {/* Play/Pause Button */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (file.isPlaying) {
                          onFilePause?.(file.id);
                        } else {
                          onFilePlay?.(file.id);
                        }
                      }}
                      className="h-8 w-8 p-0"
                    >
                      {file.isPlaying ? (
                        <Pause className="h-4 w-4" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>

                    {/* More Actions Menu */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onFileInfo?.(file)}>
                          <Info className="h-4 w-4 mr-2" />
                          File Info
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onFileDownload?.(file.id)}>
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => handleDeleteClick(file.id)}
                          className="text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredAndSortedFiles.length === 0 && searchQuery && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                No files found matching "{searchQuery}"
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Audio File</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this audio file? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};