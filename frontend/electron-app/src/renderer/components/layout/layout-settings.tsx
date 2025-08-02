import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';
import { Slider } from '../ui/slider';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { 
  Settings, 
  Monitor, 
  Smartphone, 
  Tablet, 
  Laptop, 
  Eye, 
  EyeOff, 
  RotateCcw,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { useLayoutConfigurationHook } from '../../hooks/use-layout-configuration';

export const LayoutSettings: React.FC = () => {
  const {
    layoutPreferences,
    currentBreakpoint,
    isComponentVisible,
    getComponentHeight,
    toggleComponentVisibility,
    updateComponentHeight,
    toggleSidebar,
    toggleCompactMode,
    resetLayout,
    isMobile,
    isTablet,
    isLaptop,
    isDesktop,
    canFitAllComponents,
    getOptimalLayout,
    getColumnCount
  } = useLayoutConfigurationHook();

  const getBreakpointIcon = () => {
    switch (currentBreakpoint) {
      case 'mobile': return <Smartphone className="h-4 w-4" />;
      case 'tablet': return <Tablet className="h-4 w-4" />;
      case 'laptop': return <Laptop className="h-4 w-4" />;
      case 'desktop': return <Monitor className="h-4 w-4" />;
    }
  };

  const componentLabels = {
    fileUploader: 'File Uploader',
    waveformPlayer: 'Waveform Player',
    chatInterface: 'Chat Interface',
    fileManager: 'File Manager',
    sidebar: 'Sidebar'
  };

  return (
    <div className="space-y-6">
      {/* Current Layout Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Layout Configuration</span>
          </CardTitle>
          <CardDescription>
            Customize your workspace layout and component preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getBreakpointIcon()}
              <span className="font-medium">Current Breakpoint:</span>
              <Badge variant="outline">{currentBreakpoint}</Badge>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">Layout:</span>
              <Badge>{getOptimalLayout()}</Badge>
              <Badge variant="secondary">{getColumnCount()} columns</Badge>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm">All components fit on screen:</span>
            <Badge variant={canFitAllComponents() ? "default" : "destructive"}>
              {canFitAllComponents() ? "Yes" : "No"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Component Visibility */}
      <Card>
        <CardHeader>
          <CardTitle>Component Visibility</CardTitle>
          <CardDescription>
            Show or hide components in your workspace
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(componentLabels).map(([key, label]) => (
            <div key={key} className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {isComponentVisible(key) ? (
                  <Eye className="h-4 w-4 text-green-600" />
                ) : (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                )}
                <Label htmlFor={`visibility-${key}`}>{label}</Label>
              </div>
              <Switch
                id={`visibility-${key}`}
                checked={isComponentVisible(key)}
                onCheckedChange={() => toggleComponentVisibility(key)}
              />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Component Heights */}
      <Card>
        <CardHeader>
          <CardTitle>Component Heights</CardTitle>
          <CardDescription>
            Adjust the height of each component (100px - 800px)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {Object.entries(componentLabels)
            .filter(([key]) => key !== 'sidebar' && isComponentVisible(key))
            .map(([key, label]) => (
              <div key={key} className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>{label}</Label>
                  <Badge variant="outline">{getComponentHeight(key)}px</Badge>
                </div>
                <Slider
                  value={[getComponentHeight(key)]}
                  onValueChange={([value]) => updateComponentHeight(key, value)}
                  min={100}
                  max={800}
                  step={25}
                  className="w-full"
                />
              </div>
            ))}
        </CardContent>
      </Card>

      {/* Layout Options */}
      <Card>
        <CardHeader>
          <CardTitle>Layout Options</CardTitle>
          <CardDescription>
            Configure general layout behavior
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label>Sidebar Collapsed</Label>
              <p className="text-sm text-muted-foreground">
                Collapse the sidebar to save space
              </p>
            </div>
            <Switch
              checked={layoutPreferences.sidebarCollapsed}
              onCheckedChange={toggleSidebar}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label>Compact Mode</Label>
              <p className="text-sm text-muted-foreground">
                Reduce component sizes for more content
              </p>
            </div>
            <Switch
              checked={layoutPreferences.compactMode}
              onCheckedChange={toggleCompactMode}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label>Auto-hide Components</Label>
              <p className="text-sm text-muted-foreground">
                Automatically hide components on smaller screens
              </p>
            </div>
            <Switch
              checked={layoutPreferences.autoHideComponents}
              onCheckedChange={() => {
                // This would need to be implemented in the context
                console.log('Auto-hide toggle not yet implemented');
              }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Responsive Behavior */}
      <Card>
        <CardHeader>
          <CardTitle>Responsive Behavior</CardTitle>
          <CardDescription>
            Configure how the layout adapts to different screen sizes
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Mobile Layout</Label>
              <Badge variant="outline">{layoutPreferences.mobileLayoutMode}</Badge>
            </div>
            <div className="space-y-2">
              <Label>Tablet Layout</Label>
              <Badge variant="outline">{layoutPreferences.tabletLayoutMode}</Badge>
            </div>
          </div>
          
          <div className="text-sm text-muted-foreground">
            <p>Current screen behavior:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              {isMobile && <li>Mobile: Single column, essential components only</li>}
              {isTablet && <li>Tablet: Two columns or single column based on preference</li>}
              {isLaptop && <li>Laptop: Three columns, may collapse to two if needed</li>}
              {isDesktop && <li>Desktop: Full three-column layout</li>}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
          <CardDescription>
            Reset or manage your layout configuration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={resetLayout}
              className="flex items-center space-x-2"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Reset to Defaults</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={toggleCompactMode}
              className="flex items-center space-x-2"
            >
              {layoutPreferences.compactMode ? (
                <Maximize2 className="h-4 w-4" />
              ) : (
                <Minimize2 className="h-4 w-4" />
              )}
              <span>
                {layoutPreferences.compactMode ? 'Exit Compact' : 'Enter Compact'}
              </span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};