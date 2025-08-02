import { useCallback, useMemo } from 'react';
import { useLayoutConfiguration } from '../contexts/layout-configuration-context';
import { BreakpointName } from '../components/layout/types';

export interface UseLayoutConfigurationReturn {
  // Configuration data
  layoutConfiguration: ReturnType<typeof useLayoutConfiguration>['layoutConfiguration'];
  layoutPreferences: ReturnType<typeof useLayoutConfiguration>['layoutPreferences'];
  currentBreakpoint: BreakpointName;
  
  // Component management
  isComponentVisible: (component: string) => boolean;
  getComponentHeight: (component: string) => number;
  toggleComponentVisibility: (component: string) => void;
  updateComponentHeight: (component: string, height: number) => void;
  
  // Layout management
  toggleSidebar: () => void;
  toggleCompactMode: () => void;
  resetLayout: () => void;
  
  // Responsive utilities
  isMobile: boolean;
  isTablet: boolean;
  isLaptop: boolean;
  isDesktop: boolean;
  isBreakpointOrSmaller: (breakpoint: BreakpointName) => boolean;
  isBreakpointOrLarger: (breakpoint: BreakpointName) => boolean;
  
  // Layout utilities
  canFitAllComponents: () => boolean;
  getOptimalLayout: () => 'single-column' | 'two-column' | 'three-column';
  shouldShowComponent: (component: string) => boolean;
  getColumnCount: () => number;
  
  // Performance utilities
  isCompactMode: boolean;
  shouldUseVirtualScrolling: boolean;
  shouldLazyLoad: boolean;
}

export const useLayoutConfigurationHook = (): UseLayoutConfigurationReturn => {
  const {
    layoutConfiguration,
    layoutPreferences,
    currentBreakpoint,
    updateLayoutPreferences,
    resetLayoutPreferences,
    toggleComponentVisibility,
    updateComponentHeight,
    toggleSidebar,
    toggleCompactMode,
    isComponentVisible,
    getComponentHeight,
    canFitAllComponents
  } = useLayoutConfiguration();

  // Responsive utilities
  const isMobile = currentBreakpoint === 'mobile';
  const isTablet = currentBreakpoint === 'tablet';
  const isLaptop = currentBreakpoint === 'laptop';
  const isDesktop = currentBreakpoint === 'desktop';

  const isBreakpointOrSmaller = useCallback((breakpoint: BreakpointName): boolean => {
    const order: BreakpointName[] = ['mobile', 'tablet', 'laptop', 'desktop'];
    const currentIndex = order.indexOf(currentBreakpoint);
    const targetIndex = order.indexOf(breakpoint);
    return currentIndex <= targetIndex;
  }, [currentBreakpoint]);

  const isBreakpointOrLarger = useCallback((breakpoint: BreakpointName): boolean => {
    const order: BreakpointName[] = ['mobile', 'tablet', 'laptop', 'desktop'];
    const currentIndex = order.indexOf(currentBreakpoint);
    const targetIndex = order.indexOf(breakpoint);
    return currentIndex >= targetIndex;
  }, [currentBreakpoint]);

  // Layout utilities
  const getOptimalLayout = useCallback((): 'single-column' | 'two-column' | 'three-column' => {
    if (isMobile) return 'single-column';
    if (isTablet) return layoutPreferences.tabletLayoutMode === 'single-column' ? 'single-column' : 'two-column';
    if (isLaptop && !canFitAllComponents()) return 'two-column';
    return 'three-column';
  }, [isMobile, isTablet, isLaptop, layoutPreferences.tabletLayoutMode, canFitAllComponents]);

  const shouldShowComponent = useCallback((component: string): boolean => {
    const componentKey = component as keyof typeof layoutPreferences.componentVisibility;
    
    // Check if component is visible in preferences
    if (!isComponentVisible(componentKey)) return false;
    
    // Auto-hide components on smaller screens if enabled
    if (layoutPreferences.autoHideComponents) {
      if (isMobile) {
        // On mobile, only show essential components
        return ['fileUploader', 'waveformPlayer'].includes(component);
      }
      if (isTablet) {
        // On tablet, hide less essential components
        return component !== 'fileManager';
      }
    }
    
    return true;
  }, [isComponentVisible, layoutPreferences.autoHideComponents, isMobile, isTablet]);

  const getColumnCount = useCallback((): number => {
    const layout = getOptimalLayout();
    switch (layout) {
      case 'single-column': return 1;
      case 'two-column': return 2;
      case 'three-column': return 3;
      default: return 3;
    }
  }, [getOptimalLayout]);

  // Performance utilities
  const isCompactMode = layoutPreferences.compactMode;
  
  const shouldUseVirtualScrolling = useMemo(() => {
    // Use virtual scrolling on mobile/tablet or when in compact mode
    return isMobile || isTablet || isCompactMode;
  }, [isMobile, isTablet, isCompactMode]);

  const shouldLazyLoad = useMemo(() => {
    // Use lazy loading on smaller screens or when many components are visible
    const visibleComponents = Object.values(layoutPreferences.componentVisibility)
      .filter(Boolean).length;
    return isMobile || isTablet || visibleComponents > 3;
  }, [isMobile, isTablet, layoutPreferences.componentVisibility]);

  // Enhanced component management
  const enhancedToggleComponentVisibility = useCallback((component: string) => {
    const componentKey = component as keyof typeof layoutPreferences.componentVisibility;
    toggleComponentVisibility(componentKey);
  }, [toggleComponentVisibility]);

  const enhancedUpdateComponentHeight = useCallback((component: string, height: number) => {
    const componentKey = component as keyof typeof layoutPreferences.componentHeights;
    updateComponentHeight(componentKey, height);
  }, [updateComponentHeight]);

  const enhancedIsComponentVisible = useCallback((component: string): boolean => {
    const componentKey = component as keyof typeof layoutPreferences.componentVisibility;
    return isComponentVisible(componentKey);
  }, [isComponentVisible]);

  const enhancedGetComponentHeight = useCallback((component: string): number => {
    const componentKey = component as keyof typeof layoutPreferences.componentHeights;
    return getComponentHeight(componentKey);
  }, [getComponentHeight]);

  return {
    // Configuration data
    layoutConfiguration,
    layoutPreferences,
    currentBreakpoint,
    
    // Component management
    isComponentVisible: enhancedIsComponentVisible,
    getComponentHeight: enhancedGetComponentHeight,
    toggleComponentVisibility: enhancedToggleComponentVisibility,
    updateComponentHeight: enhancedUpdateComponentHeight,
    
    // Layout management
    toggleSidebar,
    toggleCompactMode,
    resetLayout: resetLayoutPreferences,
    
    // Responsive utilities
    isMobile,
    isTablet,
    isLaptop,
    isDesktop,
    isBreakpointOrSmaller,
    isBreakpointOrLarger,
    
    // Layout utilities
    canFitAllComponents,
    getOptimalLayout,
    shouldShowComponent,
    getColumnCount,
    
    // Performance utilities
    isCompactMode,
    shouldUseVirtualScrolling,
    shouldLazyLoad
  };
};