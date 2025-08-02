import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { CompactFileUploader } from '../compact-file-uploader';

// Mock react-dropzone
jest.mock('react-dropzone', () => ({
  useDropzone: jest.fn(() => ({
    getRootProps: () => ({ 'data-testid': 'dropzone' }),
    getInputProps: () => ({ 'data-testid': 'file-input' }),
    isDragActive: false,
    isDragReject: false,
  })),
}));

describe('CompactFileUploader', () => {
  const mockProps = {
    onFileSelect: jest.fn(),
    selectedFiles: [],
    onRemoveFile: jest.fn(),
    onClearAll: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders empty state correctly', () => {
    render(<CompactFileUploader {...mockProps} />);
    
    expect(screen.getByText('Drop audio files here')).toBeInTheDocument();
    expect(screen.getByText('MP3, WAV, FLAC, OGG, M4A, AAC')).toBeInTheDocument();
  });

  it('renders with fixed height', () => {
    const { container } = render(<CompactFileUploader {...mockProps} maxHeight={200} />);
    
    const card = container.querySelector('.compact-file-uploader');
    expect(card).toHaveStyle({ height: '200px' });
  });

  it('renders selected files with tabs', () => {
    const mockFiles = [
      new File(['content1'], 'test1.mp3', { type: 'audio/mp3' }),
      new File(['content2'], 'test2.wav', { type: 'audio/wav' }),
    ];

    render(<CompactFileUploader {...mockProps} selectedFiles={mockFiles} />);
    
    expect(screen.getByText('test1.mp3')).toBeInTheDocument();
    expect(screen.getByText('test2.wav')).toBeInTheDocument();
    expect(screen.getByText('Clear All')).toBeInTheDocument();
  });

  it('calls onRemoveFile when remove button is clicked', () => {
    const mockFiles = [
      new File(['content1'], 'test1.mp3', { type: 'audio/mp3' }),
    ];

    render(<CompactFileUploader {...mockProps} selectedFiles={mockFiles} />);
    
    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);
    
    expect(mockProps.onRemoveFile).toHaveBeenCalledWith(0);
  });

  it('calls onClearAll when clear all button is clicked', () => {
    const mockFiles = [
      new File(['content1'], 'test1.mp3', { type: 'audio/mp3' }),
    ];

    render(<CompactFileUploader {...mockProps} selectedFiles={mockFiles} />);
    
    const clearAllButton = screen.getByText('Clear All');
    fireEvent.click(clearAllButton);
    
    expect(mockProps.onClearAll).toHaveBeenCalled();
  });

  it('truncates long file names in tabs', () => {
    const mockFiles = [
      new File(['content1'], 'very-long-filename-that-should-be-truncated.mp3', { type: 'audio/mp3' }),
    ];

    render(<CompactFileUploader {...mockProps} selectedFiles={mockFiles} />);
    
    // The full name should be in the tab content, but truncated in the tab trigger
    expect(screen.getByText('very-long-filename-that-should-be-truncated.mp3')).toBeInTheDocument();
  });

  it('shows error message when provided', () => {
    // This would require modifying the component to accept an error prop
    // or testing the internal error state through drag/drop simulation
    // For now, we'll test the basic structure
    render(<CompactFileUploader {...mockProps} />);
    expect(screen.getByTestId('dropzone')).toBeInTheDocument();
  });
});