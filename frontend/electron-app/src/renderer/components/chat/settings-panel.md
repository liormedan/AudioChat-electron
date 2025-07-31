# Advanced Settings Panel Component

The Advanced Settings Panel is a comprehensive React component for configuring AI model parameters with built-in presets, custom profiles, real-time preview, and advanced parameter management.

## Features

### 🎛️ Core Functionality
- **Interactive Sliders**: Visual parameter adjustment with real-time feedback
- **Built-in Presets**: Creative, Balanced, Precise, and Code presets
- **Custom Profiles**: Save and load parameter configurations
- **Real-time Preview**: Live preview of parameter effects
- **Advanced Parameters**: Extended parameter set for fine-tuning

### 📊 Parameter Management
- **Parameter Validation**: Automatic constraint enforcement
- **Visual Feedback**: Color-coded parameter values
- **Copy to Clipboard**: Quick parameter value copying
- **Import/Export**: Settings backup and sharing
- **Parameter History**: Track parameter changes

### 🎨 User Experience
- **Responsive Design**: Works on mobile and desktop
- **RTL Support**: Hebrew/Arabic text direction
- **Accessibility**: Full keyboard navigation and screen reader support
- **Progressive Disclosure**: Advanced features hidden by default

## Usage

### Basic Usage

```tsx
import { AdvancedSettingsPanel } from '@/components/chat/settings-panel';

function MyComponent() {
  const handleParametersChange = (parameters) => {
    console.log('Parameters updated:', parameters);
    // Apply parameters to your AI model
  };

  return (
    <AdvancedSettingsPanel
      onParametersChange={handleParametersChange}
      initialParameters={{
        temperature: 0.7,
        max_tokens: 2048,
        top_p: 0.9
      }}
    />
  );
}
```

### With Real-time Preview

```tsx
<AdvancedSettingsPanel
  onParametersChange={handleParametersChange}
  modelId="gpt-4"
  showPreview={true}
  enableProfiles={true}
/>
```

### Minimal Configuration

```tsx
<AdvancedSettingsPanel
  onParametersChange={handleParametersChange}
  showPreview={false}
  enableProfiles={false}
  enableAdvancedParams={false}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onParametersChange` | `(parameters: ModelParameters) => void` | `undefined` | Callback when parameters change |
| `initialParameters` | `ModelParameters` | `DEFAULT_PARAMETERS` | Initial parameter values |
| `modelId` | `string` | `undefined` | Model ID for preview generation |
| `className` | `string` | `''` | Additional CSS classes |
| `showPreview` | `boolean` | `true` | Enable real-time preview |
| `enableProfiles` | `boolean` | `true` | Enable profile save/load |
| `enableAdvancedParams` | `boolean` | `true` | Show advanced parameters |

## Data Interfaces

### ModelParameters

```tsx
interface ModelParameters {
  temperature: number;           // Creativity and randomness (0-2)
  max_tokens: number;           // Maximum response length (1-8192)
  top_p: number;               // Nucleus sampling (0-1)
  top_k?: number;              // Top-k sampling (1-200)
  frequency_penalty?: number;   // Reduce word repetition (-2 to 2)
  presence_penalty?: number;    // Encourage new topics (-2 to 2)
  repetition_penalty?: number;  // Overall repetition reduction (0.5-2)
  stop_sequences?: string[];    // Stop generation sequences
  seed?: number;               // Deterministic generation seed
}
```

### ParameterPreset

```tsx
interface ParameterPreset {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  parameters: ModelParameters;
  category: 'built-in' | 'custom';
  createdAt?: string;
  usageCount?: number;
}
```

### ParameterProfile

```tsx
interface ParameterProfile {
  id: string;
  name: string;
  description: string;
  parameters: ModelParameters;
  createdAt: string;
  updatedAt: string;
  isDefault: boolean;
  tags: string[];
}
```

## Built-in Presets

### Creative
- **Temperature**: 0.9 (High creativity)
- **Top P**: 0.95 (Wide vocabulary)
- **Max Tokens**: 2048
- **Use Case**: Creative writing, brainstorming, artistic content

### Balanced
- **Temperature**: 0.7 (Moderate creativity)
- **Top P**: 0.9 (Balanced vocabulary)
- **Max Tokens**: 2048
- **Use Case**: General conversation, balanced responses

### Precise
- **Temperature**: 0.3 (Low creativity)
- **Top P**: 0.8 (Focused vocabulary)
- **Max Tokens**: 1024
- **Use Case**: Factual answers, precise information

### Code
- **Temperature**: 0.2 (Very low creativity)
- **Top P**: 0.85 (Technical vocabulary)
- **Max Tokens**: 4096
- **Stop Sequences**: ['```', '---']
- **Use Case**: Code generation, technical documentation

## Parameter Details

### Core Parameters

#### Temperature (0-2)
Controls randomness and creativity in responses.
- **0.0-0.3**: Very focused, deterministic
- **0.4-0.7**: Balanced creativity
- **0.8-1.2**: Creative and varied
- **1.3-2.0**: Highly creative, potentially chaotic

#### Max Tokens (1-8192)
Maximum number of tokens in the response.
- **256-512**: Short responses
- **1024-2048**: Medium responses
- **4096-8192**: Long-form content

#### Top P (0-1)
Nucleus sampling - controls vocabulary diversity.
- **0.1-0.5**: Very focused vocabulary
- **0.6-0.9**: Balanced vocabulary
- **0.9-1.0**: Full vocabulary range

### Advanced Parameters

#### Top K (1-200)
Limits selection to top K most likely tokens.
- **1-20**: Very focused
- **21-50**: Moderate focus
- **51-200**: Diverse selection

