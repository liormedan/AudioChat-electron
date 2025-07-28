import os
import json
import sqlite3
import uuid
import threading
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from models.audio_export import AudioExport


class ExportService:
    """שירות לניהול ייצואי אודיו"""
    
    def __init__(self, db_path: str = None):
        """
        אתחול שירות ייצואים
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים. אם לא מסופק, ישתמש בנתיב ברירת מחדל
        """
        # מנעול לסנכרון גישה למסד הנתונים
        self.db_lock = threading.Lock()
        
        if db_path is None:
            # יצירת תיקיית נתונים אם לא קיימת
            data_dir = os.path.join(os.path.expanduser("~"), ".audio_app", "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "audio_exports.db")
        
        self.db_path = db_path
        
        # יצירת תיקיית ייצואים אם לא קיימת
        self.exports_dir = os.path.join(os.path.expanduser("~"), ".audio_app", "exports")
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # מעקב אחר ייצואים בתהליך
        self.processing_exports = {}
        
        # אתחול מסד הנתונים
        self._init_db()
    
    def _init_db(self):
        """אתחול מסד הנתונים"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # יצירת טבלת ייצואים אם לא קיימת
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS exports (
                id TEXT PRIMARY KEY,
                source_file_id TEXT NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                format TEXT NOT NULL,
                size INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                settings TEXT NOT NULL,
                metadata TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
    
    def get_all_exports(self) -> List[AudioExport]:
        """
        קבלת כל הייצואים
        
        Returns:
            List[AudioExport]: רשימת כל הייצואים
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, source_file_id, name, path, format, size, duration, created_at, status, settings, metadata
            FROM exports
            ORDER BY created_at DESC
            ''')
            
            exports = []
            for row in cursor.fetchall():
                id, source_file_id, name, path, format, size, duration, created_at, status, settings_json, metadata_json = row
                
                # המרת JSON למילון
                settings = json.loads(settings_json)
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                # יצירת אובייקט ייצוא
                export = AudioExport(
                    id=id,
                    source_file_id=source_file_id,
                    name=name,
                    path=path,
                    format=format,
                    size=size,
                    duration=duration,
                    created_at=datetime.fromisoformat(created_at),
                    status=status,
                    settings=settings,
                    metadata=metadata
                )
                
                exports.append(export)
            
            conn.close()
            return exports
    
    def get_exports_page(self, page: int = 1, page_size: int = 10) -> Tuple[List[AudioExport], Dict[str, Any]]:
        """
        קבלת עמוד של ייצואים
        
        Args:
            page (int, optional): מספר העמוד (ברירת מחדל: 1)
            page_size (int, optional): גודל העמוד (ברירת מחדל: 10)
            
        Returns:
            Tuple[List[AudioExport], Dict[str, Any]]: רשימת ייצואים ומידע על העימוד
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ספירת סך הכל ייצואים
            cursor.execute('SELECT COUNT(*) FROM exports')
            total_count = cursor.fetchone()[0]
            
            # חישוב מספר העמודים
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
            
            # וידוא שמספר העמוד תקין
            page = max(1, min(page, total_pages))
            
            # חישוב היסט
            offset = (page - 1) * page_size
            
            # שליפת הייצואים לעמוד הנוכחי
            cursor.execute('''
            SELECT id, source_file_id, name, path, format, size, duration, created_at, status, settings, metadata
            FROM exports
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            ''', (page_size, offset))
            
            exports = []
            for row in cursor.fetchall():
                id, source_file_id, name, path, format, size, duration, created_at, status, settings_json, metadata_json = row
                
                # המרת JSON למילון
                settings = json.loads(settings_json)
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                # יצירת אובייקט ייצוא
                export = AudioExport(
                    id=id,
                    source_file_id=source_file_id,
                    name=name,
                    path=path,
                    format=format,
                    size=size,
                    duration=duration,
                    created_at=datetime.fromisoformat(created_at),
                    status=status,
                    settings=settings,
                    metadata=metadata
                )
                
                exports.append(export)
            
            conn.close()
            
            # מידע על העימוד
            pagination = {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
            
            return exports, pagination
    
    def get_export_by_id(self, export_id: str) -> Optional[AudioExport]:
        """
        קבלת ייצוא לפי מזהה
        
        Args:
            export_id (str): מזהה הייצוא
            
        Returns:
            Optional[AudioExport]: אובייקט הייצוא או None אם לא נמצא
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, source_file_id, name, path, format, size, duration, created_at, status, settings, metadata
            FROM exports
            WHERE id = ?
            ''', (export_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                id, source_file_id, name, path, format, size, duration, created_at, status, settings_json, metadata_json = row
                
                # המרת JSON למילון
                settings = json.loads(settings_json)
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                # יצירת אובייקט ייצוא
                return AudioExport(
                    id=id,
                    source_file_id=source_file_id,
                    name=name,
                    path=path,
                    format=format,
                    size=size,
                    duration=duration,
                    created_at=datetime.fromisoformat(created_at),
                    status=status,
                    settings=settings,
                    metadata=metadata
                )
            
            return None
    
    def create_export(self, source_file_id: str, format: str, settings: Dict[str, Any], name: Optional[str] = None) -> AudioExport:
        """
        יצירת ייצוא חדש
        
        Args:
            source_file_id (str): מזהה קובץ המקור
            format (str): פורמט הייצוא
            settings (Dict[str, Any]): הגדרות הייצוא
            name (Optional[str], optional): שם הייצוא. אם לא מסופק, ייווצר שם ברירת מחדל
            
        Returns:
            AudioExport: אובייקט הייצוא שנוצר
        """
        # יצירת מזהה ייחודי
        export_id = str(uuid.uuid4())
        
        # קבלת מידע על קובץ המקור
        # בפרויקט אמיתי, כאן היינו משתמשים בשירות הקבצים
        # אבל בבדיקות אנחנו משתמשים במוק
        try:
            from .file_service import FileService
            file_service = FileService()
            source_file = file_service.get_file_info(source_file_id)
        except (ImportError, AttributeError):
            # אם לא ניתן לייבא את השירות, נשתמש במידע מדומה
            source_file = None
        
        if not source_file:
            # יצירת אובייקט מדומה לצורך בדיקות
            class MockSourceFile:
                def __init__(self):
                    self.name = f"source_{source_file_id}.mp3"
                    self.path = f"/path/to/source_{source_file_id}.mp3"
                    self.duration = 180
            
            source_file = MockSourceFile()
        
        # יצירת שם ברירת מחדל אם לא סופק שם
        if not name:
            name = f"{os.path.splitext(source_file.name)[0]}.{format}"
        
        # יצירת נתיב לקובץ המיוצא
        path = os.path.join(self.exports_dir, f"{export_id}.{format}")
        
        # יצירת אובייקט ייצוא
        export = AudioExport(
            id=export_id,
            source_file_id=source_file_id,
            name=name,
            path=path,
            format=format,
            size=0,  # יעודכן בסיום הייצוא
            duration=source_file.duration,
            created_at=datetime.now(),
            status="processing",
            settings=settings
        )
        
        # שמירת הייצוא במסד הנתונים
        self._save_export(export)
        
        # התחלת תהליך ייצוא ברקע
        self.processing_exports[export_id] = threading.Thread(
            target=self._process_export,
            args=(export_id, source_file.path, path, format, settings)
        )
        self.processing_exports[export_id].daemon = True
        self.processing_exports[export_id].start()
        
        return export
    
    def _process_export(self, export_id: str, source_path: str, target_path: str, format: str, settings: Dict[str, Any]):
        """
        עיבוד ייצוא ברקע
        
        Args:
            export_id (str): מזהה הייצוא
            source_path (str): נתיב קובץ המקור
            target_path (str): נתיב קובץ היעד
            format (str): פורמט הייצוא
            settings (Dict[str, Any]): הגדרות הייצוא
        """
        try:
            # בפרויקט אמיתי, כאן היינו מבצעים את הייצוא בפועל
            # לדוגמה, שימוש בספריית pydub או ffmpeg
            
            # סימולציה של זמן עיבוד
            time.sleep(random.uniform(1.0, 3.0))
            
            # בדיקה שקובץ המקור קיים
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"קובץ המקור {source_path} לא נמצא")
            
            # סימולציה של יצירת קובץ יעד
            with open(target_path, "wb") as f:
                # העתקת תוכן מקובץ המקור או יצירת תוכן חדש
                try:
                    with open(source_path, "rb") as src_file:
                        content = src_file.read()
                        f.write(content)
                except Exception:
                    # אם לא ניתן לקרוא את קובץ המקור, יצירת קובץ ריק
                    f.write(f"Simulated {format} export file".encode())
            
            # חישוב גודל הקובץ
            size = os.path.getsize(target_path)
            
            # עדכון הייצוא
            export = self.get_export_by_id(export_id)
            if export:
                export.size = size
                export.status = "completed"
                
                # הוספת מטא-דאטה
                export.metadata["processed_at"] = datetime.now().isoformat()
                export.metadata["processing_time"] = random.uniform(0.5, 2.5)
                
                # שמירת הייצוא המעודכן
                self._save_export(export)
        
        except Exception as e:
            # עדכון סטטוס שגיאה
            export = self.get_export_by_id(export_id)
            if export:
                export.status = "failed"
                export.metadata["error"] = str(e)
                self._save_export(export)
            
            print(f"שגיאה בעיבוד ייצוא {export_id}: {e}")
        
        finally:
            # הסרת הייצוא מרשימת הייצואים בתהליך
            if export_id in self.processing_exports:
                del self.processing_exports[export_id]
    
    def _save_export(self, export: AudioExport):
        """
        שמירת ייצוא במסד הנתונים
        
        Args:
            export (AudioExport): אובייקט הייצוא לשמירה
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # המרת מילונים ל-JSON
            settings_json = json.dumps(export.settings)
            metadata_json = json.dumps(export.metadata)
            
            # שמירת הייצוא
            cursor.execute('''
            INSERT OR REPLACE INTO exports
            (id, source_file_id, name, path, format, size, duration, created_at, status, settings, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                export.id,
                export.source_file_id,
                export.name,
                export.path,
                export.format,
                export.size,
                export.duration,
                export.created_at.isoformat(),
                export.status,
                settings_json,
                metadata_json
            ))
            
            conn.commit()
            conn.close()
    
    def update_export(self, export_id: str, data: Dict[str, Any]) -> Optional[AudioExport]:
        """
        עדכון ייצוא
        
        Args:
            export_id (str): מזהה הייצוא
            data (Dict[str, Any]): נתונים לעדכון
            
        Returns:
            Optional[AudioExport]: אובייקט הייצוא המעודכן או None אם הייצוא לא נמצא
        """
        # קבלת הייצוא
        export = self.get_export_by_id(export_id)
        if not export:
            return None
        
        # עדכון נתונים
        for key, value in data.items():
            if hasattr(export, key):
                setattr(export, key, value)
        
        # שמירת הייצוא
        self._save_export(export)
        
        return export
    
    def delete_export(self, export_id: str) -> bool:
        """
        מחיקת ייצוא
        
        Args:
            export_id (str): מזהה הייצוא
            
        Returns:
            bool: האם המחיקה הצליחה
        """
        # קבלת הייצוא
        export = self.get_export_by_id(export_id)
        if not export:
            return False
        
        # בדיקה שהייצוא לא בתהליך
        if export_id in self.processing_exports:
            return False
        
        # מחיקת הקובץ
        try:
            if os.path.exists(export.path):
                os.remove(export.path)
        except Exception as e:
            print(f"שגיאה במחיקת קובץ הייצוא: {e}")
        
        # מחיקת הרשומה ממסד הנתונים
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM exports WHERE id = ?", (export_id,))
            
            conn.commit()
            conn.close()
            
            return True
    
    def delete_multiple_exports(self, export_ids: List[str]) -> Dict[str, Any]:
        """
        מחיקת מספר ייצואים
        
        Args:
            export_ids (List[str]): רשימת מזהי ייצואים למחיקה
            
        Returns:
            Dict[str, Any]: תוצאות המחיקה
        """
        results = {
            "success": True,
            "deleted": 0,
            "failed": 0,
            "errors": {}
        }
        
        for export_id in export_ids:
            try:
                if self.delete_export(export_id):
                    results["deleted"] += 1
                else:
                    results["failed"] += 1
                    results["errors"][export_id] = "ייצוא לא נמצא או בתהליך"
            except Exception as e:
                results["failed"] += 1
                results["errors"][export_id] = str(e)
        
        if results["failed"] > 0:
            results["success"] = False
        
        return results
    
    def search_exports(self, search_text: str = "", filters: Dict[str, Any] = None) -> List[AudioExport]:
        """
        חיפוש ייצואים
        
        Args:
            search_text (str, optional): טקסט לחיפוש
            filters (Dict[str, Any], optional): פילטרים נוספים
            
        Returns:
            List[AudioExport]: רשימת הייצואים שנמצאו
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # בניית שאילתת חיפוש
            query = '''
            SELECT id, source_file_id, name, path, format, size, duration, created_at, status, settings, metadata
            FROM exports
            WHERE 1=1
            '''
            params = []
            
            # הוספת חיפוש טקסט
            if search_text:
                query += " AND (name LIKE ? OR format LIKE ?)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])
            
            # הוספת פילטרים
            if filters:
                if "format" in filters and filters["format"]:
                    query += " AND format = ?"
                    params.append(filters["format"])
                
                if "status" in filters and filters["status"]:
                    query += " AND status = ?"
                    params.append(filters["status"])
                
                if "min_size" in filters and filters["min_size"] is not None:
                    query += " AND size >= ?"
                    params.append(int(filters["min_size"]))
                
                if "max_size" in filters and filters["max_size"] is not None:
                    query += " AND size <= ?"
                    params.append(int(filters["max_size"]))
                
                if "min_duration" in filters and filters["min_duration"] is not None:
                    query += " AND duration >= ?"
                    params.append(filters["min_duration"])
                
                if "max_duration" in filters and filters["max_duration"] is not None:
                    query += " AND duration <= ?"
                    params.append(filters["max_duration"])
                
                if "start_date" in filters and filters["start_date"]:
                    query += " AND created_at >= ?"
                    params.append(filters["start_date"].isoformat())
                
                if "end_date" in filters and filters["end_date"]:
                    query += " AND created_at <= ?"
                    params.append(filters["end_date"].isoformat())
            
            # מיון
            sort_field = "created_at"
            sort_order = "DESC"
            
            if filters and "sort" in filters:
                sort_parts = filters["sort"].split(":")
                if len(sort_parts) == 2:
                    field, order = sort_parts
                    if field in ["name", "format", "size", "duration", "created_at", "status"]:
                        sort_field = field
                    if order.upper() in ["ASC", "DESC"]:
                        sort_order = order.upper()
            
            query += f" ORDER BY {sort_field} {sort_order}"
            
            # הגבלת תוצאות
            if filters and "limit" in filters and filters["limit"] > 0:
                query += " LIMIT ?"
                params.append(filters["limit"])
            
            cursor.execute(query, params)
            
            exports = []
            for row in cursor.fetchall():
                id, source_file_id, name, path, format, size, duration, created_at, status, settings_json, metadata_json = row
                
                # המרת JSON למילון
                settings = json.loads(settings_json)
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                # יצירת אובייקט ייצוא
                export = AudioExport(
                    id=id,
                    source_file_id=source_file_id,
                    name=name,
                    path=path,
                    format=format,
                    size=size,
                    duration=duration,
                    created_at=datetime.fromisoformat(created_at),
                    status=status,
                    settings=settings,
                    metadata=metadata
                )
                
                exports.append(export)
            
            conn.close()
            return exports
    
    def get_export_stats(self) -> Dict[str, Any]:
        """
        קבלת סטטיסטיקות על ייצואים
        
        Returns:
            Dict[str, Any]: סטטיסטיקות על ייצואים
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # סך הכל ייצואים
            cursor.execute("SELECT COUNT(*) FROM exports")
            total_count = cursor.fetchone()[0]
            
            # ספירה לפי סטטוס
            cursor.execute("SELECT status, COUNT(*) FROM exports GROUP BY status")
            status_counts = {status: count for status, count in cursor.fetchall()}
            
            # ספירה לפי פורמט
            cursor.execute("SELECT format, COUNT(*) FROM exports GROUP BY format")
            format_counts = {format: count for format, count in cursor.fetchall()}
            
            # סך הכל גודל
            cursor.execute("SELECT SUM(size) FROM exports")
            total_size = cursor.fetchone()[0] or 0
            
            # סך הכל משך
            cursor.execute("SELECT SUM(duration) FROM exports")
            total_duration = cursor.fetchone()[0] or 0
            
            # ייצוא אחרון
            cursor.execute("SELECT created_at FROM exports ORDER BY created_at DESC LIMIT 1")
            last_export = cursor.fetchone()
            last_export_date = datetime.fromisoformat(last_export[0]) if last_export else None
            
            conn.close()
            
            return {
                "total_count": total_count,
                "status_counts": status_counts,
                "format_counts": format_counts,
                "total_size": total_size,
                "total_duration": total_duration,
                "last_export_date": last_export_date.isoformat() if last_export_date else None
            }
    
    def get_export_formats(self) -> List[str]:
        """
        קבלת רשימת פורמטים זמינים
        
        Returns:
            List[str]: רשימת פורמטים
        """
        return ["mp3", "wav", "flac", "ogg", "m4a", "aac"]
    
    def clear_all_exports(self) -> bool:
        """
        מחיקת כל הייצואים
        
        Returns:
            bool: האם המחיקה הצליחה
        """
        try:
            # קבלת כל הייצואים
            exports = self.get_all_exports()
            
            # מחיקת כל הקבצים
            for export in exports:
                try:
                    if os.path.exists(export.path):
                        os.remove(export.path)
                except Exception as e:
                    print(f"שגיאה במחיקת קובץ הייצוא {export.path}: {e}")
            
            # מחיקת כל הרשומות ממסד הנתונים
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM exports")
                
                conn.commit()
                conn.close()
                
                return True
        
        except Exception as e:
            print(f"שגיאה במחיקת כל הייצואים: {e}")
            return False
