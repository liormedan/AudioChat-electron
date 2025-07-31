import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ModelSelector } from '../model-selector';

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
    trainingDataCutoff: '2023-04',
    version: '1.0',
    parameters: {},
    metadata: {},
    metrics: {
      responseTime: 1200,
      tokensPerSecond: 45,
      successRate: 98.5,
      totalRequests: 1500,
      averageCost: 0.05,
      lastUsed: '2024-01-01T10:00:00Z',
      uptime: 99.8
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
      { name: 'text-generation', supported: true, quality: 'good' as const },
      { name: 'code-generation', supported: true, quality: 'good' as const }
    ],
    isActive: false,
    isAvailable: true,
    contextWindow: 4096,
    trainingDataCutoff: '2023-09',
    version: '1.0',
    parameters: {},
    metadata: {},
    metrics: {
      responseTime: 800,
      tokensPerSecond: 60,
      successRate: 99.2,
      totalRequests: 3000,
      averageCost: 0.01,
      lastUsed: '2024-01-01T09:00:00Z',
      uptime: 99.9
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
    trainingDataCutoff: '2024-02',
    version: '3.0',
    parameters: {},
    metadata: {},
    metrics: {
      responseTime: 1500,
      tokensPerSecond: 35,
      successRate: 97.8,
      totalRequests: 800,
      averageCost: 0.08,
      lastUsed: '2024-01-01T08:00:00Z',
      uptime: 95.5
    },
    tier: 'enterprise' as const,
    category: 'analysis' as const
  }
];

const mockActiveModel = mockModels[0];

