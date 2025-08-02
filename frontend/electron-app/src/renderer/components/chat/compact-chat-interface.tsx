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
    showSuggestions?: boolean;
    autoScroll?: boolean;
    isTyping?: boolean;
    disabled?: boolean;
}

interface CommandSuggestion {
    text: string;
    description: string;
    category: string;
}

const COMMAND_SUGGESTIONS: CommandSuggestion[] = [
    { text: "Increase volume by 20%", description: "Boost audio", category: "Volume" },
    { text: "Remove background noise", description: "Clean audio", category: "Cleanup" },
    { text: "Cut first 30 seconds", description: "Trim start", category: "Edit" },
    { text: "Add fade in effect", description: "Smooth start", category: "Effects" },
    { text: "Normalize audio levels", description: "Balance sound", category: "Volume" },
    { text: "Extract 1:00 to 2:30", description: "Get section", category: "Edit" }
];

// Memoized message item component for virtual scrolling
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
    showSuggestions = true,
    autoScroll = true,
    isTyping = false,
    disabled = false
}) => {
    const [inputValue, setInputValue] = useState('');
    const [showAllSuggestions, setShowAllSuggestions] = useState(false);
    const listRef = useRef<List>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    // Limit messages for performance (keep only the most recent)
    const displayMessages = useMemo(() => {
        const recentMessages = messages.slice(-maxMessages);
        return recentMessages;
    }, [messages, maxMessages]);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (autoScroll && listRef.current && displayMessages.length > 0) {
            listRef.current.scrollToItem(displayMessages.length - 1, 'end');
        }
    }, [displayMessages.length, autoScroll]);

    const handleSendMessage = useCallback(() => {
        if (!inputValue.trim() || disabled) return;

        onSendMessage?.(inputValue.trim());
        setInputValue('');

        // Focus back to input
        setTimeout(() => {
            inputRef.current?.focus();
        }, 100);
    }, [inputValue, disabled, onSendMessage]);

    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    }, [handleSendMessage]);

    const handleCommandSelect = useCallback((command: string) => {
        onCommandSelect?.(command);
        // Optionally add the command as a user message
        onSendMessage?.(command);
    }, [onCommandSelect, onSendMessage]);

    const visibleSuggestions = showAllSuggestions
        ? COMMAND_SUGGESTIONS
        : COMMAND_SUGGESTIONS.slice(0, 3);

    // Calculate heights for different sections
    const chatHeight = showSuggestions ? Math.floor(height * 0.65) : Math.floor(height * 0.85); // ~260px or ~340px
    const inputHeight = 60; // Fixed input area height
    const suggestionsHeight = showSuggestions ? height - chatHeight - inputHeight : 0; // ~80px

    return (
        <Card className="w-full compact-chat-interface" style={{ height }}>
            <CardContent className="p-0 h-full flex flex-col">
                {/* Chat Messages Area */}
                <div className="flex-shrink-0 border-b" style={{ height: chatHeight }}>
                    {displayMessages.length === 0 ? (
                        <div className="flex items-center justify-center h-full text-muted-foreground">
                            <div className="text-center">
                                <MessageCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                                <p className="text-sm">No messages yet</p>
                                <p className="text-xs">Start a conversation below</p>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full">
                            <List
                                ref={listRef}
                                height={chatHeight}
                                itemCount={displayMessages.length + (isTyping ? 1 : 0)}
                                itemSize={80}
                                itemData={displayMessages}
                                className="scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent"
                            >
                                {({ index, style }) => {
                                    if (index === displayMessages.length && isTyping) {
                                        return (
                                            <div style={style} className="px-3 py-1">
                                                <div className="flex justify-start">
                                                    <div className="bg-muted text-foreground px-3 py-2 rounded-lg text-sm">
                                                        <div className="flex items-center space-x-1">
                                                            <div className="flex space-x-1">
                                                                <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                                                <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                                                <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                                            </div>
                                                            <span className="text-xs opacity-70 ml-2">Typing...</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    }
                                    return <MessageItem index={index} style={style} data={displayMessages} />;
                                }}
                            </List>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="flex-shrink-0 border-b p-3" style={{ height: inputHeight }}>
                    <div className="flex items-end space-x-2">
                        <Textarea
                            ref={inputRef}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Type your message..."
                            className="flex-1 min-h-[36px] max-h-[36px] resize-none text-sm"
                            disabled={disabled}
                        />
                        <Button
                            onClick={handleSendMessage}
                            disabled={!inputValue.trim() || disabled}
                            size="sm"
                            className="h-9 w-9 p-0"
                        >
                            <Send className="h-4 w-4" />
                        </Button>
                    </div>
                </div>

                {/* Command Suggestions Area */}
                {showSuggestions && (
                    <div className="flex-1 overflow-hidden" style={{ height: suggestionsHeight }}>
                        <div className="p-2 h-full">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center space-x-1">
                                    <Zap className="h-3 w-3 text-muted-foreground" />
                                    <span className="text-xs font-medium text-muted-foreground">Quick Commands</span>
                                </div>
                                {COMMAND_SUGGESTIONS.length > 3 && (
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => setShowAllSuggestions(!showAllSuggestions)}
                                        className="h-6 px-2 text-xs"
                                    >
                                        <ChevronDown className={cn(
                                            "h-3 w-3 transition-transform",
                                            showAllSuggestions && "rotate-180"
                                        )} />
                                    </Button>
                                )}
                            </div>

                            <ScrollArea className="h-full">
                                <div className="space-y-1">
                                    {visibleSuggestions.map((suggestion, index) => (
                                        <Button
                                            key={index}
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleCommandSelect(suggestion.text)}
                                            disabled={disabled}
                                            className="w-full justify-start h-auto p-2 text-left"
                                        >
                                            <div className="space-y-0.5">
                                                <div className="text-xs font-medium">{suggestion.text}</div>
                                                <div className="text-xs text-muted-foreground">
                                                    {suggestion.description}
                                                </div>
                                            </div>
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