import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Save, X, Volume2, Scissors, Zap } from 'lucide-react';

interface AudioEditPreviewProps {
  originalFile?: string;
  editedFile?: string;
  editOperation?: string;
  editParams?: Record<string, any>;
  onSave?: (file: string) => void;
  onDiscard?: () => void;
  onUndo?: () => void;
  canUndo?: boolean;
}

interface AudioPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
}

export const AudioEditPreview: React.FC<AudioEditPreviewProps> = ({
  originalFile,
  editedFile,
  editOperation,
  editParams,
  onSave,
  onDiscard,
  onUndo,
  canUndo = false
}) => {
  const [originalPlayer, setOriginalPlayer] = useState<AudioPlayerState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0
  });
  
  const [editedPlayer, setEditedPlayer] = useState<AudioPlayerState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0
  });

  const originalAudioRef = useRef<HTMLAudioElement>(null);
  const editedAudioRef = useRef<HTMLAudioElement>(null);

  // עדכון זמן נגינה
  useEffect(() => {
    const updateTime = (audioRef: React.RefObject<HTMLAudioElement>, setter: React.Dispatch<React.SetStateAction<AudioPlayerState>>) => {
      const audio = audioRef.current;
      if (!audio) return;

      const handleTimeUpdate = () => {
        setter(prev => ({
          ...prev,
          currentTime: audio.currentTime,
          duration: audio.duration || 0
        }));
      };

      const handleLoadedMetadata = () => {
        setter(prev => ({
          ...prev,
          duration: audio.duration || 0
        }));
      };

      const handleEnded = () => {
        setter(prev => ({
          ...prev,
          isPlaying: false,
          currentTime: 0
        }));
      };

      audio.addEventListener('timeupdate', handleTimeUpdate);
      audio.addEventListener('loadedmetadata', handleLoadedMetadata);
      audio.addEventListener('ended', handleEnded);

      return () => {
        audio.removeEventListener('timeupdate', handleTimeUpdate);
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audio.removeEventListener('ended', handleEnded);
      };
    };

    const cleanupOriginal = updateTime(originalAudioRef, setOriginalPlayer);
    const cleanupEdited = updateTime(editedAudioRef, setEditedPlayer);

    return () => {
      cleanupOriginal?.();
      cleanupEdited?.();
    };
  }, [originalFile, editedFile]);

  const togglePlay = (type: 'original' | 'edited') => {
    const audioRef = type === 'original' ? originalAudioRef : editedAudioRef;
    const playerState = type === 'original' ? originalPlayer : editedPlayer;
    const setPlayerState = type === 'original' ? setOriginalPlayer : setEditedPlayer;
    const otherAudioRef = type === 'original' ? editedAudioRef : originalAudioRef;
    const setOtherPlayerState = type === 'original' ? setEditedPlayer : setOriginalPlayer;

    const audio = audioRef.current;
    const otherAudio = otherAudioRef.current;

    if (!audio) return;

    // עצירת הנגן השני
    if (otherAudio && !otherAudio.paused) {
      otherAudio.pause();
      setOtherPlayerState(prev => ({ ...prev, isPlaying: false }));
    }

    if (playerState.isPlaying) {
      audio.pause();
      setPlayerState(prev => ({ ...prev, isPlaying: false }));
    } else {
      audio.play();
      setPlayerState(prev => ({ ...prev, isPlaying: true }));
    }
  };

  const formatTime = (seconds: number): string => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getOperationIcon = (operation?: string) => {
    switch (operation) {
      case 'trim_audio':
        return <Scissors className="w-4 h-4" />;
      case 'adjust_volume':
        return <Volume2 className="w-4 h-4" />;
      case 'apply_fade':
      case 'normalize_audio':
      case 'reduce_noise':
        return <Zap className="w-4 h-4" />;
      default:
        return <Zap className="w-4 h-4" />;
    }
  };

  const getOperationDescription = (operation?: string, params?: Record<string, any>): string => {
    if (!operation || !params) return 'עריכת אודיו';

    switch (operation) {
      case 'trim_audio':
        return `חיתוך: ${params.start_time || 0}s - ${params.end_time || 'סוף'}s`;
      case 'adjust_volume':
        return `שינוי עוצמה: ${params.volume_change_db > 0 ? '+' : ''}${params.volume_change_db}dB`;
      case 'apply_fade':
        const fadeDesc = [];
        if (params.fade_in_duration > 0) fadeDesc.push(`Fade In: ${params.fade_in_duration}s`);
        if (params.fade_out_duration > 0) fadeDesc.push(`Fade Out: ${params.fade_out_duration}s`);
        return fadeDesc.join(', ') || 'Fade Effect';
      case 'normalize_audio':
        return `נורמליזציה: ${params.target_level_db}dB (${params.normalization_type})`;
      case 'remove_silence':
        return `הסרת שקט: סף ${params.silence_threshold_db}dB`;
      case 'reduce_noise':
        return `הפחתת רעש: ${Math.round((params.reduction_amount || 0.5) * 100)}%`;
      case 'combine_audio_files':
        return `חיבור קבצים: ${params.method} (${params.input_files_count} קבצים)`;
      default:
        return 'עריכת אודיו';
    }
  };

  if (!originalFile && !editedFile) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <div className="text-gray-500 mb-2">אין קובץ לתצוגה מקדימה</div>
        <div className="text-sm text-gray-400">בחר קובץ אודיו ובצע עריכה כדי לראות תצוגה מקדימה</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* כותרת */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          {getOperationIcon(editOperation)}
          <div>
            <h3 className="font-semibold text-gray-900">תצוגה מקדימה - עריכת אודיו</h3>
            <p className="text-sm text-gray-600">{getOperationDescription(editOperation, editParams)}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {canUndo && (
            <button
              onClick={onUndo}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              ביטול
            </button>
          )}
        </div>
      </div>

      {/* נגני אודיו */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* נגן מקורי */}
        {originalFile && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">מקורי</h4>
              <span className="text-sm text-gray-500">
                {formatTime(originalPlayer.duration)}
              </span>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <audio ref={originalAudioRef} src={originalFile} preload="metadata" />
              
              <div className="flex items-center gap-3 mb-3">
                <button
                  onClick={() => togglePlay('original')}
                  className="flex items-center justify-center w-10 h-10 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors"
                >
                  {originalPlayer.isPlaying ? (
                    <Pause className="w-5 h-5" />
                  ) : (
                    <Play className="w-5 h-5 ml-0.5" />
                  )}
                </button>
                
                <div className="flex-1">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>{formatTime(originalPlayer.currentTime)}</span>
                    <span>{formatTime(originalPlayer.duration)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-100"
                      style={{
                        width: `${originalPlayer.duration > 0 ? (originalPlayer.currentTime / originalPlayer.duration) * 100 : 0}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* נגן מעובד */}
        {editedFile && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">לאחר עריכה</h4>
              <span className="text-sm text-gray-500">
                {formatTime(editedPlayer.duration)}
              </span>
            </div>
            
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <audio ref={editedAudioRef} src={editedFile} preload="metadata" />
              
              <div className="flex items-center gap-3 mb-3">
                <button
                  onClick={() => togglePlay('edited')}
                  className="flex items-center justify-center w-10 h-10 bg-green-600 hover:bg-green-700 text-white rounded-full transition-colors"
                >
                  {editedPlayer.isPlaying ? (
                    <Pause className="w-5 h-5" />
                  ) : (
                    <Play className="w-5 h-5 ml-0.5" />
                  )}
                </button>
                
                <div className="flex-1">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>{formatTime(editedPlayer.currentTime)}</span>
                    <span>{formatTime(editedPlayer.duration)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all duration-100"
                      style={{
                        width: `${editedPlayer.duration > 0 ? (editedPlayer.currentTime / editedPlayer.duration) * 100 : 0}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* פעולות */}
      {editedFile && (
        <div className="flex items-center justify-end gap-3 mt-6 pt-6 border-t border-gray-200">
          <button
            onClick={onDiscard}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
            ביטול שינויים
          </button>
          
          <button
            onClick={() => onSave?.(editedFile)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
            <Save className="w-4 h-4" />
            שמירת שינויים
          </button>
        </div>
      )}
    </div>
  );
};