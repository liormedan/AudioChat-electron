import { app, BrowserWindow, ipcMain, dialog, Notification } from 'electron';
import { join, resolve, dirname } from 'path';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { ServiceManager } from './service-manager';
// In Electron/Node.js CommonJS context, __filename and __dirname are available
// We'll use them directly since we're in a CommonJS environment

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
  private serviceManager: ServiceManager | null = null;
  private windowState: WindowState = {
    width: 1200,
    height: 800,
  };
  private windowStateFile = join(app.getPath('userData'), 'window-state.json');
  private saveStateTimer: NodeJS.Timeout | null = null;
  private readonly debounceDelay = 500;
  private isIntegratedMode = false;

  constructor() {
    // Check if running in integrated mode
    this.isIntegratedMode = process.argv.includes('--integrated');
    
    this.loadWindowState();
    this.createWindow();
    this.setupIPC();
    
    // Initialize ServiceManager if in integrated mode
    if (this.isIntegratedMode && this.window) {
      this.serviceManager = new ServiceManager(this.window);
    }
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
    this.window = new BrowserWindow({
      width: this.windowState.width,
      height: this.windowState.height,
      x: this.windowState.x,
      y: this.windowState.y,
      minWidth: 800,
      minHeight: 600,
      show: false,
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      webPreferences: {
        contextIsolation: true,
        nodeIntegration: false,
        webSecurity: true,
        preload: join(__dirname, '../preload/preload/preload.js'),
      },
    });

    if (isDev) {
      const devServerUrl = process.env.VITE_DEV_SERVER_URL ?? 'http://localhost:5176';
      console.log('Loading renderer from dev server:', devServerUrl);
      void this.window.loadURL(devServerUrl);
    } else {
      const indexPath = resolve(__dirname, '..', '..', 'renderer', 'index.html');
      console.log('📂 Checking renderer index.html');
      console.log('⛳ Path:', indexPath);
      console.log('✅ Exists?', existsSync(indexPath));

      if (existsSync(indexPath)) {
        void this.window.loadFile(indexPath);
      } else {
        console.error('❌ No renderer found. App will exit.');
        app.quit();
        return;
      }
    }

    if (shouldOpenDevTools) {
      this.window.webContents.openDevTools();
    }

    this.window.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
      console.error('Failed to load:', errorCode, errorDescription);
    });

    this.window.webContents.on('crashed', () => {
      console.error('Renderer process crashed');
    });

    this.window.once('ready-to-show', () => {
      if (this.windowState.isMaximized) {
        this.window?.maximize();
      }
      this.window?.show();
      this.window?.webContents.focus();
    });

    this.window.on('closed', () => {
      this.clearSaveTimer();
      this.saveWindowStateNow();
      this.window = null;
    });

    this.window.on('resize', () => this.scheduleSaveWindowState());
    this.window.on('move', () => this.scheduleSaveWindowState());
  }

  private setupIPC() {
    ipcMain.handle('window:minimize', () => this.window?.minimize());
    ipcMain.handle('window:maximize', () => {
      this.window?.isMaximized() ? this.window.unmaximize() : this.window?.maximize();
    });
    ipcMain.handle('window:close', () => this.window?.close());

    ipcMain.handle('window:getState', () => {
      if (!this.window) return null;
      const bounds = this.window.getBounds();
      return { ...bounds, isMaximized: this.window.isMaximized() };
    });

    ipcMain.handle('window:setBounds', (_, bounds) => {
      this.window?.setBounds(bounds);
    });

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

    ipcMain.handle('settings:get', () => ({}));
    ipcMain.handle('settings:update', (_, settings) => {
      console.log('Settings updated:', settings);
    });

    ipcMain.handle('theme:set', (_, theme) => {
      console.log('Theme set to:', theme);
    });
    ipcMain.handle('theme:get', () => 'light');

    ipcMain.handle('notification:show', (_, title, body) => {
      new Notification({ title, body }).show();
    });

    ipcMain.handle('python:call', async (_, service, method, payload) => {
      console.log(`Python call: ${service}.${method}`, payload);
      return { success: true, message: 'Python backend not implemented yet' };
    });

    // Service Management IPC handlers
    ipcMain.handle('services:start', async () => {
      if (this.serviceManager) {
        await this.serviceManager.startAllServices();
        return { success: true };
      }
      return { success: false, error: 'Service manager not available' };
    });

    ipcMain.handle('services:stop', async () => {
      if (this.serviceManager) {
        await this.serviceManager.stopAllServices();
        return { success: true };
      }
      return { success: false, error: 'Service manager not available' };
    });

    ipcMain.handle('services:restart', async (_, serviceName: string) => {
      if (this.serviceManager) {
        await this.serviceManager.restartService(serviceName);
        return { success: true };
      }
      return { success: false, error: 'Service manager not available' };
    });

    ipcMain.handle('services:status', async (_, serviceName?: string) => {
      if (this.serviceManager) {
        if (serviceName) {
          return this.serviceManager.getServiceStatus(serviceName);
        } else {
          return this.serviceManager.getAllServiceStatus();
        }
      }
      return null;
    });

    ipcMain.handle('services:health', async () => {
      if (this.serviceManager) {
        return await this.serviceManager.checkHealth();
      }
      return {};
    });

    ipcMain.handle('app:isIntegrated', () => {
      return this.isIntegratedMode;
    });
  }
}

app.whenReady().then(() => {
  console.log('⚡ App is ready, creating main window...');
  new MainWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    new MainWindow();
  }
});
