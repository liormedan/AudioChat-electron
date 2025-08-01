import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Play, 
  Square, 
  RotateCcw, 
  ExternalLink,
  Settings,
  Activity,
  Zap
} from 'lucide-react';

interface TerminalControlsProps {
  onStartAll: () => void;
  onStopAll: () => void;
  onRestartAll: () => void;
  onCheckHealth: () => void;
  isLoading?: boolean;
  servicesRunning: number;
  totalServices: number;
}

export const TerminalControls: React.FC<TerminalControlsProps> = ({
  onStartAll,
  onStopAll,
  onRestartAll,
  onCheckHealth,
  isLoading = false,
  servicesRunning,
  totalServices
}) => {
  const openUrl = (url: string) => {
    window.open(url, '_blank');
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>System Controls</span>
          </div>
          <Badge variant="outline" className="text-xs">
            {servicesRunning}/{totalServices} running
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Service Control Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <Button
            onClick={onStartAll}
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            <Play className="h-4 w-4" />
            <span>Start All</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={onStopAll}
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            <Square className="h-4 w-4" />
            <span>Stop All</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={onRestartAll}
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            <RotateCcw className="h-4 w-4" />
            <span>Restart All</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={onCheckHealth}
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            <Activity className="h-4 w-4" />
            <span>Health Check</span>
          </Button>
        </div>

        {/* Quick Access Links */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">Quick Access</h4>
          <div className="grid grid-cols-1 gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => openUrl('http://127.0.0.1:5000/docs')}
              className="flex items-center justify-between"
            >
              <div className="flex items-center space-x-2">
                <Zap className="h-3 w-3" />
                <span>API Documentation</span>
              </div>
              <ExternalLink className="h-3 w-3" />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => openUrl('http://127.0.0.1:5000/')}
              className="flex items-center justify-between"
            >
              <div className="flex items-center space-x-2">
                <Activity className="h-3 w-3" />
                <span>Backend API</span>
              </div>
              <ExternalLink className="h-3 w-3" />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => openUrl('http://127.0.0.1:5001/')}
              className="flex items-center justify-between"
            >
              <div className="flex items-center space-x-2">
                <Settings className="h-3 w-3" />
                <span>Admin Panel</span>
              </div>
              <ExternalLink className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* System Info */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">System Info</h4>
          <div className="text-xs space-y-1 text-muted-foreground">
            <div>Node.js: {process.versions?.node || 'Unknown'}</div>
            <div>Electron: {process.versions?.electron || 'Unknown'}</div>
            <div>Platform: {process.platform}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};