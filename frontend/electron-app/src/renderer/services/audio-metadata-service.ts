export interface AudioProperties {
  duration: number;
  duration_formatted: string;
  sample_rate: number;
  samples: number;
  channels: number;
  bit_depth: string;
  nyquist_frequency: number;
  frame_count: number;
  rms_energy: number;
  max_amplitude: number;
  dynamic_range: number;
}

export interface SpectralFeatures {
  spectral_centroid: FeatureStats;
  spectral_rolloff: FeatureStats;
  spectral_bandwidth: FeatureStats;
  zero_crossing_rate: FeatureStats;
  mfcc_features: {
    shape: number[];
    mean_per_coefficient: number[];
    std_per_coefficient: number[];
  };
}

export interface FeatureStats {
  mean: number;
  std: number;
  min: number;
  max: number;
}

export interface TemporalFeatures {
  rms_energy: FeatureStats;
  onsets: {
    count: number;
    times: number[];
    density: number;
  };
  tempo: {
    bpm: number;
    beat_count: number;
    beat_times: number[];
    average_beat_interval: number;
  };
}

export interface AdvancedFeatures {
  chroma_features: {
    shape: number[];
    mean_per_pitch_class: number[];
    dominant_pitch_class: number;
  };
  tonnetz_features: {
    shape: number[];
    mean_per_dimension: number[];
  };
  spectral_contrast: {
    shape: number[];
    mean_per_band: number[];
  };
  poly_features: {
    shape: number[];
    coefficients: number[];
  };
}

export interface HarmonicAnalysis {
  harmonic_percussive_separation: {
    harmonic_energy: number;
    percussive_energy: number;
    harmonic_ratio: number;
  };
  pitch_analysis: {
    fundamental_frequencies: number[];
    pitch_count: number;
    mean_f0: number;
    std_f0: number;
    pitch_range: number;
  };
}

export interface RhythmAnalysis {
  tempogram_analysis: {
    shape: number[];
    tempo_bins: number;
    time_frames: number;
  };
  beat_tracking: {
    global_tempo: number;
    beat_count: number;
    beat_consistency: number;
  };
  dynamic_tempo: {
    tempo_variation: number[];
    tempo_stability: number;
    mean_tempo: number;
  };
}

export interface ComprehensiveMetadata {
  success: boolean;
  file_info: {
    file_path: string;
    file_name: string;
    file_size: number;
    file_size_mb: number;
    created_time: number;
    modified_time: number;
    file_extension: string;
  };
  audio_properties: AudioProperties;
  spectral_features: SpectralFeatures;
  temporal_features: TemporalFeatures;
  advanced_features?: AdvancedFeatures;
  harmonic_analysis?: HarmonicAnalysis;
  rhythm_analysis?: RhythmAnalysis;
  extraction_timestamp: string;
  error?: string;
}

export interface AudioSummary {
  success: boolean;
  file_name: string;
  duration: string;
  sample_rate: string;
  file_size: string;
  brightness: string;
  energy_level: string;
  tempo: string;
  onset_density: string;
  dynamic_range: string;
  error?: string;
}

export interface WaveformData {
  success: boolean;
  waveform: number[];
  time_axis: number[];
  sample_rate: number;
  duration: number;
  original_samples: number;
  downsampled_samples: number;
  error?: string;
}

export interface SpectrogramData {
  success: boolean;
  spectrogram: number[][];
  frequencies: number[];
  times: number[];
  shape: number[];
  sample_rate: number;
  n_fft: number;
  hop_length: number;
  error?: string;
}

