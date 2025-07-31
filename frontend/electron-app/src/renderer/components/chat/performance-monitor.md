# Performance Monitor Component

The Performance Monitor is a comprehensive React component for real-time monitoring of AI model performance, including response times, token usage, cost tracking, reliability metrics, and intelligent alerting system.

## Features

### 📊 Real-time Performance Metrics
- **Response Time Tracking**: Current, average, min/max response times with historical data
- **Token Usage Monitoring**: Input/output tokens, tokens per second, efficiency metrics
- **Cost Analysis**: Real-time cost tracking with trends and projections
- **Reliability Metrics**: Success rates, error rates, uptime monitoring
- **Resource Usage**: CPU, memory, throughput, and concurrency tracking

### 🚨 Intelligent Alerting System
- **Configurable Thresholds**: Custom alert thresholds for different metrics
- **Real-time Notifications**: Instant alerts for performance anomalies
- **Alert Acknowledgment**: Mark alerts as acknowledged with tracking
- **Alert History**: Complete history of all alerts and responses
- **Smart Filtering**: Filter alerts by type, model, and severity

### 📈 Performance Comparison
- **Multi-Model Comparison**: Side-by-side comparison of multiple models
- **Smart Recommendations**: AI-powered recommendations for optimal model selection
- **Benchmark Analysis**: Performance benchmarking across different metrics
- **Trend Analysis**: Historical performance trends and predictions
- **Cost-Benefit Analysis**: ROI analysis for different model choices

### 🎛️ Flexible Display Modes
- **Overview Mode**: High-level dashboard with key metrics
- **Detailed Mode**: Comprehensive metrics with expandable cards
- **Comparison Mode**: Side-by-side model comparison
- **Compact Mode**: Minimal view for sidebars and dashboards

## Usage

### Basic Usage

```tsx
import { PerformanceMonitor } from '@/components/chat/performance-monitor';

function Dashboard() {
  const handleModelSelect = (modelId: string) => {
    console.log('Selected model:', modelId);
  };

  const handleAlertAcknowledge = (alertId: string) => {
    console.log('Acknowledged alert:', alertId);
  };

  return (
    <PerformanceMonitor
      onModelSelect={handleModelSelect}
      onAlertAcknowledge={handleAlertAcknowledge}
      showAlerts={true}
      enableComparison={true}
      autoRefresh={true}
    />
  );
}
```

### Compact Mode for Sidebars

```tsx
<PerformanceMonitor
  compactMode
  onModelSelect={handleModelSelect}
  showAlerts={false}
  enableComparison={false}
  autoRefresh={true}
  refreshInterval={60000}
/>
```

### Dashboard Integration

