import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PerformanceMonitor } from '../performance-monitor';

// Mock fetch
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Mock data
const mockMetrics = {
  'gpt-4': {
    modelId: 'gpt-4',
    modelName: 'GPT-4',
    provider: 'OpenAI',
    responseTime: {
      current: 1200,
      average: 1150,
      min: 800,
      max: 2500,
      history: [
        { timestamp: '2024-01-01T10:00:00Z', value: 1100 },
        { timestamp: '2024-01-01T11:00:00Z', value: 1200 }
      ]
    },
    tokenUsage: {
      inputTokens: 15000,
      outputTokens: 12000,
      totalTokens: 27000,
      tokensPerSecond: 45,
      efficiency: 0.85
    },
    costMetrics: {
      totalCost: 12.50,
      costPerToken: 0.00003,
      costPerRequest: 0.024,
      dailyCost: 2.40,
      monthlyCost: 72.00,
      costTrend: 'stable' as const
    },
    reliability: {
      successRate: 98.5,
      errorRate: 1.5,
      uptime: 99.2,
      errorHistory: []
    },
    performance: {
      throughput: 120,
      concurrency: 5,
      queueLength: 2,
      memoryUsage: 65.5,
      cpuUsage: 45.2
    },
    usage: {
      totalRequests: 1500,
      requestsPerHour: 125,
      requestsPerDay: 3000,
      activeUsers: 25,
      popularityScore: 8.5
    },
    lastUpdated: '2024-01-01T12:00:00Z'
  }
}; const m
ockAlerts = [
  {
    id: 'alert-1',
    type: 'warning' as const,
    title: 'זמן תגובה גבוה',
    message: 'זמן התגובה עלה מעל הסף המוגדר',
    modelId: 'gpt-4',
    threshold: 1000,
    currentValue: 1200,
    timestamp: '2024-01-01T12:00:00Z',
    isActive: true,
    acknowledged: false
  },
  {
    id: 'alert-2',
    type: 'error' as const,
    title: 'שיעור שגיאות גבוה',
    message: 'שיעור השגיאות עלה מעל 5%',
    modelId: 'gpt-4',
    threshold: 5,
    currentValue: 8.2,
    timestamp: '2024-01-01T11:30:00Z',
    isActive: true,
    acknowledged: false
  }
];

const mockComparisonData = {
  models: ['gpt-4', 'gpt-3.5-turbo'],
  metrics: {
    responseTime: {
      'gpt-4': 1150,
      'gpt-3.5-turbo': 800
    },
    cost: {
      'gpt-4': 0.024,
      'gpt-3.5-turbo': 0.008
    },
    reliability: {
      'gpt-4': 98.5,
      'gpt-3.5-turbo': 97.8
    },
    efficiency: {
      'gpt-4': 0.85,
      'gpt-3.5-turbo': 0.78
    }
  },
  recommendations: [
    {
      type: 'fastest' as const,
      modelId: 'gpt-3.5-turbo',
      reason: 'זמן תגובה מהיר ביותר',
      score: 95
    },
    {
      type: 'cheapest' as const,
      modelId: 'gpt-3.5-turbo',
      reason: 'עלות נמוכה ביותר',
      score: 90
    }
  ]
};

describe('PerformanceMonitor', () => {
  const mockOnModelSelect = jest.fn();
  const mockOnAlertAcknowledge = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    mockFetch.mockImplementation((url) => {
      if (url.includes('/api/performance/metrics')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockMetrics)
        } as Response);
      }

      if (url === '/api/performance/alerts') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAlerts)
        } as Response);
      }

      if (url === '/api/performance/comparison') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockComparisonData)
        } as Response);
      }

      return Promise.reject(new Error('Unknown URL'));
    });
  }); it('
renders performance monitor interface', async () => {
    render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('מוניטור ביצועי מודלים')).toBeInTheDocument();
  });

  expect(screen.getByText('סקירה כללית')).toBeInTheDocument();
  expect(screen.getByText('פירוט מלא')).toBeInTheDocument();
  expect(screen.getByText('השוואה')).toBeInTheDocument();
});