export class AudioMetadataService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://127.0.0.1:5000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Get comprehensive metadata analysis for an audio file
   */
  async getAdvancedMetadata(fileId: string, includeAdvanced: boolean = true): Promise<ComprehensiveMetadata> {
    try {
      const url = `${this.baseUrl}/api/audio/metadata/advanced/${fileId}?include_advanced=${includeAdvanced}`;
      const response = await fetch(url);
      const result = await response.json();
      return result;
    } catch (error) {
      return {
        success: false,
        error: `Failed to get advanced metadata: ${error instanceof Error ? error.message : 'Unknown error'}`,
        file_info: {} as any,
        audio_properties: {} as any,
        spectral_features: {} as any,
        temporal_features: {} as any,
        extraction_timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Get a quick summary of audio characteristics
   */
  async getAudioSummary(fileId: string): Promise<AudioSummary> {
    try {
      const response = await fetch(`${this.baseUrl}/api/audio/summary/${fileId}`);
      const result = await response.json();
      return result;
    } catch (error) {
      return {
        success: false,
        error: `Failed to get audio summary: ${error instanceof Error ? error.message : 'Unknown error'}`,
        file_name: '',
        duration: '',
        sample_rate: '',
        file_size: '',
        brightness: '',
        energy_level: '',
        tempo: '',
        onset_density: '',
        dynamic_range: ''
      };
    }
  }

  /**
   * Get waveform data for visualization
   */
  async getWaveformData(fileId: string, maxPoints: number = 1000): Promise<WaveformData> {
    try {
      const url = `${this.baseUrl}/api/audio/waveform/${fileId}?max_points=${maxPoints}`;
      const response = await fetch(url);
      const result = await response.json();
      return result;
    } catch (error) {
      return {
        success: false,
        error: `Failed to get waveform data: ${error instanceof Error ? error.message : 'Unknown error'}`,
        waveform: [],
        time_axis: [],
        sample_rate: 0,
        duration: 0,
        original_samples: 0,
        downsampled_samples: 0
      };
    }
  }

  /**
   * Get spectrogram data for visualization
   */
  async getSpectrogramData(fileId: string, nFft: number = 2048, hopLength: number = 512): Promise<SpectrogramData> {
    try {
      const url = `${this.baseUrl}/api/audio/spectrogram/${fileId}?n_fft=${nFft}&hop_length=${hopLength}`;
      const response = await fetch(url);
      const result = await response.json();
      return result;
    } catch (error) {
      return {
        success: false,
        error: `Failed to get spectrogram data: ${error instanceof Error ? error.message : 'Unknown error'}`,
        spectrogram: [],
        frequencies: [],
        times: [],
        shape: [],
        sample_rate: 0,
        n_fft: 0,
        hop_length: 0
      };
    }
  }

  /**
   * Format metadata for display
   */
  formatMetadataForDisplay(metadata: ComprehensiveMetadata): Record<string, any> {
    if (!metadata.success) {
      return { error: metadata.error };
    }

    const formatted = {
      'File Information': {
        'Name': metadata.file_info.file_name,
        'Size': `${metadata.file_info.file_size_mb} MB`,
        'Extension': metadata.file_info.file_extension,
        'Created': new Date(metadata.file_info.created_time * 1000).toLocaleString()
      },
      'Audio Properties': {
        'Duration': metadata.audio_properties.duration_formatted,
        'Sample Rate': `${metadata.audio_properties.sample_rate} Hz`,
        'Channels': metadata.audio_properties.channels,
        'Samples': metadata.audio_properties.samples.toLocaleString(),
        'RMS Energy': metadata.audio_properties.rms_energy.toFixed(4),
        'Max Amplitude': metadata.audio_properties.max_amplitude.toFixed(4),
        'Dynamic Range': metadata.audio_properties.dynamic_range.toFixed(4)
      },
      'Spectral Analysis': {
        'Spectral Centroid (Mean)': `${metadata.spectral_features.spectral_centroid.mean.toFixed(2)} Hz`,
        'Spectral Rolloff (Mean)': `${metadata.spectral_features.spectral_rolloff.mean.toFixed(2)} Hz`,
        'Spectral Bandwidth (Mean)': `${metadata.spectral_features.spectral_bandwidth.mean.toFixed(2)} Hz`,
        'Zero Crossing Rate (Mean)': metadata.spectral_features.zero_crossing_rate.mean.toFixed(4)
      },
      'Temporal Analysis': {
        'Tempo': `${metadata.temporal_features.tempo.bpm.toFixed(1)} BPM`,
        'Beat Count': metadata.temporal_features.tempo.beat_count,
        'Onset Count': metadata.temporal_features.onsets.count,
        'Onset Density': `${metadata.temporal_features.onsets.density.toFixed(2)} onsets/sec`
      }
    };

    if (metadata.advanced_features) {
      formatted['Advanced Features'] = {
        'Dominant Pitch Class': metadata.advanced_features.chroma_features.dominant_pitch_class,
        'Chroma Shape': metadata.advanced_features.chroma_features.shape.join(' x '),
        'Tonnetz Shape': metadata.advanced_features.tonnetz_features.shape.join(' x '),
        'Spectral Contrast Shape': metadata.advanced_features.spectral_contrast.shape.join(' x ')
      };
    }

    if (metadata.harmonic_analysis) {
      formatted['Harmonic Analysis'] = {
        'Harmonic Ratio': metadata.harmonic_analysis.harmonic_percussive_separation.harmonic_ratio.toFixed(3),
        'Pitch Count': metadata.harmonic_analysis.pitch_analysis.pitch_count,
        'Mean F0': `${metadata.harmonic_analysis.pitch_analysis.mean_f0.toFixed(2)} Hz`,
        'Pitch Range': `${metadata.harmonic_analysis.pitch_analysis.pitch_range.toFixed(2)} Hz`
      };
    }

    if (metadata.rhythm_analysis) {
      formatted['Rhythm Analysis'] = {
        'Global Tempo': `${metadata.rhythm_analysis.beat_tracking.global_tempo.toFixed(1)} BPM`,
        'Beat Consistency': metadata.rhythm_analysis.beat_tracking.beat_consistency.toFixed(4),
        'Tempo Stability': metadata.rhythm_analysis.dynamic_tempo.tempo_stability.toFixed(2),
        'Mean Dynamic Tempo': `${metadata.rhythm_analysis.dynamic_tempo.mean_tempo.toFixed(1)} BPM`
      };
    }

    return formatted;
  }

  /**
   * Get color for visualization based on value range
   */
  getColorForValue(value: number, min: number, max: number): string {
    const normalized = (value - min) / (max - min);
    const hue = (1 - normalized) * 240; // Blue to red
    return `hsl(${hue}, 70%, 50%)`;
  }

  /**
   * Create visualization data for charts
   */
  createVisualizationData(metadata: ComprehensiveMetadata): Record<string, any> {
    if (!metadata.success) {
      return {};
    }

    const visualizations: Record<string, any> = {};

    // MFCC coefficients chart
    if (metadata.spectral_features.mfcc_features) {
      visualizations.mfcc = {
        labels: Array.from({ length: metadata.spectral_features.mfcc_features.mean_per_coefficient.length }, (_, i) => `MFCC ${i + 1}`),
        datasets: [{
          label: 'Mean MFCC Coefficients',
          data: metadata.spectral_features.mfcc_features.mean_per_coefficient,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      };
    }

    // Chroma features chart
    if (metadata.advanced_features?.chroma_features) {
      const pitchClasses = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
      visualizations.chroma = {
        labels: pitchClasses,
        datasets: [{
          label: 'Chroma Features',
          data: metadata.advanced_features.chroma_features.mean_per_pitch_class,
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }]
      };
    }

    // Spectral contrast chart
    if (metadata.advanced_features?.spectral_contrast) {
      visualizations.spectralContrast = {
        labels: Array.from({ length: metadata.advanced_features.spectral_contrast.mean_per_band.length }, (_, i) => `Band ${i + 1}`),
        datasets: [{
          label: 'Spectral Contrast',
          data: metadata.advanced_features.spectral_contrast.mean_per_band,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }]
      };
    }

    return visualizations;
  }
}