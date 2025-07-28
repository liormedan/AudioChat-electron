import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ui.components.file_upload.file_info import FileInfo


@dataclass
class StatsSummary:
    """Summary statistics for all files"""
    total_files: int
    total_duration_seconds: int
    format_distribution: Dict[str, int]
    last_upload: Optional[datetime]

    @property
    def total_duration_formatted(self) -> str:
        seconds = self.total_duration_seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


class FileStatsDataManager:
    """Provide aggregate statistics for uploaded files."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".audio_app", "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "audio_files.db")
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_total_files_count(self) -> int:
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files")
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else 0
        except Exception:
            return 0

    def get_total_duration(self) -> int:
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(duration) FROM files")
            row = cursor.fetchone()
            conn.close()
            return int(row[0] or 0)
        except Exception:
            return 0

    def get_format_distribution(self) -> Dict[str, int]:
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT format, COUNT(*) FROM files GROUP BY format")
            rows = cursor.fetchall()
            conn.close()
            return {fmt: count for fmt, count in rows}
        except Exception:
            return {}

    def get_last_upload_date(self) -> Optional[datetime]:
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT upload_date FROM files ORDER BY upload_date DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            return datetime.fromisoformat(row[0]) if row else None
        except Exception:
            return None

    def get_recent_files(self, limit: int = 10) -> List[FileInfo]:
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, path, size, format, duration, upload_date FROM files ORDER BY upload_date DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            conn.close()
            files = []
            for row in rows:
                name, path, size, fmt, duration, upload_date = row
                files.append(
                    FileInfo(
                        name=name,
                        path=path,
                        size=size,
                        format=fmt,
                        duration=duration,
                        upload_date=datetime.fromisoformat(upload_date),
                    )
                )
            return files
        except Exception:
            return []

    def get_upload_timeline(self, days: int = 7) -> Dict[str, int]:
        try:
            start_date = datetime.now() - timedelta(days=days - 1)
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date(upload_date), COUNT(*) FROM files WHERE date(upload_date) >= date(?) GROUP BY date(upload_date)",
                (start_date.date().isoformat(),),
            )
            rows = cursor.fetchall()
            conn.close()
            return {date: count for date, count in rows}
        except Exception:
            return {}

