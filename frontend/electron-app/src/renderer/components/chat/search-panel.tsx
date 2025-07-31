import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { Search, Filter, Calendar, User, History, Save, X, ChevronDown, ChevronUp } from 'lucide-react';
import { useChatStore } from '@/stores/chat-store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

interface SearchResult {
  sessionId: string;
  sessionTitle: string;
  messageId: string;
  messageText: string;
  sender: 'user' | 'bot';
  timestamp: string;
  highlights: Array<{ start: number; end: number; text: string }>;
}

interface SearchFilter {
  dateFrom?: string;
  dateTo?: string;
  sender?: 'user' | 'bot' | 'all';
  sessionId?: string;
}

interface SavedSearch {
  id: string;
  name: string;
  query: string;
  filters: SearchFilter;
  createdAt: string;
}

interface SearchPanelProps {
  className?: string;
  onResultSelect?: (sessionId: string, messageId: string) => void;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({ 
  className = '', 
  onResultSelect 
}) => {
  const { sessions } = useChatStore();
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [isRegexMode, setIsRegexMode] = useState(false);
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  
  // Filter state
  const [filters, setFilters] = useState<SearchFilter>({
    sender: 'all'
  });
  
  // Search history and saved searches
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveSearchName, setSaveSearchName] = useState('');
  
