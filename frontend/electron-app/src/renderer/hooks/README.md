# Responsive Layout Hooks

A comprehensive set of React hooks for managing responsive layout behavior, breakpoint transitions, and adaptive component sizing.

## Overview

The responsive layout system consists of three main hooks:

1. **`useResponsiveLayout`** - Core responsive layout management
2. **`useResponsiveLayoutTransitions`** - Smooth transitions between breakpoints
3. **`useLayoutConfigurationHook`** - Enhanced layout utilities with user preferences

## useResponsiveLayout

The main hook for responsive layout management with enhanced breakpoint detection and transition handling.

### Features

- **Enhanced Breakpoint Detection**: Hysteresis-based detection prevents flickering
- **Adaptive Component Sizing**: Components automatically adjust based on available space
- **Transition Tracking**: Complete history of breakpoint transitions
- **Performance Optimization**: Debounced resize handling with requestAnimationFrame
- **Multiple Event Listeners**: Handles resize, orientation change, and zoom events

### Usage

```tsx
import { useResponsiveLayout } from '../hooks/use-responsive-layout';

function MyComponent() {
  const {
    screenSize,
    currentBreakpoint,
    previousBreakpoint,
    layoutConfiguration,
    layoutMetrics,
    isTransitioning,
    transitionHistory,
    isBreakpoint,
    isBreakpointOrSmaller,
    isBreakpointOrLarger,
    getBreakpointRange,
    getOptimalColumnCount,
    shouldUseCompactLayout
  } = useResponsiveLayout({
    customBreakpoints: {
      tablet: 800 // Custom tablet breakpoint
    },
    debounceMs: 200,
    enableTransitionTracking: true,
    adaptiveComponentSizing: true,
    performanceMode: false,
    onBreakpointChange: (transition) => {
      console.log(`Breakpoint changed: ${transition.from} → ${transition.to}`);
    }
  });

  return (
    <div>
      <p>Current: {currentBreakpoint}</p>
      <p>Screen: {screenSize.width}x{screenSize.height}</p>
      <p>Optimal columns: {getOptimalColumnCount()}</p>
      <p>Use compact: {shouldUseCompactLayout() ? 'Yes' : 'No'}</p>
    </div>
  );
}
```

### Options

```typescript
interface ResponsiveLayoutHookOptions {
  customBreakpoints?: Partial<ResponsiveBreakpoints>;
  debounceMs?: number; // Default: 150
  enableTransitionTracking?: boolean; // Default: true
  onBreakpointChange?: (transition: BreakpointTransition) => void;
  adaptiveComponentSizing?: boolean; // Default: true
  performanceMode?: boolean; // Default: false
}
```

### Return Value

```typescript
{
  // Basic responsive data
  screenSize: { width: number; height: number };
  currentBreakpoint: BreakpointName;
  previousBreakpoint: BreakpointName;
  layoutConfiguration: LayoutConfiguration;
  
  // Breakpoint utilities
  isBreakpoint: (breakpoint: BreakpointName) => boolean;
  isBreakpointOrSmaller: (breakpoint: BreakpointName) => boolean;
  isBreakpointOrLarger: (breakpoint: BreakpointName) => boolean;
  isMobile: boolean;
  isTablet: boolean;
  isLaptop: boolean;
  isDesktop: boolean;
  
  // Enhanced utilities
  getBreakpointRange: (breakpoint: BreakpointName) => { min: number; max: number };
  getOptimalColumnCount: () => number;
  shouldUseCompactLayout: () => boolean;
  layoutMetrics: {
    totalComponentHeight: number;
    availableHeight: number;
    fitsOnScreen: boolean;
    optimalColumnCount: number;
    shouldUseCompactLayout: boolean;
    breakpointRange: { min: number; max: number };
  };
  
  // Transition management
  isTransitioning: boolean;
  transitionHistory: BreakpointTransition[];
  
  // Configuration
  breakpoints: ResponsiveBreakpoints;
  options: ResponsiveLayoutHookOptions;
}
```

## useResponsiveLayoutTransitions

Manages smooth transitions between breakpoints with CSS animations and component state tracking.

### Features

- **Smooth Animations**: CSS-based transitions with configurable duration and easing
- **Staggered Animations**: Components animate with delays for polished effects
- **Transition State Tracking**: Know which components are currently transitioning
- **Preloading**: Preload adjacent breakpoint layouts for instant transitions
- **Accessibility**: Respects `prefers-reduced-motion` setting

### Usage

