import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
import { 
  Palette, 
  Zap, 
  Eye, 
  MousePointer, 
  Keyboard,
  Monitor,
  Volume2,
  Settings,
  CheckCircle,
  Star,
  Clock,
  Gauge
} from 'lucide-react';

interface UXImprovement {
  id: string;
  name: string;
  description: string;
  category: 'visual' | 'interaction' | 'performance' | 'accessibility' | 'feedback';
  impact: 'low' | 'medium' | 'high';
  implemented: boolean;
  priority: number;
}

interface UXMetric {
  name: string;
  value: number;
  unit: string;
  target: number;
  status: 'good' | 'warning' | 'poor';
  icon: React.ReactNode;
}

const uxImprovements: UXImprovement[] = [
  // Visual Improvements
  {
    id: 'dark-mode-toggle',
    name: 'Dark Mode Toggle',
    description: 'Easy toggle between light and dark themes',
    category: 'visual',
    impact: 'medium',
    implemented: true,
    priority: 8
  },
  {
    id: 'waveform-visualization',
    name: 'Enhanced Waveform',
    description: 'Better waveform visualization with zoom and selection',
    category: 'visual',
    impact: 'high',
    implemented: true,
    priority: 9
  },
  {
    id: 'progress-indicators',
    name: 'Progress Indicators',
    description: 'Clear progress feedback for all operations',
    category: 'visual',
    impact: 'high',
    implemented: true,
    priority: 9
  },
  {
    id: 'status-animations',
    name: 'Status Animations',
    description: 'Smooth animations for status changes',
    category: 'visual',
    impact: 'medium',
    implemented: false,
    priority: 6
  },

  // Interaction Improvements
  {
    id: 'drag-drop-upload',
    name: 'Drag & Drop Upload',
    description: 'Drag and drop files anywhere to upload',
    category: 'interaction',
    impact: 'high',
    implemented: true,
    priority: 9
  },
  {
    id: 'keyboard-shortcuts',
    name: 'Keyboard Shortcuts',
    description: 'Comprehensive keyboard shortcuts for power users',
    category: 'interaction',
    impact: 'medium',
    implemented: false,
    priority: 7
  },
  {
    id: 'quick-commands',
    name: 'Quick Command Palette',
    description: 'Command palette for fast access to functions',
    category: 'interaction',
    impact: 'high',
    implemented: true,
    priority: 8
  },
  {
    id: 'context-menus',
    name: 'Context Menus',
    description: 'Right-click context menus for common actions',
    category: 'interaction',
    impact: 'medium',
    implemented: false,
    priority: 6
  },

  // Performance Improvements
  {
    id: 'lazy-loading',
    name: 'Lazy Loading',
    description: 'Load components and data only when needed',
    category: 'performance',
    impact: 'medium',
    implemented: false,
    priority: 7
  },
  {
    id: 'audio-streaming',
    name: 'Audio Streaming',
    description: 'Stream large audio files instead of full download',
    category: 'performance',
    impact: 'high',
    implemented: false,
    priority: 8
  },
  {
    id: 'caching-strategy',
    name: 'Smart Caching',
    description: 'Cache processed audio and metadata',
    category: 'performance',
    impact: 'medium',
    implemented: false,
    priority: 7
  },

  // Accessibility Improvements
  {
    id: 'screen-reader',
    name: 'Screen Reader Support',
    description: 'Full screen reader compatibility',
    category: 'accessibility',
    impact: 'high',
    implemented: false,
    priority: 8
  },
  {
    id: 'high-contrast',
    name: 'High Contrast Mode',
    description: 'High contrast theme for better visibility',
    category: 'accessibility',
    impact: 'medium',
    implemented: false,
    priority: 6
  },
  {
    id: 'font-scaling',
    name: 'Font Size Scaling',
    description: 'Adjustable font sizes for better readability',
    category: 'accessibility',
    impact: 'medium',
    implemented: false,
    priority: 6
  },

  // Feedback Improvements
  {
    id: 'toast-notifications',
    name: 'Toast Notifications',
    description: 'Non-intrusive notifications for actions',
    category: 'feedback',
    impact: 'medium',
    implemented: false,
    priority: 7
  },
  {
    id: 'sound-feedback',
    name: 'Audio Feedback',
    description: 'Optional sound feedback for actions',
    category: 'feedback',
    impact: 'low',
    implemented: false,
    priority: 4
  },
  {
    id: 'haptic-feedback',
    name: 'Haptic Feedback',
    description: 'Vibration feedback on supported devices',
    category: 'feedback',
    impact: 'low',
    implemented: false,
    priority: 3
  }
];

