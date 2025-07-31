import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import {
  Activity,
  BarChart3,
  Clock,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Zap,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Settings,
  Eye,
  EyeOff,
  Gauge,
  Target,
  Award,
  Flame,
  Users,
  Calendar,
  Filter,
  Download,
  Bell,
  BellOff,
  Cpu,
  MemoryStick,
  Timer,
  LineChart,
  PieChart,
  BarChart,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';// Perfo
rmance metrics interfaces
export interface ModelMetrics {
  modelId: string;
  modelName: string;
  provider: string;
  responseTime: {
    current: number;
    average: number;
    min: number;
    max: number;
    history: Array<{ timestamp: string; value: number }>;
  };
  tokenUsage: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
    tokensPerSecond: number;
    efficiency: number;
  };
  costMetrics: {
    totalCost: number;
    costPerToken: number;
    costPerRequest: number;
    dailyCost: number;
    monthlyCost: number;
    costTrend: 'up' | 'down' | 'stable';
  };
  reliability: {
    successRate: number;
    errorRate: number;
    uptime: number;
    lastError?: string;
    errorHistory: Array<{ timestamp: string; error: string }>;
  };
  performance: {
    throughput: number;
    concurrency: number;
    queueLength: number;
    memoryUsage: number;
    cpuUsage: number;
  };
  usage: {
    totalRequests: number;
    requestsPerHour: number;
    requestsPerDay: number;
    activeUsers: number;
    popularityScore: number;
  };
  lastUpdated: string;
}expor
t interface PerformanceAlert {
  id: string;
  type: 'warning' | 'error' | 'info' | 'success';
  title: string;
  message: string;
  modelId: string;
  threshold: number;
  currentValue: number;
  timestamp: string;
  isActive: boolean;
  acknowledged: boolean;
}

export interface AlertThreshold {
  id: string;
  name: string;
  metric: 'responseTime' | 'cost' | 'errorRate' | 'tokenUsage';
  condition: 'above' | 'below' | 'equals';
  value: number;
  enabled: boolean;
  modelIds: string[];
}

export interface ComparisonData {
  models: string[];
  metrics: {
    responseTime: Record<string, number>;
    cost: Record<string, number>;
    reliability: Record<string, number>;
    efficiency: Record<string, number>;
  };
  recommendations: Array<{
    type: 'fastest' | 'cheapest' | 'most_reliable' | 'most_efficient';
    modelId: string;
    reason: string;
    score: number;
  }>;
}

interface PerformanceMonitorProps {
  className?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
  showAlerts?: boolean;
  enableComparison?: boolean;
  compactMode?: boolean;
  selectedModels?: string[];
  onModelSelect?: (modelId: string) => void;
  onAlertAcknowledge?: (alertId: string) => void;
}ex
port const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  className = '',
  autoRefresh = true,
  refreshInterval = 30000,
  showAlerts = true,
  enableComparison = true,
  compactMode = false,
  selectedModels = [],
  onModelSelect,
  onAlertAcknowledge
}) => {
  // State management
  const [metrics, setMetrics] = useState<Record<string, ModelMetrics>>({});
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);
  const [alertThresholds, setAlertThresholds] = useState<AlertThreshold[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [selectedTimeRange, setSelectedTimeRange] = useState<'1h' | '6h' | '24h' | '7d' | '30d'>('24h');
  const [viewMode, setViewMode] = useState<'overview' | 'detailed' | 'comparison'>('overview');
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());
  
  // Refs
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load data on mount
  useEffect(() => {
    loadMetrics();
    loadAlerts();
    loadAlertThresholds();
    
    if (autoRefresh) {
      refreshIntervalRef.current = setInterval(() => {
        loadMetrics();
        loadAlerts();
      }, refreshInterval);
    }

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval]);

  // Load comparison data when models change
  useEffect(() => {
    if (enableComparison && selectedModels.length > 1) {
      loadComparisonData();
    }
  }, [selectedModels, enableComparison]);

  const loadMetrics = useCallback(async () => {
    try {
      const response = await fetch(`/api/performance/metrics?timeRange=${selectedTimeRange}`);
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
        setLastRefresh(new Date());
      }
    } catch (error) {
      console.error('Error loading metrics:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedTimeRange]); 
 const loadAlerts = useCallback(async () => {
    if (!showAlerts) return;
    
    try {
      const response = await fetch('/api/performance/alerts');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data);
      }
    } catch (error) {
      console.error('Error loading alerts:', error);
    }
  }, [showAlerts]);

  const loadAlertThresholds = useCallback(async () => {
    try {
      const response = await fetch('/api/performance/alert-thresholds');
      if (response.ok) {
        const data = await response.json();
        setAlertThresholds(data);
      }
    } catch (error) {
      console.error('Error loading alert thresholds:', error);
    }
  }, []);

  const loadComparisonData = useCallback(async () => {
    try {
      const response = await fetch('/api/performance/comparison', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ models: selectedModels, timeRange: selectedTimeRange })
      });
      if (response.ok) {
        const data = await response.json();
        setComparisonData(data);
      }
    } catch (error) {
      console.error('Error loading comparison data:', error);
    }
  }, [selectedModels, selectedTimeRange]);

  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      const response = await fetch(`/api/performance/alerts/${alertId}/acknowledge`, {
        method: 'POST'
      });
      if (response.ok) {
        setAlerts(prev => prev.map(alert => 
          alert.id === alertId ? { ...alert, acknowledged: true } : alert
        ));
        onAlertAcknowledge?.(alertId);
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  }, [onAlertAcknowledge]);  con
st toggleCardExpansion = useCallback((cardId: string) => {
    setExpandedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(cardId)) {
        newSet.delete(cardId);
      } else {
        newSet.add(cardId);
      }
      return newSet;
    });
  }, []);

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

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const getPerformanceColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value <= thresholds.good) return 'text-green-600';
    if (value <= thresholds.warning) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'down': return <TrendingDown className="h-4 w-4 text-green-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getAlertIcon = (type: PerformanceAlert['type']) => {
    switch (type) {
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'success': return <CheckCircle className="h-4 w-4 text-green-500" />;
      default: return <Activity className="h-4 w-4 text-blue-500" />;
    }
  };  // Ac
