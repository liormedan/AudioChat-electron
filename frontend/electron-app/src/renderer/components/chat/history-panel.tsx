import React, { useState, useMemo, useCallback } from 'react';
import { 
  Clock, 
  Star, 
  TrendingUp, 
  Calendar, 
  MessageSquare, 
  BarChart3,
  Filter,
  SortAsc,
  SortDesc,
  GripVertical,
  Pin,
  PinOff
} from 'lucide-react';
import { useChatStore } from '@/stores/chat-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface HistoryPanelProps {
  onSessionSelect?: (sessionId: string) => void;
  className?: string;
}

interface SessionStats {
  totalMessages: number;
  lastActivity: string;
  duration: string;
  popularity: number;
}

interface DragItem {
  id: string;
  type: 'session';
}

export const HistoryPanel: React.FC<HistoryPanelProps> = ({
  onSessionSelect,
  className = ''
}) => {
  const { sessions, activeSessionId, setActiveSession, updateSession } = useChatStore();
  
  const [sortBy, setSortBy] = useState<'recent' | 'popular' | 'messages' | 'alphabetical'>('recent');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [draggedItem, setDraggedItem] = useState<DragItem | null>(null);
  const [pinnedSessions, setPinnedSessions] = useState<Set<string>>(new Set());

  // Calculate session statistics
  const getSessionStats = useCallback((session: any): SessionStats => {
    const totalMessages = session.messages.length;
    const lastActivity = session.updatedAt || session.createdAt || new Date().toISOString();
    
    // Calculate approximate duration based on message timestamps
    const firstMessage = session.messages[0];
    const lastMessage = session.messages[session.messages.length - 1];
    let duration = '0 דק';
    
    if (firstMessage && lastMessage && session.messages.length > 1) {
      const start = new Date(firstMessage.timestamp || session.createdAt || 0);
      const end = new Date(lastMessage.timestamp || session.updatedAt || 0);
      const diffMinutes = Math.floor((end.getTime() - start.getTime()) / (1000 * 60));
      duration = diffMinutes > 0 ? `${diffMinutes} דק` : '< 1 דק';
    }
    
    // Calculate popularity score based on messages and recency
    const daysSinceUpdate = (Date.now() - new Date(lastActivity).getTime()) / (1000 * 60 * 60 * 24);
    const popularity = Math.max(0, totalMessages * Math.exp(-daysSinceUpdate / 7));
    
    return {
      totalMessages,
      lastActivity,
      duration,
      popularity
    };
  }, []);

  // Get recent sessions (last 7 days)
  const recentSessions = useMemo(() => {
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    return sessions
      .filter(session => {
        const lastActivity = new Date(session.updatedAt || session.createdAt || 0);
        return lastActivity >= sevenDaysAgo && !session.isArchived;
      })
      .sort((a, b) => {
        const aTime = new Date(a.updatedAt || a.createdAt || 0).getTime();
        const bTime = new Date(b.updatedAt || b.createdAt || 0).getTime();
        return bTime - aTime;
      })
      .slice(0, 10);
  }, [sessions]);

  // Get popular sessions based on activity
  const popularSessions = useMemo(() => {
    return sessions
      .filter(session => !session.isArchived)
      .map(session => ({
        ...session,
        stats: getSessionStats(session)
      }))
      .sort((a, b) => b.stats.popularity - a.stats.popularity)
      .slice(0, 8);
  }, [sessions, getSessionStats]);

  // Sort sessions based on current criteria
  const sortedSessions = useMemo(() => {
    let sorted = [...sessions].filter(session => !session.isArchived);
    
    switch (sortBy) {
      case 'recent':
        sorted.sort((a, b) => {
          const aTime = new Date(a.updatedAt || a.createdAt || 0).getTime();
          const bTime = new Date(b.updatedAt || b.createdAt || 0).getTime();
          return sortOrder === 'desc' ? bTime - aTime : aTime - bTime;
        });
        break;
      case 'popular':
        sorted.sort((a, b) => {
          const aStats = getSessionStats(a);
          const bStats = getSessionStats(b);
          return sortOrder === 'desc' ? 
            bStats.popularity - aStats.popularity : 
            aStats.popularity - bStats.popularity;
        });
        break;
      case 'messages':
        sorted.sort((a, b) => {
          return sortOrder === 'desc' ? 
            b.messages.length - a.messages.length : 
            a.messages.length - b.messages.length;
        });
        break;
      case 'alphabetical':
        sorted.sort((a, b) => {
          return sortOrder === 'desc' ? 
            b.title.localeCompare(a.title, 'he') : 
            a.title.localeCompare(b.title, 'he');
        });
        break;
    }
    
    // Always show pinned sessions first
    const pinned = sorted.filter(s => pinnedSessions.has(s.id));
    const unpinned = sorted.filter(s => !pinnedSessions.has(s.id));
    
    return [...pinned, ...unpinned];
  }, [sessions, sortBy, sortOrder, getSessionStats, pinnedSessions]);

  const handleSessionClick = (sessionId: string) => {
    setActiveSession(sessionId);
    onSessionSelect?.(sessionId);
  };

  const togglePin = (sessionId: string) => {
    const newPinned = new Set(pinnedSessions);
    if (newPinned.has(sessionId)) {
      newPinned.delete(sessionId);
    } else {
      newPinned.add(sessionId);
    }
    setPinnedSessions(newPinned);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return 'עכשיו';
    } else if (diffInHours < 24) {
      return `לפני ${Math.floor(diffInHours)} שעות`;
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString('he-IL', { weekday: 'short' });
    } else {
      return date.toLocaleDateString('he-IL', { 
        day: '2-digit', 
        month: '2-digit' 
      });
    }
  };

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, sessionId: string) => {
    setDraggedItem({ id: sessionId, type: 'session' });
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, targetSessionId: string) => {
    e.preventDefault();
    
    if (draggedItem && draggedItem.id !== targetSessionId) {
      // Here you could implement session reordering logic
      // For now, we'll just pin the dragged session
      togglePin(draggedItem.id);
    }
    
    setDraggedItem(null);
  };

  const renderSessionCard = (session: any, showStats = false) => {
    const stats = getSessionStats(session);
    const isPinned = pinnedSessions.has(session.id);
    
    return (
      <Card
        key={session.id}
        className={`cursor-pointer transition-all hover:shadow-md ${
          activeSessionId === session.id ? 'ring-2 ring-primary' : ''
        } ${isPinned ? 'border-primary/50' : ''}`}
        draggable
        onDragStart={(e) => handleDragStart(e, session.id)}
        onDragOver={handleDragOver}
        onDrop={(e) => handleDrop(e, session.id)}
        onClick={() => handleSessionClick(session.id)}
      >
        <CardContent className="p-3">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-2 flex-1 min-w-0">
              <GripVertical className="h-4 w-4 text-muted-foreground mt-1 cursor-grab" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium truncate">{session.title}</h3>
                  {isPinned && (
                    <Pin className="h-3 w-3 text-primary" />
                  )}
                </div>
                
                <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
                  <div className="flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" />
                    {stats.totalMessages}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDate(stats.lastActivity)}
                  </div>
                  {showStats && (
                    <div className="flex items-center gap-1">
                      <BarChart3 className="h-3 w-3" />
                      {stats.duration}
                    </div>
                  )}
                </div>

                {/* Last message preview */}
                {session.messages.length > 0 && (
                  <p className="text-xs text-muted-foreground truncate">
                    {session.messages[session.messages.length - 1].text}
                  </p>
                )}
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                togglePin(session.id);
              }}
            >
              {isPinned ? (
                <PinOff className="h-3 w-3" />
              ) : (
                <Pin className="h-3 w-3" />
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className={`history-panel ${className}`}>
      <Tabs defaultValue="recent" className="h-full">
        <div className="flex items-center justify-between mb-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="recent" className="text-xs">
              <Clock className="h-3 w-3 mr-1" />
              אחרונות
            </TabsTrigger>
            <TabsTrigger value="popular" className="text-xs">
              <TrendingUp className="h-3 w-3 mr-1" />
              פופולריות
            </TabsTrigger>
            <TabsTrigger value="all" className="text-xs">
              <BarChart3 className="h-3 w-3 mr-1" />
              הכל
            </TabsTrigger>
          </TabsList>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <Filter className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setSortBy('recent')}>
                <Calendar className="h-4 w-4 mr-2" />
                לפי זמן
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortBy('popular')}>
                <Star className="h-4 w-4 mr-2" />
                לפי פופולריות
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortBy('messages')}>
                <MessageSquare className="h-4 w-4 mr-2" />
                לפי הודעות
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortBy('alphabetical')}>
                <SortAsc className="h-4 w-4 mr-2" />
                אלפביתי
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}>
                {sortOrder === 'asc' ? (
                  <SortDesc className="h-4 w-4 mr-2" />
                ) : (
                  <SortAsc className="h-4 w-4 mr-2" />
                )}
                {sortOrder === 'asc' ? 'יורד' : 'עולה'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <TabsContent value="recent" className="space-y-2 mt-0">
          <div className="mb-3">
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              שיחות אחרונות (7 ימים)
            </h3>
            {recentSessions.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground text-sm">
                אין שיחות אחרונות
              </div>
            ) : (
              <div className="space-y-2">
                {recentSessions.map((session) => renderSessionCard(session))}
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="popular" className="space-y-2 mt-0">
          <div className="mb-3">
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              שיחות פופולריות
            </h3>
            {popularSessions.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground text-sm">
                אין שיחות פופולריות
              </div>
            ) : (
              <div className="space-y-2">
                {popularSessions.map((session) => renderSessionCard(session, true))}
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="all" className="space-y-2 mt-0">
          <div className="mb-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">
                כל השיחות ({sortedSessions.length})
              </h3>
              <Badge variant="secondary" className="text-xs">
                {sortBy === 'recent' && 'לפי זמן'}
                {sortBy === 'popular' && 'לפי פופולריות'}
                {sortBy === 'messages' && 'לפי הודעות'}
                {sortBy === 'alphabetical' && 'אלפביתי'}
              </Badge>
            </div>
            
            {sortedSessions.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground text-sm">
                אין שיחות
              </div>
            ) : (
              <div className="space-y-2">
                {sortedSessions.map((session) => renderSessionCard(session, true))}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};import React, { useState, useMemo, useCallback } from 'react';
import { 
  Clock, 
  Star, 
  TrendingUp, 
  Calendar, 
  MessageSquare, 
  Archive,
  MoreHorizontal,
  Pin,
  PinOff,
  BarChart3,
  Filter
} from 'lucide-react';
import { useChatStore } from '@/stores/chat-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

interface HistoryPanelProps {
  onSessionSelect?: (sessionId: string) => void;
  className?: string;
}

interface SessionWithStats {
  id: string;
  title: string;
  messages: any[];
  createdAt?: string;
  updatedAt?: string;
  isArchived?: boolean;
  metadata?: Record<string, any>;
  isPinned?: boolean;
  messageCount: number;
  lastActivity: Date;
  popularity: number; // Based on message count and recent activity
}

export const HistoryPanel: React.FC<HistoryPanelProps> = ({
  onSessionSelect,
  className = ''
}) => {
  const {
    sessions,
    activeSessionId,
    setActiveSession,
    updateSession
  } = useChatStore();

  const [draggedSession, setDraggedSession] = useState<string | null>(null);
  const [dragOverSession, setDragOverSession] = useState<string | null>(null);
  const [showStats, setShowStats] = useState(false);

  // Enhanced sessions with statistics
  const sessionsWithStats = useMemo((): SessionWithStats[] => {
    return sessions.map(session => {
      const messageCount = session.messages.length;
      const lastActivity = new Date(session.updatedAt || session.createdAt || Date.now());
      const daysSinceLastActivity = (Date.now() - lastActivity.getTime()) / (1000 * 60 * 60 * 24);
      
      // Calculate popularity score based on message count and recency
      const popularity = messageCount * Math.max(0, 10 - daysSinceLastActivity);
      
      return {
        ...session,
        messageCount,
        lastActivity,
        popularity,
        isPinned: session.metadata?.isPinned || false
      };
    });
  }, [sessions]);

  // Recent sessions (last 7 days, sorted by last activity)
  const recentSessions = useMemo(() => {
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    return sessionsWithStats
      .filter(session => 
        !session.isArchived && 
        session.lastActivity > sevenDaysAgo
      )
      .sort((a, b) => b.lastActivity.getTime() - a.lastActivity.getTime())
      .slice(0, 10);
  }, [sessionsWithStats]);

  // Popular sessions (sorted by popularity score)
  const popularSessions = useMemo(() => {
    return sessionsWithStats
      .filter(session => !session.isArchived && session.messageCount > 0)
      .sort((a, b) => b.popularity - a.popularity)
      .slice(0, 8);
  }, [sessionsWithStats]);

  // Pinned sessions
  const pinnedSessions = useMemo(() => {
    return sessionsWithStats
      .filter(session => session.isPinned && !session.isArchived)
      .sort((a, b) => b.lastActivity.getTime() - a.lastActivity.getTime());
  }, [sessionsWithStats]);

  // Statistics
  const stats = useMemo(() => {
    const totalSessions = sessions.length;
    const activeSessions = sessions.filter(s => !s.isArchived).length;
    const archivedSessions = sessions.filter(s => s.isArchived).length;
    const totalMessages = sessions.reduce((sum, s) => sum + s.messages.length, 0);
    const avgMessagesPerSession = totalSessions > 0 ? Math.round(totalMessages / totalSessions) : 0;
    
    return {
      totalSessions,
      activeSessions,
      archivedSessions,
      totalMessages,
      avgMessagesPerSession
    };
  }, [sessions]);

  const handleSessionClick = useCallback((sessionId: string) => {
    setActiveSession(sessionId);
    onSessionSelect?.(sessionId);
  }, [setActiveSession, onSessionSelect]);

  const handlePinToggle = useCallback((sessionId: string, isPinned: boolean) => {
    updateSession(sessionId, {
      metadata: { isPinned: !isPinned }
    });
  }, [updateSession]);

  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return 'עכשיו';
    } else if (diffInHours < 24) {
      return `לפני ${Math.floor(diffInHours)} שעות`;
    } else if (diffInHours < 24 * 7) {
      const days = Math.floor(diffInHours / 24);
      return `לפני ${days} ימים`;
    } else {
      return date.toLocaleDateString('he-IL', { 
        day: '2-digit', 
        month: '2-digit' 
      });
    }
  };

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, sessionId: string) => {
    setDraggedSession(sessionId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, sessionId: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverSession(sessionId);
  };

  const handleDragLeave = () => {
    setDragOverSession(null);
  };

  const handleDrop = (e: React.DragEvent, targetSessionId: string) => {
    e.preventDefault();
    setDragOverSession(null);
    
    if (draggedSession && draggedSession !== targetSessionId) {
      // Here you could implement session reordering logic
      // For now, we'll just clear the drag state
      console.log(`Moving session ${draggedSession} to position of ${targetSessionId}`);
    }
    
    setDraggedSession(null);
  };

  const SessionItem: React.FC<{ session: SessionWithStats; showPopularity?: boolean }> = ({ 
    session, 
    showPopularity = false 
  }) => (
    <Card
      key={session.id}
      className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
        activeSessionId === session.id ? 'ring-2 ring-primary bg-primary/5' : ''
      } ${
        dragOverSession === session.id ? 'ring-2 ring-blue-400 bg-blue-50' : ''
      }`}
      draggable
      onDragStart={(e) => handleDragStart(e, session.id)}
      onDragOver={(e) => handleDragOver(e, session.id)}
      onDragLeave={handleDragLeave}
      onDrop={(e) => handleDrop(e, session.id)}
      onClick={() => handleSessionClick(session.id)}
    >
      <CardContent className="p-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-medium text-sm truncate">{session.title}</h4>
              {session.isPinned && (
                <Pin className="h-3 w-3 text-primary" />
              )}
              {showPopularity && session.popularity > 50 && (
                <Badge variant="secondary" className="text-xs">
                  <TrendingUp className="h-2 w-2 mr-1" />
                  פופולרי
                </Badge>
              )}
            </div>
            
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <MessageSquare className="h-3 w-3" />
                {session.messageCount}
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formatRelativeTime(session.lastActivity)}
              </div>
            </div>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreHorizontal className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem 
                onClick={(e) => {
                  e.stopPropagation();
                  handlePinToggle(session.id, session.isPinned);
                }}
              >
                {session.isPinned ? (
                  <>
                    <PinOff className="h-4 w-4 mr-2" />
                    ביטול נעיצה
                  </>
                ) : (
                  <>
                    <Pin className="h-4 w-4 mr-2" />
                    נעיצה
                  </>
                )}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className={`history-panel w-80 border-r bg-background/50 ${className}`}>
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">היסטוריית שיחות</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowStats(!showStats)}
          >
            <BarChart3 className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Statistics Panel */}
        <Collapsible open={showStats} onOpenChange={setShowStats}>
          <CollapsibleContent>
            <Card className="mb-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">סטטיסטיקות</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="text-center p-2 bg-muted rounded">
                    <div className="font-semibold">{stats.totalSessions}</div>
                    <div className="text-muted-foreground">שיחות</div>
                  </div>
                  <div className="text-center p-2 bg-muted rounded">
                    <div className="font-semibold">{stats.totalMessages}</div>
                    <div className="text-muted-foreground">הודעות</div>
                  </div>
                  <div className="text-center p-2 bg-muted rounded">
                    <div className="font-semibold">{stats.activeSessions}</div>
                    <div className="text-muted-foreground">פעילות</div>
                  </div>
                  <div className="text-center p-2 bg-muted rounded">
                    <div className="font-semibold">{stats.avgMessagesPerSession}</div>
                    <div className="text-muted-foreground">ממוצע</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </CollapsibleContent>
        </Collapsible>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4">
          <Tabs defaultValue="recent" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="recent" className="text-xs">
                <Clock className="h-3 w-3 mr-1" />
                אחרונות
              </TabsTrigger>
              <TabsTrigger value="popular" className="text-xs">
                <Star className="h-3 w-3 mr-1" />
                פופולריות
              </TabsTrigger>
              <TabsTrigger value="pinned" className="text-xs">
                <Pin className="h-3 w-3 mr-1" />
                נעוצות
              </TabsTrigger>
            </TabsList>

            <TabsContent value="recent" className="mt-4">
              <div className="space-y-2">
                {recentSessions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    אין שיחות אחרונות
                  </div>
                ) : (
                  recentSessions.map((session) => (
                    <SessionItem key={session.id} session={session} />
                  ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="popular" className="mt-4">
              <div className="space-y-2">
                {popularSessions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    אין שיחות פופולריות
                  </div>
                ) : (
                  popularSessions.map((session) => (
                    <SessionItem 
                      key={session.id} 
                      session={session} 
                      showPopularity={true}
                    />
                  ))
                )}
              </div>
            </TabsContent>

            <TabsContent value="pinned" className="mt-4">
              <div className="space-y-2">
                {pinnedSessions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    אין שיחות נעוצות
                  </div>
                ) : (
                  pinnedSessions.map((session) => (
                    <SessionItem key={session.id} session={session} />
                  ))
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </ScrollArea>
    </div>
  );
};