import { useCallback, useMemo, useRef, useEffect, useState } from 'react';
import { debounce, throttle } from 'lodash-es';

/**
 * Performance optimization hooks
 * Hooks מותאמים לאופטימיזציה של ביצועים
 */

// Hook for debounced values
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Hook for debounced callbacks
export const useDebouncedCallback = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
  deps: React.DependencyList = []
): T => {
  const debouncedCallback = useMemo(
    () => debounce(callback, delay),
    [callback, delay, ...deps]
  );

  useEffect(() => {
    return () => {
      debouncedCallback.cancel();
    };
  }, [debouncedCallback]);

  return debouncedCallback as T;
};

// Hook for throttled callbacks
export const useThrottledCallback = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
  deps: React.DependencyList = []
): T => {
  const throttledCallback = useMemo(
    () => throttle(callback, delay),
    [callback, delay, ...deps]
  );

  useEffect(() => {
    return () => {
      throttledCallback.cancel();
    };
  }, [throttledCallback]);

  return throttledCallback as T;
};

// Hook for memoized expensive calculations
export const useExpensiveCalculation = <T>(
  calculation: () => T,
  deps: React.DependencyList
): T => {
  return useMemo(calculation, deps);
};

// Hook for previous value
export const usePrevious = <T>(value: T): T | undefined => {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};

// Hook for stable callback references
export const useStableCallback = <T extends (...args: any[]) => any>(
  callback: T
): T => {
  const callbackRef = useRef(callback);
  
  useEffect(() => {
    callbackRef.current = callback;
  });

  return useCallback((...args: any[]) => {
    return callbackRef.current(...args);
  }, []) as T;
};

// Hook for intersection observer (for lazy loading)
export const useIntersectionObserver = (
  options: IntersectionObserverInit = {}
) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);
  const elementRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
        setEntry(entry);
      },
      options
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [options]);

  return { elementRef, isIntersecting, entry };
};

// Hook for measuring render performance
export const useRenderPerformance = (componentName: string) => {
  const renderStartTime = useRef<number>(0);
  const renderCount = useRef<number>(0);

  useEffect(() => {
    renderStartTime.current = performance.now();
    renderCount.current += 1;
  });

  useEffect(() => {
    const renderTime = performance.now() - renderStartTime.current;
    if (process.env.NODE_ENV === 'development') {
      console.log(`${componentName} render #${renderCount.current}: ${renderTime.toFixed(2)}ms`);
    }
  });

  return {
    renderCount: renderCount.current,
    markRenderStart: () => {
      renderStartTime.current = performance.now();
    },
    markRenderEnd: () => {
      const renderTime = performance.now() - renderStartTime.current;
      if (process.env.NODE_ENV === 'development') {
        console.log(`${componentName} render time: ${renderTime.toFixed(2)}ms`);
      }
      return renderTime;
    }
  };
};

// Hook for virtual scrolling calculations
export const useVirtualScrolling = (
  itemCount: number,
  itemHeight: number,
  containerHeight: number,
  scrollTop: number = 0
) => {
  return useMemo(() => {
    const visibleItemCount = Math.ceil(containerHeight / itemHeight);
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(startIndex + visibleItemCount + 1, itemCount - 1);
    const totalHeight = itemCount * itemHeight;
    const offsetY = startIndex * itemHeight;

    return {
      startIndex,
      endIndex,
      visibleItemCount,
      totalHeight,
      offsetY,
      visibleItems: Array.from(
        { length: endIndex - startIndex + 1 },
        (_, index) => startIndex + index
      )
    };
  }, [itemCount, itemHeight, containerHeight, scrollTop]);
};

// Hook for lazy loading with intersection observer
export const useLazyLoading = <T>(
  items: T[],
  batchSize: number = 20,
  threshold: number = 0.1
) => {
  const [loadedCount, setLoadedCount] = useState(batchSize);
  const { elementRef, isIntersecting } = useIntersectionObserver({
    threshold
  });

  useEffect(() => {
    if (isIntersecting && loadedCount < items.length) {
      setLoadedCount(prev => Math.min(prev + batchSize, items.length));
    }
  }, [isIntersecting, loadedCount, items.length, batchSize]);

  const visibleItems = useMemo(
    () => items.slice(0, loadedCount),
    [items, loadedCount]
  );

  const hasMore = loadedCount < items.length;

  return {
    visibleItems,
    hasMore,
    loadMoreRef: elementRef,
    loadedCount,
    totalCount: items.length
  };
};

// Hook for optimized search
export const useOptimizedSearch = <T>(
  items: T[],
  searchTerm: string,
  searchFields: (keyof T)[],
  debounceMs: number = 300
) => {
  const debouncedSearchTerm = useDebounce(searchTerm, debounceMs);

  const filteredItems = useMemo(() => {
    if (!debouncedSearchTerm.trim()) {
      return items;
    }

    const searchLower = debouncedSearchTerm.toLowerCase();
    return items.filter(item =>
      searchFields.some(field => {
        const value = item[field];
        return typeof value === 'string' && 
               value.toLowerCase().includes(searchLower);
      })
    );
  }, [items, debouncedSearchTerm, searchFields]);

  return {
    filteredItems,
    isSearching: searchTerm !== debouncedSearchTerm,
    searchTerm: debouncedSearchTerm
  };
};

// Hook for memory usage monitoring
export const useMemoryMonitor = () => {
  const [memoryInfo, setMemoryInfo] = useState<{
    usedJSHeapSize: number;
    totalJSHeapSize: number;
    jsHeapSizeLimit: number;
  } | null>(null);

  useEffect(() => {
    const updateMemoryInfo = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        setMemoryInfo({
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit
        });
      }
    };

    updateMemoryInfo();
    const interval = setInterval(updateMemoryInfo, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return memoryInfo;
};

// Hook for component size monitoring
export const useComponentSize = () => {
  const [size, setSize] = useState({ width: 0, height: 0 });
  const elementRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setSize({ width, height });
      }
    });

    resizeObserver.observe(element);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  return { elementRef, size };
};

// Hook for optimized event handlers
export const useOptimizedEventHandlers = () => {
  const handlersRef = useRef<Map<string, (...args: any[]) => void>>(new Map());

  const getHandler = useCallback((key: string, handler: (...args: any[]) => void) => {
    if (!handlersRef.current.has(key)) {
      handlersRef.current.set(key, handler);
    }
    return handlersRef.current.get(key)!;
  }, []);

  const clearHandlers = useCallback(() => {
    handlersRef.current.clear();
  }, []);

  return { getHandler, clearHandlers };
};