# SearchPanel Component

The SearchPanel component provides comprehensive search functionality for chat messages with advanced filtering, highlighting, and search management features.

## Features

### 🔍 Core Search Functionality
- **Real-time search**: Search results update as you type with 300ms debouncing
- **Text highlighting**: Search terms are highlighted in results with yellow background
- **Message content search**: Searches through all message text content
- **Session title search**: Also searches session titles for broader results

### 🎯 Advanced Filtering
- **Date range filtering**: Filter results by specific date ranges
- **Sender filtering**: Filter by user messages, bot messages, or both
- **Session filtering**: Limit search to specific chat sessions
- **Regex support**: Toggle regex mode for advanced pattern matching

### 💾 Search Management
- **Search history**: Automatically saves last 10 searches to localStorage
- **Saved searches**: Save frequently used searches with custom names
- **Quick access**: Easily reload previous searches from history or saved searches

### 🎨 User Interface
- **Tabbed interface**: Organized tabs for Results, History, and Saved searches
- **Collapsible filters**: Advanced filters can be hidden/shown as needed
- **Responsive design**: Works well in different container sizes
- **RTL support**: Fully supports Hebrew/Arabic right-to-left text

## Usage

### Basic Usage

```tsx
import { SearchPanel } from '@/components/chat/search-panel';

function ChatInterface() {
  const handleResultSelect = (sessionId: string, messageId: string) => {
    // Navigate to the selected message
    console.log('Selected message:', messageId, 'in session:', sessionId);
  };

  return (
    <div className="w-96">
      <SearchPanel onResultSelect={handleResultSelect} />
    </div>
  );
}
```

### Advanced Integration

```tsx
import { SearchPanel } from '@/components/chat/search-panel';
import { useChatStore } from '@/stores/chat-store';

function ChatWithSearch() {
  const { setActiveSession } = useChatStore();
  const [highlightedMessage, setHighlightedMessage] = useState<string | null>(null);

  const handleSearchResultSelect = (sessionId: string, messageId: string) => {
    // Switch to the session
    setActiveSession(sessionId);
    
    // Highlight the message
    setHighlightedMessage(messageId);
    
    // Scroll to message
    setTimeout(() => {
      document.getElementById(`message-${messageId}`)?.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }, 100);
  };

  return (
    <div className="flex">
      <div className="flex-1">
        {/* Your chat interface */}
      </div>
      <div className="w-96 border-l">
        <SearchPanel onResultSelect={handleSearchResultSelect} />
      </div>
    </div>
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | `string` | `''` | Additional CSS classes for the container |
| `onResultSelect` | `(sessionId: string, messageId: string) => void` | `undefined` | Callback when a search result is clicked |

## Search Result Interface

```tsx
interface SearchResult {
  sessionId: string;           // ID of the session containing the message
  sessionTitle: string;        // Title of the session
  messageId: string;          // ID of the specific message
  messageText: string;        // Content of the message
  sender: 'user' | 'bot';     // Who sent the message
  timestamp: string;          // When the message was sent
  highlights: Array<{         // Highlighted text segments
    start: number;
    end: number;
    text: string;
  }>;
}
```

## Filter Options

```tsx
interface SearchFilter {
  dateFrom?: string;          // Start date (YYYY-MM-DD format)
  dateTo?: string;           // End date (YYYY-MM-DD format)
  sender?: 'user' | 'bot' | 'all';  // Filter by message sender
  sessionId?: string;        // Limit to specific session
}
```

## Local Storage

The component automatically manages two localStorage keys:

- `chat-search-history`: Array of recent search queries (max 10)
- `chat-saved-searches`: Array of saved search objects with names and filters

## Styling

The component uses Tailwind CSS classes and follows the design system established by the UI components. Key styling features:

- **Dark mode support**: Automatically adapts to dark/light themes
- **Hover effects**: Interactive elements have hover states
- **Focus management**: Proper keyboard navigation support
- **Responsive text**: Handles long text with ellipsis and wrapping

## Accessibility

- **Keyboard navigation**: All interactive elements are keyboard accessible
- **Screen reader support**: Proper ARIA labels and semantic HTML
- **Focus management**: Clear focus indicators and logical tab order
- **RTL support**: Works correctly with right-to-left languages

## Performance Considerations

- **Debounced search**: 300ms delay prevents excessive API calls
- **Virtual scrolling**: Results list handles large numbers of results efficiently
- **Memoized highlighting**: Text highlighting is optimized for performance
- **Lazy loading**: Advanced filters are only rendered when opened

## Error Handling

- **Invalid regex**: Falls back to plain text search if regex is invalid
- **Missing data**: Gracefully handles missing timestamps or session data
- **Storage errors**: Continues working even if localStorage is unavailable

## Testing

The component includes comprehensive tests covering:

- Basic search functionality
- Advanced filtering options
- Regex mode operation
- Search history management
- Saved searches functionality
- Error handling scenarios
- User interaction flows

Run tests with:
```bash
npm test search-panel.test.tsx
```

## Browser Support

- **Modern browsers**: Chrome 88+, Firefox 85+, Safari 14+, Edge 88+
- **Mobile browsers**: iOS Safari 14+, Chrome Mobile 88+
- **Features used**: ES2020, CSS Grid, Flexbox, localStorage

## Future Enhancements

Potential improvements for future versions:

- **Export results**: Allow exporting search results to CSV/JSON
- **Search operators**: Support for AND, OR, NOT operators
- **Fuzzy search**: Implement fuzzy matching for typo tolerance
- **Search analytics**: Track popular searches and terms
- **Keyboard shortcuts**: Add hotkeys for common operations
- **Search suggestions**: Auto-complete based on message content