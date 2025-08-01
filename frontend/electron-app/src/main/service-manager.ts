import { spawn, ChildProcess } from 'child_process';
import { BrowserWindow } from 'electron';
import { join } from 'path';
import { existsSync } from 'fs';

export interface ServiceStatus {
  name: string;
  status: 'starting' | 'running' | 'stopped' | 'error';
  port?: number;
  pid?: number;
  uptime?: number;
  lastError?: string;
}

export interface TerminalLog {
  service: string;
  type: 'info' | 'error' | 'success' | 'warning';
  message: string;
  timestamp: Date;
}

export class ServiceManager {
  private window: BrowserWindow;
  private services: Map<string, ChildProcess> = new Map();
  private serviceStatus: Map<string, ServiceStatus> = new Map();
  private projectRoot: string;
  private startTimes: Map<string, Date> = new Map();

  constructor(window: BrowserWindow) {
    this.window = window;
    this.projectRoot = join(__dirname, '../../../..');
    
    // Initialize service status
    this.initializeServiceStatus();
  }

  private initializeServiceStatus() {
    const services = ['backend', 'admin', 'frontend'];
    services.forEach(service => {
      this.serviceStatus.set(service, {
        name: service,
        status: 'stopped'
      });
    });
  }

  private sendLog(service: string, type: TerminalLog['type'], message: string) {
    const log: TerminalLog = {
      service,
      type,
      message: message.trim(),
      timestamp: new Date()
    };
    
    this.window.webContents.send('terminal:log', log);
  }

  private updateServiceStatus(serviceName: string, updates: Partial<ServiceStatus>) {
    const current = this.serviceStatus.get(serviceName);
    if (current) {
      const updated = { ...current, ...updates };
      
      // Calculate uptime if service is running
      if (updated.status === 'running' && this.startTimes.has(serviceName)) {
        const startTime = this.startTimes.get(serviceName)!;
        updated.uptime = Date.now() - startTime.getTime();
      }
      
      this.serviceStatus.set(serviceName, updated);
      this.window.webContents.send('service:status', serviceName, updated);
    }
  }

