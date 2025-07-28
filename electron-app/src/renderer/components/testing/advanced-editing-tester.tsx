import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Slider } from '../ui/slider';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Scissors, 
  Volume2, 
  Zap, 
  Settings, 
  Upload, 
  Play,
  CheckCircle, 
  XCircle, 
  Loader2,
  FileAudio,
  Download,
  RefreshCw,
  Combine,
  Filter
} from 'lucide-react';

interface EditingResult {
  success: boolean;
  message?: string;
  output_file?: string;
  processing_time?: number;
  error?: string;
  [key: string]: any;
}

interface EditingOperation {
  id: string;
  name: string;
  description: string;
  category: 'basic' | 'advanced' | 'effects';
  parameters: Array<{
    name: string;
    type: 'number' | 'string' | 'boolean' | 'range';
    default: any;
    min?: number;
    max?: number;
    step?: number;
    options?: string[];
  }>;
}

const editingOperations: EditingOperation[] = [
  {
    id: 'trim',
    name: 'Trim Audio',
    description: 'Cut audio between specific time points',
    category: 'basic',
    parameters: [
      { name: 'start_time', type: 'number', default: 0, min: 0, step: 0.1 },
      { name: 'end_time', type: 'number', default: 10, min: 0, step: 0.1 }
    ]
  },
  {
    id: 'volume',
    name: 'Adjust Volume',
    description: 'Change audio volume level',
    category: 'basic',
    parameters: [
      { name: 'volume_change_db', type: 'range', default: 0, min: -60, max: 20, step: 1 }
    ]
  },
  {
    id: 'fade',
    name: 'Apply Fade',
    description: 'Add fade in/out effects',
    category: 'basic',
    parameters: [
      { name: 'fade_in_duration', type: 'number', default: 2, min: 0, max: 10, step: 0.1 },
      { name: 'fade_out_duration', type: 'number', default: 2, min: 0, max: 10, step: 0.1 }
    ]
  },
  {
    id: 'normalize',
    name: 'Normalize Audio',
    description: 'Normalize audio levels',
    category: 'basic',
    parameters: [
      { name: 'target_level_db', type: 'range', default: -3, min: -20, max: 0, step: 1 },
      { name: 'normalization_type', type: 'string', default: 'peak', options: ['peak', 'rms'] }
    ]
  },
  {
    id: 'silence',
    name: 'Remove Silence',
    description: 'Remove silent sections from audio',
    category: 'advanced',
    parameters: [
      { name: 'silence_threshold_db', type: 'range', default: -40, min: -60, max: -10, step: 1 },
      { name: 'min_silence_duration', type: 'number', default: 1, min: 0.1, max: 5, step: 0.1 }
    ]
  },
  {
    id: 'noise_reduction',
    name: 'Reduce Noise',
    description: 'Remove background noise',
    category: 'advanced',
    parameters: [
      { name: 'reduction_amount', type: 'range', default: 0.5, min: 0, max: 1, step: 0.1 },
      { name: 'noise_type', type: 'string', default: 'auto', options: ['auto', 'hum', 'hiss', 'click'] }
    ]
  }
];