```tsx
import { useResponsiveLayoutTransitions } from '../hooks/use-responsive-layout-transitions';

function MyComponent() {
  const {
    isTransitioning,
    activeTransitions,
    getTransitionStyles,
    getLayoutClasses,
    startComponentTransition,
    transitionConfig
  } = useResponsiveLayoutTransitions({
    transitionConfig: {
      duration: 300,
      easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
      staggerDelay: 50,
      enableAnimations: true
    },
    onTransitionStart: (transition) => {
      console.log('Transition started:', transition);
    },
    onTransitionEnd: (transition) => {
      console.log('Transition ended:', transition);
    },
    enablePreloading: true
  });

  return (
    <div className={getLayoutClasses()}>
      <div 
        className="my-component"
        style={getTransitionStyles('myComponent')}
      >
        Content with smooth transitions
      </div>
    </div>
  );
}
```

### CSS Integration

Import the transition styles:

```tsx
import './responsive-transitions.css';
```

The CSS provides:
- Smooth grid transitions
- Component height/width animations
- Staggered column animations
- Breakpoint-specific transition effects
- Accessibility support (reduced motion)

## useLayoutConfigurationHook

Enhanced hook that combines responsive layout with user preferences and configuration management.

### Features

- **User Preferences Integration**: Connects with LayoutConfigurationProvider
- **Component Management**: Show/hide and resize components
- **Performance Utilities**: Virtual scrolling and lazy loading recommendations
- **Layout Optimization**: Automatic layout suggestions based on screen size

### Usage

```tsx
import { useLayoutConfigurationHook } from '../hooks/use-layout-configuration';

function MyComponent() {
  const {
    layoutConfiguration,
    currentBreakpoint,
    isComponentVisible,
    shouldShowComponent,
    getOptimalLayout,
    shouldUseVirtualScrolling,
    shouldLazyLoad,
    toggleComponentVisibility,
    updateComponentHeight
  } = useLayoutConfigurationHook();

  return (
    <div>
      <p>Layout: {getOptimalLayout()}</p>
      <p>Use virtual scrolling: {shouldUseVirtualScrolling ? 'Yes' : 'No'}</p>
      
      {shouldShowComponent('chatInterface') && (
        <div>Chat Interface</div>
      )}
      
      <button onClick={() => toggleComponentVisibility('sidebar')}>
        Toggle Sidebar
      </button>
    </div>
  );
}
```

## Best Practices

### Performance

1. **Use Debouncing**: Default 150ms debounce prevents excessive re-renders
2. **Enable Performance Mode**: Reduces component visibility on smaller screens
3. **Memoize Expensive Calculations**: Layout metrics are automatically memoized
4. **Use requestAnimationFrame**: Smooth resize handling with RAF

### Accessibility

1. **Respect User Preferences**: Automatically disables animations for `prefers-reduced-motion`
2. **High Contrast Support**: Enhanced borders and focus states
3. **Keyboard Navigation**: Maintains focus during transitions
4. **Screen Reader Support**: Announces layout changes

### Responsive Design

1. **Mobile First**: Design for mobile, enhance for larger screens
2. **Progressive Enhancement**: Add features as screen size increases
3. **Content Priority**: Hide non-essential components on smaller screens
4. **Touch Targets**: Ensure adequate touch target sizes

### Transitions

1. **Meaningful Motion**: Transitions should guide user attention
2. **Consistent Timing**: Use consistent duration and easing
3. **Stagger Effects**: Animate components in logical order
4. **Reduce Complexity**: Simpler animations perform better

## Examples

### Basic Responsive Layout

```tsx
function ResponsiveLayout() {
  const { currentBreakpoint, layoutConfiguration } = useResponsiveLayout();
  
  return (
    <div className={`layout-${currentBreakpoint}`}>
      {/* Layout content */}
    </div>
  );
}
```

### Animated Transitions

```tsx
function AnimatedLayout() {
  const { getLayoutClasses } = useResponsiveLayoutTransitions();
  
  return (
    <div className={getLayoutClasses()}>
      {/* Animated layout content */}
    </div>
  );
}
```

### User Preferences

```tsx
function ConfigurableLayout() {
  const { 
    shouldShowComponent,
    toggleComponentVisibility 
  } = useLayoutConfigurationHook();
  
  return (
    <div>
      {shouldShowComponent('sidebar') && <Sidebar />}
      <button onClick={() => toggleComponentVisibility('sidebar')}>
        Toggle Sidebar
      </button>
    </div>
  );
}
```

## Browser Support

- Modern browsers with CSS Grid support
- Fallback handling for older browsers
- Progressive enhancement approach
- Polyfills not required for core functionality

## Testing

The hooks can be tested with custom breakpoints and mock window dimensions:

```tsx
// Test with custom breakpoints
const { result } = renderHook(() => 
  useResponsiveLayout({
    customBreakpoints: { mobile: 400, tablet: 600 }
  })
);

// Mock window dimensions
Object.defineProperty(window, 'innerWidth', { value: 800 });
Object.defineProperty(window, 'innerHeight', { value: 600 });
```