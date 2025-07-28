import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Slider } from '../ui/slider';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { 
  Settings, 
  Brain, 
  Zap, 
  Target, 
  Palette,
  Save,
  RotateCcw,
  Info
} from 'lucide-react';

interface ModelSettings {
  temperature: number;
  maxTokens: number;
  topP: number;
  frequencyPenalty: number;
  presencePenalty: number;
  systemPromptMode: 'precision' | 'balanced' | 'creative';
  enableAudioContext: boolean;
  enableTechnicalDetails: boolean;
  enableSafetyChecks: boolean;
  responseFormat: 'concise' | 'detailed' | 'step-by-step';
}

interface ModelProfile {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  settings: ModelSettings;
  useCase: string;
}

const defaultProfiles: ModelProfile[] = [
  {
    id: 'precision',
    name: 'Precision Mode',
    description: 'Focused on technical accuracy and professional audio editing',
    icon: <Target className="h-5 w-5" />,
    useCase: 'Professional audio editing, mastering, technical analysis',
    settings: {
      temperature: 0.2,
      maxTokens: 1000,
      topP: 0.8,
      frequencyPenalty: 0.1,
      presencePenalty: 0.1,
      systemPromptMode: 'precision',
      enableAudioContext: true,
      enableTechnicalDetails: true,
      enableSafetyChecks: true,
      responseFormat: 'detailed'
    }
  },
  {
    id: 'balanced',
    name: 'Balanced Mode',
    description: 'Good balance between creativity and technical accuracy',
    icon: <Settings className="h-5 w-5" />,
    useCase: 'General audio editing, podcast production, content creation',
    settings: {
      temperature: 0.5,
      maxTokens: 800,
      topP: 0.9,
      frequencyPenalty: 0.2,
      presencePenalty: 0.2,
      systemPromptMode: 'balanced',
      enableAudioContext: true,
      enableTechnicalDetails: false,
      enableSafetyChecks: true,
      responseFormat: 'concise'
    }
  },
  {
    id: 'creative',
    name: 'Creative Mode',
    description: 'Encourages creative and experimental audio processing',
    icon: <Palette className="h-5 w-5" />,
    useCase: 'Sound design, artistic audio, experimental processing',
    settings: {
      temperature: 0.8,
      maxTokens: 1200,
      topP: 0.95,
      frequencyPenalty: 0.3,
      presencePenalty: 0.3,
      systemPromptMode: 'creative',
      enableAudioContext: true,
      enableTechnicalDetails: false,
      enableSafetyChecks: false,
      responseFormat: 'step-by-step'
    }
  }
];

