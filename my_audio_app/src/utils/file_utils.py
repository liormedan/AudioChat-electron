import os
import mimetypes
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from ui.components.file_upload.file_info import FileInfo


def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    חילוץ מטא-דאטה מקובץ אודיו
    
    Args:
        file_path (str): נתיב הקובץ
        
    Returns:
        Dict[str, Any]: מילון עם מטא-דאטה של הקובץ
    """
    metadata = {}
    
    try:
        # בדיקה אם הקובץ קיים
        if not os.path.exists(file_path):
            return metadata
        
        # מידע בסיסי
        file_stat = os.stat(file_path)
        metadata["size"] = file_stat.st_size
        metadata["created"] = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
        metadata["modified"] = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        
        # סוג MIME
        mime_type, encoding = mimetypes.guess_type(file_path)
        if mime_type:
            metadata["mime_type"] = mime_type
        
        # בפרויקט אמיתי, כאן היינו משתמשים בספריות כמו mutagen או pydub
        # לחילוץ מידע נוסף כמו:
        # - משך הקובץ
        # - קצב דגימה
        # - קצב סיביות
        # - מספר ערוצים
        # - תגיות ID3 (לקבצי MP3)
        # לדוגמה:
        # try:
        #     from mutagen.mp3 import MP3
        #     if file_path.lower().endswith('.mp3'):
        #         audio = MP3(file_path)
        #         metadata["duration"] = audio.info.length
        #         metadata["bitrate"] = audio.info.bitrate
        #         metadata["sample_rate"] = audio.info.sample_rate
        #         metadata["channels"] = audio.info.channels
        #         
        #         # תגיות ID3
        #         if audio.tags:
        #             for key in audio.tags.keys():
        #                 metadata[f"tag_{key}"] = str(audio.tags[key])
        # except ImportError:
        #     pass
        
    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata


def extract_audio_duration(file_path: str) -> Optional[int]:
    """
    חילוץ משך הקובץ בשניות
    
    Args:
        file_path (str): נתיב הקובץ
        
    Returns:
        Optional[int]: משך הקובץ בשניות או None אם לא ניתן לחלץ
    """
    try:
        # בפרויקט אמיתי, כאן היינו משתמשים בספריות כמו mutagen או pydub
        # לדוגמה:
        # from mutagen.mp3 import MP3
        # if file_path.lower().endswith('.mp3'):
        #     audio = MP3(file_path)
        #     return int(audio.info.length)
        # 
        # from mutagen.wave import WAVE
        # if file_path.lower().endswith('.wav'):
        #     audio = WAVE(file_path)
        #     return int(audio.info.length)
        
        # כרגע נחזיר None כי אין לנו ספריות חיצוניות
        return None
    
    except Exception:
        return None


def get_audio_format_details(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    קבלת פרטים על פורמט האודיו
    
    Args:
        file_path (str): נתיב הקובץ
        
    Returns:
        Tuple[str, Dict[str, Any]]: פורמט הקובץ ומילון עם פרטים נוספים
    """
    format_name = os.path.splitext(file_path)[1].lower().replace('.', '')
    details = {}
    
    # בפרויקט אמיתי, כאן היינו מוסיפים מידע ספציפי לפורמט
    # לדוגמה:
    if format_name == 'mp3':
        details["description"] = "MPEG Audio Layer III"
        details["lossy"] = True
    elif format_name == 'wav':
        details["description"] = "Waveform Audio File Format"
        details["lossy"] = False
    elif format_name == 'flac':
        details["description"] = "Free Lossless Audio Codec"
        details["lossy"] = False
    elif format_name == 'ogg':
        details["description"] = "Ogg Vorbis Audio"
        details["lossy"] = True
    elif format_name == 'm4a':
        details["description"] = "MPEG-4 Audio"
        details["lossy"] = True
    elif format_name == 'aac':
        details["description"] = "Advanced Audio Coding"
        details["lossy"] = True
    
    return format_name, details


def create_file_info_from_path(file_path: str) -> Optional[FileInfo]:
    """
    יצירת אובייקט FileInfo מנתיב קובץ עם מידע מורחב
    
    Args:
        file_path (str): נתיב הקובץ
        
    Returns:
        Optional[FileInfo]: אובייקט FileInfo או None אם הקובץ לא קיים
    """
    try:
        # בדיקה אם הקובץ קיים
        if not os.path.exists(file_path):
            return None
        
        # מידע בסיסי
        name = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        format_name, _ = get_audio_format_details(file_path)
        
        # חילוץ משך הקובץ
        duration = extract_audio_duration(file_path) or 0
        
        # יצירת אובייקט FileInfo
        return FileInfo(
            name=name,
            path=file_path,
            size=size,
            format=format_name,
            duration=duration,
            upload_date=datetime.now()
        )
    
    except Exception:
        return None