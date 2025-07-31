import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { 
  Bot, 
  ChevronDown, 
  Zap, 
  Clock, 
  TrendingUp, 
  Star, 
  AlertCircle,
  CheckCircle,
  Loader,
  Settings,
  BarChart3,
  Wifi,
  WifiOff,
  Crown,
  Shield,
  Gauge,
  Activity,
  DollarSign,
  Users,
  Target,
  Sparkles,
  RefreshCw,
  ArrowUpDown,
  Filter,
  X,
  Info,
  Lightbulb,
  Flame,
  Award,
  Cpu,
  Zap as Lightning,
  Timer
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuLabel,
  DropdownMenuGroup,
} from '@/components/ui/dropdown-menu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export interface ModelMetrics {
  responseTime: number;
  tokensPerSecond: number;
  successRate: number;
  totalRequests: number;
  averageCost: number;
  lastUsed: string;
  uptime: number;
  throughput: number;
  errorRate: number;
  avgTokensPerRequest: number;
}

export interface ModelCapability {
  name: string;
  supported: boolean;
  quality: 'excellent' | 'good' | 'fair' | 'poor';
}

export interface LLMModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  maxTokens: number;
  costPerToken: number;
  capabilities: ModelCapability[];
  isActive: boolean;
  isAvailable: boolean;
  contextWindow: number;
  trainingDataCutoff: string | null;
  version: string | null;
  parameters: Record<string, any>;
  metadata: Record<string, any>;
  metrics: ModelMetrics;
  tier: 'free' | 'premium' | 'enterprise';
  category: 'chat' | 'code' | 'creative' | 'analysis';
}

export interface ModelRecommendation {
  modelId: string;
  reason: string;
  score: number;
  category: 'performance' | 'cost' | 'capability' | 'reliability' | 'trending';
  icon: React.ReactNode;
}

export interface QuickSwitchOption {
  modelId: string;
  name: string;
  provider: string;
  responseTime: number;
  isAvailable: boolean;
  reason?: string;
}

export interface EnhancedModelSelectorProps {
  onModelChange?: (modelId: string) => void;
  showMetrics?: boolean;
  showRecommendations?: boolean;
  compact?: boolean;
  className?: string;
  enableQuickSwitch?: boolean;
  showPerformanceDetails?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
  showTrending?: boolean;
  enableSmartRecommendations?: boolean;
}

