import { useUIStore, useUserStore, useSettingsStore } from '../stores';
// Types are imported directly from store files when needed

// Custom hooks for easier state access and mutations

// UI State hooks
export const useCurrentPage = () => useUIStore((state) => state.currentPage);
export const useSetCurrentPage = () => useUIStore((state) => state.setCurrentPage);

export const useSidebar = () => useUIStore((state) => ({
  collapsed: state.sidebarCollapsed,
  toggle: state.toggleSidebar,
  setCollapsed: state.setSidebarCollapsed,
}));

export const useTheme = () => useUIStore((state) => ({
  theme: state.theme,
  setTheme: state.setTheme,
}));

export const useLoading = () => useUIStore((state) => ({
  isLoading: state.isLoading,
  message: state.loadingMessage,
  setLoading: state.setLoading,
}));

export const useNotifications = () => useUIStore((state) => ({
  notifications: state.notifications,
  addNotification: state.addNotification,
  removeNotification: state.removeNotification,
  clearNotifications: state.clearNotifications,
}));

export const useModal = () => useUIStore((state) => ({
  activeModal: state.activeModal,
  setActiveModal: state.setActiveModal,
}));

// User State hooks
export const useUser = () => useUserStore((state) => ({
  user: state.user,
  isAuthenticated: state.isAuthenticated,
  setUser: state.setUser,
  logout: state.logout,
}));

export const useUserPreferences = () => useUserStore((state) => ({
  preferences: state.user?.preferences,
  updatePreferences: state.updateUserPreferences,
}));

export const useRecentFiles = () => useUserStore((state) => ({
  recentFiles: state.recentFiles,
  addRecentFile: state.addRecentFile,
  removeRecentFile: state.removeRecentFile,
  clearRecentFiles: state.clearRecentFiles,
}));

export const useRecentProjects = () => useUserStore((state) => ({
  recentProjects: state.recentProjects,
  addRecentProject: state.addRecentProject,
  removeRecentProject: state.removeRecentProject,
  clearRecentProjects: state.clearRecentProjects,
}));

export const useSession = () => useUserStore((state) => ({
  sessionId: state.sessionId,
  lastActivity: state.lastActivity,
  setSessionId: state.setSessionId,
  updateLastActivity: state.updateLastActivity,
}));

// Settings State hooks
export const useAppSettings = () => useSettingsStore((state) => ({
  settings: state.settings.app,
  updateSettings: state.updateAppSettings,
}));

export const useAudioSettings = () => useSettingsStore((state) => ({
  settings: state.settings.audio,
  updateSettings: state.updateAudioSettings,
}));

export const useUISettings = () => useSettingsStore((state) => ({
  settings: state.settings.ui,
  updateSettings: state.updateUISettings,
}));

export const usePerformanceSettings = () => useSettingsStore((state) => ({
  settings: state.settings.performance,
  updateSettings: state.updatePerformanceSettings,
}));

export const usePrivacySettings = () => useSettingsStore((state) => ({
  settings: state.settings.privacy,
  updateSettings: state.updatePrivacySettings,
}));

export const useShortcuts = () => useSettingsStore((state) => ({
  shortcuts: state.settings.shortcuts,
  updateShortcuts: state.updateShortcuts,
}));

export const useAdvancedSettings = () => useSettingsStore((state) => ({
  settings: state.settings.advanced,
  updateSettings: state.updateAdvancedSettings,
}));

export const useSettingsActions = () => useSettingsStore((state) => ({
  isLoading: state.isLoading,
  hasUnsavedChanges: state.hasUnsavedChanges,
  lastSaved: state.lastSaved,
  saveSettings: state.saveSettings,
  loadSettings: state.loadSettings,
  resetSettings: state.resetSettings,
  resetSection: state.resetSection,
  exportSettings: state.exportSettings,
  importSettings: state.importSettings,
}));

// Combined hooks for common use cases
export const useAppTheme = () => {
  const uiTheme = useTheme();
  const uiSettings = useUISettings();
  
  return {
    currentTheme: uiTheme.theme,
    systemTheme: uiSettings.settings.theme,
    setUITheme: uiTheme.setTheme,
    setSystemTheme: (theme: 'light' | 'dark' | 'system') => 
      uiSettings.updateSettings({ theme }),
  };
};

export const useAppState = () => {
  const ui = useUIStore();
  const user = useUserStore();
  const settings = useSettingsStore();
  
  return {
    ui,
    user,
    settings,
  };
};