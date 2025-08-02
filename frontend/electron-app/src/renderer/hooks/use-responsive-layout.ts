import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { 
  LayoutConfiguration, 
  ResponsiveBreakpoints, 
  DEFAULT_BREAKPOINTS, 
  DEFAULT_COMPONENT_HEIGHTS,
  BreakpointName 
} from '../components/layout/types';

export interface BreakpointTransition {
  from: BreakpointName;
  to: BreakpointName;
  timestamp: number;
  direction: 'up' | 'down';
}

export interface ResponsiveLayoutHookOptions {
  customBreakpoints?: Partial<ResponsiveBreakpoints>;
  debounceMs?: number;
  enableTransitionTracking?: boolean;
  onBreakpointChange?: (transition: BreakpointTransition) => void;
  adaptiveComponentSizing?: boolean;
  performanceMode?: boolean;
}

export const useResponsiveLayout = (
  options: ResponsiveLayoutHookOptions = {}
) => {
  const {
    customBreakpoints,
    debounceMs = 150,
    enableTransitionTracking = true,
    onBreakpointChange,
    adaptiveComponentSizing = true,
    performanceMode = false
  } = options;

  const breakpoints = { ...DEFAULT_BREAKPOINTS, ...customBreakpoints };
  
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1920,
    height: typeof window !== 'undefined' ? window.innerHeight : 1080
  });

  const [currentBreakpoint, setCurrentBreakpoint] = useState<BreakpointName>('desktop');
  const [previousBreakpoint, setPreviousBreakpoint] = useState<BreakpointName>('desktop');
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitionHistory, setTransitionHistory] = useState<BreakpointTransition[]>([]);
  
  // Refs for performance optimization
  const resizeTimeoutRef = useRef<NodeJS.Timeout>();
  const transitionTimeoutRef = useRef<NodeJS.Timeout>();
  const lastResizeTimeRef = useRef<number>(0);
  const frameRequestRef = useRef<number>();

  const getCurrentBreakpoint = useCallback((width: number): BreakpointName => {
    if (width >= breakpoints.desktop) return 'desktop';
    if (width >= breakpoints.laptop) return 'laptop';
    if (width >= breakpoints.tablet) return 'tablet';
    return 'mobile';
  }, [breakpoints]);

  // Enhanced breakpoint detection with hysteresis to prevent flickering
  const getBreakpointWithHysteresis = useCallback((width: number, currentBp: BreakpointName): BreakpointName => {
    const hysteresis = 20; // 20px buffer to prevent rapid switching
    
    switch (currentBp) {
      case 'desktop':
        if (width < breakpoints.laptop - hysteresis) return getCurrentBreakpoint(width);
        return 'desktop';
      case 'laptop':
        if (width >= breakpoints.desktop + hysteresis) return 'desktop';
        if (width < breakpoints.tablet - hysteresis) return getCurrentBreakpoint(width);
        return 'laptop';
      case 'tablet':
        if (width >= breakpoints.laptop + hysteresis) return getCurrentBreakpoint(width);
        if (width < breakpoints.mobile - hysteresis) return 'mobile';
        return 'tablet';
      case 'mobile':
        if (width >= breakpoints.tablet + hysteresis) return getCurrentBreakpoint(width);
        return 'mobile';
      default:
        return getCurrentBreakpoint(width);
    }
  }, [breakpoints, getCurrentBreakpoint]);

  // Handle breakpoint transitions
  const handleBreakpointTransition = useCallback((newBreakpoint: BreakpointName) => {
    if (newBreakpoint === currentBreakpoint) return;

    const transition: BreakpointTransition = {
      from: currentBreakpoint,
      to: newBreakpoint,
      timestamp: Date.now(),
      direction: getBreakpointOrder(newBreakpoint) > getBreakpointOrder(currentBreakpoint) ? 'up' : 'down'
    };

    setPreviousBreakpoint(currentBreakpoint);
    setCurrentBreakpoint(newBreakpoint);
    
    if (enableTransitionTracking) {
      setTransitionHistory(prev => [...prev.slice(-9), transition]); // Keep last 10 transitions
      setIsTransitioning(true);
      
      // Clear transition state after animation
      clearTimeout(transitionTimeoutRef.current);
      transitionTimeoutRef.current = setTimeout(() => {
        setIsTransitioning(false);
      }, 300); // Match CSS transition duration
    }

    onBreakpointChange?.(transition);
  }, [currentBreakpoint, enableTransitionTracking, onBreakpointChange]);

  // Helper function to get breakpoint order
  const getBreakpointOrder = useCallback((breakpoint: BreakpointName): number => {
    const order = { mobile: 0, tablet: 1, laptop: 2, desktop: 3 };
    return order[breakpoint];
  }, []);

  const getLayoutConfiguration = useCallback((): LayoutConfiguration => {
    const bp = currentBreakpoint;
    
    // Calculate adaptive dimensions based on actual screen size
    const calculateAdaptiveDimensions = () => {
      const availableWidth = screenSize.width;
      const availableHeight = screenSize.height;
      
      let sidebarWidth: number;
      let contentColumns: number[];
      
      switch (bp) {
        case 'desktop':
          sidebarWidth = Math.min(240, availableWidth * 0.15);
          const desktopContentWidth = availableWidth - sidebarWidth - 60; // 60px for padding
          const desktopColumnWidth = Math.floor(desktopContentWidth / 3);
          contentColumns = [desktopColumnWidth, desktopColumnWidth, desktopColumnWidth];
          break;
          
        case 'laptop':
          sidebarWidth = Math.min(200, availableWidth * 0.12);
          const laptopContentWidth = availableWidth - sidebarWidth - 40;
          const laptopColumnWidth = Math.floor(laptopContentWidth / 3);
          contentColumns = [laptopColumnWidth, laptopColumnWidth, laptopColumnWidth];
          break;
          
        case 'tablet':
          sidebarWidth = availableWidth > 900 ? Math.min(160, availableWidth * 0.1) : 0;
          const tabletContentWidth = availableWidth - sidebarWidth - 30;
          contentColumns = [tabletContentWidth];
          break;
          
        case 'mobile':
          sidebarWidth = 0;
          contentColumns = [availableWidth - 20];
          break;
          
        default:
          sidebarWidth = 240;
          contentColumns = [560, 560, 560];
      }
      
      return { sidebar: sidebarWidth, content: contentColumns };
    };

    const columns = adaptiveComponentSizing ? calculateAdaptiveDimensions() : {
      sidebar: bp === 'desktop' ? 240 : bp === 'laptop' ? 200 : bp === 'tablet' ? 160 : 0,
      content: bp === 'desktop' ? [560, 560, 560] : bp === 'laptop' ? [450, 450, 450] : [screenSize.width - 180]
    };

    // Enhanced component height calculation with adaptive sizing
    const getComponentHeight = (component: keyof typeof DEFAULT_COMPONENT_HEIGHTS) => {
      const baseHeight = DEFAULT_COMPONENT_HEIGHTS[component];
      
      if (!adaptiveComponentSizing) {
        // Simple breakpoint-based sizing
        switch (bp) {
          case 'mobile':
            return Math.max(baseHeight * 0.75, 250);
          case 'tablet':
            return Math.max(baseHeight * 0.85, 300);
          default:
            return baseHeight;
        }
      }
      
      // Adaptive sizing based on available screen space
      const availableHeight = screenSize.height - DEFAULT_COMPONENT_HEIGHTS.header - 100; // Reserve space for header and padding
      const scaleFactor = Math.min(1, availableHeight / (baseHeight * 4)); // Assume 4 components max
      
      let adaptedHeight = baseHeight * scaleFactor;
      
      // Apply breakpoint-specific adjustments
      switch (bp) {
        case 'mobile':
          adaptedHeight = Math.max(adaptedHeight * 0.8, 200);
          break;
        case 'tablet':
          adaptedHeight = Math.max(adaptedHeight * 0.9, 250);
          break;
        case 'laptop':
          adaptedHeight = Math.max(adaptedHeight * 0.95, 280);
          break;
      }
      
      return Math.floor(adaptedHeight);
    };

    // Determine component visibility based on breakpoint and available space
    const getComponentVisibility = (component: keyof typeof DEFAULT_COMPONENT_HEIGHTS) => {
      if (performanceMode && (bp === 'mobile' || bp === 'tablet')) {
        // In performance mode, hide non-essential components on smaller screens
        const essentialComponents = ['fileUploader', 'waveformPlayer'];
        return essentialComponents.includes(component);
      }
      return true;
    };

    // Calculate optimal component positions
    const getComponentPosition = (component: keyof typeof DEFAULT_COMPONENT_HEIGHTS) => {
      switch (component) {
        case 'fileUploader':
          return { column: 1, row: 1 };
        case 'waveformPlayer':
          return { 
            column: bp === 'mobile' ? 1 : 2, 
            row: bp === 'mobile' ? 2 : 1 
          };
        case 'chatInterface':
          return { 
            column: bp === 'tablet' || bp === 'mobile' ? 1 : 3, 
            row: bp === 'tablet' ? 3 : bp === 'mobile' ? 4 : 1 
          };
        case 'fileManager':
          return { 
            column: 1, 
            row: bp === 'mobile' ? 3 : 2 
          };
        default:
          return { column: 1, row: 1 };
      }
    };

    return {
      screenSize,
      columns,
      components: {
        header: {
          height: bp === 'mobile' ? 50 : DEFAULT_COMPONENT_HEIGHTS.header,
          visible: true,
          position: { column: 1, row: 1 }
        },
        fileUploader: {
          height: getComponentHeight('fileUploader'),
          visible: getComponentVisibility('fileUploader'),
          position: getComponentPosition('fileUploader')
        },
        waveformPlayer: {
          height: getComponentHeight('waveformPlayer'),
          visible: getComponentVisibility('waveformPlayer'),
          position: getComponentPosition('waveformPlayer')
        },
        chatInterface: {
          height: getComponentHeight('chatInterface'),
          visible: getComponentVisibility('chatInterface'),
          position: getComponentPosition('chatInterface')
        },
        fileManager: {
          height: getComponentHeight('fileManager'),
          visible: getComponentVisibility('fileManager'),
          position: getComponentPosition('fileManager')
        }
      }
    };
  }, [screenSize, currentBreakpoint, adaptiveComponentSizing, performanceMode]);

  const handleResize = useCallback(() => {
    const now = Date.now();
    lastResizeTimeRef.current = now;
    
    // Use requestAnimationFrame for smooth updates
    if (frameRequestRef.current) {
      cancelAnimationFrame(frameRequestRef.current);
    }
    
    frameRequestRef.current = requestAnimationFrame(() => {
      // Only update if this is the most recent resize event
      if (now === lastResizeTimeRef.current) {
        const newSize = {
          width: window.innerWidth,
          height: window.innerHeight
        };
        
        setScreenSize(newSize);
        
        // Use hysteresis for breakpoint detection to prevent flickering
        const newBreakpoint = getBreakpointWithHysteresis(newSize.width, currentBreakpoint);
        handleBreakpointTransition(newBreakpoint);
      }
    });
  }, [currentBreakpoint, getBreakpointWithHysteresis, handleBreakpointTransition]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Set initial breakpoint
    const initialBreakpoint = getCurrentBreakpoint(screenSize.width);
    setCurrentBreakpoint(initialBreakpoint);
    setPreviousBreakpoint(initialBreakpoint);

    // Enhanced resize handler with debouncing and throttling
    const debouncedResize = () => {
      clearTimeout(resizeTimeoutRef.current);
      resizeTimeoutRef.current = setTimeout(handleResize, debounceMs);
    };

    // Add multiple event listeners for comprehensive detection
    window.addEventListener('resize', debouncedResize, { passive: true });
    window.addEventListener('orientationchange', debouncedResize, { passive: true });
    
    // Listen for zoom changes (affects layout)
    const handleZoom = () => {
      // Delay to allow zoom to complete
      setTimeout(debouncedResize, 100);
    };
    
    window.addEventListener('wheel', handleZoom, { passive: true });
    
    return () => {
      window.removeEventListener('resize', debouncedResize);
      window.removeEventListener('orientationchange', debouncedResize);
      window.removeEventListener('wheel', handleZoom);
      
      // Cleanup timeouts and animation frames
      clearTimeout(resizeTimeoutRef.current);
      clearTimeout(transitionTimeoutRef.current);
      if (frameRequestRef.current) {
        cancelAnimationFrame(frameRequestRef.current);
      }
    };
  }, [handleResize, getCurrentBreakpoint, screenSize.width, debounceMs]);

  const isBreakpoint = useCallback((breakpoint: BreakpointName) => {
    return currentBreakpoint === breakpoint;
  }, [currentBreakpoint]);

  const isBreakpointOrSmaller = useCallback((breakpoint: BreakpointName) => {
    const order: BreakpointName[] = ['mobile', 'tablet', 'laptop', 'desktop'];
    const currentIndex = order.indexOf(currentBreakpoint);
    const targetIndex = order.indexOf(breakpoint);
    return currentIndex <= targetIndex;
  }, [currentBreakpoint]);

  const isBreakpointOrLarger = useCallback((breakpoint: BreakpointName) => {
    const order: BreakpointName[] = ['mobile', 'tablet', 'laptop', 'desktop'];
    const currentIndex = order.indexOf(currentBreakpoint);
    const targetIndex = order.indexOf(breakpoint);
    return currentIndex >= targetIndex;
  }, [currentBreakpoint]);

  // Enhanced utility functions
  const getBreakpointRange = useCallback((breakpoint: BreakpointName): { min: number; max: number } => {
    switch (breakpoint) {
      case 'mobile':
        return { min: 0, max: breakpoints.tablet - 1 };
      case 'tablet':
        return { min: breakpoints.tablet, max: breakpoints.laptop - 1 };
      case 'laptop':
        return { min: breakpoints.laptop, max: breakpoints.desktop - 1 };
      case 'desktop':
        return { min: breakpoints.desktop, max: Infinity };
    }
  }, [breakpoints]);

  const getOptimalColumnCount = useCallback((): number => {
    const availableWidth = screenSize.width - (currentBreakpoint === 'mobile' ? 0 : 240); // Account for sidebar
    const minColumnWidth = 300; // Minimum width for usable column
    return Math.max(1, Math.floor(availableWidth / minColumnWidth));
  }, [screenSize.width, currentBreakpoint]);

  const shouldUseCompactLayout = useCallback((): boolean => {
    return currentBreakpoint === 'mobile' || currentBreakpoint === 'tablet' || 
           (currentBreakpoint === 'laptop' && screenSize.height < 800);
  }, [currentBreakpoint, screenSize.height]);

  const getLayoutMetrics = useCallback(() => {
    const config = getLayoutConfiguration();
    const totalComponentHeight = Object.values(config.components)
      .filter(comp => comp.visible)
      .reduce((sum, comp) => sum + comp.height, 0);
    
    return {
      totalComponentHeight,
      availableHeight: screenSize.height - config.components.header.height,
      fitsOnScreen: totalComponentHeight <= (screenSize.height - config.components.header.height - 100),
      optimalColumnCount: getOptimalColumnCount(),
      shouldUseCompactLayout: shouldUseCompactLayout(),
      breakpointRange: getBreakpointRange(currentBreakpoint)
    };
  }, [getLayoutConfiguration, screenSize, getOptimalColumnCount, shouldUseCompactLayout, getBreakpointRange]);

  // Memoized values for performance
  const layoutConfiguration = useMemo(() => getLayoutConfiguration(), [getLayoutConfiguration]);
  const layoutMetrics = useMemo(() => getLayoutMetrics(), [getLayoutMetrics]);

  return {
    // Basic responsive data
    screenSize,
    currentBreakpoint,
    previousBreakpoint,
    layoutConfiguration,
    
    // Breakpoint utilities
    isBreakpoint,
    isBreakpointOrSmaller,
    isBreakpointOrLarger,
    isMobile: isBreakpoint('mobile'),
    isTablet: isBreakpoint('tablet'),
    isLaptop: isBreakpoint('laptop'),
    isDesktop: isBreakpoint('desktop'),
    
    // Enhanced utilities
    getBreakpointRange,
    getOptimalColumnCount,
    shouldUseCompactLayout,
    layoutMetrics,
    
    // Transition management
    isTransitioning,
    transitionHistory,
    
    // Configuration
    breakpoints,
    options: {
      debounceMs,
      enableTransitionTracking,
      adaptiveComponentSizing,
      performanceMode
    }
  };
};