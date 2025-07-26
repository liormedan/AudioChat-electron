import { contextBridge, ipcRenderer } from 'electron';
import type { ElectronAPI } from '../shared/types/ipc';

// Security: Validate IPC messages
const validateIPCCall = (channel: string, ...args: unknown[]): boolean => {
  // Define allowed IPC channels
  const allowedChannels = [
    'window:minimize',
    'window:maximize', 
    'window:close',
    'file:select',
    'file:selectDirectory',
    'settings:get',
    'settings:update',
    'theme:set',
    'theme:get',
    'notification:show',
    'python:call'
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
};

// Security: Expose API through context bridge
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Security: Remove any global Node.js objects that might have leaked
delete (globalThis as any).global;
delete (globalThis as any).Buffer;
delete (globalThis as any).process;
delete (globalThis as any).clearImmediate;
delete (globalThis as any).setImmediate;