  async startBackend(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.sendLog('backend', 'info', '🔵 Starting Backend API Server...');
      this.updateServiceStatus('backend', { status: 'starting' });

      const pythonPath = join(this.projectRoot, '.venv', 'Scripts', 'python.exe');
      const backendScript = join(this.projectRoot, 'backend', 'main.py');

      if (!existsSync(pythonPath)) {
        const error = 'Python virtual environment not found';
        this.sendLog('backend', 'error', `❌ ${error}`);
        this.updateServiceStatus('backend', { status: 'error', lastError: error });
        reject(new Error(error));
        return;
      }

      const backendProcess = spawn(pythonPath, [
        backendScript,
        '--host', '127.0.0.1',
        '--port', '5000'
      ], {
        cwd: this.projectRoot,
        stdio: 'pipe',
        env: { ...process.env, PYTHONPATH: this.projectRoot }
      });

      this.services.set('backend', backendProcess);
      this.startTimes.set('backend', new Date());

      backendProcess.stdout?.on('data', (data) => {
        const message = data.toString();
        this.sendLog('backend', 'info', message);
        
        // Check if server started successfully
        if (message.includes('Application startup complete') || message.includes('Uvicorn running')) {
          this.updateServiceStatus('backend', { 
            status: 'running', 
            port: 5000, 
            pid: backendProcess.pid 
          });
          this.sendLog('backend', 'success', '✅ Backend API Server started successfully');
          resolve();
        }
      });

      backendProcess.stderr?.on('data', (data) => {
        const message = data.toString();
        this.sendLog('backend', 'error', message);
        
        if (message.includes('Address already in use')) {
          this.updateServiceStatus('backend', { 
            status: 'error', 
            lastError: 'Port 5000 already in use' 
          });
        }
      });

      backendProcess.on('error', (error) => {
        this.sendLog('backend', 'error', `❌ Backend process error: ${error.message}`);
        this.updateServiceStatus('backend', { 
          status: 'error', 
          lastError: error.message 
        });
        reject(error);
      });

      backendProcess.on('exit', (code) => {
        this.sendLog('backend', code === 0 ? 'info' : 'error', 
          `🔵 Backend process exited with code ${code}`);
        this.updateServiceStatus('backend', { status: 'stopped' });
        this.services.delete('backend');
        this.startTimes.delete('backend');
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.serviceStatus.get('backend')?.status === 'starting') {
          this.sendLog('backend', 'warning', '⚠️ Backend startup timeout, but continuing...');
          this.updateServiceStatus('backend', { status: 'running', port: 5000 });
          resolve();
        }
      }, 30000);
    });
  }

  async startAdmin(): Promise<void> {
    return new Promise((resolve) => {
      const adminScript = join(this.projectRoot, 'backend', 'admin', 'main.py');
      
      if (!existsSync(adminScript)) {
        this.sendLog('admin', 'warning', '⚠️ Admin interface not found, skipping...');
        this.updateServiceStatus('admin', { status: 'stopped' });
        resolve();
        return;
      }

      this.sendLog('admin', 'info', '🟢 Starting Admin Interface...');
      this.updateServiceStatus('admin', { status: 'starting' });

      const pythonPath = join(this.projectRoot, '.venv', 'Scripts', 'python.exe');
      const adminProcess = spawn(pythonPath, [adminScript], {
        cwd: join(this.projectRoot, 'backend', 'admin'),
        stdio: 'pipe',
        env: { ...process.env, PYTHONPATH: this.projectRoot }
      });

      this.services.set('admin', adminProcess);
      this.startTimes.set('admin', new Date());

      adminProcess.stdout?.on('data', (data) => {
        const message = data.toString();
        this.sendLog('admin', 'info', message);
        
        if (message.includes('running') || message.includes('5001')) {
          this.updateServiceStatus('admin', { 
            status: 'running', 
            port: 5001, 
            pid: adminProcess.pid 
          });
          this.sendLog('admin', 'success', '✅ Admin Interface started successfully');
        }
      });

      adminProcess.stderr?.on('data', (data) => {
        this.sendLog('admin', 'error', data.toString());
      });

      adminProcess.on('exit', (code) => {
        this.sendLog('admin', 'info', `🟢 Admin process exited with code ${code}`);
        this.updateServiceStatus('admin', { status: 'stopped' });
        this.services.delete('admin');
        this.startTimes.delete('admin');
      });

      // Admin is optional, so resolve after a short delay
      setTimeout(() => {
        resolve();
      }, 3000);
    });
  }

  async startFrontendDev(): Promise<void> {
    return new Promise((resolve) => {
      this.sendLog('frontend', 'info', '🎨 Frontend Dev Server already running in this process');
      this.updateServiceStatus('frontend', { 
        status: 'running', 
        port: 5176,
        pid: process.pid
      });
      this.sendLog('frontend', 'success', '✅ Frontend Dev Server is active');
      resolve();
    });
  }

  async startAllServices(): Promise<void> {
    this.sendLog('system', 'info', '🚀 Starting all services...');
    
    try {
      // Start services in sequence
      await this.startBackend();
      await this.startAdmin();
      await this.startFrontendDev();
      
      this.sendLog('system', 'success', '✅ All services started successfully!');
      this.sendLog('system', 'info', '📱 Application ready for use');
      
    } catch (error) {
      this.sendLog('system', 'error', `❌ Failed to start services: ${error}`);
    }
  }

  async stopService(serviceName: string): Promise<void> {
    const process = this.services.get(serviceName);
    if (process) {
      this.sendLog(serviceName, 'info', `🛑 Stopping ${serviceName} service...`);
      process.kill('SIGTERM');
      
      // Force kill after 5 seconds
      setTimeout(() => {
        if (!process.killed) {
          process.kill('SIGKILL');
        }
      }, 5000);
    }
  }

  async stopAllServices(): Promise<void> {
    this.sendLog('system', 'info', '🛑 Stopping all services...');
    
    const serviceNames = Array.from(this.services.keys());
    await Promise.all(serviceNames.map(name => this.stopService(name)));
    
    this.sendLog('system', 'success', '✅ All services stopped');
  }

  async restartService(serviceName: string): Promise<void> {
    this.sendLog(serviceName, 'info', `🔄 Restarting ${serviceName} service...`);
    
    await this.stopService(serviceName);
    
    // Wait a bit before restarting
    setTimeout(async () => {
      switch (serviceName) {
        case 'backend':
          await this.startBackend();
          break;
        case 'admin':
          await this.startAdmin();
          break;
        case 'frontend':
          await this.startFrontendDev();
          break;
      }
    }, 2000);
  }

  getServiceStatus(serviceName: string): ServiceStatus | undefined {
    return this.serviceStatus.get(serviceName);
  }

  getAllServiceStatus(): ServiceStatus[] {
    return Array.from(this.serviceStatus.values());
  }

  async checkHealth(): Promise<{ [key: string]: boolean }> {
    const health: { [key: string]: boolean } = {};
    
    // Check Backend
    try {
      const response = await fetch('http://127.0.0.1:5000/health', { 
        method: 'GET',
        timeout: 5000 
      } as any);
      health.backend = response.ok;
    } catch {
      health.backend = false;
    }
    
    // Check Admin
    try {
      const response = await fetch('http://127.0.0.1:5001/', { 
        method: 'GET',
        timeout: 5000 
      } as any);
      health.admin = response.ok;
    } catch {
      health.admin = false;
    }
    
    // Frontend is always healthy if we're running
    health.frontend = true;
    
    return health;
  }
}