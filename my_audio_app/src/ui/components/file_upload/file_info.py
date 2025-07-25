from dataclasses import dataclass
from datetime import datetime
import os
from PyQt6.QtCore import QDateTime


@dataclass
class FileInfo:
    """מידע על קובץ אודיו"""
    name: str
    path: str
    size: int
    format: str
    duration: int = 0  # משך בשניות
    upload_date: datetime = None
    
    def __post_init__(self):
        """אתחול לאחר יצירת האובייקט"""
        if self.upload_date is None:
            self.upload_date = datetime.now()
    
    @property
    def size_formatted(self) -> str:
        """החזרת גודל קובץ בפורמט קריא"""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.1f} GB"
    
    @property
    def duration_formatted(self) -> str:
        """החזרת משך בפורמט קריא"""
        if self.duration == 0:
            return "00:00"
        
        minutes, seconds = divmod(self.duration, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    @property
    def upload_date_formatted(self) -> str:
        """החזרת תאריך העלאה בפורמט קריא"""
        now = datetime.now()
        date = self.upload_date
        
        # אם התאריך הוא היום
        if date.date() == now.date():
            return f"היום, {date.strftime('%H:%M')}"
        
        # אם התאריך הוא אתמול
        yesterday = now.date().replace(day=now.day-1)
        if date.date() == yesterday:
            return f"אתמול, {date.strftime('%H:%M')}"
        
        # אחרת, החזר תאריך מלא
        return date.strftime("%d/%m/%Y, %H:%M")
    
    @property
    def extension(self) -> str:
        """החזרת סיומת הקובץ"""
        return os.path.splitext(self.name)[1].lower()
    
    @classmethod
    def from_file_path(cls, file_path: str, duration: int = 0):
        """יצירת אובייקט FileInfo מנתיב קובץ"""
        name = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        format = os.path.splitext(name)[1].lower().replace('.', '')
        
        return cls(
            name=name,
            path=file_path,
            size=size,
            format=format,
            duration=duration,
            upload_date=datetime.now()
        )
    
    @classmethod
    def from_qt_datetime(cls, file_path: str, duration: int = 0, upload_date: QDateTime = None):
        """יצירת אובייקט FileInfo מנתיב קובץ עם QDateTime"""
        info = cls.from_file_path(file_path, duration)
        
        if upload_date:
            info.upload_date = upload_date.toPython()
        
        return info