it('displays model metrics correctly', async () => {
  render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  // Should show key metrics
  expect(screen.getByText('1.2s')).toBeInTheDocument(); // Response time
  expect(screen.getByText('45')).toBeInTheDocument(); // Tokens per second
  expect(screen.getByText('$0.0240')).toBeInTheDocument(); // Cost per request
  expect(screen.getByText('125')).toBeInTheDocument(); // Requests per hour
});

it('shows performance alerts', async () => {
  render(<PerformanceMonitor showAlerts onAlertAcknowledge={mockOnAlertAcknowledge} />);

  await waitFor(() => {
    expect(screen.getByText('התראות ביצועים')).toBeInTheDocument();
  });

  // Should show active alerts
  expect(screen.getByText('זמן תגובה גבוה')).toBeInTheDocument();
  expect(screen.getByText('שיעור שגיאות גבוה')).toBeInTheDocument();

  // Should show alert count badge
  expect(screen.getByText('2')).toBeInTheDocument();
});

it('acknowledges alerts when clicked', async () => {
  const user = userEvent.setup();

  // Mock successful alert acknowledgment
  mockFetch.mockImplementationOnce(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({})
    } as Response)
  );

  render(<PerformanceMonitor showAlerts onAlertAcknowledge={mockOnAlertAcknowledge} />);

  await waitFor(() => {
    expect(screen.getByText('זמן תגובה גבוה')).toBeInTheDocument();
  });

  // Find and click acknowledge button
  const acknowledgeButtons = screen.getAllByRole('button');
  const acknowledgeButton = acknowledgeButtons.find(button =>
    button.querySelector('svg') && button.closest('div')?.textContent?.includes('זמן תגובה גבוה')
  );

  if (acknowledgeButton) {
    await user.click(acknowledgeButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/performance/alerts/alert-1/acknowledge', {
        method: 'POST'
      });
      expect(mockOnAlertAcknowledge).toHaveBeenCalledWith('alert-1');
    });
  }
});

it('expands and collapses metric cards', async () => {
  const user = userEvent.setup();
  render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  // Initially detailed metrics should not be visible
  expect(screen.queryByText('מינימום:')).not.toBeInTheDocument();

  // Find and click expand button
  const expandButtons = screen.getAllByRole('button');
  const expandButton = expandButtons.find(button =>
    button.querySelector('svg') && button.closest('div')?.textContent?.includes('GPT-4')
  );

  if (expandButton) {
    await user.click(expandButton);

    // Should show detailed metrics
    await waitFor(() => {
      expect(screen.getByText('מינימום:')).toBeInTheDocument();
      expect(screen.getByText('800ms')).toBeInTheDocument();
    });
  }
});

it('switches between time ranges', async () => {
  const user = userEvent.setup();
  render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('24h')).toBeInTheDocument();
  });

  // Click time range dropdown
  const timeRangeButton = screen.getByText('24h');
  await user.click(timeRangeButton);

  // Select different time range
  const sevenDaysOption = screen.getByText('7d');
  await user.click(sevenDaysOption);

  // Should call API with new time range
  await waitFor(() => {
    expect(mockFetch).toHaveBeenCalledWith('/api/performance/metrics?timeRange=7d');
  });
});

it('renders compact mode correctly', async () => {
  render(<PerformanceMonitor compactMode onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('ביצועי מודלים')).toBeInTheDocument();
  });

  // Should show simplified view
  expect(screen.getByText('GPT-4')).toBeInTheDocument();
  expect(screen.queryByText('מוניטור ביצועי מודלים')).not.toBeInTheDocument();
});

