# API Key Management Component

The API Key Management component is a comprehensive React component for securely managing API keys across multiple AI providers with connection testing, usage monitoring, and provider status tracking.

## Features

### 🔐 Secure Key Management
- **Masked Input Fields**: API keys are masked by default with show/hide functionality
- **Secure Storage**: Keys are securely stored and transmitted
- **Copy to Clipboard**: One-click copying with visual feedback
- **Key Validation**: Format validation for different providers
- **Access Control**: Enable/disable keys without deletion

### 🔌 Connection Testing
- **Real-time Testing**: Test API key validity with live connections
- **Visual Feedback**: Clear status indicators (active, invalid, testing, expired)
- **Automatic Testing**: Test new keys immediately after addition
- **Error Reporting**: Detailed error messages for failed connections
- **Response Time Monitoring**: Track connection performance

### 📊 Provider Status Dashboard
- **Multi-Provider Support**: OpenAI, Anthropic, Google AI, Cohere
- **Connection Status**: Real-time provider availability
- **Model Availability**: List of accessible models per provider
- **Rate Limits**: Display current rate limiting information
- **Performance Metrics**: Response times and uptime tracking

### 📈 Usage Statistics
- **Request Tracking**: Monitor API requests per provider
- **Token Usage**: Track token consumption and costs
- **Cost Analysis**: Detailed cost breakdown and trends
- **Usage Alerts**: Notifications for usage limits
- **Historical Data**: Usage trends over time

## Usage

### Basic Usage

```tsx
import { APIKeyManagement } from '@/components/settings/api-key-management';

function SettingsPage() {
  return (
    <div className="container mx-auto p-6">
      <h1>API Configuration</h1>
      <APIKeyManagement />
    </div>
  );
}
```

### Embedded in Settings

```tsx
import { APIKeyManagement } from '@/components/settings/api-key-management';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

function SettingsPage() {
  return (
    <Tabs defaultValue="api-keys">
      <TabsList>
        <TabsTrigger value="general">General</TabsTrigger>
        <TabsTrigger value="api-keys">API Keys</TabsTrigger>
        <TabsTrigger value="security">Security</TabsTrigger>
      </TabsList>
      
      <TabsContent value="api-keys">
        <APIKeyManagement />
      </TabsContent>
    </Tabs>
  );
}
```

### Custom Styling

```tsx
<APIKeyManagement className="max-w-4xl mx-auto" />
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | `string` | `''` | Additional CSS classes for styling |

## Data Interfaces

### APIProvider

```tsx
interface APIProvider {
  id: string;                    // Unique provider identifier
  name: string;                  // Internal name
  displayName: string;           // Display name for UI
  description: string;           // Provider description
  website: string;              // Provider website URL
  icon: React.ReactNode;        // Provider icon
  supportedModels: string[];    // List of supported models
  requiresApiKey: boolean;      // Whether API key is required
  keyFormat: string;            // Expected key format
  keyExample: string;           // Example key format
  testEndpoint: string;         // Endpoint for testing connection
  documentationUrl: string;     // Documentation URL
  pricingUrl: string;          // Pricing information URL
}
```

### APIKey

```tsx
interface APIKey {
  id: string;                   // Unique key identifier
  providerId: string;           // Associated provider ID
  name: string;                 // User-defined key name
  key: string;                  // The actual API key
  isActive: boolean;            // Whether key is active
  createdAt: string;           // Creation timestamp
  lastUsed?: string;           // Last usage timestamp
  lastTested?: string;         // Last test timestamp
  status: 'active' | 'inactive' | 'invalid' | 'expired' | 'testing';
  usage?: {                    // Usage statistics
    totalRequests: number;
    totalTokens: number;
    totalCost: number;
    lastMonth: {
      requests: number;
      tokens: number;
      cost: number;
    };
  };
  limits?: {                   // Usage limits
    dailyRequests?: number;
    monthlyTokens?: number;
    monthlyCost?: number;
  };
}
```

### ProviderStatus

```tsx
interface ProviderStatus {
  providerId: string;           // Provider identifier
  isConnected: boolean;         // Connection status
  lastChecked: string;         // Last check timestamp
  responseTime: number;        // Response time in ms
  errorMessage?: string;       // Error message if any
  availableModels: string[];   // Currently available models
  rateLimits: {               // Current rate limits
    requestsPerMinute: number;
    tokensPerMinute: number;
    requestsPerDay: number;
  };
}
```

### UsageStatistics

```tsx
interface UsageStatistics {
  providerId: string;          // Provider identifier
  period: 'day' | 'week' | 'month';  // Statistics period
  data: Array<{               // Time series data
    date: string;
    requests: number;
    tokens: number;
    cost: number;
    errors: number;
  }>;
  totals: {                   // Aggregate totals
    requests: number;
    tokens: number;
    cost: number;
    errors: number;
  };
}
```

## Supported Providers

### OpenAI
- **Models**: GPT-4, GPT-3.5 Turbo, GPT-4 Turbo
- **Key Format**: `sk-...`
- **Features**: Chat completion, embeddings, image generation
- **Documentation**: https://platform.openai.com/docs

### Anthropic
- **Models**: Claude 3 Opus, Claude 3 Sonnet, Claude 2
- **Key Format**: `sk-ant-...`
- **Features**: Advanced reasoning, long context
- **Documentation**: https://docs.anthropic.com

### Google AI
- **Models**: Gemini Pro, Gemini Pro Vision
- **Key Format**: `AIza...`
- **Features**: Multimodal capabilities, large context
- **Documentation**: https://ai.google.dev/docs

### Cohere
- **Models**: Command, Command Light
- **Key Format**: `co-...`
- **Features**: Text generation, embeddings
- **Documentation**: https://docs.cohere.ai

## API Endpoints

The component expects the following API endpoints to be available:

### GET /api/settings/api-keys
Returns array of stored API keys.

### POST /api/settings/api-keys
Creates a new API key entry.

### PATCH /api/settings/api-keys/{keyId}
Updates an existing API key.

### DELETE /api/settings/api-keys/{keyId}
Deletes an API key.

### GET /api/providers/status
Returns current status of all providers.

### GET /api/providers/usage-stats
Returns usage statistics for all providers.

### POST /api/test/{providerId}
Tests connection for a specific provider.

## Security Features

### Key Protection
- **Masked Display**: Keys are masked by default
- **Secure Transmission**: HTTPS-only communication
- **Access Control**: Role-based key management
- **Audit Logging**: Track key usage and changes

### Input Validation
- **Format Validation**: Validate key formats per provider
- **Length Validation**: Ensure appropriate key lengths
- **Character Validation**: Check for valid characters
- **Duplicate Prevention**: Prevent duplicate key entries

### Error Handling
- **Graceful Degradation**: Continue working with partial failures
- **User Feedback**: Clear error messages and recovery suggestions
- **Retry Logic**: Automatic retry for transient failures
- **Fallback Options**: Alternative providers when primary fails

## User Interface

### Key Management Tab
- **Provider Grouping**: Keys organized by provider
- **Status Indicators**: Visual status for each key
- **Quick Actions**: Test, edit, delete, enable/disable
- **Bulk Operations**: Manage multiple keys at once

### Provider Status Tab
- **Connection Status**: Real-time provider availability
- **Performance Metrics**: Response times and uptime
- **Model Availability**: List of accessible models
- **Rate Limits**: Current usage limits and quotas

### Usage Statistics Tab
- **Usage Graphs**: Visual representation of usage trends
- **Cost Tracking**: Detailed cost breakdown
- **Usage Alerts**: Notifications for approaching limits
- **Export Options**: Download usage reports

## Accessibility

### Keyboard Navigation
- **Tab Navigation**: Full keyboard accessibility
- **Arrow Keys**: Navigate between elements
- **Enter/Space**: Activate buttons and controls
- **Escape**: Close dialogs and menus

### Screen Reader Support
- **ARIA Labels**: Comprehensive labeling
- **Semantic HTML**: Proper HTML structure
- **Live Regions**: Dynamic content announcements
- **Focus Management**: Logical focus flow

### Visual Accessibility
- **High Contrast**: Support for high contrast modes
- **Color Independence**: Information not dependent on color alone
- **Font Scaling**: Respects user font size preferences
- **Focus Indicators**: Clear focus visualization

## Performance

### Optimization Strategies
- **Lazy Loading**: Load data only when needed
- **Debounced Updates**: Prevent excessive API calls
- **Caching**: Cache provider status and usage data
- **Virtual Scrolling**: Handle large numbers of keys efficiently

### Memory Management
- **Cleanup**: Proper cleanup of intervals and listeners
- **Efficient Rendering**: Minimize re-renders
- **Data Structures**: Optimized data organization
- **Garbage Collection**: Prevent memory leaks

## Testing

### Test Coverage
- **Unit Tests**: Individual component functionality
- **Integration Tests**: API interaction testing
- **Accessibility Tests**: Screen reader and keyboard testing
- **Security Tests**: Key handling and validation

### Test Utilities
```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { APIKeyManagement } from '../api-key-management';

