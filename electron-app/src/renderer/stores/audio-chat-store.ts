import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AudioUploadService, type UploadResult, type AudioMetadata } from '../services/audio-upload-service';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  audioFile?: string;
  processingStatus?: 'pending' | 'processing' | 'completed' | 'error';
}

export interface AudioFile {
  id: string;
  file: File;
  name: string;
  url: string;
  duration?: number;
  serverFileId?: string;
  uploadResult?: UploadResult;
  metadata?: AudioMetadata;
}

interface AudioChatState {
  // Audio state
  selectedFile: AudioFile | null;
  uploadedFiles: AudioFile[];
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  
  // Upload state
  isUploading: boolean;
  uploadProgress: number;
  
  // Chat state
  chatMessages: ChatMessage[];
  currentMessage: string;
  isProcessing: boolean;
  
  // Services
  uploadService: AudioUploadService;
  
  // Actions
  setSelectedFile: (file: AudioFile | null) => void;
  addUploadedFile: (file: AudioFile) => void;
  removeUploadedFile: (fileId: string) => void;
  setPlayingState: (isPlaying: boolean) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  
  // Upload actions
  setUploading: (isUploading: boolean) => void;
  setUploadProgress: (progress: number) => void;
  uploadFileToServer: (file: File) => Promise<AudioFile | null>;
  
  addChatMessage: (message: ChatMessage) => void;
  setCurrentMessage: (message: string) => void;
  setProcessing: (isProcessing: boolean) => void;
  clearChat: () => void;
  
  // Combined actions
  selectFileAndNotifyChat: (file: AudioFile) => void;
  sendAudioCommand: (command: string) => Promise<void>;
}

export const useAudioChatStore = create<AudioChatState>()(
  persist(
    (set, get) => ({
      // Initial state
      selectedFile: null,
      uploadedFiles: [],
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      isUploading: false,
      uploadProgress: 0,
      chatMessages: [],
      currentMessage: '',
      isProcessing: false,
      
      // Services
      uploadService: new AudioUploadService(),
      
      // Audio actions
      setSelectedFile: (file) => set({ selectedFile: file }),
      
      addUploadedFile: (file) => set((state) => ({
        uploadedFiles: [...state.uploadedFiles, file]
      })),
      
      removeUploadedFile: (fileId) => set((state) => ({
        uploadedFiles: state.uploadedFiles.filter(f => f.id !== fileId),
        selectedFile: state.selectedFile?.id === fileId ? null : state.selectedFile
      })),
      
      setPlayingState: (isPlaying) => set({ isPlaying }),
      setCurrentTime: (time) => set({ currentTime: time }),
      setDuration: (duration) => set({ duration }),
      
      // Upload actions
      setUploading: (isUploading) => set({ isUploading }),
      setUploadProgress: (progress) => set({ uploadProgress: progress }),
      
      uploadFileToServer: async (file: File) => {
        const { uploadService, setUploading, setUploadProgress, addChatMessage } = get();
        
        try {
          setUploading(true);
          setUploadProgress(0);
          
          // Client-side validation
          const validation = uploadService.validateFileBeforeUpload(file);
          if (!validation.valid) {
            const errorMessage: ChatMessage = {
              id: Date.now().toString(),
              type: 'assistant',
              content: `❌ Upload failed: ${validation.error}`,
              timestamp: new Date(),
              processingStatus: 'error'
            };
            addChatMessage(errorMessage);
            return null;
          }
          
          // Upload to server
          const result = await uploadService.uploadFile(file, (progress) => {
            setUploadProgress(progress);
          });
          
          if (result.success) {
            const audioFile: AudioFile = {
              id: Date.now().toString(),
              file,
              name: file.name,
              url: URL.createObjectURL(file),
              serverFileId: result.file_id,
              uploadResult: result,
              metadata: result.metadata
            };
            
            // Add success message
            const successMessage: ChatMessage = {
              id: (Date.now() + 1).toString(),
              type: 'assistant',
              content: `✅ File "${file.name}" uploaded successfully to server!\n\nFile details:\n• Size: ${uploadService.formatFileSize(result.file_size || 0)}\n• Duration: ${result.metadata?.duration ? uploadService.formatDuration(result.metadata.duration) : 'Unknown'}\n• Format: ${result.validation?.file_extension?.toUpperCase() || 'Unknown'}`,
              timestamp: new Date(),
              audioFile: file.name,
              processingStatus: 'completed'
            };
            addChatMessage(successMessage);
            
            return audioFile;
          } else {
            const errorMessage: ChatMessage = {
              id: Date.now().toString(),
              type: 'assistant',
              content: `❌ Upload failed: ${result.error}`,
              timestamp: new Date(),
              processingStatus: 'error'
            };
            addChatMessage(errorMessage);
            return null;
          }
          
        } catch (error) {
          const errorMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'assistant',
            content: `❌ Upload error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date(),
            processingStatus: 'error'
          };
          addChatMessage(errorMessage);
          return null;
        } finally {
          setUploading(false);
          setUploadProgress(0);
        }
      },
      
      // Chat actions
      addChatMessage: (message) => set((state) => ({
        chatMessages: [...state.chatMessages, message]
      })),
      
      setCurrentMessage: (message) => set({ currentMessage: message }),
      setProcessing: (isProcessing) => set({ isProcessing }),
      
      clearChat: () => set({ chatMessages: [], currentMessage: '' }),
      
      // Combined actions
      selectFileAndNotifyChat: (file) => {
        set({ selectedFile: file });
        
        const systemMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'system',
          content: `Audio file "${file.name}" selected! ${file.serverFileId ? '✅ File is uploaded to server.' : '⚠️ File is local only.'}\n\nYou can now give me editing commands like:
          
• "Remove background noise"
• "Increase volume by 20%"
• "Cut the first 30 seconds"
• "Add fade in and fade out effects"
• "Normalize the audio"

What would you like me to do with this audio?`,
          timestamp: new Date(),
          audioFile: file.name
        };
        
        get().addChatMessage(systemMessage);
      },
      
      sendAudioCommand: async (command: string) => {
        const { selectedFile, addChatMessage, setProcessing } = get();
        
        if (!selectedFile) {
          const errorMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'assistant',
            content: 'Please select an audio file first before giving commands.',
            timestamp: new Date(),
            processingStatus: 'error'
          };
          addChatMessage(errorMessage);
          return;
        }

        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: command,
          timestamp: new Date()
        };

        addChatMessage(userMessage);
        setProcessing(true);

        try {
          // Use server file ID if available, otherwise use filename
          const fileIdentifier = selectedFile.serverFileId || selectedFile.name;
          
          const response = await fetch('http://127.0.0.1:5000/api/audio/process-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              command: command,
              filename: fileIdentifier,
              file_id: selectedFile.serverFileId
            }),
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const result = await response.json();
          
          const assistantMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: result.response || 'Audio processing completed successfully!',
            timestamp: new Date(),
            processingStatus: 'completed'
          };

          addChatMessage(assistantMessage);
        } catch (error: any) {
          console.error('Error processing command:', error);
          
          const errorMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: `Sorry, I couldn't process that command. Error: ${error.message}`,
            timestamp: new Date(),
            processingStatus: 'error'
          };

          addChatMessage(errorMessage);
        } finally {
          setProcessing(false);
        }
      }
    }),
    {
      name: 'audio-chat-storage',
      partialize: (state) => ({
        uploadedFiles: state.uploadedFiles,
        chatMessages: state.chatMessages.filter(msg => msg.type !== 'system') // Don't persist system messages
      })
    }
  )
);