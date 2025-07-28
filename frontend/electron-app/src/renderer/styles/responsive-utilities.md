# Responsive Design Utilities

This document outlines the responsive design utilities and patterns used in the Audio Chat Studio Electron application.

## Breakpoints

The application uses Tailwind CSS's default breakpoint system:

| Breakpoint | Min Width | Usage |
|------------|-----------|-------|
| `sm` | 640px | Small tablets and large phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small laptops |
| `xl` | 1280px | Large laptops and desktops |
| `2xl` | 1536px | Large desktops |

## Container System

### Container Class
The `container` class provides responsive max-widths and centering:

```tsx
<div className="container mx-auto px-4">
  {/* Content automatically centered with responsive max-widths */}
</div>
```

**Container Behavior:**
- Automatically centers content
- Responsive max-widths at each breakpoint
- Default padding of 2rem
- Max width of 1400px on 2xl screens

## Common Responsive Patterns

### Grid Layouts
```tsx
// Responsive grid that adapts to screen size
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => (
    <Card key={item.id}>
      {/* Card content */}
    </Card>
  ))}
</div>

// Dashboard layout
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <div className="lg:col-span-2">
    {/* Main content */}
  </div>
  <div>
    {/* Sidebar */}
  </div>
</div>
```

### Flexbox Layouts
```tsx
// Responsive flex direction
<div className="flex flex-col md:flex-row gap-4">
  <div className="flex-1">Content 1</div>
  <div className="flex-1">Content 2</div>
</div>

// Responsive button groups
<div className="flex flex-col sm:flex-row gap-2">
  <Button>Action 1</Button>
  <Button>Action 2</Button>
  <Button>Action 3</Button>
</div>
```

### Typography
```tsx
// Responsive headings
<h1 className="text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-bold">
  Responsive Heading
</h1>

// Responsive body text
<p className="text-sm md:text-base lg:text-lg">
  Responsive paragraph text
</p>
```

### Spacing
```tsx
// Responsive padding
<div className="p-4 md:p-6 lg:p-8">
  Content with responsive padding
</div>

// Responsive margins
<div className="mb-4 md:mb-6 lg:mb-8">
  Content with responsive bottom margin
</div>

// Responsive gaps
<div className="space-y-4 md:space-y-6 lg:space-y-8">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

### Visibility
```tsx
// Hide on mobile, show on desktop
<div className="hidden md:block">
  Desktop only content
</div>

// Show on mobile, hide on desktop
<div className="block md:hidden">
  Mobile only content
</div>

// Different content for different screen sizes
<div>
  <span className="inline md:hidden">Mobile text</span>
  <span className="hidden md:inline">Desktop text</span>
</div>
```

## Component-Specific Responsive Patterns

### Cards
```tsx
// Responsive card grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  <Card>
    <CardHeader>
      <CardTitle className="text-lg md:text-xl">Title</CardTitle>
    </CardHeader>
    <CardContent className="p-4 md:p-6">
      Content
    </CardContent>
  </Card>
</div>
```

### Tables
```tsx
// Responsive table with horizontal scroll on mobile
<div className="overflow-x-auto">
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead className="min-w-[100px]">Name</TableHead>
        <TableHead className="min-w-[80px]">Status</TableHead>
        <TableHead className="min-w-[120px] hidden md:table-cell">
          Created
        </TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      {/* Table rows */}
    </TableBody>
  </Table>
</div>
```

### Dialogs
```tsx
// Responsive dialog sizing
<DialogContent className="w-full max-w-md md:max-w-lg lg:max-w-xl">
  <DialogHeader>
    <DialogTitle className="text-lg md:text-xl">
      Responsive Dialog
    </DialogTitle>
  </DialogHeader>
  <div className="p-4 md:p-6">
    Dialog content
  </div>
</DialogContent>
```

### Navigation
```tsx
// Responsive navigation
<nav className="flex flex-col md:flex-row gap-2 md:gap-4">
  <Button variant="ghost" className="justify-start md:justify-center">
    Home
  </Button>
  <Button variant="ghost" className="justify-start md:justify-center">
    About
  </Button>
</nav>
```

## Mobile-First Approach

The application follows a mobile-first responsive design approach:

1. **Base styles** target mobile devices (no prefix)
2. **Breakpoint prefixes** add styles for larger screens
3. **Progressive enhancement** adds features as screen size increases

```tsx
// Mobile-first example
<div className="
  p-4          // Mobile: 16px padding
  md:p-6       // Tablet: 24px padding
  lg:p-8       // Desktop: 32px padding
  text-sm      // Mobile: small text
  md:text-base // Tablet+: normal text
  flex-col     // Mobile: vertical stack
  md:flex-row  // Tablet+: horizontal layout
">
  Content
</div>
```

## Performance Considerations

### Efficient Responsive Images
```tsx
// Responsive image sizing
<img 
  src="/image.jpg"
  className="w-full h-auto max-w-xs md:max-w-sm lg:max-w-md"
  alt="Responsive image"
/>
```

### Conditional Rendering
```tsx
// Use CSS classes instead of conditional rendering when possible
// Good:
<div className="hidden md:block">Desktop content</div>

// Avoid when possible:
{isDesktop && <div>Desktop content</div>}
```

## Testing Responsive Design

### Browser DevTools
1. Open Chrome/Firefox DevTools
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test different device presets
4. Use responsive mode to test custom sizes

### Common Test Sizes
- **Mobile**: 375px (iPhone), 360px (Android)
- **Tablet**: 768px (iPad), 1024px (iPad Pro)
- **Desktop**: 1280px, 1440px, 1920px

### Accessibility Testing
- Ensure touch targets are at least 44px on mobile
- Test keyboard navigation on all screen sizes
- Verify text remains readable at all sizes
- Check color contrast at different zoom levels

## Best Practices

1. **Mobile-first design**: Start with mobile styles, enhance for larger screens
2. **Touch-friendly**: Ensure buttons and interactive elements are large enough
3. **Content priority**: Show most important content first on small screens
4. **Performance**: Minimize layout shifts and reflows
5. **Accessibility**: Maintain usability across all device types
6. **Testing**: Test on real devices when possible

## Common Pitfalls to Avoid

1. **Fixed heights**: Use min-height instead of height when possible
2. **Horizontal scrolling**: Ensure content fits within viewport
3. **Tiny touch targets**: Make buttons at least 44px on mobile
4. **Overlapping content**: Test content at various zoom levels
5. **Inconsistent spacing**: Use consistent spacing scales across breakpoints