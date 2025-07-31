import React, { useState, useCallback } from 'react';
import { APIKeyManagement, APIKey, ProviderStatus } from './api-key-management';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, Key, Activity, BarChart3, Shield, AlertTriangle } from 'lucide-react';

/**
 * Example component showing different ways to integrate the API Key Management component
 * This demonstrates various configurations and use cases
 */
export const APIKeyManagementIntegrationExample: React.FC = () => {
  const [integrationMode, setIntegrationMode] = useState<'standalone' | 'embedded' | 'minimal'>('standalone');
  const [securityLevel, setSecurityLevel] = useState<'standard' | 'high' | 'enterprise'>('standard');

  const handleSecurityChange = useCallback((level: 'standard' | 'high' | 'enterprise') => {
    setSecurityLevel(level);
    console.log('Security level changed to:', level);
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">API Key Management - Integration Examples</h1>
        <p className="text-muted-foreground">
          Different configurations and use cases for the API key management system
        </p>
      </div>

      <Tabs defaultValue="standalone" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="standalone">Standalone</TabsTrigger>
          <TabsTrigger value="embedded">Embedded</TabsTrigger>
          <TabsTrigger value="settings">Settings Page</TabsTrigger>
        </TabsList>

        {/* Standalone Mode */}
        <TabsContent value="standalone" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                Standalone API Key Management
              </CardTitle>
            </CardHeader>
            <CardContent>
              <APIKeyManagement className="max-w-6xl" />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Embedded Mode */}
        <TabsContent value="embedded" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>API Configuration</CardTitle>
                </CardHeader>
                <CardContent>
                  <APIKeyManagement />
                </CardContent>
              </Card>
            </div>
            
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Security Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Security Level:</span>
                    <Badge variant={
                      securityLevel === 'enterprise' ? 'default' :
                      securityLevel === 'high' ? 'secondary' : 'outline'
                    }>
                      {securityLevel}
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    {['standard', 'high', 'enterprise'].map((level) => (
                      <Button
                        key={level}
                        variant={securityLevel === level ? 'default' : 'outline'}
                        size="sm"
                        className="w-full"
                        onClick={() => handleSecurityChange(level as any)}
                      >
                        {level === 'standard' && <Shield className="h-4 w-4 mr-2" />}
                        {level === 'high' && <AlertTriangle className="h-4 w-4 mr-2" />}
                        {level === 'enterprise' && <Settings className="h-4 w-4 mr-2" />}
                        {level.charAt(0).toUpperCase() + level.slice(1)}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Quick Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span>Active Keys:</span>
                    <Badge variant="default">3</Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Connected Providers:</span>
                    <Badge variant="secondary">2/4</Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Monthly Usage:</span>
                    <Badge variant="outline">$45.20</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Settings Page Integration */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Settings Page Integration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="api-keys" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="general">General</TabsTrigger>
                  <TabsTrigger value="api-keys">
                    <Key className="h-4 w-4 mr-2" />
                    API Keys
                  </TabsTrigger>
                  <TabsTrigger value="security">Security</TabsTrigger>
                  <TabsTrigger value="billing">Billing</TabsTrigger>
                </TabsList>

                <TabsContent value="general" className="space-y-4">
                  <div className="text-center py-8 text-muted-foreground">
                    <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>General settings would go here</p>
                  </div>
                </TabsContent>

                <TabsContent value="api-keys" className="space-y-4">
                  <APIKeyManagement />
                </TabsContent>

                <TabsContent value="security" className="space-y-4">
                  <div className="text-center py-8 text-muted-foreground">
                    <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Security settings would go here</p>
                  </div>
                </TabsContent>

                <TabsContent value="billing" className="space-y-4">
                  <div className="text-center py-8 text-muted-foreground">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Billing settings would go here</p>
                  </div>
                </TabsContent>
              </Tabs>
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
{`import { APIKeyManagement } from '@/components/settings/api-key-management';

function SettingsPage() {
  return (
    <div className="container mx-auto p-6">
      <h1>API Configuration</h1>
      <APIKeyManagement />
    </div>
  );
}`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Embedded in Settings:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<Tabs defaultValue="api-keys">
  <TabsList>
    <TabsTrigger value="general">General</TabsTrigger>
    <TabsTrigger value="api-keys">API Keys</TabsTrigger>
    <TabsTrigger value="security">Security</TabsTrigger>
  </TabsList>
  
  <TabsContent value="api-keys">
    <APIKeyManagement />
  </TabsContent>
</Tabs>`}
            </pre>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">With Custom Styling:</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`<APIKeyManagement 
  className="max-w-4xl mx-auto"
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
                <Key className="h-4 w-4 text-blue-500" />
                <h4 className="font-medium">Secure Key Management</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Masked input fields with show/hide functionality for secure API key handling
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-green-500" />
                <h4 className="font-medium">Connection Testing</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Real-time connection testing with visual feedback and status indicators
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="h-4 w-4 text-purple-500" />
                <h4 className="font-medium">Usage Statistics</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Detailed usage tracking and cost monitoring per provider
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="h-4 w-4 text-orange-500" />
                <h4 className="font-medium">Provider Dashboard</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Comprehensive status dashboard for all AI providers
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Settings className="h-4 w-4 text-gray-500" />
                <h4 className="font-medium">Multi-Provider Support</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Support for OpenAI, Anthropic, Google AI, Cohere, and more
              </p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-4 w-4 text-red-500" />
                <h4 className="font-medium">Error Handling</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Robust error handling with clear user feedback and recovery options
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};