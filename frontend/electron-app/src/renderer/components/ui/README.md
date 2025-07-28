# shadcn/ui Component Library

This directory contains the shadcn/ui component library implementation for the Audio Chat Studio Electron application. All components are built with React, TypeScript, and Tailwind CSS, providing a consistent and accessible user interface.

## Available Components

### Button
A versatile button component with multiple variants and sizes.

**Variants:**
- `default` - Primary button style
- `destructive` - For dangerous actions
- `outline` - Outlined button
- `secondary` - Secondary button style
- `ghost` - Minimal button style
- `link` - Link-styled button

**Sizes:**
- `default` - Standard size (h-10)
- `sm` - Small size (h-9)
- `lg` - Large size (h-11)
- `icon` - Square icon button (h-10 w-10)

**Usage:**
```tsx
import { Button } from '@/renderer/components/ui/button';

<Button variant="default" size="lg">
  Click me
</Button>
```

### Input
Form input component with consistent styling and validation support.

**Features:**
- Consistent styling across all input types
- Focus states and accessibility
- Disabled state support
- File input styling

**Usage:**
```tsx
import { Input } from '@/renderer/components/ui/input';

<Input 
  type="text" 
  placeholder="Enter text..." 
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>
```

### Card
Container component for grouping related content.

**Components:**
- `Card` - Main container
- `CardHeader` - Header section
- `CardTitle` - Title component
- `CardDescription` - Description text
- `CardContent` - Main content area
- `CardFooter` - Footer section

**Usage:**
```tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/renderer/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
</Card>
```

### Dialog
Modal dialog component built on Radix UI primitives.

**Components:**
- `Dialog` - Root component
- `DialogTrigger` - Trigger button
- `DialogContent` - Modal content
- `DialogHeader` - Header section
- `DialogTitle` - Dialog title
- `DialogDescription` - Dialog description
- `DialogFooter` - Footer section
- `DialogClose` - Close button

**Usage:**
```tsx
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/renderer/components/ui/dialog';

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>Dialog description</DialogDescription>
    </DialogHeader>
    <p>Dialog content</p>
  </DialogContent>
</Dialog>
```

### Table
Data table components with consistent styling.

**Components:**
- `Table` - Main table container
- `TableHeader` - Table header
- `TableBody` - Table body
- `TableFooter` - Table footer
- `TableRow` - Table row
- `TableHead` - Header cell
- `TableCell` - Data cell
- `TableCaption` - Table caption

**Usage:**
```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/renderer/components/ui/table';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Item 1</TableCell>
      <TableCell>Active</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Toast
Toast notification system for user feedback.

**Components:**
- `Toast` - Individual toast
- `ToastProvider` - Context provider
- `ToastViewport` - Toast container
- `ToastTitle` - Toast title
- `ToastDescription` - Toast description
- `ToastAction` - Action button
- `ToastClose` - Close button
- `Toaster` - Complete toast system

**Usage:**
```tsx
import { useToast } from '@/renderer/hooks/use-toast';

const { toast } = useToast();

// Show success toast
toast({
  title: "Success!",
  description: "Your action was completed successfully.",
});

// Show error toast
toast({
  title: "Error!",
  description: "Something went wrong.",
  variant: "destructive",
});
```

## Theme System

The component library supports both dark and light themes using CSS variables. Theme switching is handled through the `ThemeProvider` context.

### CSS Variables

The following CSS variables are available for theming:

**Light Theme:**
- `--background` - Main background color
- `--foreground` - Main text color
- `--primary` - Primary brand color
- `--secondary` - Secondary color
- `--muted` - Muted backgrounds
- `--accent` - Accent color
- `--destructive` - Error/danger color
- `--border` - Border color
- `--input` - Input border color
- `--ring` - Focus ring color

**Dark Theme:**
All variables have dark theme equivalents automatically applied when the `dark` class is present on the root element.

### Theme Provider Usage

```tsx
import { ThemeProvider } from '@/renderer/contexts/theme-provider';
import { useTheme } from '@/renderer/contexts/theme-provider';

// Wrap your app
<ThemeProvider defaultTheme="system" storageKey="ui-theme">
  <App />
</ThemeProvider>

// Use in components
const { theme, setTheme } = useTheme();

<Button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
  Toggle Theme
</Button>
```

## Responsive Design

The component library includes responsive design utilities:

### Breakpoints
- `sm` - 640px and up
- `md` - 768px and up
- `lg` - 1024px and up
- `xl` - 1280px and up
- `2xl` - 1536px and up

### Container
The `container` class provides responsive max-widths:
- Centered by default
- 2rem padding
- Max width of 1400px on 2xl screens

### Usage Examples
```tsx
// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Cards */}
</div>

// Responsive text
<h1 className="text-2xl md:text-3xl lg:text-4xl">
  Responsive Heading
</h1>

// Responsive spacing
<div className="p-4 md:p-6 lg:p-8">
  Content
</div>
```

## Accessibility

All components follow accessibility best practices:

- Semantic HTML elements
- ARIA attributes where needed
- Keyboard navigation support
- Focus management
- Screen reader compatibility
- Color contrast compliance

## Customization

Components can be customized using:

1. **CSS Variables** - Modify theme colors
2. **Tailwind Classes** - Override specific styles
3. **Component Props** - Use variant and size props
4. **Custom CSS** - Add additional styles as needed

### Example Customization
```tsx
// Using className prop
<Button className="bg-gradient-to-r from-blue-500 to-purple-600">
  Gradient Button
</Button>

// Using CSS variables
:root {
  --primary: 220 100% 50%; /* Custom blue */
}
```

## Development Guidelines

When working with these components:

1. **Import from the ui directory** - Always import from `@/renderer/components/ui/`
2. **Use TypeScript** - All components are fully typed
3. **Follow naming conventions** - Use PascalCase for components
4. **Test accessibility** - Ensure keyboard and screen reader support
5. **Maintain consistency** - Use existing patterns and styles

## Performance Considerations

- Components use `React.forwardRef` for proper ref forwarding
- Minimal re-renders through proper prop handling
- Tree-shakable imports
- Optimized bundle size with Tailwind CSS purging
- Lazy loading support for large component sets

## Browser Support

The component library supports:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

When adding new components:

1. Follow the existing patterns
2. Include proper TypeScript types
3. Add accessibility features
4. Test in both light and dark themes
5. Update this documentation
6. Add usage examples