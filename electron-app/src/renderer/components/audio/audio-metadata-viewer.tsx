import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Loader2, BarChart3, Waveform, Music, Brain, Zap, Clock } from 'lucide-react';
import { AudioMetadataService, type ComprehensiveMetadata, type AudioSummary, type WaveformData } from '../../services/audio-metadata-service';

interface AudioMetadataViewerProps {
  fileId: string | null;
  fileName?: string;
}

export const AudioMetadataViewer: React.FC<AudioMetadataViewerProps> = ({ fileId, fileName }) => {
  const [metadata, setMetadata] = useState<ComprehensiveMetadata | null>(null);
  const [summary, setSummary] = useState<AudioSummary | null>(null);
  const [waveformData, setWaveformData] = useState<WaveformData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  const [includeAdvanced, setIncludeAdvanced] = useState(false);

  const metadataService = new AudioMetadataService();

  useEffect(() => {
    if (fileId) {
      loadMetadata();
    }
  }, [fileId, includeAdvanced]);

  const loadMetadata = async () => {
    if (!fileId) return;

    setIsLoading(true);
    try {
      // Load summary (fast)
      const summaryResult = await metadataService.getAudioSummary(fileId);
      setSummary(summaryResult);

      // Load comprehensive metadata
      const metadataResult = await metadataService.getAdvancedMetadata(fileId, includeAdvanced);
      setMetadata(metadataResult);

      // Load waveform data for visualization
      const waveformResult = await metadataService.getWaveformData(fileId, 500);
      setWaveformData(waveformResult);

    } catch (error) {
      console.error('Error loading metadata:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderSummary = () => {
    if (!summary || !summary.success) {
      return <div className="text-muted-foreground">No summary available</div>;
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Duration</span>
            <Badge variant="secondary">{summary.duration}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Sample Rate</span>
            <Badge variant="secondary">{summary.sample_rate}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">File Size</span>
            <Badge variant="secondary">{summary.file_size}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Tempo</span>
            <Badge variant="secondary">{summary.tempo}</Badge>
          </div>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Brightness</span>
            <Badge variant={getBrightnessVariant(summary.brightness)}>{summary.brightness}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Energy Level</span>
            <Badge variant={getEnergyVariant(summary.energy_level)}>{summary.energy_level}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Dynamic Range</span>
            <Badge variant={getDynamicRangeVariant(summary.dynamic_range)}>{summary.dynamic_range}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Onset Density</span>
            <Badge variant="secondary">{summary.onset_density}</Badge>
          </div>
        </div>
      </div>
    );
  };

  const renderDetailedMetadata = () => {
    if (!metadata || !metadata.success) {
      return <div className="text-muted-foreground">No detailed metadata available</div>;
    }

    const formatted = metadataService.formatMetadataForDisplay(metadata);

    return (
      <div className="space-y-6">
        {Object.entries(formatted).map(([section, data]) => (
          <Card key={section}>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                {getSectionIcon(section)}
                <span>{section}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(data as Record<string, any>).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{key}</span>
                    <span className="text-sm text-muted-foreground font-mono">{value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  const renderWaveform = () => {
    if (!waveformData || !waveformData.success) {
      return <div className="text-muted-foreground">No waveform data available</div>;
    }

    // Simple ASCII-style waveform visualization
    const maxValue = Math.max(...waveformData.waveform.map(Math.abs));
    const normalizedWaveform = waveformData.waveform.map(v => v / maxValue);

    return (
      <div className="space-y-4">
        <div className="text-sm text-muted-foreground">
          Waveform visualization ({waveformData.downsampled_samples} points from {waveformData.original_samples.toLocaleString()} samples)
        </div>
        <div className="bg-muted/20 p-4 rounded-lg overflow-x-auto">
          <div className="flex items-center h-32 space-x-1" style={{ minWidth: `${normalizedWaveform.length * 2}px` }}>
            {normalizedWaveform.map((value, index) => (
              <div
                key={index}
                className="bg-primary"
                style={{
                  width: '2px',
                  height: `${Math.abs(value) * 100}%`,
                  opacity: 0.7
                }}
              />
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium">Duration:</span> {waveformData.duration.toFixed(2)}s
          </div>
          <div>
            <span className="font-medium">Sample Rate:</span> {waveformData.sample_rate} Hz
          </div>
          <div>
            <span className="font-medium">Original Samples:</span> {waveformData.original_samples.toLocaleString()}
          </div>
          <div>
            <span className="font-medium">Visualization Points:</span> {waveformData.downsampled_samples}
          </div>
        </div>
      </div>
    );
  };

  const getBrightnessVariant = (brightness: string) => {
    switch (brightness.toLowerCase()) {
      case 'dark': return 'secondary';
      case 'warm': return 'secondary';
      case 'balanced': return 'default';
      case 'bright': return 'default';
      case 'very bright': return 'destructive';
      default: return 'secondary';
    }
  };

  const getEnergyVariant = (energy: string) => {
    switch (energy.toLowerCase()) {
      case 'very low': return 'secondary';
      case 'low': return 'secondary';
      case 'medium': return 'default';
      case 'high': return 'default';
      case 'very high': return 'destructive';
      default: return 'secondary';
    }
  };

  const getDynamicRangeVariant = (range: string) => {
    switch (range.toLowerCase()) {
      case 'compressed': return 'destructive';
      case 'limited': return 'secondary';
      case 'good': return 'default';
      case 'wide': return 'default';
      default: return 'secondary';
    }
  };

  const getSectionIcon = (section: string) => {
    switch (section.toLowerCase()) {
      case 'file information': return <BarChart3 className="h-4 w-4" />;
      case 'audio properties': return <Waveform className="h-4 w-4" />;
      case 'spectral analysis': return <Zap className="h-4 w-4" />;
      case 'temporal analysis': return <Clock className="h-4 w-4" />;
      case 'advanced features': return <Brain className="h-4 w-4" />;
      case 'harmonic analysis': return <Music className="h-4 w-4" />;
      case 'rhythm analysis': return <Music className="h-4 w-4" />;
      default: return <BarChart3 className="h-4 w-4" />;
    }
  };

  if (!fileId) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-32">
          <div className="text-center text-muted-foreground">
            <BarChart3 className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Select an audio file to view metadata</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Audio Metadata</span>
            </CardTitle>
            <CardDescription>
              {fileName ? `Analysis for ${fileName}` : 'Detailed audio analysis'}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIncludeAdvanced(!includeAdvanced)}
              disabled={isLoading}
            >
              {includeAdvanced ? 'Basic' : 'Advanced'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={loadMetadata}
              disabled={isLoading}
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Refresh'}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
              <p className="text-muted-foreground">
                {includeAdvanced ? 'Analyzing audio (this may take a moment)...' : 'Loading metadata...'}
              </p>
            </div>
          </div>
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="detailed">Detailed</TabsTrigger>
              <TabsTrigger value="waveform">Waveform</TabsTrigger>
            </TabsList>
            <TabsContent value="summary" className="mt-4">
              {renderSummary()}
            </TabsContent>
            <TabsContent value="detailed" className="mt-4">
              {renderDetailedMetadata()}
            </TabsContent>
            <TabsContent value="waveform" className="mt-4">
              {renderWaveform()}
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
};