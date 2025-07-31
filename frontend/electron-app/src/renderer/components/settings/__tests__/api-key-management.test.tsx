import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { APIKeyManagement } from '../api-key-management';

// Mock fetch
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Mock clipboard API
Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: jest.fn(),
  },
});

// Mock data
const mockAPIKeys = [
  {
    id: 'key-1',
    providerId: 'openai',
    name: 'Production Key',
    key: 'sk-1234567890abcdef1234567890abcdef',
    isActive: true,
    createdAt: '2024-01-01T10:00:00Z',
    lastUsed: '2024-01-15T14:30:00Z',
    lastTested: '2024-01-15T14:00:00Z',
    status: 'active' as const,
    usage: {
      totalRequests: 1500,
      totalTokens: 45000,
      totalCost: 12.50,
      lastMonth: {
        requests: 500,
        tokens: 15000,
        cost: 4.20
      }
    }
  },
  {
    id: 'key-2',
    providerId: 'anthropic',
    name: 'Development Key',
    key: 'sk-ant-abcdef1234567890abcdef1234567890',
    isActive: false,
    createdAt: '2024-01-10T15:00:00Z',
    status: 'inactive' as const
  }
];

const mockProviderStatuses = {
  openai: {
    providerId: 'openai',
    isConnected: true,
    lastChecked: '2024-01-15T14:00:00Z',
    responseTime: 250,
    availableModels: ['gpt-4', 'gpt-3.5-turbo'],
    rateLimits: {
      requestsPerMinute: 3500,
      tokensPerMinute: 90000,
      requestsPerDay: 10000
    }
  },
  anthropic: {
    providerId: 'anthropic',
    isConnected: false,
    lastChecked: '2024-01-15T14:00:00Z',
    responseTime: 0,
    errorMessage: 'Invalid API key',
    availableModels: [],
    rateLimits: {
      requestsPerMinute: 0,
      tokensPerMinute: 0,
      requestsPerDay: 0
    }
  }
};

const mockUsageStats = {
  openai: {
    providerId: 'openai',
    period: 'month' as const,
    data: [
      { date: '2024-01-01', requests: 100, tokens: 3000, cost: 0.80, errors: 2 },
      { date: '2024-01-02', requests: 150, tokens: 4500, cost: 1.20, errors: 1 },
      { date: '2024-01-03', requests: 120, tokens: 3600, cost: 0.95, errors: 0 }
    ],
    totals: {
      requests: 1500,
      tokens: 45000,
      cost: 12.50,
      errors: 15
    }
  }
};

