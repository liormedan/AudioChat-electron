import React from 'react';
import { LayoutConfigurationProvider } from '../../contexts/layout-configuration-context';
import { MainLayoutGrid, ContentArea, Column, CompactComponent } from './main-layout-grid';
import { LayoutSettings } from './layout-settings';
import { Header } from './header';
import Sidebar from './sidebar';
import { useLayoutConfigurationHook } from '../../hooks/use-layout-configuration';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import './main-layout-grid.css';

const LayoutContent: React.FC = () => {
  const {
    layoutConfiguration,
    currentBreakpoint,
    shouldShowComponent,
    getComponentHeight,
    getOptimalLayout,
    getColumnCount,
    isMobile,
    isTablet
  } = useLayoutConfigurationHook();

  return (
    <MainLayoutGrid>
      {/* Header */}
      <div style={{ gridColumn: '1 / -1', gridRow: '1' }}>
        <Header />
      </div>

      {/* Sidebar - Hidden on mobile */}
      {shouldShowComponent('sidebar') && !isMobile && (
        <div style={{ gridColumn: '1', gridRow: '2' }}>
          <Sidebar />
        </div>
      )}

      {/* Content Area */}
      <ContentArea>
        {/* Column 1 - Upload & Files */}
        {shouldShowComponent('fileUploader') && (
          <Column column={1}>
            <CompactComponent 
              height={getComponentHeight('fileUploader')}
              scrollable={false}
            >
              <Card className="h-full border-0 shadow-none">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center justify-between">
                    File Upload
                    <Badge variant="secondary" className="text-xs">
                      {getComponentHeight('fileUploader')}px
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div style={{ 
                    height: `${getComponentHeight('fileUploader') - 80}px`, 
                    border: '2px dashed var(--border)', 
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--muted-foreground)',
                    fontSize: '12px'
                  }}>
                    Drag & Drop Area
                  </div>
                </CardContent>
              </Card>
            </CompactComponent>
          </Column>
        )}

        {shouldShowComponent('fileManager') && (
          <Column column={1}>
            <CompactComponent 
              height={getComponentHeight('fileManager')}
              scrollable={true}
            >
              <Card className="h-full border-0 shadow-none">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center justify-between">
                    File Manager
                    <Badge variant="secondary" className="text-xs">
                      {getComponentHeight('fileManager')}px
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                    {Array.from({ length: 15 }, (_, i) => (
                      <div key={i} style={{ 
                        padding: '6px 0', 
                        borderBottom: '1px solid var(--border)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}>
                        <span>Audio File {i + 1}.mp3</span>
                        <Badge variant="outline" className="text-xs">
                          {Math.floor(Math.random() * 300) + 60}s
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </CompactComponent>
          </Column>
        )}

        {/* Column 2 - Player & Info */}
        {shouldShowComponent('waveformPlayer') && getColumnCount() >= 2 && (
          <Column column={2}>
            <CompactComponent 
              height={getComponentHeight('waveformPlayer')}
              scrollable={false}
            >
              <Card className="h-full border-0 shadow-none">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center justify-between">
                    Waveform Player
                    <Badge variant="secondary" className="text-xs">
                      {getComponentHeight('waveformPlayer')}px
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div style={{ 
                    height: `${Math.max(120, getComponentHeight('waveformPlayer') - 120)}px`, 
                    backgroundColor: 'var(--muted)', 
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--muted-foreground)',
                    fontSize: '12px',
                    marginBottom: '12px'
                  }}>
                    🎵 Waveform Visualization
                  </div>
                  <div style={{ fontSize: '11px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
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
        {shouldShowComponent('chatInterface') && getColumnCount() >= 3 && (
          <Column column={3}>
            <CompactComponent 
              height={getComponentHeight('chatInterface')}
              scrollable={true}
            >
              <Card className="h-full border-0 shadow-none">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center justify-between">
                    AI Chat
                    <Badge variant="secondary" className="text-xs">
                      {getComponentHeight('chatInterface')}px
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col h-full">
                  <div style={{ flex: 1, fontSize: '12px', color: 'var(--muted-foreground)' }}>
                    <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: 'var(--muted)', borderRadius: '4px' }}>
                      🤖 AI: Hello! Upload an audio file to get started.
                    </div>
                    <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: 'var(--primary)', color: 'var(--primary-foreground)', borderRadius: '4px', textAlign: 'right' }}>
                      👤 User: Can you help me edit this audio?
                    </div>
                    <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: 'var(--muted)', borderRadius: '4px' }}>
                      🤖 AI: Of course! I can help you with various audio editing tasks like trimming, volume adjustment, noise reduction, and more.
                    </div>
                    <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: 'var(--primary)', color: 'var(--primary-foreground)', borderRadius: '4px', textAlign: 'right' }}>
                      👤 User: Great! Let me upload a file first.
                    </div>
                  </div>
                  <div style={{ 
                    marginTop: '8px', 
                    padding: '8px', 
                    border: '1px solid var(--border)', 
                    borderRadius: '4px',
                    fontSize: '12px',
                    backgroundColor: 'var(--background)'
                  }}>
                    Type your message...
                  </div>
                </CardContent>
              </Card>
            </CompactComponent>
          </Column>
        )}

        {/* Mobile/Tablet: Components in full width rows */}
        {(isTablet || isMobile) && shouldShowComponent('chatInterface') && getColumnCount() < 3 && (
          <div style={{ gridColumn: '1 / -1' }}>
            <CompactComponent 
              height={Math.min(300, getComponentHeight('chatInterface'))}
              scrollable={true}
            >
              <Card className="border-0 shadow-none">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">
                    AI Chat ({currentBreakpoint} view)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                    Chat interface optimized for {currentBreakpoint} view with {getOptimalLayout()} layout.
                  </div>
                </CardContent>
              </Card>
            </CompactComponent>
          </div>
        )}
      </ContentArea>

      {/* Debug Info */}
      <div style={{ 
        position: 'fixed', 
        top: '70px', 
        right: '10px', 
        padding: '8px', 
        backgroundColor: 'var(--card)', 
        border: '1px solid var(--border)', 
        borderRadius: '4px',
        fontSize: '10px',
        zIndex: 1000,
        minWidth: '200px'
      }}>
        <div><strong>Layout Debug Info:</strong></div>
        <div>Breakpoint: <Badge variant="outline" className="text-xs">{currentBreakpoint}</Badge></div>
        <div>Screen: {layoutConfiguration.screenSize.width}x{layoutConfiguration.screenSize.height}</div>
        <div>Sidebar: {layoutConfiguration.columns.sidebar}px</div>
        <div>Layout: <Badge variant="outline" className="text-xs">{getOptimalLayout()}</Badge></div>
        <div>Columns: {getColumnCount()}</div>
      </div>
    </MainLayoutGrid>
  );
};

export const LayoutConfigurationDemo: React.FC = () => {
  return (
    <LayoutConfigurationProvider>
      <div className="h-screen">
        <Tabs defaultValue="demo" className="h-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="demo">Layout Demo</TabsTrigger>
            <TabsTrigger value="settings">Layout Settings</TabsTrigger>
          </TabsList>
          
          <TabsContent value="demo" className="h-full mt-0">
            <LayoutContent />
          </TabsContent>
          
          <TabsContent value="settings" className="h-full mt-0 p-4 overflow-y-auto">
            <div className="max-w-4xl mx-auto">
              <LayoutSettings />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </LayoutConfigurationProvider>
  );
};