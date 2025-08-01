import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface AppSettings {
  // Application settings
  app: {
    startMinimized: boolean;
    minimizeToTray: boolean;
    closeToTray: boolean;
    autoStart: boolean;
    checkForUpdates: boolean;
    updateChannel: 'stable' | 'beta' | 'alpha';
  };
  
  // Audio settings
  audio: {
    defaultFormat: string;
    defaultQuality: number;
    outputDirectory: string;
    maxFileSize: number; // in MB
    enablePreview: boolean;
    previewVolume: number;
  };
  
  // UI settings
  ui: {
    theme: 'light' | 'dark' | 'system';
    fontSize: 'small' | 'medium' | 'large';
    compactMode: boolean;
    showTooltips: boolean;
    animationsEnabled: boolean;
    sidebarWidth: number;
  };
  
  // Performance settings
  performance: {
    maxConcurrentJobs: number;
    enableHardwareAcceleration: boolean;
    memoryLimit: number; // in MB
    cacheSize: number; // in MB
    enableLogging: boolean;
    logLevel: 'error' | 'warn' | 'info' | 'debug';
  };
  
  // Privacy settings
  privacy: {
    sendAnalytics: boolean;
    sendCrashReports: boolean;
    saveHistory: boolean;
    clearHistoryOnExit: boolean;
  };
  
  // Keyboard shortcuts
  shortcuts: Record<string, string>;
  
  // Advanced settings
  advanced: {
    developerMode: boolean;
    experimentalFeatures: boolean;
    customCSSEnabled: boolean;
    customCSS: string;
  };
}

export interface SettingsState {
  // Settings data
  settings: AppSettings;
  
  // Settings state
  isLoading: boolean;
  hasUnsavedChanges: boolean;
  lastSaved: Date | null;
  
  // Actions
  updateSettings: (settings: Partial<AppSettings>) => void;
  updateAppSettings: (appSettings: Partial<AppSettings['app']>) => void;
  updateAudioSettings: (audioSettings: Partial<AppSettings['audio']>) => void;
  updateUISettings: (uiSettings: Partial<AppSettings['ui']>) => void;
  updatePerformanceSettings: (performanceSettings: Partial<AppSettings['performance']>) => void;
  updatePrivacySettings: (privacySettings: Partial<AppSettings['privacy']>) => void;
  updateShortcuts: (shortcuts: Partial<Record<string, string>>) => void;
  updateAdvancedSettings: (advancedSettings: Partial<AppSettings['advanced']>) => void;
  resetSettings: () => void;
  resetSection: (section: keyof AppSettings) => void;
  resetAllSettings: () => void;
  saveSettings: () => Promise<void>;
  loadSettings: () => Promise<void>;
  exportSettings: () => string;
  importSettings: (settingsJson: string) => boolean;
}

