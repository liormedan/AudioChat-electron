import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Terminal as TerminalIcon,
  Server,
  Activity,
  Settings
} from 'lucide-react';
import { ServiceStatusCard } from '../components/terminal/service-status-card';
import { TerminalOutput } from '../components/terminal/terminal-output';
import { TerminalControls } from '../components/terminal/terminal-controls';
import { TerminalLog, ServiceStatus } from '../shared/types/ipc';

export const IntegratedTerminalPage: React.FC = () => {
  const [logs, setLogs] = useState<TerminalLog[]>([]);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isIntegratedMode, setIsIntegratedMode] = useState(false);

  useEffect(() => {
    // Check if running in integrated mode
    const checkIntegratedMode = async () => {
      try {
        const integrated = await window.electronAPI.isIntegratedMode();
        setIsIntegratedMode(integrated);
        
        if (integrated) {
          // Start services automatically in integrated mode
          await handleStartAllServices();
        }
      } catch (error) {
        console.error('Failed to check integrated mode:', error);
      }
    };

    checkIntegratedMode();

    // Set up event listeners for real-time updates
    const unsubscribeLog = window.electronAPI.onTerminalLog((log: TerminalLog) => {
      setLogs(prev => [...prev, log]);
    });

    const unsubscribeStatus = window.electronAPI.onServiceStatus((serviceName: string, status: ServiceStatus) => {
      setServices(prev => {
        const updated = prev.filter(s => s.name !== serviceName);
        return [...updated, status];
      });
    });

    // Load initial service status
    loadServiceStatus();

    return () => {
      unsubscribeLog();
      unsubscribeStatus();
    };
  }, []);

  const loadServiceStatus = async () => {
    try {
      const status = await window.electronAPI.getServiceStatus();
      if (Array.isArray(status)) {
        setServices(status);
      }
    } catch (error) {
      console.error('Failed to load service status:', error);
    }
  };

  const handleStartAllServices = async () => {
    setIsLoading(true);
    try {
      await window.electronAPI.startServices();
    } catch (error) {
      console.error('Failed to start services:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopAllServices = async () => {
    setIsLoading(true);
    try {
      await window.electronAPI.stopServices();
    } catch (error) {
      console.error('Failed to stop services:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestartAllServices = async () => {
    setIsLoading(true);
    try {
      await window.electronAPI.stopServices();
      // Wait a bit before restarting
      setTimeout(async () => {
        await window.electronAPI.startServices();
        setIsLoading(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to restart services:', error);
      setIsLoading(false);
    }
  };

  const handleRestartService = async (serviceName: string) => {
    try {
      await window.electronAPI.restartService(serviceName);
    } catch (error) {
      console.error(`Failed to restart ${serviceName}:`, error);
    }
  };

  const handleCheckHealth = async () => {
    try {
      const health = await window.electronAPI.checkServicesHealth();
      console.log('Health check results:', health);
      
      // Add health check results to logs
      Object.entries(health).forEach(([service, isHealthy]) => {
        const log: TerminalLog = {
          service: 'system',
          type: isHealthy ? 'success' : 'error',
          message: `Health check: ${service} is ${isHealthy ? 'healthy' : 'unhealthy'}`,
          timestamp: new Date()
        };
        setLogs(prev => [...prev, log]);
      });
    } catch (error) {
      console.error('Failed to check health:', error);
    }
  };

  const handleClearLogs = () => {
    setLogs([]);
  };

  const runningServices = services.filter(s => s.status === 'running').length;

  if (!isIntegratedMode) {
    return (
      <div className="p-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TerminalIcon className="h-5 w-5" />
              <span>Terminal</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                Integrated terminal is only available when running in integrated mode.
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Use <code>scripts/start-integrated.bat</code> to enable this feature.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center space-x-2">
          <TerminalIcon className="h-8 w-8" />
          <span>Integrated Terminal</span>
        </h1>
        <p className="text-muted-foreground">
          Monitor and control all Audio Chat Studio services from one place
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview" className="flex items-center space-x-2">
            <Activity className="h-4 w-4" />
            <span>Overview</span>
          </TabsTrigger>
          <TabsTrigger value="services" className="flex items-center space-x-2">
            <Server className="h-4 w-4" />
            <span>Services</span>
          </TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center space-x-2">
            <TerminalIcon className="h-4 w-4" />
            <span>Logs</span>
          </TabsTrigger>
          <TabsTrigger value="controls" className="flex items-center space-x-2">
            <Settings className="h-4 w-4" />
            <span>Controls</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* System Status */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">System Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Services Running</span>
                  <Badge variant={runningServices === services.length ? 'default' : 'secondary'}>
                    {runningServices}/{services.length}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Total Logs</span>
                  <Badge variant="outline">{logs.length}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Mode</span>
                  <Badge variant="default">Integrated</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Recent Logs */}
            <Card className="lg:col-span-2">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {logs.slice(-5).map((log, index) => (
                    <div key={index} className="flex items-center space-x-2 text-sm">
                      <Badge variant="outline" className="text-xs">
                        {log.service}
                      </Badge>
                      <span className="text-muted-foreground text-xs">
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                      <span className="flex-1 truncate">{log.message}</span>
                    </div>
                  ))}
                  {logs.length === 0 && (
                    <p className="text-muted-foreground text-sm">No recent activity</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.map((service) => (
              <ServiceStatusCard
                key={service.name}
                service={service}
                onStart={() => handleRestartService(service.name)}
                onStop={() => handleRestartService(service.name)}
                onRestart={() => handleRestartService(service.name)}
                onOpenBrowser={service.port ? () => {
                  const url = service.name === 'backend' 
                    ? `http://127.0.0.1:${service.port}/docs`
                    : `http://127.0.0.1:${service.port}`;
                  window.open(url, '_blank');
                } : undefined}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <TerminalOutput
            logs={logs}
            onClear={handleClearLogs}
          />
        </TabsContent>

        <TabsContent value="controls" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <TerminalControls
              onStartAll={handleStartAllServices}
              onStopAll={handleStopAllServices}
              onRestartAll={handleRestartAllServices}
              onCheckHealth={handleCheckHealth}
              isLoading={isLoading}
              servicesRunning={runningServices}
              totalServices={services.length}
            />
            
            {/* Additional System Info */}
            <Card>
              <CardHeader>
                <CardTitle>System Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Platform:</span>
                    <span className="ml-2">{typeof process !== 'undefined' ? process.platform : 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Node.js:</span>
                    <span className="ml-2">{typeof process !== 'undefined' ? process.versions?.node || 'Unknown' : 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Electron:</span>
                    <span className="ml-2">{typeof process !== 'undefined' ? process.versions?.electron || 'Unknown' : 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Chrome:</span>
                    <span className="ml-2">{typeof process !== 'undefined' ? process.versions?.chrome || 'Unknown' : 'Unknown'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};