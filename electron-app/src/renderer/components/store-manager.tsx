import React, { useEffect } from 'react';
import { useSettingsStore } from '../stores';
import { useNotifications } from '../hooks/use-app-state';

interface StoreManagerProps {
  children: React.ReactNode;
}

export const StoreManager: React.FC<StoreManagerProps> = ({ children }) => {
  const { addNotification } = useNotifications();
  const { hasUnsavedChanges, saveSettings } = useSettingsStore();
  
  // Auto-save settings when there are unsaved changes
  useEffect(() => {
    if (!hasUnsavedChanges) return;
    
    const autoSaveTimeout = setTimeout(async () => {
      try {
        await saveSettings();
      } catch (error) {
        addNotification({
          type: 'error',
          title: 'Auto-save Failed',
          message: 'Failed to automatically save settings. Please save manually.',
          duration: 10000, // Show longer for errors
        });
      }
    }, 2000); // Auto-save after 2 seconds of inactivity
    
    return () => clearTimeout(autoSaveTimeout);
  }, [hasUnsavedChanges, saveSettings, addNotification]);
  
  // Handle app shutdown - save any unsaved changes
  useEffect(() => {
    const handleBeforeUnload = async (event: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        event.preventDefault();
        event.returnValue = 'You have unsaved changes. Are you sure you want to exit?';
        
        try {
          await saveSettings();
        } catch (error) {
          console.error('Failed to save settings on exit:', error);
        }
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasUnsavedChanges, saveSettings]);
  
  // Handle visibility change - save when app becomes hidden
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.hidden && hasUnsavedChanges) {
        try {
          await saveSettings();
        } catch (error) {
          console.error('Failed to save settings on visibility change:', error);
        }
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [hasUnsavedChanges, saveSettings]);
  
  return <>{children}</>;
};