#### Frequency Penalty (-2 to 2)
Reduces repetition of frequent words.
- **Negative**: Encourage repetition
- **0**: No penalty
- **Positive**: Discourage repetition

#### Presence Penalty (-2 to 2)
Encourages discussion of new topics.
- **Negative**: Stay on topic
- **0**: No penalty
- **Positive**: Explore new topics

#### Repetition Penalty (0.5-2)
Overall repetition reduction.
- **< 1.0**: Allow repetition
- **1.0**: No penalty
- **> 1.0**: Discourage repetition

## Real-time Preview

The preview feature generates sample responses using current parameters:

### Preview API Endpoint
```
POST /api/llm/preview
{
  "model_id": "gpt-4",
  "parameters": { ... },
  "prompt": "Sample prompt for testing"
}
```

### Preview Metrics
- **Creativity**: Measured novelty and originality
- **Coherence**: Logical flow and consistency
- **Relevance**: Alignment with prompt

### Preview Quality Indicators
- 🟢 **Excellent**: High-quality response
- 🟡 **Good**: Acceptable quality
- 🟠 **Fair**: Needs improvement
- 🔴 **Poor**: Low quality

## Profile Management

### Saving Profiles
1. Adjust parameters to desired values
2. Click "שמור" (Save) button
3. Enter profile name and description
4. Profile saved to localStorage

### Loading Profiles
1. Click "טען" (Load) button
2. Select from saved profiles
3. Parameters automatically applied

### Profile Storage
Profiles are stored in localStorage:
- **Key**: `chat-parameter-profiles`
- **Format**: JSON array of ParameterProfile objects

## Custom Presets

### Creating Custom Presets
1. Configure desired parameters
2. Click "צור פריסט" (Create Preset)
3. Enter preset name and description
4. Preset added to preset list

### Preset Storage
Custom presets are stored in localStorage:
- **Key**: `chat-custom-presets`
- **Format**: JSON array of ParameterPreset objects

## Import/Export

### Export Settings
Exports complete configuration including:
- Current parameters
- Saved profiles
- Custom presets
- Export timestamp

### Import Settings
Imports configuration from JSON file:
- Validates data structure
- Merges with existing settings
- Updates localStorage

### Export Format
```json
{
  "parameters": { ... },
  "profiles": [ ... ],
  "customPresets": [ ... ],
  "exportedAt": "2024-01-01T10:00:00Z"
}
```

## Styling and Theming

### CSS Classes
- `.advanced-settings-panel`: Root container
- Parameter-specific classes for custom styling

### Color Coding
- **Blue**: Conservative values
- **Green**: Balanced values
- **Orange**: Aggressive values

### Responsive Breakpoints
- **Mobile**: Single column layout
- **Tablet**: Two column layout
- **Desktop**: Multi-column layout

## Accessibility

### Keyboard Navigation
- **Tab**: Navigate between controls
- **Arrow Keys**: Adjust slider values
- **Enter/Space**: Activate buttons
- **Escape**: Close dialogs

### Screen Reader Support
- ARIA labels for all controls
- Semantic HTML structure
- Live regions for dynamic updates

### High Contrast Mode
- Sufficient color contrast ratios
- Focus indicators
- Alternative text for icons

## Performance Considerations

### Debounced Updates
- Parameter changes debounced (300ms)
- Preview generation debounced (1000ms)
- Prevents excessive API calls

### Efficient Rendering
- React.memo for expensive components
- useMemo for computed values
- useCallback for event handlers

### Memory Management
- Cleanup intervals on unmount
- Limited history storage
- Efficient localStorage usage

## Error Handling

### Parameter Validation
- Automatic constraint enforcement
- Visual feedback for invalid values
- Graceful fallback to defaults

### API Error Handling
- Network error recovery
- Timeout handling
- User-friendly error messages

### Storage Error Handling
- localStorage availability check
- Graceful degradation
- Error logging

## Testing

### Test Coverage
- Unit tests for all components
- Integration tests for API calls
- Accessibility tests
- Performance tests

### Test Utilities
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { AdvancedSettingsPanel } from '../settings-panel';

test('applies preset correctly', async () => {
  const onParametersChange = jest.fn();
  render(<AdvancedSettingsPanel onParametersChange={onParametersChange} />);
  
  fireEvent.click(screen.getByText('Creative'));
  
  expect(onParametersChange).toHaveBeenCalledWith(
    expect.objectContaining({
      temperature: 0.9,
      top_p: 0.95
    })
  );
});
```

## Browser Support

- **Modern Browsers**: Chrome 88+, Firefox 85+, Safari 14+, Edge 88+
- **Mobile**: iOS Safari 14+, Chrome Mobile 88+
- **Features**: ES2020, CSS Grid, Flexbox, localStorage

## Migration Guide

### From Basic Parameter Controls
```tsx
// Old approach
<input 
  type="range" 
  min="0" 
  max="2" 
  step="0.1"
  value={temperature}
  onChange={(e) => setTemperature(parseFloat(e.target.value))}
/>

// New approach
<AdvancedSettingsPanel
  onParametersChange={(params) => setTemperature(params.temperature)}
  initialParameters={{ temperature }}
/>
```

### Adding Advanced Features
```tsx
// Start simple
<AdvancedSettingsPanel onParametersChange={handleChange} />

// Add features incrementally
<AdvancedSettingsPanel 
  onParametersChange={handleChange}
  showPreview={true}
  enableProfiles={true}
/>
```

## Future Enhancements

Planned improvements:
- **Parameter Templates**: Industry-specific templates
- **A/B Testing**: Compare parameter sets
- **Usage Analytics**: Parameter effectiveness tracking
- **Cloud Sync**: Cross-device profile synchronization
- **Collaborative Profiles**: Team parameter sharing