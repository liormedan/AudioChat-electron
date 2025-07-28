import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { useToast } from '../../hooks/use-toast';
import { useTheme } from '../../contexts/theme-provider';

/**
 * Comprehensive examples of how to use each UI component
 * This file serves as both documentation and testing for components
 */

// Button Examples
export const ButtonExamples: React.FC = () => {
  const { toast } = useToast();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Button Examples</CardTitle>
        <CardDescription>
          Various button configurations and use cases
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Variants */}
        <div>
          <h4 className="font-medium mb-3">Basic Variants</h4>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => toast({ title: "Default clicked" })}>
              Default
            </Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </div>
        </div>

        {/* Sizes */}
        <div>
          <h4 className="font-medium mb-3">Sizes</h4>
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
            <Button size="icon">🎵</Button>
          </div>
        </div>

        {/* States */}
        <div>
          <h4 className="font-medium mb-3">States</h4>
          <div className="flex flex-wrap gap-2">
            <Button disabled>Disabled</Button>
            <Button variant="outline" disabled>Disabled Outline</Button>
            <Button className="loading">Loading...</Button>
          </div>
        </div>

        {/* With Icons */}
        <div>
          <h4 className="font-medium mb-3">With Icons</h4>
          <div className="flex flex-wrap gap-2">
            <Button>
              <span className="mr-2">📁</span>
              Open File
            </Button>
            <Button variant="outline">
              Save
              <span className="ml-2">💾</span>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Input Examples
export const InputExamples: React.FC = () => {
  const [values, setValues] = useState({
    text: '',
    email: '',
    password: '',
    number: '',
    search: ''
  });

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setValues(prev => ({ ...prev, [field]: e.target.value }));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Input Examples</CardTitle>
        <CardDescription>
          Different input types and configurations
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Text Input</label>
            <Input
              type="text"
              placeholder="Enter text..."
              value={values.text}
              onChange={handleChange('text')}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Email Input</label>
            <Input
              type="email"
              placeholder="Enter email..."
              value={values.email}
              onChange={handleChange('email')}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Password Input</label>
            <Input
              type="password"
              placeholder="Enter password..."
              value={values.password}
              onChange={handleChange('password')}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Number Input</label>
            <Input
              type="number"
              placeholder="Enter number..."
              value={values.number}
              onChange={handleChange('number')}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Search Input</label>
            <Input
              type="search"
              placeholder="Search..."
              value={values.search}
              onChange={handleChange('search')}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Disabled Input</label>
            <Input
              disabled
              placeholder="Disabled input..."
            />
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-muted rounded-md">
          <h5 className="font-medium mb-2">Current Values:</h5>
          <pre className="text-xs overflow-x-auto">
            {JSON.stringify(values, null, 2)}
          </pre>
        </div>
      </CardContent>
    </Card>
  );
};

// Dialog Examples
export const DialogExamples: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { toast } = useToast();

  const handleConfirm = () => {
    toast({ title: "Confirmed!", description: "Action was confirmed" });
    setIsOpen(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dialog Examples</CardTitle>
        <CardDescription>
          Modal dialogs for user interactions
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {/* Basic Dialog */}
          <Dialog>
            <DialogTrigger asChild>
              <Button>Basic Dialog</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Basic Dialog</DialogTitle>
                <DialogDescription>
                  This is a basic dialog with title and description.
                </DialogDescription>
              </DialogHeader>
              <p>Dialog content goes here.</p>
            </DialogContent>
          </Dialog>

          {/* Confirmation Dialog */}
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="destructive">Delete Item</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Confirm Deletion</DialogTitle>
                <DialogDescription>
                  Are you sure you want to delete this item? This action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsOpen(false)}>
                  Cancel
                </Button>
                <Button variant="destructive" onClick={handleConfirm}>
                  Delete
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Form Dialog */}
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline">Form Dialog</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Item</DialogTitle>
                <DialogDescription>
                  Fill out the form below to create a new item.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Name</label>
                  <Input placeholder="Enter name..." />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Description</label>
                  <Input placeholder="Enter description..." />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline">Cancel</Button>
                <Button>Create</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </CardContent>
    </Card>
  );
};

