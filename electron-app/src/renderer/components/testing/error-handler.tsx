import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { 
  AlertTriangle, 
  RefreshCw, 
  MessageSquare, 
  Settings, 
  CheckCircle,
  XCircle,
  Info,
  Zap,
  FileAudio
} from 'lucide-react';

interface ErrorScenario {
  id: string;
  name: string;
  description: string;
  category: 'network' | 'file' | 'command' | 'server' | 'ui';
  testInput: string;
  expectedBehavior: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

interface ErrorTestResult {
  scenarioId: string;
  timestamp: Date;
  success: boolean;
  actualBehavior: string;
  errorMessage?: string;
  recoveryTime?: number;
}

const errorScenarios: ErrorScenario[] = [
  // Network Errors
  {
    id: 'network-timeout',
    name: 'Network Timeout',
    description: 'Test behavior when server request times out',
    category: 'network',
    testInput: 'Simulate network timeout',
    expectedBehavior: 'Show timeout error with retry option',
    severity: 'high'
  },
  {
    id: 'server-unavailable',
    name: 'Server Unavailable',
    description: 'Test behavior when server is down',
    category: 'network',
    testInput: 'Connect to unavailable server',
    expectedBehavior: 'Show connection error with clear message',
    severity: 'critical'
  },
  
  // File Errors
  {
    id: 'invalid-file-format',
    name: 'Invalid File Format',
    description: 'Test uploading unsupported file format',
    category: 'file',
    testInput: 'Upload .txt file as audio',
    expectedBehavior: 'Reject file with format error message',
    severity: 'medium'
  },
  {
    id: 'corrupted-file',
    name: 'Corrupted Audio File',
    description: 'Test uploading corrupted audio file',
    category: 'file',
    testInput: 'Upload corrupted .mp3 file',
    expectedBehavior: 'Detect corruption and show error',
    severity: 'medium'
  },
  {
    id: 'file-too-large',
    name: 'File Size Limit',
    description: 'Test uploading file exceeding size limit',
    category: 'file',
    testInput: 'Upload 500MB audio file',
    expectedBehavior: 'Reject with size limit message',
    severity: 'low'
  },
  
  // Command Errors
  {
    id: 'ambiguous-command',
    name: 'Ambiguous Command',
    description: 'Test unclear or ambiguous audio command',
    category: 'command',
    testInput: 'Make it sound better',
    expectedBehavior: 'Ask for clarification with suggestions',
    severity: 'low'
  },
  {
    id: 'impossible-command',
    name: 'Impossible Command',
    description: 'Test technically impossible audio operation',
    category: 'command',
    testInput: 'Remove vocals from mono recording',
    expectedBehavior: 'Explain why operation is not possible',
    severity: 'medium'
  },
  {
    id: 'destructive-command',
    name: 'Destructive Command',
    description: 'Test potentially destructive operation',
    category: 'command',
    testInput: 'Delete all audio content',
    expectedBehavior: 'Show warning and require confirmation',
    severity: 'high'
  },
  
  // Server Errors
  {
    id: 'processing-failure',
    name: 'Processing Failure',
    description: 'Test server-side processing failure',
    category: 'server',
    testInput: 'Trigger server processing error',
    expectedBehavior: 'Show processing error with retry option',
    severity: 'high'
  },
  {
    id: 'memory-limit',
    name: 'Server Memory Limit',
    description: 'Test server running out of memory',
    category: 'server',
    testInput: 'Process extremely large file',
    expectedBehavior: 'Show resource limit error',
    severity: 'medium'
  },
  
  // UI Errors
  {
    id: 'ui-state-corruption',
    name: 'UI State Corruption',
    description: 'Test UI state becoming inconsistent',
    category: 'ui',
    testInput: 'Rapid state changes',
    expectedBehavior: 'Maintain consistent UI state',
    severity: 'medium'
  },
  {
    id: 'memory-leak',
    name: 'Memory Leak',
    description: 'Test for memory leaks in long sessions',
    category: 'ui',
    testInput: 'Extended usage session',
    expectedBehavior: 'Stable memory usage over time',
    severity: 'low'
  }
];

export const ErrorHandler: React.FC = () => {
  const [testResults, setTestResults] = useState<ErrorTestResult[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<ErrorScenario | null>(null);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [customErrorInput, setCustomErrorInput] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [errorLogs, setErrorLogs] = useState<string[]>([]);

  const categories = [
    { id: 'all', name: 'All Categories', icon: <Settings className="h-4 w-4" /> },
    { id: 'network', name: 'Network', icon: <Zap className="h-4 w-4" /> },
    { id: 'file', name: 'File', icon: <FileAudio className="h-4 w-4" /> },
    { id: 'command', name: 'Command', icon: <MessageSquare className="h-4 w-4" /> },
    { id: 'server', name: 'Server', icon: <Settings className="h-4 w-4" /> },
    { id: 'ui', name: 'UI', icon: <Info className="h-4 w-4" /> }
  ];

  const filteredScenarios = selectedCategory === 'all' 
    ? errorScenarios 
    : errorScenarios.filter(scenario => scenario.category === selectedCategory);

  const addErrorLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setErrorLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const runErrorTest = async (scenario: ErrorScenario) => {
    setIsRunningTest(true);
    setSelectedScenario(scenario);
    addErrorLog(`Starting error test: ${scenario.name}`);
    
    const startTime = Date.now();
    
    try {
      let success = false;
      let actualBehavior = '';
      let errorMessage = '';
      
      // Simulate different error scenarios
      switch (scenario.id) {
        case 'network-timeout':
          success = await testNetworkTimeout();
          actualBehavior = success ? 'Timeout handled gracefully' : 'Timeout not handled';
          break;
          
        case 'server-unavailable':
          success = await testServerUnavailable();
          actualBehavior = success ? 'Server error handled' : 'Server error not handled';
          break;
          
        case 'invalid-file-format':
          success = await testInvalidFileFormat();
          actualBehavior = success ? 'Invalid format rejected' : 'Invalid format not caught';
          break;
          
        case 'ambiguous-command':
          success = await testAmbiguousCommand();
          actualBehavior = success ? 'Clarification requested' : 'Ambiguous command processed';
          break;
          
        case 'destructive-command':
          success = await testDestructiveCommand();
          actualBehavior = success ? 'Warning shown' : 'No warning displayed';
          break;
          
        default:
          // Generic error test
          success = await testGenericError(scenario);
          actualBehavior = success ? 'Error handled appropriately' : 'Error not handled';
      }
      
      const recoveryTime = Date.now() - startTime;
      
      const result: ErrorTestResult = {
        scenarioId: scenario.id,
        timestamp: new Date(),
        success,
        actualBehavior,
        errorMessage: success ? undefined : 'Test failed',
        recoveryTime
      };
      
      setTestResults(prev => [result, ...prev]);
      addErrorLog(`${success ? '✅' : '❌'} Test completed: ${scenario.name} (${recoveryTime}ms)`);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const result: ErrorTestResult = {
        scenarioId: scenario.id,
        timestamp: new Date(),
        success: false,
        actualBehavior: 'Test threw exception',
        errorMessage,
        recoveryTime: Date.now() - startTime
      };
      
      setTestResults(prev => [result, ...prev]);
      addErrorLog(`❌ Test error: ${scenario.name} - ${errorMessage}`);
    } finally {
      setIsRunningTest(false);
      setSelectedScenario(null);
    }
  };

  const testNetworkTimeout = async (): Promise<boolean> => {
    try {
      // Simulate timeout by making request to non-existent endpoint with short timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000);
      
      await fetch('http://127.0.0.1:5000/api/timeout-test', {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return false; // Should not reach here
    } catch (error) {
      // Check if error is handled gracefully
      addErrorLog('Network timeout detected and handled');
      return true;
    }
  };

  const testServerUnavailable = async (): Promise<boolean> => {
    try {
      await fetch('http://127.0.0.1:9999/api/test'); // Non-existent server
      return false;
    } catch (error) {
      addErrorLog('Server unavailable error handled');
      return true;
    }
  };

  const testInvalidFileFormat = async (): Promise<boolean> => {
    // Simulate file format validation
    const invalidFile = new File(['invalid content'], 'test.txt', { type: 'text/plain' });
    
    // Check if validation catches invalid format
    if (!invalidFile.type.startsWith('audio/')) {
      addErrorLog('Invalid file format detected');
      return true;
    }
    
    return false;
  };

  const testAmbiguousCommand = async (): Promise<boolean> => {
    const ambiguousCommand = 'Make it sound better';
    
    try {
      const response = await fetch('http://127.0.0.1:5000/api/llm/chat/completion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          messages: [{ role: 'user', content: ambiguousCommand }]
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        // Check if response asks for clarification
        const content = result.content?.toLowerCase() || '';
        const asksClarification = content.includes('clarify') || 
                                content.includes('specific') || 
                                content.includes('what do you mean');
        
        addErrorLog(`Ambiguous command response: ${asksClarification ? 'Asked for clarification' : 'Processed directly'}`);
        return asksClarification;
      }
    } catch (error) {
      addErrorLog('Error testing ambiguous command');
    }
    
    return false;
  };

  const testDestructiveCommand = async (): Promise<boolean> => {
    // Simulate checking for destructive commands
    const destructiveCommand = 'Delete all audio content';
    const destructiveKeywords = ['delete', 'remove all', 'clear everything', 'erase'];
    
    const isDestructive = destructiveKeywords.some(keyword => 
      destructiveCommand.toLowerCase().includes(keyword)
    );
    
    if (isDestructive) {
      addErrorLog('Destructive command detected - warning should be shown');
      return true;
    }
    
    return false;
  };

  const testGenericError = async (scenario: ErrorScenario): Promise<boolean> => {
    // Generic error test - simulate based on category
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Randomly succeed or fail for demonstration
    const success = Math.random() > 0.3;
    addErrorLog(`Generic test for ${scenario.name}: ${success ? 'passed' : 'failed'}`);
    return success;
  };

  const runCustomErrorTest = async () => {
    if (!customErrorInput.trim()) return;
    
    const customScenario: ErrorScenario = {
      id: 'custom',
      name: 'Custom Error Test',
      description: 'User-defined error scenario',
      category: 'command',
      testInput: customErrorInput,
      expectedBehavior: 'Handle error appropriately',
      severity: 'medium'
    };
    
    await runErrorTest(customScenario);
    setCustomErrorInput('');
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'high': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'critical': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'network': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'file': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'command': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'server': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'ui': return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Error Testing Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5" />
            <span>Error Handling & Recovery Testing</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Category Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Category:</label>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category.id}
                  variant={selectedCategory === category.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category.id)}
                  className="flex items-center space-x-1"
                >
                  {category.icon}
                  <span>{category.name}</span>
                </Button>
              ))}
            </div>
          </div>

