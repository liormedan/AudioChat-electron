import React, { memo, useCallback, useMemo, useState } from 'react';
import { Message } from '@/types/chat';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { 
  Copy, 
  Check, 
  Trash2, 
  Edit3, 
  MoreHorizontal,
  User,
  Bot,
  Clock
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useStableCallback } from '@/hooks/usePerformance';

interface MessageBubbleProps {
  message: Message;
  showTimestamp?: boolean;
  showActions?: boolean;
  showAvatar?: boolean;
  compact?: boolean;
  onCopy?: (message: Message) => void;
  onEdit?: (message: Message) => void;
  onDelete?: (messageId: string) => void;
  onRegenerate?: (message: Message) => void;
  className?: string;
}

// Memoized timestamp component
const MessageTimestamp = memo<{ timestamp: Date; compact?: boolean }>(({ 
  timestamp, 
  compact = false 
}) => {
  const formattedTime = useMemo(() => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (compact) {
      if (minutes < 1) return 'עכשיו';
      if (minutes < 60) return `${minutes}ד`;
      if (hours < 24) return `${hours}ש`;
      if (days < 7) return `${days}י`;
      return timestamp.toLocaleDateString('he-IL', { 
        month: 'short', 
        day: 'numeric' 
      });
    }

    if (minutes < 1) return 'עכשיו';
    if (minutes < 60) return `לפני ${minutes} דקות`;
    if (hours < 24) return `לפני ${hours} שעות`;
    if (days < 7) return `לפני ${days} ימים`;
    
    return timestamp.toLocaleDateString('he-IL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }, [timestamp, compact]);

  return (
    <span className={cn(
      "text-xs text-muted-foreground flex items-center gap-1",
      compact && "text-[10px]"
    )}>
      <Clock className="w-3 h-3" />
      {formattedTime}
    </span>
  );
});

MessageTimestamp.displayName = 'MessageTimestamp';

// Memoized avatar component
const MessageAvatar = memo<{ role: string; compact?: boolean }>(({ 
  role, 
  compact = false 
}) => {
  const isUser = role === 'user';
  const size = compact ? 'w-6 h-6' : 'w-8 h-8';
  
  return (
    <div className={cn(
      "flex-shrink-0 rounded-full flex items-center justify-center",
      size,
      isUser 
        ? "bg-primary text-primary-foreground" 
        : "bg-secondary text-secondary-foreground"
    )}>
      {isUser ? (
        <User className={compact ? "w-3 h-3" : "w-4 h-4"} />
      ) : (
        <Bot className={compact ? "w-3 h-3" : "w-4 h-4"} />
      )}
    </div>
  );
});

MessageAvatar.displayName = 'MessageAvatar';

// Memoized message content with syntax highlighting
const MessageContent = memo<{ 
  content: string; 
  role: string;
  compact?: boolean;
}>(({ content, role, compact = false }) => {
  // Simple markdown-like formatting
  const formattedContent = useMemo(() => {
    let formatted = content;
    
    // Code blocks
    formatted = formatted.replace(
      /```(\w+)?\n([\s\S]*?)```/g,
      '<pre class="bg-muted p-3 rounded-md overflow-x-auto my-2"><code class="text-sm">$2</code></pre>'
    );
    
    // Inline code
    formatted = formatted.replace(
      /`([^`]+)`/g,
      '<code class="bg-muted px-1 py-0.5 rounded text-sm">$1</code>'
    );
    
    // Bold text
    formatted = formatted.replace(
      /\*\*(.*?)\*\*/g,
      '<strong>$1</strong>'
    );
    
    // Italic text
    formatted = formatted.replace(
      /\*(.*?)\*/g,
      '<em>$1</em>'
    );
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br />');
    
    return formatted;
  }, [content]);

  return (
    <div 
      className={cn(
        "prose prose-sm max-w-none",
        compact && "text-sm",
        role === 'user' ? "prose-invert" : "prose-slate"
      )}
      dangerouslySetInnerHTML={{ __html: formattedContent }}
    />
  );
});

MessageContent.displayName = 'MessageContent';

// Memoized copy button with feedback
const CopyButton = memo<{ 
  onCopy: () => void;
  compact?: boolean;
}>(({ onCopy, compact = false }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useStableCallback(() => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  });

  return (
    <Button
      variant="ghost"
      size={compact ? "sm" : "default"}
      onClick={handleCopy}
      className={cn(
        "opacity-0 group-hover:opacity-100 transition-opacity",
        compact && "h-6 w-6 p-1"
      )}
      title="העתק הודעה"
    >
      {copied ? (
        <Check className={compact ? "w-3 h-3" : "w-4 h-4"} />
      ) : (
        <Copy className={compact ? "w-3 h-3" : "w-4 h-4"} />
      )}
    </Button>
  );
});

CopyButton.displayName = 'CopyButton';

// Memoized message actions dropdown
const MessageActions = memo<{
  message: Message;
  onCopy?: (message: Message) => void;
  onEdit?: (message: Message) => void;
  onDelete?: (messageId: string) => void;
  onRegenerate?: (message: Message) => void;
  compact?: boolean;
}>(({ message, onCopy, onEdit, onDelete, onRegenerate, compact = false }) => {
  const handleCopy = useStableCallback(() => {
    onCopy?.(message);
    navigator.clipboard.writeText(message.content);
  });

  const handleEdit = useStableCallback(() => {
    onEdit?.(message);
  });

  const handleDelete = useStableCallback(() => {
    onDelete?.(message.id);
  });

  const handleRegenerate = useStableCallback(() => {
    onRegenerate?.(message);
  });

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size={compact ? "sm" : "default"}
          className={cn(
            "opacity-0 group-hover:opacity-100 transition-opacity",
            compact && "h-6 w-6 p-1"
          )}
        >
          <MoreHorizontal className={compact ? "w-3 h-3" : "w-4 h-4"} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem onClick={handleCopy}>
          <Copy className="w-4 h-4 mr-2" />
          העתק הודעה
        </DropdownMenuItem>
        
        {message.role === 'user' && onEdit && (
          <DropdownMenuItem onClick={handleEdit}>
            <Edit3 className="w-4 h-4 mr-2" />
            ערוך הודעה
          </DropdownMenuItem>
        )}
        
        {message.role === 'assistant' && onRegenerate && (
          <DropdownMenuItem onClick={handleRegenerate}>
            <Bot className="w-4 h-4 mr-2" />
            צור תשובה מחדש
          </DropdownMenuItem>
        )}
        
        <DropdownMenuSeparator />
        
        {onDelete && (
          <DropdownMenuItem 
            onClick={handleDelete}
            className="text-destructive focus:text-destructive"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            מחק הודעה
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
});

MessageActions.displayName = 'MessageActions';

// Main message bubble component
export const MessageBubble = memo<MessageBubbleProps>(({
  message,
  showTimestamp = true,
  showActions = true,
  showAvatar = true,
  compact = false,
  onCopy,
  onEdit,
  onDelete,
  onRegenerate,
  className
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const isSystem = message.role === 'system';

  // Memoized bubble classes
  const bubbleClasses = useMemo(() => cn(
    "group relative flex gap-3 p-4 rounded-lg transition-all duration-200",
    compact && "p-2 gap-2",
    isUser && "flex-row-reverse",
    "hover:bg-accent/50",
    className
  ), [isUser, compact, className]);

  // Memoized content classes
  const contentClasses = useMemo(() => cn(
    "flex-1 min-w-0",
    isUser && "text-right"
  ), [isUser]);

  // Memoized message bubble classes
  const messageBubbleClasses = useMemo(() => cn(
    "rounded-lg px-4 py-2 max-w-[80%] break-words",
    compact && "px-3 py-1.5 text-sm",
    isUser && [
      "bg-primary text-primary-foreground",
      "ml-auto"
    ],
    isAssistant && [
      "bg-secondary text-secondary-foreground",
      "mr-auto"
    ],
    isSystem && [
      "bg-muted text-muted-foreground",
      "mx-auto text-center text-sm italic"
    ]
  ), [isUser, isAssistant, isSystem, compact]);

  // Stable copy handler
  const handleCopy = useStableCallback(() => {
    navigator.clipboard.writeText(message.content);
    onCopy?.(message);
  });

  return (
    <div className={bubbleClasses}>
      {showAvatar && !isSystem && (
        <MessageAvatar role={message.role} compact={compact} />
      )}
      
      <div className={contentClasses}>
        <div className={messageBubbleClasses}>
          <MessageContent 
            content={message.content} 
            role={message.role}
            compact={compact}
          />
          
          {showTimestamp && (
            <div className={cn(
              "mt-2 flex items-center gap-2",
              isUser ? "justify-end" : "justify-start"
            )}>
              <MessageTimestamp 
                timestamp={new Date(message.timestamp)} 
                compact={compact}
              />
              
              {message.tokens_used && (
                <span className="text-xs text-muted-foreground">
                  {message.tokens_used} tokens
                </span>
              )}
              
              {message.response_time && (
                <span className="text-xs text-muted-foreground">
                  {message.response_time.toFixed(1)}s
                </span>
              )}
            </div>
          )}
        </div>
        
        {showActions && !isSystem && (
          <div className={cn(
            "flex items-center gap-1 mt-2",
            isUser ? "justify-end" : "justify-start"
          )}>
            <CopyButton onCopy={handleCopy} compact={compact} />
            
            <MessageActions
              message={message}
              onCopy={onCopy}
              onEdit={onEdit}
              onDelete={onDelete}
              onRegenerate={onRegenerate}
              compact={compact}
            />
          </div>
        )}
      </div>
    </div>
  );
});

MessageBubble.displayName = 'MessageBubble';

// Lightweight version for virtual scrolling
export const MessageBubbleLite = memo<Pick<MessageBubbleProps, 
  'message' | 'compact' | 'className'
>>(({ message, compact = true, className }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={cn(
      "flex gap-2 p-2",
      isUser && "flex-row-reverse",
      className
    )}>
      <MessageAvatar role={message.role} compact={true} />
      <div className={cn(
        "rounded-lg px-3 py-2 max-w-[80%] text-sm",
        isUser 
          ? "bg-primary text-primary-foreground ml-auto" 
          : "bg-secondary text-secondary-foreground mr-auto"
      )}>
        {message.content}
      </div>
    </div>
  );
});

MessageBubbleLite.displayName = 'MessageBubbleLite';

export default MessageBubble;