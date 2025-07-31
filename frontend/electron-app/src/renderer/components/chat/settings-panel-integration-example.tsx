import React, { useState, useCallback } from 'react';
import { AdvancedSettingsPanel } from './settings-panel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, Bot, Code, Palette, Target, Activity } from 'lucide-react';

interface ModelParameters {
  temperature: number;
  max_tokens: number;
  top_p: number;
  top_k?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  repetition_penalty?: number;
  stop_sequences?: string[];
  seed?: number;
}

/**
 * Example component showing different ways to integrate the Advanced Settings Panel
 * This demonstrates various configurations and use cases
 */
export const SettingsPanelIntegrationExample: React.FC = () => {
  const [currentParameters, setCurrentParameters] = useState<ModelParameters>({
    temperature: 0.7,
    max_tokens: 2048,
    top_p: 0.9,
    top_k: 50,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
    repetition_penalty: 1.0,
    stop_sequences: [],
  });
  
  const [parameterHistory, setParameterHistory] = useState<Array<{
    parameters: ModelParameters;
    timestamp: Date;
    source: string;
  }>>([]);
  
  const [selectedModel, setSelectedModel] = useState('gpt-4');

  const handleParametersChange = useCallback((parameters: ModelParameters) => {
    setCurrentParameters(parameters);
    setParameterHistory(prev => [
      ...prev,
      {
        parameters: { ...parameters },
        timestamp: new Date(),
        source: 'manual'
      }
    ].slice(-20)); // Keep last 20 changes
  }, []);

  const getParameterSummary = (params: ModelParameters) => {
    if (params.temperature > 0.8) return { type: 'creative', color: 'bg-purple-100 text-purple-800' };
    if (params.temperature < 0.4) return { type: 'precise', color: 'bg-blue-100 text-blue-800' };
    if (params.max_tokens > 3000) return { type: 'long-form', color: 'bg-green-100 text-green-800' };
    return { type: 'balanced', color: 'bg-gray-100 text-gray-800' };
  };

  const simulateAPICall = useCallback(async () => {
    // Simulate API call with current parameters
    console.log('Simulating API call with parameters:', currentParameters);
    
    // Add to history as API usage
    setParameterHistory(prev => [
      ...prev,
      {
        parameters: { ...currentParameters },
        timestamp: new Date(),
        source: 'api-call'
      }
    ].slice(-20));
  }, [currentParameters]);

  return (
    <div className="p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Advanced Settings Panel - Integration Examples</h1>
        <p className="text-muted-foreground">
          Different configurations and use cases for the advanced settings panel
        </p>
      </div>

      <Tabs defaultValue="full" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="full">Full Featured</TabsTrigger>
          <TabsTrigger value="minimal">Minimal</TabsTrigger>
          <TabsTrigger value="preview">With Preview</TabsTrigger>
          <TabsTrigger value="profiles">Profile Focus</TabsTrigger>
        </TabsList>

        {/* Full Featured Mode */}
        <TabsContent value="full" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Full Featured Settings Panel
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <AdvancedSettingsPanel
                    onParametersChange={handleParametersChange}
                    initialParameters={currentParameters}
                    modelId={selectedModel}
                    showPreview={true}
                    enableProfiles={true}
                    enableAdvancedParams={true}
                  />
                </CardContent>
              </Card>
            </div>
            
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Current Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Model:</span>
                    <Badge variant="outline">{selectedModel}</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Profile:</span>
                    <Badge className={getParameterSummary(currentParameters).color}>
                      {getParameterSummary(currentParameters).type}
                    </Badge>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Temperature:</span>
                      <span className="font-mono">{currentParameters.temperature.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Max Tokens:</span>
                      <span className="font-mono">{currentParameters.max_tokens}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Top P:</span>
                      <span className="font-mono">{currentParameters.top_p.toFixed(2)}</span>
                    </div>
                  </div>
                  
                  <Button onClick={simulateAPICall} className="w-full">
                    <Bot className="h-4 w-4 mr-2" />
                    Test with Current Settings
                  </Button>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Parameter History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {parameterHistory.slice().reverse().map((entry, index) => (
                      <div key={index} className="flex items-center justify-between text-sm p-2 bg-muted/50 rounded">
                        <div>
                          <div className="font-medium">
                            T: {entry.parameters.temperature.toFixed(2)} | 
                            MT: {entry.parameters.max_tokens} | 
                            P: {entry.parameters.top_p.toFixed(2)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {entry.timestamp.toLocaleTimeString('he-IL')}
                          </div>
                        </div>
                        <Badge variant={entry.source === 'api-call' ? 'default' : 'secondary'}>
                          {entry.source}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Minimal Mode */}
        <TabsContent value="minimal" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Minimal Settings Panel</CardTitle>
            </CardHeader>
            <CardContent>
              <AdvancedSettingsPanel
                onParametersChange={handleParametersChange}
                showPreview={false}
                enableProfiles={false}
                enableAdvancedParams={false}
                className="max-w-2xl"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preview Mode */}
        <TabsContent value="preview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Settings with Real-time Preview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <AdvancedSettingsPanel
                onParametersChange={handleParametersChange}
                modelId={selectedModel}
                showPreview={true}
                enableProfiles={true}
                enableAdvancedParams={true}
                className="max-w-4xl"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Profile Focus */}
        <TabsContent value="profiles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Profile-Focused Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <AdvancedSettingsPanel
                onParametersChange={handleParametersChange}
                showPreview={false}
                enableProfiles={true}
                enableAdvancedParams={true}
                className="max-w-3xl"
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Usage Examples */}
      <Card>
        <CardHeader>
          <CardTitle>Code Examples</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-medium">Basic Usage:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<AdvancedSettingsPanel
  onParametersChange={(params) => console.log('Parameters:', params)}
  initialParameters={{
    temperature: 0.7,
    max_tokens: 2048,
    top_p: 0.9
  }}
/>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">With Preview:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<AdvancedSettingsPanel
  onParametersChange={handleParametersChange}
  modelId="gpt-4"
  showPreview={true}
  enableProfiles={true}
/>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Minimal Configuration:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<AdvancedSettingsPanel
  onParametersChange={handleParametersChange}
  showPreview={false}
  enableProfiles={false}
  enableAdvancedParams={false}
/>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Custom Model Integration:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`const [parameters, setParameters] = useState(defaultParams);

const handleAPICall = async () => {
  const response = await fetch('/api/llm/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: selectedModel,
      parameters: parameters,
      prompt: userInput
    })
  });
  
  return response.json();
};

<AdvancedSettingsPanel
  onParametersChange={setParameters}
  modelId={selectedModel}
  initialParameters={parameters}
/>`}
            </pre>
          </div>
        </CardContent>
      </Card>

      {/* Model Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Model Selection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            {['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro'].map((model) => (
              <Button
                key={model}
                variant={selectedModel === model ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedModel(model)}
              >
                {model}
              </Button>
            ))}
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            Select a model to see how the settings panel adapts to different model capabilities.
          </p>
        </CardContent>
      </Card>

      {/* Preset Examples */}
      <Card>
        <CardHeader>
          <CardTitle>Common Use Cases</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Palette className="h-4 w-4 text-purple-500" />
                <h4 className="font-medium">Creative Writing</h4>
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>Temperature: 0.9</div>
                <div>Top P: 0.95</div>
                <div>Max Tokens: 2048</div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Code className="h-4 w-4 text-blue-500" />
                <h4 className="font-medium">Code Generation</h4>
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>Temperature: 0.2</div>
                <div>Top P: 0.85</div>
                <div>Max Tokens: 4096</div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-4 w-4 text-green-500" />
                <h4 className="font-medium">Precise Analysis</h4>
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>Temperature: 0.3</div>
                <div>Top P: 0.8</div>
                <div>Max Tokens: 1024</div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Bot className="h-4 w-4 text-orange-500" />
                <h4 className="font-medium">Balanced Chat</h4>
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>Temperature: 0.7</div>
                <div>Top P: 0.9</div>
                <div>Max Tokens: 2048</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};