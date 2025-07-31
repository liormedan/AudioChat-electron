import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Settings,
  Sliders,
  Save,
  Upload,
  Download,
  RotateCcw,
  Eye,
  EyeOff,
  Palette,
  Brain,
  Code,
  Target,
  Sparkles,
  Play,
  Pause,
  RefreshCw,
  Copy,
  Check,
  X,
  Info,
  AlertTriangle,
  Lightbulb,
  Zap,
  Gauge,
  Activity
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
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
  DialogTrigger,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';

// Parameter interfaces
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

interface ParameterPreset {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  parameters: ModelParameters;
  category: 'built-in' | 'custom';
  createdAt?: string;
  usageCount?: number;
}

interface ParameterProfile {
  id: string;
  name: string;
  description: string;
  parameters: ModelParameters;
  createdAt: string;
  updatedAt: string;
  isDefault: boolean;
  tags: string[];
}

interface PreviewResult {
  text: string;
  parameters: ModelParameters;
  timestamp: string;
  quality: 'excellent' | 'good' | 'fair' | 'poor';
  metrics: {
    creativity: number;
    coherence: number;
    relevance: number;
  };
}

interface AdvancedSettingsPanelProps {
  onParametersChange?: (parameters: ModelParameters) => void;
  initialParameters?: ModelParameters;
  modelId?: string;
  className?: string;
  showPreview?: boolean;
  enableProfiles?: boolean;
  enableAdvancedParams?: boolean;
}

// Default parameter values
const DEFAULT_PARAMETERS: ModelParameters = {
  temperature: 0.7,
  max_tokens: 2048,
  top_p: 0.9,
  top_k: 50,
  frequency_penalty: 0.0,
  presence_penalty: 0.0,
  repetition_penalty: 1.0,
  stop_sequences: [],
  seed: undefined
};

// Built-in presets
const BUILT_IN_PRESETS: ParameterPreset[] = [
  {
    id: 'creative',
    name: 'Creative',
    description: 'מקסימום יצירתיות ורעיונות מקוריים',
    icon: <Palette className="h-4 w-4" />,
    category: 'built-in',
    parameters: {
      temperature: 0.9,
      max_tokens: 2048,
      top_p: 0.95,
      top_k: 100,
      frequency_penalty: 0.3,
      presence_penalty: 0.3,
      repetition_penalty: 1.1,
      stop_sequences: [],
    }
  },
  {
    id: 'balanced',
    name: 'Balanced',
    description: 'איזון בין יצירתיות לדיוק',
    icon: <Brain className="h-4 w-4" />,
    category: 'built-in',
    parameters: {
      temperature: 0.7,
      max_tokens: 2048,
      top_p: 0.9,
      top_k: 50,
      frequency_penalty: 0.1,
      presence_penalty: 0.1,
      repetition_penalty: 1.05,
      stop_sequences: [],
    }
  },
  {
    id: 'precise',
    name: 'Precise',
    description: 'דיוק מקסימלי ועקביות',
    icon: <Target className="h-4 w-4" />,
    category: 'built-in',
    parameters: {
      temperature: 0.3,
      max_tokens: 1024,
      top_p: 0.8,
      top_k: 20,
      frequency_penalty: 0.0,
      presence_penalty: 0.0,
      repetition_penalty: 1.0,
      stop_sequences: [],
    }
  },
  {
    id: 'code',
    name: 'Code',
    description: 'אופטימלי לכתיבת קוד ופתרון בעיות טכניות',
    icon: <Code className="h-4 w-4" />,
    category: 'built-in',
    parameters: {
      temperature: 0.2,
      max_tokens: 4096,
      top_p: 0.85,
      top_k: 30,
      frequency_penalty: 0.0,
      presence_penalty: 0.0,
      repetition_penalty: 1.0,
      stop_sequences: ['```', '---'],
    }
  }
];

