import React, { memo, useCallback, useMemo, useRef, useEffect, useState } from 'react';
import { FixedSizeList as List, ListChildComponentProps } from 'react-window';
import { Message } from '@/types/chat';
import { MessageBubble } from './MessageBubble';
import { useVirtualScrolling, useComponentSize, useRenderPerformance } from '@/hooks/usePerformance';
import { cn } from '@/lib/utils';

interface VirtualMessageListProps {
  messages: Message[];
  sessionId: string;
  autoScroll?: boolean;
  itemHeight?: number;
  className?: string;
  onMessageClick?: (message: Message) => void;
  onMessageCopy?: (message: Message) => void;
  onMessageDelete?: (messageId: string) => void;
  loading?: boolean;
  error?: string;
}

// Memoized message item component
const MessageItem = memo<ListChildComponentProps<Message[]>>(({ 
  index, 
  style, 
  data 
}) => {
  const message = data[index];
  
  if (!message) {
    return (
      <div style={style} className="flex items-center justify-center">
        <div className="animate-pulse bg-muted rounded-lg h-16 w-full mx-4" />
      </div>
    );
  }

  return (
    <div style={style} className="px-4 py-2">
      <MessageBubble 
        message={message}
        showTimestamp={true}
        showActions={true}
      />
    </div>
  );
});

MessageItem.displayName = 'MessageItem';

// Optimized scroll-to-bottom component
const ScrollToBottomButton = memo<{
  visible: boolean;
  onClick: () => void;
}>(({ visible, onClick }) => {
  if (!visible) return null;

  return (
    <button
      onClick={onClick}
      className={cn(
        "absolute bottom-4 right-4 z-10",
        "bg-primary text-primary-foreground",
        "rounded-full p-2 shadow-lg",
        "transition-all duration-200",
        "hover:scale-110 hover:shadow-xl",
        "focus:outline-none focus:ring-2 focus:ring-primary/50"
      )}
      aria-label="גלול למטה"
    >
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M19 14l-7 7m0 0l-7-7m7 7V3"
        />
      </svg>
    </button>
  );
});

ScrollToBottomButton.displayName = 'ScrollToBottomButton';

// Loading skeleton component
const MessageListSkeleton = memo(() => (
  <div className="space-y-4 p-4">
    {Array.from({ length: 5 }).map((_, index) => (
      <div key={index} className="animate-pulse">
        <div className={cn(
          "flex gap-3",
          index % 2 === 0 ? "justify-start" : "justify-end"
        )}>
          <div className={cn(
            "rounded-lg p-3 max-w-[70%]",
            index % 2 === 0 ? "bg-muted" : "bg-primary/20"
          )}>
            <div className="h-4 bg-current opacity-20 rounded mb-2" />
            <div className="h-4 bg-current opacity-20 rounded w-3/4" />
          </div>
        </div>
      </div>
    ))}
  </div>
));

MessageListSkeleton.displayName = 'MessageListSkeleton';

// Error state component
const MessageListError = memo<{ error: string; onRetry?: () => void }>(({ 
  error, 
  onRetry 
}) => (
  <div className="flex flex-col items-center justify-center h-full p-8 text-center">
    <div className="text-destructive mb-4">
      <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <h3 className="text-lg font-semibold mb-2">שגיאה בטעינת ההודעות</h3>
    <p className="text-muted-foreground mb-4">{error}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      >
        נסה שוב
      </button>
    )}
  </div>
));

MessageListError.displayName = 'MessageListError';

// Empty state component
const EmptyMessageList = memo(() => (
  <div className="flex flex-col items-center justify-center h-full p-8 text-center">
    <div className="text-muted-foreground mb-4">
      <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    </div>
    <h3 className="text-lg font-semibold mb-2">אין הודעות עדיין</h3>
    <p className="text-muted-foreground">התחל שיחה חדשה על ידי כתיבת הודעה למטה</p>
  </div>
));

