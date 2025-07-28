import React, { useState, useCallback, useEffect } from 'react';
import { AudioEditPreview } from './audio-edit-preview';
import { AudioEditHistory, EditHistoryItem } from './audio-edit-history';
import { useAudioEditHistory } from '../../hooks/use-audio-edit-history';
import { 
  Play, 
  Pause, 
  Save, 
  Upload, 
  Settings, 
  AlertCircle,
  CheckCircle,
  Loader
} from 'lucide-react';

interface InteractiveAudioEditorProps {
  initialFile?: string;
  onSaveFile?: (file: string) => void;
  onFileChange?: (file: string) => void;
}

interface EditOperation {
  type: string;
  params: Record<string, any>;
  description: string;
}

interface ProcessingState {
  isProcessing: boolean;
  operation?: string;
  progress?: number;
  error?: string;
}

export const InteractiveAudioEditor: React.FC<InteractiveAudioEditorProps> = ({
  initialFile,
  onSaveFile,
  onFileChange
}) => {
  const [currentFile, setCurrentFile] = useState<string | undefined>(initialFile);
  const [previewFile, setPreviewFile] = useState<string | undefined>();
  const [currentOperation, setCurrentOperation] = useState<EditOperation | undefined>();
  const [processingState, setProcessingState] = useState<ProcessingState>({
    isProcessing: false
  });
  const [showHistory, setShowHistory] = useState(false);

  const {
    history,
    currentIndex,
    canUndo,
    canRedo,
    addEdit,
    undo,
    redo,
    jumpTo,
    clearHistory,
    getCurrentEdit
  } = useAudioEditHistory();

  // עדכון קובץ נוכחי כאשר משתנה הקובץ הראשוני
  useEffect(() => {
    if (initialFile && initialFile !== currentFile) {
      setCurrentFile(initialFile);
      setPreviewFile(undefined);
      setCurrentOperation(undefined);
    }
  }, [initialFile, currentFile]);

  // פונקציה לביצוע עריכת אודיו
  const executeEdit = useCallback(async (operation: EditOperation) => {
    if (!currentFile) return;

    setProcessingState({
      isProcessing: true,
      operation: operation.description,
      progress: 0
    });

    try {
      // כאן נקרא לשירות העריכה בפועל
      const response = await fetch('/api/audio/execute-command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          input_file: currentFile,
          operation: operation.type,
          params: operation.params
        })
      });

      if (!response.ok) {
        throw new Error(`שגיאה בעיבוד: ${response.statusText}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'שגיאה לא ידועה בעיבוד');
      }

      // עדכון תצוגה מקדימה
      setPreviewFile(result.output_file);
      setCurrentOperation(operation);

      // הוספה להיסטוריה
      addEdit({
        operation: operation.type,
        params: operation.params,
        inputFile: currentFile,
        outputFile: result.output_file,
        processingTime: result.processing_time * 1000, // המרה לmilliseconds
        description: operation.description
      });

      setProcessingState({
        isProcessing: false
      });

    } catch (error) {
      console.error('Error executing edit:', error);
      setProcessingState({
        isProcessing: false,
        error: error instanceof Error ? error.message : 'שגיאה לא ידועה'
      });
    }
  }, [currentFile, addEdit]);

  // שמירת שינויים
  const handleSaveChanges = useCallback((file: string) => {
    setCurrentFile(file);
    setPreviewFile(undefined);
    setCurrentOperation(undefined);
    onSaveFile?.(file);
    onFileChange?.(file);
  }, [onSaveFile, onFileChange]);

  // ביטול שינויים
  const handleDiscardChanges = useCallback(() => {
    setPreviewFile(undefined);
    setCurrentOperation(undefined);
  }, []);

  // ביטול פעולה
  const handleUndo = useCallback(() => {
    const previousEdit = undo();
    if (previousEdit) {
      setCurrentFile(previousEdit.inputFile);
      setPreviewFile(undefined);
      setCurrentOperation(undefined);
      onFileChange?.(previousEdit.inputFile);
    }
  }, [undo, onFileChange]);

  // חזרה על פעולה
  const handleRedo = useCallback(() => {
    const nextEdit = redo();
    if (nextEdit) {
      setCurrentFile(nextEdit.outputFile);
      setPreviewFile(undefined);
      setCurrentOperation(undefined);
      onFileChange?.(nextEdit.outputFile);
    }
  }, [redo, onFileChange]);

  // קפיצה לנקודה בהיסטוריה
  const handleJumpTo = useCallback((index: number) => {
    const edit = jumpTo(index);
    if (edit) {
      setCurrentFile(edit.outputFile);
      setPreviewFile(undefined);
      setCurrentOperation(undefined);
      onFileChange?.(edit.outputFile);
    }
  }, [jumpTo, onFileChange]);

  // פונקציות עריכה מהירות
  const quickEdits = [
    {
      name: 'נורמליזציה',
      operation: {
        type: 'normalize_audio',
        params: { target_level_db: -3.0, normalization_type: 'peak' },
        description: 'נורמליזציה: -3dB (peak)'
      }
    },
    {
      name: 'הפחתת רעש',
      operation: {
        type: 'reduce_noise',
        params: { reduction_amount: 0.5, noise_type: 'auto' },
        description: 'הפחתת רעש: 50%'
      }
    },
    {
      name: 'הסרת שקט',
      operation: {
        type: 'remove_silence',
        params: { 
          silence_threshold_db: -40.0, 
          min_silence_duration: 1.0,
          keep_silence: 0.1 
        },
        description: 'הסרת שקט: סף -40dB'
      }
    }
  ];

  if (!currentFile) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">אין קובץ אודיו נבחר</h3>
        <p className="text-gray-600 mb-4">העלה קובץ אודיו כדי להתחיל לערוך</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* סטטוס עיבוד */}
      {processingState.isProcessing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <Loader className="w-5 h-5 text-blue-600 animate-spin" />
            <div>
              <div className="font-medium text-blue-900">מעבד...</div>
              <div className="text-sm text-blue-700">{processingState.operation}</div>
            </div>
          </div>
        </div>
      )}

      {/* שגיאות */}
      {processingState.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div>
              <div className="font-medium text-red-900">שגיאה בעיבוד</div>
              <div className="text-sm text-red-700">{processingState.error}</div>
            </div>
          </div>
        </div>
      )}

      {/* כפתורי עריכה מהירה */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-3">עריכה מהירה</h3>
        <div className="flex flex-wrap gap-2">
          {quickEdits.map((edit) => (
            <button
              key={edit.name}
              onClick={() => executeEdit(edit.operation)}
              disabled={processingState.isProcessing}
              className="px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {edit.name}
            </button>
          ))}
        </div>
      </div>

      {/* תצוגה מקדימה */}
      <AudioEditPreview
        originalFile={currentFile}
        editedFile={previewFile}
        editOperation={currentOperation?.type}
        editParams={currentOperation?.params}
        onSave={handleSaveChanges}
        onDiscard={handleDiscardChanges}
        onUndo={handleUndo}
        canUndo={canUndo}
      />

      {/* היסטוריה */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">היסטוריית עריכה</h3>
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          {showHistory ? 'הסתר' : 'הצג'} היסטוריה
        </button>
      </div>

      {showHistory && (
        <AudioEditHistory
          history={history}
          currentIndex={currentIndex}
          onUndo={handleUndo}
          onRedo={handleRedo}
          onJumpTo={handleJumpTo}
          onClearHistory={clearHistory}
          canUndo={canUndo}
          canRedo={canRedo}
        />
      )}

      {/* סטטיסטיקות */}
      {history.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{history.length}</div>
              <div className="text-sm text-gray-600">פעולות בוצעו</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{currentIndex + 1}</div>
              <div className="text-sm text-gray-600">מיקום נוכחי</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {history.reduce((sum, edit) => sum + edit.processingTime, 0) / 1000}s
              </div>
              <div className="text-sm text-gray-600">זמן עיבוד כולל</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};