```tsx
<div className="grid grid-cols-4 gap-6">
  <div className="col-span-3">
    <PerformanceMonitor
      selectedModels={['gpt-4', 'claude-3']}
      showAlerts={true}
      enableComparison={true}
      autoRefresh={true}
      refreshInterval={30000}
    />
  </div>
  <div>
    {/* Sidebar controls */}
  </div>
</div>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | `string` | `''` | Additional CSS classes |
| `autoRefresh` | `boolean` | `true` | Enable automatic data refresh |
| `refreshInterval` | `number` | `30000` | Refresh interval in milliseconds |
| `showAlerts` | `boolean` | `true` | Show alerts panel |
| `enableComparison` | `boolean` | `true` | Enable model comparison features |
| `compactMode` | `boolean` | `false` | Use compact display mode |
| `selectedModels` | `string[]` | `[]` | Models to monitor/compare |
| `onModelSelect` | `(modelId: string) => void` | `undefined` | Model selection callback |
| `onAlertAcknowledge` | `(alertId: string) => void` | `undefined` | Alert acknowledgment callback |

## Data Interfaces

### ModelMetrics

```tsx
interface ModelMetrics {
  modelId: string;
  modelName: string;
  provider: string;
  responseTime: {
    current: number;
    average: number;
    min: number;
    max: number;
    history: Array<{ timestamp: string; value: number }>;
  };
  tokenUsage: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
    tokensPerSecond: number;
    efficiency: number;
  };
  costMetrics: {
    totalCost: number;
    costPerToken: number;
    costPerRequest: number;
    dailyCost: number;
    monthlyCost: number;
    costTrend: 'up' | 'down' | 'stable';
  };
  reliability: {
    successRate: number;
    errorRate: number;
    uptime: number;
    lastError?: string;
    errorHistory: Array<{ timestamp: string; error: string }>;
  };
  performance: {
    throughput: number;
    concurrency: number;
    queueLength: number;
    memoryUsage: number;
    cpuUsage: number;
  };
  usage: {
    totalRequests: number;
    requestsPerHour: number;
    requestsPerDay: number;
    activeUsers: number;
    popularityScore: number;
  };
  lastUpdated: string;
}
```

### PerformanceAlert

```tsx
interface PerformanceAlert {
  id: string;
  type: 'warning' | 'error' | 'info' | 'success';
  title: string;
  message: string;
  modelId: string;
  threshold: number;
  currentValue: number;
  timestamp: string;
  isActive: boolean;
  acknowledged: boolean;
}
```

### ComparisonData

```tsx
interface ComparisonData {
  models: string[];
  metrics: {
    responseTime: Record<string, number>;
    cost: Record<string, number>;
    reliability: Record<string, number>;
    efficiency: Record<string, number>;
  };
  recommendations: Array<{
    type: 'fastest' | 'cheapest' | 'most_reliable' | 'most_efficient';
    modelId: string;
    reason: string;
    score: number;
  }>;
}
```

## API Endpoints

The component expects the following API endpoints:

### GET /api/performance/metrics
Returns performance metrics for all models.

**Query Parameters:**
- `timeRange`: '1h' | '6h' | '24h' | '7d' | '30d'

**Response:**
```json
{
  "gpt-4": {
    "modelId": "gpt-4",
    "modelName": "GPT-4",
    "provider": "OpenAI",
    "responseTime": { ... },
    "tokenUsage": { ... },
    "costMetrics": { ... },
    "reliability": { ... },
    "performance": { ... },
    "usage": { ... },
    "lastUpdated": "2024-01-01T12:00:00Z"
  }
}
```

### GET /api/performance/alerts
Returns active performance alerts.

**Response:**
```json
[
  {
    "id": "alert-1",
    "type": "warning",
    "title": "High Response Time",
    "message": "Response time exceeded threshold",
    "modelId": "gpt-4",
    "threshold": 1000,
    "currentValue": 1200,
    "timestamp": "2024-01-01T12:00:00Z",
    "isActive": true,
    "acknowledged": false
  }
]
```

### POST /api/performance/alerts/{alertId}/acknowledge
Acknowledges a specific alert.

### GET /api/performance/alert-thresholds
Returns configured alert thresholds.

### POST /api/performance/comparison
Returns comparison data for selected models.

**Request Body:**
```json
{
  "models": ["gpt-4", "gpt-3.5-turbo"],
  "timeRange": "24h"
}
```

## Display Modes

### Overview Mode
- High-level dashboard with key metrics
- Expandable cards for detailed information
- Quick access to model selection
- Alert notifications panel

### Detailed Mode
- Comprehensive metrics display
- Historical data visualization
- Performance trends and analysis
- Resource usage monitoring

### Comparison Mode
- Side-by-side model comparison
- Smart recommendations
- Benchmark analysis
- Cost-benefit comparison

### Compact Mode
- Minimal space usage
- Essential metrics only
- Quick status indicators
- Suitable for sidebars

## Metrics Explained

### Response Time Metrics
- **Current**: Latest response time measurement
- **Average**: Mean response time over selected period
- **Min/Max**: Fastest and slowest response times
- **History**: Time series data for trend analysis

### Token Usage Metrics
- **Input Tokens**: Tokens in user prompts
- **Output Tokens**: Tokens in model responses
- **Total Tokens**: Sum of input and output tokens
- **Tokens Per Second**: Generation speed
- **Efficiency**: Token utilization efficiency

### Cost Metrics
- **Total Cost**: Cumulative cost for the period
- **Cost Per Token**: Average cost per token
- **Cost Per Request**: Average cost per API request
- **Daily/Monthly Cost**: Cost projections
- **Cost Trend**: Cost trend direction

### Reliability Metrics
- **Success Rate**: Percentage of successful requests
- **Error Rate**: Percentage of failed requests
- **Uptime**: Service availability percentage
- **Error History**: Recent error occurrences

### Performance Metrics
- **Throughput**: Requests processed per minute
- **Concurrency**: Simultaneous request handling
- **Queue Length**: Pending requests count
- **Memory/CPU Usage**: Resource utilization

## Alert System

### Alert Types
- **Error**: Critical issues requiring immediate attention
- **Warning**: Performance degradation or threshold breaches
- **Info**: General information and status updates
- **Success**: Performance improvements or issue resolutions

### Alert Thresholds
Configure custom thresholds for:
- Response time limits
- Error rate thresholds
- Cost budgets
- Token usage limits
- Resource utilization limits

### Alert Management
- **Real-time Notifications**: Instant alert delivery
- **Acknowledgment System**: Mark alerts as reviewed
- **Alert History**: Complete audit trail
- **Filtering Options**: Filter by type, model, severity
- **Bulk Operations**: Manage multiple alerts

## Performance Optimization

### Efficient Data Loading
- **Lazy Loading**: Load data only when needed
- **Caching**: Cache frequently accessed data
- **Debounced Updates**: Prevent excessive API calls
- **Incremental Updates**: Update only changed data

### Memory Management
- **Data Cleanup**: Remove old historical data
- **Efficient Rendering**: Minimize re-renders
- **Virtual Scrolling**: Handle large datasets
- **Resource Cleanup**: Proper cleanup on unmount

### Network Optimization
- **Request Batching**: Combine multiple requests
- **Compression**: Compress API responses
- **CDN Usage**: Cache static resources
- **Connection Pooling**: Reuse HTTP connections

## Accessibility

### Keyboard Navigation
- **Tab Navigation**: Navigate between elements
- **Arrow Keys**: Navigate within components
- **Enter/Space**: Activate controls
- **Escape**: Close dialogs and menus

### Screen Reader Support
- **ARIA Labels**: Comprehensive labeling
- **Semantic HTML**: Proper HTML structure
- **Live Regions**: Dynamic content announcements
- **Focus Management**: Logical focus flow

### Visual Accessibility
- **Color Coding**: Performance-based color indicators
- **High Contrast**: Support for high contrast modes
- **Font Scaling**: Respects user font preferences
- **Focus Indicators**: Clear focus visualization

## Browser Support

- **Modern Browsers**: Chrome 88+, Firefox 85+, Safari 14+, Edge 88+
- **Mobile**: iOS Safari 14+, Chrome Mobile 88+
- **Features**: ES2020, CSS Grid, Flexbox, WebSocket

## Troubleshooting

### Common Issues

#### Metrics Not Loading
- Check API endpoint availability
- Verify authentication tokens
- Check network connectivity
- Review browser console for errors

#### Alerts Not Showing
- Verify alert thresholds configuration
- Check alert service status
- Ensure WebSocket connection
- Review alert filtering settings

#### Performance Issues
- Reduce refresh frequency
- Limit number of monitored models
- Enable data compression
- Use compact mode for better performance

### Debug Mode
Enable debug logging:
```javascript
localStorage.setItem('performance-monitor-debug', 'true');
```

## Migration Guide

### From Basic Monitoring
```tsx
// Old approach
const [metrics, setMetrics] = useState({});
useEffect(() => {
  fetchMetrics().then(setMetrics);
}, []);

// New approach
<PerformanceMonitor onModelSelect={handleSelect} />
```

### Adding Custom Metrics
```tsx
// Extend ModelMetrics interface
interface CustomModelMetrics extends ModelMetrics {
  customMetric: number;
}

// Use with custom data
<PerformanceMonitor
  customMetricsLoader={loadCustomMetrics}
  onModelSelect={handleSelect}
/>
```

## Future Enhancements

Planned improvements:
- **Machine Learning Insights**: AI-powered performance predictions
- **Custom Dashboards**: User-configurable dashboard layouts
- **Advanced Analytics**: Statistical analysis and forecasting
- **Integration APIs**: Third-party monitoring tool integration
- **Mobile App**: Dedicated mobile monitoring application