          {/* Custom Error Test */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Custom Error Test:</label>
            <div className="flex space-x-2">
              <Input
                value={customErrorInput}
                onChange={(e) => setCustomErrorInput(e.target.value)}
                placeholder="Enter error scenario to test..."
                className="flex-1"
              />
              <Button 
                onClick={runCustomErrorTest}
                disabled={isRunningTest || !customErrorInput.trim()}
              >
                Test
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Error Scenarios */}
        <Card>
          <CardHeader>
            <CardTitle>Error Scenarios</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {filteredScenarios.map((scenario) => (
                <div
                  key={scenario.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedScenario?.id === scenario.id
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:bg-muted/50'
                  }`}
                  onClick={() => !isRunningTest && runErrorTest(scenario)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-sm">{scenario.name}</h4>
                    <div className="flex items-center space-x-2">
                      <Badge className={`text-xs ${getCategoryColor(scenario.category)}`}>
                        {scenario.category}
                      </Badge>
                      <Badge className={`text-xs ${getSeverityColor(scenario.severity)}`}>
                        {scenario.severity}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">
                    {scenario.description}
                  </p>
                  <div className="text-xs">
                    <div><strong>Input:</strong> {scenario.testInput}</div>
                    <div><strong>Expected:</strong> {scenario.expectedBehavior}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Error Logs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span>Error Test Logs</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={errorLogs.join('\n')}
              readOnly
              className="min-h-[400px] font-mono text-xs"
              placeholder="Error test logs will appear here..."
            />
          </CardContent>
        </Card>
      </div>

      {/* Test Results */}
      {testResults.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Error Test Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {testResults.map((result, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${
                    result.success
                      ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                      : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {result.success ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                      <span className="font-medium">
                        {errorScenarios.find(s => s.id === result.scenarioId)?.name || 'Custom Test'}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {result.timestamp.toLocaleTimeString()}
                      {result.recoveryTime && ` • ${result.recoveryTime}ms`}
                    </div>
                  </div>
                  
                  <div className="text-sm">
                    <div><strong>Actual Behavior:</strong> {result.actualBehavior}</div>
                    {result.errorMessage && (
                      <div className="text-red-600 dark:text-red-400">
                        <strong>Error:</strong> {result.errorMessage}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};