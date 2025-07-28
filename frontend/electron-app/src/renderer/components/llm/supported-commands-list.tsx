import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { 
  Search, 
  Volume2, 
  Scissors, 
  Filter, 
  Music, 
  Settings,
  FileAudio,
  Zap,
  Copy,
  Check,
  Radio
} from 'lucide-react';

interface AudioCommand {
  id: string;
  command: string;
  description: string;
  category: 'volume' | 'editing' | 'effects' | 'filters' | 'analysis' | 'conversion' | 'advanced';
  examples: string[];
  parameters?: string[];
  difficulty: 'basic' | 'intermediate' | 'advanced';
  requiresFile: boolean;
}

const audioCommands: AudioCommand[] = [
  // Volume & Dynamics
  {
    id: 'normalize',
    command: 'Normalize audio',
    description: 'Adjust audio levels to a standard peak or RMS level',
    category: 'volume',
    difficulty: 'basic',
    requiresFile: true,
    examples: [
      'Normalize the audio to -3dB',
      'Normalize to -6dB peak level',
      'Apply RMS normalization to -20dB'
    ],
    parameters: ['target_level', 'normalization_type']
  },
  {
    id: 'amplify',
    command: 'Increase/decrease volume',
    description: 'Change the overall volume level by a specific amount',
    category: 'volume',
    difficulty: 'basic',
    requiresFile: true,
    examples: [
      'Increase volume by 6dB',
      'Decrease volume by 3dB',
      'Boost the audio by 10dB'
    ],
    parameters: ['gain_db']
  },
  {
    id: 'compress',
    command: 'Apply compression',
    description: 'Reduce dynamic range using compression',
    category: 'volume',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Apply gentle compression with 3:1 ratio',
      'Compress with fast attack and slow release',
      'Add limiting to prevent clipping'
    ],
    parameters: ['ratio', 'threshold', 'attack', 'release']
  },

  // Editing & Trimming
  {
    id: 'trim',
    command: 'Trim/cut audio',
    description: 'Remove sections from the beginning, end, or middle of audio',
    category: 'editing',
    difficulty: 'basic',
    requiresFile: true,
    examples: [
      'Cut the first 30 seconds',
      'Remove the last 10 seconds',
      'Extract from 1:30 to 3:45'
    ],
    parameters: ['start_time', 'end_time', 'duration']
  },
  {
    id: 'fade',
    command: 'Add fade effects',
    description: 'Apply fade in, fade out, or crossfade effects',
    category: 'editing',
    difficulty: 'basic',
    requiresFile: true,
    examples: [
      'Add 2-second fade in',
      'Apply 3-second fade out',
      'Add fade in and fade out'
    ],
    parameters: ['fade_type', 'duration', 'curve_type']
  },
  {
    id: 'split',
    command: 'Split audio',
    description: 'Divide audio into multiple segments',
    category: 'editing',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Split at silence points',
      'Divide into 5-minute segments',
      'Split at specific timestamps'
    ],
    parameters: ['split_method', 'segment_length', 'silence_threshold']
  },

  // Effects
  {
    id: 'reverb',
    command: 'Add reverb',
    description: 'Apply reverb effects for spatial enhancement',
    category: 'effects',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Add hall reverb with 2-second decay',
      'Apply room reverb',
      'Add dreamy reverb effect'
    ],
    parameters: ['reverb_type', 'decay_time', 'wet_dry_mix']
  },
  {
    id: 'delay',
    command: 'Add delay/echo',
    description: 'Create echo and delay effects',
    category: 'effects',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Add 250ms delay with 3 repeats',
      'Create ping-pong delay effect',
      'Apply slapback echo'
    ],
    parameters: ['delay_time', 'feedback', 'wet_dry_mix']
  },
  {
    id: 'chorus',
    command: 'Add modulation effects',
    description: 'Apply chorus, flanger, or phaser effects',
    category: 'effects',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Add subtle chorus effect',
      'Apply flanger with slow sweep',
      'Create phaser effect'
    ],
    parameters: ['effect_type', 'rate', 'depth', 'feedback']
  },

  // Filters & EQ
  {
    id: 'eq',
    command: 'Apply EQ',
    description: 'Adjust frequency content using equalization',
    category: 'filters',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Boost bass frequencies by 3dB at 80Hz',
      'Cut harsh frequencies around 3kHz',
      'Apply high-pass filter at 100Hz'
    ],
    parameters: ['frequency', 'gain', 'q_factor', 'filter_type']
  },
  {
    id: 'noise_reduction',
    command: 'Remove noise',
    description: 'Reduce background noise, hum, and unwanted sounds',
    category: 'filters',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Remove background noise',
      'Eliminate 60Hz hum',
      'Clean up recording noise'
    ],
    parameters: ['noise_type', 'reduction_amount', 'preserve_speech']
  },
  {
    id: 'filter',
    command: 'Apply filters',
    description: 'Use various filter types to shape frequency content',
    category: 'filters',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Apply low-pass filter at 8kHz',
      'Use band-pass filter 200Hz-2kHz',
      'Add high-pass filter to remove rumble'
    ],
    parameters: ['filter_type', 'cutoff_frequency', 'resonance']
  },

  // Analysis
  {
    id: 'analyze',
    command: 'Analyze audio',
    description: 'Extract technical information and metadata from audio',
    category: 'analysis',
    difficulty: 'basic',
    requiresFile: true,
    examples: [
      'Show audio metadata',
      'Analyze frequency spectrum',
      'Check for clipping and distortion'
    ],
    parameters: ['analysis_type', 'frequency_range']
  },
  {
    id: 'measure',
    command: 'Measure levels',
    description: 'Measure various audio parameters and levels',
    category: 'analysis',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Measure peak and RMS levels',
      'Check dynamic range',
      'Analyze loudness (LUFS)'
    ],
    parameters: ['measurement_type', 'time_range']
  },

  // Conversion
  {
    id: 'convert_format',
    command: 'Convert format',
    description: 'Change audio file format and encoding',
    category: 'conversion',
    difficulty: 'basic',
    requiresFile: true,
    examples: [
      'Convert to MP3 320kbps',
      'Export as WAV 44.1kHz 16-bit',
      'Convert to FLAC lossless'
    ],
    parameters: ['output_format', 'bitrate', 'sample_rate', 'bit_depth']
  },
  {
    id: 'resample',
    command: 'Change sample rate',
    description: 'Convert between different sample rates',
    category: 'conversion',
    difficulty: 'intermediate',
    requiresFile: true,
    examples: [
      'Resample to 44.1kHz',
      'Convert to 48kHz for video',
      'Downsample to 22kHz'
    ],
    parameters: ['target_sample_rate', 'quality']
  },
  {
    id: 'mono_stereo',
    command: 'Convert channels',
    description: 'Convert between mono and stereo, adjust channel configuration',
    category: 'conversion',
    difficulty: 'basic',
    requiresFile: true,
    examples: [
      'Convert to mono',
      'Convert to stereo',
      'Extract left channel only'
    ],
    parameters: ['channel_config', 'mix_method']
  },

  // Advanced
  {
    id: 'spectral_edit',
    command: 'Spectral editing',
    description: 'Advanced frequency-domain editing and processing',
    category: 'advanced',
    difficulty: 'advanced',
    requiresFile: true,
    examples: [
      'Remove specific frequency content',
      'Isolate vocals using spectral subtraction',
      'Remove siren from recording'
    ],
    parameters: ['frequency_range', 'processing_method', 'precision']
  },
  {
    id: 'time_stretch',
    command: 'Time stretching',
    description: 'Change tempo without affecting pitch, or vice versa',
    category: 'advanced',
    difficulty: 'advanced',
    requiresFile: true,
    examples: [
      'Slow down by 20% without pitch change',
      'Speed up to 1.5x original tempo',
      'Change pitch by +2 semitones'
    ],
    parameters: ['time_factor', 'pitch_factor', 'algorithm']
  },
  {
    id: 'batch_process',
    command: 'Batch processing',
    description: 'Apply operations to multiple files simultaneously',
    category: 'advanced',
    difficulty: 'advanced',
    requiresFile: false,
    examples: [
      'Normalize all files in folder',
      'Convert all WAV files to MP3',
      'Apply same EQ to multiple tracks'
    ],
    parameters: ['file_pattern', 'operation', 'output_settings']
  }
];

