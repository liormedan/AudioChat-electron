# MainLayoutGrid Component

A responsive CSS Grid-based layout system designed for optimal UI organization on standard screen sizes.

## Overview

The MainLayoutGrid component provides a structured 3-column layout with responsive breakpoints, designed to eliminate excessive scrolling and optimize the user experience for audio editing applications.

## Components

### MainLayoutGrid
The main container component that establishes the CSS Grid layout.

```tsx
<MainLayoutGrid className="custom-class">
  {children}
</MainLayoutGrid>
```

### ContentArea
The main content area that contains the 3-column layout.

```tsx
<ContentArea>
  <Column column={1}>...</Column>
  <Column column={2}>...</Column>
  <Column column={3}>...</Column>
</ContentArea>
```

### Column
Individual columns within the content area.

```tsx
<Column column={1} className="custom-column">
  <CompactComponent height={200}>...</CompactComponent>
</Column>
```

### CompactComponent
A container for components with fixed heights and optional scrolling.

```tsx
<CompactComponent 
  height={400} 
  scrollable={true}
  className="custom-component"
>
  {content}
</CompactComponent>
```

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        Header (60px)                        │
├─────────────────────────────────────────────────────────────┤
│ Sidebar │              Main Content Area                    │
│ (240px) │                (1680px)                          │
│         │  ┌─────────────┬─────────────┬─────────────┐     │
│         │  │   Upload    │   Player    │    Chat     │     │
│         │  │   & Files   │   & Info    │  & Tools    │     │
│         │  │   (560px)   │   (560px)   │   (560px)   │     │
│         │  │             │             │             │     │
│         │  └─────────────┴─────────────┴─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Responsive Breakpoints

| Breakpoint | Width Range | Layout | Sidebar | Columns |
|------------|-------------|--------|---------|---------|
| Desktop    | ≥1920px     | 3-col  | 240px   | 560px each |
| Laptop     | 1367-1919px | 3-col  | 200px   | 450px each |
| Small Laptop | 1025-1366px | 2+1-col | 180px | 2 cols + full-width chat |
| Tablet     | 769-1024px  | 1-col  | 160px   | Single column |
| Mobile     | ≤768px      | 1-col  | Hidden  | Single column |

## Component Heights

| Component | Desktop | Mobile | Description |
|-----------|---------|--------|-------------|
| Header    | 60px    | 50px   | App header |
| FileUploader | 200px | 150px | File upload area |
| WaveformPlayer | 300px | 225px | Audio player |
| ChatInterface | 400px | 300px | AI chat |
| FileManager | 400px | 300px | File list |

## Usage with useResponsiveLayout Hook

```tsx
import { useResponsiveLayout } from '../../hooks/use-responsive-layout';
import { MainLayoutGrid, ContentArea, Column, CompactComponent } from './main-layout-grid';

const MyComponent = () => {
  const { 
    currentBreakpoint, 
    layoutConfiguration, 
    isMobile,
    isTablet 
  } = useResponsiveLayout();

  return (
    <MainLayoutGrid>
      <ContentArea>
        <Column column={1}>
          <CompactComponent 
            height={layoutConfiguration.components.fileUploader.height}
          >
            {/* File uploader content */}
          </CompactComponent>
        </Column>
        
        {!isMobile && (
          <Column column={2}>
            <CompactComponent 
              height={layoutConfiguration.components.waveformPlayer.height}
            >
              {/* Waveform player content */}
            </CompactComponent>
          </Column>
        )}
      </ContentArea>
    </MainLayoutGrid>
  );
};
```

## Features

- **Responsive Design**: Automatically adapts to different screen sizes
- **RTL Support**: Full right-to-left language support
- **Performance Optimized**: Smooth transitions with reduced motion support
- **Accessibility**: High contrast mode support and keyboard navigation
- **Customizable**: Easy to extend with custom breakpoints and component heights

## CSS Classes

- `.main-layout-grid` - Main container
- `.main-layout-grid.rtl` - RTL mode
- `.content-area` - Content grid area
- `.layout-column` - Individual columns
- `.layout-column-1`, `.layout-column-2`, `.layout-column-3` - Specific column styling
- `.compact-component` - Component containers

## Performance Considerations

- Uses CSS Grid for optimal performance
- Debounced resize handling (150ms)
- Smooth transitions with `prefers-reduced-motion` support
- Optimized scrollbar styling
- Box-sizing border-box for all elements

## Browser Support

- Modern browsers with CSS Grid support
- Fallback handling for older browsers
- Progressive enhancement approach