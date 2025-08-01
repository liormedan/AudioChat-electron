import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Square, 
  RotateCcw, 
  ExternalLink, 
  Circle,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
import { ServiceStatus } from '@/types/ipc';

interface ServiceStatusCardProps {
  service: ServiceStatus;
  onStart: () => void;
  onStop: () => void;
  onRestart: () => void;
  onOpenBrowser?: () => void;
}

export const ServiceStatusCard: React.FC<ServiceStatusCardProps> = ({
  service,
  onStart,
  onStop,
  onRestart,
  onOpenBrowser
}) => {
  const getStatusIcon = () => {
    switch (service.status) {
      case 'running':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'starting':
        return <Clock className="h-4 w-4 text-yellow-500 animate-spin" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'stopped':
      default:
        return <Circle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (service.status) {
      case 'running':
        return 'bg-green-500';
      case 'starting':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      case 'stopped':
      default:
        return 'bg-gray-400';
    }
  };

  const formatUptime = (uptime?: number) => {
    if (!uptime) return 'N/A';
    const seconds = Math.floor(uptime / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="capitalize">{service.name}</span>
            {service.port && (
              <Badge variant="outline" className="text-xs">
                :{service.port}
              </Badge>
            )}
          </div>
          <div className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
            <Badge 
              variant={service.status === 'running' ? 'default' : 
                     service.status === 'error' ? 'destructive' : 'secondary'}
              className="text-xs"
            >
              {service.status}
            </Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Service Info */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-muted-foreground">PID:</span>
            <span className="ml-2">{service.pid || 'N/A'}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Uptime:</span>
            <span className="ml-2">{formatUptime(service.uptime)}</span>
          </div>
        </div>

        {/* Error Message */}
        {service.status === 'error' && service.lastError && (
          <div className="p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-sm">
            <span className="text-red-600 dark:text-red-400">Error: {service.lastError}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          {service.status === 'stopped' || service.status === 'error' ? (
            <Button
              size="sm"
              onClick={onStart}
              className="flex items-center space-x-1"
            >
              <Play className="h-3 w-3" />
              <span>Start</span>
            </Button>
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={onStop}
              className="flex items-center space-x-1"
            >
              <Square className="h-3 w-3" />
              <span>Stop</span>
            </Button>
          )}
          
          <Button
            size="sm"
            variant="outline"
            onClick={onRestart}
            disabled={service.status === 'starting'}
            className="flex items-center space-x-1"
          >
            <RotateCcw className="h-3 w-3" />
            <span>Restart</span>
          </Button>

          {service.port && service.status === 'running' && onOpenBrowser && (
            <Button
              size="sm"
              variant="outline"
              onClick={onOpenBrowser}
              className="flex items-center space-x-1"
            >
              <ExternalLink className="h-3 w-3" />
              <span>Open</span>
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};