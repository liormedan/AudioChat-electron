import React, { useState, useMemo } from 'react';
import { Search, Plus, MoreVertical, Archive, Trash2, Edit3, Calendar, MessageSquare } from 'lucide-react';
import { useChatStore } from '@/stores/chat-store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';

interface SessionManagerProps {
  onSessionSelect?: (sessionId: string) => void | undefined;
  className?: string;
}

export const SessionManager: React.FC<SessionManagerProps> = ({
  onSessionSelect,
  className = ''
}) => {
  const {
    sessions,
    activeSessionId,
    createSession,
    setActiveSession,
    deleteSession,
    updateSession,
    archiveSession
  } = useChatStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'active' | 'archived'>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [newSessionTitle, setNewSessionTitle] = useState('');
  const [editSessionTitle, setEditSessionTitle] = useState('');

  // Filter and search sessions
  const filteredSessions = useMemo(() => {
    return sessions.filter(session => {
      // Filter by type
      if (filterType === 'archived' && !session.isArchived) return false;
      if (filterType === 'active' && session.isArchived) return false;

      // Filter by search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          session.title.toLowerCase().includes(query) ||
          session.messages.some(msg => 
            msg.text.toLowerCase().includes(query)
          )
        );
      }

      return true;
    }).sort((a, b) => {
      // Sort by last updated (most recent first)
      return new Date(b.updatedAt || b.createdAt || 0).getTime() - 
             new Date(a.updatedAt || a.createdAt || 0).getTime();
    });
  }, [sessions, searchQuery, filterType]);

  const handleCreateSession = () => {
    if (newSessionTitle.trim()) {
      const sessionId = createSession(newSessionTitle.trim());
      setNewSessionTitle('');
      setIsCreateDialogOpen(false);
      onSessionSelect?.(sessionId);
    }
  };

  const handleEditSession = () => {
    if (selectedSessionId && editSessionTitle.trim()) {
      updateSession(selectedSessionId, { title: editSessionTitle.trim() });
      setEditSessionTitle('');
      setIsEditDialogOpen(false);
      setSelectedSessionId(null);
    }
  };

  const handleDeleteSession = () => {
    if (selectedSessionId) {
      deleteSession(selectedSessionId);
      setIsDeleteDialogOpen(false);
      setSelectedSessionId(null);
    }
  };

  const handleSessionClick = (sessionId: string) => {
    setActiveSession(sessionId);
    onSessionSelect?.(sessionId);
  };

  const openEditDialog = (session: any) => {
    setSelectedSessionId(session.id);
    setEditSessionTitle(session.title);
    setIsEditDialogOpen(true);
  };

  const openDeleteDialog = (sessionId: string) => {
    setSelectedSessionId(sessionId);
    setIsDeleteDialogOpen(true);
  };

  const handleArchiveSession = (sessionId: string) => {
    archiveSession(sessionId);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('he-IL', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString('he-IL', { 
        weekday: 'short' 
      });
    } else {
      return date.toLocaleDateString('he-IL', { 
        day: '2-digit', 
        month: '2-digit' 
      });
    }
  };

  return (
    <div className={`session-manager ${className}`}>
      {/* Header with search and create button */}
      <div className="flex items-center gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            placeholder="חיפוש שיחות..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="shrink-0">
              <Plus className="h-4 w-4 mr-1" />
              שיחה חדשה
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>יצירת שיחה חדשה</DialogTitle>
              <DialogDescription>
                הזן כותרת לשיחה החדשה
              </DialogDescription>
            </DialogHeader>
            <Input
              placeholder="כותרת השיחה..."
              value={newSessionTitle}
              onChange={(e) => setNewSessionTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleCreateSession();
                }
              }}
            />
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                ביטול
              </Button>
              <Button onClick={handleCreateSession} disabled={!newSessionTitle.trim()}>
                יצירה
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 mb-4">
        <Button
          variant={filterType === 'all' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setFilterType('all')}
        >
          הכל ({sessions.length})
        </Button>
        <Button
          variant={filterType === 'active' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setFilterType('active')}
        >
          פעילות ({sessions.filter(s => !s.isArchived).length})
        </Button>
        <Button
          variant={filterType === 'archived' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setFilterType('archived')}
        >
          ארכיון ({sessions.filter(s => s.isArchived).length})
        </Button>
      </div>

      {/* Sessions list */}
      <div className="space-y-2">
        {filteredSessions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            {searchQuery ? 'לא נמצאו שיחות התואמות לחיפוש' : 'אין שיחות עדיין'}
          </div>
        ) : (
          filteredSessions.map((session) => (
            <Card
              key={session.id}
              className={`cursor-pointer transition-colors hover:bg-accent/50 ${
                activeSessionId === session.id ? 'ring-2 ring-primary' : ''
              }`}
              onClick={() => handleSessionClick(session.id)}
            >
              <CardContent className="p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium truncate">{session.title}</h3>
                      {session.isArchived && (
                        <Badge variant="secondary" className="text-xs">
                          <Archive className="h-3 w-3 mr-1" />
                          ארכיון
                        </Badge>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <MessageSquare className="h-3 w-3" />
                        {session.messages.length} הודעות
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(session.updatedAt || session.createdAt || new Date().toISOString())}
                      </div>
                    </div>

                    {/* Last message preview */}
                    {session.messages.length > 0 && (
                      <p className="text-sm text-muted-foreground mt-1 truncate">
                        {session.messages[session.messages.length - 1].text}
                      </p>
                    )}
                  </div>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => openEditDialog(session)}>
                        <Edit3 className="h-4 w-4 mr-2" />
                        עריכת כותרת
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={() => handleArchiveSession(session.id)}
                      >
                        <Archive className="h-4 w-4 mr-2" />
                        {session.isArchived ? 'שחזור מארכיון' : 'העברה לארכיון'}
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => openDeleteDialog(session.id)}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        מחיקה
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>עריכת כותרת השיחה</DialogTitle>
            <DialogDescription>
              שנה את כותרת השיחה
            </DialogDescription>
          </DialogHeader>
          <Input
            placeholder="כותרת השיחה..."
            value={editSessionTitle}
            onChange={(e) => setEditSessionTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleEditSession();
              }
            }}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              ביטול
            </Button>
            <Button onClick={handleEditSession} disabled={!editSessionTitle.trim()}>
              שמירה
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>מחיקת שיחה</DialogTitle>
            <DialogDescription>
              האם אתה בטוח שברצונך למחוק את השיחה? פעולה זו לא ניתנת לביטול.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              ביטול
            </Button>
            <Button variant="destructive" onClick={handleDeleteSession}>
              מחיקה
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};