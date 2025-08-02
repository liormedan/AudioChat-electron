# CompactFileUploader Component

A compact, space-efficient file uploader component designed for audio files with a fixed height of 200px and support for multiple files through tabs.

## Features

- **Fixed Height**: Maintains a consistent 200px height regardless of content
- **Drag & Drop**: Primary interaction method for file uploads
- **Multi-file Support**: Handles multiple files with tab-based navigation
- **Minimal UI**: Clean, compact design with essential visual indicators
- **Audio Focus**: Optimized for audio file formats (MP3, WAV, FLAC, OGG, M4A, AAC)
- **Responsive**: Adapts to different screen sizes

## Usage

```tsx
import { CompactFileUploader } from './components/audio/compact-file-uploader';

function MyComponent() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFileSelect = (file: File) => {
    setSelectedFiles(prev => [...prev, file]);
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleClearAll = () => {
    setSelectedFiles([]);
  };

  return (
    <CompactFileUploader
      onFileSelect={handleFileSelect}
      selectedFiles={selectedFiles}
      onRemoveFile={handleRemoveFile}
      onClearAll={handleClearAll}
      dragDropOnly={true}
      maxHeight={200}
    />
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onFileSelect` | `(file: File) => void` | Required | Callback when a file is selected |
| `selectedFiles` | `File[]` | Required | Array of currently selected files |
| `onRemoveFile` | `(index: number) => void` | Required | Callback to remove a file by index |
| `onClearAll` | `() => void` | Required | Callback to clear all files |
| `accept` | `Record<string, string[]>` | Audio formats | File types to accept |
| `maxSize` | `number` | 100MB | Maximum file size in bytes |
| `dragDropOnly` | `boolean` | `true` | Whether to show only drag & drop (no browse button) |
| `maxHeight` | `number` | `200` | Fixed height of the component in pixels |

## States

### Empty State
- Shows drag & drop area with audio icon
- Displays supported file formats
- Optional browse button (when `dragDropOnly` is false)

### Files Selected State
- Tab-based navigation for multiple files
- File information display (name, size)
- Individual file removal buttons
- "Clear All" button
- Additional files can be added via drag & drop on the "+" tab

## Design Specifications

- **Height**: Fixed at 200px (configurable via `maxHeight` prop)
- **Layout**: Card-based with minimal padding
- **Tabs**: Compact tabs with file icons and truncated names
- **Colors**: Uses theme colors with muted backgrounds
- **Icons**: Lucide React icons (Music, FileAudio, X, Plus)

## Accessibility

- Keyboard navigation support through tab system
- Screen reader friendly with proper ARIA labels
- High contrast support through theme colors
- Focus indicators on interactive elements

## Performance Considerations

- Efficient file handling without unnecessary re-renders
- Truncated file names to prevent layout overflow
- Minimal DOM updates when switching between tabs
- Optimized for handling multiple files without performance degradation

## Error Handling

- File size validation with user-friendly messages
- File type validation
- Drag & drop error states with visual feedback
- Graceful handling of upload failures

## Responsive Behavior

- Tab names truncate on smaller screens
- Maintains fixed height across all screen sizes
- Touch-friendly on mobile devices
- Horizontal scrolling for many tabs

## Integration with Layout System

This component is designed to work within the UI layout optimization system:

- Fits within the 560px column width
- Maintains consistent spacing with other components
- Integrates with the overall design system
- Supports the compact layout requirements

## Testing

The component includes comprehensive tests covering:
- Rendering in different states
- User interactions (file selection, removal)
- Error handling
- Accessibility features
- Responsive behavior

Run tests with:
```bash
npm test compact-file-uploader.test.tsx
```

## Related Components

- `FileUploader`: Original full-featured file uploader
- `FileDropZone`: Simple drag & drop zone
- `AudioFileManager`: File management component