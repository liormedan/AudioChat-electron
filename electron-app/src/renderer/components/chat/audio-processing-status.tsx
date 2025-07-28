import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { 
  Loader2, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Zap,
  FileAudio,
  AlertCircle
} from 'lucide-react';

interface AudioProcessingStatusProps {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  progress?: number;
  message?: string;
  fileName?: string | undefined;
  estimatedTime?: string;
  currentStep?: string;
  totalSteps?: number;
  currentStepIndex?: number;
}

export const AudioProcessingStatus: React.FC<AudioProcessingStatusProps> = ({
  status,
  progress = 0,
  message,
  fileName,
  estimatedTime,
  currentStep,
  totalSteps,
  currentStepIndex = 0
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'uploading':
        return {
          icon: <Loader2 className="h-4 w-4 animate-spin" />,
          color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
          title: 'Uploading',
          description: 'Uploading your audio file to the server...'
        };
      case 'processing':
        return {
          icon: <Zap className="h-4 w-4 animate-pulse" />,
          color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
          title: 'Processing',
          description: message || 'Processing your audio command...'
        };
      case 'completed':
        return {
          icon: <CheckCircle className="h-4 w-4" />,
          color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
          title: 'Completed',
          description: 'Audio processing completed successfully!'
        };
      case 'error':
        return {
          icon: <XCircle className="h-4 w-4" />,
          color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
          title: 'Error',
          description: message || 'An error occurred during processing'
        };
      default:
        return null;
    }
  };

  const statusConfig = getStatusConfig();

  if (status === 'idle' || !statusConfig) {
    return null;
  }

  return (
    <Card className="w-full border-l-4 border-l-primary">
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Status Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {statusConfig.icon}
              <span className="font-medium">{statusConfig.title}</span>
              {fileName && (
                <Badge variant="outline" className="text-xs">
                  <FileAudio className="h-3 w-3 mr-1" />
                  {fileName}
                </Badge>
              )}
            </div>
            <Badge className={statusConfig.color}>
              {statusConfig.title}
            </Badge>
          </div>

          {/* Progress Bar */}
          {(status === 'uploading' || status === 'processing') && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>{statusConfig.description}</span>
                <span className="text-muted-foreground">{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}

          {/* Step Progress */}
          {currentStep && totalSteps && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center space-x-2">
                  <span>Step {currentStepIndex + 1} of {totalSteps}:</span>
                  <span className="font-medium">{currentStep}</span>
                </span>
                {estimatedTime && (
                  <span className="flex items-center text-muted-foreground">
                    <Clock className="h-3 w-3 mr-1" />
                    {estimatedTime}
                  </span>
                )}
              </div>
              <Progress 
                value={(currentStepIndex / totalSteps) * 100} 
                className="h-1" 
              />
            </div>
          )}

          {/* Status Message */}
          <p className="text-sm text-muted-foreground">
            {statusConfig.description}
          </p>

          {/* Estimated Time */}
          {estimatedTime && status === 'processing' && (
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>Estimated time remaining: {estimatedTime}</span>
            </div>
          )}

          {/* Error Details */}
          {status === 'error' && message && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-red-700 dark:text-red-300">
                  <p className="font-medium">Error Details:</p>
                  <p className="mt-1">{message}</p>
                </div>
              </div>
            </div>
          )}

          {/* Success Details */}
          {status === 'completed' && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
              <div className="flex items-center space-x-2 text-green-700 dark:text-green-300">
                <CheckCircle className="h-4 w-4" />
                <span className="text-sm font-medium">
                  Processing completed successfully! Check the preview above.
                </span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};