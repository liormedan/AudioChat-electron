import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { PrivacySettings } from '../privacy-settings';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock URL.createObjectURL
global.URL.createObjectURL = vi.fn(() => 'mock-url');
global.URL.revokeObjectURL = vi.fn();

// Mock DOM methods
Object.defineProperty(document, 'createElement', {
  value: vi.fn(() => ({
    href: '',
    download: '',
    click: vi.fn(),
    remove: vi.fn()
  }))
});

Object.defineProperty(document.body, 'appendChild', {
  value: vi.fn()
});

Object.defineProperty(document.body, 'removeChild', {
  value: vi.fn()
});

describe('PrivacySettings', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    
    // Default mock responses
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/settings/privacy')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            localOnlyMode: false,
            dataRetentionDays: 90,
            encryptionEnabled: true,
            anonymousMode: false,
            telemetryEnabled: true,
            crashReportsEnabled: true,
            usageAnalyticsEnabled: false,
            autoDeleteEnabled: false,
            backupEnabled: true,
            cloudSyncEnabled: false
          })
        });
      }
      
      if (url.includes('/api/data/statistics')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            totalMessages: 150,
            totalSessions: 25,
            storageUsed: 1024000,
            oldestData: '2024-01-01T00:00:00Z',
            encryptedMessages: 150
          })
        });
      }
      
      if (url.includes('/api/security/encryption/status')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            encryption_enabled: true,
            current_key: {
              key_id: 'test-key-123',
              algorithm: 'AES-256-GCM',
              days_until_expiry: 25
            }
          })
        });
      }
      
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      });
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders privacy settings tabs', async () => {
    render(<PrivacySettings />);
    
    await waitFor(() => {
      expect(screen.getByText('כללי')).toBeInTheDocument();
      expect(screen.getByText('נתונים')).toBeInTheDocument();
      expect(screen.getByText('שמירה')).toBeInTheDocument();
      expect(screen.getByText('סטטוס')).toBeInTheDocument();
    });
  });

  it('loads and displays privacy settings', async () => {
    render(<PrivacySettings />);
    
    await waitFor(() => {
      expect(screen.getByText('הגדרות פרטיות כלליות')).toBeInTheDocument();
      expect(screen.getByText('מצב מקומי בלבד')).toBeInTheDocument();
      expect(screen.getByText('הצפנת הודעות')).toBeInTheDocument();
      expect(screen.getByText('מצב אנונימי')).toBeInTheDocument();
    });
  });

  it('displays data statistics', async () => {
    render(<PrivacySettings />);
    
    // Switch to data tab
    fireEvent.click(screen.getByText('נתונים'));
    
    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument(); // totalMessages
      expect(screen.getByText('25')).toBeInTheDocument(); // totalSessions
      expect(screen.getByText('1.00 MB')).toBeInTheDocument(); // storageUsed formatted
    });
  });

  it('shows encryption management section when encryption status is available', async () => {
    render(<PrivacySettings />);
    
    await waitFor(() => {
      expect(screen.getByText('ניהול הצפנה')).toBeInTheDocument();
      expect(screen.getByText('סטטוס הצפנה')).toBeInTheDocument();
      expect(screen.getByText('פעיל')).toBeInTheDocument();
      expect(screen.getByText('test-key-123')).toBeInTheDocument();
    });
  });

  it('handles local-only mode toggle', async () => {
    const onSettingsChange = vi.fn();
    render(<PrivacySettings onSettingsChange={onSettingsChange} />);
    
    await waitFor(() => {
      const localOnlySwitch = screen.getByRole('switch', { name: /מצב מקומי בלבד/i });
      expect(localOnlySwitch).toBeInTheDocument();
    });

    // Mock the POST request for saving settings
    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true })
      })
    );

    const localOnlySwitch = screen.getByRole('switch', { name: /מצב מקומי בלבד/i });
    fireEvent.click(localOnlySwitch);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/settings/privacy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: expect.stringContaining('"localOnlyMode":true')
      });
    });
  });

  it('handles encryption toggle', async () => {
    render(<PrivacySettings />);
    
    await waitFor(() => {
      const encryptionSwitch = screen.getByRole('switch', { name: /הצפנת הודעות/i });
      expect(encryptionSwitch).toBeInTheDocument();
    });

    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true })
      })
    );

    const encryptionSwitch = screen.getByRole('switch', { name: /הצפנת הודעות/i });
    fireEvent.click(encryptionSwitch);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/settings/privacy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: expect.stringContaining('"encryptionEnabled":false')
      });
    });
  });

  it('shows data retention settings', async () => {
    render(<PrivacySettings />);
    
    // Switch to retention tab
    fireEvent.click(screen.getByText('שמירה'));
    
    await waitFor(() => {
      expect(screen.getByText('מדיניות שמירת נתונים')).toBeInTheDocument();
      expect(screen.getByText('תקופת שמירה מותאמת: 90 ימים')).toBeInTheDocument();
      expect(screen.getByText('מחיקה אוטומטית')).toBeInTheDocument();
    });
  });

  it('shows predefined retention policies', async () => {
    render(<PrivacySettings />);
    
    // Switch to retention tab
    fireEvent.click(screen.getByText('שמירה'));
    
    await waitFor(() => {
      expect(screen.getByText('מינימלי')).toBeInTheDocument();
      expect(screen.getByText('סטנדרטי')).toBeInTheDocument();
      expect(screen.getByText('מורחב')).toBeInTheDocument();
    });
  });

  it('displays privacy indicators', async () => {
    render(<PrivacySettings />);
    
    // Switch to indicators tab
    fireEvent.click(screen.getByText('סטטוס'));
    
    await waitFor(() => {
      expect(screen.getByText('אינדיקטורי פרטיות')).toBeInTheDocument();
      expect(screen.getByText('הצפנה פעילה')).toBeInTheDocument();
      expect(screen.getByText('מצב רגיל')).toBeInTheDocument();
    });
  });

  it('opens clear data dialog', async () => {
    render(<PrivacySettings />);
    
    // Switch to data tab
    fireEvent.click(screen.getByText('נתונים'));
    
    await waitFor(() => {
      const clearButton = screen.getByText('מחק את כל הנתונים');
      fireEvent.click(clearButton);
    });

    await waitFor(() => {
      expect(screen.getByText('מחיקת כל הנתונים')).toBeInTheDocument();
      expect(screen.getByText('פעולה זו תמחק את כל הנתונים המקומיים')).toBeInTheDocument();
    });
  });

  it('opens export data dialog', async () => {
    render(<PrivacySettings />);
    
    // Switch to data tab
    fireEvent.click(screen.getByText('נתונים'));
    
    await waitFor(() => {
      const exportButton = screen.getByText('ייצא את כל הנתונים');
      fireEvent.click(exportButton);
    });

    await waitFor(() => {
      expect(screen.getByText('ייצוא נתונים')).toBeInTheDocument();
      expect(screen.getByText('ייצוא כל הנתונים המקומיים לקובץ JSON')).toBeInTheDocument();
    });
  });

  it('handles data export', async () => {
    render(<PrivacySettings />);
    
    // Switch to data tab and open export dialog
    fireEvent.click(screen.getByText('נתונים'));
    
    await waitFor(() => {
      const exportButton = screen.getByText('ייצא את כל הנתונים');
      fireEvent.click(exportButton);
    });

    // Mock successful export
    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        blob: () => Promise.resolve(new Blob(['test data'], { type: 'application/json' }))
      })
    );

    await waitFor(() => {
      const confirmExportButton = screen.getByText('ייצא נתונים');
      fireEvent.click(confirmExportButton);
    });

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/data/export');
    });
  });

  it('handles encryption key rotation', async () => {
    render(<PrivacySettings />);
    
    await waitFor(() => {
      const rotateButton = screen.getByText('רוטציה של מפתחות הצפנה');
      expect(rotateButton).toBeInTheDocument();
    });

    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true, new_key_id: 'new-key-456' })
      })
    );

    const rotateButton = screen.getByText('רוטציה של מפתחות הצפנה');
    fireEvent.click(rotateButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/security/encryption/rotate-keys', {
        method: 'POST'
      });
    });
  });

  it('opens migration dialog', async () => {
    render(<PrivacySettings />);
    
    await waitFor(() => {
      const migrateButton = screen.getByText('העבר הודעות קיימות להצפנה');
      fireEvent.click(migrateButton);
    });

    await waitFor(() => {
      expect(screen.getByText('העברה להצפנה')).toBeInTheDocument();
      expect(screen.getByText('פעולה זו תעביר את כל ההודעות הקיימות להצפנה')).toBeInTheDocument();
    });
  });

  it('handles encryption migration', async () => {
    render(<PrivacySettings />);
    
    // Open migration dialog
    await waitFor(() => {
      const migrateButton = screen.getByText('העבר הודעות קיימות להצפנה');
      fireEvent.click(migrateButton);
    });

    // Mock successful migration
    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ 
          success: true, 
          migrated_count: 100,
          failed_count: 0,
          total_messages: 100
        })
      })
    );

    await waitFor(() => {
      const startMigrationButton = screen.getByText('התחל העברה');
      fireEvent.click(startMigrationButton);
    });

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/security/encryption/migrate', {
        method: 'POST'
      });
    });
  });

  it('disables telemetry and crash reports when anonymous mode is enabled', async () => {
    render(<PrivacySettings />);
    
    await waitFor(() => {
      const anonymousSwitch = screen.getByRole('switch', { name: /מצב אנונימי/i });
      expect(anonymousSwitch).toBeInTheDocument();
    });

    // Enable anonymous mode
    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true })
      })
    );

    const anonymousSwitch = screen.getByRole('switch', { name: /מצב אנונימי/i });
    fireEvent.click(anonymousSwitch);

    await waitFor(() => {
      const telemetrySwitch = screen.getByRole('switch', { name: /טלמטריה/i });
      const crashReportsSwitch = screen.getByRole('switch', { name: /דוחות קריסות/i });
      
      expect(telemetrySwitch).toBeDisabled();
      expect(crashReportsSwitch).toBeDisabled();
    });
  });

  it('shows local-only mode alert when enabled', async () => {
    // Mock settings with local-only mode enabled
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/settings/privacy')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            localOnlyMode: true,
            dataRetentionDays: 90,
            encryptionEnabled: true,
            anonymousMode: false,
            telemetryEnabled: true,
            crashReportsEnabled: true,
            usageAnalyticsEnabled: false,
            autoDeleteEnabled: false,
            backupEnabled: true,
            cloudSyncEnabled: false
          })
        });
      }
      
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      });
    });

    render(<PrivacySettings />);
    
    await waitFor(() => {
      expect(screen.getByText('מצב מקומי בלבד פעיל')).toBeInTheDocument();
      expect(screen.getByText('כל הנתונים נשמרים מקומית בלבד. לא יישלחו נתונים לשרתים חיצוניים.')).toBeInTheDocument();
    });
  });
});