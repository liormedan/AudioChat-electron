export interface IPCMessage {
  id: string;
  service: string;
  method: string;
  payload: unknown;
  timestamp: number;
}

export interface IPCResponse {
  id: string;
  success: boolean;
  data?: unknown;
  error?: string;
  timestamp: number;
}

export interface ElectronAPI {
  // Window management
  minimize: () => Promise<void>;
  maximize: () => Promise<void>;
  close: () => Promise<void>;
  
  // File operations
  selectFile: (options?: { filters?: Array<{ name: string; extensions: string[] }> }) => Promise<string | null>;
  selectDirectory: () => Promise<string | null>;
  
  // Settings
  getSettings: () => Promise<Record<string, unknown>>;
  updateSettings: (settings: Record<string, unknown>) => Promise<void>;
  
  // Theme
  setTheme: (theme: 'light' | 'dark') => Promise<void>;
  getTheme: () => Promise<'light' | 'dark'>;
  
  // Notifications
  showNotification: (title: string, body: string) => Promise<void>;
  
  // Python backend communication
  callPythonService: (service: string, method: string, payload: unknown) => Promise<unknown>;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}