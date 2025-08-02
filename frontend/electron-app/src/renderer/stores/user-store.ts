import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface UserProfile {
  id: string;
  name: string;
  email?: string;
  avatar?: string;
  preferences: UserPreferences;
  createdAt: Date;
  lastLoginAt: Date;
}

export interface UserPreferences {
  language: string;
  timezone: string;
  dateFormat: string;
  audioQuality: 'low' | 'medium' | 'high';
  autoSave: boolean;
  notifications: {
    desktop: boolean;
    sound: boolean;
    email: boolean;
  };
  privacy: {
    analytics: boolean;
    crashReports: boolean;
  };
  layoutPreferences?: {
    componentVisibility: {
      fileUploader: boolean;
      waveformPlayer: boolean;
      chatInterface: boolean;
      fileManager: boolean;
      sidebar: boolean;
    };
    componentHeights: {
      fileUploader: number;
      waveformPlayer: number;
      chatInterface: number;
      fileManager: number;
    };
    sidebarCollapsed: boolean;
    compactMode: boolean;
    autoHideComponents: boolean;
    columnOrder: [1, 2, 3] | [2, 1, 3] | [1, 3, 2] | [2, 3, 1] | [3, 1, 2] | [3, 2, 1];
    mobileLayoutMode: 'stack' | 'tabs' | 'accordion';
    tabletLayoutMode: 'two-column' | 'single-column';
  };
}

export interface UserState {
  // User data
  user: UserProfile | null;
  isAuthenticated: boolean;
  
  // Session data
  sessionId: string | null;
  lastActivity: Date | null;
  
  // Recent activity
  recentFiles: string[];
  recentProjects: string[];
  
  // Actions
  setUser: (user: UserProfile | null) => void;
  updateUserPreferences: (preferences: Partial<UserPreferences>) => void;
  setAuthenticated: (authenticated: boolean) => void;
  setSessionId: (sessionId: string | null) => void;
  updateLastActivity: () => void;
  addRecentFile: (filePath: string) => void;
  removeRecentFile: (filePath: string) => void;
  addRecentProject: (projectPath: string) => void;
  removeRecentProject: (projectPath: string) => void;
  clearRecentFiles: () => void;
  clearRecentProjects: () => void;
  logout: () => void;
}

// Default preferences are defined inline in the store

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        user: null,
        isAuthenticated: false,
        sessionId: null,
        lastActivity: null,
        recentFiles: [],
        recentProjects: [],

        // Actions
        setUser: (user: UserProfile | null) => {
          set(
            {
              user,
              isAuthenticated: user !== null,
              lastActivity: user ? new Date() : null,
            },
            false,
            'user/setUser'
          );
        },

        updateUserPreferences: (preferences: Partial<UserPreferences>) => {
          set(
            (state) => ({
              user: state.user
                ? {
                    ...state.user,
                    preferences: { ...state.user.preferences, ...preferences },
                  }
                : null,
            }),
            false,
            'user/updateUserPreferences'
          );
        },

        setAuthenticated: (authenticated: boolean) => {
          set({ isAuthenticated: authenticated }, false, 'user/setAuthenticated');
        },

        setSessionId: (sessionId: string | null) => {
          set({ sessionId }, false, 'user/setSessionId');
        },

        updateLastActivity: () => {
          set({ lastActivity: new Date() }, false, 'user/updateLastActivity');
        },

        addRecentFile: (filePath: string) => {
          set(
            (state) => {
              const filtered = state.recentFiles.filter((f) => f !== filePath);
              return {
                recentFiles: [filePath, ...filtered].slice(0, 10), // Keep only 10 recent files
              };
            },
            false,
            'user/addRecentFile'
          );
        },

        removeRecentFile: (filePath: string) => {
          set(
            (state) => ({
              recentFiles: state.recentFiles.filter((f) => f !== filePath),
            }),
            false,
            'user/removeRecentFile'
          );
        },

        addRecentProject: (projectPath: string) => {
          set(
            (state) => {
              const filtered = state.recentProjects.filter((p) => p !== projectPath);
              return {
                recentProjects: [projectPath, ...filtered].slice(0, 5), // Keep only 5 recent projects
              };
            },
            false,
            'user/addRecentProject'
          );
        },

        removeRecentProject: (projectPath: string) => {
          set(
            (state) => ({
              recentProjects: state.recentProjects.filter((p) => p !== projectPath),
            }),
            false,
            'user/removeRecentProject'
          );
        },

        clearRecentFiles: () => {
          set({ recentFiles: [] }, false, 'user/clearRecentFiles');
        },

        clearRecentProjects: () => {
          set({ recentProjects: [] }, false, 'user/clearRecentProjects');
        },

        logout: () => {
          set(
            {
              user: null,
              isAuthenticated: false,
              sessionId: null,
              lastActivity: null,
            },
            false,
            'user/logout'
          );
        },
      }),
      {
        name: 'user-store',
        // Only persist certain fields
        partialize: (state) => ({
          user: state.user,
          recentFiles: state.recentFiles,
          recentProjects: state.recentProjects,
        }),
      }
    ),
    {
      name: 'user-store',
    }
  )
);