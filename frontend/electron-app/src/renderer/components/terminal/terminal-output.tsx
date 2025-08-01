import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Trash2, 
  Search, 
  Filter, 
  Copy,
  Download,
  Terminal as TerminalIcon
} from 'lucide-react';
import { TerminalLog } from '@/types/ipc';

interface TerminalOutputProps {
  logs: TerminalLog[];
  onClear: () => void;
}

export const TerminalOutput: React.FC<TerminalOutputProps> = ({ logs, onClear }) => {
  const [filter, setFilter] = useState<string>('');
  const [serviceFilter, setServiceFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const outputRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  // Check if user scrolled up to disable auto-scroll
  const handleScroll = () => {
    if (outputRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = outputRef.current;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
      setAutoScroll(isAtBottom);
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesText = filter === '' || 
      log.message.toLowerCase().includes(filter.toLowerCase()) ||
      log.service.toLowerCase().includes(filter.toLowerCase());
    
    const matchesService = serviceFilter === 'all' || log.service === serviceFilter;
    const matchesType = typeFilter === 'all' || log.type === typeFilter;
    
    return matchesText && matchesService && matchesType;
  });

  const getLogTypeColor = (type: TerminalLog['type']) => {
    switch (type) {
      case 'error':
        return 'text-red-500 dark:text-red-400';
      case 'warning':
        return 'text-yellow-500 dark:text-yellow-400';
      case 'success':
        return 'text-green-500 dark:text-green-400';
      case 'info':
      default:
        return 'text-blue-500 dark:text-blue-400';
    }
  };

  const getServiceColor = (service: string) => {
    switch (service) {
      case 'backend':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'frontend':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'admin':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'system':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const copyToClipboard = () => {
    const logText = filteredLogs
      .map(log => `[${log.timestamp.toLocaleTimeString()}] [${log.service}] [${log.type}] ${log.message}`)
      .join('\n');
    navigator.clipboard.writeText(logText);
  };

  const downloadLogs = () => {
    const logText = filteredLogs
      .map(log => `[${log.timestamp.toLocaleTimeString()}] [${log.service}] [${log.type}] ${log.message}`)
      .join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `terminal-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const uniqueServices = Array.from(new Set(logs.map(log => log.service)));
  const logTypes = ['info', 'success', 'warning', 'error'];

  return (
    <Card className="flex-1 flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TerminalIcon className="h-5 w-5" />
            <span>Terminal Output</span>
            <Badge variant="outline" className="text-xs">
              {filteredLogs.length} / {logs.length} logs
            </Badge>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={copyToClipboard}
              className="flex items-center space-x-1"
            >
              <Copy className="h-3 w-3" />
              <span>Copy</span>
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={downloadLogs}
              className="flex items-center space-x-1"
            >
              <Download className="h-3 w-3" />
              <span>Download</span>
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={onClear}
              className="flex items-center space-x-1"
            >
              <Trash2 className="h-3 w-3" />
              <span>Clear</span>
            </Button>
          </div>
        </CardTitle>
        
        {/* Filters */}
        <div className="flex items-center space-x-2 pt-2">
          <div className="flex items-center space-x-1">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search logs..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-48 h-8"
            />
          </div>
          
          <select
            value={serviceFilter}
            onChange={(e) => setServiceFilter(e.target.value)}
            className="h-8 px-2 border border-input bg-background rounded text-sm"
          >
            <option value="all">All Services</option>
            {uniqueServices.map(service => (
              <option key={service} value={service}>{service}</option>
            ))}
          </select>
          
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="h-8 px-2 border border-input bg-background rounded text-sm"
          >
            <option value="all">All Types</option>
            {logTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col p-0">
        <div 
          ref={outputRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto p-4 bg-gray-50 dark:bg-gray-900 font-mono text-sm"
          style={{ maxHeight: '400px' }}
        >
          {filteredLogs.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              {logs.length === 0 ? 'No logs yet...' : 'No logs match your filters'}
            </div>
          ) : (
            filteredLogs.map((log, index) => (
              <div key={index} className="flex items-start space-x-2 py-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded px-2 -mx-2">
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {log.timestamp.toLocaleTimeString()}
                </span>
                <Badge 
                  variant="outline" 
                  className={`text-xs ${getServiceColor(log.service)} border-0`}
                >
                  {log.service}
                </Badge>
                <span className={`text-xs font-medium ${getLogTypeColor(log.type)} uppercase`}>
                  {log.type}
                </span>
                <span className="flex-1 text-sm break-words">
                  {log.message}
                </span>
              </div>
            ))
          )}
          <div ref={endRef} />
        </div>
        
        {/* Auto-scroll indicator */}
        {!autoScroll && (
          <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 border-t">
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setAutoScroll(true);
                endRef.current?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="w-full text-xs"
            >
              Auto-scroll disabled. Click to scroll to bottom.
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};