import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { 
  Play, 
  Loader2, 
  CheckCircle, 
  XCircle, 
  FileAudio,
  Zap,
  Clock,
  MessageSquare
} from 'lucide-react';

interface TestCommand {
  id: string;
  command: string;
  description: string;
  category: 'basic' | 'advanced' | 'creative';
  expectedBehavior: string;
}

interface TestResult {
  command: string;
  response: string;
  success: boolean;
  responseTime: number;
  timestamp: Date;
  error?: string;
}

const sampleCommands: TestCommand[] = [
  {
    id: 'normalize-audio',
    command: 'Normalize the audio to -3dB',
    description: 'Basic audio normalization command',
    category: 'basic',
    expectedBehavior: 'Should normalize audio levels to -3dB peak'
  },
  {
    id: 'remove-noise',
    command: 'Remove background noise from this recording',
    description: 'Noise reduction processing',
    category: 'basic',
    expectedBehavior: 'Should apply noise reduction algorithms'
  },
  {
    id: 'fade-effects',
    command: 'Add a 2-second fade in and 3-second fade out',
    description: 'Apply fade effects to audio',
    category: 'basic',
    expectedBehavior: 'Should add fade in/out with specified durations'
  },
  {
    id: 'eq-boost',
    command: 'Boost the bass frequencies by 3dB around 80Hz',
    description: 'EQ adjustment for bass enhancement',
    category: 'advanced',
    expectedBehavior: 'Should apply EQ boost at specified frequency'
  },
  {
    id: 'compression',
    command: 'Apply gentle compression with 3:1 ratio and slow attack',
    description: 'Dynamic range compression',
    category: 'advanced',
    expectedBehavior: 'Should apply compression with specified parameters'
  },
  {
    id: 'stereo-width',
    command: 'Widen the stereo image by 20% without phase issues',
    description: 'Stereo field manipulation',
    category: 'advanced',
    expectedBehavior: 'Should enhance stereo width while maintaining mono compatibility'
  },
  {
    id: 'creative-reverb',
    command: 'Add a dreamy hall reverb with 2.5 second decay',
    description: 'Creative reverb application',
    category: 'creative',
    expectedBehavior: 'Should add reverb with artistic characteristics'
  },
  {
    id: 'vintage-warmth',
    command: 'Give this audio a vintage analog warmth',
    description: 'Vintage character processing',
    category: 'creative',
    expectedBehavior: 'Should apply vintage-style processing for warmth'
  },
  {
    id: 'rhythmic-gate',
    command: 'Create a rhythmic gating effect synced to 120 BPM',
    description: 'Rhythmic audio processing',
    category: 'creative',
    expectedBehavior: 'Should apply tempo-synced gating effect'
  }
];

