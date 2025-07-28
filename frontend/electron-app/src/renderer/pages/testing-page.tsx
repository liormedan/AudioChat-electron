import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  TestTube, 
  AlertTriangle, 
  Palette, 
  BookOpen,
  CheckCircle,
  Settings,
  Zap,
  FileAudio
} from 'lucide-react';
import { FullFlowTester } from '../components/testing/full-flow-tester';
import { ErrorHandler } from '../components/testing/error-handler';
import { UXImprovements } from '../components/testing/ux-improvements';
import { CommandDocumentation } from '../components/testing/command-documentation';
import { CommandInterpreterTester } from '../components/testing/command-interpreter-tester';
import { AdvancedEditingTester } from '../components/testing/advanced-editing-tester';
import { InteractiveAudioEditor } from '../components/audio/interactive-audio-editor';

export const TestingPage: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight flex items-center space-x-2">
          <TestTube className="h-8 w-8" />
          <span>Testing & Quality Assurance</span>
        </h1>
        <p className="text-muted-foreground">
          Comprehensive testing tools, error handling, UX improvements, and documentation
        </p>
      </div>

      {/* Testing Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Flow Tests</CardTitle>
            <TestTube className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              6
            </div>
            <p className="text-xs text-muted-foreground">
              End-to-end test steps
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Scenarios</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              12
            </div>
            <p className="text-xs text-muted-foreground">
              Error handling tests
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">UX Improvements</CardTitle>
            <Palette className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              16
            </div>
            <p className="text-xs text-muted-foreground">
              Enhancement items
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documented Commands</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              50+
            </div>
            <p className="text-xs text-muted-foreground">
              Audio commands
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Testing Tabs */}
      <Tabs defaultValue="command-interpreter" className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="command-interpreter" className="flex items-center space-x-2">
            <Settings className="h-4 w-4" />
            <span>Command Interpreter</span>
          </TabsTrigger>
          <TabsTrigger value="advanced-editing" className="flex items-center space-x-2">
            <Zap className="h-4 w-4" />
            <span>Advanced Editing</span>
          </TabsTrigger>
          <TabsTrigger value="interactive-editor" className="flex items-center space-x-2">
            <FileAudio className="h-4 w-4" />
            <span>Interactive Editor</span>
          </TabsTrigger>
          <TabsTrigger value="flow-testing" className="flex items-center space-x-2">
            <TestTube className="h-4 w-4" />
            <span>Flow Testing</span>
          </TabsTrigger>
          <TabsTrigger value="error-handling" className="flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4" />
            <span>Error Handling</span>
          </TabsTrigger>
          <TabsTrigger value="ux-improvements" className="flex items-center space-x-2">
            <Palette className="h-4 w-4" />
            <span>UX Improvements</span>
          </TabsTrigger>
          <TabsTrigger value="documentation" className="flex items-center space-x-2">
            <BookOpen className="h-4 w-4" />
            <span>Documentation</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="command-interpreter" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Command Interpreter Testing</span>
              </CardTitle>
              <CardDescription>
                Test the natural language command interpretation engine
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CommandInterpreterTester />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced-editing" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>Advanced Audio Editing</span>
              </CardTitle>
              <CardDescription>
                Test advanced audio editing functions with pydub and librosa
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AdvancedEditingTester />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="interactive-editor" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileAudio className="h-5 w-5" />
                <span>Interactive Audio Editor</span>
              </CardTitle>
              <CardDescription>
                Interactive audio editor with preview, history, and undo/redo functionality
              </CardDescription>
            </CardHeader>
            <CardContent>
              <InteractiveAudioEditor />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="flow-testing" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TestTube className="h-5 w-5" />
                <span>Full Flow Testing</span>
              </CardTitle>
              <CardDescription>
                Test the complete user journey from file upload to audio processing
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FullFlowTester />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="error-handling" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5" />
                <span>Error Handling & Recovery</span>
              </CardTitle>
              <CardDescription>
                Test error scenarios and recovery mechanisms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ErrorHandler />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ux-improvements" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Palette className="h-5 w-5" />
                <span>UX Improvements & Settings</span>
              </CardTitle>
              <CardDescription>
                User experience enhancements and customization options
              </CardDescription>
            </CardHeader>
            <CardContent>
              <UXImprovements />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documentation" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5" />
                <span>Command Documentation</span>
              </CardTitle>
              <CardDescription>
                Comprehensive documentation for all audio commands
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CommandDocumentation />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Testing Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5" />
            <span>Testing Summary</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium flex items-center space-x-2">
                <TestTube className="h-4 w-4 text-blue-500" />
                <span>Flow Testing</span>
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• File upload validation</li>
                <li>• Chat initialization</li>
                <li>• Command processing</li>
                <li>• Result validation</li>
                <li>• UI state management</li>
                <li>• Error recovery</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4 text-orange-500" />
                <span>Error Scenarios</span>
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Network timeouts</li>
                <li>• Invalid file formats</li>
                <li>• Server unavailability</li>
                <li>• Ambiguous commands</li>
                <li>• Processing failures</li>
                <li>• Memory limitations</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium flex items-center space-x-2">
                <Palette className="h-4 w-4 text-purple-500" />
                <span>UX Features</span>
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Dark mode support</li>
                <li>• Accessibility options</li>
                <li>• Performance metrics</li>
                <li>• Customizable settings</li>
                <li>• Progress indicators</li>
                <li>• Keyboard shortcuts</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium flex items-center space-x-2">
                <BookOpen className="h-4 w-4 text-green-500" />
                <span>Documentation</span>
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Command syntax</li>
                <li>• Parameter details</li>
                <li>• Usage examples</li>
                <li>• Best practices</li>
                <li>• Related commands</li>
                <li>• Export options</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};