# LayoutConfigurationProvider

A React context provider that manages layout configuration and user preferences for the UI layout optimization system.

## Overview

The LayoutConfigurationProvider manages:
- Component visibility preferences
- Component size preferences  
- Layout behavior settings
- Responsive breakpoint handling
- User preference persistence

## Usage

### Basic Setup

```tsx
import { LayoutConfigurationProvider } from '../contexts/layout-configuration-context';

function App() {
  return (
    <LayoutConfigurationProvider>
      <YourAppContent />
    </LayoutConfigurationProvider>
  );
}
```

### Using the Hook

```tsx
import { useLayoutConfiguration } from '../contexts/layout-configuration-context';

function MyComponent() {
  const {
    layoutConfiguration,
    layoutPreferences,
    currentBreakpoint,
    toggleComponentVisibility,
    updateComponentHeight,
    toggleSidebar,
    toggleCompactMode
  } = useLayoutConfiguration();

  return (
    <div>
      <p>Current breakpoint: {currentBreakpoint}</p>
      <button onClick={() => toggleComponentVisibility('chatInterface')}>
        Toggle Chat
      </button>
    </div>
  );
}
```

### Enhanced Hook

For more utilities, use the enhanced hook:

```tsx
import { useLayoutConfigurationHook } from '../hooks/use-layout-configuration';

function MyComponent() {
  const {
    isMobile,
    isTablet,
    shouldShowComponent,
    getOptimalLayout,
    canFitAllComponents,
    shouldUseVirtualScrolling
  } = useLayoutConfigurationHook();

  if (isMobile) {
    return <MobileLayout />;
  }

  return (
    <div>
      <p>Layout: {getOptimalLayout()}</p>
      <p>All components fit: {canFitAllComponents() ? 'Yes' : 'No'}</p>
    </div>
  );
}
```

## Context Value

### Configuration Data
- `layoutConfiguration`: Current layout configuration object
- `layoutPreferences`: User's layout preferences
- `currentBreakpoint`: Current responsive breakpoint

### Actions
- `updateLayoutPreferences(preferences)`: Update user preferences
- `resetLayoutPreferences()`: Reset to default preferences
- `toggleComponentVisibility(component)`: Show/hide components
- `updateComponentHeight(component, height)`: Adjust component heights
- `toggleSidebar()`: Collapse/expand sidebar
- `toggleCompactMode()`: Enable/disable compact mode

### Utilities
- `isComponentVisible(component)`: Check if component is visible
- `getComponentHeight(component)`: Get component height
- `canFitAllComponents()`: Check if all components fit on screen

## Layout Preferences

```typescript
interface LayoutPreferences {
  componentVisibility: {
    fileUploader: boolean;
    waveformPlayer: boolean;
    chatInterface: boolean;
    fileManager: boolean;
    sidebar: boolean;
  };
  
  componentHeights: {
    fileUploader: number;
    waveformPlayer: number;
    chatInterface: number;
    fileManager: number;
  };
  
  sidebarCollapsed: boolean;
  compactMode: boolean;
  autoHideComponents: boolean;
  columnOrder: [1, 2, 3] | [2, 1, 3] | [1, 3, 2] | [2, 3, 1] | [3, 1, 2] | [3, 2, 1];
  mobileLayoutMode: 'stack' | 'tabs' | 'accordion';
  tabletLayoutMode: 'two-column' | 'single-column';
}
```

## Persistence

Layout preferences are automatically saved to the user store and persisted across sessions. The provider integrates with the existing `useUserStore` for seamless preference management.

## Responsive Behavior

The provider automatically detects screen size changes and updates the current breakpoint:

- **Desktop** (≥1920px): Full 3-column layout
- **Laptop** (1367-1919px): 3-column layout with smaller sidebar
- **Tablet** (769-1024px): 2-column or single-column layout
- **Mobile** (≤768px): Single-column layout, sidebar hidden

## Performance Features

- Debounced resize handling (150ms)
- Automatic component height clamping (100px - 800px)
- Optimized re-renders with useCallback
- Memory-efficient preference storage

## Integration with User Store

The provider extends the existing UserPreferences interface:

```typescript
interface UserPreferences {
  // ... existing preferences
  layoutPreferences?: LayoutPreferences;
}
```

Preferences are automatically synced with the user store and persisted using Zustand's persist middleware.

## Components

### LayoutSettings
A comprehensive settings panel for configuring layout preferences:

```tsx
import { LayoutSettings } from '../components/layout/layout-settings';

<LayoutSettings />
```

### LayoutConfigurationDemo
A demo component showing the layout system in action:

```tsx
import { LayoutConfigurationDemo } from '../components/layout/layout-configuration-demo';

<LayoutConfigurationDemo />
```

## Best Practices

1. **Wrap at App Level**: Place the provider high in your component tree
2. **Use Enhanced Hook**: Prefer `useLayoutConfigurationHook` for additional utilities
3. **Responsive Design**: Always check breakpoints before rendering components
4. **Performance**: Use `shouldShowComponent` to conditionally render heavy components
5. **Accessibility**: Respect user preferences for reduced motion and high contrast

## Error Handling

The provider includes comprehensive error handling:
- Graceful fallbacks for invalid preferences
- Automatic reset on corrupted data
- Console warnings for development debugging

## Testing

The provider can be tested with custom initial values:

```tsx
<LayoutConfigurationProvider initialBreakpoint="mobile">
  <TestComponent />
</LayoutConfigurationProvider>
```