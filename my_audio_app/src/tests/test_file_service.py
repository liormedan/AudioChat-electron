import os
import unittest
import tempfile
import shutil
from datetime import datetime

from services.file_service import FileService
from ui.components.file_upload.file_info import FileInfo


class TestFileService(unittest.TestCase):
    """בדיקות יחידה לשירות קבצים"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        # יצירת תיקייה זמנית לבדיקות
        self.test_dir = tempfile.mkdtemp()
        
        # יצירת מסד נתונים זמני
        self.db_path = os.path.join(self.test_dir, "test_files.db")
        self.file_service = FileService(db_path=self.db_path)
        
        # יצירת קבצי דוגמה
        self.sample_files = []
        self._create_sample_files()
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        # מחיקת התיקייה הזמנית
        shutil.rmtree(self.test_dir)
    
    def _create_sample_files(self):
        """יצירת קבצי דוגמה לבדיקות"""
        # יצירת קובץ MP3 לדוגמה
        mp3_path = os.path.join(self.test_dir, "sample.mp3")
        with open(mp3_path, "wb") as f:
            f.write(b"This is a fake MP3 file")
        self.sample_files.append(mp3_path)
        
        # יצירת קובץ WAV לדוגמה
        wav_path = os.path.join(self.test_dir, "sample.wav")
        with open(wav_path, "wb") as f:
            f.write(b"This is a fake WAV file")
        self.sample_files.append(wav_path)
    
    def test_extract_file_info(self):
        """בדיקת חילוץ מידע מקובץ"""
        # חילוץ מידע מקובץ MP3
        file_info = self.file_service.extract_file_info(self.sample_files[0])
        
        # וידוא שהמידע נכון
        self.assertIsNotNone(file_info)
        self.assertEqual(file_info.name, "sample.mp3")
        self.assertEqual(file_info.format, "mp3")
        self.assertGreater(file_info.size, 0)
    
    def test_save_and_get_file_info(self):
        """בדיקת שמירה וקבלת מידע על קובץ"""
        # יצירת אובייקט FileInfo
        file_info = FileInfo(
            name="test.mp3",
            path="/path/to/test.mp3",
            size=1024,
            format="mp3",
            duration=180,
            upload_date=datetime.now()
        )
        
        # שמירת המידע
        result = self.file_service.save_file_info(file_info)
        self.assertTrue(result)
        
        # קבלת המידע
        retrieved_info = self.file_service.get_file_info("/path/to/test.mp3")
        
        # וידוא שהמידע נכון
        self.assertIsNotNone(retrieved_info)
        self.assertEqual(retrieved_info.name, "test.mp3")
        self.assertEqual(retrieved_info.size, 1024)
        self.assertEqual(retrieved_info.format, "mp3")
        self.assertEqual(retrieved_info.duration, 180)
    
    def test_get_recent_files(self):
        """בדיקת קבלת קבצים אחרונים"""
        # שמירת מספר קבצים
        for i in range(5):
            file_info = FileInfo(
                name=f"test{i}.mp3",
                path=f"/path/to/test{i}.mp3",
                size=1024 * (i + 1),
                format="mp3",
                duration=180,
                upload_date=datetime.now()
            )
            self.file_service.save_file_info(file_info)
        
        # קבלת קבצים אחרונים
        recent_files = self.file_service.get_recent_files(limit=3)
        
        # וידוא שמספר הקבצים נכון
        self.assertEqual(len(recent_files), 3)
    
    def test_delete_file(self):
        """בדיקת מחיקת קובץ"""
        # שמירת קובץ
        file_info = FileInfo(
            name="test.mp3",
            path="/path/to/test.mp3",
            size=1024,
            format="mp3",
            duration=180,
            upload_date=datetime.now()
        )
        self.file_service.save_file_info(file_info)
        
        # מחיקת הקובץ
        result = self.file_service.delete_file("/path/to/test.mp3")
        self.assertTrue(result)
        
        # וידוא שהקובץ נמחק
        retrieved_info = self.file_service.get_file_info("/path/to/test.mp3")
        self.assertIsNone(retrieved_info)
    
    def test_clear_all_files(self):
        """בדיקת מחיקת כל הקבצים"""
        # שמירת מספר קבצים
        for i in range(5):
            file_info = FileInfo(
                name=f"test{i}.mp3",
                path=f"/path/to/test{i}.mp3",
                size=1024 * (i + 1),
                format="mp3",
                duration=180,
                upload_date=datetime.now()
            )
            self.file_service.save_file_info(file_info)
        
        # מחיקת כל הקבצים
        result = self.file_service.clear_all_files()
        self.assertTrue(result)
        
        # וידוא שכל הקבצים נמחקו
        recent_files = self.file_service.get_recent_files()
        self.assertEqual(len(recent_files), 0)
    
    def test_with_sample_files(self):
        """בדיקת השירות עם קבצי דוגמה"""
        # בדיקת השירות עם קבצי דוגמה
        results = self.file_service.test_with_sample_files(self.sample_files)
        
        # וידוא שהבדיקה הצליחה
        self.assertTrue(results["success"])
        self.assertEqual(results["files_processed"], 2)
        self.assertEqual(results["files_saved"], 2)
        self.assertEqual(len(results["errors"]), 0)


if __name__ == "__main__":
    unittest.main()