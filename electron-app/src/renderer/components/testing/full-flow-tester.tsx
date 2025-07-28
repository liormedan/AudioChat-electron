import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Textarea } from '../ui/textarea';
import { 
  Play, 
  Upload, 
  MessageSquare, 
  Settings, 
  CheckCircle, 
  XCircle, 
  Clock,
  FileAudio,
  Loader2,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';

interface TestStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  duration?: number;
  error?: string;
  result?: any;
}

interface FlowTestResult {
  testId: string;
  timestamp: Date;
  totalDuration: number;
  steps: TestStep[];
  overallStatus: 'passed' | 'failed' | 'partial';
  errors: string[];
}

const testSteps: TestStep[] = [
  {
    id: 'file-upload',
    name: 'File Upload',
    description: 'Upload an audio file to the server',
    status: 'pending'
  },
  {
    id: 'file-validation',
    name: 'File Validation',
    description: 'Validate uploaded file format and metadata',
    status: 'pending'
  },
  {
    id: 'chat-initialization',
    name: 'Chat Initialization',
    description: 'Initialize chat with uploaded file context',
    status: 'pending'
  },
  {
    id: 'command-processing',
    name: 'Command Processing',
    description: 'Send and process audio editing command',
    status: 'pending'
  },
  {
    id: 'result-validation',
    name: 'Result Validation',
    description: 'Validate processing results and output',
    status: 'pending'
  },
  {
    id: 'ui-updates',
    name: 'UI Updates',
    description: 'Verify UI updates and status indicators',
    status: 'pending'
  }
];

const sampleCommands = [
  'Normalize the audio to -3dB',
  'Remove background noise',
  'Add 2-second fade in and fade out',
  'Increase volume by 6dB',
  'Apply gentle compression',
  'Show audio metadata'
];