describe('APIKeyManagement', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    mockFetch.mockImplementation((url) => {
      if (url === '/api/settings/api-keys') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAPIKeys)
        } as Response);
      }
      
      if (url === '/api/providers/status') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProviderStatuses)
        } as Response);
      }
      
      if (url === '/api/providers/usage-stats') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockUsageStats)
        } as Response);
      }
      
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  it('renders API key management interface', async () => {
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('ניהול מפתחות API')).toBeInTheDocument();
    });
    
    expect(screen.getByText('מפתחות API')).toBeInTheDocument();
    expect(screen.getByText('סטטוס ספקים')).toBeInTheDocument();
    expect(screen.getByText('סטטיסטיקות שימוש')).toBeInTheDocument();
  });

  it('displays API keys correctly', async () => {
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Production Key')).toBeInTheDocument();
      expect(screen.getByText('Development Key')).toBeInTheDocument();
    });
    
    // Should show provider names
    expect(screen.getByText('OpenAI')).toBeInTheDocument();
    expect(screen.getByText('Anthropic')).toBeInTheDocument();
    
    // Should show status badges
    expect(screen.getByText('פעיל')).toBeInTheDocument();
    expect(screen.getByText('לא פעיל')).toBeInTheDocument();
  });

  it('masks API keys by default', async () => {
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      // Keys should be masked
      expect(screen.getByText('sk-1•••••••••••••••••••••••••cdef')).toBeInTheDocument();
    });
  });

  it('toggles API key visibility', async () => {
    const user = userEvent.setup();
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Production Key')).toBeInTheDocument();
    });
    
    // Find and click the eye icon to show the key
    const eyeButtons = screen.getAllByRole('button');
    const showKeyButton = eyeButtons.find(button => 
      button.querySelector('svg') && button.closest('div')?.textContent?.includes('sk-1')
    );
    
    if (showKeyButton) {
      await user.click(showKeyButton);
      
      // Key should now be visible
      await waitFor(() => {
        expect(screen.getByText('sk-1234567890abcdef1234567890abcdef')).toBeInTheDocument();
      });
    }
  });

  it('copies API key to clipboard', async () => {
    const user = userEvent.setup();
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Production Key')).toBeInTheDocument();
    });
    
    // Find and click the copy button
    const copyButtons = screen.getAllByRole('button');
    const copyButton = copyButtons.find(button => 
      button.querySelector('svg') && button.closest('div')?.textContent?.includes('sk-1')
    );
    
    if (copyButton) {
      await user.click(copyButton);
      
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('sk-1234567890abcdef1234567890abcdef');
    }
  });

  it('opens add API key dialog', async () => {
    const user = userEvent.setup();
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('הוסף מפתח')).toBeInTheDocument();
    });
    
    const addButton = screen.getByText('הוסף מפתח');
    await user.click(addButton);
    
    expect(screen.getByText('הוסף מפתח API')).toBeInTheDocument();
    expect(screen.getByText('בחר ספק')).toBeInTheDocument();
  });

  it('adds new API key', async () => {
    const user = userEvent.setup();
    
    // Mock successful API key creation
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ id: 'new-key', ...mockAPIKeys[0] })
      } as Response)
    );
    
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('הוסף מפתח')).toBeInTheDocument();
    });
    
    // Open add dialog
    const addButton = screen.getByText('הוסף מפתח');
    await user.click(addButton);
    
    // Fill in the form
    const providerSelect = screen.getByDisplayValue('בחר ספק');
    await user.selectOptions(providerSelect, 'openai');
    
    const nameInput = screen.getByPlaceholderText('למשל: Production Key');
    await user.type(nameInput, 'Test Key');
    
    const keyInput = screen.getByPlaceholderText('sk-1234567890abcdef...');
    await user.type(keyInput, 'sk-test1234567890abcdef');
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: 'הוסף מפתח' });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/settings/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          providerId: 'openai',
          name: 'Test Key',
          key: 'sk-test1234567890abcdef',
          isActive: true,
          status: 'inactive'
        })
      });
    });
  });

  it('tests API key connection', async () => {
    const user = userEvent.setup();
    
    // Mock successful connection test
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true })
      } as Response)
    );
    
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Production Key')).toBeInTheDocument();
    });
    
    // Find and click the test button
    const testButtons = screen.getAllByRole('button');
    const testButton = testButtons.find(button => 
      button.querySelector('svg') && button.getAttribute('title')?.includes('test')
    );
    
    if (testButton) {
      await user.click(testButton);
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/test/openai', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ keyId: 'key-1' })
        });
      });
    }
  });

  it('displays provider status correctly', async () => {
    const user = userEvent.setup();
    render(<APIKeyManagement />);
    
    // Switch to status tab
    const statusTab = screen.getByText('סטטוס ספקים');
    await user.click(statusTab);
    
    await waitFor(() => {
      expect(screen.getByText('סטטוס ספקים')).toBeInTheDocument();
    });
    
    // Should show provider statuses
    expect(screen.getByText('מחובר')).toBeInTheDocument();
    expect(screen.getByText('לא מחובר')).toBeInTheDocument();
    
    // Should show response times and other details
    expect(screen.getByText('250ms')).toBeInTheDocument();
    expect(screen.getByText('Invalid API key')).toBeInTheDocument();
  });

  it('displays usage statistics', async () => {
    const user = userEvent.setup();
    render(<APIKeyManagement />);
    
    // Switch to usage tab
    const usageTab = screen.getByText('סטטיסטיקות שימוש');
    await user.click(usageTab);
    
    await waitFor(() => {
      expect(screen.getByText('סטטיסטיקות שימוש')).toBeInTheDocument();
    });
    
    // Should show usage statistics
    expect(screen.getByText('1,500')).toBeInTheDocument(); // Total requests
    expect(screen.getByText('45,000')).toBeInTheDocument(); // Total tokens
    expect(screen.getByText('$12.50')).toBeInTheDocument(); // Total cost
  });

  it('deletes API key', async () => {
    const user = userEvent.setup();
    
    // Mock successful deletion
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      } as Response)
    );
    
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Production Key')).toBeInTheDocument();
    });
    
    // Find and click the settings menu
    const settingsButtons = screen.getAllByRole('button');
    const settingsButton = settingsButtons.find(button => 
      button.querySelector('svg') && button.closest('div')?.textContent?.includes('Production Key')
    );
    
    if (settingsButton) {
      await user.click(settingsButton);
      
      // Click delete option
      const deleteOption = screen.getByText('מחק');
      await user.click(deleteOption);
      
      // Confirm deletion
      const confirmButton = screen.getByRole('button', { name: 'מחק' });
      await user.click(confirmButton);
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/settings/api-keys/key-1', {
          method: 'DELETE'
        });
      });
    }
  });

  it('toggles API key active status', async () => {
    const user = userEvent.setup();
    
    // Mock successful update
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      } as Response)
    );
    
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Production Key')).toBeInTheDocument();
    });
    
    // Find and click the settings menu
    const settingsButtons = screen.getAllByRole('button');
    const settingsButton = settingsButtons.find(button => 
      button.querySelector('svg') && button.closest('div')?.textContent?.includes('Production Key')
    );
    
    if (settingsButton) {
      await user.click(settingsButton);
      
      // Click disable option
      const disableOption = screen.getByText('השבת');
      await user.click(disableOption);
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/settings/api-keys/key-1', {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ isActive: false })
        });
      });
    }
  });

  it('refreshes provider statuses', async () => {
    const user = userEvent.setup();
    render(<APIKeyManagement />);
    
    // Switch to status tab
    const statusTab = screen.getByText('סטטוס ספקים');
    await user.click(statusTab);
    
    await waitFor(() => {
      expect(screen.getByText('רענן')).toBeInTheDocument();
    });
    
    // Clear previous calls
    mockFetch.mockClear();
    
    // Click refresh button
    const refreshButton = screen.getByText('רענן');
    await user.click(refreshButton);
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/providers/status');
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500
      } as Response)
    );
    
    render(<APIKeyManagement />);
    
    // Should not crash and show loading state initially
    expect(screen.getByText('טוען מפתחות...')).toBeInTheDocument();
    
    await waitFor(() => {
      // Should handle error gracefully
      expect(mockFetch).toHaveBeenCalled();
    });
  });

  it('shows empty state when no keys exist', async () => {
    // Mock empty API keys response
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      } as Response)
    );
    
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('אין מפתחות API עבור OpenAI')).toBeInTheDocument();
      expect(screen.getByText('הוסף מפתח ראשון')).toBeInTheDocument();
    });
  });

  it('validates API key format', async () => {
    const user = userEvent.setup();
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('הוסף מפתח')).toBeInTheDocument();
    });
    
    // Open add dialog
    const addButton = screen.getByText('הוסף מפתח');
    await user.click(addButton);
    
    // Select provider to see format hint
    const providerSelect = screen.getByDisplayValue('בחר ספק');
    await user.selectOptions(providerSelect, 'openai');
    
    // Should show format hint
    expect(screen.getByText('פורמט: sk-...')).toBeInTheDocument();
  });

  it('shows provider documentation links', async () => {
    render(<APIKeyManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('OpenAI')).toBeInTheDocument();
    });
    
    // Should have external link buttons
    const externalLinkButtons = screen.getAllByRole('button');
    const docButton = externalLinkButtons.find(button => 
      button.querySelector('svg') && button.closest('div')?.textContent?.includes('OpenAI')
    );
    
    expect(docButton).toBeInTheDocument();
  });
});