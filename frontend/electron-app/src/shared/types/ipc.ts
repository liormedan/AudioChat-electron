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

export interface TerminalLog {
  service: string;
  type: 'info' | 'error' | 'success' | 'warning';
  message: string;
  timestamp: Date;
}

export interface ServiceStatus {
  name: string;
  status: 'starting' | 'running' | 'stopped' | 'error';
  port?: number;
  pid?: number;
  uptime?: number;
  lastError?: string;
}

export interface ElectronAPI {
  // Window management
  minimize: () => Promise<void>;
  maximize: () => Promise<void>;
  close: () => Promise<void>;
  getWindowState: () => Promise<{ width: number; height: number; x?: number; y?: number; isMaximized?: boolean } | null>;
  setWindowBounds: (bounds: { width: number; height: number; x?: number; y?: number }) => Promise<void>;
  
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
  
  // Service Management
  startServices: () => Promise<{ success: boolean; error?: string }>;
  stopServices: () => Promise<{ success: boolean; error?: string }>;
  restartService: (serviceName: string) => Promise<{ success: boolean; error?: string }>;
  getServiceStatus: (serviceName?: string) => Promise<ServiceStatus | ServiceStatus[] | null>;
  checkServicesHealth: () => Promise<{ [key: string]: boolean }>;
  isIntegratedMode: () => Promise<boolean>;
  
  // Event listeners
  onTerminalLog: (callback: (log: TerminalLog) => void) => () => void;
  onServiceStatus: (callback: (serviceName: string, status: ServiceStatus) => void) => () => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}