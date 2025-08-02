# CompactChatInterface Component

A compact, space-efficient chat interface component designed for audio editing applications with a fixed height of 400px, virtual scrolling for performance, and integrated command suggestions.

## Features

- **Fixed Height**: Maintains a consistent 400px total height
- **Virtual Scrolling**: Uses react-window for efficient rendering of large message lists
- **Performance Optimized**: Limits visible messages to 10 for optimal performance
- **Command Suggestions**: Built-in quick commands for audio editing tasks
- **Real-time Typing**: Shows typing indicators during bot responses
- **Responsive Design**: Adapts to different screen sizes while maintaining fixed height

## Usage

```tsx
import { CompactChatInterface } from './components/chat/compact-chat-interface';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

function MyComponent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = (message: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text: message,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleCommandSelect = (command: string) => {
    console.log('Command selected:', command);
  };

  return (
    <CompactChatInterface
      messages={messages}
      onSendMessage={handleSendMessage}
      onCommandSelect={handleCommandSelect}
      height={400}
      maxMessages={10}
      showSuggestions={true}
      autoScroll={true}
      isTyping={isTyping}
    />
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `messages` | `Message[]` | `[]` | Array of chat messages |
| `onSendMessage` | `(message: string) => void` | Optional | Callback when user sends a message |
| `onCommandSelect` | `(command: string) => void` | Optional | Callback when user selects a command |
| `height` | `number` | `400` | Total component height in pixels |
| `maxMessages` | `number` | `10` | Maximum messages to display for performance |
| `showSuggestions` | `boolean` | `true` | Whether to show command suggestions |
| `autoScroll` | `boolean` | `true` | Auto-scroll to bottom on new messages |
| `isTyping` | `boolean` | `false` | Show typing indicator |
| `disabled` | `boolean` | `false` | Disable input and interactions |

## Message Interface

```typescript
interface Message {
  id: string;           // Unique message identifier
  text: string;         // Message content
  sender: 'user' | 'bot'; // Message sender type
  timestamp: Date;      // When the message was sent
}
```

## Layout Structure

The component is divided into three main sections:

### 1. Chat Messages Area (~260px - 65%)
- Virtual scrolling message list
- User and bot message bubbles
- Typing indicator
- Empty state when no messages

### 2. Input Area (60px - Fixed)
- Text input with auto-resize
- Send button
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)

### 3. Command Suggestions Area (~80px - 20%)
- Quick command buttons
- Expandable/collapsible suggestions
- Audio editing specific commands

## Built-in Commands

The component includes predefined audio editing commands:

- **Volume**: "Increase volume by 20%", "Normalize audio levels"
- **Cleanup**: "Remove background noise"
- **Editing**: "Cut first 30 seconds", "Extract 1:00 to 2:30"
- **Effects**: "Add fade in effect"

## Performance Optimizations

### Virtual Scrolling
- Uses `react-window` for efficient rendering
- Only renders visible messages
- Smooth scrolling performance with large message lists

### Message Limiting
- Displays only the most recent `maxMessages` (default: 10)
- Older messages are kept in memory but not rendered
- Reduces DOM nodes and improves performance

### Memoization
- Message components are memoized to prevent unnecessary re-renders
- Callbacks are optimized with `useCallback`
- Expensive computations are memoized with `useMemo`

## Accessibility

- Keyboard navigation support
- Screen reader friendly with proper ARIA labels
- Focus management for input and buttons
- High contrast support through theme colors
- Semantic HTML structure

## Responsive Design

- Adapts message bubble sizes on smaller screens
- Adjusts font sizes for mobile devices
- Maintains fixed height across all screen sizes
- Touch-friendly interface on mobile

## States

### Empty State
- Shows welcome message and instructions
- Displays chat icon
- Encourages user to start conversation

### Loading/Typing State
- Animated typing indicator
- Shows when bot is responding
- Maintains chat flow continuity

### Error State
- Graceful error handling
- User-friendly error messages
- Recovery options when possible

## Integration with Layout System

This component is designed to work within the UI layout optimization system:

- Fits within the 560px column width of the right column
- Maintains consistent spacing with other components
- Integrates with the overall design system
- Supports the compact layout requirements

## Styling

The component uses CSS modules for styling:

```css
.compact-chat-interface {
  height: 400px;
  overflow: hidden;
}

.chat-messages {
  height: 260px; /* ~65% */
}

.input-area {
  height: 60px; /* Fixed */
}

.suggestions-area {
  height: 80px; /* ~20% */
}
```

## Event Handling

### Message Sending
- Enter key sends message
- Shift+Enter adds new line
- Send button click
- Input validation and trimming

### Command Selection
- Click on suggestion buttons
- Automatic message sending
- Command execution callback

### Scrolling
- Auto-scroll to bottom on new messages
- Manual scroll detection
- Scroll-to-bottom button when needed

## Testing

The component includes comprehensive tests covering:
- Rendering in different states
- Message display and formatting
- User interactions (typing, sending, commands)
- Performance optimizations
- Accessibility features
- Virtual scrolling behavior

Run tests with:
```bash
npm test compact-chat-interface.test.tsx
```

## Performance Monitoring

In development mode, the component can display performance metrics:
- Message count
- Render times
- Memory usage
- Virtual scrolling efficiency

## Related Components

- `ChatInterface`: Full-featured chat interface
- `MessageList`: Message display component
- `VirtualMessageList`: Virtual scrolling message list
- `InputArea`: Chat input component
- `CommandSuggestions`: Audio command suggestions

## Technical Dependencies

- `react-window`: Virtual scrolling
- `lucide-react`: Icon library
- `@/components/ui/*`: UI component library
- React hooks for state management

## Browser Support

- Modern browsers with ES2018+ support
- Virtual scrolling requires modern JavaScript features
- Responsive design works on all screen sizes
- Touch events supported for mobile devices