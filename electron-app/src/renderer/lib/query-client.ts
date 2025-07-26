import { QueryClient } from '@tanstack/react-query';

// Create a query client with optimized defaults
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: 5 minutes
      staleTime: 5 * 60 * 1000,
      // Cache time: 10 minutes
      gcTime: 10 * 60 * 1000,
      // Retry failed requests 3 times
      retry: 3,
      // Retry delay with exponential backoff
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Refetch on window focus
      refetchOnWindowFocus: true,
      // Don't refetch on reconnect by default (can be overridden per query)
      refetchOnReconnect: false,
      // Don't refetch on mount if data is fresh
      refetchOnMount: true,
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
      // Retry delay for mutations
      retryDelay: 1000,
    },
  },
});

// Query keys factory for consistent key management
export const queryKeys = {
  // Audio related queries
  audio: {
    all: ['audio'] as const,
    files: () => [...queryKeys.audio.all, 'files'] as const,
    file: (id: string) => [...queryKeys.audio.files(), id] as const,
    waveform: (id: string) => [...queryKeys.audio.file(id), 'waveform'] as const,
    analysis: (id: string) => [...queryKeys.audio.file(id), 'analysis'] as const,
    exports: () => [...queryKeys.audio.all, 'exports'] as const,
    export: (id: string) => [...queryKeys.audio.exports(), id] as const,
  },
  
  // File system related queries
  files: {
    all: ['files'] as const,
    stats: () => [...queryKeys.files.all, 'stats'] as const,
    metadata: (path: string) => [...queryKeys.files.all, 'metadata', path] as const,
    directory: (path: string) => [...queryKeys.files.all, 'directory', path] as const,
  },
  
  // LLM related queries
  llm: {
    all: ['llm'] as const,
    providers: () => [...queryKeys.llm.all, 'providers'] as const,
    models: (provider: string) => [...queryKeys.llm.providers(), provider, 'models'] as const,
    conversations: () => [...queryKeys.llm.all, 'conversations'] as const,
    conversation: (id: string) => [...queryKeys.llm.conversations(), id] as const,
  },
  
  // Settings related queries
  settings: {
    all: ['settings'] as const,
    app: () => [...queryKeys.settings.all, 'app'] as const,
    user: () => [...queryKeys.settings.all, 'user'] as const,
    system: () => [...queryKeys.settings.all, 'system'] as const,
  },
  
  // System related queries
  system: {
    all: ['system'] as const,
    info: () => [...queryKeys.system.all, 'info'] as const,
    health: () => [...queryKeys.system.all, 'health'] as const,
    logs: () => [...queryKeys.system.all, 'logs'] as const,
  },

  // Misc stats
  stats: {
    all: ['stats'] as const,
    quick: () => [...queryKeys.stats.all, 'quick'] as const,
  },
} as const;

// Type helpers for query keys
export type QueryKeys = typeof queryKeys;
export type AudioQueryKeys = QueryKeys['audio'];
export type FilesQueryKeys = QueryKeys['files'];
export type LLMQueryKeys = QueryKeys['llm'];
export type SettingsQueryKeys = QueryKeys['settings'];
export type SystemQueryKeys = QueryKeys['system'];