import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUIStore } from '../stores/ui-store';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  metaKey?: boolean;
  action: () => void;
  description: string;
}

export const useKeyboardShortcuts = () => {
  const navigate = useNavigate();
  const { toggleSidebar, setCurrentPage } = useUIStore();

  const shortcuts: KeyboardShortcut[] = [
    // Navigation shortcuts
    {
      key: '1',
      ctrlKey: true,
      action: () => {
        setCurrentPage('home');
        navigate('/');
      },
      description: 'Go to Home'
    },
    {
      key: '2',
      ctrlKey: true,
      action: () => {
        setCurrentPage('audio');
        navigate('/audio');
      },
      description: 'Go to Audio Processing'
    },
    {
      key: '3',
      ctrlKey: true,
      action: () => {
        setCurrentPage('export');
        navigate('/export');
      },
      description: 'Go to Export'
    },
    {
      key: '4',
      ctrlKey: true,
      action: () => {
        setCurrentPage('stats');
        navigate('/stats');
      },
      description: 'Go to File Statistics'
    },
    {
      key: '5',
      ctrlKey: true,
      action: () => {
        setCurrentPage('llm');
        navigate('/llm');
      },
      description: 'Go to AI Assistant'
    },
    {
      key: '6',
      ctrlKey: true,
      action: () => {
        setCurrentPage('profile');
        navigate('/profile');
      },
      description: 'Go to Profile'
    },
    // UI shortcuts
    {
      key: 'b',
      ctrlKey: true,
      action: toggleSidebar,
      description: 'Toggle Sidebar'
    },
    {
      key: ',',
      ctrlKey: true,
      action: () => {
        setCurrentPage('settings');
        navigate('/settings');
      },
      description: 'Open Settings'
    }
  ];

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in input fields
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.contentEditable === 'true'
      ) {
        return;
      }

      const matchingShortcut = shortcuts.find(shortcut => {
        return (
          shortcut.key.toLowerCase() === event.key.toLowerCase() &&
          !!shortcut.ctrlKey === event.ctrlKey &&
          !!shortcut.altKey === event.altKey &&
          !!shortcut.shiftKey === event.shiftKey &&
          !!shortcut.metaKey === event.metaKey
        );
      });

      if (matchingShortcut) {
        event.preventDefault();
        event.stopPropagation();
        matchingShortcut.action();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [navigate, setCurrentPage, toggleSidebar]);

  return { shortcuts };
};