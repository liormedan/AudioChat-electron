import { useState, useEffect, useCallback, useRef } from 'react';
import { BreakpointName } from '../components/layout/types';
import { useResponsiveLayout, BreakpointTransition } from './use-responsive-layout';

export interface LayoutTransitionConfig {
  duration: number;
  easing: string;
  staggerDelay: number;
  enableAnimations: boolean;
}

export interface ResponsiveLayoutTransitionsOptions {
  transitionConfig?: Partial<LayoutTransitionConfig>;
  onTransitionStart?: (transition: BreakpointTransition) => void;
  onTransitionEnd?: (transition: BreakpointTransition) => void;
  onComponentResize?: (component: string, newHeight: number) => void;
  enablePreloading?: boolean;
}

const DEFAULT_TRANSITION_CONFIG: LayoutTransitionConfig = {
  duration: 300,
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
  staggerDelay: 50,
  enableAnimations: true
};

export const useResponsiveLayoutTransitions = (
  options: ResponsiveLayoutTransitionsOptions = {}
) => {
  const {
    transitionConfig = {},
    onTransitionStart,
    onTransitionEnd,
    onComponentResize,
    enablePreloading = true
  } = options;

  const config = { ...DEFAULT_TRANSITION_CONFIG, ...transitionConfig };
  
  const {
    currentBreakpoint,
    previousBreakpoint,
    isTransitioning,
    transitionHistory,
    layoutConfiguration,
    screenSize
  } = useResponsiveLayout({
    enableTransitionTracking: true,
    onBreakpointChange: (transition) => {
      handleTransitionStart(transition);
    }
  });

  const [activeTransitions, setActiveTransitions] = useState<Set<string>>(new Set());
  const [preloadedLayouts, setPreloadedLayouts] = useState<Map<BreakpointName, any>>(new Map());
  const transitionTimeoutRefs = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Handle transition start
  const handleTransitionStart = useCallback((transition: BreakpointTransition) => {
    onTransitionStart?.(transition);
    
    // Add CSS classes for transition animations
    if (config.enableAnimations && typeof document !== 'undefined') {
      document.documentElement.classList.add('layout-transitioning');
      document.documentElement.classList.add(`transition-${transition.direction}`);
      document.documentElement.classList.add(`from-${transition.from}`);
      document.documentElement.classList.add(`to-${transition.to}`);
    }
  }, [onTransitionStart, config.enableAnimations]);

  // Handle transition end
  const handleTransitionEnd = useCallback((transition: BreakpointTransition) => {
    onTransitionEnd?.(transition);
    
    // Remove CSS classes
    if (config.enableAnimations && typeof document !== 'undefined') {
      document.documentElement.classList.remove('layout-transitioning');
      document.documentElement.classList.remove(`transition-${transition.direction}`);
      document.documentElement.classList.remove(`from-${transition.from}`);
      document.documentElement.classList.remove(`to-${transition.to}`);
    }
  }, [onTransitionEnd, config.enableAnimations]);

  // Preload layouts for smooth transitions
  const preloadLayout = useCallback((breakpoint: BreakpointName) => {
    if (!enablePreloading || preloadedLayouts.has(breakpoint)) return;
    
    // Simulate layout calculation for the target breakpoint
    // This would be more complex in a real implementation
    const preloadedLayout = {
      breakpoint,
      timestamp: Date.now(),
      // Add preloaded layout data here
    };
    
    setPreloadedLayouts(prev => new Map(prev).set(breakpoint, preloadedLayout));
  }, [enablePreloading, preloadedLayouts]);

  // Component transition management
  const startComponentTransition = useCallback((componentId: string, newHeight: number) => {
    setActiveTransitions(prev => new Set(prev).add(componentId));
    
    // Clear existing timeout
    const existingTimeout = transitionTimeoutRefs.current.get(componentId);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }
    
    // Set new timeout
    const timeout = setTimeout(() => {
      setActiveTransitions(prev => {
        const newSet = new Set(prev);
        newSet.delete(componentId);
        return newSet;
      });
      transitionTimeoutRefs.current.delete(componentId);
      onComponentResize?.(componentId, newHeight);
    }, config.duration);
    
    transitionTimeoutRefs.current.set(componentId, timeout);
  }, [config.duration, onComponentResize]);

  // Get transition styles for components
  const getTransitionStyles = useCallback((componentId: string) => {
    if (!config.enableAnimations) return {};
    
    const isActive = activeTransitions.has(componentId);
    const delay = Array.from(activeTransitions).indexOf(componentId) * config.staggerDelay;
    
    return {
      transition: `all ${config.duration}ms ${config.easing}`,
      transitionDelay: `${delay}ms`,
      willChange: isActive ? 'transform, opacity, height, width' : 'auto'
    };
  }, [activeTransitions, config]);

  // Get layout transition classes
  const getLayoutClasses = useCallback(() => {
    const classes = [];
    
    if (isTransitioning) {
      classes.push('layout-transitioning');
    }
    
    classes.push(`breakpoint-${currentBreakpoint}`);
    
    if (previousBreakpoint !== currentBreakpoint) {
      classes.push(`from-${previousBreakpoint}`);
      classes.push(`to-${currentBreakpoint}`);
    }
    
    return classes.join(' ');
  }, [isTransitioning, currentBreakpoint, previousBreakpoint]);

  // Preload adjacent breakpoints
  useEffect(() => {
    if (!enablePreloading) return;
    
    const breakpointOrder: BreakpointName[] = ['mobile', 'tablet', 'laptop', 'desktop'];
    const currentIndex = breakpointOrder.indexOf(currentBreakpoint);
    
    // Preload adjacent breakpoints
    if (currentIndex > 0) {
      preloadLayout(breakpointOrder[currentIndex - 1]);
    }
    if (currentIndex < breakpointOrder.length - 1) {
      preloadLayout(breakpointOrder[currentIndex + 1]);
    }
  }, [currentBreakpoint, enablePreloading, preloadLayout]);

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      transitionTimeoutRefs.current.forEach(timeout => clearTimeout(timeout));
      transitionTimeoutRefs.current.clear();
    };
  }, []);

  // Monitor component height changes
  useEffect(() => {
    const components = layoutConfiguration.components;
    Object.entries(components).forEach(([componentId, config]) => {
      if (config.visible) {
        startComponentTransition(componentId, config.height);
      }
    });
  }, [layoutConfiguration.components, startComponentTransition]);

  return {
    // Transition state
    isTransitioning,
    activeTransitions: Array.from(activeTransitions),
    transitionHistory,
    
    // Transition utilities
    getTransitionStyles,
    getLayoutClasses,
    startComponentTransition,
    
    // Preloading
    preloadedLayouts: Array.from(preloadedLayouts.entries()),
    preloadLayout,
    
    // Configuration
    transitionConfig: config,
    
    // Callbacks
    handleTransitionStart,
    handleTransitionEnd
  };
};