const defaultSettings: AppSettings = {
  app: {
    startMinimized: false,
    minimizeToTray: true,
    closeToTray: false,
    autoStart: false,
    checkForUpdates: true,
    updateChannel: 'stable',
  },
  audio: {
    defaultFormat: 'mp3',
    defaultQuality: 320,
    outputDirectory: '',
    maxFileSize: 500,
    enablePreview: true,
    previewVolume: 0.8,
  },
  ui: {
    theme: 'dark',
    fontSize: 'medium',
    compactMode: false,
    showTooltips: true,
    animationsEnabled: true,
    sidebarWidth: 280,
  },
  performance: {
    maxConcurrentJobs: 3,
    enableHardwareAcceleration: true,
    memoryLimit: 1024,
    cacheSize: 256,
    enableLogging: true,
    logLevel: 'info',
  },
  privacy: {
    sendAnalytics: false,
    sendCrashReports: true,
    saveHistory: true,
    clearHistoryOnExit: false,
  },
  shortcuts: {
    'file.open': 'Ctrl+O',
    'file.save': 'Ctrl+S',
    'file.export': 'Ctrl+E',
    'edit.undo': 'Ctrl+Z',
    'edit.redo': 'Ctrl+Y',
    'view.toggleSidebar': 'Ctrl+B',
    'view.toggleTheme': 'Ctrl+Shift+T',
    'audio.play': 'Space',
    'audio.stop': 'Escape',
  },
  advanced: {
    developerMode: false,
    experimentalFeatures: false,
    customCSSEnabled: false,
    customCSS: '',
  },
};

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        settings: defaultSettings,
        isLoading: false,
        hasUnsavedChanges: false,
        lastSaved: null,

        // Actions
        updateSettings: (newSettings: Partial<AppSettings>) => {
          set(
            (state) => ({
              settings: { ...state.settings, ...newSettings },
              hasUnsavedChanges: true,
            }),
            false,
            'settings/updateSettings'
          );
        },

        updateAppSettings: (appSettings: Partial<AppSettings['app']>) => {
          set(
            (state) => ({
              settings: {
                ...state.settings,
                app: { ...state.settings.app, ...appSettings },
              },
              hasUnsavedChanges: true,
            }),
            false,
            'settings/updateAppSettings'
          );
        },

        updateAudioSettings: (audioSettings: Partial<AppSettings['audio']>) => {
          set(
            (state) => ({
              settings: {
                ...state.settings,
                audio: { ...state.settings.audio, ...audioSettings },
              },
              hasUnsavedChanges: true,
            }),
            false,
            'settings/updateAudioSettings'
          );
        },

        updateUISettings: (uiSettings: Partial<AppSettings['ui']>) => {
          set(
            (state) => ({
              settings: {
                ...state.settings,
                ui: { ...state.settings.ui, ...uiSettings },
              },
              hasUnsavedChanges: true,
            }),
            false,
            'settings/updateUISettings'
          );
        },

        updatePerformanceSettings: (performanceSettings: Partial<AppSettings['performance']>) => {
          set(
            (state) => ({
              settings: {
                ...state.settings,
                performance: { ...state.settings.performance, ...performanceSettings },
              },
              hasUnsavedChanges: true,
            }),
            false,
            'settings/updatePerformanceSettings'
          );
        },

        updatePrivacySettings: (privacySettings: Partial<AppSettings['privacy']>) => {
          set(
            (state) => ({
              settings: {
                ...state.settings,
                privacy: { ...state.settings.privacy, ...privacySettings },
              },
              hasUnsavedChanges: true,
            }),
            false,
            'settings/updatePrivacySettings'
          );
        },

        updateShortcuts: (shortcuts: Partial<Record<string, string>>) => {
          set(
            (state) => {
              const filteredShortcuts: Record<string, string> = {};
              Object.entries(shortcuts).forEach(([key, value]) => {
                if (value !== undefined) {
                  filteredShortcuts[key] = value;
                }
              });
              
              return {
                ...state,
                settings: {
                  ...state.settings,
                  shortcuts: { ...state.settings.shortcuts, ...filteredShortcuts },
                },
                hasUnsavedChanges: true,
              };
            },
            false,
            'settings/updateShortcuts'
          );
        },

        updateAdvancedSettings: (advancedSettings: Partial<AppSettings['advanced']>) => {
          set(
            (state) => ({
              settings: {
                ...state.settings,
                advanced: { ...state.settings.advanced, ...advancedSettings },
              },
              hasUnsavedChanges: true,
            }),
            false,
            'settings/updateAdvancedSettings'
          );
        },

        resetSettings: () => {
          set(
            {
              settings: defaultSettings,
              hasUnsavedChanges: true,
            },
            false,
            'settings/resetSettings'
          );
        },

        resetSection: (section: keyof AppSettings) => {
          set(
            (state) => ({
              settings: {
                ...state.settings,
                [section]: defaultSettings[section],
              },
              hasUnsavedChanges: true,
            }),
            false,
            'settings/resetSection'
          );
        },

        resetAllSettings: () => {
          set(
            {
              settings: defaultSettings,
              hasUnsavedChanges: true,
            },
            false,
            'settings/resetAllSettings'
          );
        },

        saveSettings: async () => {
          set({ isLoading: true }, false, 'settings/saveSettings/start');
          
          try {
            // Here we would typically save to electron's main process via IPC
            // For now, we'll just simulate the save operation
            await new Promise(resolve => setTimeout(resolve, 100));
            
            set(
              {
                isLoading: false,
                hasUnsavedChanges: false,
                lastSaved: new Date(),
              },
              false,
              'settings/saveSettings/success'
            );
          } catch (error) {
            set({ isLoading: false }, false, 'settings/saveSettings/error');
            throw error;
          }
        },

        loadSettings: async () => {
          // Settings are automatically loaded by Zustand persist middleware
          // This function is mainly for future IPC integration
          set(
            {
              isLoading: false,
              hasUnsavedChanges: false,
              lastSaved: new Date(),
            },
            false,
            'settings/loadSettings/success'
          );
        },

        exportSettings: () => {
          const { settings } = get();
          return JSON.stringify(settings, null, 2);
        },

        importSettings: (settingsJson: string) => {
          try {
            const importedSettings = JSON.parse(settingsJson) as AppSettings;
            
            // Validate the imported settings structure
            if (typeof importedSettings !== 'object' || !importedSettings.app) {
              return false;
            }
            
            set(
              {
                settings: { ...defaultSettings, ...importedSettings },
                hasUnsavedChanges: true,
              },
              false,
              'settings/importSettings'
            );
            
            return true;
          } catch (error) {
            return false;
          }
        },
      }),
      {
        name: 'settings-store',
        // Persist all settings
        partialize: (state) => ({
          settings: state.settings,
          lastSaved: state.lastSaved,
        }),
      }
    ),
    {
      name: 'settings-store',
    }
  )
);