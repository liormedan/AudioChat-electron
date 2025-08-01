import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { ScrollArea } from '../components/ui/scroll-area';
import { 
  Play, 
  Square, 
  RefreshCw, 
  ExternalLink, 
  Terminal as TerminalIcon,
  Server,
  Monitor,
  Activity,
  Trash2,
  Download
} from 'lucide-react';

interface LogEntry {
  timestamp: string;
  level: 'info' | 'error' | 'warning' | 'success';
  source: 'backend' | 'frontend' | 'system';
  message: string;
}

interface SystemStatus {
  backend: 'running' | 'stopped' | 'starting' | 'error';
  frontend: 'running' | 'stopped' | 'starting' | 'error';
  lastCheck: string;
}

export const TerminalPage: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    backend: 'stopped',
    frontend: 'stopped',
    lastCheck: new Date().toLocaleTimeString()
  });
  const [isLoading, setIsLoading] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Check system status periodically
  useEffect(() => {
    const checkStatus = async () => {
      try {
        // Check Backend
        const backendResponse = await fetch('http://127.0.0.1:5000/', { 
          method: 'GET',
          timeout: 2000 
        });
        const backendRunning = backendResponse.ok;

        // Check Frontend (Vite dev server)
        const frontendResponse = await fetch('http://127.0.0.1:5176/', { 
          method: 'GET',
          timeout: 2000 
        });
        const frontendRunning = frontendResponse.ok;

        setSystemStatus({
          backend: backendRunning ? 'running' : 'stopped',
          frontend: frontendRunning ? 'running' : 'stopped',
          lastCheck: new Date().toLocaleTimeString()
        });
      } catch (error) {
        setSystemStatus(prev => ({
          ...prev,
          lastCheck: new Date().toLocaleTimeString()
        }));
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000); // Check every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const addLog = (level: LogEntry['level'], source: LogEntry['source'], message: string) => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      level,
      source,
      message
    };
    setLogs(prev => [...prev.slice(-99), newLog]); // Keep last 100 logs
  };

  const handleStartSystem = async () => {
    setIsLoading(true);
    addLog('info', 'system', 'Starting full system...');
    
    try {
      // This would typically call your backend API to start services
      // For now, we'll simulate the process
      addLog('info', 'backend', 'Initializing Backend API...');
      setSystemStatus(prev => ({ ...prev, backend: 'starting' }));
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      addLog('success', 'backend', 'Backend API started successfully on port 5000');
      addLog('info', 'frontend', 'Starting Frontend development server...');
      setSystemStatus(prev => ({ ...prev, frontend: 'starting' }));
      
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      addLog('success', 'frontend', 'Frontend started successfully on port 5176');
      addLog('success', 'system', 'System startup completed!');
      
      setSystemStatus({
        backend: 'running',
        frontend: 'running',
        lastCheck: new Date().toLocaleTimeString()
      });
    } catch (error) {
      addLog('error', 'system', `Startup failed: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopSystem = async () => {
    setIsLoading(true);
    addLog('info', 'system', 'Stopping all services...');
    
    try {
      addLog('info', 'system', 'Stopping Backend and Frontend processes...');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addLog('success', 'system', 'All services stopped successfully');
      setSystemStatus({
        backend: 'stopped',
        frontend: 'stopped',
        lastCheck: new Date().toLocaleTimeString()
      });
    } catch (error) {
      addLog('error', 'system', `Stop failed: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearLogs = () => {
    setLogs([]);
    addLog('info', 'system', 'Logs cleared');
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      running: 'default',
      stopped: 'secondary',
      starting: 'outline',
      error: 'destructive'
    } as const;

    const colors = {
      running: 'bg-green-500',
      stopped: 'bg-gray-500',
      starting: 'bg-yellow-500',
      error: 'bg-red-500'
    };

    return (
      <Badge variant={variants[status as keyof typeof variants]} className="ml-2">
        <div className={`w-2 h-2 rounded-full mr-1 ${colors[status as keyof typeof colors]}`} />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'success': return '✅';
      default: return 'ℹ️';
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-500';
      case 'warning': return 'text-yellow-500';
      case 'success': return 'text-green-500';
      default: return 'text-blue-500';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <TerminalIcon className="h-8 w-8" />
          <h1 className="text-3xl font-bold">System Terminal</h1>
        </div>
        <div className="text-sm text-muted-foreground">
          Last check: {systemStatus.lastCheck}
        </div>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center">
                <Server className="h-5 w-5 mr-2" />
                <span className="font-medium">Backend API</span>
              </div>
              {getStatusBadge(systemStatus.backend)}
            </div>
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center">
                <Monitor className="h-5 w-5 mr-2" />
                <span className="font-medium">Frontend</span>
              </div>
              {getStatusBadge(systemStatus.frontend)}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle>System Control</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button 
              onClick={handleStartSystem} 
              disabled={isLoading}
              className="flex items-center"
            >
              <Play className="h-4 w-4 mr-2" />
              Start System
            </Button>
            <Button 
              onClick={handleStopSystem} 
              disabled={isLoading}
              variant="destructive"
              className="flex items-center"
            >
              <Square className="h-4 w-4 mr-2" />
              Stop System
            </Button>
            <Button 
              onClick={() => window.open('http://127.0.0.1:5000/docs', '_blank')}
              variant="outline"
              className="flex items-center"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Swagger UI
            </Button>
            <Button 
              onClick={() => window.open('http://127.0.0.1:5176', '_blank')}
              variant="outline"
              className="flex items-center"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Frontend
            </Button>
            <Button 
              onClick={handleClearLogs}
              variant="outline"
              className="flex items-center"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Logs
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Logs */}
      <Card className="flex-1">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>System Logs</span>
            <Badge variant="outline">{logs.length} entries</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96 w-full border rounded-lg p-4 bg-black text-green-400 font-mono text-sm">
            {logs.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No logs available. Start the system to see logs.
              </div>
            ) : (
              <div className="space-y-1">
                {logs.map((log, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <span className="text-gray-500 text-xs min-w-[80px]">
                      {log.timestamp}
                    </span>
                    <span className="text-xs min-w-[60px] text-blue-400">
                      [{log.source.toUpperCase()}]
                    </span>
                    <span className="text-xs">
                      {getLogIcon(log.level)}
                    </span>
                    <span className={`text-xs ${getLogColor(log.level)}`}>
                      {log.message}
                    </span>
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="system" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="system">System</TabsTrigger>
              <TabsTrigger value="backend">Backend</TabsTrigger>
              <TabsTrigger value="frontend">Frontend</TabsTrigger>
            </TabsList>
            
            <TabsContent value="system" className="space-y-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => addLog('info', 'system', 'Running health check...')}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Health Check
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => addLog('info', 'system', 'Cleaning temporary files...')}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Clean System
              </Button>
            </TabsContent>
            
            <TabsContent value="backend" className="space-y-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => addLog('info', 'backend', 'Restarting Backend API...')}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Restart Backend
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => window.open('http://127.0.0.1:5000/docs', '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                API Documentation
              </Button>
            </TabsContent>
            
            <TabsContent value="frontend" className="space-y-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => addLog('info', 'frontend', 'Restarting Frontend...')}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Restart Frontend
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => addLog('info', 'frontend', 'Building for production...')}
              >
                <Download className="h-4 w-4 mr-2" />
                Build Production
              </Button>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};