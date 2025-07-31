import React, { useState, useCallback } from 'react';
import { EnhancedModelSelector } from './enhanced-model-selector';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Bot, Settings, BarChart3, Zap } from 'lucide-react';

/**
 * Example component showing different ways to integrate the Enhanced Model Selector
 * This demonstrates various configurations and use cases
 */
export const ModelSelectorIntegrationExample: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [modelChangeHistory, setModelChangeHistory] = useState<Array<{ modelId: string; timestamp: Date }>>([]);

  const handleModelChange = useCallback((modelId: string) => {
    setSelectedModel(modelId);
    setModelChangeHistory(prev => [
      ...prev,
      { modelId, timestamp: new Date() }
    ].slice(-10)); // Keep last 10 changes
    
    console.log('Model changed to:', modelId);
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Enhanced Model Selector - Integration Examples</h1>
        <p className="text-muted-foreground">
          Different configurations and use cases for the enhanced model selector
        </p>
      </div>

      <Tabs defaultValue="full" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="full">Full Featured</TabsTrigger>
          <TabsTrigger value="compact">Compact Mode</TabsTrigger>
          <TabsTrigger value="performance">Performance Focus</TabsTrigger>
          <TabsTrigger value="simple">Simple Mode</TabsTrigger>
        </TabsList>

        {/* Full Featured Mode */}
        <TabsContent value="full" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Full Featured Model Selector
              </CardTitle>
            </CardHeader>
            <CardContent>
              <EnhancedModelSelector
                onModelChange={handleModelChange}
                showMetrics={true}
                showRecommendations={true}
                enableQuickSwitch={true}
                showPerformanceDetails={true}
                showTrending={true}
                enableSmartRecommendations={true}
                autoRefresh={true}
                refreshInterval={30000}
                className="max-w-4xl"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compact Mode */}
        <TabsContent value="compact" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Compact with Quick Switch</CardTitle>
              </CardHeader>
              <CardContent>
                <EnhancedModelSelector
                  compact
                  onModelChange={handleModelChange}
                  enableQuickSwitch={true}
                  showRecommendations={true}
                />
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Minimal Compact</CardTitle>
              </CardHeader>
              <CardContent>
                <EnhancedModelSelector
                  compact
                  onModelChange={handleModelChange}
                  showMetrics={false}
                  showRecommendations={false}
                  enableQuickSwitch={false}
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Focus */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Performance-Focused Configuration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <EnhancedModelSelector
                onModelChange={handleModelChange}
                showMetrics={true}
                showRecommendations={true}
                showPerformanceDetails={true}
                showTrending={true}
                enableSmartRecommendations={false}
                autoRefresh={true}
                refreshInterval={10000} // More frequent updates
                className="max-w-4xl"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Simple Mode */}
        <TabsContent value="simple" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Simple Configuration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <EnhancedModelSelector
                onModelChange={handleModelChange}
                showMetrics={true}
                showRecommendations={false}
                enableQuickSwitch={false}
                showPerformanceDetails={false}
                showTrending={false}
                enableSmartRecommendations={false}
                autoRefresh={false}
                className="max-w-2xl"
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Status Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Integration Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Current Model:</span>
              {selectedModel ? (
                <Badge variant="default">{selectedModel}</Badge>
              ) : (
                <Badge variant="secondary">None Selected</Badge>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Changes:</span>
              <Badge variant="outline">{modelChangeHistory.length}</Badge>
            </div>
          </div>

          {modelChangeHistory.length > 0 && (
            <div>
              <h4 className="text-sm font-medium mb-2">Recent Model Changes:</h4>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {modelChangeHistory.slice().reverse().map((change, index) => (
                  <div key={index} className="flex items-center justify-between text-sm p-2 bg-muted/50 rounded">
                    <span>{change.modelId}</span>
                    <span className="text-muted-foreground">
                      {change.timestamp.toLocaleTimeString('he-IL')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Usage Examples */}
      <Card>
        <CardHeader>
          <CardTitle>Code Examples</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-medium">Basic Usage:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<EnhancedModelSelector
  onModelChange={(modelId) => console.log('Selected:', modelId)}
  showMetrics={true}
  showRecommendations={true}
/>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Compact Mode:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<EnhancedModelSelector
  compact
  enableQuickSwitch={true}
  onModelChange={handleModelChange}
/>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Performance Focused:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<EnhancedModelSelector
  showPerformanceDetails={true}
  showTrending={true}
  autoRefresh={true}
  refreshInterval={10000}
  onModelChange={handleModelChange}
/>`}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};