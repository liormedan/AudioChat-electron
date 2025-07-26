import { app, BrowserWindow, ipcMain, dialog, shell, Notification } from 'electron';
import { join } from 'path';
import { existsSync } from 'fs';

// Security: Disable node integration and enable context isolation
const isDev = process.env.NODE_ENV === 'development';

class MainWindow {
  private window: BrowserWindow | null = null;
  private readonly windowState = {
    width: 1200,
    height: 800,
    x: undefined as number | undefined,
    y: undefined as number | undefined,
  };

  constructor() {
    this.createWindow();
    this.setupIPC();
  }

  private createWindow(): void {
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
        preload: join(__dirname, '../preload/preload.js'),
      },
    });

    // Load the app
    // For testing, load the simple test to show implementation status
    const testPath = join(__dirname, '../../simple-test.html');
    const indexPath = join(__dirname, '../renderer/index.html');
    
    if (existsSync(testPath)) {
      void this.window.loadFile(testPath);
      // Always open DevTools for debugging
      this.window.webContents.openDevTools();
    } else if (existsSync(indexPath)) {
      void this.window.loadFile(indexPath);
      // Always open DevTools for debugging
      this.window.webContents.openDevTools();
    } else {
      console.error('No renderer found. Paths checked:');
      console.error('Test path:', testPath);
      console.error('Index path:', indexPath);
      console.error('Current __dirname:', __dirname);
      app.quit();
    }

    // Show window when ready
    this.window.once('ready-to-show', () => {
      this.window?.show();
      
      // Focus window on creation
      if (isDev) {
        this.window?.webContents.focus();
      }
    });

    // Handle window closed
    this.window.on('closed', () => {
      this.window = null;
    });

    // Save window state on resize/move
    this.window.on('resize', () => this.saveWindowState());
    this.window.on('move', () => this.saveWindowState());

    // Security: Prevent new window creation
    this.window.webContents.setWindowOpenHandler(() => {
      return { action: 'deny' };
    });

    // Security: Handle external links
    this.window.webContents.on('will-navigate', (event, navigationUrl) => {
      const parsedUrl = new URL(navigationUrl);
      
      if (parsedUrl.origin !== 'http://localhost:5174' && !isDev) {
        event.preventDefault();
        void shell.openExternal(navigationUrl);
      }
    });
  }

  private saveWindowState(): void {
    if (!this.window) return;
    
    const bounds = this.window.getBounds();
    this.windowState.width = bounds.width;
    this.windowState.height = bounds.height;
    this.windowState.x = bounds.x;
    this.windowState.y = bounds.y;
  }

  private setupIPC(): void {
    // Window management
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

    // File operations
    ipcMain.handle('file:select', async (_, options?: { filters?: Array<{ name: string; extensions: string[] }> }) => {
      if (!this.window) return null;
      
      const result = await dialog.showOpenDialog(this.window, {
        properties: ['openFile'],
        filters: options?.filters ?? [
          { name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'aac', 'm4a'] },
          { name: 'All Files', extensions: ['*'] }
        ]
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

    // Settings (placeholder - will be implemented with actual storage)
    ipcMain.handle('settings:get', async () => {
      // TODO: Implement actual settings storage
      return {};
    });

    ipcMain.handle('settings:update', async (_, settings: Record<string, unknown>) => {
      // TODO: Implement actual settings storage
      console.log('Settings updated:', settings);
    });

    // Theme management
    ipcMain.handle('theme:set', async (_, theme: 'light' | 'dark') => {
      // TODO: Implement theme persistence
      console.log('Theme set to:', theme);
    });

    ipcMain.handle('theme:get', async () => {
      // TODO: Implement theme persistence
      return 'light' as const;
    });

    // Notifications
    ipcMain.handle('notification:show', async (_, title: string, body: string) => {
      if (Notification.isSupported()) {
        new Notification({ title, body }).show();
      }
    });

    // Python backend communication (placeholder)
    ipcMain.handle('python:call', async (_, service: string, method: string, payload: unknown) => {
      // TODO: Implement actual Python backend communication
      console.log(`Python call: ${service}.${method}`, payload);
      return { success: true, data: null };
    });
  }

  public getWindow(): BrowserWindow | null {
    return this.window;
  }
}

// App event handlers
app.whenReady().then(() => {
  // Security: Set app user model ID for Windows
  if (process.platform === 'win32') {
    app.setAppUserModelId('com.audiochatstudio.electron');
  }

  const mainWindow = new MainWindow();

  app.on('activate', () => {
    // On macOS, re-create window when dock icon is clicked
    if (BrowserWindow.getAllWindows().length === 0) {
      new MainWindow();
    }
  });

  // Security: Prevent new window creation from renderer
  app.on('web-contents-created', (_, contents) => {
    contents.setWindowOpenHandler(() => {
      return { action: 'deny' };
    });
  });
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  // On macOS, keep app running even when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Security: Prevent navigation to external URLs
app.on('web-contents-created', (_, contents) => {
  contents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    
    if (parsedUrl.origin !== 'http://localhost:5174' && !isDev) {
      event.preventDefault();
    }
  });
});

// Handle certificate errors
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (isDev) {
    // In development, ignore certificate errors for localhost
    event.preventDefault();
    callback(true);
  } else {
    // In production, use default behavior
    callback(false);
  }
});