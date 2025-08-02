import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useUserStore } from '../stores';
import { 
  LayoutConfiguration, 
  ComponentConfig,
  DEFAULT_COMPONENT_HEIGHTS,
  DEFAULT_BREAKPOINTS,
  BreakpointName 
} from '../components/layout/types';

export interface LayoutPreferences {
  // Component visibility preferences
  componentVisibility: {
    fileUploader: boolean;
    waveformPlayer: boolean;
    chatInterface: boolean;
    fileManager: boolean;
    sidebar: boolean;
  };
  
  // Component size preferences
  componentHeights: {
    fileUploader: number;
    waveformPlayer: number;
    chatInterface: number;
    fileManager: number;
  };
  
  // Layout preferences
  sidebarCollapsed: boolean;
  compactMode: boolean;
  autoHideComponents: boolean;
  
  // Column preferences
  columnOrder: [1, 2, 3] | [2, 1, 3] | [1, 3, 2] | [2, 3, 1] | [3, 1, 2] | [3, 2, 1];
  
  // Responsive preferences
  mobileLayoutMode: 'stack' | 'tabs' | 'accordion';
  tabletLayoutMode: 'two-column' | 'single-column';
}

export interface LayoutConfigurationContextValue {
  // Current configuration
  layoutConfiguration: LayoutConfiguration;
  layoutPreferences: LayoutPreferences;
  currentBreakpoint: BreakpointName;
  
  // Actions
  updateLayoutPreferences: (preferences: Partial<LayoutPreferences>) => void;
  resetLayoutPreferences: () => void;
  toggleComponentVisibility: (component: keyof LayoutPreferences['componentVisibility']) => void;
  updateComponentHeight: (component: keyof LayoutPreferences['componentHeights'], height: number) => void;
  toggleSidebar: () => void;
  toggleCompactMode: () => void;
  
  // Utility functions
  isComponentVisible: (component: keyof LayoutPreferences['componentVisibility']) => boolean;
  getComponentHeight: (component: keyof LayoutPreferences['componentHeights']) => number;
  canFitAllComponents: () => boolean;
}

const DEFAULT_LAYOUT_PREFERENCES: LayoutPreferences = {
  componentVisibility: {
    fileUploader: true,
    waveformPlayer: true,
    chatInterface: true,
    fileManager: true,
    sidebar: true,
  },
  componentHeights: {
    fileUploader: DEFAULT_COMPONENT_HEIGHTS.fileUploader,
    waveformPlayer: DEFAULT_COMPONENT_HEIGHTS.waveformPlayer,
    chatInterface: DEFAULT_COMPONENT_HEIGHTS.chatInterface,
    fileManager: DEFAULT_COMPONENT_HEIGHTS.fileManager,
  },
  sidebarCollapsed: false,
  compactMode: false,
  autoHideComponents: true,
  columnOrder: [1, 2, 3],
  mobileLayoutMode: 'stack',
  tabletLayoutMode: 'two-column',
};

const LayoutConfigurationContext = createContext<LayoutConfigurationContextValue | null>(null);

export interface LayoutConfigurationProviderProps {
  children: React.ReactNode;
  initialBreakpoint?: BreakpointName;
}

