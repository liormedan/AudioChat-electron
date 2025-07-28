import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { 
  BookOpen, 
  Search, 
  Copy, 
  Check, 
  Download,
  FileText,
  Code,
  Play,
  Info,
  ExternalLink
} from 'lucide-react';

interface CommandDoc {
  id: string;
  command: string;
  category: string;
  description: string;
  syntax: string;
  parameters: {
    name: string;
    type: string;
    required: boolean;
    description: string;
    default?: string;
    examples?: string[];
  }[];
  examples: {
    command: string;
    description: string;
    result: string;
  }[];
  notes?: string[];
  relatedCommands?: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  version: string;
}

const commandDocs: CommandDoc[] = [
  {
    id: 'normalize',
    command: 'Normalize Audio',
    category: 'Volume Control',
    description: 'Adjusts audio levels to a standard peak or RMS level, ensuring consistent volume across different audio files.',
    syntax: 'normalize [target_level] [type]',
    difficulty: 'beginner',
    version: '1.0.0',
    parameters: [
      {
        name: 'target_level',
        type: 'number',
        required: false,
        description: 'Target level in dB (default: -3dB for peak, -20dB for RMS)',
        default: '-3',
        examples: ['-3', '-6', '-12']
      },
      {
        name: 'type',
        type: 'string',
        required: false,
        description: 'Normalization type: peak or rms',
        default: 'peak',
        examples: ['peak', 'rms']
      }
    ],
    examples: [
      {
        command: 'Normalize the audio to -3dB',
        description: 'Standard peak normalization',
        result: 'Audio normalized to -3dB peak level'
      },
      {
        command: 'Normalize to -20dB RMS',
        description: 'RMS normalization for consistent perceived loudness',
        result: 'Audio normalized to -20dB RMS level'
      },
      {
        command: 'Apply peak normalization to -6dB',
        description: 'Conservative peak normalization',
        result: 'Audio normalized to -6dB peak level with headroom'
      }
    ],
    notes: [
      'Peak normalization adjusts the highest peak to the target level',
      'RMS normalization adjusts the average level for perceived loudness',
      'Use -3dB to -6dB for peak normalization to avoid clipping',
      'RMS normalization is better for matching loudness between tracks'
    ],
    relatedCommands: ['amplify', 'compress', 'limit']
  },
  {
    id: 'noise-reduction',
    command: 'Remove Noise',
    category: 'Cleanup',
    description: 'Reduces or removes unwanted background noise, hum, and other audio artifacts using advanced noise reduction algorithms.',
    syntax: 'remove noise [type] [amount] [preserve_speech]',
    difficulty: 'intermediate',
    version: '1.0.0',
    parameters: [
      {
        name: 'type',
        type: 'string',
        required: false,
        description: 'Type of noise to remove',
        default: 'auto',
        examples: ['auto', 'hum', 'hiss', 'click', 'broadband']
      },
      {
        name: 'amount',
        type: 'number',
        required: false,
        description: 'Reduction amount (0-100%)',
        default: '50',
        examples: ['25', '50', '75']
      },
      {
        name: 'preserve_speech',
        type: 'boolean',
        required: false,
        description: 'Preserve speech quality during noise reduction',
        default: 'true',
        examples: ['true', 'false']
      }
    ],
    examples: [
      {
        command: 'Remove background noise',
        description: 'Automatic noise detection and removal',
        result: 'Background noise reduced by 50% with speech preservation'
      },
      {
        command: 'Eliminate 60Hz hum',
        description: 'Remove electrical hum at 60Hz',
        result: '60Hz hum and harmonics removed'
      },
      {
        command: 'Clean up recording noise with 75% reduction',
        description: 'Aggressive noise reduction',
        result: 'Recording noise reduced by 75%'
      }
    ],
    notes: [
      'Start with moderate settings (50%) and adjust as needed',
      'Aggressive noise reduction may affect audio quality',
      'Use speech preservation for voice recordings',
      'Different noise types require different algorithms'
    ],
    relatedCommands: ['filter', 'eq', 'gate']
  },
  {
    id: 'eq',
    command: 'Apply EQ',
    category: 'Frequency Control',
    description: 'Adjusts the frequency content of audio using equalization. Allows boosting or cutting specific frequency ranges.',
    syntax: 'eq [frequency] [gain] [q_factor] [filter_type]',
    difficulty: 'intermediate',
    version: '1.0.0',
    parameters: [
      {
        name: 'frequency',
        type: 'number',
        required: true,
        description: 'Center frequency in Hz',
        examples: ['80', '1000', '5000', '10000']
      },
      {
        name: 'gain',
        type: 'number',
        required: true,
        description: 'Gain in dB (positive = boost, negative = cut)',
        examples: ['+3', '-6', '+12', '-12']
      },
      {
        name: 'q_factor',
        type: 'number',
        required: false,
        description: 'Q factor (bandwidth control)',
        default: '1.0',
        examples: ['0.5', '1.0', '2.0', '5.0']
      },
      {
        name: 'filter_type',
        type: 'string',
        required: false,
        description: 'Filter type',
        default: 'bell',
        examples: ['bell', 'highpass', 'lowpass', 'shelf']
      }
    ],
    examples: [
      {
        command: 'Boost bass frequencies by 3dB at 80Hz',
        description: 'Enhance low-end with bell filter',
        result: 'Bass frequencies around 80Hz boosted by 3dB'
      },
      {
        command: 'Cut harsh frequencies around 3kHz by 6dB',
        description: 'Reduce harshness in midrange',
        result: 'Frequencies around 3kHz reduced by 6dB'
      },
      {
        command: 'Apply high-pass filter at 100Hz',
        description: 'Remove low-frequency rumble',
        result: 'Frequencies below 100Hz filtered out'
      }
    ],
    notes: [
      'Use narrow Q (high values) for precise corrections',
      'Use wide Q (low values) for musical adjustments',
      'High-pass filters remove rumble and low-frequency noise',
      'Be careful with large boosts as they can cause distortion'
    ],
    relatedCommands: ['filter', 'normalize', 'compress']
  },
  {
    id: 'reverb',
    command: 'Add Reverb',
    category: 'Effects',
    description: 'Adds reverb effect to create spatial depth and ambience. Simulates acoustic spaces from small rooms to large halls.',
    syntax: 'reverb [type] [decay_time] [wet_dry_mix] [pre_delay]',
    difficulty: 'intermediate',
    version: '1.0.0',
    parameters: [
      {
        name: 'type',
        type: 'string',
        required: false,
        description: 'Reverb type/space simulation',
        default: 'hall',
        examples: ['room', 'hall', 'plate', 'spring', 'chamber']
      },
      {
        name: 'decay_time',
        type: 'number',
        required: false,
        description: 'Reverb decay time in seconds',
        default: '2.0',
        examples: ['0.5', '1.0', '2.0', '4.0']
      },
      {
        name: 'wet_dry_mix',
        type: 'number',
        required: false,
        description: 'Wet/dry mix percentage (0-100%)',
        default: '30',
        examples: ['10', '25', '50', '75']
      },
      {
        name: 'pre_delay',
        type: 'number',
        required: false,
        description: 'Pre-delay in milliseconds',
        default: '20',
        examples: ['0', '20', '50', '100']
      }
    ],
    examples: [
      {
        command: 'Add hall reverb with 2-second decay',
        description: 'Classic hall reverb for spacious sound',
        result: 'Hall reverb applied with 2-second decay time'
      },
      {
        command: 'Apply room reverb with 30% mix',
        description: 'Subtle room ambience',
        result: 'Room reverb applied at 30% wet signal'
      },
      {
        command: 'Create dreamy reverb effect',
        description: 'Atmospheric reverb with long decay',
        result: 'Long, dreamy reverb effect applied'
      }
    ],
    notes: [
      'Longer decay times create more spacious sounds',
      'Use pre-delay to separate direct sound from reverb',
      'Plate reverb is great for vocals and drums',
      'Spring reverb gives vintage character'
    ],
    relatedCommands: ['delay', 'chorus', 'compress']
  },
  {
    id: 'spectral-edit',
    command: 'Spectral Editing',
    category: 'Advanced',
    description: 'Advanced frequency-domain editing for precise removal or isolation of specific frequency content over time.',
    syntax: 'spectral edit [frequency_range] [time_range] [operation] [precision]',
    difficulty: 'advanced',
    version: '1.1.0',
    parameters: [
      {
        name: 'frequency_range',
        type: 'string',
        required: true,
        description: 'Frequency range in Hz (e.g., "1000-3000")',
        examples: ['100-500', '1000-3000', '5000-8000']
      },
      {
        name: 'time_range',
        type: 'string',
        required: false,
        description: 'Time range in seconds (e.g., "10-15")',
        examples: ['0-5', '10-15', '30-45']
      },
      {
        name: 'operation',
        type: 'string',
        required: false,
        description: 'Operation to perform',
        default: 'remove',
        examples: ['remove', 'isolate', 'reduce', 'enhance']
      },
      {
        name: 'precision',
        type: 'string',
        required: false,
        description: 'Processing precision',
        default: 'medium',
        examples: ['low', 'medium', 'high', 'ultra']
      }
    ],
    examples: [
      {
        command: 'Remove specific frequency content between 2-4kHz',
        description: 'Surgical frequency removal',
        result: 'Frequencies between 2-4kHz removed with high precision'
      },
      {
        command: 'Isolate vocals using spectral subtraction',
        description: 'Extract vocal content from mix',
        result: 'Vocal frequencies isolated using spectral analysis'
      },
      {
        command: 'Remove siren from recording at 1-2kHz from 30-35 seconds',
        description: 'Time and frequency specific removal',
        result: 'Siren frequencies removed from specified time range'
      }
    ],
    notes: [
      'Spectral editing works in the frequency domain',
      'Higher precision takes longer to process',
      'Use for removing specific unwanted sounds',
      'Can cause artifacts if used aggressively'
    ],
    relatedCommands: ['eq', 'filter', 'noise-reduction']
  }
];