export const AdvancedSettingsPanel: React.FC<AdvancedSettingsPanelProps> = ({
  onParametersChange,
  initialParameters = DEFAULT_PARAMETERS,
  modelId,
  className = '',
  showPreview = true,
  enableProfiles = true,
  enableAdvancedParams = true
}) => {
  // State management
  const [parameters, setParameters] = useState<ModelParameters>(initialParameters);
  const [presets, setPresets] = useState<ParameterPreset[]>(BUILT_IN_PRESETS);
  const [profiles, setProfiles] = useState<ParameterProfile[]>([]);
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [isPreviewEnabled, setIsPreviewEnabled] = useState(showPreview);
  const [previewResults, setPreviewResults] = useState<PreviewResult[]>([]);
  const [isGeneratingPreview, setIsGeneratingPreview] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Dialog states
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [showPresetDialog, setShowPresetDialog] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [newProfileDescription, setNewProfileDescription] = useState('');
  const [newPresetName, setNewPresetName] = useState('');
  const [newPresetDescription, setNewPresetDescription] = useState('');
  
  // Copy states
  const [copiedParam, setCopiedParam] = useState<string | null>(null);

  // Load saved profiles on mount
  useEffect(() => {
    loadProfiles();
  }, []);

  // Notify parent of parameter changes
  useEffect(() => {
    onParametersChange?.(parameters);
  }, [parameters, onParametersChange]);

  // Auto-generate preview when parameters change
  useEffect(() => {
    if (isPreviewEnabled && !isGeneratingPreview) {
      const timeoutId = setTimeout(() => {
        generatePreview();
      }, 1000); // Debounce preview generation
      
      return () => clearTimeout(timeoutId);
    }
  }, [parameters, isPreviewEnabled]);

  const loadProfiles = useCallback(() => {
    try {
      const savedProfiles = localStorage.getItem('chat-parameter-profiles');
      const savedPresets = localStorage.getItem('chat-custom-presets');
      
      if (savedProfiles) {
        setProfiles(JSON.parse(savedProfiles));
      }
      
      if (savedPresets) {
        const customPresets = JSON.parse(savedPresets);
        setPresets(prev => [...BUILT_IN_PRESETS, ...customPresets]);
      }
    } catch (error) {
      console.error('Error loading profiles:', error);
    }
  }, []);

  const saveProfile = useCallback(() => {
    if (!newProfileName.trim()) return;
    
    const newProfile: ParameterProfile = {
      id: `profile-${Date.now()}`,
      name: newProfileName.trim(),
      description: newProfileDescription.trim(),
      parameters: { ...parameters },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isDefault: false,
      tags: []
    };
    
    const updatedProfiles = [...profiles, newProfile];
    setProfiles(updatedProfiles);
    localStorage.setItem('chat-parameter-profiles', JSON.stringify(updatedProfiles));
    
    setNewProfileName('');
    setNewProfileDescription('');
    setShowSaveDialog(false);
  }, [newProfileName, newProfileDescription, parameters, profiles]);

  const loadProfile = useCallback((profile: ParameterProfile) => {
    setParameters(profile.parameters);
    setActivePreset(null);
    setShowLoadDialog(false);
  }, []);

  const applyPreset = useCallback((preset: ParameterPreset) => {
    setParameters(preset.parameters);
    setActivePreset(preset.id);
    
    // Update usage count for custom presets
    if (preset.category === 'custom') {
      const updatedPresets = presets.map(p => 
        p.id === preset.id 
          ? { ...p, usageCount: (p.usageCount || 0) + 1 }
          : p
      );
      setPresets(updatedPresets);
      
      const customPresets = updatedPresets.filter(p => p.category === 'custom');
      localStorage.setItem('chat-custom-presets', JSON.stringify(customPresets));
    }
  }, [presets]);

  const createCustomPreset = useCallback(() => {
    if (!newPresetName.trim()) return;
    
    const newPreset: ParameterPreset = {
      id: `custom-${Date.now()}`,
      name: newPresetName.trim(),
      description: newPresetDescription.trim(),
      icon: <Sparkles className="h-4 w-4" />,
      category: 'custom',
      parameters: { ...parameters },
      createdAt: new Date().toISOString(),
      usageCount: 0
    };
    
    const updatedPresets = [...presets, newPreset];
    setPresets(updatedPresets);
    
    const customPresets = updatedPresets.filter(p => p.category === 'custom');
    localStorage.setItem('chat-custom-presets', JSON.stringify(customPresets));
    
    setNewPresetName('');
    setNewPresetDescription('');
    setShowPresetDialog(false);
  }, [newPresetName, newPresetDescription, parameters, presets]);

  const resetToDefaults = useCallback(() => {
    setParameters(DEFAULT_PARAMETERS);
    setActivePreset(null);
  }, []);

  const generatePreview = useCallback(async () => {
    if (!modelId) return;
    
    setIsGeneratingPreview(true);
    try {
      const response = await fetch('/api/llm/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_id: modelId,
          parameters,
          prompt: 'כתוב פסקה קצרה על חשיבות הבינה המלאכותית בעתיד.'
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        const previewResult: PreviewResult = {
          text: result.text,
          parameters: { ...parameters },
          timestamp: new Date().toISOString(),
          quality: result.quality || 'good',
          metrics: result.metrics || {
            creativity: Math.random() * 100,
            coherence: Math.random() * 100,
            relevance: Math.random() * 100
          }
        };
        
        setPreviewResults(prev => [previewResult, ...prev.slice(0, 4)]);
      }
    } catch (error) {
      console.error('Error generating preview:', error);
    } finally {
      setIsGeneratingPreview(false);
    }
  }, [modelId, parameters]);

  const copyParameterValue = useCallback((paramName: string, value: any) => {
    navigator.clipboard.writeText(String(value));
    setCopiedParam(paramName);
    setTimeout(() => setCopiedParam(null), 2000);
  }, []);

  const exportSettings = useCallback(() => {
    const exportData = {
      parameters,
      profiles,
      customPresets: presets.filter(p => p.category === 'custom'),
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-settings-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [parameters, profiles, presets]);

  const importSettings = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importData = JSON.parse(e.target?.result as string);
        
        if (importData.parameters) {
          setParameters(importData.parameters);
        }
        
        if (importData.profiles) {
          setProfiles(importData.profiles);
          localStorage.setItem('chat-parameter-profiles', JSON.stringify(importData.profiles));
        }
        
        if (importData.customPresets) {
          const updatedPresets = [...BUILT_IN_PRESETS, ...importData.customPresets];
          setPresets(updatedPresets);
          localStorage.setItem('chat-custom-presets', JSON.stringify(importData.customPresets));
        }
      } catch (error) {
        console.error('Error importing settings:', error);
      }
    };
    
    reader.readAsText(file);
    event.target.value = '';
  }, []);

  // Parameter validation and constraints
  const getParameterConstraints = (param: keyof ModelParameters) => {
    switch (param) {
      case 'temperature':
        return { min: 0, max: 2, step: 0.01, description: 'שולט על רמת היצירתיות והאקראיות' };
      case 'max_tokens':
        return { min: 1, max: 8192, step: 1, description: 'מספר מקסימלי של טוקנים בתגובה' };
      case 'top_p':
        return { min: 0, max: 1, step: 0.01, description: 'דגימת nucleus - מגביל את מגוון המילים' };
      case 'top_k':
        return { min: 1, max: 200, step: 1, description: 'מספר המילים הסבירות ביותר לבחירה' };
      case 'frequency_penalty':
        return { min: -2, max: 2, step: 0.01, description: 'מפחית חזרה על מילים שכיחות' };
      case 'presence_penalty':
        return { min: -2, max: 2, step: 0.01, description: 'מעודד נושאים חדשים' };
      case 'repetition_penalty':
        return { min: 0.5, max: 2, step: 0.01, description: 'מפחית חזרות בכלל' };
      default:
        return { min: 0, max: 1, step: 0.01, description: '' };
    }
  };

  const getParameterColor = (param: keyof ModelParameters, value: number) => {
    const constraints = getParameterConstraints(param);
    const normalized = (value - constraints.min) / (constraints.max - constraints.min);
    
    if (normalized < 0.3) return 'text-blue-600';
    if (normalized < 0.7) return 'text-green-600';
    return 'text-orange-600';
  };

  const renderParameterSlider = (
    param: keyof ModelParameters,
    label: string,
    icon: React.ReactNode
  ) => {
    const constraints = getParameterConstraints(param);
    const value = parameters[param] as number;
    
    return (
      <div key={param} className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon}
            <Label className="text-sm font-medium">{label}</Label>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => copyParameterValue(param, value)}
            >
              {copiedParam === param ? (
                <Check className="h-3 w-3 text-green-500" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-mono ${getParameterColor(param, value)}`}>
              {typeof value === 'number' ? value.toFixed(param === 'max_tokens' || param === 'top_k' ? 0 : 2) : value}
            </span>
            <Input
              type="number"
              value={value}
              onChange={(e) => {
                const newValue = parseFloat(e.target.value);
                if (!isNaN(newValue)) {
                  setParameters(prev => ({ ...prev, [param]: newValue }));
                  setActivePreset(null);
                }
              }}
              min={constraints.min}
              max={constraints.max}
              step={constraints.step}
              className="w-20 h-8 text-xs"
            />
          </div>
        </div>
        
        <Slider
          value={[value]}
          onValueChange={([newValue]) => {
            setParameters(prev => ({ ...prev, [param]: newValue }));
            setActivePreset(null);
          }}
          min={constraints.min}
          max={constraints.max}
          step={constraints.step}
          className="w-full"
        />
        
        <div className="text-xs text-muted-foreground">
          {constraints.description}
        </div>
      </div>
    );
  };

  return (
    <div className={`advanced-settings-panel ${className}`}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              הגדרות מתקדמות
              {activePreset && (
                <Badge variant="secondary" className="text-xs">
                  {presets.find(p => p.id === activePreset)?.name}
                </Badge>
              )}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={exportSettings}
                title="ייצא הגדרות"
              >
                <Download className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => document.getElementById('import-settings')?.click()}
                title="יבא הגדרות"
              >
                <Upload className="h-4 w-4" />
              </Button>
              <input
                id="import-settings"
                type="file"
                accept=".json"
                onChange={importSettings}
                className="hidden"
              />
              <Button
                variant="ghost"
                size="sm"
                onClick={resetToDefaults}
                title="איפוס לברירת מחדל"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Presets Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium flex items-center gap-2">
                <Zap className="h-4 w-4" />
                פריסטים מוכנים
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowPresetDialog(true)}
              >
                <Sparkles className="h-4 w-4 mr-1" />
                צור פריסט
              </Button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {presets.map((preset) => (
                <Button
                  key={preset.id}
                  variant={activePreset === preset.id ? "default" : "outline"}
                  size="sm"
                  onClick={() => applyPreset(preset)}
                  className="flex flex-col items-center gap-1 h-auto p-3"
                >
                  {preset.icon}
                  <span className="text-xs">{preset.name}</span>
                  {preset.usageCount !== undefined && preset.usageCount > 0 && (
                    <Badge variant="secondary" className="text-xs">
                      {preset.usageCount}
                    </Badge>
                  )}
                </Button>
              ))}
            </div>
          </div>

          {/* Main Parameters */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium flex items-center gap-2">
              <Sliders className="h-4 w-4" />
              פרמטרים עיקריים
            </h3>
            
            <div className="space-y-4">
              {renderParameterSlider('temperature', 'Temperature', <Gauge className="h-4 w-4" />)}
              {renderParameterSlider('max_tokens', 'Max Tokens', <Activity className="h-4 w-4" />)}
              {renderParameterSlider('top_p', 'Top P', <Target className="h-4 w-4" />)}
            </div>
          </div>

          {/* Advanced Parameters */}
          {enableAdvancedParams && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium">פרמטרים מתקדמים</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                >
                  {showAdvanced ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
              
              {showAdvanced && (
                <div className="space-y-4 border-t pt-4">
                  {renderParameterSlider('top_k', 'Top K', <Brain className="h-4 w-4" />)}
                  {renderParameterSlider('frequency_penalty', 'Frequency Penalty', <RefreshCw className="h-4 w-4" />)}
                  {renderParameterSlider('presence_penalty', 'Presence Penalty', <Lightbulb className="h-4 w-4" />)}
                  {renderParameterSlider('repetition_penalty', 'Repetition Penalty', <AlertTriangle className="h-4 w-4" />)}
                  
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Stop Sequences</Label>
                    <Textarea
                      placeholder="הזן רצפי עצירה, מופרדים בפסיקים"
                      value={parameters.stop_sequences?.join(', ') || ''}
                      onChange={(e) => {
                        const sequences = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
                        setParameters(prev => ({ ...prev, stop_sequences: sequences }));
                        setActivePreset(null);
                      }}
                      className="h-20"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Seed (אופציונלי)</Label>
                    <Input
                      type="number"
                      placeholder="הזן seed לתוצאות עקביות"
                      value={parameters.seed || ''}
                      onChange={(e) => {
                        const seed = e.target.value ? parseInt(e.target.value) : undefined;
                        setParameters(prev => ({ ...prev, seed }));
                        setActivePreset(null);
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Profile Management */}
          {enableProfiles && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium">פרופילי פרמטרים</h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowLoadDialog(true)}
                    disabled={profiles.length === 0}
                  >
                    <Upload className="h-4 w-4 mr-1" />
                    טען
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowSaveDialog(true)}
                  >
                    <Save className="h-4 w-4 mr-1" />
                    שמור
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Real-time Preview */}
          {showPreview && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium flex items-center gap-2">
                  <Eye className="h-4 w-4" />
                  תצוגה מקדימה
                </h3>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={isPreviewEnabled}
                    onCheckedChange={setIsPreviewEnabled}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={generatePreview}
                    disabled={isGeneratingPreview || !modelId}
                  >
                    {isGeneratingPreview ? (
                      <Loader className="h-4 w-4 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
              
              {previewResults.length > 0 && (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {previewResults.map((result, index) => (
                    <Card key={index} className="p-3">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant={
                          result.quality === 'excellent' ? 'default' :
                          result.quality === 'good' ? 'secondary' :
                          result.quality === 'fair' ? 'outline' : 'destructive'
                        }>
                          {result.quality}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(result.timestamp).toLocaleTimeString('he-IL')}
                        </span>
                      </div>
                      
                      <p className="text-sm mb-2">{result.text}</p>
                      
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div>
                          <div className="text-muted-foreground">יצירתיות</div>
                          <Progress value={result.metrics.creativity} className="h-1" />
                        </div>
                        <div>
                          <div className="text-muted-foreground">קוהרנטיות</div>
                          <Progress value={result.metrics.coherence} className="h-1" />
                        </div>
                        <div>
                          <div className="text-muted-foreground">רלוונטיות</div>
                          <Progress value={result.metrics.relevance} className="h-1" />
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Save Profile Dialog */}
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>שמור פרופיל פרמטרים</DialogTitle>
            <DialogDescription>
              שמור את הפרמטרים הנוכחיים כפרופיל לשימוש עתידי
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="profile-name">שם הפרופיל</Label>
              <Input
                id="profile-name"
                value={newProfileName}
                onChange={(e) => setNewProfileName(e.target.value)}
                placeholder="הזן שם לפרופיל..."
              />
            </div>
            <div>
              <Label htmlFor="profile-description">תיאור (אופציונלי)</Label>
              <Textarea
                id="profile-description"
                value={newProfileDescription}
                onChange={(e) => setNewProfileDescription(e.target.value)}
                placeholder="תאר את מטרת הפרופיל..."
                className="h-20"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
              ביטול
            </Button>
            <Button onClick={saveProfile} disabled={!newProfileName.trim()}>
              שמור
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Load Profile Dialog */}
      <Dialog open={showLoadDialog} onOpenChange={setShowLoadDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>טען פרופיל פרמטרים</DialogTitle>
            <DialogDescription>
              בחר פרופיל לטעינה
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {profiles.map((profile) => (
              <Card
                key={profile.id}
                className="p-3 cursor-pointer hover:bg-accent/50"
                onClick={() => loadProfile(profile)}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium">{profile.name}</h4>
                    {profile.description && (
                      <p className="text-sm text-muted-foreground mt-1">
                        {profile.description}
                      </p>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(profile.updatedAt).toLocaleDateString('he-IL')}
                  </div>
                </div>
              </Card>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLoadDialog(false)}>
              ביטול
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Preset Dialog */}
      <Dialog open={showPresetDialog} onOpenChange={setShowPresetDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>צור פריסט מותאם</DialogTitle>
            <DialogDescription>
              צור פריסט חדש מהפרמטרים הנוכחיים
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="preset-name">שם הפריסט</Label>
              <Input
                id="preset-name"
                value={newPresetName}
                onChange={(e) => setNewPresetName(e.target.value)}
                placeholder="הזן שם לפריסט..."
              />
            </div>
            <div>
              <Label htmlFor="preset-description">תיאור</Label>
              <Input
                id="preset-description"
                value={newPresetDescription}
                onChange={(e) => setNewPresetDescription(e.target.value)}
                placeholder="תאר את מטרת הפריסט..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPresetDialog(false)}>
              ביטול
            </Button>
            <Button onClick={createCustomPreset} disabled={!newPresetName.trim()}>
              צור
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};