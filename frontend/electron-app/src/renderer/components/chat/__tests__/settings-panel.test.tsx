import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AdvancedSettingsPanel } from '../settings-panel';

// Mock fetch
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock clipboard API
Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: jest.fn(),
  },
});

describe('AdvancedSettingsPanel', () => {
  const mockOnParametersChange = jest.fn();
  const defaultParameters = {
    temperature: 0.7,
    max_tokens: 2048,
    top_p: 0.9,
    top_k: 50,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
    repetition_penalty: 1.0,
    stop_sequences: [],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    
    mockFetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          text: 'בינה מלאכותית היא טכנולוגיה מהפכנית שתשנה את העתיד.',
          quality: 'good',
          metrics: {
            creativity: 75,
            coherence: 85,
            relevance: 90
          }
        })
      } as Response)
    );
  });

  it('renders with default parameters', () => {
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    expect(screen.getByText('הגדרות מתקדמות')).toBeInTheDocument();
    expect(screen.getByText('פריסטים מוכנים')).toBeInTheDocument();
    expect(screen.getByText('פרמטרים עיקריים')).toBeInTheDocument();
  });

  it('shows built-in presets', () => {
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    expect(screen.getByText('Creative')).toBeInTheDocument();
    expect(screen.getByText('Balanced')).toBeInTheDocument();
    expect(screen.getByText('Precise')).toBeInTheDocument();
    expect(screen.getByText('Code')).toBeInTheDocument();
  });

  it('applies preset when clicked', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    const creativePreset = screen.getByText('Creative');
    await user.click(creativePreset);
    
    await waitFor(() => {
      expect(mockOnParametersChange).toHaveBeenCalledWith(
        expect.objectContaining({
          temperature: 0.9,
          max_tokens: 2048,
          top_p: 0.95
        })
      );
    });
  });

  it('updates parameters when sliders change', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    // Find temperature input
    const temperatureInput = screen.getByDisplayValue('0.70');
    await user.clear(temperatureInput);
    await user.type(temperatureInput, '0.8');
    
    await waitFor(() => {
      expect(mockOnParametersChange).toHaveBeenCalledWith(
        expect.objectContaining({
          temperature: 0.8
        })
      );
    });
  });

  it('shows advanced parameters when toggled', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel enableAdvancedParams onParametersChange={mockOnParametersChange} />);
    
    // Initially advanced params should be hidden
    expect(screen.queryByText('Top K')).not.toBeInTheDocument();
    
    // Click to show advanced parameters
    const showAdvancedButton = screen.getByRole('button', { name: /פרמטרים מתקדמים/i });
    await user.click(showAdvancedButton);
    
    await waitFor(() => {
      expect(screen.getByText('Top K')).toBeInTheDocument();
      expect(screen.getByText('Frequency Penalty')).toBeInTheDocument();
    });
  });

  it('saves custom profile', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel enableProfiles onParametersChange={mockOnParametersChange} />);
    
    // Click save button
    const saveButton = screen.getByText('שמור');
    await user.click(saveButton);
    
    // Fill in profile details
    const nameInput = screen.getByPlaceholderText('הזן שם לפרופיל...');
    await user.type(nameInput, 'My Custom Profile');
    
    const descriptionInput = screen.getByPlaceholderText('תאר את מטרת הפרופיל...');
    await user.type(descriptionInput, 'Custom settings for testing');
    
    // Save the profile
    const saveProfileButton = screen.getByRole('button', { name: 'שמור' });
    await user.click(saveProfileButton);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'chat-parameter-profiles',
      expect.stringContaining('My Custom Profile')
    );
  });

  it('loads saved profile', async () => {
    const user = userEvent.setup();
    
    // Mock saved profiles
    const savedProfiles = [
      {
        id: 'profile-1',
        name: 'Test Profile',
        description: 'Test description',
        parameters: {
          temperature: 0.5,
          max_tokens: 1024,
          top_p: 0.8,
        },
        createdAt: '2024-01-01T10:00:00Z',
        updatedAt: '2024-01-01T10:00:00Z',
        isDefault: false,
        tags: []
      }
    ];
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(savedProfiles));
    
    render(<AdvancedSettingsPanel enableProfiles onParametersChange={mockOnParametersChange} />);
    
    // Click load button
    const loadButton = screen.getByText('טען');
    await user.click(loadButton);
    
    // Should show the saved profile
    expect(screen.getByText('Test Profile')).toBeInTheDocument();
    
    // Click on the profile to load it
    const profileCard = screen.getByText('Test Profile').closest('div');
    if (profileCard) {
      await user.click(profileCard);
      
      await waitFor(() => {
        expect(mockOnParametersChange).toHaveBeenCalledWith(
          expect.objectContaining({
            temperature: 0.5,
            max_tokens: 1024,
            top_p: 0.8
          })
        );
      });
    }
  });

  it('creates custom preset', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    // Click create preset button
    const createPresetButton = screen.getByText('צור פריסט');
    await user.click(createPresetButton);
    
    // Fill in preset details
    const nameInput = screen.getByPlaceholderText('הזן שם לפריסט...');
    await user.type(nameInput, 'My Custom Preset');
    
    const descriptionInput = screen.getByPlaceholderText('תאר את מטרת הפריסט...');
    await user.type(descriptionInput, 'Custom preset for testing');
    
    // Create the preset
    const createButton = screen.getByRole('button', { name: 'צור' });
    await user.click(createButton);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'chat-custom-presets',
      expect.stringContaining('My Custom Preset')
    );
  });

  it('resets to default parameters', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    // First change some parameters
    const temperatureInput = screen.getByDisplayValue('0.70');
    await user.clear(temperatureInput);
    await user.type(temperatureInput, '0.9');
    
    // Reset to defaults
    const resetButton = screen.getByTitle('איפוס לברירת מחדל');
    await user.click(resetButton);
    
    await waitFor(() => {
      expect(mockOnParametersChange).toHaveBeenCalledWith(
        expect.objectContaining({
          temperature: 0.7,
          max_tokens: 2048,
          top_p: 0.9
        })
      );
    });
  });

  it('generates preview when enabled', async () => {
    const user = userEvent.setup();
    render(
      <AdvancedSettingsPanel 
        showPreview 
        modelId="gpt-4" 
        onParametersChange={mockOnParametersChange} 
      />
    );
    
    // Click generate preview button
    const generateButton = screen.getByRole('button', { name: /תצוגה מקדימה/i });
    await user.click(generateButton);
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/llm/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: expect.stringContaining('gpt-4')
      });
    });
  });

  it('copies parameter values to clipboard', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    // Find and click copy button for temperature
    const copyButtons = screen.getAllByRole('button');
    const temperatureCopyButton = copyButtons.find(button => 
      button.querySelector('svg') && button.closest('div')?.textContent?.includes('Temperature')
    );
    
    if (temperatureCopyButton) {
      await user.click(temperatureCopyButton);
      
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('0.7');
    }
  });

  it('exports settings', async () => {
    const user = userEvent.setup();
    
    // Mock URL.createObjectURL and related functions
    const mockCreateObjectURL = jest.fn(() => 'blob:mock-url');
    const mockRevokeObjectURL = jest.fn();
    Object.defineProperty(URL, 'createObjectURL', { value: mockCreateObjectURL });
    Object.defineProperty(URL, 'revokeObjectURL', { value: mockRevokeObjectURL });
    
    // Mock document.createElement and appendChild
    const mockAnchor = {
      href: '',
      download: '',
      click: jest.fn()
    };
    const mockCreateElement = jest.fn(() => mockAnchor);
    const mockAppendChild = jest.fn();
    const mockRemoveChild = jest.fn();
    
    Object.defineProperty(document, 'createElement', { value: mockCreateElement });
    Object.defineProperty(document.body, 'appendChild', { value: mockAppendChild });
    Object.defineProperty(document.body, 'removeChild', { value: mockRemoveChild });
    
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    const exportButton = screen.getByTitle('ייצא הגדרות');
    await user.click(exportButton);
    
    expect(mockCreateObjectURL).toHaveBeenCalled();
    expect(mockAnchor.click).toHaveBeenCalled();
  });

  it('imports settings from file', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    const importData = {
      parameters: {
        temperature: 0.8,
        max_tokens: 1024,
        top_p: 0.85
      },
      profiles: [],
      customPresets: []
    };
    
    // Mock FileReader
    const mockFileReader = {
      readAsText: jest.fn(),
      onload: null as any,
      result: JSON.stringify(importData)
    };
    
    Object.defineProperty(window, 'FileReader', {
      value: jest.fn(() => mockFileReader)
    });
    
    // Trigger file input change
    const importButton = screen.getByTitle('יבא הגדרות');
    await user.click(importButton);
    
    // Simulate file selection
    const fileInput = document.getElementById('import-settings') as HTMLInputElement;
    const file = new File([JSON.stringify(importData)], 'settings.json', {
      type: 'application/json'
    });
    
    Object.defineProperty(fileInput, 'files', {
      value: [file]
    });
    
    fireEvent.change(fileInput);
    
    // Simulate FileReader onload
    if (mockFileReader.onload) {
      mockFileReader.onload({ target: { result: JSON.stringify(importData) } } as any);
    }
    
    await waitFor(() => {
      expect(mockOnParametersChange).toHaveBeenCalledWith(
        expect.objectContaining({
          temperature: 0.8,
          max_tokens: 1024,
          top_p: 0.85
        })
      );
    });
  });

  it('handles stop sequences input', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel enableAdvancedParams onParametersChange={mockOnParametersChange} />);
    
    // Show advanced parameters
    const showAdvancedButton = screen.getByRole('button', { name: /פרמטרים מתקדמים/i });
    await user.click(showAdvancedButton);
    
    // Find stop sequences textarea
    const stopSequencesInput = screen.getByPlaceholderText('הזן רצפי עצירה, מופרדים בפסיקים');
    await user.type(stopSequencesInput, '```', ', ---', ', END');
    
    await waitFor(() => {
      expect(mockOnParametersChange).toHaveBeenCalledWith(
        expect.objectContaining({
          stop_sequences: ['```', '---', 'END']
        })
      );
    });
  });

  it('handles seed input', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel enableAdvancedParams onParametersChange={mockOnParametersChange} />);
    
    // Show advanced parameters
    const showAdvancedButton = screen.getByRole('button', { name: /פרמטרים מתקדמים/i });
    await user.click(showAdvancedButton);
    
    // Find seed input
    const seedInput = screen.getByPlaceholderText('הזן seed לתוצאות עקביות');
    await user.type(seedInput, '12345');
    
    await waitFor(() => {
      expect(mockOnParametersChange).toHaveBeenCalledWith(
        expect.objectContaining({
          seed: 12345
        })
      );
    });
  });

  it('toggles preview functionality', async () => {
    const user = userEvent.setup();
    render(
      <AdvancedSettingsPanel 
        showPreview 
        modelId="gpt-4" 
        onParametersChange={mockOnParametersChange} 
      />
    );
    
    // Find preview toggle switch
    const previewToggle = screen.getByRole('switch');
    
    // Toggle off
    await user.click(previewToggle);
    expect(previewToggle).not.toBeChecked();
    
    // Toggle back on
    await user.click(previewToggle);
    expect(previewToggle).toBeChecked();
  });

  it('shows parameter constraints and descriptions', () => {
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    expect(screen.getByText('שולט על רמת היצירתיות והאקראיות')).toBeInTheDocument();
    expect(screen.getByText('מספר מקסימלי של טוקנים בתגובה')).toBeInTheDocument();
    expect(screen.getByText('דגימת nucleus - מגביל את מגוון המילים')).toBeInTheDocument();
  });

  it('validates parameter ranges', async () => {
    const user = userEvent.setup();
    render(<AdvancedSettingsPanel onParametersChange={mockOnParametersChange} />);
    
    // Try to set temperature above maximum
    const temperatureInput = screen.getByDisplayValue('0.70');
    await user.clear(temperatureInput);
    await user.type(temperatureInput, '3.0');
    
    // The input should be constrained by min/max attributes
    expect(temperatureInput).toHaveAttribute('max', '2');
  });

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup();
    
    // Mock failed API response
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500
      } as Response)
    );
    
    render(
      <AdvancedSettingsPanel 
        showPreview 
        modelId="gpt-4" 
        onParametersChange={mockOnParametersChange} 
      />
    );
    
    // Try to generate preview
    const generateButton = screen.getByRole('button', { name: /תצוגה מקדימה/i });
    await user.click(generateButton);
    
    // Should not crash and handle error gracefully
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    });
  });
});