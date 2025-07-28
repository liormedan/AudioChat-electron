import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { 
  Download, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Clock,
  FileAudio
} from 'lucide-react';
import { AudioChatMessage } from './AudioChatMessage';

interface AudioPreviewProps {
  originalFile?: {
    name: string;
    url: string;
    duration?: string | undefined;
    size?: string | undefined;
  } | undefined;
  processedFile?: {
    name: string;
    url: string;
    duration?: string;
    size?: string;
  };
  processingStatus: 'idle' | 'processing' | 'completed' | 'error';
  processingProgress?: number;
  processingMessage?: string;
  onDownload?: (fileUrl: string, fileName: string) => void;
  onReprocess?: () => void;
  onAccept?: () => void;
  onReject?: () => void;
  showComparison?: boolean;
}

export const AudioPreview: React.FC<AudioPreviewProps> = ({
  originalFile,
  processedFile,
  processingStatus,
  processingProgress = 0,
  processingMessage = 'Processing audio...',
  onDownload,
  onReprocess,
  onAccept,
  onReject,
  showComparison = true
}) => {

  const getStatusIcon = () => {
    switch (processingStatus) {
      case 'processing':
        return <RefreshCw className="h-4 w-4 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <FileAudio className="h-4 w-4" />;
    }
  };

  const getStatusColor = () => {
    switch (processingStatus) {
      case 'processing':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  if (processingStatus === 'idle' && !originalFile && !processedFile) {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span>Audio Preview</span>
          </div>
          <Badge className={getStatusColor()}>
            {processingStatus.charAt(0).toUpperCase() + processingStatus.slice(1)}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Processing Status */}
        {processingStatus === 'processing' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center space-x-2">
                <RefreshCw className="h-3 w-3 animate-spin" />
                <span>{processingMessage}</span>
              </span>
              <span>{Math.round(processingProgress)}%</span>
            </div>
            <Progress value={processingProgress} className="h-2" />
          </div>
        )}

        {/* Error Message */}
        {processingStatus === 'error' && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
            <div className="flex items-center space-x-2 text-red-800 dark:text-red-200">
              <XCircle className="h-4 w-4" />
              <span className="font-medium">Processing Failed</span>
            </div>
            <p className="text-sm text-red-600 dark:text-red-300 mt-1">
              {processingMessage || 'An error occurred while processing the audio file.'}
            </p>
            {onReprocess && (
              <Button
                variant="outline"
                size="sm"
                onClick={onReprocess}
                className="mt-2"
              >
                <RefreshCw className="h-3 w-3 mr-1" />
                Try Again
              </Button>
            )}
          </div>
        )}

        {/* Audio Comparison */}
        {showComparison && (originalFile || processedFile) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Original File */}
            {originalFile && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-sm">Original</h4>
                  <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                    {originalFile.duration && (
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {originalFile.duration}
                      </span>
                    )}
                    {originalFile.size && (
                      <span className="flex items-center">
                        <FileAudio className="h-3 w-3 mr-1" />
                        {originalFile.size}
                      </span>
                    )}
                  </div>
                </div>
                <AudioChatMessage 
                  audioUrl={originalFile.url} 
                  fileName={originalFile.name}
                />
              </div>
            )}

            {/* Processed File */}
            {processedFile && processingStatus === 'completed' && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-sm">Processed</h4>
                  <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                    {processedFile.duration && (
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {processedFile.duration}
                      </span>
                    )}
                    {processedFile.size && (
                      <span className="flex items-center">
                        <FileAudio className="h-3 w-3 mr-1" />
                        {processedFile.size}
                      </span>
                    )}
                  </div>
                </div>
                <AudioChatMessage 
                  audioUrl={processedFile.url} 
                  fileName={processedFile.name}
                />
              </div>
            )}
          </div>
        )}

        {/* Single File Preview */}
        {!showComparison && processedFile && processingStatus === 'completed' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Processed Audio</h4>
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                {processedFile.duration && (
                  <span className="flex items-center">
                    <Clock className="h-3 w-3 mr-1" />
                    {processedFile.duration}
                  </span>
                )}
                {processedFile.size && (
                  <span className="flex items-center">
                    <FileAudio className="h-3 w-3 mr-1" />
                    {processedFile.size}
                  </span>
                )}
              </div>
            </div>
            <AudioChatMessage 
              audioUrl={processedFile.url} 
              fileName={processedFile.name}
            />
          </div>
        )}

        {/* Action Buttons */}
        {processingStatus === 'completed' && processedFile && (
          <div className="flex items-center justify-between pt-2 border-t">
            <div className="flex items-center space-x-2">
              {onDownload && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onDownload(processedFile.url, processedFile.name)}
                >
                  <Download className="h-3 w-3 mr-1" />
                  Download
                </Button>
              )}
              {onReprocess && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onReprocess}
                >
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Reprocess
                </Button>
              )}
            </div>
            
            {(onAccept || onReject) && (
              <div className="flex items-center space-x-2">
                {onReject && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onReject}
                  >
                    <XCircle className="h-3 w-3 mr-1" />
                    Reject
                  </Button>
                )}
                {onAccept && (
                  <Button
                    size="sm"
                    onClick={onAccept}
                  >
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Accept
                  </Button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Processing Info */}
        {processingStatus === 'completed' && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
            <div className="flex items-center space-x-2 text-green-800 dark:text-green-200">
              <CheckCircle className="h-4 w-4" />
              <span className="font-medium">Processing Complete</span>
            </div>
            <p className="text-sm text-green-600 dark:text-green-300 mt-1">
              Your audio has been successfully processed. You can preview the results above.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};