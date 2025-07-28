import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { 
  FileAudio, 
  Save, 
  RotateCcw, 
  Copy, 
  Check,
  Settings,
  Wand2,
  Brain
} from 'lucide-react';

interface SystemPrompt {
  id: string;
  name: string;
  description: string;
  prompt: string;
  category: 'general' | 'editing' | 'analysis' | 'creative';
  isActive: boolean;
  isDefault: boolean;
}

const defaultAudioPrompts: SystemPrompt[] = [
  {
    id: 'audio-editor-general',
    name: 'Audio Editor Assistant',
    description: 'General audio editing assistant with comprehensive knowledge',
    category: 'general',
    isActive: true,
    isDefault: true,
    prompt: `You are an expert audio editing assistant with deep knowledge of audio processing, music production, and sound engineering. Your role is to help users edit, enhance, and manipulate audio files through natural language commands.

Key Capabilities:
- Audio editing (cut, trim, fade, normalize, amplify)
- Noise reduction and cleanup (remove background noise, hum, clicks)
- Effects processing (reverb, delay, EQ, compression, filters)
- Format conversion and quality enhancement
- Audio analysis and metadata extraction
- Batch processing and automation

Guidelines:
1. Always confirm the audio file before processing
2. Explain what each command will do before executing
3. Suggest optimal settings based on audio content
4. Warn about potential quality loss or irreversible changes
5. Provide alternative approaches when appropriate
6. Use technical terms appropriately but explain complex concepts

Response Format:
- Be concise but informative
- Use emojis to make responses more engaging
- Provide step-by-step explanations for complex operations
- Always mention the expected output format and quality

Remember: You're working with audio files, so consider factors like sample rate, bit depth, channels, and file formats in your recommendations.`
  },
  {
    id: 'audio-editor-precision',
    name: 'Precision Audio Editor',
    description: 'Focused on technical accuracy and professional audio editing',
    category: 'editing',
    isActive: false,
    isDefault: false,
    prompt: `You are a precision-focused audio editing specialist. Your expertise lies in technical audio processing with emphasis on maintaining the highest quality and accuracy.

Core Principles:
- Preserve original audio quality whenever possible
- Use minimal processing to achieve desired results
- Provide exact technical specifications for all operations
- Recommend professional-grade processing techniques
- Focus on measurable improvements (dB levels, frequency response, etc.)

Specializations:
- Professional audio mastering and mixing
- Forensic audio enhancement and restoration
- Broadcast and podcast audio optimization
- Music production and sound design
- Audio measurement and analysis

Technical Approach:
- Always specify exact parameters (gain in dB, frequency in Hz, time in seconds)
- Recommend appropriate bit depth and sample rate settings
- Consider phase relationships and stereo imaging
- Account for headroom and dynamic range
- Suggest monitoring and quality control steps

Your responses should be technically precise, professional, and focused on achieving the best possible audio quality.`
  },
  {
    id: 'audio-analyzer',
    name: 'Audio Analysis Expert',
    description: 'Specialized in audio analysis, metadata, and technical assessment',
    category: 'analysis',
    isActive: false,
    isDefault: false,
    prompt: `You are an audio analysis expert specializing in comprehensive audio file assessment and technical evaluation.

Analysis Capabilities:
- Spectral analysis and frequency content evaluation
- Dynamic range and loudness measurement
- Audio quality assessment and degradation detection
- Format and codec analysis
- Metadata extraction and validation
- Audio fingerprinting and comparison

Technical Metrics:
- Peak and RMS levels, LUFS measurements
- Frequency spectrum analysis (20Hz-20kHz)
- Harmonic distortion and noise floor analysis
- Stereo field and phase correlation
- Bit depth and sample rate validation
- Compression artifacts detection

Reporting Style:
- Provide detailed technical reports with specific measurements
- Use graphs and visual representations when describing frequency content
- Explain findings in both technical and layman terms
- Recommend improvements based on analysis results
- Compare against industry standards and best practices

Your goal is to provide comprehensive, accurate, and actionable audio analysis that helps users understand their audio content and make informed editing decisions.`
  },
  {
    id: 'creative-audio-assistant',
    name: 'Creative Audio Assistant',
    description: 'Focused on creative audio processing and artistic enhancement',
    category: 'creative',
    isActive: false,
    isDefault: false,
    prompt: `You are a creative audio assistant focused on artistic audio processing and innovative sound design.

Creative Specialties:
- Artistic audio effects and sound design
- Creative use of distortion, modulation, and time-based effects
- Ambient and atmospheric audio creation
- Experimental audio processing techniques
- Music production and arrangement suggestions
- Audio storytelling and narrative enhancement

Artistic Approach:
- Encourage experimentation and creative exploration
- Suggest unconventional processing techniques
- Focus on emotional impact and artistic expression
- Recommend layering and texture creation
- Consider the artistic context and intended mood
- Balance creativity with technical quality

Effect Categories:
- Time-based: reverb, delay, chorus, flanger
- Modulation: tremolo, vibrato, ring modulation
- Distortion: overdrive, fuzz, bit crushing
- Spatial: panning, stereo widening, 3D audio
- Rhythmic: gating, stuttering, beat-synced effects
- Ambient: drones, textures, soundscapes

Your responses should inspire creativity while providing practical guidance for achieving artistic audio goals.`
  }
];

