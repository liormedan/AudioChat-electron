import os
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.file_utils import get_file_metadata, extract_audio_duration
from ui.components.file_upload.file_info import FileInfo

class FileService:
    """שירות לניהול מידע על קבצי אודיו"""
    
    def __init__(self, db_path: str = None):
        """
        אתחול שירות קבצים
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים. אם לא מסופק, ישתמש בנתיב ברירת מחדל
        """
        if db_path is None:
            # יצירת תיקיית נתונים אם לא קיימת
            data_dir = os.path.join(os.path.expanduser("~"), ".audio_app", "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "audio_files.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """אתחול מסד הנתונים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # יצירת טבלת קבצים אם לא קיימת
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,
            size INTEGER NOT NULL,
            format TEXT NOT NULL,
            duration INTEGER DEFAULT 0,
            upload_date TEXT NOT NULL,
            metadata TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_file_info(self, file_info: FileInfo) -> bool:
        """
        שמירת מידע על קובץ במסד הנתונים
        
        Args:
            file_info (FileInfo): אובייקט המידע על הקובץ
            
        Returns:
            bool: האם השמירה הצליחה
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # בדיקה אם הקובץ כבר קיים
            cursor.execute("SELECT id FROM files WHERE path = ?", (file_info.path,))
            existing_file = cursor.fetchone()
            
            # הכנת מטא-דאטה כ-JSON
            metadata = {}  # ניתן להוסיף כאן מידע נוסף בעתיד
            metadata_json = json.dumps(metadata)
            
            if existing_file:
                # עדכון קובץ קיים
                cursor.execute('''
                UPDATE files
                SET name = ?, size = ?, format = ?, duration = ?, upload_date = ?, metadata = ?
                WHERE path = ?
                ''', (
                    file_info.name,
                    file_info.size,
                    file_info.format,
                    file_info.duration,
                    file_info.upload_date.isoformat(),
                    metadata_json,
                    file_info.path
                ))
            else:
                # הוספת קובץ חדש
                cursor.execute('''
                INSERT INTO files (name, path, size, format, duration, upload_date, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_info.name,
                    file_info.path,
                    file_info.size,
                    file_info.format,
                    file_info.duration,
                    file_info.upload_date.isoformat(),
                    metadata_json
                ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"שגיאה בשמירת מידע על קובץ: {e}")
            return False
    
    def get_recent_files(self, limit: int = 10) -> List[FileInfo]:
        """
        קבלת רשימת הקבצים האחרונים
        
        Args:
            limit (int, optional): מספר מקסימלי של קבצים להחזרה
            
        Returns:
            List[FileInfo]: רשימת אובייקטי FileInfo
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT name, path, size, format, duration, upload_date
            FROM files
            ORDER BY upload_date DESC
            LIMIT ?
            ''', (limit,))
            
            files = []
            for row in cursor.fetchall():
                name, path, size, format, duration, upload_date_str = row
                
                # המרת תאריך מ-ISO לאובייקט datetime
                upload_date = datetime.fromisoformat(upload_date_str)
                
                # יצירת אובייקט FileInfo
                file_info = FileInfo(
                    name=name,
                    path=path,
                    size=size,
                    format=format,
                    duration=duration,
                    upload_date=upload_date
                )
                
                files.append(file_info)
            
            conn.close()
            return files
        
        except Exception as e:
            print(f"שגיאה בטעינת קבצים אחרונים: {e}")
            # Return an empty list if there's an error
            return []
    
    def delete_file(self, file_path: str) -> bool:
        """
        מחיקת מידע על קובץ ממסד הנתונים
        
        Args:
            file_path (str): נתיב הקובץ למחיקה
            
        Returns:
            bool: האם המחיקה הצליחה
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM files WHERE path = ?", (file_path,))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"שגיאה במחיקת מידע על קובץ: {e}")
            return False
    
    def clear_all_files(self) -> bool:
        """
        מחיקת כל המידע על הקבצים ממסד הנתונים
        
        Returns:
            bool: האם המחיקה הצליחה
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM files")
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"שגיאה במחיקת כל המידע על הקבצים: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """
        קבלת מידע על קובץ ספציפי
        
        Args:
            file_path (str): נתיב הקובץ
            
        Returns:
            Optional[FileInfo]: אובייקט FileInfo או None אם הקובץ לא נמצא
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT name, path, size, format, duration, upload_date
            FROM files
            WHERE path = ?
            ''', (file_path,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                name, path, size, format, duration, upload_date_str = row
                
                # המרת תאריך מ-ISO לאובייקט datetime
                upload_date = datetime.fromisoformat(upload_date_str)
                
                # יצירת אובייקט FileInfo
                return FileInfo(
                    name=name,
                    path=path,
                    size=size,
                    format=format,
                    duration=duration,
                    upload_date=upload_date
                )
            
            return None
        
        except Exception as e:
            print(f"שגיאה בטעינת מידע על קובץ: {e}")
            return None
    
    def extract_file_info(self, file_path: str) -> Optional[FileInfo]:
        """
        חילוץ מידע על קובץ אודיו
        
        Args:
            file_path (str): נתיב הקובץ
            
        Returns:
            Optional[FileInfo]: אובייקט FileInfo או None אם לא ניתן לחלץ מידע
        """
        try:
            if not os.path.exists(file_path):
                print(f"הקובץ {file_path} לא קיים")
                return None
            
            # מידע בסיסי
            name = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            format = os.path.splitext(name)[1].lower().replace('.', '')
            
            # חילוץ משך הקובץ
            duration = extract_audio_duration(file_path) or 0
            
            # יצירת אובייקט FileInfo
            return FileInfo(
                name=name,
                path=file_path,
                size=size,
                format=format,
                duration=duration,
                upload_date=datetime.now()
            )
        
        except Exception as e:
            print(f"שגיאה בחילוץ מידע מהקובץ {file_path}: {e}")
            return None
    
    
    def test_with_sample_files(self, sample_files: List[str]) -> Dict[str, Any]:
        """
        בדיקת השירות עם קבצי דוגמה
        
        Args:
            sample_files (List[str]): רשימת נתיבים לקבצי דוגמה
            
        Returns:
            Dict[str, Any]: תוצאות הבדיקה
        """
        results = {
            "success": True,
            "files_processed": 0,
            "files_saved": 0,
            "errors": [],
            "formats_tested": set()
        }
        
        for file_path in sample_files:
            try:
                # חילוץ מידע
                file_info = self.extract_file_info(file_path)
                results["files_processed"] += 1
                
                if file_info:
                    # הוספת הפורמט לרשימת הפורמטים שנבדקו
                    results["formats_tested"].add(file_info.format.lower())
                    
                    # שמירת מידע
                    if self.save_file_info(file_info):
                        results["files_saved"] += 1
                    else:
                        results["errors"].append(f"שגיאה בשמירת מידע על הקובץ: {file_path}")
                else:
                    results["errors"].append(f"לא ניתן לחלץ מידע מהקובץ: {file_path}")
            
            except Exception as e:
                results["errors"].append(f"שגיאה בעיבוד הקובץ {file_path}: {str(e)}")
        
        # המרת סט הפורמטים לרשימה לצורך JSON
        results["formats_tested"] = list(results["formats_tested"])
        
        if results["errors"]:
            results["success"] = False
        
        return results
        
    def test_with_various_formats(self) -> Dict[str, Any]:
        """
        בדיקת השירות עם מגוון פורמטים של קבצי אודיו
        
        Returns:
            Dict[str, Any]: תוצאות הבדיקה
        """
        # יצירת תיקייה זמנית לבדיקות
        import tempfile
        import shutil
        
        test_dir = tempfile.mkdtemp()
        sample_files = []
        
        try:
            # יצירת קבצי דוגמה בפורמטים שונים
            formats = ["mp3", "wav", "flac", "ogg", "m4a", "aac"]
            
            for fmt in formats:
                file_path = os.path.join(test_dir, f"sample.{fmt}")
                with open(file_path, "wb") as f:
                    f.write(f"This is a fake {fmt} file".encode())
                sample_files.append(file_path)
            
            # בדיקת השירות עם הקבצים
            results = self.test_with_sample_files(sample_files)
            
            # הוספת מידע על הפורמטים שנבדקו
            results["expected_formats"] = formats
            
            return results
        
        finally:
            # ניקוי התיקייה הזמנית
            shutil.rmtree(test_dir)
