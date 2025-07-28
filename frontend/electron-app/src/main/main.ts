import { app, BrowserWindow, ipcMain, dialog, Notification } from 'electron';
import { join } from 'path';
import { existsSync, readFileSync, writeFileSync } from 'fs';

// Security: Disable node integration and enable context isolation
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
const shouldOpenDevTools = ['1', 'true'].includes(
  (process.env.OPEN_DEVTOOLS ?? '').toLowerCase()
);

interface WindowState {
  width: number;
  height: number;
  x?: number;
  y?: number;
  isMaximized?: boolean;
}

class MainWindow {
  private window: BrowserWindow | null = null;
  private windowState: WindowState = {
    width: 1200,
    height: 800,
  };
  private windowStateFile = join(app.getPath('userData'), 'window-state.json');
  private saveStateTimer: NodeJS.Timeout | null = null;
  private readonly debounceDelay = 500;

  constructor() {
    this.loadWindowState();
    this.createWindow();
    this.setupIPC();
  }

  private loadWindowState() {
    try {
      if (existsSync(this.windowStateFile)) {
        const state = JSON.parse(readFileSync(this.windowStateFile, 'utf-8'));
        this.windowState = { ...this.windowState, ...state };
      }
    } catch (error) {
      console.error('Failed to load window state:', error);
    }
  }

  private saveWindowStateNow() {
    if (this.window && !this.window.isDestroyed()) {
      if (this.window.isMaximized()) {
        this.windowState.isMaximized = true;
      } else {
        this.windowState.isMaximized = false;
        const bounds = this.window.getBounds();
        this.windowState.width = bounds.width;
        this.windowState.height = bounds.height;
        this.windowState.x = bounds.x;
        this.windowState.y = bounds.y;
      }
      try {
        writeFileSync(this.windowStateFile, JSON.stringify(this.windowState));
      } catch (error) {
        console.error('Failed to save window state:', error);
      }
    }
  }

  private scheduleSaveWindowState() {
    this.clearSaveTimer();
    this.saveStateTimer = setTimeout(() => this.saveWindowStateNow(), this.debounceDelay);
  }

  private clearSaveTimer() {
    if (this.saveStateTimer) {
      clearTimeout(this.saveStateTimer);
      this.saveStateTimer = null;
    }
  }

  private createWindow() {
    // Create the browser window with security best practices
    this.window = new BrowserWindow({
      width: this.windowState.width,
      height: this.windowState.height,
      x: this.windowState.x,
      y: this.windowState.y,
      minWidth: 800,
      minHeight: 600,
      show: false, // Don't show until ready
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      webPreferences: {
        // Security: Enable context isolation and disable node integration
        contextIsolation: true,
        nodeIntegration: false,
        nodeIntegrationInWorker: false,
        nodeIntegrationInSubFrames: false,
        // enableRemoteModule is deprecated in newer Electron versions
        webSecurity: true,
        allowRunningInsecureContent: false,
        experimentalFeatures: false,
        // Preload script for secure IPC
        preload: join(__dirname, '../preload/preload/preload.js'),
      },
    });

    // Load the application UI
    // __dirname is dist/main/main, so we need to go up to dist/renderer
    const indexPath = join(__dirname, '../../renderer/index.html');
    console.log('Loading renderer from:', indexPath);
    console.log('File exists:', existsSync(indexPath));

    if (existsSync(indexPath)) {
      void this.window.loadFile(indexPath);
    } else {
      console.error('No renderer found. Path checked:', indexPath);
      console.error('Current __dirname:', __dirname);
      app.quit();
      return;
    }

    // Always open DevTools for debugging
    this.window.webContents.openDevTools();
    
    // Add error handling
    this.window.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
      console.error('Failed to load:', errorCode, errorDescription);
    });
    
    this.window.webContents.on('crashed', () => {
      console.error('Renderer process crashed');
    });

    // Show window when ready
    this.window.once('ready-to-show', () => {
      console.log('Window ready to show');
      if (this.windowState.isMaximized) {
        this.window?.maximize();
      }
      this.window?.show();
      
      // Focus window on creation
      this.window?.webContents.focus();
    });

    // Handle window closed
    this.window.on('closed', () => {
      this.clearSaveTimer();
      this.saveWindowStateNow();
      this.window = null;
    });

    // Save window state on resize/move
    this.window.on('resize', () => this.scheduleSaveWindowState());
    this.window.on('move', () => this.scheduleSaveWindowState());
  }

  private setupIPC() {
    // Window management handlers
    ipcMain.handle('window:minimize', () => {
      this.window?.minimize();
    });

    ipcMain.handle('window:maximize', () => {
      if (this.window?.isMaximized()) {
        this.window.unmaximize();
      } else {
        this.window?.maximize();
      }
    });

    ipcMain.handle('window:close', () => {
      this.window?.close();
    });

    ipcMain.handle('window:getState', () => {
      if (!this.window) return null;
      const bounds = this.window.getBounds();
      return {
        width: bounds.width,
        height: bounds.height,
        x: bounds.x,
        y: bounds.y,
        isMaximized: this.window.isMaximized()
      };
    });

    ipcMain.handle('window:setBounds', (_, bounds) => {
      this.window?.setBounds(bounds);
    });

    // File operations
    ipcMain.handle('file:select', async (_, options) => {
      if (!this.window) return null;
      const result = await dialog.showOpenDialog(this.window, {
        properties: ['openFile'],
        filters: options?.filters || []
      });
      return result.canceled ? null : result.filePaths[0];
    });

    ipcMain.handle('file:selectDirectory', async () => {
      if (!this.window) return null;
      const result = await dialog.showOpenDialog(this.window, {
        properties: ['openDirectory']
      });
      return result.canceled ? null : result.filePaths[0];
    });

    // Settings (placeholder)
    ipcMain.handle('settings:get', () => {
      return {};
    });

    ipcMain.handle('settings:update', (_, settings) => {
      // Implement settings storage
      console.log('Settings updated:', settings);
    });

    // Theme (placeholder)
    ipcMain.handle('theme:set', (_, theme) => {
      console.log('Theme set to:', theme);
    });

    ipcMain.handle('theme:get', () => {
      return 'light';
    });

    // Notifications
    ipcMain.handle('notification:show', (_, title, body) => {
      new Notification({ title, body }).show();
    });

    // Python backend communication (placeholder)
    ipcMain.handle('python:call', async (_, service, method, payload) => {
      console.log(`Python call: ${service}.${method}`, payload);
      // This would normally communicate with the Python backend
      return { success: true, message: 'Python backend not implemented yet' };
    });
  }
}

app.whenReady().then(() => {
  console.log('App is ready, creating main window...');
  new MainWindow();
});

app.on('window-all-closed', () => {
  console.log('All windows closed');
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  console.log('App activated');
  if (BrowserWindow.getAllWindows().length === 0) {
    new MainWindow();
  }
});
