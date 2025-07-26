import React, { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { Music, Download, BarChart3, Bot, FileAudio, Clock } from 'lucide-react';
import { useUIStore } from '../stores/ui-store';
import { useAppState } from '../hooks/use-app-state';
import { FileDropZone } from '../components/file-drop-zone';
import { useToast } from '../hooks/use-toast';
import { useQuickStats } from '../hooks/use-queries';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { setCurrentPage } = useUIStore();
  const appState = useAppState();
  const { toast } = useToast();
  const { data: quickStats } = useQuickStats();

  useEffect(() => {
    toast({ title: 'Welcome back!' });
  }, [toast]);

  const handleFiles = (files: FileList) => {
    Array.from(files).forEach((file) => appState.user.addRecentFile(file.path));
    toast({ title: 'Files uploaded', description: `${files.length} file(s) added` });
  };

  const handleQuickAction = (path: string, pageId: string) => {
    setCurrentPage(pageId);
    navigate(path);
  };

  const quickActions = [
    {
      id: 'audio',
      title: 'Audio Processing',
      description: 'Process and edit audio files',
      icon: Music,
      path: '/audio',
      color: 'text-blue-600 dark:text-blue-400'
    },
    {
      id: 'export',
      title: 'Export Files',
      description: 'Export and download processed files',
      icon: Download,
      path: '/export',
      color: 'text-green-600 dark:text-green-400'
    },
    {
      id: 'stats',
      title: 'File Statistics',
      description: 'View file analytics and insights',
      icon: BarChart3,
      path: '/stats',
      color: 'text-purple-600 dark:text-purple-400'
    },
    {
      id: 'llm',
      title: 'AI Assistant',
      description: 'Manage AI models and chat',
      icon: Bot,
      path: '/llm',
      color: 'text-orange-600 dark:text-orange-400'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome to Audio Chat Studio
        </h1>
        <p className="text-muted-foreground">
          Your modern audio processing and AI-powered chat application
        </p>
      </div>

      {/* Upload Zone */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Audio</CardTitle>
          <CardDescription>Drag and drop audio files to add them</CardDescription>
        </CardHeader>
        <CardContent>
          <FileDropZone onFiles={handleFiles} />
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Files</CardTitle>
            <FileAudio className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {quickStats?.totalFiles ?? appState.user.recentFiles.length}
            </div>
            <p className="text-xs text-muted-foreground">Files processed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processing Jobs</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {quickStats?.processingJobs ?? 0}
            </div>
            <p className="text-xs text-muted-foreground">Active processing jobs</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Conversations</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {quickStats?.conversations ?? 0}
            </div>
            <p className="text-xs text-muted-foreground">Active chat sessions</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Jump to commonly used features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Button
                  key={action.id}
                  variant="outline"
                  className="h-auto p-4 flex flex-col items-center space-y-2"
                  onClick={() => handleQuickAction(action.path, action.id)}
                >
                  <Icon className={`h-8 w-8 ${action.color}`} />
                  <div className="text-center">
                    <div className="font-medium">{action.title}</div>
                    <div className="text-xs text-muted-foreground">
                      {action.description}
                    </div>
                  </div>
                </Button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent Files */}
      {appState.user.recentFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Files</CardTitle>
            <CardDescription>
              Recently accessed audio files
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {appState.user.recentFiles.slice(0, 5).map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 cursor-pointer"
                >
                  <div className="flex items-center space-x-3">
                    <FileAudio className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">
                        {file.split('/').pop() || file}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {file}
                      </div>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    Open
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};