it('displays comparison view', async () => {
  const user = userEvent.setup();
  render(
    <PerformanceMonitor
      enableComparison
      selectedModels={['gpt-4', 'gpt-3.5-turbo']}
      onModelSelect={mockOnModelSelect}
    />
  );

  // Switch to comparison tab
  const comparisonTab = screen.getByText('השוואה');
  await user.click(comparisonTab);

  await waitFor(() => {
    expect(screen.getByText('המלצות')).toBeInTheDocument();
  });

  // Should show recommendations
  expect(screen.getByText('הכי מהיר')).toBeInTheDocument();
  expect(screen.getByText('הכי חסכוני')).toBeInTheDocument();
});

it('refreshes data when refresh button clicked', async () => {
  const user = userEvent.setup();
  render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  // Clear previous API calls
  mockFetch.mockClear();

  // Click refresh button
  const refreshButton = screen.getByRole('button', { name: /refresh/i });
  await user.click(refreshButton);

  await waitFor(() => {
    expect(mockFetch).toHaveBeenCalledWith('/api/performance/metrics?timeRange=24h');
  });
});

it('handles model selection', async () => {
  const user = userEvent.setup();
  render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  // Find and click model select button
  const selectButtons = screen.getAllByRole('button');
  const selectButton = selectButtons.find(button =>
    button.querySelector('svg') && button.closest('div')?.textContent?.includes('GPT-4')
  );

  if (selectButton) {
    await user.click(selectButton);
    expect(mockOnModelSelect).toHaveBeenCalledWith('gpt-4');
  }
});

it('toggles alerts on/off', async () => {
  const user = userEvent.setup();
  render(<PerformanceMonitor showAlerts onAlertAcknowledge={mockOnAlertAcknowledge} />);

  await waitFor(() => {
    expect(screen.getByText('התראות פעילות')).toBeInTheDocument();
  });

  // Find alerts toggle switch
  const alertsToggle = screen.getByRole('switch');

  // Toggle off
  await user.click(alertsToggle);
  expect(alertsToggle).not.toBeChecked();

  // Toggle back on
  await user.click(alertsToggle);
  expect(alertsToggle).toBeChecked();
});

it('handles API errors gracefully', async () => {
  // Mock API error
  mockFetch.mockImplementationOnce(() =>
    Promise.resolve({
      ok: false,
      status: 500
    } as Response)
  );

  render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  // Should show loading state initially
  expect(screen.getByText('טוען נתוני ביצועים...')).toBeInTheDocument();

  await waitFor(() => {
    // Should handle error gracefully
    expect(mockFetch).toHaveBeenCalled();
  });
});

it('shows empty comparison state', async () => {
  const user = userEvent.setup();
  render(<PerformanceMonitor enableComparison selectedModels={[]} onModelSelect={mockOnModelSelect} />);

  // Switch to comparison tab
  const comparisonTab = screen.getByText('השוואה');
  await user.click(comparisonTab);

  await waitFor(() => {
    expect(screen.getByText('בחר לפחות 2 מודלים להשוואה')).toBeInTheDocument();
  });
});

it('formats numbers and currencies correctly', async () => {
  render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    // Should format currency with proper locale
    expect(screen.getByText('$0.0240')).toBeInTheDocument();

    // Should format numbers with proper locale
    expect(screen.getByText('1,500')).toBeInTheDocument();
  });
});

it('shows performance color coding', async () => {
  render(<PerformanceMonitor onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  // Response time should be color-coded based on performance
  const responseTimeElement = screen.getByText('1.2s');
  expect(responseTimeElement).toHaveClass('text-yellow-600'); // Warning color for 1200ms
});

it('auto-refreshes when enabled', async () => {
  jest.useFakeTimers();

  render(<PerformanceMonitor autoRefresh refreshInterval={5000} onModelSelect={mockOnModelSelect} />);

  await waitFor(() => {
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
  });

  // Clear initial calls
  mockFetch.mockClear();

  // Fast-forward time
  act(() => {
    jest.advanceTimersByTime(5000);
  });

  // Should have called metrics update
  await waitFor(() => {
    expect(mockFetch).toHaveBeenCalledWith('/api/performance/metrics?timeRange=24h');
  });

  jest.useRealTimers();
});
});