export const AudioModelSettings: React.FC = () => {
  const [currentSettings, setCurrentSettings] = useState<ModelSettings>(defaultProfiles[1].settings);
  const [selectedProfile, setSelectedProfile] = useState<string>('balanced');
  const [isCustom, setIsCustom] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadSavedSettings();
  }, []);

  const loadSavedSettings = () => {
    try {
      const saved = localStorage.getItem('audio-model-settings');
      if (saved) {
        const savedSettings = JSON.parse(saved);
        setCurrentSettings(savedSettings.settings);
        setSelectedProfile(savedSettings.profile);
        setIsCustom(savedSettings.isCustom || false);
      }
    } catch (error) {
      console.error('Error loading saved settings:', error);
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);
    try {
      const settingsData = {
        settings: currentSettings,
        profile: selectedProfile,
        isCustom
      };
      
      localStorage.setItem('audio-model-settings', JSON.stringify(settingsData));
      
      // Also save to server if API is available
      await fetch('http://127.0.0.1:5000/api/llm/model-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentSettings),
      });
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleProfileSelect = (profileId: string) => {
    const profile = defaultProfiles.find(p => p.id === profileId);
    if (profile) {
      setCurrentSettings(profile.settings);
      setSelectedProfile(profileId);
      setIsCustom(false);
    }
  };

  const handleSettingChange = (key: keyof ModelSettings, value: any) => {
    setCurrentSettings(prev => ({ ...prev, [key]: value }));
    setIsCustom(true);
    setSelectedProfile('custom');
  };

  const resetToDefault = () => {
    const defaultProfile = defaultProfiles[1]; // Balanced mode
    setCurrentSettings(defaultProfile.settings);
    setSelectedProfile(defaultProfile.id);
    setIsCustom(false);
  };

  const getTemperatureDescription = (temp: number) => {
    if (temp <= 0.3) return 'Very focused and deterministic';
    if (temp <= 0.5) return 'Balanced creativity and consistency';
    if (temp <= 0.7) return 'More creative and varied responses';
    return 'Highly creative and experimental';
  };

  const getResponseFormatDescription = (format: string) => {
    switch (format) {
      case 'concise': return 'Brief, to-the-point responses';
      case 'detailed': return 'Comprehensive explanations with technical details';
      case 'step-by-step': return 'Clear step-by-step instructions';
      default: return '';
    }
  };

  return (
    <div className="space-y-6">
      {/* Profile Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Audio Editing Profiles</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {defaultProfiles.map((profile) => (
              <div
                key={profile.id}
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedProfile === profile.id && !isCustom
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:bg-muted/50'
                }`}
                onClick={() => handleProfileSelect(profile.id)}
              >
                <div className="flex items-center space-x-2 mb-2">
                  {profile.icon}
                  <span className="font-medium">{profile.name}</span>
                  {selectedProfile === profile.id && !isCustom && (
                    <Badge variant="default" className="text-xs">Active</Badge>
                  )}
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  {profile.description}
                </p>
                <p className="text-xs text-muted-foreground">
                  <strong>Best for:</strong> {profile.useCase}
                </p>
              </div>
            ))}
            
            {/* Custom Profile */}
            {isCustom && (
              <div className="p-4 rounded-lg border border-primary bg-primary/5">
                <div className="flex items-center space-x-2 mb-2">
                  <Settings className="h-5 w-5" />
                  <span className="font-medium">Custom Settings</span>
                  <Badge variant="default" className="text-xs">Active</Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  Customized model settings based on your preferences
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Settings */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Core Parameters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5" />
              <span>Core Parameters</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Temperature */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Temperature</label>
                <span className="text-sm text-muted-foreground">
                  {currentSettings.temperature}
                </span>
              </div>
              <Slider
                value={[currentSettings.temperature]}
                onValueChange={(value) => handleSettingChange('temperature', value[0])}
                max={1}
                min={0}
                step={0.1}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                {getTemperatureDescription(currentSettings.temperature)}
              </p>
            </div>

            {/* Max Tokens */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Max Tokens</label>
                <span className="text-sm text-muted-foreground">
                  {currentSettings.maxTokens}
                </span>
              </div>
              <Slider
                value={[currentSettings.maxTokens]}
                onValueChange={(value) => handleSettingChange('maxTokens', value[0])}
                max={2000}
                min={100}
                step={50}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Maximum length of AI responses
              </p>
            </div>

            {/* Top P */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Top P</label>
                <span className="text-sm text-muted-foreground">
                  {currentSettings.topP}
                </span>
              </div>
              <Slider
                value={[currentSettings.topP]}
                onValueChange={(value) => handleSettingChange('topP', value[0])}
                max={1}
                min={0.1}
                step={0.05}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Controls diversity of word selection
              </p>
            </div>

            {/* Frequency Penalty */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Frequency Penalty</label>
                <span className="text-sm text-muted-foreground">
                  {currentSettings.frequencyPenalty}
                </span>
              </div>
              <Slider
                value={[currentSettings.frequencyPenalty]}
                onValueChange={(value) => handleSettingChange('frequencyPenalty', value[0])}
                max={1}
                min={0}
                step={0.1}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Reduces repetition of frequent words
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Audio-Specific Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>Audio-Specific Settings</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Response Format */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Response Format</label>
              <div className="grid grid-cols-1 gap-2">
                {[
                  { value: 'concise', label: 'Concise' },
                  { value: 'detailed', label: 'Detailed' },
                  { value: 'step-by-step', label: 'Step-by-step' }
                ].map((option) => (
                  <div
                    key={option.value}
                    className={`p-2 rounded border cursor-pointer transition-colors ${
                      currentSettings.responseFormat === option.value
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:bg-muted/50'
                    }`}
                    onClick={() => handleSettingChange('responseFormat', option.value)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{option.label}</span>
                      {currentSettings.responseFormat === option.value && (
                        <Badge variant="default" className="text-xs">Selected</Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {getResponseFormatDescription(option.value)}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Toggle Settings */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Audio Context Awareness</label>
                  <p className="text-xs text-muted-foreground">
                    Include audio file information in responses
                  </p>
                </div>
                <Switch
                  checked={currentSettings.enableAudioContext}
                  onCheckedChange={(checked) => handleSettingChange('enableAudioContext', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Technical Details</label>
                  <p className="text-xs text-muted-foreground">
                    Include technical parameters and measurements
                  </p>
                </div>
                <Switch
                  checked={currentSettings.enableTechnicalDetails}
                  onCheckedChange={(checked) => handleSettingChange('enableTechnicalDetails', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <label className="text-sm font-medium">Safety Checks</label>
                  <p className="text-xs text-muted-foreground">
                    Warn about potentially destructive operations
                  </p>
                </div>
                <Switch
                  checked={currentSettings.enableSafetyChecks}
                  onCheckedChange={(checked) => handleSettingChange('enableSafetyChecks', checked)}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Info className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                Settings are automatically applied to new conversations
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" onClick={resetToDefault}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset to Default
              </Button>
              <Button onClick={saveSettings} disabled={isSaving}>
                <Save className="h-4 w-4 mr-2" />
                {isSaving ? 'Saving...' : 'Save Settings'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};