import React, { useState } from 'react';
import { 
  History, 
  RotateCcw, 
  RotateCw, 
  Trash2, 
  Clock, 
  Scissors, 
  Volume2, 
  Zap,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export interface EditHistoryItem {
  id: string;
  timestamp: Date;
  operation: string;
  params: Record<string, any>;
  inputFile: string;
  outputFile: string;
  processingTime: number;
  description: string;
}

interface AudioEditHistoryProps {
  history: EditHistoryItem[];
  currentIndex: number;
  onUndo: () => void;
  onRedo: () => void;
  onJumpTo: (index: number) => void;
  onClearHistory: () => void;
  canUndo: boolean;
  canRedo: boolean;
}

export const AudioEditHistory: React.FC<AudioEditHistoryProps> = ({
  history,
  currentIndex,
  onUndo,
  redo,
  onJumpTo,
  onClearHistory,
  canUndo,
  canRedo
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDetails, setShowDetails] = useState<string | null>(null);

  const getOperationIcon = (operation: string) => {
    switch (operation) {
      case 'trim_audio':
        return <Scissors className="w-4 h-4" />;
      case 'adjust_volume':
        return <Volume2 className="w-4 h-4" />;
      case 'apply_fade':
      case 'normalize_audio':
      case 'reduce_noise':
      case 'combine_audio_files':
        return <Zap className="w-4 h-4" />;
      default:
        return <Zap className="w-4 h-4" />;
    }
  };

  const getOperationColor = (operation: string) => {
    switch (operation) {
      case 'trim_audio':
        return 'text-blue-600 bg-blue-50';
      case 'adjust_volume':
        return 'text-purple-600 bg-purple-50';
      case 'apply_fade':
        return 'text-green-600 bg-green-50';
      case 'normalize_audio':
        return 'text-orange-600 bg-orange-50';
      case 'reduce_noise':
        return 'text-red-600 bg-red-50';
      case 'combine_audio_files':
        return 'text-indigo-600 bg-indigo-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('he-IL', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatProcessingTime = (ms: number): string => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  if (history.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <History className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <div className="text-gray-500 mb-1">אין היסטוריית עריכה</div>
        <div className="text-sm text-gray-400">פעולות העריכה שלך יופיעו כאן</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {/* כותרת וכפתורי פעולה */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <History className="w-5 h-5 text-gray-600" />
          <div>
            <h3 className="font-semibold text-gray-900">היסטוריית עריכה</h3>
            <p className="text-sm text-gray-500">
              {history.length} פעולות • נוכחי: {currentIndex + 1}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onUndo}
            disabled={!canUndo}
            className={`flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors ${
              canUndo
                ? 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                : 'bg-gray-50 text-gray-400 cursor-not-allowed'
            }`}
          >
            <RotateCcw className="w-4 h-4" />
            ביטול
          </button>

          <button
            onClick={onRedo}
            disabled={!canRedo}
            className={`flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors ${
              canRedo
                ? 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                : 'bg-gray-50 text-gray-400 cursor-not-allowed'
            }`}
          >
            <RotateCw className="w-4 h-4" />
            חזרה
          </button>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
          >
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
            {isExpanded ? 'כווץ' : 'הרחב'}
          </button>

          {history.length > 0 && (
            <button
              onClick={onClearHistory}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              נקה
            </button>
          )}
        </div>
      </div>

      {/* רשימת היסטוריה */}
      {isExpanded && (
        <div className="max-h-96 overflow-y-auto">
          {history.map((item, index) => {
            const isActive = index === currentIndex;
            const isFuture = index > currentIndex;
            const colorClasses = getOperationColor(item.operation);

            return (
              <div
                key={item.id}
                className={`border-b border-gray-100 last:border-b-0 ${
                  isActive
                    ? 'bg-blue-50 border-blue-200'
                    : isFuture
                    ? 'bg-gray-50 opacity-60'
                    : 'bg-white hover:bg-gray-50'
                } transition-colors cursor-pointer`}
                onClick={() => onJumpTo(index)}
              >
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      {/* אייקון פעולה */}
                      <div className={`p-2 rounded-lg ${colorClasses}`}>
                        {getOperationIcon(item.operation)}
                      </div>

                      {/* פרטי הפעולה */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-gray-900 truncate">
                            {item.description}
                          </h4>
                          {isActive && (
                            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                              נוכחי
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatTime(item.timestamp)}
                          </div>
                          <div>
                            זמן עיבוד: {formatProcessingTime(item.processingTime)}
                          </div>
                        </div>

                        {/* פרטים נוספים */}
                        {showDetails === item.id && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg text-sm">
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <span className="font-medium">קובץ קלט:</span>
                                <div className="text-gray-600 truncate">
                                  {item.inputFile.split('/').pop()}
                                </div>
                              </div>
                              <div>
                                <span className="font-medium">קובץ פלט:</span>
                                <div className="text-gray-600 truncate">
                                  {item.outputFile.split('/').pop()}
                                </div>
                              </div>
                            </div>
                            
                            {Object.keys(item.params).length > 0 && (
                              <div className="mt-2">
                                <span className="font-medium">פרמטרים:</span>
                                <div className="text-gray-600 mt-1">
                                  {Object.entries(item.params).map(([key, value]) => (
                                    <div key={key} className="flex justify-between">
                                      <span>{key}:</span>
                                      <span>{String(value)}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* כפתור פרטים */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowDetails(showDetails === item.id ? null : item.id);
                      }}
                      className="text-gray-400 hover:text-gray-600 p-1"
                    >
                      {showDetails === item.id ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* סיכום מהיר */}
      {!isExpanded && history.length > 0 && (
        <div className="p-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>
              פעולה אחרונה: {history[currentIndex]?.description || 'אין'}
            </div>
            <div>
              {formatTime(history[currentIndex]?.timestamp || new Date())}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};