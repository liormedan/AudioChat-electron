import React from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { 
  Volume2, 
  Scissors, 
  Filter, 
  Zap, 
  TrendingUp,
  Clock,
  FileAudio
} from 'lucide-react';

interface AudioCommandSuggestionsProps {
  onCommandSelect: (command: string) => void;
  selectedFile?: { name: string; duration?: string | undefined } | null;
  isProcessing?: boolean;
}

interface CommandCategory {
  title: string;
  icon: React.ReactNode;
  commands: {
    text: string;
    description: string;
    category: 'basic' | 'advanced' | 'analysis';
  }[];
}

const commandCategories: CommandCategory[] = [
  {
    title: 'Volume & Dynamics',
    icon: <Volume2 className="h-4 w-4" />,
    commands: [
      { text: 'Normalize audio levels', description: 'Balance overall volume', category: 'basic' },
      { text: 'Increase volume by 20%', description: 'Boost audio level', category: 'basic' },
      { text: 'Add compression', description: 'Even out dynamics', category: 'advanced' },
      { text: 'Remove clipping', description: 'Fix distorted audio', category: 'advanced' },
    ]
  },
  {
    title: 'Editing & Trimming',
    icon: <Scissors className="h-4 w-4" />,
    commands: [
      { text: 'Cut first 30 seconds', description: 'Remove beginning', category: 'basic' },
      { text: 'Extract middle 2 minutes', description: 'Get specific section', category: 'basic' },
      { text: 'Add fade in and fade out', description: 'Smooth transitions', category: 'basic' },
      { text: 'Split at silence points', description: 'Auto-segment audio', category: 'advanced' },
    ]
  },
  {
    title: 'Noise & Cleanup',
    icon: <Filter className="h-4 w-4" />,
    commands: [
      { text: 'Remove background noise', description: 'Clean up audio', category: 'basic' },
      { text: 'Apply low-pass filter', description: 'Remove high frequencies', category: 'advanced' },
      { text: 'Remove hum and buzz', description: 'Fix electrical noise', category: 'advanced' },
      { text: 'Enhance voice clarity', description: 'Improve speech', category: 'basic' },
    ]
  },
  {
    title: 'Analysis & Info',
    icon: <TrendingUp className="h-4 w-4" />,
    commands: [
      { text: 'Show audio metadata', description: 'File information', category: 'analysis' },
      { text: 'Analyze frequency spectrum', description: 'View frequencies', category: 'analysis' },
      { text: 'Detect tempo and key', description: 'Musical analysis', category: 'analysis' },
      { text: 'Find loudest sections', description: 'Peak detection', category: 'analysis' },
    ]
  }
];

export const AudioCommandSuggestions: React.FC<AudioCommandSuggestionsProps> = ({
  onCommandSelect,
  selectedFile,
  isProcessing = false
}) => {
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'basic': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'advanced': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'analysis': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  if (!selectedFile) {
    return (
      <Card className="w-full">
        <CardContent className="p-6 text-center">
          <FileAudio className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-lg font-medium mb-2">No Audio File Selected</h3>
          <p className="text-muted-foreground">
            Upload an audio file to see available editing commands
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Quick Commands</h3>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-xs">
            {selectedFile.name}
          </Badge>
          {selectedFile.duration && (
            <Badge variant="secondary" className="text-xs">
              <Clock className="h-3 w-3 mr-1" />
              {selectedFile.duration}
            </Badge>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {commandCategories.map((category, categoryIndex) => (
          <Card key={categoryIndex} className="h-fit">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center space-x-2">
                {category.icon}
                <span>{category.title}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {category.commands.map((command, commandIndex) => (
                <div key={commandIndex} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onCommandSelect(command.text)}
                      disabled={isProcessing}
                      className="justify-start h-auto p-2 text-left flex-1"
                    >
                      <div className="space-y-1">
                        <div className="font-medium text-sm">{command.text}</div>
                        <div className="text-xs text-muted-foreground">
                          {command.description}
                        </div>
                      </div>
                    </Button>
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ml-2 ${getCategoryColor(command.category)}`}
                    >
                      {command.category}
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Popular Commands Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center space-x-2">
            <Zap className="h-4 w-4" />
            <span>Most Popular</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {[
              'Remove background noise',
              'Normalize audio levels', 
              'Show audio metadata',
              'Add fade in and fade out',
              'Increase volume by 20%',
              'Cut first 30 seconds'
            ].map((command, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => onCommandSelect(command)}
                disabled={isProcessing}
                className="text-xs"
              >
                {command}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};