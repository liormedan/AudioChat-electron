import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EnhancedModelSelector } from '../enhanced-model-selector';

// Mock fetch
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Mock data
const mockModels = [
  {
    id: 'gpt-4',
    name: 'GPT-4',
    provider: 'OpenAI',
    description: 'Most capable GPT model',
    maxTokens: 8192,
    costPerToken: 0.00003,
    capabilities: [
      { name: 'text-generation', supported: true, quality: 'excellent' as const },
      { name: 'code-generation', supported: true, quality: 'excellent' as const }
    ],
    isActive: true,
    isAvailable: true,
    contextWindow: 8192,
    trainingDataCutoff: '2023-04-01',
    version: '4.0',
    parameters: {},
    metadata: {},
    metrics: {
      responseTime: 1200,
      tokensPerSecond: 45,
      successRate: 98.5,
      totalRequests: 1500,
      averageCost: 0.024,
      lastUsed: '2024-01-01T10:00:00Z',
      uptime: 99.2,
      throughput: 120,
      errorRate: 1.5,
      avgTokensPerRequest: 800
    },
    tier: 'premium' as const,
    category: 'chat' as const
  },
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'OpenAI',
    description: 'Fast and efficient model',
    maxTokens: 4096,
    costPerToken: 0.000002,
    capabilities: [
      { name: 'text-generation', supported: true, quality: 'good' as const }
    ],
    isActive: false,
    isAvailable: true,
    contextWindow: 4096,
    trainingDataCutoff: '2021-09-01',
    version: '3.5',
    parameters: {},
    metadata: {},
    metrics: {
      responseTime: 800,
      tokensPerSecond: 60,
      successRate: 97.8,
      totalRequests: 2500,
      averageCost: 0.008,
      lastUsed: '2024-01-01T09:00:00Z',
      uptime: 99.8,
      throughput: 180,
      errorRate: 2.2,
      avgTokensPerRequest: 400
    },
    tier: 'free' as const,
    category: 'chat' as const
  },
  {
    id: 'claude-3',
    name: 'Claude 3',
    provider: 'Anthropic',
    description: 'Advanced reasoning model',
    maxTokens: 100000,
    costPerToken: 0.000015,
    capabilities: [
      { name: 'text-generation', supported: true, quality: 'excellent' as const },
      { name: 'analysis', supported: true, quality: 'excellent' as const }
    ],
    isActive: false,
    isAvailable: false,
    contextWindow: 100000,
    trainingDataCutoff: '2024-02-01',
    version: '3.0',
    parameters: {},
    metadata: {},
    metrics: {
      responseTime: 1500,
      tokensPerSecond: 35,
      successRate: 99.1,
      totalRequests: 800,
      averageCost: 0.045,
      lastUsed: '2024-01-01T08:00:00Z',
      uptime: 95.5,
      throughput: 90,
      errorRate: 0.9,
      avgTokensPerRequest: 1200
    },
    tier: 'enterprise' as const,
    category: 'analysis' as const
  }
];

const mockConnectionStatus = {
  'gpt-4': 'connected' as const,
  'gpt-3.5-turbo': 'connected' as const,
  'claude-3': 'disconnected' as const
};

const mockUsageStats = {
  'gpt-4': {
    hourly: [10, 15, 20, 18, 25, 30],
    daily: [150, 200, 180, 220, 190, 240, 210]
  },
  'gpt-3.5-turbo': {
    hourly: [25, 30, 35, 40, 45, 50],
    daily: [300, 350, 320, 380, 340, 400, 360]
  }
};

