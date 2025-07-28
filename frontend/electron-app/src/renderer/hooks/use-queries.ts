import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../lib/query-client';
import { useNotifications } from './use-app-state';

// Types for API responses (these would typically come from shared types)
interface AudioFile {
  id: string;
  path: string;
  name: string;
  size: number;
  duration: number;
  format: string;
  metadata: Record<string, any>;
  createdAt: Date;
  modifiedAt: Date;
}

interface WaveformData {
  peaks: number[];
  duration: number;
  sampleRate: number;
  channels: number;
}

interface AudioAnalysis {
  tempo: number;
  key: string;
  loudness: number;
  spectralCentroid: number;
  spectralRolloff: number;
  mfcc: number[];
}

interface ExportJob {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  inputFile: string;
  outputFile: string;
  format: string;
  quality: number;
  createdAt: Date;
  completedAt?: Date;
  error?: string;
}

interface FileStats {
  path: string;
  size: number;
  created: Date;
  modified: Date;
  type: string;
  metadata: Record<string, any>;
}

export interface QuickStats {
  totalFiles: number;
  processingJobs: number;
  conversations: number;
}

// Mock API functions (these would typically call the actual IPC/API)
const mockAPI = {
  audio: {
    getFiles: async (): Promise<AudioFile[]> => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      return [];
    },
    
    getFile: async (id: string): Promise<AudioFile | null> => {
      await new Promise(resolve => setTimeout(resolve, 300));
      console.log('Mock API: getFile called with id:', id);
      return null;
    },
    
    getWaveform: async (id: string): Promise<WaveformData> => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Mock API: getWaveform called with id:', id);
      return {
        peaks: [],
        duration: 0,
        sampleRate: 44100,
        channels: 2,
      };
    },
    
    getAnalysis: async (id: string): Promise<AudioAnalysis> => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Mock API: getAnalysis called with id:', id);
      return {
        tempo: 120,
        key: 'C',
        loudness: -12,
        spectralCentroid: 2000,
        spectralRolloff: 8000,
        mfcc: [],
      };
    },
    
    exportAudio: async (params: {
      fileId: string;
      format: string;
      quality: number;
      outputPath: string;
    }): Promise<ExportJob> => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return {
        id: `export-${Date.now()}`,
        status: 'pending',
        progress: 0,
        inputFile: params.fileId,
        outputFile: params.outputPath,
        format: params.format,
        quality: params.quality,
        createdAt: new Date(),
      };
    },
  },
  
  files: {
    getStats: async (path: string): Promise<FileStats> => {
      await new Promise(resolve => setTimeout(resolve, 200));
      return {
        path,
        size: 0,
        created: new Date(),
        modified: new Date(),
        type: 'audio',
        metadata: {},
      };
    },
    
    getMetadata: async (path: string): Promise<Record<string, any>> => {
      await new Promise(resolve => setTimeout(resolve, 300));
      console.log('Mock API: getMetadata called with path:', path);
      return {};
    },
  },

  stats: {
    getQuickStats: async (): Promise<QuickStats> => {
      // Placeholder for Python backend call
      const resp = (await window.electronAPI.callPythonService(
        'stats',
        'get_quick_stats',
        null
      )) as { success: boolean; data?: QuickStats } | null;

      if (resp && resp.success && resp.data) {
        return resp.data;
      }

      return { totalFiles: 0, processingJobs: 0, conversations: 0 };
    },
  },
};

// Audio-related hooks
export const useAudioFiles = () => {
  return useQuery({
    queryKey: queryKeys.audio.files(),
    queryFn: mockAPI.audio.getFiles,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useAudioFile = (id: string | undefined) => {
  return useQuery({
    queryKey: queryKeys.audio.file(id || ''),
    queryFn: () => mockAPI.audio.getFile(id!),
    enabled: !!id,
  });
};

export const useWaveform = (id: string | undefined) => {
  return useQuery({
    queryKey: queryKeys.audio.waveform(id || ''),
    queryFn: () => mockAPI.audio.getWaveform(id!),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes - waveforms don't change
  });
};

export const useAudioAnalysis = (id: string | undefined) => {
  return useQuery({
    queryKey: queryKeys.audio.analysis(id || ''),
    queryFn: () => mockAPI.audio.getAnalysis(id!),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes - analysis doesn't change
  });
};

// File-related hooks
export const useFileStats = (path: string | undefined) => {
  return useQuery({
    queryKey: queryKeys.files.stats(),
    queryFn: () => mockAPI.files.getStats(path!),
    enabled: !!path,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

export const useFileMetadata = (path: string | undefined) => {
  return useQuery({
    queryKey: queryKeys.files.metadata(path || ''),
    queryFn: () => mockAPI.files.getMetadata(path!),
    enabled: !!path,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Quick stats
export const useQuickStats = () => {
  return useQuery({
    queryKey: queryKeys.stats.quick(),
    queryFn: () => mockAPI.stats.getQuickStats(),
    staleTime: 30 * 1000,
  });
};

// Mutation hooks with notifications
export const useExportAudio = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotifications();
  
  return useMutation({
    mutationFn: mockAPI.audio.exportAudio,
    onSuccess: (data) => {
      // Invalidate exports queries
      queryClient.invalidateQueries({ queryKey: queryKeys.audio.exports() });
      
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: `Audio export job ${data.id} has been queued.`,
      });
    },
    onError: (error) => {
      addNotification({
        type: 'error',
        title: 'Export Failed',
        message: `Failed to start audio export: ${error.message}`,
      });
    },
  });
};

// Custom hook for optimistic updates
export const useOptimisticUpdate = <T>(
  queryKey: readonly unknown[],
  updateFn: (oldData: T | undefined, newData: Partial<T>) => T
) => {
  const queryClient = useQueryClient();
  
  return (newData: Partial<T>) => {
    queryClient.setQueryData<T>(queryKey, (oldData) => 
      updateFn(oldData, newData)
    );
  };
};

// Custom hook for invalidating related queries
export const useInvalidateQueries = () => {
  const queryClient = useQueryClient();
  
  return {
    invalidateAudio: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.audio.all });
    },
    invalidateFiles: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.files.all });
    },
    invalidateAll: () => {
      queryClient.invalidateQueries();
    },
    refetchAudio: () => {
      queryClient.refetchQueries({ queryKey: queryKeys.audio.all });
    },
    refetchFiles: () => {
      queryClient.refetchQueries({ queryKey: queryKeys.files.all });
    },
  };
};

// Custom hook for prefetching data
export const usePrefetch = () => {
  const queryClient = useQueryClient();
  
  return {
    prefetchAudioFile: (id: string) => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.audio.file(id),
        queryFn: () => mockAPI.audio.getFile(id),
        staleTime: 5 * 60 * 1000,
      });
    },
    prefetchWaveform: (id: string) => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.audio.waveform(id),
        queryFn: () => mockAPI.audio.getWaveform(id),
        staleTime: 10 * 60 * 1000,
      });
    },
  };
};