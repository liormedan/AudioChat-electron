import React from 'react';
import { MainLayoutGrid, ContentArea, Column, CompactComponent } from './main-layout-grid';
import { Header } from './header';
import Sidebar from './sidebar';
import { useResponsiveLayout } from '../../hooks/use-responsive-layout';
import './main-layout-grid.css';

export const LayoutDemo: React.FC = () => {
  const { 
    currentBreakpoint, 
    layoutConfiguration, 
    screenSize,
    isMobile,
    isTablet 
  } = useResponsiveLayout();

  return (
    <MainLayoutGrid>
      {/* Header */}
      <div style={{ gridColumn: '1 / -1', gridRow: '1' }}>
        <Header />
      </div>

      {/* Sidebar - Hidden on mobile */}
      {!isMobile && (
        <div style={{ gridColumn: '1', gridRow: '2' }}>
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
          >
            <div style={{ padding: '16px' }}>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '600' }}>
                File Upload
              </h3>
              <div style={{ 
                height: '120px', 
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
            </div>
          </CompactComponent>

          <CompactComponent 
            height={layoutConfiguration.components.fileManager.height}
            scrollable={true}
          >
            <div style={{ padding: '16px' }}>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '600' }}>
                File Manager
              </h3>
              <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                {Array.from({ length: 10 }, (_, i) => (
                  <div key={i} style={{ padding: '4px 0', borderBottom: '1px solid var(--border)' }}>
                    Audio File {i + 1}.mp3
                  </div>
                ))}
              </div>
            </div>
          </CompactComponent>
        </Column>

        {/* Column 2 - Player & Info */}
        <Column column={2}>
          <CompactComponent 
            height={layoutConfiguration.components.waveformPlayer.height}
            scrollable={false}
          >
            <div style={{ padding: '16px' }}>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '600' }}>
                Waveform Player
              </h3>
              <div style={{ 
                height: '120px', 
                backgroundColor: 'var(--muted)', 
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--muted-foreground)',
                fontSize: '12px'
              }}>
                Waveform Visualization
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px' }}>
                <div>Duration: 3:45</div>
                <div>Sample Rate: 44.1kHz</div>
              </div>
            </div>
          </CompactComponent>
        </Column>

        {/* Column 3 - Chat & Tools */}
        {(!isTablet && !isMobile) && (
          <Column column={3}>
            <CompactComponent 
              height={layoutConfiguration.components.chatInterface.height}
              scrollable={true}
            >
              <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '600' }}>
                  AI Chat
                </h3>
                <div style={{ flex: 1, fontSize: '12px', color: 'var(--muted-foreground)' }}>
                  <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: 'var(--muted)', borderRadius: '4px' }}>
                    AI: Hello! Upload an audio file to get started.
                  </div>
                  <div style={{ marginBottom: '8px', padding: '8px', backgroundColor: 'var(--primary)', color: 'var(--primary-foreground)', borderRadius: '4px', textAlign: 'right' }}>
                    User: Can you help me edit this audio?
                  </div>
                </div>
                <div style={{ 
                  marginTop: '8px', 
                  padding: '8px', 
                  border: '1px solid var(--border)', 
                  borderRadius: '4px',
                  fontSize: '12px'
                }}>
                  Type your message...
                </div>
              </div>
            </CompactComponent>
          </Column>
        )}

        {/* Mobile/Tablet: Chat in full width row */}
        {(isTablet || isMobile) && (
          <div style={{ gridColumn: '1 / -1' }}>
            <CompactComponent 
              height={300}
              scrollable={true}
            >
              <div style={{ padding: '16px' }}>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '600' }}>
                  AI Chat
                </h3>
                <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                  Chat interface optimized for {currentBreakpoint} view
                </div>
              </div>
            </CompactComponent>
          </div>
        )}
      </ContentArea>

      {/* Debug Info */}
      <div style={{ 
        position: 'fixed', 
        top: '10px', 
        right: '10px', 
        padding: '8px', 
        backgroundColor: 'var(--card)', 
        border: '1px solid var(--border)', 
        borderRadius: '4px',
        fontSize: '10px',
        zIndex: 1000
      }}>
        <div>Breakpoint: {currentBreakpoint}</div>
        <div>Screen: {screenSize.width}x{screenSize.height}</div>
        <div>Sidebar: {layoutConfiguration.columns.sidebar}px</div>
      </div>
    </MainLayoutGrid>
  );
};