EmptyMessageList.displayName = 'EmptyMessageList';

export const VirtualMessageList = memo<VirtualMessageListProps>(({
  messages,
  sessionId,
  autoScroll = true,
  itemHeight = 120,
  className,
  onMessageClick,
  onMessageCopy,
  onMessageDelete,
  loading = false,
  error
}) => {
  const { markRenderStart, markRenderEnd } = useRenderPerformance('VirtualMessageList');
  const { elementRef, size } = useComponentSize();
  const listRef = useRef<List>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const lastMessageCountRef = useRef(messages.length);

  // Mark render start
  markRenderStart();

  // Memoized messages for performance
  const memoizedMessages = useMemo(() => messages, [messages]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScroll && !isUserScrolling && messages.length > lastMessageCountRef.current) {
      listRef.current?.scrollToItem(messages.length - 1, 'end');
    }
    lastMessageCountRef.current = messages.length;
  }, [messages.length, autoScroll, isUserScrolling]);

  // Handle scroll events
  const handleScroll = useCallback(({ scrollOffset, scrollUpdateWasRequested }: {
    scrollOffset: number;
    scrollUpdateWasRequested: boolean;
  }) => {
    if (!scrollUpdateWasRequested) {
      setIsUserScrolling(true);
      
      // Show scroll-to-bottom button when not at bottom
      const isAtBottom = scrollOffset >= (messages.length * itemHeight) - size.height - 100;
      setShowScrollButton(!isAtBottom && messages.length > 0);
      
      // Reset user scrolling flag after a delay
      setTimeout(() => setIsUserScrolling(false), 1000);
    }
  }, [messages.length, itemHeight, size.height]);

  // Scroll to bottom handler
  const scrollToBottom = useCallback(() => {
    listRef.current?.scrollToItem(messages.length - 1, 'end');
    setShowScrollButton(false);
    setIsUserScrolling(false);
  }, [messages.length]);

  // Optimized item renderer
  const itemRenderer = useCallback((props: ListChildComponentProps) => (
    <MessageItem {...props} data={memoizedMessages} />
  ), [memoizedMessages]);

  // Mark render end
  useEffect(() => {
    markRenderEnd();
  });

  // Loading state
  if (loading) {
    return (
      <div ref={elementRef} className={cn("flex-1 overflow-hidden", className)}>
        <MessageListSkeleton />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div ref={elementRef} className={cn("flex-1 overflow-hidden", className)}>
        <MessageListError error={error} />
      </div>
    );
  }

  // Empty state
  if (messages.length === 0) {
    return (
      <div ref={elementRef} className={cn("flex-1 overflow-hidden", className)}>
        <EmptyMessageList />
      </div>
    );
  }

  return (
    <div ref={elementRef} className={cn("flex-1 overflow-hidden relative", className)}>
      {size.height > 0 && (
        <List
          ref={listRef}
          height={size.height}
          itemCount={messages.length}
          itemSize={itemHeight}
          itemData={memoizedMessages}
          onScroll={handleScroll}
          className="scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent"
          direction="rtl"
        >
          {itemRenderer}
        </List>
      )}
      
      <ScrollToBottomButton
        visible={showScrollButton}
        onClick={scrollToBottom}
      />
    </div>
  );
});

VirtualMessageList.displayName = 'VirtualMessageList';

// Performance monitoring wrapper (development only)
export const VirtualMessageListWithMonitoring = memo<VirtualMessageListProps>((props) => {
  if (process.env.NODE_ENV === 'development') {
    return (
      <div className="relative">
        <VirtualMessageList {...props} />
        <div className="absolute top-2 left-2 bg-black/80 text-white text-xs p-2 rounded">
          Messages: {props.messages.length}
        </div>
      </div>
    );
  }
  
  return <VirtualMessageList {...props} />;
});

VirtualMessageListWithMonitoring.displayName = 'VirtualMessageListWithMonitoring';

export default VirtualMessageList;