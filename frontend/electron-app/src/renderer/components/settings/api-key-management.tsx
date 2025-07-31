import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Key,
  Eye,
  EyeOff,
  TestTube,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader,
  Plus,
  Trash2,
  Edit3,
  Copy,
  Check,
  Activity,
  BarChart3,
  DollarSign,
  Clock,
  Zap,
  Shield,
  RefreshCw,
  Settings,
  Info,
  ExternalLink,
  AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';

// Provider interfaces
export interface APIProvider {
  id: string;
  name: string;
  displayName: string;
  description: string;
  website: string;
  icon: React.ReactNode;
  supportedModels: string[];
  requiresApiKey: boolean;
  keyFormat: string;
  keyExample: string;
  testEndpoint: string;
  documentationUrl: string;
  pricingUrl: string;
}

export interface APIKey {
  id: string;
  providerId: string;
  name: string;
  key: string;
  isActive: boolean;
  createdAt: string;
  lastUsed?: string;
  lastTested?: string;
  status: 'active' | 'inactive' | 'invalid' | 'expired' | 'testing';
  usage?: {
    totalRequests: number;
    totalTokens: number;
    totalCost: number;
    lastMonth: {
      requests: number;
      tokens: number;
      cost: number;
    };
  };
  limits?: {
    dailyRequests?: number;
    monthlyTokens?: number;
    monthlyCost?: number;
  };
}

export interface ProviderStatus {
  providerId: string;
  isConnected: boolean;
  lastChecked: string;
  responseTime: number;
  errorMessage?: string;
  availableModels: string[];
  rateLimits: {
    requestsPerMinute: number;
    tokensPerMinute: number;
    requestsPerDay: number;
  };
}

export interface UsageStatistics {
  providerId: string;
  period: 'day' | 'week' | 'month';
  data: {
    date: string;
    requests: number;
    tokens: number;
    cost: number;
    errors: number;
  }[];
  totals: {
    requests: number;
    tokens: number;
    cost: number;
    errors: number;
  };
}

interface APIKeyManagementProps {
  className?: string;
}

// Supported providers
const SUPPORTED_PROVIDERS: APIProvider[] = [
  {
    id: 'openai',
    name: 'openai',
    displayName: 'OpenAI',
    description: 'GPT-4, GPT-3.5, DALL-E, Whisper',
    website: 'https://openai.com',
    icon: <Zap className="h-4 w-4" />,
    supportedModels: ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo'],
    requiresApiKey: true,
    keyFormat: 'sk-...',
    keyExample: 'sk-1234567890abcdef...',
    testEndpoint: '/api/test/openai',
    documentationUrl: 'https://platform.openai.com/docs',
    pricingUrl: 'https://openai.com/pricing'
  },
  {
    id: 'anthropic',
    name: 'anthropic',
    displayName: 'Anthropic',
    description: 'Claude 3, Claude 2',
    website: 'https://anthropic.com',
    icon: <Shield className="h-4 w-4" />,
    supportedModels: ['claude-3-opus', 'claude-3-sonnet', 'claude-2'],
    requiresApiKey: true,
    keyFormat: 'sk-ant-...',
    keyExample: 'sk-ant-1234567890abcdef...',
    testEndpoint: '/api/test/anthropic',
    documentationUrl: 'https://docs.anthropic.com',
    pricingUrl: 'https://www.anthropic.com/pricing'
  },
  {
    id: 'google',
    name: 'google',
    displayName: 'Google AI',
    description: 'Gemini Pro, PaLM 2',
    website: 'https://ai.google.dev',
    icon: <Activity className="h-4 w-4" />,
    supportedModels: ['gemini-pro', 'gemini-pro-vision'],
    requiresApiKey: true,
    keyFormat: 'AIza...',
    keyExample: 'AIzaSyDaGmWKa4JsXZ-HjGw...',
    testEndpoint: '/api/test/google',
    documentationUrl: 'https://ai.google.dev/docs',
    pricingUrl: 'https://ai.google.dev/pricing'
  },
  {
    id: 'cohere',
    name: 'cohere',
    displayName: 'Cohere',
    description: 'Command, Generate, Embed',
    website: 'https://cohere.ai',
    icon: <BarChart3 className="h-4 w-4" />,
    supportedModels: ['command', 'command-light'],
    requiresApiKey: true,
    keyFormat: 'co-...',
    keyExample: 'co-1234567890abcdef...',
    testEndpoint: '/api/test/cohere',
    documentationUrl: 'https://docs.cohere.ai',
    pricingUrl: 'https://cohere.ai/pricing'
  }
];

