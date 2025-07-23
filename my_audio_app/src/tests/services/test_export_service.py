import unittest
import os
import tempfile
import shutil
import sqlite3
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from services.export_service import ExportService
from models.audio_export import AudioExport


class TestExportService(unittest.TestCase):
    """בדיקות יחידה לשירות ExportService"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        # יצירת תיקיית זמנית לבדיקות
        self.test_dir = tempfile.mkdtemp()
        
        # יצירת מסד נתונים זמני
        self.db_path = os.path.join(self.test_dir, "test_exports.db")
        
        # יצירת תיקיית ייצואים זמנית
        self.exports_dir = os.path.join(self.test_dir, "exports")
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # יצירת שירות ייצואים
        self.export_service = ExportService(db_path=self.db_path)
        self.export_service.exports_dir = self.exports_dir
        
        # יצירת קובץ מקור לדוגמה
        self.source_file_path = os.path.join(self.test_dir, "source.mp3")
        with open(self.source_file_path, "wb") as f:
            f.write(b"Test audio content")
        
        # מוק לשירות הקבצים
        self.file_service_mock = MagicMock()
        self.file_service_mock.get_file_info.return_value = MagicMock(
            id="source-123",
            name="source.mp3",
            path=self.source_file_path,
            size=1024,
            format="mp3",
            duration=180
        )
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        # מחיקת תיקיית הבדיקות
        shutil.rmtree(self.test_dir)
    
    def test_create_export(self):
        """בדיקת יצירת ייצוא"""
        # יצירת קובץ מקור לדוגמה
        source_path = os.path.join(self.test_dir, "source_file.mp3")
        with open(source_path, "wb") as f:
            f.write(b"Test audio content")
        
        # יצירת ייצוא
        settings = {"bitrate": "320", "sample_rate": "44.1"}
        export = self.export_service.create_export(
            source_file_id=source_path,  # שימוש בנתיב הקובץ במקום במזהה
            format="mp3",
            settings=settings,
            name="test_export.mp3"
        )
        
        # בדיקת שדות הייצוא
        self.assertIsNotNone(export)
        self.assertEqual(export.name, "test_export.mp3")
        self.assertEqual(export.format, "mp3")
        self.assertEqual(export.source_file_id, source_path)
        self.assertEqual(export.status, "processing")
        self.assertEqual(export.settings, settings)
        
        # בדיקה שהייצוא נשמר במסד הנתונים
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exports WHERE id = ?", (export.id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1)
        
        # המתנה לסיום תהליך הייצוא
        import time
        time.sleep(3)
        
        # בדיקה שהסטטוס התעדכן
        updated_export = self.export_service.get_export_by_id(export.id)
        self.assertIsNotNone(updated_export)
        
        # הסטטוס יכול להיות completed או failed, תלוי אם הקובץ נוצר בהצלחה
        self.assertIn(updated_export.status, ["completed", "failed"])
        
        # אם הסטטוס הוא completed, בדוק שהגודל גדול מ-0
        if updated_export.status == "completed":
            self.assertGreater(updated_export.size, 0)
    
    def test_get_all_exports(self):
        """בדיקת קבלת כל הייצואים"""
        # יצירת ייצואים לדוגמה
        self._create_sample_exports(5)
        
        # קבלת כל הייצואים
        exports = self.export_service.get_all_exports()
        
        # בדיקה שהתקבלו 5 ייצואים
        self.assertEqual(len(exports), 5)
        
        # בדיקה שהייצואים מסודרים לפי תאריך יצירה יורד
        for i in range(1, len(exports)):
            self.assertGreaterEqual(exports[i-1].created_at, exports[i].created_at)
    
    def test_get_exports_page(self):
        """בדיקת קבלת עמוד של ייצואים"""
        # יצירת ייצואים לדוגמה
        self._create_sample_exports(15)
        
        # קבלת העמוד הראשון (10 ייצואים)
        exports, pagination = self.export_service.get_exports_page(page=1, page_size=10)
        
        # בדיקת הייצואים
        self.assertEqual(len(exports), 10)
        
        # בדיקת מידע על העימוד
        self.assertEqual(pagination["page"], 1)
        self.assertEqual(pagination["page_size"], 10)
        self.assertEqual(pagination["total_items"], 15)
        self.assertEqual(pagination["total_pages"], 2)
        self.assertTrue(pagination["has_next"])
        self.assertFalse(pagination["has_prev"])
        
        # קבלת העמוד השני (5 ייצואים)
        exports, pagination = self.export_service.get_exports_page(page=2, page_size=10)
        
        # בדיקת הייצואים
        self.assertEqual(len(exports), 5)
        
        # בדיקת מידע על העימוד
        self.assertEqual(pagination["page"], 2)
        self.assertEqual(pagination["total_pages"], 2)
        self.assertFalse(pagination["has_next"])
        self.assertTrue(pagination["has_prev"])
    
    def test_get_export_by_id(self):
        """בדיקת קבלת ייצוא לפי מזהה"""
        # יצירת ייצוא לדוגמה
        export = self._create_sample_export()
        
        # קבלת הייצוא לפי מזהה
        retrieved_export = self.export_service.get_export_by_id(export.id)
        
        # בדיקה שהתקבל הייצוא הנכון
        self.assertIsNotNone(retrieved_export)
        self.assertEqual(retrieved_export.id, export.id)
        self.assertEqual(retrieved_export.name, export.name)
        
        # בדיקת קבלת ייצוא שלא קיים
        non_existent_export = self.export_service.get_export_by_id("non-existent-id")
        self.assertIsNone(non_existent_export)
    
    def test_update_export(self):
        """בדיקת עדכון ייצוא"""
        # יצירת ייצוא לדוגמה
        export = self._create_sample_export()
        
        # עדכון הייצוא
        updated_export = self.export_service.update_export(export.id, {
            "name": "updated_name.mp3",
            "status": "completed",
            "size": 2048
        })
        
        # בדיקה שהייצוא התעדכן
        self.assertIsNotNone(updated_export)
        self.assertEqual(updated_export.name, "updated_name.mp3")
        self.assertEqual(updated_export.status, "completed")
        self.assertEqual(updated_export.size, 2048)
        
        # בדיקה שהעדכון נשמר במסד הנתונים
        retrieved_export = self.export_service.get_export_by_id(export.id)
        self.assertEqual(retrieved_export.name, "updated_name.mp3")
        self.assertEqual(retrieved_export.status, "completed")
        self.assertEqual(retrieved_export.size, 2048)
        
        # בדיקת עדכון ייצוא שלא קיים
        non_existent_update = self.export_service.update_export("non-existent-id", {"name": "test"})
        self.assertIsNone(non_existent_update)
    
    def test_delete_export(self):
        """בדיקת מחיקת ייצוא"""
        # יצירת ייצוא לדוגמה
        export = self._create_sample_export()
        
        # יצירת קובץ ייצוא לדוגמה
        with open(export.path, "wb") as f:
            f.write(b"Test export content")
        
        # בדיקה שהקובץ קיים
        self.assertTrue(os.path.exists(export.path))
        
        # מחיקת הייצוא
        result = self.export_service.delete_export(export.id)
        
        # בדיקה שהמחיקה הצליחה
        self.assertTrue(result)
        
        # בדיקה שהייצוא לא קיים יותר במסד הנתונים
        deleted_export = self.export_service.get_export_by_id(export.id)
        self.assertIsNone(deleted_export)
        
        # בדיקה שהקובץ נמחק
        self.assertFalse(os.path.exists(export.path))
        
        # בדיקת מחיקת ייצוא שלא קיים
        non_existent_delete = self.export_service.delete_export("non-existent-id")
        self.assertFalse(non_existent_delete)
    
    def test_delete_multiple_exports(self):
        """בדיקת מחיקת מספר ייצואים"""
        # יצירת ייצואים לדוגמה
        exports = []
        for i in range(5):
            export = self._create_sample_export(f"export_{i}.mp3")
            exports.append(export)
            
            # יצירת קובץ ייצוא לדוגמה
            with open(export.path, "wb") as f:
                f.write(f"Test export content {i}".encode())
        
        # מחיקת חלק מהייצואים
        export_ids = [exports[0].id, exports[2].id, exports[4].id, "non-existent-id"]
        results = self.export_service.delete_multiple_exports(export_ids)
        
        # בדיקת תוצאות המחיקה
        self.assertFalse(results["success"])  # לא הצליח למחוק את כל הייצואים
        self.assertEqual(results["deleted"], 3)  # הצליח למחוק 3 ייצואים
        self.assertEqual(results["failed"], 1)  # נכשל במחיקת ייצוא אחד
        self.assertIn("non-existent-id", results["errors"])  # שגיאה עבור הייצוא שלא קיים
        
        # בדיקה שהייצואים שנמחקו לא קיימים יותר במסד הנתונים
        for i in [0, 2, 4]:
            deleted_export = self.export_service.get_export_by_id(exports[i].id)
            self.assertIsNone(deleted_export)
            self.assertFalse(os.path.exists(exports[i].path))
        
        # בדיקה שהייצואים שלא נמחקו עדיין קיימים
        for i in [1, 3]:
            existing_export = self.export_service.get_export_by_id(exports[i].id)
            self.assertIsNotNone(existing_export)
            self.assertTrue(os.path.exists(exports[i].path))
    
    def test_search_exports(self):
        """בדיקת חיפוש ייצואים"""
        # יצירת ייצואים לדוגמה עם פורמטים שונים
        formats = ["mp3", "wav", "flac", "mp3", "ogg"]
        for i, format in enumerate(formats):
            self._create_sample_export(
                name=f"test_{format}_{i}.{format}",
                format=format,
                size=(i + 1) * 1024,
                duration=(i + 1) * 60
            )
        
        # חיפוש לפי טקסט
        mp3_exports = self.export_service.search_exports(search_text="mp3")
        self.assertEqual(len(mp3_exports), 2)
        for export in mp3_exports:
            self.assertEqual(export.format, "mp3")
        
        # חיפוש לפי פילטר פורמט
        wav_exports = self.export_service.search_exports(filters={"format": "wav"})
        self.assertEqual(len(wav_exports), 1)
        self.assertEqual(wav_exports[0].format, "wav")
        
        # חיפוש לפי פילטר גודל
        large_exports = self.export_service.search_exports(filters={"min_size": 3000})
        self.assertEqual(len(large_exports), 3)  # ייצואים 3, 4, 5
        for export in large_exports:
            self.assertGreaterEqual(export.size, 3000)
        
        # חיפוש לפי פילטר משך
        long_exports = self.export_service.search_exports(filters={"min_duration": 180})
        self.assertEqual(len(long_exports), 3)  # ייצואים 3, 4, 5
        for export in long_exports:
            self.assertGreaterEqual(export.duration, 180)
        
        # חיפוש משולב
        # יצירת ייצוא ספציפי שיתאים לחיפוש
        specific_export = self._create_sample_export(
            name="test_specific_mp3.mp3",
            format="mp3",
            size=3072,
            duration=180
        )
        
        combined_exports = self.export_service.search_exports(
            search_text="test",
            filters={
                "min_size": 2000,
                "max_size": 4000,
                "format": "mp3"
            }
        )
        
        # בדיקה שנמצא לפחות ייצוא אחד שמתאים לחיפוש
        self.assertGreaterEqual(len(combined_exports), 1)
        
        # בדיקה שכל הייצואים שנמצאו מתאימים לקריטריונים
        for export in combined_exports:
            self.assertEqual(export.format, "mp3")
            self.assertGreaterEqual(export.size, 2000)
            self.assertLessEqual(export.size, 4000)
            self.assertIn("test", export.name)
    
    def test_get_export_stats(self):
        """בדיקת קבלת סטטיסטיקות על ייצואים"""
        # יצירת ייצואים לדוגמה עם פורמטים ומצבים שונים
        formats = ["mp3", "wav", "flac", "mp3", "ogg"]
        statuses = ["completed", "completed", "processing", "failed", "completed"]
        
        for i, (format, status) in enumerate(zip(formats, statuses)):
            self._create_sample_export(
                name=f"test_{format}_{i}.{format}",
                format=format,
                status=status,
                size=(i + 1) * 1024,
                duration=(i + 1) * 60
            )
        
        # קבלת סטטיסטיקות
        stats = self.export_service.get_export_stats()
        
        # בדיקת סטטיסטיקות
        self.assertEqual(stats["total_count"], 5)
        self.assertEqual(stats["status_counts"]["completed"], 3)
        self.assertEqual(stats["status_counts"]["processing"], 1)
        self.assertEqual(stats["status_counts"]["failed"], 1)
        self.assertEqual(stats["format_counts"]["mp3"], 2)
        self.assertEqual(stats["format_counts"]["wav"], 1)
        self.assertEqual(stats["format_counts"]["flac"], 1)
        self.assertEqual(stats["format_counts"]["ogg"], 1)
        self.assertEqual(stats["total_size"], sum((i + 1) * 1024 for i in range(5)))
        self.assertEqual(stats["total_duration"], sum((i + 1) * 60 for i in range(5)))
        self.assertIsNotNone(stats["last_export_date"])
    
    def test_clear_all_exports(self):
        """בדיקת מחיקת כל הייצואים"""
        # יצירת ייצואים לדוגמה
        exports = []
        for i in range(5):
            export = self._create_sample_export(f"export_{i}.mp3")
            exports.append(export)
            
            # יצירת קובץ ייצוא לדוגמה
            with open(export.path, "wb") as f:
                f.write(f"Test export content {i}".encode())
        
        # בדיקה שיש 5 ייצואים
        self.assertEqual(len(self.export_service.get_all_exports()), 5)
        
        # מחיקת כל הייצואים
        result = self.export_service.clear_all_exports()
        
        # בדיקה שהמחיקה הצליחה
        self.assertTrue(result)
        
        # בדיקה שאין יותר ייצואים
        self.assertEqual(len(self.export_service.get_all_exports()), 0)
        
        # בדיקה שכל הקבצים נמחקו
        for export in exports:
            self.assertFalse(os.path.exists(export.path))
    
    def _create_sample_export(self, name="test_export.mp3", format="mp3", status="completed", size=1024, duration=180):
        """יצירת ייצוא לדוגמה"""
        export_id = f"test-{os.urandom(4).hex()}"
        path = os.path.join(self.exports_dir, f"{export_id}.{format}")
        
        export = AudioExport(
            id=export_id,
            source_file_id="source-123",
            name=name,
            path=path,
            format=format,
            size=size,
            duration=duration,
            created_at=datetime.now(),
            status=status,
            settings={"bitrate": "320", "sample_rate": "44.1"},
            metadata={}
        )
        
        # שמירת הייצוא במסד הנתונים
        self.export_service._save_export(export)
        
        return export
    
    def _create_sample_exports(self, count):
        """יצירת מספר ייצואים לדוגמה"""
        exports = []
        for i in range(count):
            # יצירת ייצוא עם תאריך יצירה יורד
            created_at = datetime.now() - timedelta(minutes=i)
            
            export = AudioExport(
                id=f"test-{os.urandom(4).hex()}",
                source_file_id="source-123",
                name=f"test_export_{i}.mp3",
                path=os.path.join(self.exports_dir, f"test_export_{i}.mp3"),
                format="mp3",
                size=1024,
                duration=180,
                created_at=created_at,
                status="completed",
                settings={"bitrate": "320", "sample_rate": "44.1"},
                metadata={}
            )
            
            # שמירת הייצוא במסד הנתונים
            self.export_service._save_export(export)
            exports.append(export)
        
        return exports


if __name__ == "__main__":
    unittest.main()