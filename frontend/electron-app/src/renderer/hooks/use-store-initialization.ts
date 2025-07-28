import { useEffect, useState } from 'react';
import { useSettingsStore, useUserStore, useUIStore } from '../stores';

export const useStoreInitialization = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [initializationError, setInitializationError] = useState<string | null>(null);
  
  useEffect(() => {
    const initializeStores = async () => {
      try {
        setInitializationError(null);
        
        // Get store instances
        const settingsStore = useSettingsStore.getState();
        const uiStore = useUIStore.getState();
        const userStore = useUserStore.getState();
        
        // Load settings (this is mostly a no-op since persist middleware handles it)
        await settingsStore.loadSettings();
        
        // Apply theme based on settings
        const themePreference = settingsStore.settings.ui.theme;
        if (themePreference === 'system') {
          // Detect system theme
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          uiStore.setTheme(prefersDark ? 'dark' : 'light');
          
          // Listen for system theme changes
          const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
          const handleThemeChange = (e: MediaQueryListEvent) => {
            uiStore.setTheme(e.matches ? 'dark' : 'light');
          };
          
          mediaQuery.addEventListener('change', handleThemeChange);
          
          // Return cleanup function for theme listener
          const cleanup = () => {
            mediaQuery.removeEventListener('change', handleThemeChange);
          };
          
          // Store cleanup for later use
          (window as any).__themeCleanup = cleanup;
        } else {
          uiStore.setTheme(themePreference as 'light' | 'dark');
        }
        
        // Update user activity
        userStore.updateLastActivity();
        
        // Set up activity tracking
        const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        let activityTimeout: NodeJS.Timeout;
        
        const handleActivity = () => {
          clearTimeout(activityTimeout);
          activityTimeout = setTimeout(() => {
            userStore.updateLastActivity();
          }, 30000); // Update every 30 seconds of activity
        };
        
        activityEvents.forEach(event => {
          document.addEventListener(event, handleActivity, true);
        });
        
        // Store activity cleanup
        (window as any).__activityCleanup = () => {
          activityEvents.forEach(event => {
            document.removeEventListener(event, handleActivity, true);
          });
          clearTimeout(activityTimeout);
        };
        
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize stores:', error);
        setInitializationError(error instanceof Error ? error.message : 'Unknown error');
        setIsInitialized(true); // Still mark as initialized to prevent infinite loading
      }
    };
    
    // Small delay to ensure stores are ready
    const timer = setTimeout(() => {
      initializeStores();
    }, 100);
    
    // Cleanup function
    return () => {
      clearTimeout(timer);
      if ((window as any).__themeCleanup) {
        (window as any).__themeCleanup();
      }
      if ((window as any).__activityCleanup) {
        (window as any).__activityCleanup();
      }
    };
  }, []); // Empty dependency array - only run once on mount
  
  return {
    isInitialized,
    initializationError,
  };
};