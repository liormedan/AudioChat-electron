import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input'; // Assuming you have an Input component
import { Bot, MessageSquare, Settings, Zap, CheckCircle, XCircle, Loader } from 'lucide-react';

interface LLMProvider {
  name: string;
  api_base_url: string;
  supported_models: string[];
  is_connected: boolean;
  connection_status: string;
  last_test_date: string | null;
  error_message: string | null;
  rate_limit: number;
  cost_per_1k_tokens: number;
  metadata: Record<string, any>;
}

interface LLMModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  max_tokens: number;
  cost_per_token: number;
  capabilities: string[];
  is_active: boolean;
  is_available: boolean;
  context_window: number;
  training_data_cutoff: string | null;
  version: string | null;
  parameters: Record<string, any>;
  metadata: Record<string, any>;
}

export const LLMPage: React.FC = () => {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [activeModel, setActiveModel] = useState<LLMModel | null>(null);
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null);
  const [providerModels, setProviderModels] = useState<Record<string, LLMModel[]>>({});
  const [testingProvider, setTestingProvider] = useState<string | null>(null);

  useEffect(() => {
    fetchProviders();
    fetchActiveModel();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/llm/providers');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: LLMProvider[] = await response.json();
      setProviders(data);
      // Initialize API keys state (assuming we might fetch them later or they are empty initially)
      const initialApiKeys: Record<string, string> = {};
      data.forEach(p => (initialApiKeys[p.name] = '')); // Or fetch existing keys if an endpoint exists
      setApiKeys(initialApiKeys);
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  const fetchActiveModel = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/llm/active-model');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: LLMModel | null = await response.json();
      setActiveModel(data);
    } catch (error) {
      console.error('Error fetching active model:', error);
    }
  };

  const handleApiKeyChange = (providerName: string, value: string) => {
    setApiKeys(prev => ({ ...prev, [providerName]: value }));
  };

  const handleSaveApiKey = async (providerName: string) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/llm/set-api-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider_name: providerName, api_key: apiKeys[providerName] }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json();
      if (result.success) {
        console.log(`API key for ${providerName} saved successfully.`);
        fetchProviders(); // Refresh providers to update connection status
      } else {
        console.error(`Failed to save API key for ${providerName}:`, result.error);
      }
    } catch (error) {
      console.error(`Error saving API key for ${providerName}:`, error);
    }
  };

  const handleTestConnection = async (providerName: string) => {
    setTestingProvider(providerName);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/llm/test-connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider_name: providerName }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json();
      if (result.success) {
        console.log(`Connection to ${providerName} successful.`);
      } else {
        console.error(`Connection to ${providerName} failed:`, result.error);
      }
      fetchProviders(); // Refresh providers to update connection status
    } catch (error) {
      console.error(`Error testing connection for ${providerName}:`, error);
    } finally {
      setTestingProvider(null);
    }
  };

  const handleSetActiveModel = async (modelId: string) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/llm/active-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json();
      if (result.success) {
        console.log(`Active model set to: ${modelId}`);
        fetchActiveModel(); // Refresh active model state
      } else {
        console.error(`Failed to set active model:`, result.error);
      }
    } catch (error) {
      console.error(`Error setting active model:`, error);
    }
  };

  const toggleProviderModels = async (providerName: string) => {
    if (expandedProvider === providerName) {
      setExpandedProvider(null);
    } else {
      setExpandedProvider(providerName);
      if (!providerModels[providerName]) {
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/llm/models?provider=${providerName}`);
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          const data: LLMModel[] = await response.json();
          setProviderModels(prev => ({ ...prev, [providerName]: data }));
        } catch (error) {
          console.error(`Error fetching models for ${providerName}:`, error);
        }
      }
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">AI Assistant Manager</h1>
        <p className="text-muted-foreground">
          Manage AI models and chat with your audio processing assistant
        </p>
      </div>

      {/* AI Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Status</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              Offline
            </div>
            <p className="text-xs text-muted-foreground">
              AI services not connected
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Chats</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              Open conversations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Usage</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              Requests today
            </p>
          </CardContent>
        </Card>
      </div>

      {/* AI Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>AI Configuration</span>
          </CardTitle>
          <CardDescription>
            Configure AI models and API settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {providers.map(provider => (
              <Card key={provider.name} className="p-4">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-lg font-medium">{provider.name}</CardTitle>
                  <span
                    className={`h-3 w-3 rounded-full ${
                      provider.connection_status === 'connected' ? 'bg-green-500' :
                      provider.connection_status === 'testing' ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    title={provider.connection_status}
                  ></span>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Input
                      type="password"
                      placeholder="Enter API Key"
                      value={apiKeys[provider.name] || ''}
                      onChange={(e) => handleApiKeyChange(provider.name, e.target.value)}
                      className="flex-1"
                    />
                    <Button onClick={() => handleSaveApiKey(provider.name)}>Save</Button>
                  </div>
                  <Button
                    onClick={() => handleTestConnection(provider.name)}
                    disabled={testingProvider === provider.name}
                    className="w-full"
                  >
                    {testingProvider === provider.name ? (
                      <Loader className="animate-spin mr-2" size={16} />
                    ) : provider.is_connected ? (
                      <CheckCircle className="mr-2" size={16} />
                    ) : (
                      <XCircle className="mr-2" size={16} />
                    )}
                    {testingProvider === provider.name ? 'Testing...' : 'Test Connection'}
                  </Button>
                  {provider.error_message && (
                    <p className="text-red-500 text-sm">Error: {provider.error_message}</p>
                  )}
                  <Button variant="outline" onClick={() => toggleProviderModels(provider.name)} className="w-full mt-2">
                    {expandedProvider === provider.name ? 'Hide Models' : 'Show Models'}
                  </Button>
                  {expandedProvider === provider.name && (
                    <div className="mt-4 space-y-2">
                      {providerModels[provider.name] ? (
                        providerModels[provider.name].map(model => (
                          <div key={model.id} className={`flex items-center justify-between p-2 border rounded-md ${
                            activeModel?.id === model.id ? 'bg-blue-500 text-white' : 'bg-gray-700'
                          }`}>
                            <span>{model.name}</span>
                            <Button
                              size="sm"
                              onClick={() => handleSetActiveModel(model.id)}
                              disabled={activeModel?.id === model.id}
                            >
                              {activeModel?.id === model.id ? 'Active' : 'Set Active'}
                            </Button>
                          </div>
                        ))
                      ) : (
                        <p>Loading models...</p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};