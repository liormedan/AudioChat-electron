import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { ScrollArea } from '../ui/scroll-area';
import { Send, MessageCircle, Zap, ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';
import './compact-chat-interface.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface CompactChatInterfaceProps {
  messages?: Message[];
  onSendMessage?: (message: string) => void;
  onCommandSelect?: (command: string) => void;
  height?: number;
  maxMessages?: number;
  autoScroll?: boolean;
  showSuggestions?: boolean;
  isLoading?: boolean;
  placeholder?: string;
}

interface CommandSuggestion {
  text: string;
  description: string;
  category: string;
}

const defaultCommands: CommandSuggestion[] = [
  { text: "Increase volume by 20%", description: "Boost audio level", category: "Volume" },
  { text: "Remove background noise", description: "Clean audio", category: "Cleanup" },
  { text: "Cut the first 30 seconds", description: "Remove from start", category: "Editing" },
  { text: "Add fade in effect", description: "Smooth start", category: "Effects" },
  { text: "Normalize audio", description: "Balance levels", category: "Volume" },
  { text: "Extract from 1:00 to 2:30", description: "Get section", category: "Editing" }
];

// Message item component for virtual list
const MessageItem = React.memo<{
  index: number;
  style: React.CSSProperties;
  data: Message[];
}>(({ index, style, data }) => {
  const message = data[index];
  
  if (!message) return null;

  return (
    <div style={style} className="px-3 py-1">
      <div className={cn(
        "flex",
        message.sender === 'user' ? "justify-end" : "justify-start"
      )}>
        <div className={cn(
          "max-w-[80%] px-3 py-2 rounded-lg text-sm",
          message.sender === 'user' 
            ? "bg-primary text-primary-foreground" 
            : "bg-muted text-foreground"
        )}>
          <p className="whitespace-pre-wrap break-words">{message.text}</p>
          <div className="text-xs opacity-70 mt-1">
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
      </div>
    </div>
  );
});

MessageItem.displayName = 'MessageItem';

export const CompactChatInterface: React.FC<CompactChatInterfaceProps> = ({
  messages = [],
  onSendMessage,
  onCommandSelect,
  height = 400,
  maxMessages = 10,
  autoScroll = true,
  showSuggestions = true,
  isLoading = false,
  placeholder = "Type your message..."
}) => {
  const [inputValue, setInputValue] = useState('');
  const [showScrollButton, setShowScrollButton] = useState(false);
  const listRef = useRef<List>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Limit messages for performance
  const displayMessages = useMemo(() => {
    return messages.slice(-maxMessages);
  }, [messages, maxMessages]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScroll && displayMessages.length > 0) {
      listRef.current?.scrollToItem(displayMessages.length - 1, 'end');
    }
  }, [displayMessages.length, autoScroll]);

  // Handle scroll events
  const handleScroll = useCallback(({ scrollOffset, scrollUpdateWasRequested }: {
    scrollOffset: number;
    scrollUpdateWasRequested: boolean;
  }) => {
    if (!scrollUpdateWasRequested) {
      const isAtBottom = scrollOffset >= (displayMessages.length * 60) - 200;
      setShowScrollButton(!isAtBottom && displayMessages.length > 0);
    }
  }, [displayMessages.length]);

  const scrollToBottom = useCallback(() => {
    listRef.current?.scrollToItem(displayMessages.length - 1, 'end');
    setShowScrollButton(false);
  }, [displayMessages.length]);

  const handleSend = useCallback(() => {
    if (inputValue.trim() && onSendMessage) {
      onSendMessage(inputValue.trim());
      setInputValue('');
      inputRef.current?.focus();
    }
  }, [inputValue, onSendMessage]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleCommandClick = useCallback((command: string) => {
    if (onCommandSelect) {
      onCommandSelect(command);
    } else if (onSendMessage) {
      onSendMessage(command);
    }
  }, [onCommandSelect, onSendMessage]);

  const messageItemRenderer = useCallback((props: any) => (
    <MessageItem {...props} data={displayMessages} />
  ), [displayMessages]);

  return (
    <Card className="w-full compact-chat-interface" style={{ height }}>
      <CardContent className="p-0 h-full flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center justify-between p-3 border-b bg-muted/20">
          <div className="flex items-center space-x-2">
            <MessageCircle className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium text-sm">Chat</span>
          </div>
          <div className="text-xs text-muted-foreground">
            {displayMessages.length}/{messages.length} messages
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 relative overflow-hidden">
          {displayMessages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <MessageCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No messages yet</p>
                <p className="text-xs">Start a conversation below</p>
              </div>
            </div>
          ) : (
            <List
              ref={listRef}
              height={height - 160} // Account for header, input, and suggestions
              itemCount={displayMessages.length}
              itemSize={60}
              onScroll={handleScroll}
              className="scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent"
            >
              {messageItemRenderer}
            </List>
          )}

          {/* Scroll to bottom button */}
          {showScrollButton && (
            <Button
              size="sm"
              variant="outline"
              className="absolute bottom-2 right-2 h-8 w-8 p-0 rounded-full shadow-lg"
              onClick={scrollToBottom}
            >
              <ChevronDown className="h-3 w-3" />
            </Button>
          )}

          {/* Loading indicator */}
          {isLoading && (
            <div className="absolute bottom-2 left-3 flex items-center space-x-2 text-xs text-muted-foreground">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary"></div>
              <span>Typing...</span>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-3 border-t">
          <div className="flex items-end space-x-2">
            <Textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              className="flex-1 min-h-[36px] max-h-[72px] resize-none text-sm"
              rows={1}
              disabled={isLoading}
            />
            <Button
              size="sm"
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              className="h-9 w-9 p-0"
            >
              <Send className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* Command Suggestions */}
        {showSuggestions && (
          <div className="border-t bg-muted/10">
            <div className="p-2">
              <div className="flex items-center space-x-1 mb-2">
                <Zap className="h-3 w-3 text-muted-foreground" />
                <span className="text-xs font-medium text-muted-foreground">Quick Commands</span>
              </div>
              <ScrollArea className="h-16">
                <div className="flex flex-wrap gap-1">
                  {defaultCommands.map((command, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="h-6 px-2 text-xs whitespace-nowrap"
                      onClick={() => handleCommandClick(command.text)}
                      disabled={isLoading}
                      title={command.description}
                    >
                      {command.text}
                    </Button>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};