import { useState, useEffect, useCallback } from 'react';
import { 
  LayoutConfiguration, 
  ResponsiveBreakpoints, 
  DEFAULT_BREAKPOINTS, 
  DEFAULT_COMPONENT_HEIGHTS,
  BreakpointName 
} from '../components/layout/types';

export const useResponsiveLayout = (
  customBreakpoints?: Partial<ResponsiveBreakpoints>
) => {
  const breakpoints = { ...DEFAULT_BREAKPOINTS, ...customBreakpoints };
  
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1920,
    height: typeof window !== 'undefined' ? window.innerHeight : 1080
  });

  const [currentBreakpoint, setCurrentBreakpoint] = useState<BreakpointName>('desktop');

  const getCurrentBreakpoint = useCallback((width: number): BreakpointName => {
    if (width >= breakpoints.desktop) return 'desktop';
    if (width >= breakpoints.laptop) return 'laptop';
    if (width >= breakpoints.tablet) return 'tablet';
    return 'mobile';
  }, [breakpoints]);

  const getLayoutConfiguration = useCallback((): LayoutConfiguration => {
    const bp = getCurrentBreakpoint(screenSize.width);
    
    // Define column configurations based on breakpoint
    let columns: { sidebar: number; content: number[] };
    
    switch (bp) {
      case 'desktop':
        columns = { sidebar: 240, content: [560, 560, 560] };
        break;
      case 'laptop':
        columns = { sidebar: 200, content: [450, 450, 450] };
        break;
      case 'tablet':
        columns = { sidebar: 160, content: [screenSize.width - 180] };
        break;
      case 'mobile':
        columns = { sidebar: 0, content: [screenSize.width - 20] };
        break;
    }

    // Adjust component heights based on breakpoint
    const getComponentHeight = (component: keyof typeof DEFAULT_COMPONENT_HEIGHTS) => {
      const baseHeight = DEFAULT_COMPONENT_HEIGHTS[component];
      switch (bp) {
        case 'mobile':
          return Math.max(baseHeight * 0.75, 250);
        case 'tablet':
          return Math.max(baseHeight * 0.85, 300);
        default:
          return baseHeight;
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
          visible: true,
          position: { column: 1, row: 1 }
        },
        waveformPlayer: {
          height: getComponentHeight('waveformPlayer'),
          visible: true,
          position: { column: 2, row: 1 }
        },
        chatInterface: {
          height: getComponentHeight('chatInterface'),
          visible: true,
          position: { column: bp === 'tablet' || bp === 'mobile' ? 1 : 3, row: bp === 'tablet' || bp === 'mobile' ? 2 : 1 }
        },
        fileManager: {
          height: getComponentHeight('fileManager'),
          visible: true,
          position: { column: 1, row: 2 }
        }
      }
    };
  }, [screenSize, getCurrentBreakpoint]);

  const handleResize = useCallback(() => {
    const newSize = {
      width: window.innerWidth,
      height: window.innerHeight
    };
    
    setScreenSize(newSize);
    setCurrentBreakpoint(getCurrentBreakpoint(newSize.width));
  }, [getCurrentBreakpoint]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Set initial breakpoint
    setCurrentBreakpoint(getCurrentBreakpoint(screenSize.width));

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
  }, [handleResize, getCurrentBreakpoint, screenSize.width]);

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

  return {
    screenSize,
    currentBreakpoint,
    layoutConfiguration: getLayoutConfiguration(),
    isBreakpoint,
    isBreakpointOrSmaller,
    isBreakpointOrLarger,
    isMobile: isBreakpoint('mobile'),
    isTablet: isBreakpoint('tablet'),
    isLaptop: isBreakpoint('laptop'),
    isDesktop: isBreakpoint('desktop')
  };
};