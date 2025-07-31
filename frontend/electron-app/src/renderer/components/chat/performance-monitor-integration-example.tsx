import React, { useState, useCallback } from 'react';
import { PerformanceMonitor } from './performance-monitor';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { 
  Activity, 
  BarChart3, 
  Settings, 
  Bell, 
  Eye, 
  Gauge,
  TrendingUp,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

/**
 * Example component showing different ways to integrate the Performance Monitor
 * This demonstrates various configurations and use cases
 */
export const PerformanceMonitorIntegrationExample: React.FC = () => {
  const [selectedModels, setSelectedModels] = useState<string[]>(['gpt-4', 'gpt-3.5-turbo']);
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [compactMode, setCompactMode] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState<string[]>([]);

  const handleModelSelect = useCallback((modelId: string) => {
    setSelectedModel(modelId);
    console.log('Selected model:', modelId);
  }, []);

  const handleAlertAcknowledge = useCallback((alertId: string) => {
    setAcknowledgedAlerts(prev => [...prev, alertId]);
    console.log('Acknowledged alert:', alertId);
  }, []);

  const toggleModelSelection = useCallback((modelId: string) => {
    setSelectedModels(prev => 
      prev.includes(modelId) 
        ? prev.filter(id => id !== modelId)
        : [...prev, modelId]
    );
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Performance Monitor - Integration Examples</h1>
        <p className="text-muted-foreground">
          Different configurations and use cases for the performance monitoring system
        </p>
      </div>

      <Tabs defaultValue="full" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="full">Full Monitor</TabsTrigger>
          <TabsTrigger value="compact">Compact View</TabsTrigger>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="alerts">Alerts Focus</TabsTrigger>
        </TabsList>

        {/* Full Monitor */}
        <TabsContent value="full" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Full Performance Monitor
              </CardTitle>
            </CardHeader>
            <CardContent>
              <PerformanceMonitor
                onModelSelect={handleModelSelect}
                onAlertAcknowledge={handleAlertAcknowledge}
                selectedModels={selectedModels}
                showAlerts={alertsEnabled}
                enableComparison={true}
                autoRefresh={autoRefresh}
                refreshInterval={30000}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compact View */}
        <TabsContent value="compact" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Main Application</CardTitle>
                </CardHeader>
                <CardContent className="text-center py-12 text-muted-foreground">
                  <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Your main application content would go here</p>
                </CardContent>
              </Card>
            </div>
            
            <div>
              <PerformanceMonitor
                compactMode
                onModelSelect={handleModelSelect}
                showAlerts={false}
                enableComparison={false}
                autoRefresh={autoRefresh}
              />
            </div>
          </div>
        </TabsContent>

        {/* Dashboard Integration */}
        <TabsContent value="dashboard" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-3">
              <PerformanceMonitor
                onModelSelect={handleModelSelect}
                onAlertAcknowledge={handleAlertAcknowledge}
                selectedModels={selectedModels}
                showAlerts={alertsEnabled}
                enableComparison={true}
                autoRefresh={autoRefresh}
              />
            </div>
            
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Monitor Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="auto-refresh">Auto Refresh</Label>
                    <Switch
                      id="auto-refresh"
                      checked={autoRefresh}
                      onCheckedChange={setAutoRefresh}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <Label htmlFor="alerts-enabled">Show Alerts</Label>
                    <Switch
                      id="alerts-enabled"
                      checked={alertsEnabled}
                      onCheckedChange={setAlertsEnabled}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <Label htmlFor="compact-mode">Compact Mode</Label>
                    <Switch
                      id="compact-mode"
                      checked={compactMode}
                      onCheckedChange={setCompactMode}
                    />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Model Selection</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro'].map(modelId => (
                    <div key={modelId} className="flex items-center justify-between">
                      <span className="text-sm">{modelId}</span>
                      <Switch
                        checked={selectedModels.includes(modelId)}
                        onCheckedChange={() => toggleModelSelection(modelId)}
                      />
                    </div>
                  ))}
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Status</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span>Selected Model:</span>
                    <Badge variant={selectedModel ? 'default' : 'outline'}>
                      {selectedModel || 'None'}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span>Monitoring:</span>
                    <Badge variant={selectedModels.length > 0 ? 'default' : 'outline'}>
                      {selectedModels.length} models
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span>Alerts:</span>
                    <Badge variant={acknowledgedAlerts.length > 0 ? 'secondary' : 'outline'}>
                      {acknowledgedAlerts.length} acknowledged
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Alerts Focus */}
        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Alerts-Focused Monitor
              </CardTitle>
            </CardHeader>
            <CardContent>
              <PerformanceMonitor
                onModelSelect={handleModelSelect}
                onAlertAcknowledge={handleAlertAcknowledge}
                selectedModels={selectedModels}
                showAlerts={true}
                enableComparison={false}
                autoRefresh={true}
                refreshInterval={10000} // More frequent for alerts
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Code Examples */}
      <Card>
        <CardHeader>
          <CardTitle>Code Examples</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-medium">Basic Usage:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<PerformanceMonitor
  onModelSelect={(modelId) => console.log('Selected:', modelId)}
  onAlertAcknowledge={(alertId) => console.log('Acknowledged:', alertId)}
  showAlerts={true}
  enableComparison={true}
/>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Compact Mode:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<PerformanceMonitor
  compactMode
  onModelSelect={handleModelSelect}
  showAlerts={false}
  enableComparison={false}
  autoRefresh={true}
/>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Dashboard Integration:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<div className="grid grid-cols-4 gap-6">
  <div className="col-span-3">
    <PerformanceMonitor
      selectedModels={['gpt-4', 'claude-3']}
      showAlerts={true}
      enableComparison={true}
      autoRefresh={true}
      refreshInterval={30000}
    />
  </div>
  <div>
    {/* Sidebar controls */}
  </div>
</div>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Alerts-Only Mode:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<PerformanceMonitor
  showAlerts={true}
  enableComparison={false}
  autoRefresh={true}
  refreshInterval={10000} // More frequent for alerts
  onAlertAcknowledge={(alertId) => {
    // Handle alert acknowledgment
    updateAlertStatus(alertId);
  }}
/>`}
            </pre>
          </div>
        </CardContent>
      </Card>

      {/* Features Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Key Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-blue-500" />
                <h4 className="font-medium">Real-time Metrics</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Live performance monitoring with automatic refresh and real-time updates
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="h-4 w-4 text-green-500" />
                <h4 className="font-medium">Performance Comparison</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Side-by-side comparison of multiple models with recommendations
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Bell className="h-4 w-4 text-orange-500" />
                <h4 className="font-medium">Smart Alerts</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Configurable alerts for performance thresholds and anomalies
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Gauge className="h-4 w-4 text-purple-500" />
                <h4 className="font-medium">Cost Tracking</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Detailed cost analysis with trends and usage optimization
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-red-500" />
                <h4 className="font-medium">Trend Analysis</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Historical performance trends and predictive insights
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Eye className="h-4 w-4 text-gray-500" />
                <h4 className="font-medium">Flexible Views</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Multiple view modes including compact, detailed, and comparison views
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};