import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface UIState {
  // Current page state
  currentPage: string;
  
  // Sidebar state
  sidebarCollapsed: boolean;
  
  // Theme state
  theme: 'light' | 'dark';
  
  // Loading states
  isLoading: boolean;
  loadingMessage: string | undefined;
  
  // Notification state
  notifications: Notification[];
  
  // Modal/Dialog state
  activeModal: string | null;
  
  // Actions
  setCurrentPage: (page: string) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setLoading: (loading: boolean, message?: string) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  setActiveModal: (modal: string | null) => void;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  timestamp: number;
}

export const useUIStore = create<UIState>()(
  devtools(
    (set, get) => ({
      // Initial state
      currentPage: 'home',
      sidebarCollapsed: false,
      theme: 'dark',
      isLoading: false,
      loadingMessage: undefined,
      notifications: [],
      activeModal: null,

      // Actions
      setCurrentPage: (page: string) => {
        set({ currentPage: page }, false, 'ui/setCurrentPage');
      },

      toggleSidebar: () => {
        set(
          (state) => ({ sidebarCollapsed: !state.sidebarCollapsed }),
          false,
          'ui/toggleSidebar'
        );
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed }, false, 'ui/setSidebarCollapsed');
      },

      setTheme: (theme: 'light' | 'dark') => {
        set({ theme }, false, 'ui/setTheme');
        // Apply theme to document
        document.documentElement.classList.toggle('dark', theme === 'dark');
      },

      setLoading: (loading: boolean, message?: string) => {
        set(
          { isLoading: loading, loadingMessage: message || undefined },
          false,
          'ui/setLoading'
        );
      },

      addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => {
        const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const newNotification: Notification = {
          ...notification,
          id,
          timestamp: Date.now(),
        };

        set(
          (state) => ({
            notifications: [...state.notifications, newNotification],
          }),
          false,
          'ui/addNotification'
        );

        // Auto-remove notification after duration (default 5 seconds)
        const duration = notification.duration ?? 5000;
        if (duration > 0) {
          setTimeout(() => {
            get().removeNotification(id);
          }, duration);
        }
      },

      removeNotification: (id: string) => {
        set(
          (state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }),
          false,
          'ui/removeNotification'
        );
      },

      clearNotifications: () => {
        set({ notifications: [] }, false, 'ui/clearNotifications');
      },

      setActiveModal: (modal: string | null) => {
        set({ activeModal: modal }, false, 'ui/setActiveModal');
      },
    }),
    {
      name: 'ui-store',
    }
  )
);