import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { 
  Brain, 
  Send, 
  Upload, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Loader2,
  FileAudio,
  Lightbulb,
  Settings,
  Play,
  Info
} from 'lucide-react';

interface InterpretationResult {
  valid: boolean;
  command_type: string;
  confidence: number;
  parameters: Array<{
    name: string;
    value: any;
    unit?: string;
    valid: boolean;
    error?: string;
  }>;
  warnings?: string[];
  errors?: string[];
  suggestions?: string[];
}

interface ExecutionResult {
  success: boolean;
  message: string;
  parsed_command?: {
    command_type: string;
    confidence: number;
    original_text: string;
  };
  suggestions?: string[];
  warnings?: string[];
  errors?: string[];
  processing_time?: number;
  output_file?: string;
  metadata?: any;
}

interface TestCommand {
  id: string;
  text: string;
  description: string;
  category: 'basic' | 'advanced' | 'complex';
  expectedType: string;
}

const testCommands: TestCommand[] = [
  // Basic Commands
  {
    id: 'trim-basic',
    text: 'Cut the first 30 seconds',
    description: 'Simple trim command',
    category: 'basic',
    expectedType: 'trim'
  },
  {
    id: 'volume-basic',
    text: 'Increase volume by 6dB',
    description: 'Basic volume adjustment',
    category: 'basic',
    expectedType: 'volume'
  },
  {
    id: 'fade-basic',
    text: 'Add 2-second fade in',
    description: 'Simple fade effect',
    category: 'basic',
    expectedType: 'fade'
  },
  {
    id: 'normalize-basic',
    text: 'Normalize the audio',
    description: 'Basic normalization',
    category: 'basic',
    expectedType: 'normalize'
  },
  
  // Advanced Commands
  {
    id: 'trim-advanced',
    text: 'Extract from 1:30 to 2:45',
    description: 'Time range extraction',
    category: 'advanced',
    expectedType: 'trim'
  },
  {
    id: 'noise-advanced',
    text: 'Remove background noise with 75% reduction',
    description: 'Noise reduction with parameters',
    category: 'advanced',
    expectedType: 'noise_reduction'
  },
  {
    id: 'eq-advanced',
    text: 'Boost bass frequencies by 3dB at 80Hz',
    description: 'EQ with specific parameters',
    category: 'advanced',
    expectedType: 'eq'
  },
  
  // Complex Commands
  {
    id: 'complex-1',
    text: 'Make the audio sound better and louder',
    description: 'Ambiguous command requiring clarification',
    category: 'complex',
    expectedType: 'unknown'
  },
  {
    id: 'complex-2',
    text: 'Clean up this recording and add some reverb',
    description: 'Multiple operations in one command',
    category: 'complex',
    expectedType: 'noise_reduction'
  }
];