export const AdvancedEditingTester: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const [selectedOperation, setSelectedOperation] = useState<EditingOperation>(editingOperations[0]);
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<Map<string, EditingResult>>(new Map());
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize parameters when operation changes
  React.useEffect(() => {
    const initialParams: Record<string, any> = {};
    selectedOperation.parameters.forEach(param => {
      initialParams[param.name] = param.default;
    });
    setParameters(initialParams);
  }, [selectedOperation]);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !file.type.startsWith('audio/')) {
      alert('Please select a valid audio file');
      return;
    }

    setSelectedFile(file);
    await uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('audio_file', file);

      const response = await fetch('http://127.0.0.1:5000/api/audio/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        setFileId(result.file_id);
        setUploadProgress(100);
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error}`);
    } finally {
      setIsUploading(false);
    }
  };

  const executeOperation = async (operation: EditingOperation, params: Record<string, any>) => {
    if (!fileId) {
      alert('Please upload an audio file first');
      return;
    }

    setIsProcessing(true);

    try {
      // Build the command based on operation and parameters
      let command = '';
      
      switch (operation.id) {
        case 'trim':
          command = `Cut from ${params.start_time} to ${params.end_time} seconds`;
          break;
        case 'volume':
          const sign = params.volume_change_db >= 0 ? '+' : '';
          command = `${params.volume_change_db >= 0 ? 'Increase' : 'Decrease'} volume by ${Math.abs(params.volume_change_db)}dB`;
          break;
        case 'fade':
          if (params.fade_in_duration > 0 && params.fade_out_duration > 0) {
            command = `Add ${params.fade_in_duration}s fade in and ${params.fade_out_duration}s fade out`;
          } else if (params.fade_in_duration > 0) {
            command = `Add ${params.fade_in_duration}s fade in`;
          } else if (params.fade_out_duration > 0) {
            command = `Add ${params.fade_out_duration}s fade out`;
          } else {
            command = 'Add fade effects';
          }
          break;
        case 'normalize':
          command = `Normalize audio to ${params.target_level_db}dB using ${params.normalization_type} method`;
          break;
        case 'silence':
          command = `Remove silence below ${params.silence_threshold_db}dB lasting more than ${params.min_silence_duration}s`;
          break;
        case 'noise_reduction':
          command = `Reduce ${params.noise_type} noise by ${Math.round(params.reduction_amount * 100)}%`;
          break;
        default:
          command = `Apply ${operation.name}`;
      }

      const response = await fetch('http://127.0.0.1:5000/api/audio/command/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: command,
          file_id: fileId,
          context: { parameters: params }
        }),
      });

      if (!response.ok) {
        throw new Error(`Operation failed: ${response.status}`);
      }

      const result = await response.json();
      setResults(prev => new Map(prev.set(operation.id, result)));

    } catch (error) {
      console.error('Operation error:', error);
      setResults(prev => new Map(prev.set(operation.id, {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      })));
    } finally {
      setIsProcessing(false);
    }
  };

  const runAllOperations = async () => {
    if (!fileId) {
      alert('Please upload an audio file first');
      return;
    }

    setResults(new Map());
    
    for (const operation of editingOperations) {
      // Use default parameters for each operation
      const defaultParams: Record<string, any> = {};
      operation.parameters.forEach(param => {
        defaultParams[param.name] = param.default;
      });
      
      await executeOperation(operation, defaultParams);
      
      // Small delay between operations
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  };

  const renderParameterControl = (param: EditingOperation['parameters'][0]) => {
    const value = parameters[param.name] ?? param.default;

    switch (param.type) {
      case 'range':
        return (
          <div className="space-y-2">
            <div className="flex justify-between">
              <label className="text-sm font-medium">{param.name.replace('_', ' ')}</label>
              <span className="text-sm text-muted-foreground">{value}</span>
            </div>
            <Slider
              value={[value]}
              onValueChange={(newValue) => setParameters(prev => ({ ...prev, [param.name]: newValue[0] }))}
              min={param.min}
              max={param.max}
              step={param.step}
              className="w-full"
            />
          </div>
        );

      case 'number':
        return (
          <div className="space-y-2">
            <label className="text-sm font-medium">{param.name.replace('_', ' ')}</label>
            <Input
              type="number"
              value={value}
              onChange={(e) => setParameters(prev => ({ ...prev, [param.name]: parseFloat(e.target.value) || 0 }))}
              min={param.min}
              max={param.max}
              step={param.step}
            />
          </div>
        );

      case 'string':
        if (param.options) {
          return (
            <div className="space-y-2">
              <label className="text-sm font-medium">{param.name.replace('_', ' ')}</label>
              <select
                value={value}
                onChange={(e) => setParameters(prev => ({ ...prev, [param.name]: e.target.value }))}
                className="w-full p-2 border rounded"
              >
                {param.options.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>
          );
        } else {
          return (
            <div className="space-y-2">
              <label className="text-sm font-medium">{param.name.replace('_', ' ')}</label>
              <Input
                type="text"
                value={value}
                onChange={(e) => setParameters(prev => ({ ...prev, [param.name]: e.target.value }))}
              />
            </div>
          );
        }

      default:
        return null;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'basic': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'advanced': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'effects': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'basic': return <Scissors className="h-4 w-4" />;
      case 'advanced': return <Settings className="h-4 w-4" />;
      case 'effects': return <Zap className="h-4 w-4" />;
      default: return <FileAudio className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* File Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileAudio className="h-5 w-5" />
            <span>Advanced Audio Editing Testing</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* File Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Test Audio File:</label>
            <div className="flex items-center space-x-2">
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileSelect}
                className="hidden"
              />
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="flex items-center space-x-2"
              >
                <Upload className="h-4 w-4" />
                <span>Select Audio File</span>
              </Button>
              {selectedFile && (
                <Badge variant="outline">
                  {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </Badge>
              )}
              {fileId && (
                <Badge variant="default">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Uploaded
                </Badge>
              )}
            </div>
            
            {isUploading && (
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Uploading...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="h-2" />
              </div>
            )}
          </div>

          {/* Batch Operations */}
          <div className="flex items-center space-x-2">
            <Button
              onClick={runAllOperations}
              disabled={!fileId || isProcessing}
              className="flex items-center space-x-2"
            >
              {isProcessing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              <span>Run All Operations</span>
            </Button>
            <Button
              variant="outline"
              onClick={() => setResults(new Map())}
              disabled={results.size === 0}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Clear Results
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Operations */}
        <Card>
          <CardHeader>
            <CardTitle>Audio Operations</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={selectedOperation.id} onValueChange={(value) => {
              const operation = editingOperations.find(op => op.id === value);
              if (operation) setSelectedOperation(operation);
            }}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="trim">Basic</TabsTrigger>
                <TabsTrigger value="silence">Advanced</TabsTrigger>
                <TabsTrigger value="effects">Effects</TabsTrigger>
              </TabsList>

              {/* Group operations by category for tabs */}
              <TabsContent value="trim" className="space-y-3">
                {editingOperations.filter(op => op.category === 'basic').map(operation => (
                  <div
                    key={operation.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedOperation.id === operation.id
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:bg-muted/50'
                    }`}
                    onClick={() => setSelectedOperation(operation)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getCategoryIcon(operation.category)}
                        <span className="font-medium">{operation.name}</span>
                      </div>
                      <Badge className={`text-xs ${getCategoryColor(operation.category)}`}>
                        {operation.category}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{operation.description}</p>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="silence" className="space-y-3">
                {editingOperations.filter(op => op.category === 'advanced').map(operation => (
                  <div
                    key={operation.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedOperation.id === operation.id
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:bg-muted/50'
                    }`}
                    onClick={() => setSelectedOperation(operation)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getCategoryIcon(operation.category)}
                        <span className="font-medium">{operation.name}</span>
                      </div>
                      <Badge className={`text-xs ${getCategoryColor(operation.category)}`}>
                        {operation.category}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{operation.description}</p>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="effects" className="space-y-3">
                <div className="text-center py-8 text-muted-foreground">
                  <Zap className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Effects operations coming soon!</p>
                  <p className="text-sm">EQ, Reverb, Delay, and Compression</p>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Parameters & Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{selectedOperation.name}</span>
              <Button
                onClick={() => executeOperation(selectedOperation, parameters)}
                disabled={!fileId || isProcessing}
                size="sm"
              >
                {isProcessing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Parameters */}
            <div className="space-y-3">
              <h4 className="font-medium">Parameters</h4>
              {selectedOperation.parameters.map(param => (
                <div key={param.name}>
                  {renderParameterControl(param)}
                </div>
              ))}
            </div>

            {/* Result */}
            {results.has(selectedOperation.id) && (
              <div className="space-y-2">
                <h4 className="font-medium">Result</h4>
                {(() => {
                  const result = results.get(selectedOperation.id)!;
                  return (
                    <div className={`p-3 rounded-lg border ${
                      result.success
                        ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                        : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                    }`}>
                      <div className="flex items-center space-x-2 mb-2">
                        {result.success ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="font-medium">
                          {result.success ? 'Success' : 'Failed'}
                        </span>
                      </div>
                      <p className="text-sm">
                        {result.message || result.error || 'No message'}
                      </p>
                      {result.processing_time && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Processing time: {result.processing_time.toFixed(2)}s
                        </p>
                      )}
                      {result.output_file && (
                        <div className="flex items-center space-x-2 mt-2">
                          <Button variant="outline" size="sm">
                            <Download className="h-3 w-3 mr-1" />
                            Download Result
                          </Button>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Results Summary */}
      {results.size > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Operations Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {Array.from(results.entries()).map(([operationId, result]) => {
                const operation = editingOperations.find(op => op.id === operationId);
                return (
                  <div
                    key={operationId}
                    className={`p-3 rounded-lg border ${
                      result.success
                        ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                        : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">{operation?.name}</span>
                      {result.success ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {result.message || result.error || 'No details'}
                    </p>
                    {result.processing_time && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {result.processing_time.toFixed(2)}s
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};