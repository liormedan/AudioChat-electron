import React, { useEffect, useState } from 'react';
import { ThemeProvider } from './contexts/theme-provider';
import { Toaster } from './components/ui/toaster';
import ComponentShowcase from './components/ComponentShowcase';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { useTheme } from './contexts/theme-provider';
import { useToast } from './hooks/use-toast';

const AppContent: React.FC = () => {
  const [isElectronReady, setIsElectronReady] = useState(false);
  const [showShowcase, setShowShowcase] = useState(false);
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();

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
        toast({
          title: "Notification Sent",
          description: "System notification has been displayed",
        });
      } catch (error) {
        console.error('Failed to show notification:', error);
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
          await window.electronAPI.showNotification(
            'File Selected',
            `Selected: ${filePath}`
          );
          toast({
            title: "File Selected",
            description: `Selected: ${filePath.split('/').pop()}`,
          });
        }
      } catch (error) {
        console.error('Failed to select file:', error);
        toast({
          title: "Error",
          description: "Failed to select file",
          variant: "destructive",
        });
      }
    }
  };

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
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span>State management with Zustand</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span>Python backend integration</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider defaultTheme="system" storageKey="audio-chat-studio-theme">
      <AppContent />
      <Toaster />
    </ThemeProvider>
  );
};

export default App;