export const AudioCommandTester: React.FC = () => {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [currentTest, setCurrentTest] = useState<string | null>(null);
  const [customCommand, setCustomCommand] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const runSingleTest = async (command: TestCommand) => {
    setIsRunningTest(true);
    setCurrentTest(command.id);
    
    const startTime = Date.now();
    
    try {
      const response = await fetch('/api/llm/test-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          command: command.command,
          context: 'audio_editing'
        }),
      });

      const responseTime = Date.now() - startTime;
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      const testResult: TestResult = {
        command: command.command,
        response: result.response || result.content || 'No response received',
        success: true,
        responseTime,
        timestamp: new Date()
      };

      setTestResults(prev => [testResult, ...prev]);
      
    } catch (error) {
      const testResult: TestResult = {
        command: command.command,
        response: '',
        success: false,
        responseTime: Date.now() - startTime,
        timestamp: new Date(),
        error: error instanceof Error ? error.message : 'Unknown error'
      };

      setTestResults(prev => [testResult, ...prev]);
    } finally {
      setIsRunningTest(false);
      setCurrentTest(null);
    }
  };

  const runCustomTest = async () => {
    if (!customCommand.trim()) return;
    
    const customTestCommand: TestCommand = {
      id: 'custom',
      command: customCommand,
      description: 'Custom test command',
      category: 'basic',
      expectedBehavior: 'User-defined behavior'
    };
    
    await runSingleTest(customTestCommand);
    setCustomCommand('');
  };

  const runAllTests = async () => {
    const commandsToTest = selectedCategory === 'all' 
      ? sampleCommands 
      : sampleCommands.filter(cmd => cmd.category === selectedCategory);
    
    for (const command of commandsToTest) {
      await runSingleTest(command);
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  };

  const clearResults = () => {
    setTestResults([]);
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'basic': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'advanced': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'creative': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const filteredCommands = selectedCategory === 'all' 
    ? sampleCommands 
    : sampleCommands.filter(cmd => cmd.category === selectedCategory);

  return (
    <div className="space-y-6">
      {/* Test Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>Audio Command Testing</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Category Filter */}
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">Category:</span>
            <div className="flex space-x-2">
              {['all', 'basic', 'advanced', 'creative'].map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </Button>
              ))}
            </div>
          </div>

          {/* Custom Command Test */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Custom Command Test:</label>
            <div className="flex space-x-2">
              <Input
                value={customCommand}
                onChange={(e) => setCustomCommand(e.target.value)}
                placeholder="Enter a custom audio editing command..."
                className="flex-1"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !isRunningTest) {
                    runCustomTest();
                  }
                }}
              />
              <Button 
                onClick={runCustomTest} 
                disabled={isRunningTest || !customCommand.trim()}
              >
                {isRunningTest && currentTest === 'custom' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Batch Test Controls */}
          <div className="flex items-center justify-between">
            <Button 
              onClick={runAllTests} 
              disabled={isRunningTest}
              className="flex items-center space-x-2"
            >
              {isRunningTest ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              <span>Run All Tests ({filteredCommands.length})</span>
            </Button>
            
            <Button 
              variant="outline" 
              onClick={clearResults}
              disabled={testResults.length === 0}
            >
              Clear Results
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sample Commands */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileAudio className="h-5 w-5" />
              <span>Sample Commands</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {filteredCommands.map((command) => (
              <div
                key={command.id}
                className="p-3 rounded-lg border border-border"
              >
                <div className="flex items-center justify-between mb-2">
                  <Badge className={`text-xs ${getCategoryColor(command.category)}`}>
                    {command.category}
                  </Badge>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => runSingleTest(command)}
                    disabled={isRunningTest}
                  >
                    {isRunningTest && currentTest === command.id ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      <Play className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <div className="space-y-1">
                  <p className="font-medium text-sm">{command.command}</p>
                  <p className="text-xs text-muted-foreground">
                    {command.description}
                  </p>
                  <p className="text-xs text-muted-foreground italic">
                    Expected: {command.expectedBehavior}
                  </p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Test Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5" />
                <span>Test Results</span>
              </div>
              <Badge variant="outline">
                {testResults.length} tests
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {testResults.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No test results yet</p>
                <p className="text-sm">Run some commands to see results here</p>
              </div>
            ) : (
              <div className="space-y-4 max-h-[600px] overflow-y-auto">
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
                        <span className="text-sm font-medium">
                          {result.success ? 'Success' : 'Failed'}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>{result.responseTime}ms</span>
                        <span>{result.timestamp.toLocaleTimeString()}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <p className="text-sm font-medium">Command:</p>
                        <p className="text-sm text-muted-foreground italic">
                          "{result.command}"
                        </p>
                      </div>
                      
                      {result.success ? (
                        <div>
                          <p className="text-sm font-medium">Response:</p>
                          <Textarea
                            value={result.response}
                            readOnly
                            className="text-xs mt-1 min-h-[80px]"
                          />
                        </div>
                      ) : (
                        <div>
                          <p className="text-sm font-medium text-red-600">Error:</p>
                          <p className="text-sm text-red-600">
                            {result.error || 'Unknown error occurred'}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};