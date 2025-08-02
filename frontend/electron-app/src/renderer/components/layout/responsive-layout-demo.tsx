import React, { useState } from 'react';
import { MainLayoutGrid, ContentArea, Column, CompactComponent } from './main-layout-grid';
import { Header } from './header';
import Sidebar from './sidebar';
import { useResponsiveLayout } from '../../hooks/use-responsive-layout';
import { useResponsiveLayoutTransitions } from '../../hooks/use-responsive-layout-transitions';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { 
  Monitor, 
  Smartphone, 
  Tablet, 
  Laptop, 
  Play, 
  Pause,
  RotateCcw,
  Settings,
  Activity
} from 'lucide-react';
import { BreakpointName } from './types';
import './main-layout-grid.css';
import './responsive-transitions.css';

export const ResponsiveLayoutDemo: React.FC = () => {
  const [simulatedWidth, setSimulatedWidth] = useState(1920);
  const [enableAnimations, setEnableAnimations] = useState(true);
  const [showTransitionInfo, setShowTransitionInfo] = useState(true);
  const [autoDemo, setAutoDemo] = useState(false);

  const {
    screenSize,
    currentBreakpoint,
    previousBreakpoint,
    layoutConfiguration,
    layoutMetrics,
    isTransitioning,
    transitionHistory
  } = useResponsiveLayout({
    adaptiveComponentSizing: true,
    enableTransitionTracking: true,
    onBreakpointChange: (transition) => {
      console.log('Breakpoint transition:', transition);
    }
  });

  const {
    getTransitionStyles,
    getLayoutClasses,
    activeTransitions,
    transitionConfig
  } = useResponsiveLayoutTransitions({
    transitionConfig: {
      enableAnimations,
      duration: 300,
      staggerDelay: 50
    },
    onTransitionStart: (transition) => {
      console.log('Transition started:', transition);
    },
    onTransitionEnd: (transition) => {
      console.log('Transition ended:', transition);
    }
  });

  const breakpointIcons = {
    mobile: <Smartphone className="h-4 w-4" />,
    tablet: <Tablet className="h-4 w-4" />,
    laptop: <Laptop className="h-4 w-4" />,
    desktop: <Monitor className="h-4 w-4" />
  };

  const breakpointWidths = {
    mobile: 480,
    tablet: 768,
    laptop: 1366,
    desktop: 1920
  };

  const simulateBreakpoint = (breakpoint: BreakpointName) => {
    setSimulatedWidth(breakpointWidths[breakpoint]);
    // Trigger a resize event simulation
    window.dispatchEvent(new Event('resize'));
  };

  const startAutoDemo = () => {
    setAutoDemo(true);
    const breakpoints: BreakpointName[] = ['desktop', 'laptop', 'tablet', 'mobile', 'tablet', 'laptop'];
    let index = 0;
    
    const interval = setInterval(() => {
      if (index >= breakpoints.length) {
        setAutoDemo(false);
        clearInterval(interval);
        return;
      }
      
      simulateBreakpoint(breakpoints[index]);
      index++;
    }, 2000);
  };

  const resetDemo = () => {
    setAutoDemo(false);
    setSimulatedWidth(1920);
    simulateBreakpoint('desktop');
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Demo Controls */}
      <div className="bg-card border-b p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Responsive Layout Demo</h1>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="flex items-center space-x-1">
              {breakpointIcons[currentBreakpoint]}
              <span>{currentBreakpoint}</span>
            </Badge>
            {isTransitioning && (
              <Badge variant="secondary" className="flex items-center space-x-1">
                <Activity className="h-3 w-3 animate-pulse" />
                <span>Transitioning</span>
              </Badge>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Breakpoint Controls */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Breakpoint Simulation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(breakpointWidths).map(([bp, width]) => (
                  <Button
                    key={bp}
                    variant={currentBreakpoint === bp ? "default" : "outline"}
                    size="sm"
                    onClick={() => simulateBreakpoint(bp as BreakpointName)}
                    className="flex items-center space-x-1"
                    disabled={autoDemo}
                  >
                    {breakpointIcons[bp as BreakpointName]}
                    <span className="capitalize">{bp}</span>
                  </Button>
                ))}
              </div>
              
              <div className="space-y-2">
                <Label className="text-xs">Width: {simulatedWidth}px</Label>
                <Slider
                  value={[simulatedWidth]}
                  onValueChange={([value]) => setSimulatedWidth(value)}
                  min={320}
                  max={2560}
                  step={10}
                  disabled={autoDemo}
                />
              </div>
            </CardContent>
          </Card>

          {/* Animation Controls */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Animation Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-xs">Enable Animations</Label>
                <Switch
                  checked={enableAnimations}
                  onCheckedChange={setEnableAnimations}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label className="text-xs">Show Transition Info</Label>
                <Switch
                  checked={showTransitionInfo}
                  onCheckedChange={setShowTransitionInfo}
                />
              </div>

              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={startAutoDemo}
                  disabled={autoDemo}
                  className="flex items-center space-x-1"
                >
                  <Play className="h-3 w-3" />
                  <span>Auto Demo</span>
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetDemo}
                  className="flex items-center space-x-1"
                >
                  <RotateCcw className="h-3 w-3" />
                  <span>Reset</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Layout Metrics */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Layout Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span>Screen:</span>
                <span>{screenSize.width}x{screenSize.height}</span>
              </div>
              <div className="flex justify-between">
                <span>Columns:</span>
                <span>{layoutMetrics.optimalColumnCount}</span>
              </div>
              <div className="flex justify-between">
                <span>Fits Screen:</span>
                <Badge variant={layoutMetrics.fitsOnScreen ? "default" : "destructive"} className="text-xs">
                  {layoutMetrics.fitsOnScreen ? "Yes" : "No"}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span>Compact:</span>
                <Badge variant={layoutMetrics.shouldUseCompactLayout ? "secondary" : "outline"} className="text-xs">
                  {layoutMetrics.shouldUseCompactLayout ? "Yes" : "No"}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Layout Demo */}
      <div className="flex-1 overflow-hidden">
        <MainLayoutGrid className={getLayoutClasses()}>
          {/* Header */}
          <div style={{ gridColumn: '1 / -1', gridRow: '1' }}>
            <Header />
          </div>

          {/* Sidebar - Hidden on mobile */}
          {currentBreakpoint !== 'mobile' && (
            <div style={{ gridColumn: '1', gridRow: '2', ...getTransitionStyles('sidebar') }}>
              <Sidebar />
            </div>
          )}

          {/* Content Area */}
          <ContentArea>
            {/* Column 1 - Upload & Files */}
            <Column column={1}>
              <CompactComponent 
                height={layoutConfiguration.components.fileUploader.height}
                scrollable={false}
                className="file-uploader"
                style={getTransitionStyles('fileUploader')}
              >
                <Card className="h-full border-0 shadow-none">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center justify-between">
                      File Upload
                      <Badge variant="secondary" className="text-xs">
                        {layoutConfiguration.components.fileUploader.height}px
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div style={{ 
                      height: `${layoutConfiguration.components.fileUploader.height - 80}px`, 
                      border: '2px dashed var(--border)', 
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--muted-foreground)',
                      fontSize: '12px'
                    }}>
                      📁 Drag & Drop Area
                    </div>
                  </CardContent>
                </Card>
              </CompactComponent>

              <CompactComponent 
                height={layoutConfiguration.components.fileManager.height}
                scrollable={true}
                className="file-manager"
                style={getTransitionStyles('fileManager')}
              >
                <Card className="h-full border-0 shadow-none">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center justify-between">
                      File Manager
                      <Badge variant="secondary" className="text-xs">
                        {layoutConfiguration.components.fileManager.height}px
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div style={{ fontSize: '11px', color: 'var(--muted-foreground)' }}>
                      {Array.from({ length: 8 }, (_, i) => (
                        <div key={i} style={{ 
                          padding: '4px 0', 
                          borderBottom: '1px solid var(--border)',
                          display: 'flex',
                          justifyContent: 'space-between'
                        }}>
                          <span>🎵 Audio File {i + 1}.mp3</span>
                          <span>{Math.floor(Math.random() * 300) + 60}s</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </CompactComponent>
            </Column>

            {/* Column 2 - Player & Info */}
            {(currentBreakpoint === 'desktop' || currentBreakpoint === 'laptop' || 
              (currentBreakpoint === 'tablet' && layoutMetrics.optimalColumnCount >= 2)) && (
              <Column column={2}>
                <CompactComponent 
                  height={layoutConfiguration.components.waveformPlayer.height}
                  scrollable={false}
                  className="waveform-player"
                  style={getTransitionStyles('waveformPlayer')}
                >
                  <Card className="h-full border-0 shadow-none">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center justify-between">
                        Waveform Player
                        <Badge variant="secondary" className="text-xs">
                          {layoutConfiguration.components.waveformPlayer.height}px
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div style={{ 
                        height: `${Math.max(100, layoutConfiguration.components.waveformPlayer.height - 120)}px`, 
                        backgroundColor: 'var(--muted)', 
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--muted-foreground)',
                        fontSize: '12px',
                        marginBottom: '8px'
                      }}>
                        🎵 Waveform Visualization
                      </div>
                      <div style={{ fontSize: '10px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
                        <div>Duration: 3:45</div>
                        <div>Sample Rate: 44.1kHz</div>
                        <div>Bitrate: 320kbps</div>
                        <div>Format: MP3</div>
                      </div>
                    </CardContent>
                  </Card>
                </CompactComponent>
              </Column>
            )}

            {/* Column 3 - Chat & Tools */}
            {currentBreakpoint === 'desktop' || 
             (currentBreakpoint === 'laptop' && layoutMetrics.optimalColumnCount >= 3) ? (
              <Column column={3}>
                <CompactComponent 
                  height={layoutConfiguration.components.chatInterface.height}
                  scrollable={true}
                  className="chat-interface"
                  style={getTransitionStyles('chatInterface')}
                >
                  <Card className="h-full border-0 shadow-none">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center justify-between">
                        AI Chat
                        <Badge variant="secondary" className="text-xs">
                          {layoutConfiguration.components.chatInterface.height}px
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col h-full">
                      <div style={{ flex: 1, fontSize: '11px', color: 'var(--muted-foreground)' }}>
                        <div style={{ marginBottom: '6px', padding: '6px', backgroundColor: 'var(--muted)', borderRadius: '4px' }}>
                          🤖 AI: Hello! Ready to edit audio?
                        </div>
                        <div style={{ marginBottom: '6px', padding: '6px', backgroundColor: 'var(--primary)', color: 'var(--primary-foreground)', borderRadius: '4px', textAlign: 'right' }}>
                          👤 User: Yes, let's start!
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </CompactComponent>
              </Column>
            ) : (
              // Full width chat for smaller screens
              <div style={{ gridColumn: '1 / -1' }}>
                <CompactComponent 
                  height={Math.min(250, layoutConfiguration.components.chatInterface.height)}
                  scrollable={true}
                  className="chat-interface"
                  style={getTransitionStyles('chatInterface')}
                >
                  <Card className="border-0 shadow-none">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">
                        AI Chat ({currentBreakpoint} layout)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div style={{ fontSize: '11px', color: 'var(--muted-foreground)' }}>
                        Chat optimized for {currentBreakpoint} view
                      </div>
                    </CardContent>
                  </Card>
                </CompactComponent>
              </div>
            )}
          </ContentArea>

          {/* Transition Info Overlay */}
          {showTransitionInfo && (
            <div style={{ 
              position: 'fixed', 
              top: '80px', 
              right: '10px', 
              padding: '12px', 
              backgroundColor: 'var(--card)', 
              border: '1px solid var(--border)', 
              borderRadius: '6px',
              fontSize: '10px',
              zIndex: 1000,
              minWidth: '250px',
              maxHeight: '300px',
              overflow: 'auto'
            }}>
              <div className="font-semibold mb-2">Transition Debug Info</div>
              <div className="space-y-1">
                <div>Current: <Badge variant="outline" className="text-xs">{currentBreakpoint}</Badge></div>
                <div>Previous: <Badge variant="outline" className="text-xs">{previousBreakpoint}</Badge></div>
                <div>Transitioning: <Badge variant={isTransitioning ? "default" : "secondary"} className="text-xs">
                  {isTransitioning ? "Yes" : "No"}
                </Badge></div>
                <div>Active Transitions: {activeTransitions.length}</div>
                <div>Animation Duration: {transitionConfig.duration}ms</div>
                
                {transitionHistory.length > 0 && (
                  <div className="mt-2">
                    <div className="font-semibold text-xs mb-1">Recent Transitions:</div>
                    {transitionHistory.slice(-3).map((transition, i) => (
                      <div key={i} className="text-xs text-muted-foreground">
                        {transition.from} → {transition.to} ({transition.direction})
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </MainLayoutGrid>
      </div>
    </div>
  );
};