export const CommandDocumentation: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedCommand, setSelectedCommand] = useState<CommandDoc | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const categories = ['all', ...Array.from(new Set(commandDocs.map(doc => doc.category)))];
  const difficulties = ['all', 'beginner', 'intermediate', 'advanced'];

  const filteredDocs = commandDocs.filter(doc => {
    const matchesSearch = doc.command.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === 'all' || doc.difficulty === selectedDifficulty;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  const handleCopyText = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(text);
      setTimeout(() => setCopiedText(null), 2000);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
    }
  };

  const exportDocumentation = () => {
    const docContent = commandDocs.map(doc => {
      return `# ${doc.command}

**Category:** ${doc.category}
**Difficulty:** ${doc.difficulty}
**Version:** ${doc.version}

## Description
${doc.description}

## Syntax
\`${doc.syntax}\`

## Parameters
${doc.parameters.map(param => 
  `- **${param.name}** (${param.type}${param.required ? ', required' : ', optional'}): ${param.description}${param.default ? ` (default: ${param.default})` : ''}`
).join('\n')}

## Examples
${doc.examples.map(example => 
  `### ${example.description}
\`${example.command}\`
Result: ${example.result}`
).join('\n\n')}

${doc.notes ? `## Notes
${doc.notes.map(note => `- ${note}`).join('\n')}` : ''}

${doc.relatedCommands ? `## Related Commands
${doc.relatedCommands.join(', ')}` : ''}

---
`;
    }).join('\n');

    const blob = new Blob([docContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'audio-commands-documentation.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'advanced': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Documentation Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <BookOpen className="h-5 w-5" />
              <span>Audio Command Documentation</span>
            </div>
            <Button onClick={exportDocumentation} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Docs
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search commands and descriptions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium">Category:</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="text-sm border rounded px-2 py-1"
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium">Difficulty:</label>
              <select
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                className="text-sm border rounded px-2 py-1"
              >
                {difficulties.map(difficulty => (
                  <option key={difficulty} value={difficulty}>
                    {difficulty === 'all' ? 'All Levels' : difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Commands List */}
        <Card>
          <CardHeader>
            <CardTitle>Commands ({filteredDocs.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredDocs.map((doc) => (
                <div
                  key={doc.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedCommand?.id === doc.id
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:bg-muted/50'
                  }`}
                  onClick={() => setSelectedCommand(doc)}
                >
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-medium text-sm">{doc.command}</h4>
                    <Badge className={`text-xs ${getDifficultyColor(doc.difficulty)}`}>
                      {doc.difficulty}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">
                    {doc.description.substring(0, 100)}...
                  </p>
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-xs">
                      {doc.category}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      v{doc.version}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Command Details */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>Command Details</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedCommand ? (
              <div className="space-y-6">
                {/* Command Header */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold">{selectedCommand.command}</h2>
                    <div className="flex items-center space-x-2">
                      <Badge className={getDifficultyColor(selectedCommand.difficulty)}>
                        {selectedCommand.difficulty}
                      </Badge>
                      <Badge variant="outline">v{selectedCommand.version}</Badge>
                    </div>
                  </div>
                  <Badge variant="secondary">{selectedCommand.category}</Badge>
                  <p className="text-muted-foreground">{selectedCommand.description}</p>
                </div>

                {/* Syntax */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold flex items-center space-x-2">
                    <Code className="h-4 w-4" />
                    <span>Syntax</span>
                  </h3>
                  <div className="bg-muted/30 rounded-lg p-3 font-mono text-sm flex items-center justify-between">
                    <code>{selectedCommand.syntax}</code>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCopyText(selectedCommand.syntax)}
                    >
                      {copiedText === selectedCommand.syntax ? (
                        <Check className="h-3 w-3" />
                      ) : (
                        <Copy className="h-3 w-3" />
                      )}
                    </Button>
                  </div>
                </div>

                {/* Parameters */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Parameters</h3>
                  <div className="space-y-3">
                    {selectedCommand.parameters.map((param, index) => (
                      <div key={index} className="border rounded-lg p-3">
                        <div className="flex items-center space-x-2 mb-2">
                          <code className="font-mono text-sm bg-muted px-2 py-1 rounded">
                            {param.name}
                          </code>
                          <Badge variant="outline" className="text-xs">
                            {param.type}
                          </Badge>
                          <Badge variant={param.required ? 'destructive' : 'secondary'} className="text-xs">
                            {param.required ? 'required' : 'optional'}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {param.description}
                        </p>
                        {param.default && (
                          <p className="text-xs">
                            <strong>Default:</strong> {param.default}
                          </p>
                        )}
                        {param.examples && (
                          <p className="text-xs">
                            <strong>Examples:</strong> {param.examples.join(', ')}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Examples */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold flex items-center space-x-2">
                    <Play className="h-4 w-4" />
                    <span>Examples</span>
                  </h3>
                  <div className="space-y-3">
                    {selectedCommand.examples.map((example, index) => (
                      <div key={index} className="border rounded-lg p-3">
                        <h4 className="font-medium text-sm mb-2">{example.description}</h4>
                        <div className="bg-muted/30 rounded p-2 font-mono text-sm flex items-center justify-between mb-2">
                          <code>{example.command}</code>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCopyText(example.command)}
                          >
                            {copiedText === example.command ? (
                              <Check className="h-3 w-3" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                          </Button>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          <strong>Result:</strong> {example.result}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Notes */}
                {selectedCommand.notes && (
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold flex items-center space-x-2">
                      <Info className="h-4 w-4" />
                      <span>Notes</span>
                    </h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                      {selectedCommand.notes.map((note, index) => (
                        <li key={index}>{note}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Related Commands */}
                {selectedCommand.relatedCommands && (
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold flex items-center space-x-2">
                      <ExternalLink className="h-4 w-4" />
                      <span>Related Commands</span>
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedCommand.relatedCommands.map((relatedCmd, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            const relatedDoc = commandDocs.find(doc => 
                              doc.command.toLowerCase().includes(relatedCmd.toLowerCase())
                            );
                            if (relatedDoc) setSelectedCommand(relatedDoc);
                          }}
                        >
                          {relatedCmd}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Select a command from the list to view detailed documentation</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};