export const SupportedCommandsList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);

  const categories = [
    { id: 'all', name: 'All Commands', icon: <Settings className="h-4 w-4" /> },
    { id: 'volume', name: 'Volume & Dynamics', icon: <Volume2 className="h-4 w-4" /> },
    { id: 'editing', name: 'Editing & Trimming', icon: <Scissors className="h-4 w-4" /> },
    { id: 'effects', name: 'Effects', icon: <Radio className="h-4 w-4" /> },
    { id: 'filters', name: 'Filters & EQ', icon: <Filter className="h-4 w-4" /> },
    { id: 'analysis', name: 'Analysis', icon: <FileAudio className="h-4 w-4" /> },
    { id: 'conversion', name: 'Conversion', icon: <Music className="h-4 w-4" /> },
    { id: 'advanced', name: 'Advanced', icon: <Zap className="h-4 w-4" /> }
  ];

  const difficulties = [
    { id: 'all', name: 'All Levels' },
    { id: 'basic', name: 'Basic' },
    { id: 'intermediate', name: 'Intermediate' },
    { id: 'advanced', name: 'Advanced' }
  ];

  const filteredCommands = audioCommands.filter(command => {
    const matchesSearch = command.command.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         command.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         command.examples.some(example => example.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || command.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === 'all' || command.difficulty === selectedDifficulty;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  const handleCopyCommand = async (command: string) => {
    try {
      await navigator.clipboard.writeText(command);
      setCopiedCommand(command);
      setTimeout(() => setCopiedCommand(null), 2000);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'volume': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'editing': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'effects': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'filters': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'analysis': return 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200';
      case 'conversion': return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200';
      case 'advanced': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'basic': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'advanced': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileAudio className="h-5 w-5" />
            <span>Supported Audio Commands</span>
            <Badge variant="outline">{filteredCommands.length} commands</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search commands, descriptions, or examples..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Category Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Category:</label>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category.id}
                  variant={selectedCategory === category.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category.id)}
                  className="flex items-center space-x-1"
                >
                  {category.icon}
                  <span>{category.name}</span>
                </Button>
              ))}
            </div>
          </div>

          {/* Difficulty Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Difficulty:</label>
            <div className="flex flex-wrap gap-2">
              {difficulties.map((difficulty) => (
                <Button
                  key={difficulty.id}
                  variant={selectedDifficulty === difficulty.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedDifficulty(difficulty.id)}
                >
                  {difficulty.name}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Commands List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredCommands.map((command) => (
          <Card key={command.id} className="h-fit">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{command.command}</CardTitle>
                <div className="flex items-center space-x-2">
                  <Badge className={`text-xs ${getCategoryColor(command.category)}`}>
                    {command.category}
                  </Badge>
                  <Badge className={`text-xs ${getDifficultyColor(command.difficulty)}`}>
                    {command.difficulty}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {command.description}
              </p>

              {/* Examples */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Examples:</h4>
                <div className="space-y-1">
                  {command.examples.map((example, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-muted/30 rounded text-sm"
                    >
                      <span className="font-mono">{example}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleCopyCommand(example)}
                        className="h-6 w-6 p-0"
                      >
                        {copiedCommand === example ? (
                          <Check className="h-3 w-3" />
                        ) : (
                          <Copy className="h-3 w-3" />
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Parameters */}
              {command.parameters && command.parameters.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Parameters:</h4>
                  <div className="flex flex-wrap gap-1">
                    {command.parameters.map((param, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {param}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Requirements */}
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                {command.requiresFile ? (
                  <Badge variant="outline" className="text-xs">
                    Requires audio file
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-xs">
                    No file required
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCommands.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Search className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
            <p className="text-muted-foreground">
              No commands found matching your search criteria
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Try adjusting your search terms or filters
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};