const uxMetrics: UXMetric[] = [
  {
    name: 'Load Time',
    value: 2.3,
    unit: 's',
    target: 2.0,
    status: 'warning',
    icon: <Clock className="h-4 w-4" />
  },
  {
    name: 'Response Time',
    value: 150,
    unit: 'ms',
    target: 200,
    status: 'good',
    icon: <Zap className="h-4 w-4" />
  },
  {
    name: 'User Satisfaction',
    value: 4.2,
    unit: '/5',
    target: 4.0,
    status: 'good',
    icon: <Star className="h-4 w-4" />
  },
  {
    name: 'Task Completion',
    value: 87,
    unit: '%',
    target: 90,
    status: 'warning',
    icon: <CheckCircle className="h-4 w-4" />
  },
  {
    name: 'Error Rate',
    value: 3.2,
    unit: '%',
    target: 2.0,
    status: 'poor',
    icon: <Gauge className="h-4 w-4" />
  }
];

export const UXImprovements: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showImplemented, setShowImplemented] = useState(true);
  const [showNotImplemented, setShowNotImplemented] = useState(true);
  const [sortBy, setSortBy] = useState<'priority' | 'impact' | 'name'>('priority');
  const [uxSettings, setUXSettings] = useState({
    animationSpeed: 1,
    reducedMotion: false,
    highContrast: false,
    fontSize: 14,
    soundEnabled: true,
    autoSave: true
  });

  const categories = [
    { id: 'all', name: 'All Categories', icon: <Settings className="h-4 w-4" /> },
    { id: 'visual', name: 'Visual', icon: <Eye className="h-4 w-4" /> },
    { id: 'interaction', name: 'Interaction', icon: <MousePointer className="h-4 w-4" /> },
    { id: 'performance', name: 'Performance', icon: <Zap className="h-4 w-4" /> },
    { id: 'accessibility', name: 'Accessibility', icon: <Monitor className="h-4 w-4" /> },
    { id: 'feedback', name: 'Feedback', icon: <Volume2 className="h-4 w-4" /> }
  ];

  const filteredImprovements = uxImprovements
    .filter(improvement => {
      const categoryMatch = selectedCategory === 'all' || improvement.category === selectedCategory;
      const implementedMatch = (showImplemented && improvement.implemented) || 
                              (showNotImplemented && !improvement.implemented);
      return categoryMatch && implementedMatch;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          return b.priority - a.priority;
        case 'impact':
          const impactOrder = { high: 3, medium: 2, low: 1 };
          return impactOrder[b.impact] - impactOrder[a.impact];
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'visual': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'interaction': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'performance': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'accessibility': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'feedback': return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getMetricStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'text-green-600 dark:text-green-400';
      case 'warning': return 'text-yellow-600 dark:text-yellow-400';
      case 'poor': return 'text-red-600 dark:text-red-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const handleSettingChange = (key: keyof typeof uxSettings, value: any) => {
    setUXSettings(prev => ({ ...prev, [key]: value }));
    // Apply setting immediately
    applyUXSetting(key, value);
  };

  const applyUXSetting = (key: string, value: any) => {
    switch (key) {
      case 'reducedMotion':
        document.documentElement.style.setProperty(
          '--animation-duration', 
          value ? '0s' : '0.3s'
        );
        break;
      case 'highContrast':
        document.documentElement.classList.toggle('high-contrast', value);
        break;
      case 'fontSize':
        document.documentElement.style.setProperty('--base-font-size', `${value}px`);
        break;
      default:
        break;
    }
  };

  return (
    <div className="space-y-6">
      {/* UX Metrics Dashboard */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Gauge className="h-5 w-5" />
            <span>UX Metrics Dashboard</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {uxMetrics.map((metric) => (
              <div key={metric.name} className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <div className={getMetricStatusColor(metric.status)}>
                    {metric.icon}
                  </div>
                </div>
                <div className={`text-2xl font-bold ${getMetricStatusColor(metric.status)}`}>
                  {metric.value}{metric.unit}
                </div>
                <div className="text-sm text-muted-foreground">{metric.name}</div>
                <div className="text-xs text-muted-foreground">
                  Target: {metric.target}{metric.unit}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* UX Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>UX Settings</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Animation Speed */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Animation Speed</label>
              <Slider
                value={[uxSettings.animationSpeed]}
                onValueChange={(value) => handleSettingChange('animationSpeed', value[0])}
                max={2}
                min={0.5}
                step={0.1}
                className="w-full"
              />
              <div className="text-xs text-muted-foreground">
                Current: {uxSettings.animationSpeed}x
              </div>
            </div>

            {/* Font Size */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Font Size</label>
              <Slider
                value={[uxSettings.fontSize]}
                onValueChange={(value) => handleSettingChange('fontSize', value[0])}
                max={20}
                min={12}
                step={1}
                className="w-full"
              />
              <div className="text-xs text-muted-foreground">
                Current: {uxSettings.fontSize}px
              </div>
            </div>

            {/* Toggle Settings */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Reduced Motion</label>
                <Switch
                  checked={uxSettings.reducedMotion}
                  onCheckedChange={(checked) => handleSettingChange('reducedMotion', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">High Contrast</label>
                <Switch
                  checked={uxSettings.highContrast}
                  onCheckedChange={(checked) => handleSettingChange('highContrast', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Sound Feedback</label>
                <Switch
                  checked={uxSettings.soundEnabled}
                  onCheckedChange={(checked) => handleSettingChange('soundEnabled', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Auto Save</label>
                <Switch
                  checked={uxSettings.autoSave}
                  onCheckedChange={(checked) => handleSettingChange('autoSave', checked)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Improvement Filters */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Palette className="h-5 w-5" />
              <span>UX Improvements</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Category Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Category:</label>
              <div className="flex flex-wrap gap-2">
                {categories.map((category) => (
                  <Button
                    key={category.id}
                    variant={selectedCategory === category.id ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedCategory(category.id)}
                    className="flex items-center space-x-1"
                  >
                    {category.icon}
                    <span>{category.name}</span>
                  </Button>
                ))}
              </div>
            </div>

            {/* Filters */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Switch
                  checked={showImplemented}
                  onCheckedChange={setShowImplemented}
                />
                <label className="text-sm">Show Implemented</label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Switch
                  checked={showNotImplemented}
                  onCheckedChange={setShowNotImplemented}
                />
                <label className="text-sm">Show Not Implemented</label>
              </div>

              <div className="flex items-center space-x-2">
                <label className="text-sm">Sort by:</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="text-sm border rounded px-2 py-1"
                >
                  <option value="priority">Priority</option>
                  <option value="impact">Impact</option>
                  <option value="name">Name</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Improvements List */}
      <Card>
        <CardHeader>
          <CardTitle>
            Improvement Roadmap ({filteredImprovements.length} items)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredImprovements.map((improvement) => (
              <div
                key={improvement.id}
                className={`p-4 rounded-lg border ${
                  improvement.implemented
                    ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                    : 'border-border bg-card'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-sm">{improvement.name}</h4>
                  {improvement.implemented && (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  )}
                </div>
                
                <p className="text-xs text-muted-foreground mb-3">
                  {improvement.description}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge className={`text-xs ${getCategoryColor(improvement.category)}`}>
                      {improvement.category}
                    </Badge>
                    <Badge className={`text-xs ${getImpactColor(improvement.impact)}`}>
                      {improvement.impact}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <Star className="h-3 w-3 text-yellow-500" />
                    <span className="text-xs">{improvement.priority}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};