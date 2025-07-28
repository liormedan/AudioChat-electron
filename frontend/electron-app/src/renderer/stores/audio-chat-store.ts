import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AudioUploadService, type UploadResult, type AudioMetadata } from '../services/audio-upload-service';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date | string; // Allow both Date and string for persistence
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
  clearAll: () => void;
  startNewSession: () => void;
  
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
      
      clearAll: () => set({
        selectedFile: null,
        uploadedFiles: [],
        chatMessages: [],
        currentMessage: '',
        isProcessing: false,
        isUploading: false,
        uploadProgress: 0,
        isPlaying: false,
        currentTime: 0,
        duration: 0
      }),
      
      startNewSession: () => {
        const { clearAll, addChatMessage } = get();
        clearAll();
        
        // Add welcome message
        const welcomeMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'system',
          content: `🎵 **Welcome to Audio Chat Studio!**\n\nI'm here to help you edit audio files using natural language commands.\n\n**Getting Started:**\n1. Upload an audio file (drag & drop or click Upload)\n2. Give me editing commands like:\n   • "Remove background noise"\n   • "Increase volume by 20%"\n   • "Cut the first 30 seconds"\n   • "Add fade effects"\n\nWhat audio would you like to work with today?`,
          timestamp: new Date()
        };
        
        addChatMessage(welcomeMessage);
      },
      
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
            content: '⚠️ **No File Selected**\n\nPlease select an audio file first before giving commands.',
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

        // Add processing status message
        const processingMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `🔄 **Processing Command**\n\n"${command}"\n\nPlease wait while I process your audio...`,
          timestamp: new Date(),
          processingStatus: 'processing'
        };

        addChatMessage(processingMessage);
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

          // Remove processing message
          const currentState = get();
          const filteredMessages = currentState.chatMessages.filter(msg => msg.id !== processingMessage.id);
          set({ chatMessages: filteredMessages });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Server error: ${response.status}`);
          }

          const result = await response.json();
          
          let responseContent = '✅ **Command Completed Successfully**\n\n';
          responseContent += result.response || 'Audio processing completed!';
          
          if (result.processed_file) {
            responseContent += `\n\n📁 **Output File:** ${result.processed_file}`;
          }
          
          if (result.details) {
            responseContent += `\n\n📋 **Details:**\n${result.details}`;
          }

          const assistantMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'assistant',
            content: responseContent,
            timestamp: new Date(),
            processingStatus: 'completed'
          };

          addChatMessage(assistantMessage);
        } catch (error: any) {
          console.error('Error processing command:', error);
          
          // Remove processing message if still there
          const currentState = get();
          const filteredMessages = currentState.chatMessages.filter(msg => msg.id !== processingMessage.id);
          set({ chatMessages: filteredMessages });
          
          let errorContent = '❌ **Command Failed**\n\n';
          
          if (error.message.includes('Server error: 500')) {
            errorContent += 'Internal server error. The audio processing service may be unavailable.';
          } else if (error.message.includes('Server error: 404')) {
            errorContent += 'Audio file not found. Please make sure the file is properly uploaded.';
          } else if (error.message.includes('Network')) {
            errorContent += 'Network connection error. Please check your connection and try again.';
          } else {
            errorContent += `Error: ${error.message}`;
          }
          
          errorContent += '\n\n💡 **Suggestions:**\n• Check if the file is uploaded to the server\n• Try a simpler command\n• Refresh the page and try again';

          const errorMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'assistant',
            content: errorContent,
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
        chatMessages: state.chatMessages.filter(msg => msg.type !== 'system').map(msg => ({
          ...msg,
          timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString()
        }))
      }),
      onRehydrateStorage: () => (state) => {
        if (state?.chatMessages) {
          // Convert timestamp strings back to Date objects
          state.chatMessages = state.chatMessages.map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }));
        }
      }
    }
  )
);