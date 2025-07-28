import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/theme-provider';
import { ArrowLeft, Moon, Sun, Monitor, ExternalLink } from 'lucide-react';
import ComponentExamples from './examples/ComponentExamples';

interface ComponentShowcaseProps {
  onBack?: () => void;
}

const ComponentShowcase: React.FC<ComponentShowcaseProps> = ({ onBack }) => {
  const [inputValue, setInputValue] = useState('');
  const [showExamples, setShowExamples] = useState(false);
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();

  const showToast = (variant: 'default' | 'destructive' = 'default') => {
    toast({
      title: variant === 'destructive' ? 'Error!' : 'Success!',
      description: variant === 'destructive' 
        ? 'Something went wrong. Please try again.' 
        : 'Your action was completed successfully.',
      variant,
    });
  };

  const sampleData = [
    { id: 1, name: 'Audio File 1.mp3', size: '3.2 MB', duration: '2:45' },
    { id: 2, name: 'Audio File 2.wav', size: '12.8 MB', duration: '5:30' },
    { id: 3, name: 'Audio File 3.flac', size: '28.4 MB', duration: '4:15' },
  ];

  if (showExamples) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="container mx-auto p-6">
          <div className="flex items-center gap-4 mb-8">
            <Button variant="ghost" size="icon" onClick={() => setShowExamples(false)}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Component Examples</h1>
              <p className="text-muted-foreground">
                Detailed examples and usage patterns for all components
              </p>
            </div>
          </div>
          <ComponentExamples />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto p-6 space-y-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {onBack && (
              <Button variant="ghost" size="icon" onClick={onBack}>
                <ArrowLeft className="h-4 w-4" />
              </Button>
            )}
            <div>
              <h1 className="text-3xl font-bold">shadcn/ui Component Showcase</h1>
              <p className="text-muted-foreground">
                Demonstration of all available UI components with dark/light theme support.
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={theme === 'light' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setTheme('light')}
            >
              <Sun className="h-4 w-4" />
            </Button>
            <Button
              variant={theme === 'dark' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setTheme('dark')}
            >
              <Moon className="h-4 w-4" />
            </Button>
            <Button
              variant={theme === 'system' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setTheme('system')}
            >
              <Monitor className="h-4 w-4" />
            </Button>
          </div>
        </div>

      {/* Button Components */}
      <Card>
        <CardHeader>
          <CardTitle>Button Components</CardTitle>
          <CardDescription>
            Various button styles and sizes available in the component library.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button>Default</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
            <Button size="icon">🎵</Button>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button disabled>Disabled</Button>
            <Button variant="outline" disabled>Disabled Outline</Button>
          </div>
        </CardContent>
      </Card>

      {/* Input Components */}
      <Card>
        <CardHeader>
          <CardTitle>Input Components</CardTitle>
          <CardDescription>
            Form input elements with consistent styling and validation support.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Text Input</label>
              <Input 
                placeholder="Enter some text..." 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Password Input</label>
              <Input type="password" placeholder="Enter password..." />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Email Input</label>
              <Input type="email" placeholder="Enter email..." />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Disabled Input</label>
              <Input disabled placeholder="Disabled input..." />
            </div>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">
              Current input value: <code className="bg-muted px-1 rounded">{inputValue || 'empty'}</code>
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Dialog Components */}
      <Card>
        <CardHeader>
          <CardTitle>Dialog Components</CardTitle>
          <CardDescription>
            Modal dialogs for user interactions and confirmations.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Dialog>
              <DialogTrigger asChild>
                <Button>Open Dialog</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Sample Dialog</DialogTitle>
                  <DialogDescription>
                    This is a sample dialog demonstrating the dialog component.
                    You can add any content here including forms, buttons, and other components.
                  </DialogDescription>
                </DialogHeader>
                <div className="flex justify-end gap-2 mt-4">
                  <Button variant="outline">Cancel</Button>
                  <Button>Confirm</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardContent>
      </Card>

      {/* Toast Components */}
      <Card>
        <CardHeader>
          <CardTitle>Toast Notifications</CardTitle>
          <CardDescription>
            Toast notifications for user feedback and status updates.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => showToast('default')}>
              Show Success Toast
            </Button>
            <Button variant="destructive" onClick={() => showToast('destructive')}>
              Show Error Toast
            </Button>
            <Button variant="outline" onClick={() => setShowExamples(true)}>
              <ExternalLink className="h-4 w-4 mr-2" />
              View Detailed Examples
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Table Components */}
      <Card>
        <CardHeader>
          <CardTitle>Table Components</CardTitle>
          <CardDescription>
            Data tables with consistent styling and responsive design.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sampleData.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="font-medium">{item.name}</TableCell>
                  <TableCell>{item.size}</TableCell>
                  <TableCell>{item.duration}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm">
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Card Components */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Audio Processing</CardTitle>
            <CardDescription>Process and analyze audio files</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Upload audio files to get started with processing and analysis.
            </p>
            <Button className="w-full">Upload Files</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Export Manager</CardTitle>
            <CardDescription>Manage your audio exports</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              View and manage all your exported audio files.
            </p>
            <Button variant="outline" className="w-full">View Exports</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistics</CardTitle>
            <CardDescription>View processing statistics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">Files Processed:</span>
                <span className="text-sm font-medium">42</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Total Duration:</span>
                <span className="text-sm font-medium">2h 15m</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Theme Information */}
      <Card>
        <CardHeader>
          <CardTitle>Theme System</CardTitle>
          <CardDescription>
            Dark and light theme support with CSS variables
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm">
              The component library supports both dark and light themes using CSS variables.
              Theme switching is handled at the application level.
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4">
              <div className="p-2 rounded bg-primary text-primary-foreground text-center text-xs">
                Primary
              </div>
              <div className="p-2 rounded bg-secondary text-secondary-foreground text-center text-xs">
                Secondary
              </div>
              <div className="p-2 rounded bg-muted text-muted-foreground text-center text-xs">
                Muted
              </div>
              <div className="p-2 rounded bg-accent text-accent-foreground text-center text-xs">
                Accent
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      </div>
    </div>
  );
};

export default ComponentShowcase;