tive alerts (unacknowledged)
  const activeAlerts = useMemo(() => 
    alerts.filter(alert => alert.isActive && !alert.acknowledged),
    [alerts]
  );

  // Sorted models by performance
  const sortedModels = useMemo(() => {
    return Object.values(metrics).sort((a, b) => {
      // Sort by overall performance score
      const scoreA = (a.reliability.successRate * 0.3) + 
                    ((5000 - a.responseTime.average) / 5000 * 0.3) +
                    (a.tokenUsage.efficiency * 0.2) +
                    (a.usage.popularityScore * 0.2);
      const scoreB = (b.reliability.successRate * 0.3) + 
                    ((5000 - b.responseTime.average) / 5000 * 0.3) +
                    (b.tokenUsage.efficiency * 0.2) +
                    (b.usage.popularityScore * 0.2);
      return scoreB - scoreA;
    });
  }, [metrics]);

  const renderMetricCard = (metric: ModelMetrics) => {
    const isExpanded = expandedCards.has(metric.modelId);
    
    return (
      <Card key={metric.modelId} className="relative">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Badge variant="outline">{metric.provider}</Badge>
                <h3 className="font-medium">{metric.modelName}</h3>
              </div>
              <div className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${
                  metric.reliability.successRate > 95 ? 'bg-green-500' :
                  metric.reliability.successRate > 90 ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
                <span className="text-xs text-muted-foreground">
                  {metric.reliability.successRate.toFixed(1)}% uptime
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onModelSelect?.(metric.modelId)}
              >
                <Eye className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleCardExpansion(metric.modelId)}
              >
                {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </CardHeader>    
    <CardContent className="space-y-4">
          {/* Key Metrics Row */}
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`text-lg font-bold ${getPerformanceColor(metric.responseTime.average, { good: 1000, warning: 3000 })}`}>
                {formatDuration(metric.responseTime.average)}
              </div>
              <div className="text-xs text-muted-foreground">זמן תגובה ממוצע</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">
                {formatNumber(metric.tokenUsage.tokensPerSecond)}
              </div>
              <div className="text-xs text-muted-foreground">טוקנים/שנייה</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">
                {formatCurrency(metric.costMetrics.costPerRequest)}
              </div>
              <div className="text-xs text-muted-foreground">עלות/בקשה</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-purple-600">
                {formatNumber(metric.usage.requestsPerHour)}
              </div>
              <div className="text-xs text-muted-foreground">בקשות/שעה</div>
            </div>
          </div>

          {/* Progress Bars */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>יעילות</span>
              <span>{(metric.tokenUsage.efficiency * 100).toFixed(1)}%</span>
            </div>
            <Progress value={metric.tokenUsage.efficiency * 100} className="h-2" />
            
            <div className="flex items-center justify-between text-sm">
              <span>אמינות</span>
              <span>{metric.reliability.successRate.toFixed(1)}%</span>
            </div>
            <Progress value={metric.reliability.successRate} className="h-2" />
          </div>

          {/* Expanded Details */}
          {isExpanded && (
            <div className="space-y-4 border-t pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    זמני תגובה
                  </h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>מינימום:</span>
                      <span>{formatDuration(metric.responseTime.min)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>מקסימום:</span>
                      <span>{formatDuration(metric.responseTime.max)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>נוכחי:</span>
                      <span>{formatDuration(metric.responseTime.current)}</span>
                    </div>
                  </div>
                </div>   
             <div>
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <DollarSign className="h-4 w-4" />
                    עלויות
                  </h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>יומי:</span>
                      <span>{formatCurrency(metric.costMetrics.dailyCost)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>חודשי:</span>
                      <span>{formatCurrency(metric.costMetrics.monthlyCost)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>מגמה:</span>
                      <div className="flex items-center gap-1">
                        {getTrendIcon(metric.costMetrics.costTrend)}
                        <span className="capitalize">{metric.costMetrics.costTrend}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <Cpu className="h-4 w-4" />
                    ביצועים
                  </h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>תפוקה:</span>
                      <span>{formatNumber(metric.performance.throughput)} req/min</span>
                    </div>
                    <div className="flex justify-between">
                      <span>זיכרון:</span>
                      <span>{metric.performance.memoryUsage.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>CPU:</span>
                      <span>{metric.performance.cpuUsage.toFixed(1)}%</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    שימוש
                  </h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>סה"כ בקשות:</span>
                      <span>{formatNumber(metric.usage.totalRequests)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>משתמשים פעילים:</span>
                      <span>{formatNumber(metric.usage.activeUsers)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>ציון פופולריות:</span>
                      <span>{metric.usage.popularityScore.toFixed(1)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }; 
 const renderAlertsPanel = () => (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            התראות ביצועים
            {activeAlerts.length > 0 && (
              <Badge variant="destructive">{activeAlerts.length}</Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Switch
              checked={alertsEnabled}
              onCheckedChange={setAlertsEnabled}
            />
            <Label>התראות פעילות</Label>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {activeAlerts.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
            <p>אין התראות פעילות</p>
          </div>
        ) : (
          <div className="space-y-3">
            {activeAlerts.map(alert => (
              <div
                key={alert.id}
                className={`p-3 border rounded-lg ${
                  alert.type === 'error' ? 'border-red-200 bg-red-50' :
                  alert.type === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                  'border-blue-200 bg-blue-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-2">
                    {getAlertIcon(alert.type)}
                    <div>
                      <h4 className="font-medium text-sm">{alert.title}</h4>
                      <p className="text-sm text-muted-foreground mt-1">
                        {alert.message}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                        <span>מודל: {metrics[alert.modelId]?.modelName}</span>
                        <span>סף: {alert.threshold}</span>
                        <span>נוכחי: {alert.currentValue}</span>
                        <span>{new Date(alert.timestamp).toLocaleTimeString('he-IL')}</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => acknowledgeAlert(alert.id)}
                  >
                    <CheckCircle className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );  const r
enderComparisonView = () => {
    if (!comparisonData || selectedModels.length < 2) {
      return (
        <Card>
          <CardContent className="text-center py-8">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
            <p className="text-muted-foreground">
              בחר לפחות 2 מודלים להשוואה
            </p>
          </CardContent>
        </Card>
      );
    }

    return (
      <div className="space-y-4">
        {/* Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              המלצות
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {comparisonData.recommendations.map(rec => (
                <div key={rec.type} className="p-3 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    {rec.type === 'fastest' && <Zap className="h-4 w-4 text-yellow-500" />}
                    {rec.type === 'cheapest' && <DollarSign className="h-4 w-4 text-green-500" />}
                    {rec.type === 'most_reliable' && <CheckCircle className="h-4 w-4 text-blue-500" />}
                    {rec.type === 'most_efficient' && <Target className="h-4 w-4 text-purple-500" />}
                    <span className="font-medium text-sm">
                      {rec.type === 'fastest' && 'הכי מהיר'}
                      {rec.type === 'cheapest' && 'הכי חסכוני'}
                      {rec.type === 'most_reliable' && 'הכי אמין'}
                      {rec.type === 'most_efficient' && 'הכי יעיל'}
                    </span>
                  </div>
                  <div className="text-sm">
                    <div className="font-medium">{metrics[rec.modelId]?.modelName}</div>
                    <div className="text-muted-foreground">{rec.reason}</div>
                    <div className="mt-1">
                      <Badge variant="outline">ציון: {rec.score.toFixed(1)}</Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Comparison Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">זמני תגובה</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(comparisonData.metrics.responseTime).map(([modelId, value]) => (
                  <div key={modelId} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>{metrics[modelId]?.modelName}</span>
                      <span>{formatDuration(value)}</span>
                    </div>
                    <Progress 
                      value={(value / Math.max(...Object.values(comparisonData.metrics.responseTime))) * 100} 
                      className="h-2" 
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>   
       <Card>
            <CardHeader>
              <CardTitle className="text-base">עלויות</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(comparisonData.metrics.cost).map(([modelId, value]) => (
                  <div key={modelId} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>{metrics[modelId]?.modelName}</span>
                      <span>{formatCurrency(value)}</span>
                    </div>
                    <Progress 
                      value={(value / Math.max(...Object.values(comparisonData.metrics.cost))) * 100} 
                      className="h-2" 
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">אמינות</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(comparisonData.metrics.reliability).map(([modelId, value]) => (
                  <div key={modelId} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>{metrics[modelId]?.modelName}</span>
                      <span>{value.toFixed(1)}%</span>
                    </div>
                    <Progress value={value} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">יעילות</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(comparisonData.metrics.efficiency).map(([modelId, value]) => (
                  <div key={modelId} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>{metrics[modelId]?.modelName}</span>
                      <span>{(value * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={value * 100} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }; 
 if (compactMode) {
    return (
      <div className={`performance-monitor-compact ${className}`}>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Activity className="h-4 w-4" />
                ביצועי מודלים
              </CardTitle>
              <div className="flex items-center gap-2">
                {activeAlerts.length > 0 && (
                  <Badge variant="destructive" className="text-xs">
                    {activeAlerts.length}
                  </Badge>
                )}
                <Button variant="ghost" size="sm" onClick={loadMetrics}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {sortedModels.slice(0, 3).map(metric => (
                <div key={metric.modelId} className="flex items-center justify-between p-2 border rounded">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      metric.reliability.successRate > 95 ? 'bg-green-500' :
                      metric.reliability.successRate > 90 ? 'bg-yellow-500' : 'bg-red-500'
                    }`} />
                    <span className="text-sm font-medium">{metric.modelName}</span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{formatDuration(metric.responseTime.average)}</span>
                    <span>{formatCurrency(metric.costMetrics.costPerRequest)}</span>
                    <span>{metric.reliability.successRate.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={`performance-monitor ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Activity className="h-6 w-6" />
            מוניטור ביצועי מודלים
          </h2>
          <p className="text-muted-foreground">
            מעקב בזמן אמת אחר ביצועים, עלויות ואמינות
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            עודכן: {lastRefresh.toLocaleTimeString('he-IL')}
          </Badge>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Calendar className="h-4 w-4 mr-2" />
                {selectedTimeRange}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>טווח זמן</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {['1h', '6h', '24h', '7d', '30d'].map(range => (
                <DropdownMenuItem
                  key={range}
                  onClick={() => setSelectedTimeRange(range as any)}
                >
                  {range}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <Button variant="outline" size="sm" onClick={loadMetrics}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>    
  <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as any)} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">
            <BarChart3 className="h-4 w-4 mr-2" />
            סקירה כללית
          </TabsTrigger>
          <TabsTrigger value="detailed">
            <LineChart className="h-4 w-4 mr-2" />
            פירוט מלא
          </TabsTrigger>
          <TabsTrigger value="comparison">
            <PieChart className="h-4 w-4 mr-2" />
            השוואה
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {showAlerts && renderAlertsPanel()}
          
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin" />
              <span className="ml-2">טוען נתוני ביצועים...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
              {sortedModels.map(renderMetricCard)}
            </div>
          )}
        </TabsContent>

        <TabsContent value="detailed" className="space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin" />
              <span className="ml-2">טוען נתונים מפורטים...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {sortedModels.map(metric => renderMetricCard(metric))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="comparison" className="space-y-4">
          {renderComparisonView()}
        </TabsContent>
      </Tabs>
    </div>
  );
};