test('adds new API key', async () => {
  render(<APIKeyManagement />);
  
  // Open add dialog
  fireEvent.click(screen.getByText('הוסף מפתח'));
  
  // Fill form
  fireEvent.change(screen.getByDisplayValue('בחר ספק'), {
    target: { value: 'openai' }
  });
  
  fireEvent.change(screen.getByPlaceholderText('למשל: Production Key'), {
    target: { value: 'Test Key' }
  });
  
  fireEvent.change(screen.getByPlaceholderText('sk-1234567890abcdef...'), {
    target: { value: 'sk-test1234567890abcdef' }
  });
  
  // Submit
  fireEvent.click(screen.getByRole('button', { name: 'הוסף מפתח' }));
  
  await waitFor(() => {
    expect(screen.getByText('Test Key')).toBeInTheDocument();
  });
});
```

## Browser Support

- **Modern Browsers**: Chrome 88+, Firefox 85+, Safari 14+, Edge 88+
- **Mobile**: iOS Safari 14+, Chrome Mobile 88+
- **Features**: ES2020, CSS Grid, Flexbox, Fetch API

## Troubleshooting

### Common Issues

#### Keys Not Saving
- Check API endpoint availability
- Verify request format and headers
- Check browser console for errors

#### Connection Tests Failing
- Verify API key format
- Check provider service status
- Ensure network connectivity

#### Usage Statistics Not Loading
- Check API endpoint permissions
- Verify data format from backend
- Check for CORS issues

### Debug Mode
Enable debug logging by setting:
```javascript
localStorage.setItem('api-key-debug', 'true');
```

## Migration Guide

### From Manual Key Management
```tsx
// Old approach
const [apiKey, setApiKey] = useState('');
const [isVisible, setIsVisible] = useState(false);

// New approach
<APIKeyManagement />
```

### Adding Custom Providers
```tsx
// Extend SUPPORTED_PROVIDERS array
const customProvider: APIProvider = {
  id: 'custom-provider',
  name: 'custom',
  displayName: 'Custom Provider',
  // ... other properties
};
```

## Future Enhancements

Planned improvements:
- **Team Management**: Shared key management for teams
- **Key Rotation**: Automatic key rotation and expiration
- **Advanced Analytics**: More detailed usage analytics
- **Compliance Features**: SOC2, GDPR compliance tools
- **Integration APIs**: Programmatic key management