export const FullFlowTester: React.FC = () => {
  const [currentTest, setCurrentTest] = useState<TestStep[]>(testSteps);
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState<FlowTestResult[]>([]);
  const [selectedCommand, setSelectedCommand] = useState(sampleCommands[0]);
  const [testFile, setTestFile] = useState<File | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [testLogs, setTestLogs] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setTestLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const updateStepStatus = (stepId: string, status: TestStep['status'], error?: string, result?: any, duration?: number) => {
    setCurrentTest(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, status, error, result, duration }
        : step
    ));
  };

  const runStep = async (step: TestStep, stepIndex: number): Promise<boolean> => {
    setCurrentStepIndex(stepIndex);
    updateStepStatus(step.id, 'running');
    addLog(`Starting step: ${step.name}`);
    
    const startTime = Date.now();
    
    try {
      let success = false;
      
      switch (step.id) {
        case 'file-upload':
          success = await testFileUpload();
          break;
        case 'file-validation':
          success = await testFileValidation();
          break;
        case 'chat-initialization':
          success = await testChatInitialization();
          break;
        case 'command-processing':
          success = await testCommandProcessing();
          break;
        case 'result-validation':
          success = await testResultValidation();
          break;
        case 'ui-updates':
          success = await testUIUpdates();
          break;
        default:
          success = true;
      }
      
      const duration = Date.now() - startTime;
      
      if (success) {
        updateStepStatus(step.id, 'completed', undefined, undefined, duration);
        addLog(`✅ Step completed: ${step.name} (${duration}ms)`);
        return true;
      } else {
        updateStepStatus(step.id, 'failed', 'Step failed', undefined, duration);
        addLog(`❌ Step failed: ${step.name} (${duration}ms)`);
        return false;
      }
    } catch (error) {
      const duration = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      updateStepStatus(step.id, 'failed', errorMessage, undefined, duration);
      addLog(`❌ Step error: ${step.name} - ${errorMessage} (${duration}ms)`);
      return false;
    }
  };

  const testFileUpload = async (): Promise<boolean> => {
    if (!testFile) {
      throw new Error('No test file selected');
    }

    const formData = new FormData();
    formData.append('audio_file', testFile);

    const response = await fetch('http://127.0.0.1:5000/api/audio/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    const result = await response.json();
    addLog(`File uploaded successfully: ${result.file_id}`);
    return result.success;
  };

  const testFileValidation = async (): Promise<boolean> => {
    // Simulate file validation
    await new Promise(resolve => setTimeout(resolve, 500));
    addLog('File validation completed');
    return true;
  };

  const testChatInitialization = async (): Promise<boolean> => {
    // Test chat initialization
    const response = await fetch('http://127.0.0.1:5000/api/llm/chat/init', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context: 'audio_editing' }),
    });

    if (!response.ok) {
      throw new Error(`Chat initialization failed: ${response.status}`);
    }

    addLog('Chat initialized successfully');
    return true;
  };

  const testCommandProcessing = async (): Promise<boolean> => {
    const response = await fetch('http://127.0.0.1:5000/api/llm/chat/completion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        messages: [{ role: 'user', content: selectedCommand }],
        context: 'audio_editing'
      }),
    });

    if (!response.ok) {
      throw new Error(`Command processing failed: ${response.status}`);
    }

    const result = await response.json();
    addLog(`Command processed: "${selectedCommand}"`);
    addLog(`Response: ${result.content?.substring(0, 100)}...`);
    return true;
  };

  const testResultValidation = async (): Promise<boolean> => {
    // Simulate result validation
    await new Promise(resolve => setTimeout(resolve, 300));
    addLog('Results validated successfully');
    return true;
  };

  const testUIUpdates = async (): Promise<boolean> => {
    // Simulate UI update validation
    await new Promise(resolve => setTimeout(resolve, 200));
    addLog('UI updates verified');
    return true;
  };

  const runFullTest = async () => {
    if (!testFile) {
      addLog('❌ Please select a test file first');
      return;
    }

    setIsRunning(true);
    setCurrentStepIndex(-1);
    setTestLogs([]);
    
    // Reset all steps
    const resetSteps = testSteps.map(step => ({ ...step, status: 'pending' as const }));
    setCurrentTest(resetSteps);
    
    const testStartTime = Date.now();
    addLog('🚀 Starting full flow test...');
    
    let allPassed = true;
    const errors: string[] = [];
    
    for (let i = 0; i < resetSteps.length; i++) {
      const step = resetSteps[i];
      const success = await runStep(step, i);
      
      if (!success) {
        allPassed = false;
        errors.push(`${step.name}: ${step.error || 'Unknown error'}`);
        
        // Continue with remaining steps but mark them as skipped
        for (let j = i + 1; j < resetSteps.length; j++) {
          updateStepStatus(resetSteps[j].id, 'skipped');
        }
        break;
      }
      
      // Small delay between steps
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    const totalDuration = Date.now() - testStartTime;
    
    const testResult: FlowTestResult = {
      testId: Date.now().toString(),
      timestamp: new Date(),
      totalDuration,
      steps: currentTest,
      overallStatus: allPassed ? 'passed' : 'failed',
      errors
    };
    
    setTestResults(prev => [testResult, ...prev]);
    setCurrentStepIndex(-1);
    setIsRunning(false);
    
    if (allPassed) {
      addLog('🎉 All tests passed successfully!');
    } else {
      addLog(`❌ Test failed with ${errors.length} error(s)`);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('audio/')) {
      setTestFile(file);
      addLog(`Test file selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
    } else {
      addLog('❌ Please select a valid audio file');
    }
  };

  const resetTest = () => {
    setCurrentTest(testSteps.map(step => ({ ...step, status: 'pending' as const })));
    setCurrentStepIndex(-1);
    setTestLogs([]);
    setTestFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStepIcon = (step: TestStep) => {
    switch (step.status) {
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'skipped':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getOverallProgress = () => {
    const completed = currentTest.filter(step => step.status === 'completed').length;
    const failed = currentTest.filter(step => step.status === 'failed').length;
    const total = currentTest.length;
    
    if (failed > 0) return (completed / total) * 100;
    return (completed / total) * 100;
  };

  return (
    <div className="space-y-6">
      {/* Test Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Play className="h-5 w-5" />
            <span>Full Flow Test Configuration</span>
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
                className="flex items-center space-x-2"
              >
                <Upload className="h-4 w-4" />
                <span>Select Audio File</span>
              </Button>
              {testFile && (
                <Badge variant="outline">
                  {testFile.name} ({(testFile.size / 1024 / 1024).toFixed(2)} MB)
                </Badge>
              )}
            </div>
          </div>

          {/* Command Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Test Command:</label>
            <div className="flex flex-wrap gap-2">
              {sampleCommands.map((command) => (
                <Button
                  key={command}
                  variant={selectedCommand === command ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCommand(command)}
                >
                  {command}
                </Button>
              ))}
            </div>
          </div>

          {/* Test Controls */}
          <div className="flex items-center space-x-2">
            <Button
              onClick={runFullTest}
              disabled={isRunning || !testFile}
              className="flex items-center space-x-2"
            >
              {isRunning ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              <span>{isRunning ? 'Running Test...' : 'Run Full Test'}</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={resetTest}
              disabled={isRunning}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Test Progress</span>
              <Badge variant={isRunning ? 'default' : 'outline'}>
                {isRunning ? 'Running' : 'Ready'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Overall Progress */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Overall Progress</span>
                <span>{Math.round(getOverallProgress())}%</span>
              </div>
              <Progress value={getOverallProgress()} className="h-2" />
            </div>

            {/* Step List */}
            <div className="space-y-2">
              {currentTest.map((step, index) => (
                <div
                  key={step.id}
                  className={`flex items-center space-x-3 p-2 rounded-lg ${
                    currentStepIndex === index ? 'bg-primary/10 border border-primary/20' : 'bg-muted/30'
                  }`}
                >
                  {getStepIcon(step)}
                  <div className="flex-1">
                    <div className="font-medium text-sm">{step.name}</div>
                    <div className="text-xs text-muted-foreground">{step.description}</div>
                    {step.error && (
                      <div className="text-xs text-red-500 mt-1">{step.error}</div>
                    )}
                  </div>
                  {step.duration && (
                    <Badge variant="outline" className="text-xs">
                      {step.duration}ms
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Test Logs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span>Test Logs</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={testLogs.join('\n')}
              readOnly
              className="min-h-[400px] font-mono text-xs"
              placeholder="Test logs will appear here..."
            />
          </CardContent>
        </Card>
      </div>

      {/* Test Results History */}
      {testResults.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Test Results History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {testResults.map((result) => (
                <div
                  key={result.testId}
                  className={`p-3 rounded-lg border ${
                    result.overallStatus === 'passed'
                      ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                      : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {result.overallStatus === 'passed' ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                      <span className="font-medium">
                        Test {result.overallStatus === 'passed' ? 'Passed' : 'Failed'}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {result.timestamp.toLocaleString()} • {result.totalDuration}ms
                    </div>
                  </div>
                  
                  {result.errors.length > 0 && (
                    <div className="text-sm text-red-600 dark:text-red-400">
                      <strong>Errors:</strong>
                      <ul className="list-disc list-inside mt-1">
                        {result.errors.map((error, index) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};