export const APIKeyManagement: React.FC<APIKeyManagementProps> = ({
  className = ''
}) => {
  // State management
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [providerStatuses, setProviderStatuses] = useState<Record<string, ProviderStatus>>({});
  const [usageStats, setUsageStats] = useState<Record<string, UsageStatistics>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [testingKeys, setTestingKeys] = useState<Set<string>>(new Set());
  
  // Dialog states
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedKey, setSelectedKey] = useState<APIKey | null>(null);
  
  // Form states
  const [newKeyData, setNewKeyData] = useState({
    providerId: '',
    name: '',
    key: '',
    showKey: false
  });
  
  // Visibility states
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Load data on mount
  useEffect(() => {
    loadAPIKeys();
    loadProviderStatuses();
    loadUsageStatistics();
  }, []);

  // Auto-refresh provider statuses
  useEffect(() => {
    const interval = setInterval(() => {
      loadProviderStatuses();
    }, 60000); // Refresh every minute

    return () => clearInterval(interval);
  }, []);

  const loadAPIKeys = useCallback(async () => {
    try {
      const response = await fetch('/api/settings/api-keys');
      if (response.ok) {
        const keys = await response.json();
        setApiKeys(keys);
      }
    } catch (error) {
      console.error('Error loading API keys:', error);
    }
  }, []);

  const loadProviderStatuses = useCallback(async () => {
    try {
      const response = await fetch('/api/providers/status');
      if (response.ok) {
        const statuses = await response.json();
        setProviderStatuses(statuses);
      }
    } catch (error) {
      console.error('Error loading provider statuses:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadUsageStatistics = useCallback(async () => {
    try {
      const response = await fetch('/api/providers/usage-stats');
      if (response.ok) {
        const stats = await response.json();
        setUsageStats(stats);
      }
    } catch (error) {
      console.error('Error loading usage statistics:', error);
    }
  }, []);

  const saveAPIKey = useCallback(async () => {
    if (!newKeyData.providerId || !newKeyData.name || !newKeyData.key) return;

    try {
      const keyData: Omit<APIKey, 'id' | 'createdAt'> = {
        providerId: newKeyData.providerId,
        name: newKeyData.name,
        key: newKeyData.key,
        isActive: true,
        status: 'inactive'
      };

      const response = await fetch('/api/settings/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keyData)
      });

      if (response.ok) {
        await loadAPIKeys();
        setNewKeyData({ providerId: '', name: '', key: '', showKey: false });
        setShowAddDialog(false);
        
        // Test the new key
        const newKey = await response.json();
        testConnection(newKey.id);
      }
    } catch (error) {
      console.error('Error saving API key:', error);
    }
  }, [newKeyData, loadAPIKeys]);

  const updateAPIKey = useCallback(async (keyId: string, updates: Partial<APIKey>) => {
    try {
      const response = await fetch(`/api/settings/api-keys/${keyId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        await loadAPIKeys();
      }
    } catch (error) {
      console.error('Error updating API key:', error);
    }
  }, [loadAPIKeys]);

  const deleteAPIKey = useCallback(async (keyId: string) => {
    try {
      const response = await fetch(`/api/settings/api-keys/${keyId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await loadAPIKeys();
        setShowDeleteDialog(false);
        setSelectedKey(null);
      }
    } catch (error) {
      console.error('Error deleting API key:', error);
    }
  }, [loadAPIKeys]);

  const testConnection = useCallback(async (keyId: string) => {
    const key = apiKeys.find(k => k.id === keyId);
    if (!key) return;

    setTestingKeys(prev => new Set(prev).add(keyId));
    
    try {
      const provider = SUPPORTED_PROVIDERS.find(p => p.id === key.providerId);
      if (!provider) return;

      const response = await fetch(provider.testEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyId })
      });

      const result = await response.json();
      
      await updateAPIKey(keyId, {
        status: result.success ? 'active' : 'invalid',
        lastTested: new Date().toISOString()
      });

      // Refresh provider status
      await loadProviderStatuses();
    } catch (error) {
      console.error('Error testing connection:', error);
      await updateAPIKey(keyId, {
        status: 'invalid',
        lastTested: new Date().toISOString()
      });
    } finally {
      setTestingKeys(prev => {
        const newSet = new Set(prev);
        newSet.delete(keyId);
        return newSet;
      });
    }
  }, [apiKeys, updateAPIKey, loadProviderStatuses]);

  const toggleKeyVisibility = useCallback((keyId: string) => {
    setVisibleKeys(prev => {
      const newSet = new Set(prev);
      if (newSet.has(keyId)) {
        newSet.delete(keyId);
      } else {
        newSet.add(keyId);
      }
      return newSet;
    });
  }, []);

  const copyKeyToClipboard = useCallback(async (keyId: string, key: string) => {
    try {
      await navigator.clipboard.writeText(key);
      setCopiedKey(keyId);
      setTimeout(() => setCopiedKey(null), 2000);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
    }
  }, []);

  const getStatusIcon = (status: APIKey['status']) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'invalid':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'expired':
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
      case 'testing':
        return <Loader className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: APIKey['status']) => {
    const variants = {
      active: 'default',
      invalid: 'destructive',
      expired: 'secondary',
      testing: 'outline',
      inactive: 'outline'
    } as const;

    const labels = {
      active: 'פעיל',
      invalid: 'לא תקין',
      expired: 'פג תוקף',
      testing: 'בודק...',
      inactive: 'לא פעיל'
    };

    return (
      <Badge variant={variants[status] || 'outline'}>
        {labels[status] || status}
      </Badge>
    );
  };

  const maskApiKey = (key: string, isVisible: boolean) => {
    if (isVisible) return key;
    if (key.length <= 8) return '•'.repeat(key.length);
    return key.substring(0, 4) + '•'.repeat(key.length - 8) + key.substring(key.length - 4);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('he-IL').format(num);
  };

  // Group keys by provider
  const keysByProvider = useMemo(() => {
    const grouped: Record<string, APIKey[]> = {};
    apiKeys.forEach(key => {
      if (!grouped[key.providerId]) {
        grouped[key.providerId] = [];
      }
      grouped[key.providerId].push(key);
    });
    return grouped;
  }, [apiKeys]);

  return (
    <div className={`api-key-management ${className}`}>
      <Tabs defaultValue="keys" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="keys">
            <Key className="h-4 w-4 mr-2" />
            מפתחות API
          </TabsTrigger>
          <TabsTrigger value="status">
            <Activity className="h-4 w-4 mr-2" />
            סטטוס ספקים
          </TabsTrigger>
          <TabsTrigger value="usage">
            <BarChart3 className="h-4 w-4 mr-2" />
            סטטיסטיקות שימוש
          </TabsTrigger>
        </TabsList>

        {/* API Keys Tab */}
        <TabsContent value="keys" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium">ניהול מפתחות API</h3>
              <p className="text-sm text-muted-foreground">
                נהל מפתחות API עבור ספקי בינה מלאכותית שונים
              </p>
            </div>
            <Button onClick={() => setShowAddDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />
              הוסף מפתח
            </Button>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader className="h-6 w-6 animate-spin" />
              <span className="ml-2">טוען מפתחות...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {SUPPORTED_PROVIDERS.map(provider => {
                const providerKeys = keysByProvider[provider.id] || [];
                const providerStatus = providerStatuses[provider.id];
                
                return (
                  <Card key={provider.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {provider.icon}
                          <div>
                            <CardTitle className="text-base">{provider.displayName}</CardTitle>
                            <p className="text-sm text-muted-foreground">
                              {provider.description}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {providerStatus && (
                            <Badge variant={providerStatus.isConnected ? 'default' : 'destructive'}>
                              {providerStatus.isConnected ? 'מחובר' : 'לא מחובר'}
                            </Badge>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(provider.documentationUrl, '_blank')}
                          >
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      {providerKeys.length === 0 ? (
                        <div className="text-center py-6 text-muted-foreground">
                          <Key className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p>אין מפתחות API עבור {provider.displayName}</p>
                          <Button
                            variant="outline"
                            size="sm"
                            className="mt-2"
                            onClick={() => {
                              setNewKeyData(prev => ({ ...prev, providerId: provider.id }));
                              setShowAddDialog(true);
                            }}
                          >
                            הוסף מפתח ראשון
                          </Button>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {providerKeys.map(key => (
                            <div
                              key={key.id}
                              className="flex items-center justify-between p-3 border rounded-lg"
                            >
                              <div className="flex items-center gap-3 flex-1">
                                {getStatusIcon(testingKeys.has(key.id) ? 'testing' : key.status)}
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-medium">{key.name}</span>
                                    {getStatusBadge(testingKeys.has(key.id) ? 'testing' : key.status)}
                                    {key.isActive && (
                                      <Badge variant="outline" className="text-xs">
                                        פעיל
                                      </Badge>
                                    )}
                                  </div>
                                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <code className="bg-muted px-2 py-1 rounded text-xs">
                                      {maskApiKey(key.key, visibleKeys.has(key.id))}
                                    </code>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      className="h-6 w-6 p-0"
                                      onClick={() => toggleKeyVisibility(key.id)}
                                    >
                                      {visibleKeys.has(key.id) ? (
                                        <EyeOff className="h-3 w-3" />
                                      ) : (
                                        <Eye className="h-3 w-3" />
                                      )}
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      className="h-6 w-6 p-0"
                                      onClick={() => copyKeyToClipboard(key.id, key.key)}
                                    >
                                      {copiedKey === key.id ? (
                                        <Check className="h-3 w-3 text-green-500" />
                                      ) : (
                                        <Copy className="h-3 w-3" />
                                      )}
                                    </Button>
                                  </div>
                                  {key.lastUsed && (
                                    <div className="text-xs text-muted-foreground mt-1">
                                      שימוש אחרון: {new Date(key.lastUsed).toLocaleDateString('he-IL')}
                                    </div>
                                  )}
                                </div>
                              </div>
                              
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => testConnection(key.id)}
                                  disabled={testingKeys.has(key.id)}
                                >
                                  <TestTube className="h-4 w-4" />
                                </Button>
                                
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="sm">
                                      <Settings className="h-4 w-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    <DropdownMenuItem
                                      onClick={() => {
                                        setSelectedKey(key);
                                        setShowEditDialog(true);
                                      }}
                                    >
                                      <Edit3 className="h-4 w-4 mr-2" />
                                      עריכה
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                      onClick={() => updateAPIKey(key.id, { isActive: !key.isActive })}
                                    >
                                      {key.isActive ? (
                                        <>
                                          <XCircle className="h-4 w-4 mr-2" />
                                          השבת
                                        </>
                                      ) : (
                                        <>
                                          <CheckCircle className="h-4 w-4 mr-2" />
                                          הפעל
                                        </>
                                      )}
                                    </DropdownMenuItem>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem
                                      onClick={() => {
                                        setSelectedKey(key);
                                        setShowDeleteDialog(true);
                                      }}
                                      className="text-destructive"
                                    >
                                      <Trash2 className="h-4 w-4 mr-2" />
                                      מחק
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </TabsContent>

        {/* Provider Status Tab */}
        <TabsContent value="status" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium">סטטוס ספקים</h3>
              <p className="text-sm text-muted-foreground">
                מצב החיבור והזמינות של ספקי הבינה המלאכותית
              </p>
            </div>
            <Button variant="outline" onClick={loadProviderStatuses}>
              <RefreshCw className="h-4 w-4 mr-2" />
              רענן
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {SUPPORTED_PROVIDERS.map(provider => {
              const status = providerStatuses[provider.id];
              const hasKeys = keysByProvider[provider.id]?.length > 0;
              
              return (
                <Card key={provider.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {provider.icon}
                        <div>
                          <CardTitle className="text-base">{provider.displayName}</CardTitle>
                          <p className="text-sm text-muted-foreground">
                            {provider.supportedModels.length} מודלים
                          </p>
                        </div>
                      </div>
                      {status ? (
                        <Badge variant={status.isConnected ? 'default' : 'destructive'}>
                          {status.isConnected ? 'מחובר' : 'לא מחובר'}
                        </Badge>
                      ) : (
                        <Badge variant="outline">לא נבדק</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {!hasKeys ? (
                      <div className="text-center py-4 text-muted-foreground">
                        <AlertTriangle className="h-6 w-6 mx-auto mb-2" />
                        <p className="text-sm">נדרש מפתח API</p>
                      </div>
                    ) : status ? (
                      <>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <div className="text-muted-foreground">זמן תגובה</div>
                            <div className="font-medium">
                              {status.responseTime}ms
                            </div>
                          </div>
                          <div>
                            <div className="text-muted-foreground">בדיקה אחרונה</div>
                            <div className="font-medium">
                              {new Date(status.lastChecked).toLocaleTimeString('he-IL')}
                            </div>
                          </div>
                        </div>
                        
                        {status.availableModels.length > 0 && (
                          <div>
                            <div className="text-sm text-muted-foreground mb-2">מודלים זמינים</div>
                            <div className="flex flex-wrap gap-1">
                              {status.availableModels.map(model => (
                                <Badge key={model} variant="outline" className="text-xs">
                                  {model}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div>
                          <div className="text-sm text-muted-foreground mb-2">מגבלות קצב</div>
                          <div className="space-y-1 text-xs">
                            <div className="flex justify-between">
                              <span>בקשות לדקה:</span>
                              <span>{formatNumber(status.rateLimits.requestsPerMinute)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>טוקנים לדקה:</span>
                              <span>{formatNumber(status.rateLimits.tokensPerMinute)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>בקשות ליום:</span>
                              <span>{formatNumber(status.rateLimits.requestsPerDay)}</span>
                            </div>
                          </div>
                        </div>
                        
                        {status.errorMessage && (
                          <div className="p-2 bg-destructive/10 border border-destructive/20 rounded text-sm text-destructive">
                            {status.errorMessage}
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-center py-4 text-muted-foreground">
                        <Clock className="h-6 w-6 mx-auto mb-2" />
                        <p className="text-sm">ממתין לבדיקה</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Usage Statistics Tab */}
        <TabsContent value="usage" className="space-y-4">
          <div>
            <h3 className="text-lg font-medium">סטטיסטיקות שימוש</h3>
            <p className="text-sm text-muted-foreground">
              מעקב אחר השימוש והעלויות של כל ספק
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {Object.entries(usageStats).map(([providerId, stats]) => {
              const provider = SUPPORTED_PROVIDERS.find(p => p.id === providerId);
              if (!provider) return null;
              
              return (
                <Card key={providerId}>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      {provider.icon}
                      <div>
                        <CardTitle className="text-base">{provider.displayName}</CardTitle>
                        <p className="text-sm text-muted-foreground">
                          חודש נוכחי
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-3 bg-muted/50 rounded">
                        <div className="text-2xl font-bold text-blue-600">
                          {formatNumber(stats.totals.requests)}
                        </div>
                        <div className="text-sm text-muted-foreground">בקשות</div>
                      </div>
                      <div className="text-center p-3 bg-muted/50 rounded">
                        <div className="text-2xl font-bold text-green-600">
                          {formatNumber(stats.totals.tokens)}
                        </div>
                        <div className="text-sm text-muted-foreground">טוקנים</div>
                      </div>
                      <div className="text-center p-3 bg-muted/50 rounded">
                        <div className="text-2xl font-bold text-purple-600">
                          {formatCurrency(stats.totals.cost)}
                        </div>
                        <div className="text-sm text-muted-foreground">עלות</div>
                      </div>
                      <div className="text-center p-3 bg-muted/50 rounded">
                        <div className="text-2xl font-bold text-red-600">
                          {stats.totals.errors}
                        </div>
                        <div className="text-sm text-muted-foreground">שגיאות</div>
                      </div>
                    </div>
                    
                    {/* Simple usage chart representation */}
                    <div>
                      <div className="text-sm font-medium mb-2">מגמת שימוש (7 ימים אחרונים)</div>
                      <div className="flex items-end gap-1 h-16">
                        {stats.data.slice(-7).map((day, index) => {
                          const maxRequests = Math.max(...stats.data.slice(-7).map(d => d.requests));
                          const height = maxRequests > 0 ? (day.requests / maxRequests) * 100 : 0;
                          
                          return (
                            <div
                              key={index}
                              className="flex-1 bg-primary/20 rounded-t"
                              style={{ height: `${height}%` }}
                              title={`${day.date}: ${day.requests} בקשות`}
                            />
                          );
                        })}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>
      </Tabs>

      {/* Add API Key Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>הוסף מפתח API</DialogTitle>
            <DialogDescription>
              הוסף מפתח API חדש עבור ספק בינה מלאכותית
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="provider">ספק</Label>
              <select
                id="provider"
                value={newKeyData.providerId}
                onChange={(e) => setNewKeyData(prev => ({ ...prev, providerId: e.target.value }))}
                className="w-full mt-1 p-2 border rounded-md"
              >
                <option value="">בחר ספק</option>
                {SUPPORTED_PROVIDERS.map(provider => (
                  <option key={provider.id} value={provider.id}>
                    {provider.displayName}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <Label htmlFor="key-name">שם המפתח</Label>
              <Input
                id="key-name"
                value={newKeyData.name}
                onChange={(e) => setNewKeyData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="למשל: Production Key"
              />
            </div>
            
            <div>
              <Label htmlFor="api-key">מפתח API</Label>
              <div className="relative">
                <Input
                  id="api-key"
                  type={newKeyData.showKey ? 'text' : 'password'}
                  value={newKeyData.key}
                  onChange={(e) => setNewKeyData(prev => ({ ...prev, key: e.target.value }))}
                  placeholder={
                    newKeyData.providerId 
                      ? SUPPORTED_PROVIDERS.find(p => p.id === newKeyData.providerId)?.keyExample
                      : 'הזן מפתח API'
                  }
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute left-2 top-1/2 transform -translate-y-1/2"
                  onClick={() => setNewKeyData(prev => ({ ...prev, showKey: !prev.showKey }))}
                >
                  {newKeyData.showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
              {newKeyData.providerId && (
                <p className="text-xs text-muted-foreground mt-1">
                  פורמט: {SUPPORTED_PROVIDERS.find(p => p.id === newKeyData.providerId)?.keyFormat}
                </p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddDialog(false)}>
              ביטול
            </Button>
            <Button 
              onClick={saveAPIKey}
              disabled={!newKeyData.providerId || !newKeyData.name || !newKeyData.key}
            >
              הוסף מפתח
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>מחק מפתח API</DialogTitle>
            <DialogDescription>
              האם אתה בטוח שברצונך למחוק את המפתח "{selectedKey?.name}"?
              פעולה זו לא ניתנת לביטול.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              ביטול
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => selectedKey && deleteAPIKey(selectedKey.id)}
            >
              מחק
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};