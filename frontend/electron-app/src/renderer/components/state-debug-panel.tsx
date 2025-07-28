import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useAppState, useNotifications } from '../hooks/use-app-state';

export const StateDebugPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const appState = useAppState();
  const { addNotification } = useNotifications();

  const handleTestNotification = () => {
    addNotification({
      type: 'info',
      title: 'Test Notification',
      message: 'This is a test notification from the state debug panel',
    });
  };

  const handleTestThemeToggle = () => {
    const newTheme = appState.ui.theme === 'light' ? 'dark' : 'light';
    appState.ui.setTheme(newTheme);
  };

  const handleTestRecentFile = () => {
    const testFile = `/test/path/audio-${Date.now()}.mp3`;
    appState.user.addRecentFile(testFile);
    
    addNotification({
      type: 'success',
      title: 'Recent File Added',
      message: `Added ${testFile.split('/').pop()} to recent files`,
    });
  };

  return (
    <Card>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  State Debug Panel
                  <Badge variant="secondary">Zustand + React Query</Badge>
                </CardTitle>
                <CardDescription>
                  Current application state and testing controls
                </CardDescription>
              </div>
              {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        
        <CollapsibleContent>
          <CardContent className="space-y-6">
            {/* Test Actions */}
            <div className="space-y-3">
              <h4 className="font-semibold">Test Actions</h4>
              <div className="flex flex-wrap gap-2">
                <Button size="sm" onClick={handleTestNotification}>
                  Test Notification
                </Button>
                <Button size="sm" variant="outline" onClick={handleTestThemeToggle}>
                  Toggle Theme
                </Button>
                <Button size="sm" variant="secondary" onClick={handleTestRecentFile}>
                  Add Recent File
                </Button>
              </div>
            </div>

            {/* UI State */}
            <div className="space-y-3">
              <h4 className="font-semibold">UI State</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span>Current Page:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.ui.currentPage}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Theme:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.ui.theme}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Sidebar Collapsed:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.ui.sidebarCollapsed.toString()}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Loading:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.ui.isLoading.toString()}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Notifications:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.ui.notifications.length}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Active Modal:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.ui.activeModal || 'null'}
                  </code>
                </div>
              </div>
            </div>

            {/* User State */}
            <div className="space-y-3">
              <h4 className="font-semibold">User State</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span>Authenticated:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.user.isAuthenticated.toString()}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>User:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.user.user ? 'Set' : 'null'}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Recent Files:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.user.recentFiles.length}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Recent Projects:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.user.recentProjects.length}
                  </code>
                </div>
              </div>
              
              {appState.user.recentFiles.length > 0 && (
                <div className="space-y-2">
                  <span className="text-sm font-medium">Recent Files:</span>
                  <div className="space-y-1">
                    {appState.user.recentFiles.slice(0, 3).map((file, index) => (
                      <div key={index} className="text-xs bg-muted p-2 rounded">
                        {file}
                      </div>
                    ))}
                    {appState.user.recentFiles.length > 3 && (
                      <div className="text-xs text-muted-foreground">
                        ... and {appState.user.recentFiles.length - 3} more
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Settings State */}
            <div className="space-y-3">
              <h4 className="font-semibold">Settings State</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span>Has Unsaved Changes:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.settings.hasUnsavedChanges.toString()}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Loading:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.settings.isLoading.toString()}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Theme Setting:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.settings.settings.ui.theme}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span>Auto Save:</span>
                  <code className="bg-muted px-2 py-1 rounded text-xs">
                    {appState.settings.settings.app.autoStart.toString()}
                  </code>
                </div>
              </div>
            </div>

            {/* DevTools Info */}
            <div className="space-y-3">
              <h4 className="font-semibold">DevTools</h4>
              <div className="text-sm space-y-2">
                <p className="text-muted-foreground">
                  Redux DevTools are enabled for all Zustand stores. Open your browser's 
                  developer tools and look for the "Redux" tab to inspect state changes.
                </p>
                <p className="text-muted-foreground">
                  React Query DevTools are available in the bottom-right corner (development only).
                </p>
              </div>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};