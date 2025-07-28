import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Settings, Palette, Volume2, Database, Info } from 'lucide-react';
import { useUIStore } from '../stores/ui-store';

export const SettingsPage: React.FC = () => {
  const { theme, setTheme } = useUIStore();

  const handleThemeToggle = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure application settings and preferences
        </p>
      </div>

      {/* Appearance Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Palette className="h-5 w-5" />
            <span>Appearance</span>
          </CardTitle>
          <CardDescription>
            Customize the look and feel of the application
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium">Theme</h4>
              <p className="text-sm text-muted-foreground">
                Choose between light and dark theme
              </p>
            </div>
            <Button
              variant="outline"
              onClick={handleThemeToggle}
            >
              {theme === 'light' ? 'Switch to Dark' : 'Switch to Light'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Audio Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Volume2 className="h-5 w-5" />
            <span>Audio Settings</span>
          </CardTitle>
          <CardDescription>
            Configure audio processing and playback settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Audio settings configuration will be implemented here.
          </p>
        </CardContent>
      </Card>

      {/* Data & Storage */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>Data & Storage</span>
          </CardTitle>
          <CardDescription>
            Manage application data and storage settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Data and storage settings will be implemented here.
          </p>
        </CardContent>
      </Card>

      {/* General Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>General</span>
          </CardTitle>
          <CardDescription>
            General application settings and preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            General settings will be implemented here.
          </p>
        </CardContent>
      </Card>

      {/* About */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Info className="h-5 w-5" />
            <span>About</span>
          </CardTitle>
          <CardDescription>
            Application information and version details
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p><strong>Audio Chat Studio</strong></p>
            <p className="text-sm text-muted-foreground">Electron Version 1.0.0</p>
            <p className="text-sm text-muted-foreground">Built with React, TypeScript, and shadcn/ui</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};