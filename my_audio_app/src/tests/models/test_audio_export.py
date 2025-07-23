import unittest
from datetime import datetime, timedelta
import json
import os
from models.audio_export import AudioExport


class TestAudioExport(unittest.TestCase):
    """בדיקות יחידה למודל AudioExport"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        # יצירת אובייקט AudioExport לבדיקה
        self.export = AudioExport(
            id="test-id-123",
            source_file_id="source-file-456",
            name="test_export.mp3",
            path="/path/to/test_export.mp3",
            format="mp3",
            size=1024 * 1024 * 5,  # 5 MB
            duration=180,  # 3 minutes
            created_at=datetime.now(),
            status="completed",
            settings={"bitrate": "320", "sample_rate": "44.1"},
            metadata={"artist": "Test Artist", "title": "Test Title"}
        )
    
    def test_size_formatted(self):
        """בדיקת פורמט גודל"""
        # בדיקת גודל בבתים
        small_export = AudioExport(**{**self.export.to_dict(), "size": 500})
        self.assertEqual(small_export.size_formatted, "500 B")
        
        # בדיקת גודל בקילובתים
        kb_export = AudioExport(**{**self.export.to_dict(), "size": 1500})
        self.assertEqual(kb_export.size_formatted, "1.5 KB")
        
        # בדיקת גודל במגהבתים
        mb_export = AudioExport(**{**self.export.to_dict(), "size": 1024 * 1024 * 2.5})
        self.assertEqual(mb_export.size_formatted, "2.5 MB")
        
        # בדיקת גודל בגיגהבתים
        gb_export = AudioExport(**{**self.export.to_dict(), "size": 1024 * 1024 * 1024 * 1.2})
        self.assertEqual(gb_export.size_formatted, "1.2 GB")
    
    def test_duration_formatted(self):
        """בדיקת פורמט משך"""
        # בדיקת משך אפס
        zero_export = AudioExport(**{**self.export.to_dict(), "duration": 0})
        self.assertEqual(zero_export.duration_formatted, "00:00")
        
        # בדיקת משך בדקות ושניות
        minutes_export = AudioExport(**{**self.export.to_dict(), "duration": 125})
        self.assertEqual(minutes_export.duration_formatted, "2:05")
        
        # בדיקת משך בשעות, דקות ושניות
        hours_export = AudioExport(**{**self.export.to_dict(), "duration": 3725})
        self.assertEqual(hours_export.duration_formatted, "1:02:05")
    
    def test_created_at_formatted(self):
        """בדיקת פורמט תאריך יצירה"""
        # בדיקת תאריך היום
        today_export = AudioExport(**{**self.export.to_dict(), "created_at": datetime.now()})
        self.assertTrue(today_export.created_at_formatted.startswith("היום"))
        
        # בדיקת תאריך אתמול
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_export = AudioExport(**{**self.export.to_dict(), "created_at": yesterday})
        self.assertTrue(yesterday_export.created_at_formatted.startswith("אתמול"))
        
        # בדיקת תאריך אחר
        other_date = datetime.now() - timedelta(days=7)
        other_export = AudioExport(**{**self.export.to_dict(), "created_at": other_date})
        self.assertIn(other_date.strftime("%d/%m/%Y"), other_export.created_at_formatted)
    
    def test_extension(self):
        """בדיקת סיומת קובץ"""
        self.assertEqual(self.export.extension, ".mp3")
        
        # בדיקת פורמטים שונים
        wav_export = AudioExport(**{**self.export.to_dict(), "format": "WAV"})
        self.assertEqual(wav_export.extension, ".wav")
    
    def test_filename(self):
        """בדיקת שם קובץ"""
        self.assertEqual(self.export.filename, "test_export.mp3")
        
        # בדיקת נתיב מורכב
        complex_path_export = AudioExport(**{**self.export.to_dict(), "path": "/complex/path/to/file.mp3"})
        self.assertEqual(complex_path_export.filename, "file.mp3")
    
    def test_directory(self):
        """בדיקת תיקיית קובץ"""
        self.assertEqual(self.export.directory, "/path/to")
        
        # בדיקת נתיב פשוט
        simple_path_export = AudioExport(**{**self.export.to_dict(), "path": "file.mp3"})
        self.assertEqual(simple_path_export.directory, "")
    
    def test_status_properties(self):
        """בדיקת תכונות סטטוס"""
        # בדיקת סטטוס הושלם
        completed_export = AudioExport(**{**self.export.to_dict(), "status": "completed"})
        self.assertTrue(completed_export.is_completed)
        self.assertFalse(completed_export.is_processing)
        self.assertFalse(completed_export.is_failed)
        
        # בדיקת סטטוס בתהליך
        processing_export = AudioExport(**{**self.export.to_dict(), "status": "processing"})
        self.assertFalse(processing_export.is_completed)
        self.assertTrue(processing_export.is_processing)
        self.assertFalse(processing_export.is_failed)
        
        # בדיקת סטטוס נכשל
        failed_export = AudioExport(**{**self.export.to_dict(), "status": "failed"})
        self.assertFalse(failed_export.is_completed)
        self.assertFalse(failed_export.is_processing)
        self.assertTrue(failed_export.is_failed)
    
    def test_to_dict(self):
        """בדיקת המרה למילון"""
        export_dict = self.export.to_dict()
        
        # בדיקת שדות חובה
        self.assertEqual(export_dict["id"], self.export.id)
        self.assertEqual(export_dict["name"], self.export.name)
        self.assertEqual(export_dict["format"], self.export.format)
        self.assertEqual(export_dict["size"], self.export.size)
        self.assertEqual(export_dict["duration"], self.export.duration)
        self.assertEqual(export_dict["status"], self.export.status)
        
        # בדיקת המרת תאריך ל-ISO
        self.assertEqual(export_dict["created_at"], self.export.created_at.isoformat())
        
        # בדיקת שדות מורכבים
        self.assertEqual(export_dict["settings"], self.export.settings)
        self.assertEqual(export_dict["metadata"], self.export.metadata)
    
    def test_to_json(self):
        """בדיקת המרה ל-JSON"""
        export_json = self.export.to_json()
        
        # בדיקה שהתוצאה היא מחרוזת
        self.assertIsInstance(export_json, str)
        
        # בדיקה שניתן לפענח את ה-JSON
        export_dict = json.loads(export_json)
        self.assertEqual(export_dict["id"], self.export.id)
        self.assertEqual(export_dict["name"], self.export.name)
    
    def test_from_dict(self):
        """בדיקת יצירה ממילון"""
        export_dict = self.export.to_dict()
        new_export = AudioExport.from_dict(export_dict)
        
        # בדיקת שדות חובה
        self.assertEqual(new_export.id, self.export.id)
        self.assertEqual(new_export.name, self.export.name)
        self.assertEqual(new_export.format, self.export.format)
        self.assertEqual(new_export.size, self.export.size)
        self.assertEqual(new_export.duration, self.export.duration)
        self.assertEqual(new_export.status, self.export.status)
        
        # בדיקת המרת תאריך מ-ISO
        self.assertEqual(new_export.created_at.isoformat(), self.export.created_at.isoformat())
        
        # בדיקת שדות מורכבים
        self.assertEqual(new_export.settings, self.export.settings)
        self.assertEqual(new_export.metadata, self.export.metadata)
    
    def test_from_json(self):
        """בדיקת יצירה מ-JSON"""
        export_json = self.export.to_json()
        new_export = AudioExport.from_json(export_json)
        
        # בדיקת שדות חובה
        self.assertEqual(new_export.id, self.export.id)
        self.assertEqual(new_export.name, self.export.name)
        self.assertEqual(new_export.format, self.export.format)
    
    def test_update(self):
        """בדיקת עדכון שדות"""
        # עדכון שדה בודד
        self.export.update(name="new_name.mp3")
        self.assertEqual(self.export.name, "new_name.mp3")
        
        # עדכון מספר שדות
        self.export.update(
            format="wav",
            size=2048,
            status="processing"
        )
        self.assertEqual(self.export.format, "wav")
        self.assertEqual(self.export.size, 2048)
        self.assertEqual(self.export.status, "processing")
        
        # עדכון שדה שלא קיים (לא אמור להשפיע)
        self.export.update(nonexistent_field="value")
        self.assertFalse(hasattr(self.export, "nonexistent_field"))


if __name__ == "__main__":
    unittest.main()