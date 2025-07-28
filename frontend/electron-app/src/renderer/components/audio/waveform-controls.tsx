import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { 
  Settings, 
  Scissors, 
  BarChart3,
  Radio
} from 'lucide-react';

interface WaveformControlsProps {
  showSpectrogram: boolean;
  onSpectrogramToggle: (show: boolean) => void;
  enableRegions: boolean;
  onRegionsToggle: (enable: boolean) => void;
  waveformHeight: number;
  onHeightChange: (height: number) => void;
  waveColor: string;
  onWaveColorChange: (color: string) => void;
  progressColor: string;
  onProgressColorChange: (color: string) => void;
}

export const WaveformControls: React.FC<WaveformControlsProps> = ({
  showSpectrogram,
  onSpectrogramToggle,
  enableRegions,
  onRegionsToggle,
  waveformHeight,
  onHeightChange,
  waveColor,
  onWaveColorChange,
  progressColor,
  onProgressColorChange
}) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Settings className="h-5 w-5" />
          <span>Waveform Settings</span>
        </CardTitle>
        <CardDescription>
          Customize the waveform display and controls
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Display Options */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Display Options</h4>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <Label htmlFor="spectrogram">Show Spectrogram</Label>
            </div>
            <Switch
              id="spectrogram"
              checked={showSpectrogram}
              onCheckedChange={onSpectrogramToggle}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Scissors className="h-4 w-4" />
              <Label htmlFor="regions">Enable Regions</Label>
            </div>
            <Switch
              id="regions"
              checked={enableRegions}
              onCheckedChange={onRegionsToggle}
            />
          </div>
        </div>

        {/* Waveform Height */}
        <div className="space-y-2">
          <Label>Waveform Height: {waveformHeight}px</Label>
          <Slider
            value={[waveformHeight]}
            onValueChange={(value) => onHeightChange(value[0] || 80)}
            min={60}
            max={200}
            step={10}
            className="w-full"
          />
        </div>

        {/* Color Controls */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Colors</h4>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="wave-color">Wave Color</Label>
              <div className="flex items-center space-x-2">
                <input
                  id="wave-color"
                  type="color"
                  value={waveColor}
                  onChange={(e) => onWaveColorChange(e.target.value)}
                  className="w-8 h-8 rounded border"
                />
                <span className="text-xs text-muted-foreground">{waveColor}</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="progress-color">Progress Color</Label>
              <div className="flex items-center space-x-2">
                <input
                  id="progress-color"
                  type="color"
                  value={progressColor}
                  onChange={(e) => onProgressColorChange(e.target.value)}
                  className="w-8 h-8 rounded border"
                />
                <span className="text-xs text-muted-foreground">{progressColor}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Presets */}
        <div className="space-y-2">
          <Label>Quick Presets</Label>
          <div className="grid grid-cols-2 gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                onWaveColorChange('#6b7280');
                onProgressColorChange('#3b82f6');
              }}
            >
              Default
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                onWaveColorChange('#10b981');
                onProgressColorChange('#059669');
              }}
            >
              Green
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                onWaveColorChange('#f59e0b');
                onProgressColorChange('#d97706');
              }}
            >
              Orange
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                onWaveColorChange('#8b5cf6');
                onProgressColorChange('#7c3aed');
              }}
            >
              Purple
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};