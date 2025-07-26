import React, { useEffect } from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from './components/ui/toaster';
import { AppProviders } from './providers/app-providers';
import { StoreManager } from './components/store-manager';
import { useStoreInitialization } from './hooks/use-store-initialization';
import { MainLayout } from './components/layout/main-layout';
import {
  HomePage,
  AudioPage,
  ExportPage,
  StatsPage,
  LLMPage,
  ProfilePage,
  SettingsPage,
  ChatPage // Import ChatPage
} from './pages';

const AppContent: React.FC = () => {
  // const { isInitialized, initializationError } = useStoreInitialization();

  // // Show loading screen while stores are initializing
  // if (!isInitialized) {
  //   return (
  //     <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
  //       <div className="text-center space-y-4">
  //         <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
  //         <p className="text-muted-foreground">Initializing application...</p>
  //         {initializationError && (
  //           <p className="text-destructive text-sm">Error: {initializationError}</p>
  //         )}
  //       </div>
  //     </div>
  //   );
  // }

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
            <Route path="chat" element={<ChatPage />} />
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
    <AppContent />
  );
};

export default App;