export const LayoutConfigurationProvider: React.FC<LayoutConfigurationProviderProps> = ({ 
  children, 
  initialBreakpoint = 'desktop' 
}) => {
  const { user, updateUserPreferences } = useUserStore();
  
  // Get saved preferences from user store or use defaults
  const savedPreferences = user?.preferences?.layoutPreferences as LayoutPreferences | undefined;
  const [layoutPreferences, setLayoutPreferences] = useState<LayoutPreferences>(
    savedPreferences || DEFAULT_LAYOUT_PREFERENCES
  );
  
  const [currentBreakpoint, setCurrentBreakpoint] = useState<BreakpointName>(initialBreakpoint);
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1920,
    height: typeof window !== 'undefined' ? window.innerHeight : 1080
  });

  // Update breakpoint based on screen size
  const updateBreakpoint = useCallback((width: number) => {
    let newBreakpoint: BreakpointName;
    if (width >= DEFAULT_BREAKPOINTS.desktop) newBreakpoint = 'desktop';
    else if (width >= DEFAULT_BREAKPOINTS.laptop) newBreakpoint = 'laptop';
    else if (width >= DEFAULT_BREAKPOINTS.tablet) newBreakpoint = 'tablet';
    else newBreakpoint = 'mobile';
    
    setCurrentBreakpoint(newBreakpoint);
  }, []);

  // Handle window resize
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleResize = () => {
      const newSize = {
        width: window.innerWidth,
        height: window.innerHeight
      };
      setScreenSize(newSize);
      updateBreakpoint(newSize.width);
    };

    // Set initial breakpoint
    updateBreakpoint(screenSize.width);

    // Add resize listener with debouncing
    let timeoutId: NodeJS.Timeout;
    const debouncedResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleResize, 150);
    };

    window.addEventListener('resize', debouncedResize);
    
    return () => {
      window.removeEventListener('resize', debouncedResize);
      clearTimeout(timeoutId);
    };
  }, [updateBreakpoint, screenSize.width]);

  // Generate layout configuration based on current preferences and breakpoint
  const generateLayoutConfiguration = useCallback((): LayoutConfiguration => {
    // Adjust for breakpoint
    let sidebarWidth: number;
    let contentColumns: number[];
    
    switch (currentBreakpoint) {
      case 'desktop':
        sidebarWidth = layoutPreferences.sidebarCollapsed ? 60 : 240;
        contentColumns = [560, 560, 560];
        break;
      case 'laptop':
        sidebarWidth = layoutPreferences.sidebarCollapsed ? 50 : 200;
        contentColumns = [450, 450, 450];
        break;
      case 'tablet':
        sidebarWidth = layoutPreferences.componentVisibility.sidebar ? 160 : 0;
        contentColumns = [screenSize.width - sidebarWidth - 40];
        break;
      case 'mobile':
        sidebarWidth = 0;
        contentColumns = [screenSize.width - 20];
        break;
    }

    // Apply compact mode adjustments
    if (layoutPreferences.compactMode) {
      Object.keys(layoutPreferences.componentHeights).forEach(key => {
        const componentKey = key as keyof typeof layoutPreferences.componentHeights;
        layoutPreferences.componentHeights[componentKey] = Math.floor(
          layoutPreferences.componentHeights[componentKey] * 0.8
        );
      });
    }

    // Create component configurations
    const createComponentConfig = (
      component: keyof LayoutPreferences['componentVisibility'],
      defaultPosition: { column: number; row: number }
    ): ComponentConfig => ({
      height: layoutPreferences.componentHeights[component as keyof LayoutPreferences['componentHeights']] || 200,
      visible: layoutPreferences.componentVisibility[component],
      collapsed: false,
      position: defaultPosition
    });

    return {
      screenSize,
      columns: {
        sidebar: sidebarWidth,
        content: contentColumns
      },
      components: {
        header: {
          height: currentBreakpoint === 'mobile' ? 50 : DEFAULT_COMPONENT_HEIGHTS.header,
          visible: true,
          position: { column: 1, row: 1 }
        },
        fileUploader: createComponentConfig('fileUploader', { column: 1, row: 1 }),
        waveformPlayer: createComponentConfig('waveformPlayer', { column: 2, row: 1 }),
        chatInterface: createComponentConfig('chatInterface', { 
          column: currentBreakpoint === 'tablet' || currentBreakpoint === 'mobile' ? 1 : 3, 
          row: currentBreakpoint === 'tablet' || currentBreakpoint === 'mobile' ? 3 : 1 
        }),
        fileManager: createComponentConfig('fileManager', { column: 1, row: 2 })
      }
    };
  }, [layoutPreferences, currentBreakpoint, screenSize]);

  const layoutConfiguration = generateLayoutConfiguration();

  // Actions
  const updateLayoutPreferences = useCallback((preferences: Partial<LayoutPreferences>) => {
    const newPreferences = { ...layoutPreferences, ...preferences };
    setLayoutPreferences(newPreferences);
    
    // Save to user store
    updateUserPreferences({ 
      layoutPreferences: newPreferences 
    } as any);
  }, [layoutPreferences, updateUserPreferences]);

  const resetLayoutPreferences = useCallback(() => {
    setLayoutPreferences(DEFAULT_LAYOUT_PREFERENCES);
    updateUserPreferences({ 
      layoutPreferences: DEFAULT_LAYOUT_PREFERENCES 
    } as any);
  }, [updateUserPreferences]);

  const toggleComponentVisibility = useCallback((component: keyof LayoutPreferences['componentVisibility']) => {
    updateLayoutPreferences({
      componentVisibility: {
        ...layoutPreferences.componentVisibility,
        [component]: !layoutPreferences.componentVisibility[component]
      }
    });
  }, [layoutPreferences.componentVisibility, updateLayoutPreferences]);

  const updateComponentHeight = useCallback((
    component: keyof LayoutPreferences['componentHeights'], 
    height: number
  ) => {
    updateLayoutPreferences({
      componentHeights: {
        ...layoutPreferences.componentHeights,
        [component]: Math.max(100, Math.min(800, height)) // Clamp between 100-800px
      }
    });
  }, [layoutPreferences.componentHeights, updateLayoutPreferences]);

  const toggleSidebar = useCallback(() => {
    updateLayoutPreferences({
      sidebarCollapsed: !layoutPreferences.sidebarCollapsed
    });
  }, [layoutPreferences.sidebarCollapsed, updateLayoutPreferences]);

  const toggleCompactMode = useCallback(() => {
    updateLayoutPreferences({
      compactMode: !layoutPreferences.compactMode
    });
  }, [layoutPreferences.compactMode, updateLayoutPreferences]);

  // Utility functions
  const isComponentVisible = useCallback((component: keyof LayoutPreferences['componentVisibility']) => {
    return layoutPreferences.componentVisibility[component];
  }, [layoutPreferences.componentVisibility]);

  const getComponentHeight = useCallback((component: keyof LayoutPreferences['componentHeights']) => {
    return layoutPreferences.componentHeights[component];
  }, [layoutPreferences.componentHeights]);

  const canFitAllComponents = useCallback(() => {
    const totalHeight = Object.values(layoutPreferences.componentHeights)
      .filter((_, index) => Object.values(layoutPreferences.componentVisibility)[index])
      .reduce((sum, height) => sum + height, 0);
    
    return totalHeight <= (screenSize.height - DEFAULT_COMPONENT_HEIGHTS.header - 100); // 100px for padding/margins
  }, [layoutPreferences, screenSize.height]);

  const contextValue: LayoutConfigurationContextValue = {
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
  };

  return (
    <LayoutConfigurationContext.Provider value={contextValue}>
      {children}
    </LayoutConfigurationContext.Provider>
  );
};

export const useLayoutConfiguration = (): LayoutConfigurationContextValue => {
  const context = useContext(LayoutConfigurationContext);
  if (!context) {
    throw new Error('useLayoutConfiguration must be used within a LayoutConfigurationProvider');
  }
  return context;
};