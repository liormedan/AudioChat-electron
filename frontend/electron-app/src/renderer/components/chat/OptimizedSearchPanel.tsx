import React, { memo, useState, useMemo, useCallback } from 'react';
import { Search, X, Filter, Calendar, User, MessageSquare, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { cn } from '@/lib/utils';
import { 
  useOptimizedSearch, 
  useDebouncedCallback, 
  useStableCallback,
  useRenderPerformance 
} from '@/hooks/usePerformance';
import { Message } from '@/types/chat';

interface SearchFilters {
  dateRange?: {
    from: Date;
    to: Date;
  };
  messageType?: 'all' | 'user' | 'assistant' | 'system';
  sessionId?: string;
  hasAttachments?: boolean;
  minLength?: number;
  maxLength?: number;
}

interface OptimizedSearchPanelProps {
  messages: Message[];
  sessions: Array<{ id: string; title: string }>;
  onSearchResults?: (results: Message[]) => void;
  onMessageSelect?: (message: Message) => void;
  className?: string;
  placeholder?: string;
  debounceMs?: number;
  maxResults?: number;
}

// Memoized search result item
const SearchResultItem = memo<{
  message: Message;
  searchTerm: string;
  onSelect: (message: Message) => void;
}>(({ message, searchTerm, onSelect }) => {
  const handleSelect = useStableCallback(() => {
    onSelect(message);
  });

  // Highlight search term in content
  const highlightedContent = useMemo(() => {
    if (!searchTerm.trim()) return message.content;
    
    const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return message.content.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800">$1</mark>');
  }, [message.content, searchTerm]);

  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp).toLocaleString('he-IL');

  return (
    <Card 
      className="cursor-pointer hover:bg-accent/50 transition-colors"
      onClick={handleSelect}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
            isUser 
              ? "bg-primary text-primary-foreground" 
              : "bg-secondary text-secondary-foreground"
          )}>
            {isUser ? (
              <User className="w-4 h-4" />
            ) : (
              <MessageSquare className="w-4 h-4" />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-2">
              <Badge variant={isUser ? "default" : "secondary"} className="text-xs">
                {isUser ? 'משתמש' : 'עוזר'}
              </Badge>
              <span className="text-xs text-muted-foreground">{timestamp}</span>
            </div>
            
            <div 
              className="text-sm line-clamp-3"
              dangerouslySetInnerHTML={{ __html: highlightedContent }}
            />
            
            {message.tokens_used && (
              <div className="mt-2 text-xs text-muted-foreground">
                {message.tokens_used} tokens
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

SearchResultItem.displayName = 'SearchResultItem';

// Memoized filter panel
const FilterPanel = memo<{
  filters: SearchFilters;
  sessions: Array<{ id: string; title: string }>;
  onFiltersChange: (filters: SearchFilters) => void;
}>(({ filters, sessions, onFiltersChange }) => {
  const handleFilterChange = useStableCallback((key: keyof SearchFilters, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  });

  const clearFilters = useStableCallback(() => {
    onFiltersChange({});
  });

  const hasActiveFilters = useMemo(() => {
    return Object.keys(filters).length > 0;
  }, [filters]);

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="relative">
          <Filter className="w-4 h-4 mr-2" />
          מסננים
          {hasActiveFilters && (
            <Badge className="absolute -top-2 -right-2 h-5 w-5 p-0 text-xs">
              {Object.keys(filters).length}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="end">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">מסננים</h4>
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                נקה הכל
              </Button>
            )}
          </div>

          {/* Message Type Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">סוג הודעה</label>
            <Select
              value={filters.messageType || 'all'}
              onValueChange={(value) => handleFilterChange('messageType', value === 'all' ? undefined : value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">כל ההודעות</SelectItem>
                <SelectItem value="user">הודעות משתמש</SelectItem>
                <SelectItem value="assistant">הודעות עוזר</SelectItem>
                <SelectItem value="system">הודעות מערכת</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Session Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">שיחה</label>
            <Select
              value={filters.sessionId || 'all'}
              onValueChange={(value) => handleFilterChange('sessionId', value === 'all' ? undefined : value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="כל השיחות" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">כל השיחות</SelectItem>
                {sessions.map((session) => (
                  <SelectItem key={session.id} value={session.id}>
                    {session.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Date Range Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">טווח תאריכים</label>
            <div className="flex gap-2">
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Calendar className="w-4 h-4 mr-2" />
                    {filters.dateRange?.from 
                      ? filters.dateRange.from.toLocaleDateString('he-IL')
                      : 'מתאריך'
                    }
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <CalendarComponent
                    mode="single"
                    selected={filters.dateRange?.from}
                    onSelect={(date) => handleFilterChange('dateRange', {
                      ...filters.dateRange,
                      from: date
                    })}
                  />
                </PopoverContent>
              </Popover>
              
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Calendar className="w-4 h-4 mr-2" />
                    {filters.dateRange?.to 
                      ? filters.dateRange.to.toLocaleDateString('he-IL')
                      : 'עד תאריך'
                    }
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <CalendarComponent
                    mode="single"
                    selected={filters.dateRange?.to}
                    onSelect={(date) => handleFilterChange('dateRange', {
                      ...filters.dateRange,
                      to: date
                    })}
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
});

FilterPanel.displayName = 'FilterPanel';

// Main search panel component
export const OptimizedSearchPanel = memo<OptimizedSearchPanelProps>(({
  messages,
  sessions,
  onSearchResults,
  onMessageSelect,
  className,
  placeholder = "חפש בהודעות...",
  debounceMs = 300,
  maxResults = 50
}) => {
  const { markRenderStart, markRenderEnd } = useRenderPerformance('OptimizedSearchPanel');
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});
  const [isExpanded, setIsExpanded] = useState(false);

  markRenderStart();

  // Apply filters to messages
  const filteredMessages = useMemo(() => {
    let filtered = messages;

    // Apply date range filter
    if (filters.dateRange?.from || filters.dateRange?.to) {
      filtered = filtered.filter(message => {
        const messageDate = new Date(message.timestamp);
        if (filters.dateRange?.from && messageDate < filters.dateRange.from) return false;
        if (filters.dateRange?.to && messageDate > filters.dateRange.to) return false;
        return true;
      });
    }

    // Apply message type filter
    if (filters.messageType && filters.messageType !== 'all') {
      filtered = filtered.filter(message => message.role === filters.messageType);
    }

    // Apply session filter
    if (filters.sessionId) {
      filtered = filtered.filter(message => message.session_id === filters.sessionId);
    }

    // Apply length filters
    if (filters.minLength) {
      filtered = filtered.filter(message => message.content.length >= filters.minLength!);
    }
    if (filters.maxLength) {
      filtered = filtered.filter(message => message.content.length <= filters.maxLength!);
    }

    return filtered;
  }, [messages, filters]);

  // Use optimized search hook
  const { filteredItems: searchResults, isSearching } = useOptimizedSearch(
    filteredMessages,
    searchTerm,
    ['content'] as (keyof Message)[],
    debounceMs
  );

  // Limit results for performance
  const limitedResults = useMemo(() => 
    searchResults.slice(0, maxResults),
    [searchResults, maxResults]
  );

  // Debounced search results callback
  const debouncedOnSearchResults = useDebouncedCallback(
    (results: Message[]) => {
      onSearchResults?.(results);
    },
    debounceMs,
    [onSearchResults]
  );

  // Update search results
  React.useEffect(() => {
    debouncedOnSearchResults(limitedResults);
  }, [limitedResults, debouncedOnSearchResults]);

  // Stable handlers
  const handleSearchChange = useStableCallback((value: string) => {
    setSearchTerm(value);
  });

  const handleClearSearch = useStableCallback(() => {
    setSearchTerm('');
    setFilters({});
  });

  const handleMessageSelect = useStableCallback((message: Message) => {
    onMessageSelect?.(message);
  });

  const toggleExpanded = useStableCallback(() => {
    setIsExpanded(!isExpanded);
  });

  // Active filters count
  const activeFiltersCount = useMemo(() => 
    Object.keys(filters).length,
    [filters]
  );

  markRenderEnd();

  return (
    <div className={cn("space-y-4", className)}>
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input
          type="text"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="pr-10 pl-10"
        />
        {(searchTerm || activeFiltersCount > 0) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearSearch}
            className="absolute left-1 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Search Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FilterPanel
            filters={filters}
            sessions={sessions}
            onFiltersChange={setFilters}
          />
          
          {isSearching && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              מחפש...
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          {searchTerm && (
            <span>
              {limitedResults.length} מתוך {searchResults.length} תוצאות
            </span>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleExpanded}
            className="h-6"
          >
            {isExpanded ? 'כווץ' : 'הרחב'}
          </Button>
        </div>
      </div>

      {/* Search Results */}
      {searchTerm && (
        <div className={cn(
          "space-y-2 transition-all duration-200",
          isExpanded ? "max-h-[600px]" : "max-h-[300px]",
          "overflow-y-auto scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent"
        )}>
          {limitedResults.length > 0 ? (
            limitedResults.map((message) => (
              <SearchResultItem
                key={message.id}
                message={message}
                searchTerm={searchTerm}
                onSelect={handleMessageSelect}
              />
            ))
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">לא נמצאו תוצאות</h3>
                <p className="text-muted-foreground">
                  נסה לשנות את מונחי החיפוש או המסננים
                </p>
              </CardContent>
            </Card>
          )}
          
          {searchResults.length > maxResults && (
            <Card>
              <CardContent className="p-4 text-center">
                <p className="text-sm text-muted-foreground">
                  מוצגות {maxResults} תוצאות ראשונות מתוך {searchResults.length}.
                  נסה לחדד את החיפוש לתוצאות מדויקות יותר.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
});

OptimizedSearchPanel.displayName = 'OptimizedSearchPanel';

export default OptimizedSearchPanel;