export const EnhancedModelSelector: React.FC<EnhancedModelSelectorProps> = ({
  onModelChange,
  showMetrics = true,
  showRecommendations = true,
  compact = false,
  className = '',
  enableQuickSwitch = true,
  showPerformanceDetails = false,
  autoRefresh = true,
  refreshInterval = 30000,
  showTrending = true,
  enableSmartRecommendations = true
}) => {
  const [models, setModels] = useState<LLMModel[]>([]);
  const [activeModel, setActiveModel] = useState<LLMModel | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isChangingModel, setIsChangingModel] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'performance' | 'cost' | 'usage' | 'trending'>('usage');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [connectionStatus, setConnectionStatus] = useState<Record<string, 'connected' | 'connecting' | 'disconnected'>>({});
  const [quickSwitchOpen, setQuickSwitchOpen] = useState(false);
  const [performanceHistory, setPerformanceHistory] = useState<Record<string, number[]>>({});
  const [modelUsageStats, setModelUsageStats] = useState<Record<string, { hourly: number[], daily: number[] }>>({});
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch models and active model
  useEffect(() => {
    fetchModels();
    fetchActiveModel();
    fetchUsageStats();
    
    // Set up real-time updates
    if (autoRefresh) {
      refreshIntervalRef.current = setInterval(() => {
        updateModelMetrics();
        updateConnectionStatus();
      }, refreshInterval);
    }

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval]);

  const fetchModels = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/llm/models');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: LLMModel[] = await response.json();
      setModels(data);
    } catch (error) {
      console.error('Error fetching models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchActiveModel = async () => {
    try {
      const response = await fetch('/api/llm/active-model');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: LLMModel | null = await response.json();
      setActiveModel(data);
    } catch (error) {
      console.error('Error fetching active model:', error);
    }
  };

  const fetchUsageStats = async () => {
    try {
      const response = await fetch('/api/llm/usage-stats');
      if (!response.ok) return;
      const stats = await response.json();
      setModelUsageStats(stats);
    } catch (error) {
      console.error('Error fetching usage stats:', error);
    }
  };

  const updateModelMetrics = async () => {
    try {
      const response = await fetch('/api/llm/model-metrics');
      if (!response.ok) return;
      const metrics = await response.json();
      
      setModels(prev => prev.map(model => {
        const newMetrics = metrics[model.id] || model.metrics;
        
        // Update performance history for trending
        setPerformanceHistory(prevHistory => ({
          ...prevHistory,
          [model.id]: [
            ...(prevHistory[model.id] || []).slice(-9), // Keep last 10 data points
            newMetrics.responseTime
          ]
        }));
        
        return {
          ...model,
          metrics: newMetrics
        };
      }));
      
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Error updating model metrics:', error);
    }
  };

  const updateConnectionStatus = async () => {
    try {
      const response = await fetch('/api/llm/connection-status');
      if (!response.ok) return;
      const status = await response.json();
      setConnectionStatus(status);
    } catch (error) {
      console.error('Error updating connection status:', error);
    }
  };

  const forceRefresh = async () => {
    setIsLoading(true);
    await Promise.all([
      fetchModels(),
      fetchActiveModel(),
      updateModelMetrics(),
      updateConnectionStatus(),
      fetchUsageStats()
    ]);
    setIsLoading(false);
  };

  const handleModelChange = async (modelId: string) => {
    if (isChangingModel || activeModel?.id === modelId) return;
    
    setIsChangingModel(true);
    try {
      const response = await fetch('/api/llm/active-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId }),
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const result = await response.json();
      if (result.success) {
        await fetchActiveModel();
        onModelChange?.(modelId);
        setQuickSwitchOpen(false);
      }
    } catch (error) {
      console.error('Error changing model:', error);
    } finally {
      setIsChangingModel(false);
    }
  };

  // Enhanced recommendations with smart analysis
  const recommendations = useMemo((): ModelRecommendation[] => {
    if (!showRecommendations || models.length === 0) return [];
    
    const availableModels = models.filter(m => m.isAvailable);
    if (availableModels.length === 0) return [];
    
    const recs: ModelRecommendation[] = [];
    
    // Performance champion
    const fastestModel = availableModels.reduce((prev, current) => 
      current.metrics.responseTime < prev.metrics.responseTime ? current : prev
    );
    recs.push({
      modelId: fastestModel.id,
      reason: `הכי מהיר - ${fastestModel.metrics.responseTime}ms זמן תגובה`,
      score: 95 - (fastestModel.metrics.responseTime / 100),
      category: 'performance',
      icon: <Lightning className="h-3 w-3 text-yellow-500" />
    });
    
    // Cost optimizer
    const cheapestModel = availableModels.reduce((prev, current) => 
      current.costPerToken < prev.costPerToken ? current : prev
    );
    recs.push({
      modelId: cheapestModel.id,
      reason: `הכי חסכוני - $${cheapestModel.costPerToken.toFixed(6)} לטוקן`,
      score: 90,
      category: 'cost',
      icon: <DollarSign className="h-3 w-3 text-green-500" />
    });
    
    // Reliability champion
    const reliableModel = availableModels.reduce((prev, current) => 
      current.metrics.successRate > prev.metrics.successRate ? current : prev
    );
    recs.push({
      modelId: reliableModel.id,
      reason: `הכי אמין - ${reliableModel.metrics.successRate}% שיעור הצלחה`,
      score: reliableModel.metrics.successRate * 0.9,
      category: 'reliability',
      icon: <Shield className="h-3 w-3 text-blue-500" />
    });
    
    // Popular choice
    const popularModel = availableModels.reduce((prev, current) => 
      current.metrics.totalRequests > prev.metrics.totalRequests ? current : prev
    );
    if (popularModel.metrics.totalRequests > 0) {
      recs.push({
        modelId: popularModel.id,
        reason: `הכי פופולרי - ${popularModel.metrics.totalRequests} שימושים`,
        score: Math.min(85, 50 + (popularModel.metrics.totalRequests / 10)),
        category: 'capability',
        icon: <Users className="h-3 w-3 text-purple-500" />
      });
    }
    
    // Trending up (improving performance)
    if (showTrending) {
      const trendingModel = availableModels.find(model => {
        const history = performanceHistory[model.id];
        if (!history || history.length < 3) return false;
        
        const recent = history.slice(-3);
        const older = history.slice(-6, -3);
        if (older.length === 0) return false;
        
        const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
        const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
        
        return recentAvg < olderAvg * 0.9; // 10% improvement
      });
      
      if (trendingModel) {
        recs.push({
          modelId: trendingModel.id,
          reason: `משתפר - ביצועים עולים בזמן האחרון`,
          score: 80,
          category: 'trending',
          icon: <TrendingUp className="h-3 w-3 text-orange-500" />
        });
      }
    }
    
    // Smart recommendation based on current usage patterns
    if (enableSmartRecommendations && activeModel) {
      const currentCategory = activeModel.category;
      const similarModels = availableModels.filter(m => 
        m.category === currentCategory && m.id !== activeModel.id
      );
      
      if (similarModels.length > 0) {
        const smartChoice = similarModels.reduce((prev, current) => {
          const prevScore = (prev.metrics.successRate * 0.4) + 
                           ((3000 - prev.metrics.responseTime) * 0.3) + 
                           (prev.metrics.totalRequests * 0.3);
          const currentScore = (current.metrics.successRate * 0.4) + 
                              ((3000 - current.metrics.responseTime) * 0.3) + 
                              (current.metrics.totalRequests * 0.3);
          return currentScore > prevScore ? current : prev;
        });
        
        recs.push({
          modelId: smartChoice.id,
          reason: `מומלץ עבור ${currentCategory} - ביצועים מאוזנים`,
          score: 82,
          category: 'capability',
          icon: <Lightbulb className="h-3 w-3 text-amber-500" />
        });
      }
    }
    
    // Remove duplicates and sort by score
    const uniqueRecs = recs.filter((rec, index, self) => 
      index === self.findIndex(r => r.modelId === rec.modelId)
    );
    
    return uniqueRecs.sort((a, b) => b.score - a.score).slice(0, 5);
  }, [models, showRecommendations, performanceHistory, showTrending, enableSmartRecommendations, activeModel]);

  // Quick switch options for fast model switching
  const quickSwitchOptions = useMemo((): QuickSwitchOption[] => {
    if (!enableQuickSwitch) return [];
    
    const availableModels = models.filter(m => m.isAvailable && m.id !== activeModel?.id);
    
    // Get top 5 models based on different criteria
    const options: QuickSwitchOption[] = [];
    
    // Fastest model
    const fastest = availableModels.reduce((prev, current) => 
      current.metrics.responseTime < prev.metrics.responseTime ? current : prev
    );
    if (fastest) {
      options.push({
        modelId: fastest.id,
        name: fastest.name,
        provider: fastest.provider,
        responseTime: fastest.metrics.responseTime,
        isAvailable: fastest.isAvailable,
        reason: 'הכי מהיר'
      });
    }
    
    // Most reliable
    const reliable = availableModels.reduce((prev, current) => 
      current.metrics.successRate > prev.metrics.successRate ? current : prev
    );
    if (reliable && reliable.id !== fastest?.id) {
      options.push({
        modelId: reliable.id,
        name: reliable.name,
        provider: reliable.provider,
        responseTime: reliable.metrics.responseTime,
        isAvailable: reliable.isAvailable,
        reason: 'הכי אמין'
      });
    }
    
    // Most popular
    const popular = availableModels.reduce((prev, current) => 
      current.metrics.totalRequests > prev.metrics.totalRequests ? current : prev
    );
    if (popular && !options.find(o => o.modelId === popular.id)) {
      options.push({
        modelId: popular.id,
        name: popular.name,
        provider: popular.provider,
        responseTime: popular.metrics.responseTime,
        isAvailable: popular.isAvailable,
        reason: 'הכי פופולרי'
      });
    }
    
    return options.slice(0, 4);
  }, [models, activeModel, enableQuickSwitch]);

  // Filter and sort models
  const filteredModels = useMemo(() => {
    let filtered = models.filter(model => {
      if (selectedCategory === 'all') return true;
      return model.category === selectedCategory;
    });
    
    // Sort models
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'performance':
          return a.metrics.responseTime - b.metrics.responseTime;
        case 'cost':
          return a.costPerToken - b.costPerToken;
        case 'usage':
          return b.metrics.totalRequests - a.metrics.totalRequests;
        case 'trending':
          const aHistory = performanceHistory[a.id] || [];
          const bHistory = performanceHistory[b.id] || [];
          if (aHistory.length < 2 || bHistory.length < 2) return 0;
          
          const aTrend = aHistory[aHistory.length - 1] - aHistory[0];
          const bTrend = bHistory[bHistory.length - 1] - bHistory[0];
          return aTrend - bTrend; // Lower is better (negative trend = improving)
        default:
          return 0;
      }
    });
    
    return filtered;
  }, [models, selectedCategory, sortBy, performanceHistory]);

  const getStatusIcon = (model: LLMModel) => {
    const status = connectionStatus[model.id] || 'disconnected';
    
    if (!model.isAvailable || status === 'disconnected') {
      return <WifiOff className="h-4 w-4 text-red-500" />;
    }
    if (status === 'connecting') {
      return <Loader className="h-4 w-4 text-yellow-500 animate-spin" />;
    }
    if (model.metrics.uptime > 99) {
      return <Wifi className="h-4 w-4 text-green-500" />;
    }
    return <AlertCircle className="h-4 w-4 text-yellow-500" />;
  };

  const getPerformanceColor = (responseTime: number) => {
    if (responseTime < 1000) return 'text-green-600';
    if (responseTime < 3000) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'free': return <Shield className="h-3 w-3 text-blue-500" />;
      case 'premium': return <Star className="h-3 w-3 text-yellow-500" />;
      case 'enterprise': return <Crown className="h-3 w-3 text-purple-500" />;
      default: return null;
    }
  };

  const getTrendingIndicator = (modelId: string) => {
    const history = performanceHistory[modelId];
    if (!history || history.length < 3) return null;
    
    const recent = history.slice(-3).reduce((a, b) => a + b, 0) / 3;
    const older = history.slice(-6, -3);
    if (older.length === 0) return null;
    
    const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
    const improvement = ((olderAvg - recent) / olderAvg) * 100;
    
    if (improvement > 10) {
      return <TrendingUp className="h-3 w-3 text-green-500" title={`משתפר ב-${improvement.toFixed(1)}%`} />;
    } else if (improvement < -10) {
      return <TrendingUp className="h-3 w-3 text-red-500 rotate-180" title={`מתדרדר ב-${Math.abs(improvement).toFixed(1)}%`} />;
    }
    return null;
  };

  // Compact view for quick selection
  if (compact) {
    return (
      <div className={`enhanced-model-selector-compact ${className}`}>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="flex-1 justify-between">
                <div className="flex items-center gap-2">
                  {activeModel ? getStatusIcon(activeModel) : <Bot className="h-4 w-4" />}
                  <span className="truncate">
                    {activeModel ? activeModel.name : 'בחר מודל'}
                  </span>
                  {activeModel && getTierIcon(activeModel.tier)}
                  {activeModel && getTrendingIndicator(activeModel.id)}
                </div>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-80">
              <DropdownMenuLabel className="flex items-center justify-between">
                מודלים זמינים
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={forceRefresh}
                  disabled={isLoading}
                >
                  <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
                </Button>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              {/* Quick recommendations */}
              {recommendations.slice(0, 2).map((rec) => {
                const model = models.find(m => m.id === rec.modelId);
                if (!model) return null;
                
                return (
                  <DropdownMenuItem
                    key={rec.modelId}
                    onClick={() => handleModelChange(rec.modelId)}
                    disabled={isChangingModel}
                    className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20"
                  >
                    <div className="flex items-center gap-2">
                      {rec.icon}
                      <div>
                        <div className="font-medium text-sm">{model.name}</div>
                        <div className="text-xs text-muted-foreground">{rec.reason}</div>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {rec.score.toFixed(0)}
                    </Badge>
                  </DropdownMenuItem>
                );
              })}
              
              {recommendations.length > 0 && <DropdownMenuSeparator />}
              
              {filteredModels.map((model) => (
                <DropdownMenuItem
                  key={model.id}
                  onClick={() => handleModelChange(model.id)}
                  disabled={isChangingModel}
                  className="flex items-center justify-between p-3"
                >
                  <div className="flex items-center gap-2">
                    {getStatusIcon(model)}
                    <div>
                      <div className="font-medium">{model.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {model.provider} • {model.metrics.responseTime}ms
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {getTierIcon(model.tier)}
                    {getTrendingIndicator(model.id)}
                    {activeModel?.id === model.id && (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    )}
                  </div>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          
          {/* Quick switch button */}
          {enableQuickSwitch && quickSwitchOptions.length > 0 && (
            <DropdownMenu open={quickSwitchOpen} onOpenChange={setQuickSwitchOpen}>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" title="החלפה מהירה">
                  <ArrowUpDown className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-64">
                <DropdownMenuLabel>החלפה מהירה</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {quickSwitchOptions.map((option) => (
                  <DropdownMenuItem
                    key={option.modelId}
                    onClick={() => handleModelChange(option.modelId)}
                    disabled={isChangingModel}
                    className="flex items-center justify-between p-2"
                  >
                    <div>
                      <div className="font-medium text-sm">{option.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {option.reason} • {option.responseTime}ms
                      </div>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {option.provider}
                    </Badge>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    );
  }

  // Full view with detailed metrics and controls
  return (
    <div className={`enhanced-model-selector ${className}`}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              בחירת מודל AI
              <Badge variant="secondary" className="text-xs">
                עודכן לאחרונה: {lastRefresh.toLocaleTimeString('he-IL')}
              </Badge>
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={forceRefresh}
                disabled={isLoading}
                title="רענן נתונים"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAdvanced(!showAdvanced)}
                title="הגדרות מתקדמות"
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Current Model Status */}
          {activeModel && (
            <div className="p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getStatusIcon(activeModel)}
                  <span className="font-medium">{activeModel.name}</span>
                  {getTierIcon(activeModel.tier)}
                  {getTrendingIndicator(activeModel.id)}
                  <Badge variant="secondary">{activeModel.provider}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  {isChangingModel && <Loader className="h-4 w-4 animate-spin" />}
                  {enableQuickSwitch && quickSwitchOptions.length > 0 && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" size="sm">
                          <ArrowUpDown className="h-4 w-4 mr-1" />
                          החלפה מהירה
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent className="w-64">
                        <DropdownMenuLabel>החלפה מהירה</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        {quickSwitchOptions.map((option) => (
                          <DropdownMenuItem
                            key={option.modelId}
                            onClick={() => handleModelChange(option.modelId)}
                            disabled={isChangingModel}
                            className="flex items-center justify-between p-2"
                          >
                            <div>
                              <div className="font-medium text-sm">{option.name}</div>
                              <div className="text-xs text-muted-foreground">
                                {option.reason} • {option.responseTime}ms
                              </div>
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {option.provider}
                            </Badge>
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              </div>
              
              {showMetrics && (
                <div className="grid grid-cols-4 gap-4 mt-3">
                  <div className="text-center">
                    <div className={`text-lg font-bold ${getPerformanceColor(activeModel.metrics.responseTime)}`}>
                      {activeModel.metrics.responseTime}ms
                    </div>
                    <div className="text-xs text-muted-foreground">זמן תגובה</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-blue-600">
                      {activeModel.metrics.tokensPerSecond}
                    </div>
                    <div className="text-xs text-muted-foreground">טוקנים/שנייה</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">
                      {activeModel.metrics.successRate}%
                    </div>
                    <div className="text-xs text-muted-foreground">שיעור הצלחה</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-purple-600">
                      ${activeModel.metrics.averageCost.toFixed(4)}
                    </div>
                    <div className="text-xs text-muted-foreground">עלות ממוצעת</div>
                  </div>
                </div>
              )}
              
              {showPerformanceDetails && (
                <div className="mt-3 pt-3 border-t">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center justify-between">
                      <span>זמינות:</span>
                      <div className="flex items-center gap-2">
                        <Progress value={activeModel.metrics.uptime} className="h-2 w-16" />
                        <span>{activeModel.metrics.uptime}%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>שגיאות:</span>
                      <span className="text-red-600">{activeModel.metrics.errorRate}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>תפוקה:</span>
                      <span>{activeModel.metrics.throughput} req/min</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>טוקנים ממוצע:</span>
                      <span>{activeModel.metrics.avgTokensPerRequest}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Smart Recommendations */}
          {showRecommendations && recommendations.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                המלצות חכמות
              </h4>
              <div className="grid grid-cols-1 gap-2">
                {recommendations.map((rec, index) => {
                  const model = models.find(m => m.id === rec.modelId);
                  if (!model) return null;
                  
                  return (
                    <div
                      key={rec.modelId}
                      className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg cursor-pointer hover:from-blue-100 hover:to-purple-100 dark:hover:from-blue-900/30 dark:hover:to-purple-900/30 transition-all"
                      onClick={() => handleModelChange(rec.modelId)}
                    >
                      <div className="flex items-center gap-3">
                        {rec.icon}
                        <div>
                          <div className="font-medium text-sm">{model.name}</div>
                          <div className="text-xs text-muted-foreground">{rec.reason}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {rec.score.toFixed(0)}
                        </Badge>
                        {activeModel?.id === rec.modelId && (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Advanced Controls */}
          {showAdvanced && (
            <div className="space-y-4 border-t pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  <label className="text-sm font-medium">קטגוריה:</label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="text-sm border rounded px-2 py-1 flex-1"
                  >
                    <option value="all">הכל</option>
                    <option value="chat">שיחה</option>
                    <option value="code">קוד</option>
                    <option value="creative">יצירתי</option>
                    <option value="analysis">ניתוח</option>
                  </select>
                </div>
                
                <div className="flex items-center gap-2">
                  <ArrowUpDown className="h-4 w-4" />
                  <label className="text-sm font-medium">מיון לפי:</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="text-sm border rounded px-2 py-1 flex-1"
                  >
                    <option value="usage">שימוש</option>
                    <option value="performance">ביצועים</option>
                    <option value="cost">עלות</option>
                    <option value="name">שם</option>
                    <option value="trending">מגמה</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Model List */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader className="h-6 w-6 animate-spin" />
                <span className="ml-2">טוען מודלים...</span>
              </div>
            ) : filteredModels.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                לא נמצאו מודלים זמינים
              </div>
            ) : (
              filteredModels.map((model) => (
                <div
                  key={model.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-all ${
                    activeModel?.id === model.id
                      ? 'border-primary bg-primary/5 shadow-sm'
                      : 'border-border hover:bg-muted/50 hover:shadow-sm'
                  }`}
                  onClick={() => handleModelChange(model.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(model)}
                      <span className="font-medium">{model.name}</span>
                      {getTierIcon(model.tier)}
                      {getTrendingIndicator(model.id)}
                      {activeModel?.id === model.id && (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {model.provider}
                      </Badge>
                      <Badge variant="secondary" className="text-xs">
                        {model.category}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="text-xs text-muted-foreground mb-2">
                    {model.description}
                  </div>
                  
                  {showMetrics && (
                    <div className="grid grid-cols-5 gap-2 text-xs">
                      <div>
                        <div className={`font-medium ${getPerformanceColor(model.metrics.responseTime)}`}>
                          {model.metrics.responseTime}ms
                        </div>
                        <div className="text-muted-foreground">תגובה</div>
                      </div>
                      <div>
                        <div className="font-medium">{model.metrics.tokensPerSecond}</div>
                        <div className="text-muted-foreground">טוקן/ש</div>
                      </div>
                      <div>
                        <div className="font-medium">${model.costPerToken.toFixed(6)}</div>
                        <div className="text-muted-foreground">לטוקן</div>
                      </div>
                      <div>
                        <div className="font-medium">{model.metrics.totalRequests}</div>
                        <div className="text-muted-foreground">שימושים</div>
                      </div>
                      <div>
                        <div className="font-medium text-green-600">{model.metrics.successRate}%</div>
                        <div className="text-muted-foreground">הצלחה</div>
                      </div>
                    </div>
                  )}
                  
                  {/* Uptime and performance indicators */}
                  <div className="mt-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="text-xs text-muted-foreground">זמינות:</div>
                      <Progress value={model.metrics.uptime} className="h-1 w-16" />
                      <span className="text-xs">{model.metrics.uptime}%</span>
                    </div>
                    {showPerformanceDetails && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Cpu className="h-3 w-3" />
                        <span>{model.metrics.throughput} req/min</span>
                        <Timer className="h-3 w-3" />
                        <span>שגיאות: {model.metrics.errorRate}%</span>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};