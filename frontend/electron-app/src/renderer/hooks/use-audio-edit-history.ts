import { useState, useCallback, useRef } from 'react';
import { EditHistoryItem } from '../components/audio/audio-edit-history';

interface UseAudioEditHistoryReturn {
  history: EditHistoryItem[];
  currentIndex: number;
  canUndo: boolean;
  canRedo: boolean;
  addEdit: (edit: Omit<EditHistoryItem, 'id' | 'timestamp'>) => void;
  undo: () => EditHistoryItem | null;
  redo: () => EditHistoryItem | null;
  jumpTo: (index: number) => EditHistoryItem | null;
  clearHistory: () => void;
  getCurrentEdit: () => EditHistoryItem | null;
  getEditAt: (index: number) => EditHistoryItem | null;
}

export const useAudioEditHistory = (maxHistorySize: number = 50): UseAudioEditHistoryReturn => {
  const [history, setHistory] = useState<EditHistoryItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const idCounter = useRef(0);

  // יצירת ID ייחודי
  const generateId = useCallback(() => {
    idCounter.current += 1;
    return `edit_${Date.now()}_${idCounter.current}`;
  }, []);

  // הוספת עריכה חדשה
  const addEdit = useCallback((edit: Omit<EditHistoryItem, 'id' | 'timestamp'>) => {
    const newEdit: EditHistoryItem = {
      ...edit,
      id: generateId(),
      timestamp: new Date()
    };

    setHistory(prevHistory => {
      // אם אנחנו לא בסוף ההיסטוריה, נמחק את כל מה שאחרי הנקודה הנוכחית
      const newHistory = prevHistory.slice(0, currentIndex + 1);
      
      // הוספת העריכה החדשה
      newHistory.push(newEdit);
      
      // שמירה על גודל מקסימלי של ההיסטוריה
      if (newHistory.length > maxHistorySize) {
        return newHistory.slice(-maxHistorySize);
      }
      
      return newHistory;
    });

    setCurrentIndex(prevIndex => {
      const newHistoryLength = Math.min(history.length + 1, maxHistorySize);
      return newHistoryLength - 1;
    });
  }, [currentIndex, generateId, history.length, maxHistorySize]);

  // ביטול פעולה אחרונה
  const undo = useCallback((): EditHistoryItem | null => {
    if (currentIndex <= 0) return null;

    const newIndex = currentIndex - 1;
    setCurrentIndex(newIndex);
    return history[newIndex] || null;
  }, [currentIndex, history]);

  // חזרה על פעולה
  const redo = useCallback((): EditHistoryItem | null => {
    if (currentIndex >= history.length - 1) return null;

    const newIndex = currentIndex + 1;
    setCurrentIndex(newIndex);
    return history[newIndex] || null;
  }, [currentIndex, history]);

  // קפיצה לנקודה מסוימת בהיסטוריה
  const jumpTo = useCallback((index: number): EditHistoryItem | null => {
    if (index < 0 || index >= history.length) return null;

    setCurrentIndex(index);
    return history[index] || null;
  }, [history]);

  // ניקוי היסטוריה
  const clearHistory = useCallback(() => {
    setHistory([]);
    setCurrentIndex(-1);
  }, []);

  // קבלת העריכה הנוכחית
  const getCurrentEdit = useCallback((): EditHistoryItem | null => {
    if (currentIndex < 0 || currentIndex >= history.length) return null;
    return history[currentIndex];
  }, [currentIndex, history]);

  // קבלת עריכה במיקום מסוים
  const getEditAt = useCallback((index: number): EditHistoryItem | null => {
    if (index < 0 || index >= history.length) return null;
    return history[index];
  }, [history]);

  // בדיקת יכולת ביטול וחזרה
  const canUndo = currentIndex > 0;
  const canRedo = currentIndex < history.length - 1;

  return {
    history,
    currentIndex,
    canUndo,
    canRedo,
    addEdit,
    undo,
    redo,
    jumpTo,
    clearHistory,
    getCurrentEdit,
    getEditAt
  };
};