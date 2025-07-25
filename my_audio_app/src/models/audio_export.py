from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os


@dataclass
class AudioExport:
    """מודל לייצוא אודיו"""
    id: str
    source_file_id: str
    name: str
    path: str
    format: str
    size: int
    duration: int
    created_at: datetime
    status: str  # "completed", "processing", "failed"
    settings: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
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
    def created_at_formatted(self) -> str:
        """החזרת תאריך יצירה בפורמט קריא"""
        now = datetime.now()
        
        # אם התאריך הוא היום
        if self.created_at.date() == now.date():
            return f"היום, {self.created_at.strftime('%H:%M')}"
        
        # אם התאריך הוא אתמול
        yesterday = now.date().replace(day=now.day-1)
        if self.created_at.date() == yesterday:
            return f"אתמול, {self.created_at.strftime('%H:%M')}"
        
        # אחרת, החזר תאריך מלא
        return self.created_at.strftime("%d/%m/%Y, %H:%M")
    
    @property
    def extension(self) -> str:
        """החזרת סיומת הקובץ"""
        return f".{self.format.lower()}"
    
    @property
    def filename(self) -> str:
        """החזרת שם הקובץ ללא נתיב"""
        return os.path.basename(self.path)
    
    @property
    def directory(self) -> str:
        """החזרת תיקיית הקובץ"""
        return os.path.dirname(self.path)
    
    @property
    def is_completed(self) -> bool:
        """האם הייצוא הושלם"""
        return self.status == "completed"
    
    @property
    def is_processing(self) -> bool:
        """האם הייצוא בתהליך"""
        return self.status == "processing"
    
    @property
    def is_failed(self) -> bool:
        """האם הייצוא נכשל"""
        return self.status == "failed"
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת האובייקט למילון"""
        return {
            "id": self.id,
            "source_file_id": self.source_file_id,
            "name": self.name,
            "path": self.path,
            "format": self.format,
            "size": self.size,
            "duration": self.duration,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "settings": self.settings,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """המרת האובייקט למחרוזת JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioExport':
        """יצירת אובייקט מתוך מילון"""
        # המרת תאריך מ-ISO לאובייקט datetime
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        return cls(
            id=data["id"],
            source_file_id=data["source_file_id"],
            name=data["name"],
            path=data["path"],
            format=data["format"],
            size=data["size"],
            duration=data["duration"],
            created_at=data["created_at"],
            status=data["status"],
            settings=data["settings"],
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AudioExport':
        """יצירת אובייקט מתוך מחרוזת JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update(self, **kwargs) -> None:
        """עדכון שדות באובייקט"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __str__(self) -> str:
        """מחרוזת ייצוג"""
        return f"AudioExport(id={self.id}, name={self.name}, format={self.format}, status={self.status})"