  // Results state
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Load saved data from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('chat-search-history');
    const savedSearchesData = localStorage.getItem('chat-saved-searches');
    
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }
    
    if (savedSearchesData) {
      setSavedSearches(JSON.parse(savedSearchesData));
    }
  }, []);

  // Save search history to localStorage
  const saveToHistory = useCallback((query: string) => {
    if (!query.trim() || searchHistory.includes(query)) return;
    
    const newHistory = [query, ...searchHistory.slice(0, 9)]; // Keep last 10
    setSearchHistory(newHistory);
    localStorage.setItem('chat-search-history', JSON.stringify(newHistory));
  }, [searchHistory]);

  // Highlight text function
  const highlightText = useCallback((text: string, query: string, isRegex: boolean): Array<{ start: number; end: number; text: string }> => {
    if (!query.trim()) return [];
    
    try {
      const regex = isRegex 
        ? new RegExp(query, 'gi')
        : new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      
      const matches: Array<{ start: number; end: number; text: string }> = [];
      let match;
      
      while ((match = regex.exec(text)) !== null) {
        matches.push({
          start: match.index,
          end: match.index + match[0].length,
          text: match[0]
        });
        
        if (!regex.global) break;
      }
      
      return matches;
    } catch (error) {
      // Invalid regex, fall back to simple text search
      if (isRegex) {
        return highlightText(text, query, false);
      }
      return [];
    }
  }, []);

  // Perform search
  const performSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    saveToHistory(searchQuery);

    try {
      const results: SearchResult[] = [];
      
      sessions.forEach(session => {
        // Apply session filter
        if (filters.sessionId && session.id !== filters.sessionId) return;
        
        session.messages.forEach(message => {
          // Apply sender filter
          if (filters.sender !== 'all' && message.sender !== filters.sender) return;
          
          // Apply date filter
          if (filters.dateFrom || filters.dateTo) {
            const messageDate = new Date(message.timestamp || session.createdAt || '');
            if (filters.dateFrom && messageDate < new Date(filters.dateFrom)) return;
            if (filters.dateTo && messageDate > new Date(filters.dateTo)) return;
          }
          
          // Search in message text
          const highlights = highlightText(message.text, searchQuery, isRegexMode);
          
          if (highlights.length > 0) {
            results.push({
              sessionId: session.id,
              sessionTitle: session.title,
              messageId: message.id,
              messageText: message.text,
              sender: message.sender,
              timestamp: message.timestamp || session.createdAt || '',
              highlights
            });
          }
        });
      });
      
      // Sort by timestamp (newest first)
      results.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [searchQuery, filters, sessions, isRegexMode, highlightText, saveToHistory]);

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery.trim()) {
        performSearch();
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, filters, performSearch]);

  // Save search
  const saveSearch = useCallback(() => {
    if (!saveSearchName.trim() || !searchQuery.trim()) return;
    
    const newSavedSearch: SavedSearch = {
      id: `search-${Date.now()}`,
      name: saveSearchName,
      query: searchQuery,
      filters: { ...filters },
      createdAt: new Date().toISOString()
    };
    
    const newSavedSearches = [newSavedSearch, ...savedSearches];
    setSavedSearches(newSavedSearches);
    localStorage.setItem('chat-saved-searches', JSON.stringify(newSavedSearches));
    
    setShowSaveDialog(false);
    setSaveSearchName('');
  }, [saveSearchName, searchQuery, filters, savedSearches]);

  // Load saved search
  const loadSavedSearch = useCallback((savedSearch: SavedSearch) => {
    setSearchQuery(savedSearch.query);
    setFilters(savedSearch.filters);
  }, []);

  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({ sender: 'all' });
  }, []);

  // Render highlighted text
  const renderHighlightedText = useCallback((text: string, highlights: Array<{ start: number; end: number; text: string }>) => {
    if (highlights.length === 0) return text;
    
    const parts = [];
    let lastIndex = 0;
    
    highlights.forEach((highlight, index) => {
      // Add text before highlight
      if (highlight.start > lastIndex) {
        parts.push(text.slice(lastIndex, highlight.start));
      }
      
      // Add highlighted text
      parts.push(
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">
          {highlight.text}
        </mark>
      );
      
      lastIndex = highlight.end;
    });
    
    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }
    
    return parts;
  }, []);

  return (
    <div className={`search-panel ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            חיפוש בשיחות
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Main search input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="חיפוש בתוכן ההודעות..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-20"
            />
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSaveDialog(true)}
                disabled={!searchQuery.trim()}
                title="שמור חיפוש"
              >
                <Save className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
                title="חיפוש מתקדם"
              >
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Regex mode toggle */}
          <div className="flex items-center space-x-2">
            <Switch
              id="regex-mode"
              checked={isRegexMode}
              onCheckedChange={setIsRegexMode}
            />
            <Label htmlFor="regex-mode">מצב Regex</Label>
          </div>

          {/* Advanced filters */}
          <Collapsible open={isAdvancedOpen} onOpenChange={setIsAdvancedOpen}>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" className="w-full justify-between">
                <span className="flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  פילטרים מתקדמים
                </span>
                {isAdvancedOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-4 pt-4">
              {/* Date filters */}
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor="date-from">מתאריך</Label>
                  <Input
                    id="date-from"
                    type="date"
                    value={filters.dateFrom || ''}
                    onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="date-to">עד תאריך</Label>
                  <Input
                    id="date-to"
                    type="date"
                    value={filters.dateTo || ''}
                    onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
                  />
                </div>
              </div>

              {/* Sender filter */}
              <div>
                <Label>שולח ההודעה</Label>
                <div className="flex gap-2 mt-2">
                  <Button
                    variant={filters.sender === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setFilters(prev => ({ ...prev, sender: 'all' }))}
                  >
                    הכל
                  </Button>
                  <Button
                    variant={filters.sender === 'user' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setFilters(prev => ({ ...prev, sender: 'user' }))}
                  >
                    משתמש
                  </Button>
                  <Button
                    variant={filters.sender === 'bot' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setFilters(prev => ({ ...prev, sender: 'bot' }))}
                  >
                    בוט
                  </Button>
                </div>
              </div>

              {/* Session filter */}
              <div>
                <Label htmlFor="session-filter">שיחה ספציפית</Label>
                <select
                  id="session-filter"
                  className="w-full mt-1 p-2 border rounded-md"
                  value={filters.sessionId || ''}
                  onChange={(e) => setFilters(prev => ({ ...prev, sessionId: e.target.value || undefined }))}
                >
                  <option value="">כל השיחות</option>
                  {sessions.map(session => (
                    <option key={session.id} value={session.id}>
                      {session.title}
                    </option>
                  ))}
                </select>
              </div>

              <Button variant="outline" onClick={clearFilters} className="w-full">
                נקה פילטרים
              </Button>
            </CollapsibleContent>
          </Collapsible>

          {/* Tabs for results, history, and saved searches */}
          <Tabs defaultValue="results" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="results">
                תוצאות ({searchResults.length})
              </TabsTrigger>
              <TabsTrigger value="history">
                <History className="h-4 w-4 mr-1" />
                היסטוריה
              </TabsTrigger>
              <TabsTrigger value="saved">
                <Save className="h-4 w-4 mr-1" />
                שמורים
              </TabsTrigger>
            </TabsList>

            {/* Search Results */}
            <TabsContent value="results" className="space-y-2 max-h-96 overflow-y-auto">
              {isSearching ? (
                <div className="text-center py-4 text-muted-foreground">
                  מחפש...
                </div>
              ) : searchResults.length === 0 ? (
                <div className="text-center py-4 text-muted-foreground">
                  {searchQuery ? 'לא נמצאו תוצאות' : 'הזן טקסט לחיפוש'}
                </div>
              ) : (
                searchResults.map((result, index) => (
                  <Card 
                    key={`${result.sessionId}-${result.messageId}-${index}`}
                    className="cursor-pointer hover:bg-accent/50 transition-colors"
                    onClick={() => onResultSelect?.(result.sessionId, result.messageId)}
                  >
                    <CardContent className="p-3">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant={result.sender === 'user' ? 'default' : 'secondary'}>
                            {result.sender === 'user' ? 'משתמש' : 'בוט'}
                          </Badge>
                          <span className="text-sm font-medium">{result.sessionTitle}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {new Date(result.timestamp).toLocaleDateString('he-IL')}
                        </span>
                      </div>
                      <div className="text-sm">
                        {renderHighlightedText(
                          result.messageText.length > 200 
                            ? result.messageText.substring(0, 200) + '...'
                            : result.messageText,
                          result.highlights
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </TabsContent>

            {/* Search History */}
            <TabsContent value="history" className="space-y-2 max-h-96 overflow-y-auto">
              {searchHistory.length === 0 ? (
                <div className="text-center py-4 text-muted-foreground">
                  אין היסטוריית חיפוש
                </div>
              ) : (
                searchHistory.map((query, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 hover:bg-accent/50 rounded cursor-pointer"
                    onClick={() => setSearchQuery(query)}
                  >
                    <span className="text-sm">{query}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        const newHistory = searchHistory.filter((_, i) => i !== index);
                        setSearchHistory(newHistory);
                        localStorage.setItem('chat-search-history', JSON.stringify(newHistory));
                      }}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ))
              )}
            </TabsContent>

            {/* Saved Searches */}
            <TabsContent value="saved" className="space-y-2 max-h-96 overflow-y-auto">
              {savedSearches.length === 0 ? (
                <div className="text-center py-4 text-muted-foreground">
                  אין חיפושים שמורים
                </div>
              ) : (
                savedSearches.map((savedSearch) => (
                  <Card key={savedSearch.id} className="cursor-pointer hover:bg-accent/50">
                    <CardContent className="p-3">
                      <div className="flex items-start justify-between">
                        <div 
                          className="flex-1"
                          onClick={() => loadSavedSearch(savedSearch)}
                        >
                          <div className="font-medium text-sm">{savedSearch.name}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {savedSearch.query}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(savedSearch.createdAt).toLocaleDateString('he-IL')}
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            const newSavedSearches = savedSearches.filter(s => s.id !== savedSearch.id);
                            setSavedSearches(newSavedSearches);
                            localStorage.setItem('chat-saved-searches', JSON.stringify(newSavedSearches));
                          }}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Save Search Dialog */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-96">
            <CardHeader>
              <CardTitle>שמור חיפוש</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="search-name">שם החיפוש</Label>
                <Input
                  id="search-name"
                  value={saveSearchName}
                  onChange={(e) => setSaveSearchName(e.target.value)}
                  placeholder="הזן שם לחיפוש..."
                />
              </div>
              <div className="text-sm text-muted-foreground">
                חיפוש: "{searchQuery}"
              </div>
              <div className="flex gap-2">
                <Button onClick={saveSearch} disabled={!saveSearchName.trim()}>
                  שמור
                </Button>
                <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
                  ביטול
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};