import React from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Volume2, Scissors, Zap, Waves, Filter, Clock } from 'lucide-react';

interface CommandSuggestionsProps {
  onCommandSelect: (command: string) => void;
  disabled?: boolean;
}

interface CommandCategory {
  title: string;
  icon: React.ReactNode;
  commands: Array<{
    text: string;
    description: string;
  }>;
}

export const CommandSuggestions: React.FC<CommandSuggestionsProps> = ({
  onCommandSelect,
  disabled = false
}) => {
  const commandCategories: CommandCategory[] = [
    {
      title: "Volume",
      icon: <Volume2 className="h-4 w-4" />,
      commands: [
        { text: "Increase volume by 20%", description: "Boost audio level" },
        { text: "Decrease volume by 15%", description: "Lower audio level" },
        { text: "Normalize audio", description: "Balance audio levels" }
      ]
    },
    {
      title: "Editing",
      icon: <Scissors className="h-4 w-4" />,
      commands: [
        { text: "Cut the first 30 seconds", description: "Remove from start" },
        { text: "Remove the last minute", description: "Trim from end" },
        { text: "Extract from 1:00 to 2:30", description: "Get specific section" }
      ]
    },
    {
      title: "Effects",
      icon: <Waves className="h-4 w-4" />,
      commands: [
        { text: "Add 3 second fade in", description: "Smooth start" },
        { text: "Add fade out effect", description: "Smooth ending" },
        { text: "Add both fade in and out", description: "Smooth transitions" }
      ]
    },
    {
      title: "Cleanup",
      icon: <Filter className="h-4 w-4" />,
      commands: [
        { text: "Remove background noise", description: "Clean audio" },
        { text: "Remove silent parts", description: "Trim silence" },
        { text: "Enhance audio quality", description: "Improve clarity" }
      ]
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Zap className="h-4 w-4" />
          <span>Quick Commands</span>
        </CardTitle>
        <CardDescription>
          Click on any command to try it out
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {commandCategories.map((category, categoryIndex) => (
            <div key={categoryIndex} className="space-y-2">
              <div className="flex items-center space-x-2 text-sm font-medium text-muted-foreground">
                {category.icon}
                <span>{category.title}</span>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {category.commands.map((command, commandIndex) => (
                  <Button
                    key={commandIndex}
                    variant="outline"
                    size="sm"
                    className="justify-start h-auto p-3 text-left"
                    onClick={() => onCommandSelect(command.text)}
                    disabled={disabled}
                  >
                    <div className="space-y-1">
                      <div className="font-medium">{command.text}</div>
                      <div className="text-xs text-muted-foreground">
                        {command.description}
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};