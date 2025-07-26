import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from './components/ui/toaster';
import { AppProviders } from './providers/app-providers';
import { StoreManager } from './components/store-manager';
import { useStoreInitialization } from './hooks/use-store-initialization';
import { useTheme } from './hooks/use-app-state';
import { useKeyboardShortcuts } from './hooks/use-keyboard-shortcuts';
import { MainLayout } from './components/layout/main-layout';
import { 
  HomePage, 
  AudioPage, 
  ExportPage, 
  StatsPage, 
  LLMPage, 
  ProfilePage, 
  SettingsPage 
} from './pages';

const AppContent: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const { isInitialized, initializationError } = useStoreInitialization();
  
  // Initialize keyboard shortcuts
  useKeyboardShortcuts();

  useEffect(() => {
    // Check if Electron API is available and load initial theme
    if (window.electronAPI) {
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

  return (
    <Router>
      <div className="app min-h-screen bg-background text-foreground">
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<HomePage />} />
            <Route path="audio" element={<AudioPage />} />
            <Route path="export" element={<ExportPage />} />
            <Route path="stats" element={<StatsPage />} />
            <Route path="llm" element={<LLMPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </div>
    </Router>
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