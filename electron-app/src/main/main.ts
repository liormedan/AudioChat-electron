import { app, BrowserWindow, ipcMain, dialog, shell, Notification, screen } from 'electron';
import { join } from 'path';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { spawn, ChildProcessWithoutNullStreams } from 'child_process'; // Import spawn

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

let pythonProcess: ChildProcessWithoutNullStreams | null = null; // Declare pythonProcess

function startPythonBackend() {
  const pythonExecutable = process.platform === 'win32' ? 'server_dist.exe' : 'server_dist';
  const pythonPath = isDev
    ? join(__dirname, '../../server.py') // Adjust path for development
    : join(process.resourcesPath, 'python', pythonExecutable); // Path in packaged app

  console.log(`Attempting to start Python backend from: ${pythonPath}`);

  if (isDev) {
    pythonProcess = spawn('python', [pythonPath]);
  } else {
    pythonProcess = spawn(pythonPath);
  }

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data.toString()}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data.toString()}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    pythonProcess = null;
  });

  pythonProcess.on('error', (err) => {
    console.error('Failed to start Python process:', err);
    dialog.showErrorBox('Application Error', 'Failed to start Python backend. Please check logs.');
    app.quit();
  });
}

function stopPythonBackend() {
  if (pythonProcess) {
    console.log('Stopping Python backend...');
    pythonProcess.kill(); // Send SIGTERM to the process
    pythonProcess = null;
  }
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
        preload: join(__dirname, '../preload/preload.js'),
      },
    });

    // Load the application UI
    const indexPath = join(__dirname, '../renderer/index.html');

    if (existsSync(indexPath)) {
      void this.window.loadFile(indexPath);
    } else {
      console.error('No renderer found. Path checked:', indexPath);
      console.error('Current __dirname:', __dirname);
      app.quit();
      return;
    }

    // Optionally open DevTools in development
    if (isDev && shouldOpenDevTools) {
      this.window.webContents.openDevTools();
    }

    // Show window when ready
    this.window.once('ready-to-show', () => {
      if (this.windowState.isMaximized) {
        this.window?.maximize();
      }
      this.window?.show();
      
      // Focus window on creation
      if (isDev) {
        this.window?.webContents.focus();
      }
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
    // IPC handlers
  }
}

app.whenReady().then(() => {
  startPythonBackend(); // Start Python backend when app is ready
  new MainWindow();
});

app.on('window-all-closed', () => {
  stopPythonBackend(); // Stop Python backend when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    new MainWindow();
  }
});
