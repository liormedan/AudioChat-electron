import { contextBridge, ipcRenderer } from 'electron';
import type { ElectronAPI } from '../shared/types/ipc';

// Security: Validate IPC messages
const validateIPCCall = (channel: string, ...args: unknown[]): boolean => {
  // Define allowed IPC channels
  const allowedChannels = [
    'window:minimize',
    'window:maximize', 
    'window:close',
    'window:getState',
    'window:setBounds',
    'file:select',
    'file:selectDirectory',
    'settings:get',
    'settings:update',
    'theme:set',
    'theme:get',
    'notification:show',
    'python:call',
    'services:start',
    'services:stop',
    'services:restart',
    'services:status',
    'services:health',
    'app:isIntegrated'
  ];

  if (!allowedChannels.includes(channel)) {
    console.error(`Blocked IPC call to unauthorized channel: ${channel}`);
    return false;
  }

  return true;
};

// Create secure API object
const electronAPI: ElectronAPI = {
  // Window management
  minimize: async (): Promise<void> => {
    if (validateIPCCall('window:minimize')) {
      return ipcRenderer.invoke('window:minimize');
    }
  },

  maximize: async (): Promise<void> => {
    if (validateIPCCall('window:maximize')) {
      return ipcRenderer.invoke('window:maximize');
    }
  },

  close: async (): Promise<void> => {
    if (validateIPCCall('window:close')) {
      return ipcRenderer.invoke('window:close');
    }
  },

  getWindowState: async (): Promise<{ width: number; height: number; x?: number; y?: number; isMaximized?: boolean } | null> => {
    if (validateIPCCall('window:getState')) {
      return ipcRenderer.invoke('window:getState');
    }
    return null;
  },

  setWindowBounds: async (bounds: { width: number; height: number; x?: number; y?: number }): Promise<void> => {
    if (validateIPCCall('window:setBounds', bounds)) {
      return ipcRenderer.invoke('window:setBounds', bounds);
    }
  },

  // File operations
  selectFile: async (options?: { filters?: Array<{ name: string; extensions: string[] }> }): Promise<string | null> => {
    if (validateIPCCall('file:select', options)) {
      return ipcRenderer.invoke('file:select', options);
    }
    return null;
  },

  selectDirectory: async (): Promise<string | null> => {
    if (validateIPCCall('file:selectDirectory')) {
      return ipcRenderer.invoke('file:selectDirectory');
    }
    return null;
  },

  // Settings
  getSettings: async (): Promise<Record<string, unknown>> => {
    if (validateIPCCall('settings:get')) {
      return ipcRenderer.invoke('settings:get');
    }
    return {};
  },

  updateSettings: async (settings: Record<string, unknown>): Promise<void> => {
    if (validateIPCCall('settings:update', settings)) {
      return ipcRenderer.invoke('settings:update', settings);
    }
  },

  // Theme
  setTheme: async (theme: 'light' | 'dark'): Promise<void> => {
    if (validateIPCCall('theme:set', theme)) {
      return ipcRenderer.invoke('theme:set', theme);
    }
  },

  getTheme: async (): Promise<'light' | 'dark'> => {
    if (validateIPCCall('theme:get')) {
      return ipcRenderer.invoke('theme:get');
    }
    return 'light';
  },

  // Notifications
  showNotification: async (title: string, body: string): Promise<void> => {
    if (validateIPCCall('notification:show', title, body)) {
      return ipcRenderer.invoke('notification:show', title, body);
    }
  },

  // Python backend communication
  callPythonService: async (service: string, method: string, payload: unknown): Promise<unknown> => {
    if (validateIPCCall('python:call', service, method, payload)) {
      return ipcRenderer.invoke('python:call', service, method, payload);
    }
    return null;
  },

  // Service Management
  startServices: async (): Promise<{ success: boolean; error?: string }> => {
    if (validateIPCCall('services:start')) {
      return ipcRenderer.invoke('services:start');
    }
    return { success: false, error: 'IPC validation failed' };
  },

  stopServices: async (): Promise<{ success: boolean; error?: string }> => {
    if (validateIPCCall('services:stop')) {
      return ipcRenderer.invoke('services:stop');
    }
    return { success: false, error: 'IPC validation failed' };
  },

  restartService: async (serviceName: string): Promise<{ success: boolean; error?: string }> => {
    if (validateIPCCall('services:restart', serviceName)) {
      return ipcRenderer.invoke('services:restart', serviceName);
    }
    return { success: false, error: 'IPC validation failed' };
  },

  getServiceStatus: async (serviceName?: string): Promise<any> => {
    if (validateIPCCall('services:status', serviceName)) {
      return ipcRenderer.invoke('services:status', serviceName);
    }
    return null;
  },

  checkServicesHealth: async (): Promise<{ [key: string]: boolean }> => {
    if (validateIPCCall('services:health')) {
      return ipcRenderer.invoke('services:health');
    }
    return {};
  },

  isIntegratedMode: async (): Promise<boolean> => {
    if (validateIPCCall('app:isIntegrated')) {
      return ipcRenderer.invoke('app:isIntegrated');
    }
    return false;
  },

  // Event listeners for real-time updates
  onTerminalLog: (callback: (log: any) => void) => {
    ipcRenderer.on('terminal:log', (_, log) => callback(log));
    return () => ipcRenderer.removeAllListeners('terminal:log');
  },

  onServiceStatus: (callback: (serviceName: string, status: any) => void) => {
    ipcRenderer.on('service:status', (_, serviceName, status) => callback(serviceName, status));
    return () => ipcRenderer.removeAllListeners('service:status');
  },
};

// Security: Expose API through context bridge
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Security: Remove any global Node.js objects that might have leaked
delete (globalThis as any).global;
delete (globalThis as any).Buffer;
delete (globalThis as any).process;
delete (globalThis as any).clearImmediate;
delete (globalThis as any).setImmediate;