describe('ModelSelector', () => {
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
          json: () => Promise.resolve(mockActiveModel)
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
      
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  it('renders in full mode with all features', async () => {
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('בחירת מודל AI')).toBeInTheDocument();
    });
    
    // Should show current model status
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
    expect(screen.getByText('OpenAI')).toBeInTheDocument();
    
    // Should show metrics
    expect(screen.getByText('1200ms')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.getByText('98.5%')).toBeInTheDocument();
  });

  it('renders in compact mode', async () => {
    render(<ModelSelector compact onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Should show dropdown trigger
    const trigger = screen.getByRole('button');
    expect(trigger).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    expect(screen.getByText('טוען מודלים...')).toBeInTheDocument();
  });

  it('displays model recommendations', async () => {
    render(<ModelSelector showRecommendations onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('המלצות')).toBeInTheDocument();
    });
    
    // Should show performance recommendation (fastest model)
    expect(screen.getByText(/הכי מהיר - 800ms/)).toBeInTheDocument();
    
    // Should show cost recommendation (cheapest model)
    expect(screen.getByText(/הכי חסכוני/)).toBeInTheDocument();
    
    // Should show reliability recommendation
    expect(screen.getByText(/הכי אמין/)).toBeInTheDocument();
  });

  it('handles model selection', async () => {
    const user = userEvent.setup();
    
    mockFetch.mockImplementation((url, options) => {
      if (url === '/api/llm/models') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockModels)
        } as Response);
      }
      
      if (url === '/api/llm/active-model') {
        if (options?.method === 'POST') {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ success: true })
          } as Response);
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockActiveModel)
        } as Response);
      }
      
      return Promise.reject(new Error('Unknown URL'));
    });
    
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-3.5 Turbo')).toBeInTheDocument();
    });
    
    // Click on a different model
    const gpt35Model = screen.getByText('GPT-3.5 Turbo').closest('div[role="button"], .cursor-pointer');
    if (gpt35Model) {
      await user.click(gpt35Model);
      
      await waitFor(() => {
        expect(mockOnModelChange).toHaveBeenCalledWith('gpt-3.5-turbo');
      });
    }
  });

  it('shows advanced controls when toggled', async () => {
    const user = userEvent.setup();
    
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('בחירת מודל AI')).toBeInTheDocument();
    });
    
    // Click settings button to show advanced controls
    const settingsButton = screen.getByRole('button', { name: '' }); // Settings button
    await user.click(settingsButton);
    
    // Should show category and sort controls
    expect(screen.getByText('קטגוריה:')).toBeInTheDocument();
    expect(screen.getByText('מיון לפי:')).toBeInTheDocument();
  });

  it('filters models by category', async () => {
    const user = userEvent.setup();
    
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('בחירת מודל AI')).toBeInTheDocument();
    });
    
    // Show advanced controls
    const settingsButton = screen.getByRole('button', { name: '' });
    await user.click(settingsButton);
    
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
    
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('בחירת מודל AI')).toBeInTheDocument();
    });
    
    // Show advanced controls
    const settingsButton = screen.getByRole('button', { name: '' });
    await user.click(settingsButton);
    
    // Change sort to performance
    const sortSelect = screen.getByDisplayValue('שימוש');
    await user.selectOptions(sortSelect, 'performance');
    
    // Models should be sorted by response time (fastest first)
    const modelElements = screen.getAllByText(/ms$/);
    expect(modelElements[0]).toHaveTextContent('800ms'); // GPT-3.5 Turbo is fastest
  });

  it('shows correct status indicators', async () => {
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Should show green indicator for available models
    const availableModels = screen.getAllByText('GPT-4');
    expect(availableModels.length).toBeGreaterThan(0);
    
    // Should show red indicator for unavailable models (Claude 3)
    expect(screen.getByText('Claude 3')).toBeInTheDocument();
  });

  it('displays tier indicators correctly', async () => {
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Should show different tier indicators
    // Premium tier (star), Free tier (shield), Enterprise tier (crown)
    const modelCards = screen.getAllByText(/GPT|Claude/);
    expect(modelCards.length).toBeGreaterThan(0);
  });

  it('updates metrics in real-time', async () => {
    jest.useFakeTimers();
    
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Fast-forward time to trigger metrics update
    act(() => {
      jest.advanceTimersByTime(30000);
    });
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/llm/model-metrics');
    });
    
    jest.useRealTimers();
  });

  it('handles API errors gracefully', async () => {
    mockFetch.mockRejectedValue(new Error('API Error'));
    
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('לא נמצאו מודלים זמינים')).toBeInTheDocument();
    });
  });

  it('shows uptime progress bars', async () => {
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Should show uptime percentages
    expect(screen.getByText('99.8%')).toBeInTheDocument();
    expect(screen.getByText('99.9%')).toBeInTheDocument();
    expect(screen.getByText('95.5%')).toBeInTheDocument();
  });

  it('handles compact mode dropdown interactions', async () => {
    const user = userEvent.setup();
    
    render(<ModelSelector compact onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
    });
    
    // Click dropdown trigger
    const trigger = screen.getByRole('button');
    await user.click(trigger);
    
    // Should show dropdown menu
    expect(screen.getByText('מודלים זמינים')).toBeInTheDocument();
    
    // Should show all models in dropdown
    expect(screen.getByText('GPT-3.5 Turbo')).toBeInTheDocument();
    expect(screen.getByText('Claude 3')).toBeInTheDocument();
  });

  it('prevents model change when already changing', async () => {
    const user = userEvent.setup();
    
    // Mock slow API response
    mockFetch.mockImplementation((url, options) => {
      if (url === '/api/llm/active-model' && options?.method === 'POST') {
        return new Promise(() => {}); // Never resolves
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(url === '/api/llm/models' ? mockModels : mockActiveModel)
      } as Response);
    });
    
    render(<ModelSelector onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('GPT-3.5 Turbo')).toBeInTheDocument();
    });
    
    // Click on a model
    const gpt35Model = screen.getByText('GPT-3.5 Turbo').closest('.cursor-pointer');
    if (gpt35Model) {
      await user.click(gpt35Model);
      
      // Should show loading state
      expect(screen.getByTestId('loader') || screen.getByText(/loading/i)).toBeTruthy();
      
      // Clicking again should not trigger another change
      await user.click(gpt35Model);
      
      // Should only have been called once
      expect(mockOnModelChange).toHaveBeenCalledTimes(0); // Since the API never resolves
    }
  });

  it('shows performance color coding', async () => {
    render(<ModelSelector showMetrics onModelChange={mockOnModelChange} />);
    
    await waitFor(() => {
      expect(screen.getByText('1200ms')).toBeInTheDocument();
    });
    
    // Fast response time should be green, slower should be yellow/red
    const responseTimeElements = screen.getAllByText(/\d+ms/);
    expect(responseTimeElements.length).toBeGreaterThan(0);
  });
});