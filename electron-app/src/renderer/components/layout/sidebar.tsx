import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Home, 
  Music, 
  Download, 
  BarChart3, 
  Bot, 
  User, 
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { Button } from '../ui/button';
import { useUIStore } from '../../stores/ui-store';
import { cn } from '../../lib/utils';

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  description?: string;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'home',
    label: 'Home',
    icon: Home,
    path: '/',
    description: 'Dashboard and overview'
  },
  {
    id: 'audio',
    label: 'Audio Actions',
    icon: Music,
    path: '/audio',
    description: 'Audio processing and editing'
  },
  {
    id: 'export',
    label: 'Export',
    icon: Download,
    path: '/export',
    description: 'Export and download files'
  },
  {
    id: 'stats',
    label: 'File Stats',
    icon: BarChart3,
    path: '/stats',
    description: 'File statistics and analytics'
  },
  {
    id: 'llm',
    label: 'LLM Manager',
    icon: Bot,
    path: '/llm',
    description: 'AI model management'
  },
  {
    id: 'profile',
    label: 'Profile',
    icon: User,
    path: '/profile',
    description: 'User profile and preferences'
  }
];

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarCollapsed, toggleSidebar, setCurrentPage } = useUIStore();

  const handleNavigation = (item: NavigationItem) => {
    setCurrentPage(item.id);
    navigate(item.path);
  };

  return (
    <aside 
      className={cn(
        "fixed left-0 top-0 h-full bg-card border-r border-border transition-all duration-300 ease-in-out z-50",
        sidebarCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!sidebarCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Music className="w-4 h-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-sm font-semibold">Audio Chat Studio</h1>
              <p className="text-xs text-muted-foreground">Electron Version</p>
            </div>
          </div>
        )}
        
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleSidebar}
          className="h-8 w-8 p-0"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2">
        <ul className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.id}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start h-10 px-3",
                    sidebarCollapsed && "px-2 justify-center"
                  )}
                  onClick={() => handleNavigation(item)}
                  title={sidebarCollapsed ? item.label : undefined}
                >
                  <Icon className={cn(
                    "h-4 w-4",
                    !sidebarCollapsed && "mr-3"
                  )} />
                  {!sidebarCollapsed && (
                    <span className="text-sm">{item.label}</span>
                  )}
                </Button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-2 border-t border-border">
        <Button
          variant="ghost"
          className={cn(
            "w-full justify-start h-10 px-3",
            sidebarCollapsed && "px-2 justify-center"
          )}
          onClick={() => handleNavigation({
            id: 'settings',
            label: 'Settings',
            icon: Settings,
            path: '/settings'
          })}
          title={sidebarCollapsed ? 'Settings' : undefined}
        >
          <Settings className={cn(
            "h-4 w-4",
            !sidebarCollapsed && "mr-3"
          )} />
          {!sidebarCollapsed && (
            <span className="text-sm">Settings</span>
          )}
        </Button>
      </div>
    </aside>
  );
};