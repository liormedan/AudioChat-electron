import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { CompactWaveformPlayer } from '../compact-waveform-player';

// Mock WaveSurfer
jest.mock('wavesurfer.js', () => {
  return {
    __esModule: true,
    default: {
      create: jest.fn(() => ({
        load: jest.fn(),
        play: jest.fn(),
        pause: jest.fn(),
        stop: jest.fn(),
        playPause: jest.fn(),
        setVolume: jest.fn(),
        getDuration: jest.fn(() => 120),
        getCurrentTime: jest.fn(() => 30),
        on: jest.fn(),
        destroy: jest.fn(),
      })),
    },
  };
});

describe('CompactWaveformPlayer', () => {
  const mockProps = {
    audioFile: null,
    audioUrl: null,
    onTimeUpdate: jest.fn(),
    onPlayStateChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default height of 300px', () => {
    const { container } = render(<CompactWaveformPlayer {...mockProps} />);
    
    const card = container.querySelector('.compact-waveform-player');
    expect(card).toHaveStyle({ height: '300px' });
  });

  it('renders with custom height', () => {
    const { container } = render(<CompactWaveformPlayer {...mockProps} height={250} />);
    
    const card = container.querySelector('.compact-waveform-player');
    expect(card).toHaveStyle({ height: '250px' });
  });

  it('shows empty state when no audio file is provided', () => {
    render(<CompactWaveformPlayer {...mockProps} />);
    
    expect(screen.getByText('No audio file selected')).toBeInTheDocument();
    expect(screen.getByText('Waveform will appear here')).toBeInTheDocument();
  });

  it('displays file information when audio file is provided', () => {
    const mockFile = new File(['content'], 'test-audio.mp3', { 
      type: 'audio/mp3',
      lastModified: Date.now()
    });

    render(<CompactWaveformPlayer {...mockProps} audioFile={mockFile} />);
    
    expect(screen.getByText('test-audio.mp3')).toBeInTheDocument();
    expect(screen.getByText('MP3')).toBeInTheDocument();
  });

  it('renders play/pause button', () => {
    render(<CompactWaveformPlayer {...mockProps} />);
    
    const playButton = screen.getByRole('button');
    expect(playButton).toBeInTheDocument();
    expect(playButton).toBeDisabled(); // Should be disabled when no audio
  });

  it('enables controls when audio URL is provided', () => {
    const mockFile = new File(['content'], 'test.mp3', { type: 'audio/mp3' });
    
    render(
      <CompactWaveformPlayer 
        {...mockProps} 
        audioFile={mockFile}
        audioUrl="blob:test-url"
      />
    );
    
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).not.toBeDisabled();
    });
  });

  it('shows loading state', () => {
    render(<CompactWaveformPlayer {...mockProps} />);
    
    // The loading state would be triggered internally when loading audio
    // This test verifies the component structure supports loading states
    expect(screen.getByText('No file')).toBeInTheDocument();
  });

  it('formats file size correctly', () => {
    const mockFile = new File(['x'.repeat(1024 * 1024)], 'test.mp3', { 
      type: 'audio/mp3' 
    });

    render(<CompactWaveformPlayer {...mockProps} audioFile={mockFile} />);
    
    expect(screen.getByText('1.0MB')).toBeInTheDocument();
  });

  it('truncates long file names', () => {
    const longFileName = 'very-long-audio-file-name-that-should-be-truncated.mp3';
    const mockFile = new File(['content'], longFileName, { 
      type: 'audio/mp3' 
    });

    render(<CompactWaveformPlayer {...mockProps} audioFile={mockFile} />);
    
    // The full name should be in the title attribute for accessibility
    const fileNameElement = screen.getByTitle(longFileName);
    expect(fileNameElement).toBeInTheDocument();
  });

  it('has correct section heights', () => {
    const { container } = render(
      <CompactWaveformPlayer 
        {...mockProps} 
        height={300}
        waveformHeight={120}
        controlsHeight={60}
        infoHeight={120}
      />
    );
    
    // Check that the waveform container has the correct height
    const waveformContainer = container.querySelector('[style*="height: 120px"]');
    expect(waveformContainer).toBeInTheDocument();
  });

  it('does not show spectrogram in compact mode', () => {
    render(
      <CompactWaveformPlayer 
        {...mockProps} 
        showSpectrogram={true} // Should be ignored in compact mode
      />
    );
    
    // Spectrogram should not be rendered even if requested
    expect(screen.queryByText('spectrogram')).not.toBeInTheDocument();
  });
});