// Table Examples
export const TableExamples: React.FC = () => {
  const [sortField, setSortField] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const data = [
    { id: 1, name: 'Audio File 1.mp3', size: '3.2 MB', duration: '2:45', status: 'Processed' },
    { id: 2, name: 'Audio File 2.wav', size: '12.8 MB', duration: '5:30', status: 'Processing' },
    { id: 3, name: 'Audio File 3.flac', size: '28.4 MB', duration: '4:15', status: 'Queued' },
    { id: 4, name: 'Audio File 4.mp3', size: '5.1 MB', duration: '3:20', status: 'Processed' },
  ];

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Processed': return 'text-green-600 dark:text-green-400';
      case 'Processing': return 'text-yellow-600 dark:text-yellow-400';
      case 'Queued': return 'text-blue-600 dark:text-blue-400';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Table Examples</CardTitle>
        <CardDescription>
          Data tables with sorting and status indicators
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead 
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort('name')}
                >
                  Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
                </TableHead>
                <TableHead 
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort('size')}
                >
                  Size {sortField === 'size' && (sortDirection === 'asc' ? '↑' : '↓')}
                </TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((item) => (
                <TableRow key={item.id} className="hover:bg-muted/50">
                  <TableCell className="font-medium">{item.name}</TableCell>
                  <TableCell>{item.size}</TableCell>
                  <TableCell>{item.duration}</TableCell>
                  <TableCell>
                    <span className={getStatusColor(item.status)}>
                      {item.status}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button variant="ghost" size="sm">Edit</Button>
                      <Button variant="ghost" size="sm">Delete</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

// Theme Examples
export const ThemeExamples: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Theme Examples</CardTitle>
        <CardDescription>
          Theme switching and color demonstrations
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Theme Controls */}
        <div>
          <h4 className="font-medium mb-3">Theme Controls</h4>
          <div className="flex gap-2">
            <Button 
              variant={theme === 'light' ? 'default' : 'outline'}
              onClick={() => setTheme('light')}
            >
              Light
            </Button>
            <Button 
              variant={theme === 'dark' ? 'default' : 'outline'}
              onClick={() => setTheme('dark')}
            >
              Dark
            </Button>
            <Button 
              variant={theme === 'system' ? 'default' : 'outline'}
              onClick={() => setTheme('system')}
            >
              System
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            Current theme: <code className="bg-muted px-1 rounded">{theme}</code>
          </p>
        </div>

        {/* Color Palette */}
        <div>
          <h4 className="font-medium mb-3">Color Palette</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <div className="p-3 rounded bg-primary text-primary-foreground text-center text-sm">
              Primary
            </div>
            <div className="p-3 rounded bg-secondary text-secondary-foreground text-center text-sm">
              Secondary
            </div>
            <div className="p-3 rounded bg-muted text-muted-foreground text-center text-sm">
              Muted
            </div>
            <div className="p-3 rounded bg-accent text-accent-foreground text-center text-sm">
              Accent
            </div>
            <div className="p-3 rounded bg-destructive text-destructive-foreground text-center text-sm">
              Destructive
            </div>
            <div className="p-3 rounded border bg-card text-card-foreground text-center text-sm">
              Card
            </div>
            <div className="p-3 rounded border bg-popover text-popover-foreground text-center text-sm">
              Popover
            </div>
            <div className="p-3 rounded bg-background text-foreground border text-center text-sm">
              Background
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Complete Examples Component
export const ComponentExamples: React.FC = () => {
  return (
    <div className="space-y-8">
      <ButtonExamples />
      <InputExamples />
      <DialogExamples />
      <TableExamples />
      <ThemeExamples />
    </div>
  );
};

export default ComponentExamples;