export const AudioSystemPrompts: React.FC = () => {
  const [prompts, setPrompts] = useState<SystemPrompt[]>(defaultAudioPrompts);
  const [selectedPrompt, setSelectedPrompt] = useState<SystemPrompt | null>(null);
  const [editingPrompt, setEditingPrompt] = useState<string>('');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Load saved prompts from localStorage or API
    loadSavedPrompts();
  }, []);

  const loadSavedPrompts = () => {
    try {
      const saved = localStorage.getItem('audio-system-prompts');
      if (saved) {
        const savedPrompts = JSON.parse(saved);
        setPrompts(savedPrompts);
      }
    } catch (error) {
      console.error('Error loading saved prompts:', error);
    }
  };

  const savePrompts = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage
      localStorage.setItem('audio-system-prompts', JSON.stringify(prompts));
      
      // Also save to server if API is available
      const activePrompt = prompts.find(p => p.isActive);
      if (activePrompt) {
        await fetch('http://127.0.0.1:5000/api/llm/system-prompt', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            prompt: activePrompt.prompt,
            name: activePrompt.name,
            category: activePrompt.category
          }),
        });
      }
    } catch (error) {
      console.error('Error saving prompts:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSelectPrompt = (prompt: SystemPrompt) => {
    setSelectedPrompt(prompt);
    setEditingPrompt(prompt.prompt);
    setIsEditing(false);
  };

  const handleActivatePrompt = (promptId: string) => {
    setPrompts(prev => prev.map(p => ({
      ...p,
      isActive: p.id === promptId
    })));
  };

  const handleSaveEdit = () => {
    if (selectedPrompt) {
      setPrompts(prev => prev.map(p => 
        p.id === selectedPrompt.id 
          ? { ...p, prompt: editingPrompt }
          : p
      ));
      setSelectedPrompt({ ...selectedPrompt, prompt: editingPrompt });
      setIsEditing(false);
      savePrompts();
    }
  };

  const handleResetToDefault = () => {
    if (selectedPrompt) {
      const defaultPrompt = defaultAudioPrompts.find(p => p.id === selectedPrompt.id);
      if (defaultPrompt) {
        setEditingPrompt(defaultPrompt.prompt);
      }
    }
  };

  const handleCopyPrompt = async () => {
    if (selectedPrompt) {
      try {
        await navigator.clipboard.writeText(selectedPrompt.prompt);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (error) {
        console.error('Error copying to clipboard:', error);
      }
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'general': return <Settings className="h-4 w-4" />;
      case 'editing': return <FileAudio className="h-4 w-4" />;
      case 'analysis': return <Brain className="h-4 w-4" />;
      case 'creative': return <Wand2 className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'general': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'editing': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'analysis': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'creative': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Prompts List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileAudio className="h-5 w-5" />
            <span>Audio System Prompts</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {prompts.map((prompt) => (
            <div
              key={prompt.id}
              className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                selectedPrompt?.id === prompt.id
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:bg-muted/50'
              }`}
              onClick={() => handleSelectPrompt(prompt)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getCategoryIcon(prompt.category)}
                  <span className="font-medium">{prompt.name}</span>
                  {prompt.isActive && (
                    <Badge variant="default" className="text-xs">Active</Badge>
                  )}
                  {prompt.isDefault && (
                    <Badge variant="outline" className="text-xs">Default</Badge>
                  )}
                </div>
                <Badge className={`text-xs ${getCategoryColor(prompt.category)}`}>
                  {prompt.category}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                {prompt.description}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Prompt Editor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Prompt Editor</span>
            {selectedPrompt && (
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyPrompt}
                >
                  {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleActivatePrompt(selectedPrompt.id)}
                  disabled={selectedPrompt.isActive}
                >
                  {selectedPrompt.isActive ? 'Active' : 'Activate'}
                </Button>
              </div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {selectedPrompt ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">{selectedPrompt.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedPrompt.description}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(!isEditing)}
                  >
                    {isEditing ? 'View' : 'Edit'}
                  </Button>
                  {isEditing && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleResetToDefault}
                    >
                      <RotateCcw className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>

              {isEditing ? (
                <div className="space-y-3">
                  <Textarea
                    value={editingPrompt}
                    onChange={(e) => setEditingPrompt(e.target.value)}
                    className="min-h-[400px] font-mono text-sm"
                    placeholder="Enter your system prompt..."
                  />
                  <div className="flex items-center space-x-2">
                    <Button onClick={handleSaveEdit} disabled={isSaving}>
                      <Save className="h-4 w-4 mr-2" />
                      {isSaving ? 'Saving...' : 'Save Changes'}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setEditingPrompt(selectedPrompt.prompt);
                        setIsEditing(false);
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="bg-muted/30 rounded-lg p-4">
                  <pre className="whitespace-pre-wrap text-sm font-mono">
                    {selectedPrompt.prompt}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <FileAudio className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Select a system prompt to view and edit</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};