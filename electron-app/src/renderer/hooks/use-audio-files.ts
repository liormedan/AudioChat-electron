import { useState, useCallback } from 'react';
import { AudioFileData } from '../components/audio/audio-file-manager';

export interface UseAudioFilesReturn {
  files: AudioFileData[];
  selectedFile: AudioFileData | null;
  addFile: (file: File) => Promise<AudioFileData>;
  removeFile: (fileId: string) => void;
  selectFile: (fileId: string) => void;
  clearSelection: () => void;
  updateFileMetadata: (fileId: string, metadata: Partial<AudioFileData['metadata']>) => void;
  setFilePlayingState: (fileId: string, isPlaying: boolean) => void;
  clearAllFiles: () => void;
}

export const useAudioFiles = (): UseAudioFilesReturn => {
  const [files, setFiles] = useState<AudioFileData[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);

  const generateFileId = useCallback(() => {
    return `audio-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  const getFileFormat = useCallback((file: File) => {
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
  }, []);

  const estimateQuality = useCallback((file: File, duration?: number) => {
    if (!duration || duration === 0) return undefined;
    
    const bitrate = (file.size * 8) / duration / 1000; // kbps approximation
    
    if (bitrate > 256) return 'high';
    if (bitrate > 128) return 'standard';
    return 'basic';
  }, []);

  const getAudioDuration = useCallback((file: File): Promise<number> => {
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
  }, []);

  const addFile = useCallback(async (file: File): Promise<AudioFileData> => {
    const id = generateFileId();
    const format = getFileFormat(file);
    
    // Get audio duration
    const duration = await getAudioDuration(file);
    const quality = estimateQuality(file, duration);
    
    const audioFileData: AudioFileData = {
      id,
      file,
      name: file.name,
      size: file.size,
      duration,
      format,
      lastModified: new Date(file.lastModified),
      isPlaying: false,
      metadata: {
        quality,
        // These would typically come from actual audio analysis
        bitrate: duration > 0 ? Math.round((file.size * 8) / duration / 1000) : undefined,
        sampleRate: undefined, // Would need Web Audio API or backend analysis
        channels: undefined, // Would need Web Audio API or backend analysis
      }
    };

    setFiles(prev => [...prev, audioFileData]);
    return audioFileData;
  }, [generateFileId, getFileFormat, getAudioDuration, estimateQuality]);

  const removeFile = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
    
    // Clear selection if the selected file was removed
    if (selectedFileId === fileId) {
      setSelectedFileId(null);
    }
  }, [selectedFileId]);

  const selectFile = useCallback((fileId: string) => {
    setSelectedFileId(fileId);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedFileId(null);
  }, []);

  const updateFileMetadata = useCallback((fileId: string, metadata: Partial<AudioFileData['metadata']>) => {
    setFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, metadata: { ...file.metadata, ...metadata } }
        : file
    ));
  }, []);

  const setFilePlayingState = useCallback((fileId: string, isPlaying: boolean) => {
    setFiles(prev => prev.map(file => ({
      ...file,
      isPlaying: file.id === fileId ? isPlaying : false // Only one file can play at a time
    })));
  }, []);

  const clearAllFiles = useCallback(() => {
    setFiles([]);
    setSelectedFileId(null);
  }, []);

  const selectedFile = files.find(file => file.id === selectedFileId) || null;

  return {
    files,
    selectedFile,
    addFile,
    removeFile,
    selectFile,
    clearSelection,
    updateFileMetadata,
    setFilePlayingState,
    clearAllFiles
  };
};