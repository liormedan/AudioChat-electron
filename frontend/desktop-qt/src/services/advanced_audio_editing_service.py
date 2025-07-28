"""
Advanced Audio Editing Service
שירות עריכת אודיו מתקדם עם pydub ו-librosa
"""

import os
import logging
import tempfile
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
import time

try:
    from pydub import AudioSegment
    from pydub.effects import normalize as pydub_normalize
    from pydub.silence import split_on_silence, detect_nonsilent
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("pydub not available. Audio editing will be limited.")

try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logging.warning("librosa not available. Advanced audio processing will be limited.")

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False
    logging.warning("noisereduce not available. Noise reduction will be limited.")


class AdvancedAudioEditingService:
    """שירות עריכת אודיו מתקדם"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = temp_dir or tempfile.gettempdir()
        
        # בדיקת זמינות ספריות
        self.capabilities = {
            'pydub': PYDUB_AVAILABLE,
            'librosa': LIBROSA_AVAILABLE,
            'noisereduce': NOISEREDUCE_AVAILABLE
        }
        
        # פורמטים נתמכים
        self.supported_formats = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
        
        # הגדרות ברירת מחדל
        self.default_settings = {
            'sample_rate': 44100,
            'channels': 2,
            'bit_depth': 16,
            'fade_duration': 2.0,
            'normalize_target': -3.0,
            'silence_threshold': -40.0,
            'min_silence_len': 1000  # milliseconds
        }

    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """קבלת מידע על קובץ אודיו"""
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File not found'}
            
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(file_path)
                return {
                    'success': True,
                    'duration': len(audio) / 1000.0,  # seconds
                    'sample_rate': audio.frame_rate,
                    'channels': audio.channels,
                    'frame_count': audio.frame_count(),
                    'format': file_path.split('.')[-1].lower(),
                    'file_size': os.path.getsize(file_path)
                }
            else:
                # fallback without pydub
                return {
                    'success': True,
                    'file_size': os.path.getsize(file_path),
                    'format': file_path.split('.')[-1].lower()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting audio info: {e}")
            return {'success': False, 'error': str(e)}

    async def trim_audio(self, 
                        input_file: str, 
                        start_time: float = 0.0, 
                        end_time: Optional[float] = None,
                        output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        חיתוך קובץ אודיו
        
        Args:
            input_file: נתיב קובץ הקלט
            start_time: זמן התחלה בשניות
            end_time: זמן סיום בשניות (None = עד הסוף)
            output_file: נתיב קובץ הפלט (None = יצירה אוטומטית)
        """
        start_processing = time.time()
        
        try:
            if not PYDUB_AVAILABLE:
                return {'success': False, 'error': 'pydub not available'}
            
            if not os.path.exists(input_file):
                return {'success': False, 'error': 'Input file not found'}
            
            # טעינת הקובץ
            audio = AudioSegment.from_file(input_file)
            
            # המרת זמנים למילישניות
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000) if end_time else len(audio)
            
            # בדיקת תקינות הזמנים
            if start_ms < 0:
                start_ms = 0
            if end_ms > len(audio):
                end_ms = len(audio)
            if start_ms >= end_ms:
                return {'success': False, 'error': 'Invalid time range'}
            
            # חיתוך האודיו
            trimmed_audio = audio[start_ms:end_ms]
            
            # יצירת שם קובץ פלט
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                extension = os.path.splitext(input_file)[1]
                output_file = os.path.join(
                    self.temp_dir, 
                    f"{base_name}_trimmed_{start_time}s-{end_time or 'end'}s{extension}"
                )
            
            # שמירת הקובץ
            trimmed_audio.export(output_file, format=self._get_format_from_extension(output_file))
            
            processing_time = time.time() - start_processing
            
            return {
                'success': True,
                'output_file': output_file,
                'processing_time': processing_time,
                'original_duration': len(audio) / 1000.0,
                'trimmed_duration': len(trimmed_audio) / 1000.0,
                'start_time': start_time,
                'end_time': end_time or (len(audio) / 1000.0)
            }
            
        except Exception as e:
            self.logger.error(f"Error trimming audio: {e}")
            return {'success': False, 'error': str(e)}

    async def adjust_volume(self, 
                           input_file: str, 
                           volume_change_db: float,
                           output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        שינוי עוצמת קול
        
        Args:
            input_file: נתיב קובץ הקלט
            volume_change_db: שינוי בדציבלים (חיובי = הגברה, שלילי = הנמכה)
            output_file: נתיב קובץ הפלט
        """
        start_processing = time.time()
        
        try:
            if not PYDUB_AVAILABLE:
                return {'success': False, 'error': 'pydub not available'}
            
            if not os.path.exists(input_file):
                return {'success': False, 'error': 'Input file not found'}
            
            # טעינת הקובץ
            audio = AudioSegment.from_file(input_file)
            
            # בדיקת גבולות בטיחות
            if volume_change_db > 20:
                return {'success': False, 'error': 'Volume increase too high (max +20dB)'}
            if volume_change_db < -60:
                return {'success': False, 'error': 'Volume decrease too low (min -60dB)'}
            
            # שינוי עוצמת הקול
            adjusted_audio = audio + volume_change_db
            
            # יצירת שם קובץ פלט
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                extension = os.path.splitext(input_file)[1]
                sign = "+" if volume_change_db >= 0 else ""
                output_file = os.path.join(
                    self.temp_dir, 
                    f"{base_name}_volume{sign}{volume_change_db}dB{extension}"
                )
            
            # שמירת הקובץ
            adjusted_audio.export(output_file, format=self._get_format_from_extension(output_file))
            
            processing_time = time.time() - start_processing
            
            return {
                'success': True,
                'output_file': output_file,
                'processing_time': processing_time,
                'volume_change_db': volume_change_db,
                'original_max_db': audio.max_dBFS,
                'adjusted_max_db': adjusted_audio.max_dBFS
            }
            
        except Exception as e:
            self.logger.error(f"Error adjusting volume: {e}")
            return {'success': False, 'error': str(e)}

    async def apply_fade(self, 
                        input_file: str, 
                        fade_in_duration: float = 0.0,
                        fade_out_duration: float = 0.0,
                        output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        הוספת אפקטי fade
        
        Args:
            input_file: נתיב קובץ הקלט
            fade_in_duration: משך fade in בשניות
            fade_out_duration: משך fade out בשניות
            output_file: נתיב קובץ הפלט
        """
        start_processing = time.time()
        
        try:
            if not PYDUB_AVAILABLE:
                return {'success': False, 'error': 'pydub not available'}
            
            if not os.path.exists(input_file):
                return {'success': False, 'error': 'Input file not found'}
            
            # טעינת הקובץ
            audio = AudioSegment.from_file(input_file)
            
            # המרת זמנים למילישניות
            fade_in_ms = int(fade_in_duration * 1000)
            fade_out_ms = int(fade_out_duration * 1000)
            
            # בדיקת תקינות
            if fade_in_ms + fade_out_ms > len(audio):
                return {'success': False, 'error': 'Fade durations too long for audio length'}
            
            # הוספת fade effects
            faded_audio = audio
            
            if fade_in_ms > 0:
                faded_audio = faded_audio.fade_in(fade_in_ms)
            
            if fade_out_ms > 0:
                faded_audio = faded_audio.fade_out(fade_out_ms)
            
            # יצירת שם קובץ פלט
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                extension = os.path.splitext(input_file)[1]
                fade_desc = []
                if fade_in_duration > 0:
                    fade_desc.append(f"in{fade_in_duration}s")
                if fade_out_duration > 0:
                    fade_desc.append(f"out{fade_out_duration}s")
                fade_str = "_".join(fade_desc) if fade_desc else "fade"
                output_file = os.path.join(
                    self.temp_dir, 
                    f"{base_name}_fade_{fade_str}{extension}"
                )
            
            # שמירת הקובץ
            faded_audio.export(output_file, format=self._get_format_from_extension(output_file))
            
            processing_time = time.time() - start_processing
            
            return {
                'success': True,
                'output_file': output_file,
                'processing_time': processing_time,
                'fade_in_duration': fade_in_duration,
                'fade_out_duration': fade_out_duration,
                'total_duration': len(faded_audio) / 1000.0
            }
            
        except Exception as e:
            self.logger.error(f"Error applying fade: {e}")
            return {'success': False, 'error': str(e)}

    async def normalize_audio(self, 
                             input_file: str, 
                             target_level_db: float = -3.0,
                             normalization_type: str = 'peak',
                             output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        נורמליזציה של אודיו
        
        Args:
            input_file: נתיב קובץ הקלט
            target_level_db: רמת היעד בדציבלים
            normalization_type: סוג נורמליזציה ('peak' או 'rms')
            output_file: נתיב קובץ הפלט
        """
        start_processing = time.time()
        
        try:
            if not PYDUB_AVAILABLE:
                return {'success': False, 'error': 'pydub not available'}
            
            if not os.path.exists(input_file):
                return {'success': False, 'error': 'Input file not found'}
            
            # טעינת הקובץ
            audio = AudioSegment.from_file(input_file)
            
            if normalization_type == 'peak':
                # Peak normalization
                current_peak = audio.max_dBFS
                gain_needed = target_level_db - current_peak
                normalized_audio = audio + gain_needed
            
            elif normalization_type == 'rms':
                # RMS normalization (more complex)
                if LIBROSA_AVAILABLE:
                    # Use librosa for RMS calculation
                    y, sr = librosa.load(input_file, sr=None)
                    rms = librosa.feature.rms(y=y)[0]
                    current_rms_db = 20 * np.log10(np.mean(rms))
                    gain_needed = target_level_db - current_rms_db
                    normalized_audio = audio + gain_needed
                else:
                    # Fallback to peak normalization
                    current_peak = audio.max_dBFS
                    gain_needed = target_level_db - current_peak
                    normalized_audio = audio + gain_needed
            
            else:
                return {'success': False, 'error': 'Invalid normalization type'}
            
            # יצירת שם קובץ פלט
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                extension = os.path.splitext(input_file)[1]
                output_file = os.path.join(
                    self.temp_dir, 
                    f"{base_name}_normalized_{normalization_type}_{target_level_db}dB{extension}"
                )
            
            # שמירת הקובץ
            normalized_audio.export(output_file, format=self._get_format_from_extension(output_file))
            
            processing_time = time.time() - start_processing
            
            return {
                'success': True,
                'output_file': output_file,
                'processing_time': processing_time,
                'normalization_type': normalization_type,
                'target_level_db': target_level_db,
                'original_peak_db': audio.max_dBFS,
                'normalized_peak_db': normalized_audio.max_dBFS,
                'gain_applied_db': gain_needed
            }
            
        except Exception as e:
            self.logger.error(f"Error normalizing audio: {e}")
            return {'success': False, 'error': str(e)}

    async def remove_silence(self, 
                            input_file: str, 
                            silence_threshold_db: float = -40.0,
                            min_silence_duration: float = 1.0,
                            keep_silence: float = 0.1,
                            output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        הסרת שקט מקובץ אודיו
        
        Args:
            input_file: נתיב קובץ הקלט
            silence_threshold_db: סף השקט בדציבלים
            min_silence_duration: משך שקט מינימלי להסרה (שניות)
            keep_silence: כמה שקט להשאיר (שניות)
            output_file: נתיב קובץ הפלט
        """
        start_processing = time.time()
        
        try:
            if not PYDUB_AVAILABLE:
                return {'success': False, 'error': 'pydub not available'}
            
            if not os.path.exists(input_file):
                return {'success': False, 'error': 'Input file not found'}
            
            # טעינת הקובץ
            audio = AudioSegment.from_file(input_file)
            
            # המרת פרמטרים
            min_silence_len = int(min_silence_duration * 1000)  # ms
            keep_silence_len = int(keep_silence * 1000)  # ms
            
            # חיתוך על בסיס שקט
            audio_chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_threshold_db,
                keep_silence=keep_silence_len
            )
            
            if not audio_chunks:
                return {'success': False, 'error': 'No audio content found'}
            
            # חיבור החלקים
            combined_audio = AudioSegment.empty()
            for chunk in audio_chunks:
                combined_audio += chunk
            
            # יצירת שם קובץ פלט
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                extension = os.path.splitext(input_file)[1]
                output_file = os.path.join(
                    self.temp_dir, 
                    f"{base_name}_silence_removed{extension}"
                )
            
            # שמירת הקובץ
            combined_audio.export(output_file, format=self._get_format_from_extension(output_file))
            
            processing_time = time.time() - start_processing
            
            return {
                'success': True,
                'output_file': output_file,
                'processing_time': processing_time,
                'original_duration': len(audio) / 1000.0,
                'processed_duration': len(combined_audio) / 1000.0,
                'silence_removed': (len(audio) - len(combined_audio)) / 1000.0,
                'chunks_found': len(audio_chunks)
            }
            
        except Exception as e:
            self.logger.error(f"Error removing silence: {e}")
            return {'success': False, 'error': str(e)}

    async def combine_audio_files(self, 
                                 input_files: List[str], 
                                 method: str = 'concatenate',
                                 crossfade_duration: float = 0.0,
                                 output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        חיבור קבצי אודיו
        
        Args:
            input_files: רשימת נתיבי קבצי הקלט
            method: שיטת החיבור ('concatenate', 'overlay', 'mix')
            crossfade_duration: משך crossfade בשניות (רק ל-concatenate)
            output_file: נתיב קובץ הפלט
        """
        start_processing = time.time()
        
        try:
            if not PYDUB_AVAILABLE:
                return {'success': False, 'error': 'pydub not available'}
            
            if not input_files or len(input_files) < 2:
                return {'success': False, 'error': 'At least 2 files required'}
            
            # בדיקת קיום קבצים
            for file_path in input_files:
                if not os.path.exists(file_path):
                    return {'success': False, 'error': f'File not found: {file_path}'}
            
            # טעינת הקבצים
            audio_segments = []
            for file_path in input_files:
                audio = AudioSegment.from_file(file_path)
                audio_segments.append(audio)
            
            # חיבור לפי השיטה
            if method == 'concatenate':
                combined_audio = audio_segments[0]
                for audio in audio_segments[1:]:
                    if crossfade_duration > 0:
                        crossfade_ms = int(crossfade_duration * 1000)
                        combined_audio = combined_audio.append(audio, crossfade=crossfade_ms)
                    else:
                        combined_audio = combined_audio + audio
            
            elif method == 'overlay':
                combined_audio = audio_segments[0]
                for audio in audio_segments[1:]:
                    combined_audio = combined_audio.overlay(audio)
            
            elif method == 'mix':
                # Mix all files together (average)
                combined_audio = audio_segments[0]
                for audio in audio_segments[1:]:
                    combined_audio = combined_audio.overlay(audio)
                # Reduce volume to prevent clipping
                combined_audio = combined_audio - 6  # -6dB for safety
            
            else:
                return {'success': False, 'error': 'Invalid combination method'}
            
            # יצירת שם קובץ פלט
            if not output_file:
                base_names = [os.path.splitext(os.path.basename(f))[0] for f in input_files[:3]]
                combined_name = "_".join(base_names)
                if len(input_files) > 3:
                    combined_name += f"_and_{len(input_files)-3}_more"
                extension = os.path.splitext(input_files[0])[1]
                output_file = os.path.join(
                    self.temp_dir, 
                    f"{combined_name}_{method}{extension}"
                )
            
            # שמירת הקובץ
            combined_audio.export(output_file, format=self._get_format_from_extension(output_file))
            
            processing_time = time.time() - start_processing
            
            return {
                'success': True,
                'output_file': output_file,
                'processing_time': processing_time,
                'method': method,
                'input_files_count': len(input_files),
                'combined_duration': len(combined_audio) / 1000.0,
                'crossfade_duration': crossfade_duration if method == 'concatenate' else None
            }
            
        except Exception as e:
            self.logger.error(f"Error combining audio files: {e}")
            return {'success': False, 'error': str(e)}

    async def reduce_noise(self, 
                          input_file: str, 
                          reduction_amount: float = 0.5,
                          noise_type: str = 'auto',
                          output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        הפחתת רעש
        
        Args:
            input_file: נתיב קובץ הקלט
            reduction_amount: כמות הפחתה (0.0-1.0)
            noise_type: סוג הרעש ('auto', 'hum', 'hiss', 'click')
            output_file: נתיב קובץ הפלט
        """
        start_processing = time.time()
        
        try:
            if not LIBROSA_AVAILABLE or not NOISEREDUCE_AVAILABLE:
                return {'success': False, 'error': 'librosa or noisereduce not available'}
            
            if not os.path.exists(input_file):
                return {'success': False, 'error': 'Input file not found'}
            
            # טעינת הקובץ עם librosa
            y, sr = librosa.load(input_file, sr=None)
            
            # הפחתת רעש
            if noise_type == 'auto':
                # Automatic noise reduction
                reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=reduction_amount)
            else:
                # Specific noise type handling could be added here
                reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=reduction_amount)
            
            # יצירת שם קובץ פלט
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                extension = os.path.splitext(input_file)[1]
                output_file = os.path.join(
                    self.temp_dir, 
                    f"{base_name}_noise_reduced_{int(reduction_amount*100)}pct{extension}"
                )
            
            # שמירת הקובץ
            sf.write(output_file, reduced_noise, sr)
            
            processing_time = time.time() - start_processing
            
            return {
                'success': True,
                'output_file': output_file,
                'processing_time': processing_time,
                'reduction_amount': reduction_amount,
                'noise_type': noise_type,
                'sample_rate': sr,
                'duration': len(reduced_noise) / sr
            }
            
        except Exception as e:
            self.logger.error(f"Error reducing noise: {e}")
            return {'success': False, 'error': str(e)}

    def _get_format_from_extension(self, file_path: str) -> str:
        """קבלת פורמט מסיומת הקובץ"""
        extension = os.path.splitext(file_path)[1].lower()
        format_map = {
            '.mp3': 'mp3',
            '.wav': 'wav',
            '.flac': 'flac',
            '.ogg': 'ogg',
            '.m4a': 'mp4',
            '.aac': 'aac'
        }
        return format_map.get(extension, 'wav')

    def get_capabilities(self) -> Dict[str, Any]:
        """קבלת יכולות השירות"""
        return {
            'libraries': self.capabilities,
            'supported_formats': self.supported_formats,
            'operations': [
                'trim_audio',
                'adjust_volume', 
                'apply_fade',
                'normalize_audio',
                'remove_silence',
                'combine_audio_files',
                'reduce_noise'
            ],
            'default_settings': self.default_settings
        }

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """אימות קובץ אודיו"""
        try:
            if not os.path.exists(file_path):
                return {'valid': False, 'error': 'File does not exist'}
            
            extension = os.path.splitext(file_path)[1].lower()
            if extension not in self.supported_formats:
                return {'valid': False, 'error': f'Unsupported format: {extension}'}
            
            # בדיקה בסיסית עם pydub
            if PYDUB_AVAILABLE:
                try:
                    audio = AudioSegment.from_file(file_path)
                    return {
                        'valid': True,
                        'duration': len(audio) / 1000.0,
                        'sample_rate': audio.frame_rate,
                        'channels': audio.channels
                    }
                except Exception as e:
                    return {'valid': False, 'error': f'Cannot read audio file: {str(e)}'}
            
            return {'valid': True, 'note': 'Basic validation only (pydub not available)'}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}