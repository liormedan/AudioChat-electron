import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.settings_service import SettingsService


class TestSettingsService(unittest.TestCase):
    """בדיקות יחידה לשירות הגדרות"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        # יצירת קובץ מסד נתונים זמני
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # יצירת שירות עם מסד נתונים זמני
        self.settings_service = SettingsService(db_path=self.temp_db.name)
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        # מחיקת קובץ מסד הנתונים הזמני
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_set_and_get_string_setting(self):
        """בדיקת הגדרה וקבלת הגדרת מחרוזת"""
        key = "test_string"
        value = "test value"
        description = "Test string setting"
        
        # הגדרת ההגדרה
        self.settings_service.set_setting(key, value, description)
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key)
        
        # בדיקות
        self.assertEqual(retrieved_value, value)
    
    def test_set_and_get_int_setting(self):
        """בדיקת הגדרה וקבלת הגדרת מספר שלם"""
        key = "test_int"
        value = 42
        
        # הגדרת ההגדרה
        self.settings_service.set_setting(key, value)
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key)
        
        # בדיקות
        self.assertEqual(retrieved_value, value)
        self.assertIsInstance(retrieved_value, int)
    
    def test_set_and_get_float_setting(self):
        """בדיקת הגדרה וקבלת הגדרת מספר עשרוני"""
        key = "test_float"
        value = 3.14
        
        # הגדרת ההגדרה
        self.settings_service.set_setting(key, value)
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key)
        
        # בדיקות
        self.assertEqual(retrieved_value, value)
        self.assertIsInstance(retrieved_value, float)
    
    def test_set_and_get_bool_setting(self):
        """בדיקת הגדרה וקבלת הגדרת בוליאן"""
        key = "test_bool"
        value = True
        
        # הגדרת ההגדרה
        self.settings_service.set_setting(key, value)
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key)
        
        # בדיקות
        self.assertEqual(retrieved_value, value)
        self.assertIsInstance(retrieved_value, bool)
    
    def test_set_and_get_dict_setting(self):
        """בדיקת הגדרה וקבלת הגדרת מילון"""
        key = "test_dict"
        value = {"name": "test", "count": 5, "enabled": True}
        
        # הגדרת ההגדרה
        self.settings_service.set_setting(key, value)
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key)
        
        # בדיקות
        self.assertEqual(retrieved_value, value)
        self.assertIsInstance(retrieved_value, dict)
    
    def test_set_and_get_list_setting(self):
        """בדיקת הגדרה וקבלת הגדרת רשימה"""
        key = "test_list"
        value = ["item1", "item2", "item3"]
        
        # הגדרת ההגדרה
        self.settings_service.set_setting(key, value)
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key)
        
        # בדיקות
        self.assertEqual(retrieved_value, value)
        self.assertIsInstance(retrieved_value, list)
    
    def test_get_nonexistent_setting_with_default(self):
        """בדיקת קבלת הגדרה שלא קיימת עם ערך ברירת מחדל"""
        key = "nonexistent_setting"
        default_value = "default"
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key, default_value)
        
        # בדיקות
        self.assertEqual(retrieved_value, default_value)
    
    def test_get_nonexistent_setting_without_default(self):
        """בדיקת קבלת הגדרה שלא קיימת ללא ערך ברירת מחדל"""
        key = "nonexistent_setting"
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key)
        
        # בדיקות
        self.assertIsNone(retrieved_value)
    
    def test_update_existing_setting(self):
        """בדיקת עדכון הגדרה קיימת"""
        key = "update_test"
        original_value = "original"
        updated_value = "updated"
        
        # הגדרת ההגדרה המקורית
        self.settings_service.set_setting(key, original_value)
        
        # עדכון ההגדרה
        self.settings_service.set_setting(key, updated_value)
        
        # קבלת ההגדרה
        retrieved_value = self.settings_service.get_setting(key)
        
        # בדיקות
        self.assertEqual(retrieved_value, updated_value)
    
    def test_get_all_settings(self):
        """בדיקת קבלת כל ההגדרות"""
        # הגדרת מספר הגדרות
        settings = {
            "setting1": "value1",
            "setting2": 42,
            "setting3": True,
            "setting4": {"key": "value"}
        }
        
        for key, value in settings.items():
            self.settings_service.set_setting(key, value)
        
        # קבלת כל ההגדרות
        all_settings = self.settings_service.get_all_settings()
        
        # בדיקות
        for key, expected_value in settings.items():
            self.assertIn(key, all_settings)
            self.assertEqual(all_settings[key], expected_value)
    
    def test_delete_setting(self):
        """בדיקת מחיקת הגדרה"""
        key = "delete_test"
        value = "to be deleted"
        
        # הגדרת ההגדרה
        self.settings_service.set_setting(key, value)
        
        # וידוא שההגדרה קיימת
        self.assertEqual(self.settings_service.get_setting(key), value)
        
        # מחיקת ההגדרה
        result = self.settings_service.delete_setting(key)
        
        # בדיקות
        self.assertTrue(result)
        self.assertIsNone(self.settings_service.get_setting(key))
    
    def test_delete_nonexistent_setting(self):
        """בדיקת מחיקת הגדרה שלא קיימת"""
        key = "nonexistent_setting"
        
        # ניסיון מחיקת הגדרה שלא קיימת
        result = self.settings_service.delete_setting(key)
        
        # בדיקות
        self.assertFalse(result)
    
    def test_set_and_get_api_key(self):
        """בדיקת הגדרה וקבלת API key"""
        provider = "TestProvider"
        api_key = "test-api-key-123456"
        
        # הגדרת ה-API key
        result = self.settings_service.set_api_key(provider, api_key)
        self.assertTrue(result)
        
        # קבלת ה-API key
        retrieved_key = self.settings_service.get_api_key(provider)
        
        # בדיקות
        self.assertEqual(retrieved_key, api_key)
    
    def test_get_api_key_masked(self):
        """בדיקת קבלת API key מוסתר"""
        provider = "TestProvider"
        api_key = "test-api-key-123456789"
        
        # הגדרת ה-API key
        self.settings_service.set_api_key(provider, api_key)
        
        # קבלת ה-API key מוסתר
        masked_key = self.settings_service.get_api_key_masked(provider)
        
        # בדיקות
        self.assertNotEqual(masked_key, api_key)
        self.assertTrue(masked_key.startswith("test"))
        self.assertTrue(masked_key.endswith("789"))
        self.assertIn("*", masked_key)
    
    def test_get_api_key_masked_short_key(self):
        """בדיקת קבלת API key מוסתר עבור מפתח קצר"""
        provider = "TestProvider"
        api_key = "short"
        
        # הגדרת ה-API key
        self.settings_service.set_api_key(provider, api_key)
        
        # קבלת ה-API key מוסתר
        masked_key = self.settings_service.get_api_key_masked(provider)
        
        # בדיקות
        self.assertEqual(masked_key, "*" * len(api_key))
    
    def test_has_api_key(self):
        """בדיקת בדיקת קיום API key"""
        provider = "TestProvider"
        api_key = "test-api-key"
        
        # בדיקה שאין מפתח
        self.assertFalse(self.settings_service.has_api_key(provider))
        
        # הגדרת מפתח
        self.settings_service.set_api_key(provider, api_key)
        
        # בדיקה שיש מפתח
        self.assertTrue(self.settings_service.has_api_key(provider))
    
    def test_delete_api_key(self):
        """בדיקת מחיקת API key"""
        provider = "TestProvider"
        api_key = "test-api-key"
        
        # הגדרת מפתח
        self.settings_service.set_api_key(provider, api_key)
        
        # וידוא שהמפתח קיים
        self.assertTrue(self.settings_service.has_api_key(provider))
        
        # מחיקת המפתח
        result = self.settings_service.delete_api_key(provider)
        
        # בדיקות
        self.assertTrue(result)
        self.assertFalse(self.settings_service.has_api_key(provider))
        self.assertIsNone(self.settings_service.get_api_key(provider))
    
    def test_get_all_api_key_providers(self):
        """בדיקת קבלת כל ספקי API keys"""
        providers = ["Provider1", "Provider2", "Provider3"]
        
        # הגדרת מפתחות לספקים
        for provider in providers:
            self.settings_service.set_api_key(provider, f"key-for-{provider}")
        
        # קבלת כל הספקים
        all_providers = self.settings_service.get_all_api_key_providers()
        
        # בדיקות
        self.assertEqual(len(all_providers), len(providers))
        for provider in providers:
            self.assertIn(provider, all_providers)
    
    def test_validate_api_key_exists(self):
        """בדיקת תקינות API key קיים"""
        provider = "TestProvider"
        api_key = "valid-api-key"
        
        # הגדרת מפתח
        self.settings_service.set_api_key(provider, api_key)
        
        # בדיקת תקינות
        is_valid = self.settings_service.validate_api_key(provider)
        
        # בדיקות
        self.assertTrue(is_valid)
    
    def test_validate_api_key_nonexistent(self):
        """בדיקת תקינות API key שלא קיים"""
        provider = "NonexistentProvider"
        
        # בדיקת תקינות
        is_valid = self.settings_service.validate_api_key(provider)
        
        # בדיקות
        self.assertFalse(is_valid)
    
    def test_validate_api_key_empty(self):
        """בדיקת תקינות API key ריק"""
        provider = "TestProvider"
        api_key = ""
        
        # הגדרת מפתח ריק
        self.settings_service.set_api_key(provider, api_key)
        
        # בדיקת תקינות
        is_valid = self.settings_service.validate_api_key(provider)
        
        # בדיקות
        self.assertFalse(is_valid)
    
    def test_export_settings_without_api_keys(self):
        """בדיקת ייצוא הגדרות ללא API keys"""
        # הגדרת כמה הגדרות
        settings = {
            "setting1": "value1",
            "setting2": 42,
            "setting3": True
        }
        
        for key, value in settings.items():
            self.settings_service.set_setting(key, value)
        
        # יצירת קובץ זמני לייצוא
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            # ייצוא הגדרות
            result = self.settings_service.export_settings(temp_path, include_api_keys=False)
            self.assertTrue(result)
            
            # קריאת הקובץ המיוצא
            with open(temp_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            # בדיקות
            self.assertIn("settings", exported_data)
            self.assertIn("exported_at", exported_data)
            self.assertIn("version", exported_data)
            self.assertNotIn("api_keys_masked", exported_data)
            
            # בדיקת הגדרות
            for key, expected_value in settings.items():
                self.assertEqual(exported_data["settings"][key], expected_value)
        
        finally:
            # ניקוי קובץ זמני
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_settings_with_api_keys(self):
        """בדיקת ייצוא הגדרות עם API keys"""
        # הגדרת הגדרות ו-API keys
        self.settings_service.set_setting("test_setting", "test_value")
        self.settings_service.set_api_key("TestProvider", "test-api-key")
        
        # יצירת קובץ זמני לייצוא
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            # ייצוא הגדרות עם API keys
            result = self.settings_service.export_settings(temp_path, include_api_keys=True)
            self.assertTrue(result)
            
            # קריאת הקובץ המיוצא
            with open(temp_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            # בדיקות
            self.assertIn("api_keys_masked", exported_data)
            self.assertIn("warning", exported_data)
            self.assertIn("TestProvider", exported_data["api_keys_masked"])
        
        finally:
            # ניקוי קובץ זמני
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_import_settings(self):
        """בדיקת ייבוא הגדרות"""
        # יצירת נתוני ייבוא
        import_data = {
            "settings": {
                "imported_setting1": "imported_value1",
                "imported_setting2": 123,
                "imported_setting3": False
            },
            "version": "1.0"
        }
        
        # יצירת קובץ זמני לייבוא
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            json.dump(import_data, temp_file, ensure_ascii=False, indent=2)
            temp_path = temp_file.name
        
        try:
            # ייבוא הגדרות
            result = self.settings_service.import_settings(temp_path)
            self.assertTrue(result)
            
            # בדיקת הגדרות מיובאות
            for key, expected_value in import_data["settings"].items():
                retrieved_value = self.settings_service.get_setting(key)
                self.assertEqual(retrieved_value, expected_value)
        
        finally:
            # ניקוי קובץ זמני
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_signals_emitted(self):
        """בדיקת שליחת אותות"""
        # רישום לאותות
        setting_changed_signal = MagicMock()
        api_key_added_signal = MagicMock()
        api_key_removed_signal = MagicMock()
        
        self.settings_service.setting_changed.connect(setting_changed_signal)
        self.settings_service.api_key_added.connect(api_key_added_signal)
        self.settings_service.api_key_removed.connect(api_key_removed_signal)
        
        # פעולות שאמורות לשלוח אותות
        self.settings_service.set_setting("test_key", "test_value")
        self.settings_service.set_api_key("TestProvider", "test-api-key")
        self.settings_service.delete_api_key("TestProvider")
        
        # בדיקת שליחת אותות
        setting_changed_signal.assert_called_with("test_key", "test_value")
        api_key_added_signal.assert_called_with("TestProvider")
        api_key_removed_signal.assert_called_with("TestProvider")


if __name__ == "__main__":
    unittest.main()