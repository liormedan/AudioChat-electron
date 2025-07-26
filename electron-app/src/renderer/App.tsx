import React, { useEffect, useState } from 'react';
import { Toaster } from './components/ui/toaster';
import ComponentShowcase from './components/ComponentShowcase';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { AppProviders } from './providers/app-providers';
import { StoreManager } from './components/store-manager';
import { useStoreInitialization } from './hooks/use-store-initialization';
import { useTheme, useNotifications, useAppState } from './hooks/use-app-state';
import { useToast } from './hooks/use-toast';
import { StateDebugPanel } from './components/state-debug-panel';

const AppContent: React.FC = () => {
  const [isElectronReady, setIsElectronReady] = useState(false);
  const [showShowcase, setShowShowcase] = useState(false);
  const { theme, setTheme } = useTheme();
  const { addNotification } = useNotifications();
  const { toast } = useToast();
  const { isInitialized, initializationError } = useStoreInitialization();
  const appState = useAppState();

  useEffect(() => {
    // Check if Electron API is available
    if (window.electronAPI) {
      setIsElectronReady(true);
      
      // Load initial theme from Electron
      window.electronAPI.getTheme()
        .then((savedTheme) => {
          if (savedTheme === 'light' || savedTheme === 'dark') {
            setTheme(savedTheme);
          }
        })
        .catch((error) => {
          console.error('Failed to load theme:', error);
        });
    }
  }, [setTheme]);

  const handleThemeToggle = (): void => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    
    // Add notification using Zustand store
    addNotification({
      type: 'success',
      title: 'Theme Changed',
      message: `Switched to ${newTheme} theme`,
    });
    
    toast({
      title: "Theme Changed",
      description: `Switched to ${newTheme} theme`,
    });
  };

  const handleShowNotification = async (): Promise<void> => {
    if (window.electronAPI) {
      try {
        await window.electronAPI.showNotification(
          'Audio Chat Studio',
          'Welcome to the new Electron version!'
        );
        
        addNotification({
          type: 'success',
          title: 'Notification Sent',
          message: 'System notification has been displayed',
        });
        
        toast({
          title: "Notification Sent",
          description: "System notification has been displayed",
        });
      } catch (error) {
        console.error('Failed to show notification:', error);
        
        addNotification({
          type: 'error',
          title: 'Error',
          message: 'Failed to show system notification',
        });
        
        toast({
          title: "Error",
          description: "Failed to show system notification",
          variant: "destructive",
        });
      }
    }
  };

  const handleSelectFile = async (): Promise<void> => {
    if (window.electronAPI) {
      try {
        const filePath = await window.electronAPI.selectFile({
          filters: [
            { name: 'Audio Files', extensions: ['mp3', 'wav', 'flac'] },
            { name: 'All Files', extensions: ['*'] }
          ]
        });
        
        if (filePath) {
          // Add to recent files using Zustand store
          appState.user.addRecentFile(filePath);
          
          await window.electronAPI.showNotification(
            'File Selected',
            `Selected: ${filePath}`
          );
          
          addNotification({
            type: 'info',
            title: 'File Selected',
            message: `Selected: ${filePath.split('/').pop()}`,
          });
          
          toast({
            title: "File Selected",
            description: `Selected: ${filePath.split('/').pop()}`,
          });
        }
      } catch (error) {
        console.error('Failed to select file:', error);
        
        addNotification({
          type: 'error',
          title: 'Error',
          message: 'Failed to select file',
        });
        
        toast({
          title: "Error",
          description: "Failed to select file",
          variant: "destructive",
        });
      }
    }
  };

  // Show loading screen while stores are initializing
  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Initializing application...</p>
          {initializationError && (
            <p className="text-destructive text-sm">Error: {initializationError}</p>
          )}
        </div>
      </div>
    );
  }

  if (showShowcase) {
    return <ComponentShowcase onBack={() => setShowShowcase(false)} />;
  }

  return (
    <div className="app min-h-screen bg-background text-foreground">
      <div className="container mx-auto p-6 space-y-8">
        <header className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">
            Audio Chat Studio
          </h1>
          <p className="text-xl text-muted-foreground">
            Modern Electron Application with React & TypeScript
          </p>
        </header>

        <main className="space-y-8">
          {/* System Status Card */}
          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>
                Current system status and configuration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Electron API:</span>
                  <span className={`font-bold ${
                    isElectronReady ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  }`}>
                    {isElectronReady ? 'Ready' : 'Not Available'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-medium">Current Theme:</span>
                  <span className="font-mono text-sm bg-muted px-2 py-1 rounded">
                    {theme}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-medium">React Version:</span>
                  <span className="font-mono text-sm bg-muted px-2 py-1 rounded">
                    {React.version}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-medium">TypeScript:</span>
                  <span className="text-green-600 dark:text-green-400 font-bold">
                    Enabled
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Test Features Card */}
          <Card>
            <CardHeader>
              <CardTitle>Test Features</CardTitle>
              <CardDescription>
                Test the application features and integrations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <Button
                  onClick={handleThemeToggle}
                  disabled={!isElectronReady}
                  variant="default"
                >
                  Toggle Theme
                </Button>
                
                <Button
                  onClick={handleShowNotification}
                  disabled={!isElectronReady}
                  variant="secondary"
                >
                  Show Notification
                </Button>
                
                <Button
                  onClick={handleSelectFile}
                  disabled={!isElectronReady}
                  variant="outline"
                >
                  Select File
                </Button>

                <Button
                  onClick={() => setShowShowcase(true)}
                  variant="ghost"
                >
                  View Component Showcase
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Progress Card */}
          <Card>
            <CardHeader>
              <CardTitle>Development Progress</CardTitle>
              <CardDescription>
                Current implementation status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Electron + React + TypeScript foundation</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Security best practices (context isolation)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Basic window management</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>IPC communication layer</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>shadcn/ui component library</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>State management with Zustand</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>React Query for server state</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Redux DevTools integration</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span>Python backend integration</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* State Debug Panel */}
          <StateDebugPanel />
        </main>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AppProviders>
      <StoreManager>
        <AppContent />
        <Toaster />
      </StoreManager>
    </AppProviders>
  );
};

export default App;