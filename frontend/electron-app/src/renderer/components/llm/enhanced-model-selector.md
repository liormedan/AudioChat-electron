# Enhanced Model Selector Component

The Enhanced Model Selector is a comprehensive React component for selecting and managing AI language models with advanced features including real-time status indicators, performance metrics, smart recommendations, and quick-switch functionality.

## Features

### 🚀 Core Functionality
- **Real-time Status Indicators**: Live connection status and availability monitoring
- **Quick-Switch Mode**: Fast model switching during conversations
- **Performance Metrics Display**: Detailed response time, throughput, and reliability metrics
- **Smart Recommendations**: AI-powered model suggestions based on usage patterns
- **Trending Analysis**: Performance trend indicators showing improving/declining models

### 📊 Advanced Analytics
- **Performance History Tracking**: Monitors response time trends over time
- **Usage Statistics**: Tracks model usage patterns and popularity
- **Cost Analysis**: Real-time cost tracking and optimization suggestions
- **Reliability Metrics**: Success rates, uptime, and error rate monitoring

### 🎯 User Experience
- **Compact and Full Modes**: Flexible UI for different use cases
- **Auto-refresh**: Configurable real-time data updates
- **Advanced Filtering**: Filter by category, provider, tier, and performance
- **Smart Sorting**: Multiple sorting options including trending analysis

## Usage

### Basic Usage

```tsx
import { EnhancedModelSelector } from '@/components/llm/enhanced-model-selector';

function MyComponent() {
  const handleModelChange = (modelId: string) => {
    console.log('Selected model:', modelId);
  };

  return (
    <EnhancedModelSelector
      onModelChange={handleModelChange}
      showMetrics={true}
      showRecommendations={true}
    />
  );
}
```

### Compact Mode for Toolbars

```tsx
<EnhancedModelSelector
  compact
  enableQuickSwitch={true}
  onModelChange={handleModelChange}
  className="w-64"
/>
```

### Performance-Focused Configuration

```tsx
<EnhancedModelSelector
  showPerformanceDetails={true}
  showTrending={true}
  autoRefresh={true}
  refreshInterval={10000}
  enableSmartRecommendations={true}
  onModelChange={handleModelChange}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onModelChange` | `(modelId: string) => void` | `undefined` | Callback when model is changed |
| `showMetrics` | `boolean` | `true` | Show performance metrics |
| `showRecommendations` | `boolean` | `true` | Show smart recommendations |
| `compact` | `boolean` | `false` | Use compact dropdown mode |
| `className` | `string` | `''` | Additional CSS classes |
| `enableQuickSwitch` | `boolean` | `true` | Enable quick-switch functionality |
| `showPerformanceDetails` | `boolean` | `false` | Show detailed performance metrics |
| `autoRefresh` | `boolean` | `true` | Enable automatic data refresh |
| `refreshInterval` | `number` | `30000` | Refresh interval in milliseconds |
| `showTrending` | `boolean` | `true` | Show trending indicators |
| `enableSmartRecommendations` | `boolean` | `true` | Enable AI-powered recommendations |

## Data Interfaces

### LLMModel

```tsx
interface LLMModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  maxTokens: number;
  costPerToken: number;
  capabilities: ModelCapability[];
  isActive: boolean;
  isAvailable: boolean;
  contextWindow: number;
  trainingDataCutoff: string | null;
  version: string | null;
  parameters: Record<string, any>;
  metadata: Record<string, any>;
  metrics: ModelMetrics;
  tier: 'free' | 'premium' | 'enterprise';
  category: 'chat' | 'code' | 'creative' | 'analysis';
}
```

### ModelMetrics

```tsx
interface ModelMetrics {
  responseTime: number;          // Average response time in ms
  tokensPerSecond: number;       // Token generation speed
  successRate: number;           // Success rate percentage
  totalRequests: number;         // Total number of requests
  averageCost: number;          // Average cost per request
  lastUsed: string;             // Last usage timestamp
  uptime: number;               // Uptime percentage
  throughput: number;           // Requests per minute
  errorRate: number;            // Error rate percentage
  avgTokensPerRequest: number;  // Average tokens per request
}
```

### ModelRecommendation

```tsx
interface ModelRecommendation {
  modelId: string;
  reason: string;
  score: number;
  category: 'performance' | 'cost' | 'capability' | 'reliability' | 'trending';
  icon: React.ReactNode;
}
```

## API Endpoints

The component expects the following API endpoints to be available:

### GET /api/llm/models
Returns array of available models with their configurations and metrics.

### GET /api/llm/active-model
Returns the currently active model.

### POST /api/llm/active-model
Sets the active model. Expects `{ model_id: string }` in request body.

### GET /api/llm/model-metrics
Returns real-time metrics for all models.

### GET /api/llm/connection-status
Returns connection status for each model.

### GET /api/llm/usage-stats
Returns usage statistics and historical data.

## Features in Detail

### Real-time Status Indicators

The component shows live status indicators for each model:
- 🟢 **Connected**: Model is available and responding
- 🟡 **Connecting**: Model is being initialized
- 🔴 **Disconnected**: Model is unavailable

### Smart Recommendations

The recommendation engine analyzes multiple factors:
- **Performance Champion**: Fastest response time
- **Cost Optimizer**: Most cost-effective option
- **Reliability Champion**: Highest success rate
- **Popular Choice**: Most frequently used
- **Trending Up**: Improving performance over time
- **Smart Match**: Best fit for current usage pattern

### Quick Switch Functionality

Quick switch provides instant access to:
- Fastest available model
- Most reliable model
- Most popular model
- Context-appropriate alternatives

### Performance Trending

Trending indicators show:
- 📈 **Improving**: Performance getting better over time
- 📉 **Declining**: Performance degrading over time
- ➡️ **Stable**: Consistent performance

### Advanced Filtering and Sorting

Filter options:
- **Category**: chat, code, creative, analysis
- **Provider**: OpenAI, Anthropic, Google, etc.
- **Tier**: free, premium, enterprise
- **Availability**: available, unavailable

Sort options:
- **Usage**: Most frequently used first
- **Performance**: Fastest response time first
- **Cost**: Most cost-effective first
- **Name**: Alphabetical order
- **Trending**: Best improving performance first

## Styling and Theming

The component uses Tailwind CSS and follows the design system:

- **Light/Dark Mode**: Automatically adapts to theme
- **Color Coding**: Performance-based color indicators
- **Responsive Design**: Works on mobile and desktop
- **RTL Support**: Supports right-to-left languages

### Custom Styling

```tsx
<EnhancedModelSelector
  className="custom-model-selector"
  // Custom styles will be applied to the root container
/>
```

## Performance Considerations

- **Debounced Updates**: Metrics updates are debounced to prevent excessive API calls
- **Efficient Rendering**: Uses React.memo and useMemo for optimal performance
- **Lazy Loading**: Advanced features load only when needed
- **Caching**: Intelligent caching of model data and metrics

## Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels and semantic HTML
- **Focus Management**: Clear focus indicators
- **High Contrast**: Works with high contrast modes

## Error Handling

The component gracefully handles:
- **Network Errors**: Shows fallback UI when API is unavailable
- **Invalid Data**: Validates and sanitizes API responses
- **Model Switching Errors**: Provides user feedback on failures
- **Connection Issues**: Shows appropriate status indicators

## Testing

Comprehensive test coverage includes:
- **Unit Tests**: Individual component functionality
- **Integration Tests**: API interaction and data flow
- **Accessibility Tests**: Screen reader and keyboard navigation
- **Performance Tests**: Rendering and update performance

Run tests:
```bash
npm test enhanced-model-selector.test.tsx
```

## Browser Support

- **Modern Browsers**: Chrome 88+, Firefox 85+, Safari 14+, Edge 88+
- **Mobile**: iOS Safari 14+, Chrome Mobile 88+
- **Features**: ES2020, CSS Grid, Flexbox, Fetch API

## Migration from Basic Model Selector

The Enhanced Model Selector is backward compatible:

```tsx
// Old usage
<ModelSelector onModelChange={handleChange} />

// New usage (same interface)
<EnhancedModelSelector onModelChange={handleChange} />
```

Additional features can be enabled incrementally:

```tsx
// Add quick switch
<EnhancedModelSelector 
  onModelChange={handleChange}
  enableQuickSwitch={true}
/>

// Add performance details
<EnhancedModelSelector 
  onModelChange={handleChange}
  enableQuickSwitch={true}
  showPerformanceDetails={true}
/>
```

## Future Enhancements

Planned improvements:
- **Model Comparison**: Side-by-side model comparison
- **Custom Metrics**: User-defined performance metrics
- **Model Presets**: Saved model configurations
- **Usage Analytics**: Detailed usage reporting
- **A/B Testing**: Model performance comparison tools