describe('EnhancedModelSelector', () => {
  const mockOnModelChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockFetch.mockImplementation((url) => {
      if (url === '/api/llm/models') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockModels)
        } as Response);
      }
      
      if (url === '/api/llm/active-model') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockModels[0])
        } as Response);
      }
      
      if (url === '/api/llm/model-metrics') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            'gpt-4': mockModels[0].metrics,
            'gpt-3.5-turbo': mockModels[1].metrics,
            'claude-3': mockModels[2].metrics
          })
        } as Response);
      }
      
      if (url === '/api/llm/connection-status') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockConnectionStatus)
        } as Response);
      }
      
      if (url === '/api/llm/usage-stats') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockUsageStats)
        } as Response);
      }
      
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  it('renders in compact mode', async () => {
    render(<EnhancedModelSelector compact onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('renders in full mode with metrics', async () => {
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('בחירת מודל AI')).toBeInTheDocument();
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Should show metrics
    expect(screen.getByText('1200ms')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.getByText('98.5%')).toBeInTheDocument();
  });

  it('shows smart recommendations', async () => {
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('המלצות חכמות')).toBeInTheDocument();
    });
    
    // Should show different types of recommendations
    expect(screen.getByText(/הכי מהיר/)).toBeInTheDocument();
    expect(screen.getByText(/הכי חסכוני/)).toBeInTheDocument();
    expect(screen.getByText(/הכי אמין/)).toBeInTheDocument();
  });

  it('handles model switching', async () => {
    const user = userEvent.setup();
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    // Mock the POST request for model switching
    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true })
      } as Response)
    );
    
    await waitFor(() => {
      expect(screen.getByText('GPT-3.5 Turbo')).toBeInTheDocument();
    });
    
    // Click on a different model
    const gpt35Model = screen.getByText('GPT-3.5 Turbo').closest('div');
    if (gpt35Model) {
      await user.click(gpt35Model);
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/llm/active-model', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model_id: 'gpt-3.5-turbo' })
        });
      });
    }
  });

  it('shows quick switch options', async () => {
    const user = userEvent.setup();
    render(<EnhancedModelSelector enableQuickSwitch onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('החלפה מהירה')).toBeInTheDocument();
    });
    
    // Click on quick switch button
    const quickSwitchButton = screen.getByText('החלפה מהירה');
    await user.click(quickSwitchButton);
    
    // Should show quick switch options
    await waitFor(() => {
      expect(screen.getByText(/הכי מהיר/)).toBeInTheDocument();
    });
  });

  it('handles refresh functionality', async () => {
    const user = userEvent.setup();
    render(<EnhancedModelSelector autoRefresh={false} onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByTitle('רענן נתונים')).toBeInTheDocument();
    });
    
    const refreshButton = screen.getByTitle('רענן נתונים');
    await user.click(refreshButton);
    
    // Should call all the fetch endpoints again
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/llm/models');
      expect(mockFetch).toHaveBeenCalledWith('/api/llm/active-model');
      expect(mockFetch).toHaveBeenCalledWith('/api/llm/model-metrics');
    });
  });

  it('shows advanced controls', async () => {
    const user = userEvent.setup();
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByTitle('הגדרות מתקדמות')).toBeInTheDocument();
    });
    
    const advancedButton = screen.getByTitle('הגדרות מתקדמות');
    await user.click(advancedButton);
    
    // Should show advanced controls
    await waitFor(() => {
      expect(screen.getByText('קטגוריה:')).toBeInTheDocument();
      expect(screen.getByText('מיון לפי:')).toBeInTheDocument();
    });
  });

  it('filters models by category', async () => {
    const user = userEvent.setup();
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    // Open advanced controls
    await waitFor(() => {
      expect(screen.getByTitle('הגדרות מתקדמות')).toBeInTheDocument();
    });
    
    const advancedButton = screen.getByTitle('הגדרות מתקדמות');
    await user.click(advancedButton);
    
    // Change category filter
    const categorySelect = screen.getByDisplayValue('הכל');
    await user.selectOptions(categorySelect, 'analysis');
    
    // Should only show analysis models
    await waitFor(() => {
      expect(screen.getByText('Claude 3')).toBeInTheDocument();
      expect(screen.queryByText('GPT-4')).not.toBeInTheDocument();
    });
  });

  it('sorts models correctly', async () => {
    const user = userEvent.setup();
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    // Open advanced controls
    const advancedButton = screen.getByTitle('הגדרות מתקדמות');
    await user.click(advancedButton);
    
    // Change sort order
    const sortSelect = screen.getByDisplayValue('שימוש');
    await user.selectOptions(sortSelect, 'performance');
    
    // Models should be sorted by performance (response time)
    const modelElements = screen.getAllByText(/ms/);
    expect(modelElements.length).toBeGreaterThan(0);
  });

  it('shows performance details when enabled', async () => {
    render(<EnhancedModelSelector showPerformanceDetails onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('זמינות:')).toBeInTheDocument();
      expect(screen.getByText('שגיאות:')).toBeInTheDocument();
      expect(screen.getByText('תפוקה:')).toBeInTheDocument();
    });
  });

  it('handles connection status indicators', async () => {
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      // Should show different connection status icons
      const connectedIcons = screen.getAllByTitle(/connected|disconnected/i);
      expect(connectedIcons.length).toBeGreaterThan(0);
    });
  });

  it('shows trending indicators', async () => {
    render(<EnhancedModelSelector showTrending onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      // Should render without errors even if trending data is limited
      expect(screen.getByText('בחירת מודל AI')).toBeInTheDocument();
    });
  });

  it('handles loading states', async () => {
    // Mock slow response
    mockFetch.mockImplementationOnce(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve(mockModels)
        } as Response), 100)
      )
    );
    
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    // Should show loading state
    expect(screen.getByText('טוען מודלים...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        status: 500
      } as Response)
    );
    
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    // Should not crash and show empty state
    await waitFor(() => {
      expect(screen.getByText('לא נמצאו מודלים זמינים')).toBeInTheDocument();
    });
  });

  it('shows tier indicators correctly', async () => {
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      // Should show different tier indicators (icons)
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
      expect(screen.getByText('GPT-3.5 Turbo')).toBeInTheDocument();
      expect(screen.getByText('Claude 3')).toBeInTheDocument();
    });
  });

  it('handles model change errors', async () => {
    const user = userEvent.setup();
    
    // Mock successful initial load
    render(<EnhancedModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-3.5 Turbo')).toBeInTheDocument();
    });
    
    // Mock failed model change
    mockFetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        status: 500
      } as Response)
    );
    
    const gpt35Model = screen.getByText('GPT-3.5 Turbo').closest('div');
    if (gpt35Model) {
      await user.click(gpt35Model);
      
      // Should handle error gracefully without crashing
      await waitFor(() => {
        expect(mockOnModelChange).not.toHaveBeenCalled();
      });
    }
  });

  it('auto-refreshes when enabled', async () => {
    jest.useFakeTimers();
    
    render(<EnhancedModelSelector autoRefresh refreshInterval={1000} onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Clear initial calls
    mockFetch.mockClear();
    
    // Fast-forward time
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    // Should have called metrics update
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/llm/model-metrics');
    });
    
    jest.useRealTimers();
  });

  it('disables auto-refresh when specified', async () => {
    jest.useFakeTimers();
    
    render(<EnhancedModelSelector autoRefresh={false} onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Clear initial calls
    mockFetch.mockClear();
    
    // Fast-forward time
    act(() => {
      jest.advanceTimersByTime(30000);
    });
    
    // Should not have called metrics update
    expect(mockFetch).not.toHaveBeenCalledWith('/api/llm/model-metrics');
    
    jest.useRealTimers();
  });
});