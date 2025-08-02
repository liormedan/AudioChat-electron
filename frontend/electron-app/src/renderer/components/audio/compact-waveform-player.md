# CompactWaveformPlayer Component

A compact, space-efficient waveform player component designed for audio playback with a fixed height of 300px and optimized layout for the UI optimization project.

## Features

- **Fixed Height**: Maintains a consistent 300px total height
- **Compact Waveform**: 120px height waveform visualization using WaveSurfer.js
- **Minimal Controls**: Essential playback controls (play/pause, stop, volume)
- **File Information**: Displays file name, size, duration, and format
- **No Spectrogram**: Spectrogram is disabled in compact mode for space efficiency
- **Responsive**: Adapts to different screen sizes while maintaining fixed height

## Usage

```tsx
import { CompactWaveformPlayer } from './components/audio/compact-waveform-player';

function MyComponent() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const handleTimeUpdate = (currentTime: number, duration: number) => {
    console.log(`Time: ${currentTime}/${duration}`);
  };

  const handlePlayStateChange = (isPlaying: boolean) => {
    console.log(`Playing: ${isPlaying}`);
  };

  return (
    <CompactWaveformPlayer
      audioFile={audioFile}
      audioUrl={audioUrl}
      onTimeUpdate={handleTimeUpdate}
      onPlayStateChange={handlePlayStateChange}
      height={300}
      waveformHeight={120}
      controlsHeight={60}
      infoHeight={120}
    />
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `audioFile` | `File \| null` | Required | The audio file object for display info |
| `audioUrl` | `string \| null` | Required | URL or blob URL for audio playback |
| `onTimeUpdate` | `(currentTime: number, duration: number) => void` | Optional | Callback for time updates |
| `onPlayStateChange` | `(isPlaying: boolean) => void` | Optional | Callback for play state changes |
| `height` | `number` | `300` | Total component height in pixels |
| `waveformHeight` | `number` | `120` | Waveform visualization height |
| `controlsHeight` | `number` | `60` | Controls section height |
| `infoHeight` | `number` | `120` | File info section height |
| `showSpectrogram` | `boolean` | `false` | Always false in compact mode |
| `waveColor` | `string` | `'#6b7280'` | Waveform color |
| `progressColor` | `string` | `'#3b82f6'` | Progress/cursor color |

## Layout Structure

The component is divided into three main sections:

### 1. File Info Section (120px)
- File name with truncation for long names
- File size, duration, and format
- Progress bar with time indicators
- Empty state when no file is selected

### 2. Waveform Section (120px)
- WaveSurfer.js visualization
- Responsive waveform bars
- Loading state with spinner
- Empty state placeholder

### 3. Controls Section (60px)
- Play/pause button
- Stop button
- Volume slider with percentage
- Status indicator

## Design Specifications

- **Total Height**: Fixed at 300px (configurable)
- **Layout**: Vertical stack with fixed section heights
- **Colors**: Uses theme colors for consistency
- **Icons**: Lucide React icons (Play, Pause, Square, Volume2, FileAudio)
- **Typography**: Consistent with design system

## States

### Empty State
- Shows placeholder content in all sections
- All controls are disabled
- Displays "No audio file selected" message

### Loading State
- Shows loading spinner overlay on waveform
- Controls remain enabled but show loading status
- File info displays available information

### Ready State
- Waveform is fully loaded and interactive
- All controls are functional
- Complete file information is displayed

### Playing State
- Waveform shows real-time progress
- Play button changes to pause
- Progress bar updates continuously

## Accessibility

- Keyboard navigation support
- Screen reader friendly with proper ARIA labels
- High contrast support through theme colors
- Focus indicators on interactive elements
- Descriptive button titles and labels

## Performance Considerations

- Efficient WaveSurfer.js configuration for compact display
- Minimal DOM updates during playback
- Optimized for 120px waveform height
- Responsive design without layout shifts
- Proper cleanup of audio resources

## Error Handling

- Graceful handling of WaveSurfer initialization failures
- Audio loading error states
- File format validation
- Fallback displays for missing data

## Integration with Layout System

This component is designed to work within the UI layout optimization system:

- Fits within the 560px column width of the middle column
- Maintains consistent spacing with other components
- Integrates with the overall design system
- Supports the compact layout requirements

## Differences from Full WaveformPlayer

| Feature | Full Player | Compact Player |
|---------|-------------|----------------|
| Height | Variable | Fixed 300px |
| Waveform | 80px+ | 120px |
| Spectrogram | Optional | Disabled |
| Region Selection | Yes | No |
| Zoom Controls | Yes | No |
| Playback Speed | Yes | No |
| Skip Controls | Yes | No |
| Advanced Features | Yes | Minimal |

## Testing

The component includes comprehensive tests covering:
- Rendering in different states
- Height and layout constraints
- User interactions
- File information display
- Error handling
- Accessibility features

Run tests with:
```bash
npm test compact-waveform-player.test.tsx
```

## Related Components

- `WaveformPlayer`: Full-featured waveform player
- `SimpleWaveformPlayer`: Canvas-based simple player
- `CompactFileUploader`: Compact file upload component
- `AudioFileInfo`: File information display component

## Technical Dependencies

- `wavesurfer.js`: Waveform visualization library
- `lucide-react`: Icon library
- `@/components/ui/*`: UI component library
- React hooks for state management