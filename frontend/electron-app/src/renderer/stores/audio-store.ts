import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AudioFileData } from '../components/audio/audio-file-manager';

interface AudioStore {
  // State
  files: AudioFileData[];
  selectedFileId: string | null;
  currentlyPlayingId: string | null;
  
  // Actions
  addFile: (file: AudioFileData) => void;
  removeFile: (fileId: string) => void;
  selectFile: (fileId: string) => void;
  clearSelection: () => void;
  setPlayingFile: (fileId: string | null) => void;
  updateFileMetadata: (fileId: string, metadata: Partial<AudioFileData['metadata']>) => void;
  clearAllFiles: () => void;
  
  // Getters
  getSelectedFile: () => AudioFileData | null;
  getCurrentlyPlayingFile: () => AudioFileData | null;
  getFileById: (fileId: string) => AudioFileData | null;
}

export const useAudioStore = create<AudioStore>()(
  persist(
    (set, get) => ({
      // Initial state
      files: [],
      selectedFileId: null,
      currentlyPlayingId: null,

      // Actions
      addFile: (file: AudioFileData) => {
        set((state) => ({
          files: [...state.files, file]
        }));
      },

      removeFile: (fileId: string) => {
        set((state) => ({
          files: state.files.filter(f => f.id !== fileId),
          selectedFileId: state.selectedFileId === fileId ? null : state.selectedFileId,
          currentlyPlayingId: state.currentlyPlayingId === fileId ? null : state.currentlyPlayingId
        }));
      },

      selectFile: (fileId: string) => {
        set({ selectedFileId: fileId });
      },

      clearSelection: () => {
        set({ selectedFileId: null });
      },

      setPlayingFile: (fileId: string | null) => {
        set((state) => ({
          currentlyPlayingId: fileId,
          files: state.files.map(file => ({
            ...file,
            isPlaying: file.id === fileId
          }))
        }));
      },

      updateFileMetadata: (fileId: string, metadata: Partial<AudioFileData['metadata']>) => {
        set((state) => ({
          files: state.files.map(file =>
            file.id === fileId
              ? { ...file, metadata: { ...file.metadata, ...metadata } }
              : file
          )
        }));
      },

      clearAllFiles: () => {
        set({
          files: [],
          selectedFileId: null,
          currentlyPlayingId: null
        });
      },

      // Getters
      getSelectedFile: () => {
        const state = get();
        return state.files.find(f => f.id === state.selectedFileId) || null;
      },

      getCurrentlyPlayingFile: () => {
        const state = get();
        return state.files.find(f => f.id === state.currentlyPlayingId) || null;
      },

      getFileById: (fileId: string) => {
        const state = get();
        return state.files.find(f => f.id === fileId) || null;
      }
    }),
    {
      name: 'audio-store',
      // Only persist essential data, not the actual File objects
      partialize: (state) => ({
        selectedFileId: state.selectedFileId,
        // Note: We don't persist files array because File objects can't be serialized
        // In a real app, you'd store file paths or references instead
      })
    }
  )
);