export const CommandInterpreterTester: React.FC = () => {
  const [customCommand, setCustomCommand] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const [interpretationResult, setInterpretationResult] = useState<InterpretationResult | null>(null);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  
  const [isInterpreting, setIsInterpreting] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [testResults, setTestResults] = useState<Map<string, InterpretationResult>>(new Map());
  
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const interpretCommand = async (commandText: string) => {
    if (!commandText.trim()) return;

    setIsInterpreting(true);
    setInterpretationResult(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/audio/command/interpret', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: commandText,
          file_id: fileId,
          context: {}
        }),
      });

      if (!response.ok) {
        throw new Error(`Interpretation failed: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        setInterpretationResult(result.interpretation);
      } else {
        throw new Error(result.error || 'Interpretation failed');
      }
    } catch (error) {
      console.error('Interpretation error:', error);
      setInterpretationResult({
        valid: false,
        command_type: 'unknown',
        confidence: 0,
        parameters: [],
        errors: [error instanceof Error ? error.message : 'Unknown error']
      });
    } finally {
      setIsInterpreting(false);
    }
  };

  const executeCommand = async (commandText: string) => {
    if (!commandText.trim() || !fileId) {
      alert('Please select a file and enter a command');
      return;
    }

    setIsExecuting(true);
    setExecutionResult(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/audio/command/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: commandText,
          file_id: fileId,
          context: {}
        }),
      });

      if (!response.ok) {
        throw new Error(`Execution failed: ${response.status}`);
      }

      const result = await response.json();
      setExecutionResult(result);
    } catch (error) {
      console.error('Execution error:', error);
      setExecutionResult({
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        errors: [error instanceof Error ? error.message : 'Unknown error']
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const getSuggestions = async (partialCommand: string) => {
    if (!partialCommand.trim()) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/api/audio/command/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          partial_command: partialCommand,
          file_id: fileId,
          context: {}
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setSuggestions(result.suggestions || []);
        }
      }
    } catch (error) {
      console.error('Suggestions error:', error);
    }
  };

  const runTestCommand = async (testCommand: TestCommand) => {
    await interpretCommand(testCommand.text);
    
    if (interpretationResult) {
      setTestResults(prev => new Map(prev.set(testCommand.id, interpretationResult)));
    }
  };

  const runAllTests = async () => {
    setTestResults(new Map());
    
    for (const testCommand of testCommands) {
      await runTestCommand(testCommand);
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 dark:text-green-400';
    if (confidence >= 0.6) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'basic': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'advanced': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'complex': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* File Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Command Interpreter Testing</span>
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

          {/* Custom Command Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Custom Command:</label>
            <div className="flex space-x-2">
              <Input
                value={customCommand}
                onChange={(e) => {
                  setCustomCommand(e.target.value);
                  getSuggestions(e.target.value);
                }}
                placeholder="Enter audio editing command..."
                className="flex-1"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !isInterpreting) {
                    interpretCommand(customCommand);
                  }
                }}
              />
              <Button
                onClick={() => interpretCommand(customCommand)}
                disabled={isInterpreting || !customCommand.trim()}
              >
                {isInterpreting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Brain className="h-4 w-4" />
                )}
              </Button>
              <Button
                onClick={() => executeCommand(customCommand)}
                disabled={isExecuting || !customCommand.trim() || !fileId}
                variant="default"
              >
                {isExecuting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center space-x-1">
                <Lightbulb className="h-4 w-4" />
                <span>Suggestions:</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => setCustomCommand(suggestion)}
                    className="text-xs"
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Commands */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Test Commands</span>
              <Button onClick={runAllTests} disabled={isInterpreting} size="sm">
                Run All Tests
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {testCommands.map((testCommand) => {
                const result = testResults.get(testCommand.id);
                return (
                  <div
                    key={testCommand.id}
                    className="p-3 rounded-lg border border-border"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Badge className={`text-xs ${getCategoryColor(testCommand.category)}`}>
                        {testCommand.category}
                      </Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => runTestCommand(testCommand)}
                        disabled={isInterpreting}
                      >
                        {isInterpreting ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          <Brain className="h-3 w-3" />
                        )}
                      </Button>
                    </div>
                    
                    <div className="space-y-1">
                      <p className="font-medium text-sm">{testCommand.text}</p>
                      <p className="text-xs text-muted-foreground">
                        {testCommand.description}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Expected: {testCommand.expectedType}
                      </p>
                    </div>

                    {result && (
                      <div className="mt-2 pt-2 border-t">
                        <div className="flex items-center space-x-2 text-xs">
                          {result.valid ? (
                            <CheckCircle className="h-3 w-3 text-green-500" />
                          ) : (
                            <XCircle className="h-3 w-3 text-red-500" />
                          )}
                          <span>Type: {result.command_type}</span>
                          <span className={getConfidenceColor(result.confidence)}>
                            {(result.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        {result.errors && result.errors.length > 0 && (
                          <div className="text-xs text-red-600 mt-1">
                            {result.errors[0]}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Info className="h-5 w-5" />
              <span>Interpretation Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {interpretationResult ? (
              <div className="space-y-4">
                {/* Command Type & Confidence */}
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Command Type</h4>
                    <p className="text-sm text-muted-foreground">
                      {interpretationResult.command_type}
                    </p>
                  </div>
                  <div className="text-right">
                    <h4 className="font-medium">Confidence</h4>
                    <p className={`text-sm ${getConfidenceColor(interpretationResult.confidence)}`}>
                      {(interpretationResult.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Parameters */}
                {interpretationResult.parameters.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Parameters</h4>
                    <div className="space-y-2">
                      {interpretationResult.parameters.map((param, index) => (
                        <div
                          key={index}
                          className={`p-2 rounded border ${
                            param.valid 
                              ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                              : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-sm">{param.name}</span>
                            {param.valid ? (
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            ) : (
                              <XCircle className="h-4 w-4 text-red-500" />
                            )}
                          </div>
                          <div className="text-sm">
                            Value: {param.value} {param.unit && `(${param.unit})`}
                          </div>
                          {param.error && (
                            <div className="text-xs text-red-600 mt-1">
                              {param.error}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {interpretationResult.warnings && interpretationResult.warnings.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2 flex items-center space-x-1">
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                      <span>Warnings</span>
                    </h4>
                    <ul className="list-disc list-inside text-sm text-yellow-600 dark:text-yellow-400">
                      {interpretationResult.warnings.map((warning, index) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Errors */}
                {interpretationResult.errors && interpretationResult.errors.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2 flex items-center space-x-1">
                      <XCircle className="h-4 w-4 text-red-500" />
                      <span>Errors</span>
                    </h4>
                    <ul className="list-disc list-inside text-sm text-red-600 dark:text-red-400">
                      {interpretationResult.errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Suggestions */}
                {interpretationResult.suggestions && interpretationResult.suggestions.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2 flex items-center space-x-1">
                      <Lightbulb className="h-4 w-4 text-blue-500" />
                      <span>Suggestions</span>
                    </h4>
                    <div className="space-y-1">
                      {interpretationResult.suggestions.map((suggestion, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          onClick={() => setCustomCommand(suggestion)}
                          className="text-xs mr-2 mb-2"
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Enter a command to see interpretation results</p>
              </div>
            )}

            {/* Execution Results */}
            {executionResult && (
              <div className="mt-6 pt-6 border-t">
                <h4 className="font-medium mb-2 flex items-center space-x-1">
                  <Play className="h-4 w-4" />
                  <span>Execution Result</span>
                </h4>
                <div className={`p-3 rounded-lg border ${
                  executionResult.success
                    ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                    : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                }`}>
                  <div className="flex items-center space-x-2 mb-2">
                    {executionResult.success ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="font-medium">
                      {executionResult.success ? 'Success' : 'Failed'}
                    </span>
                  </div>
                  <p className="text-sm">{executionResult.message}</p>
                  {executionResult.processing_time && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Processing time: {executionResult.processing_time.toFixed(2)}s
                    </p>
                  )}
                  {executionResult.output_file && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Output: {executionResult.output_file}
                    </p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};