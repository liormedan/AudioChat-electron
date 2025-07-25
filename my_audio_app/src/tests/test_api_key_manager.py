"""
בדיקות למנהל מפתחות API
"""

import os
import tempfile
import unittest
from datetime import datetime
import sys

# הוספת נתיב למודלים
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.api_key_manager import APIKeyManager


class TestAPIKeyManager(unittest.TestCase):
    """בדיקות למנהל מפתחות API"""
    
    def setUp(self):
        """הגדרה לפני כל בדיקה"""
        # יצירת מסד נתונים זמני
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # יצירת מנהל מפתחות
        self.api_key_manager = APIKeyManager(db_path=self.temp_db.name)
        
        # מפתחות לבדיקה
        self.test_keys = {
            "OpenAI": "sk-test1234567890abcdef1234567890abcdef123456",
            "Anthropic": "sk-ant-test1234567890abcdef1234567890abcdef123456789",
            "Google": "AIzaSyTest1234567890abcdef1234567890",
            "Cohere": "test1234567890abcdef1234567890abcdef123456"
        }
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        # מחיקת מסד הנתונים הזמני
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_encryption_decryption(self):
        """בדיקת הצפנה ופענוח"""
        test_key = "sk-test1234567890abcdef"
        
        # הצפנה
        encrypted_key, salt = self.api_key_manager.encrypt_api_key(test_key)
        
        # בדיקה שההצפנה עבדה
        self.assertIsInstance(encrypted_key, str)
        self.assertIsInstance(salt, str)
        self.assertNotEqual(encrypted_key, test_key)
        
        # פענוח
        decrypted_key = self.api_key_manager.decrypt_api_key(encrypted_key, salt)
        
        # בדיקה שהפענוח עבד
        self.assertEqual(decrypted_key, test_key)
    
    def test_store_and_retrieve_api_key(self):
        """בדיקת שמירה ושליפה של מפתח API"""
        provider = "OpenAI"
        api_key = self.test_keys[provider]
        
        # שמירה
        success = self.api_key_manager.store_api_key(provider, api_key)
        self.assertTrue(success)
        
        # שליפה
        retrieved_key = self.api_key_manager.retrieve_api_key(provider)
        self.assertEqual(retrieved_key, api_key)
    
    def test_update_existing_key(self):
        """בדיקת עדכון מפתח קיים"""
        provider = "OpenAI"
        old_key = self.test_keys[provider]
        new_key = "sk-new1234567890abcdef1234567890abcdef123456"
        
        # שמירת מפתח ראשון
        self.api_key_manager.store_api_key(provider, old_key)
        
        # עדכון למפתח חדש
        success = self.api_key_manager.store_api_key(provider, new_key)
        self.assertTrue(success)
        
        # בדיקה שהמפתח החדש נשמר
        retrieved_key = self.api_key_manager.retrieve_api_key(provider)
        self.assertEqual(retrieved_key, new_key)
        self.assertNotEqual(retrieved_key, old_key)
    
    def test_delete_api_key(self):
        """בדיקת מחיקת מפתח API"""
        provider = "OpenAI"
        api_key = self.test_keys[provider]
        
        # שמירה
        self.api_key_manager.store_api_key(provider, api_key)
        
        # בדיקה שהמפתח קיים
        retrieved_key = self.api_key_manager.retrieve_api_key(provider)
        self.assertEqual(retrieved_key, api_key)
        
        # מחיקה
        success = self.api_key_manager.delete_api_key(provider)
        self.assertTrue(success)
        
        # בדיקה שהמפתח נמחק
        retrieved_key = self.api_key_manager.retrieve_api_key(provider)
        self.assertIsNone(retrieved_key)
    
    def test_list_stored_providers(self):
        """בדיקת רשימת ספקים שמורים"""
        # שמירת מספר מפתחות
        for provider, key in self.test_keys.items():
            self.api_key_manager.store_api_key(provider, key)
        
        # קבלת רשימה
        providers = self.api_key_manager.list_stored_providers()
        
        # בדיקות
        self.assertEqual(len(providers), len(self.test_keys))
        
        provider_names = [p["provider_name"] for p in providers]
        for provider in self.test_keys.keys():
            self.assertIn(provider, provider_names)
    
    def test_api_key_format_validation(self):
        """בדיקת תקינות פורמט מפתחות API"""
        # בדיקות תקינות
        valid_tests = [
            ("OpenAI", "sk-test1234567890abcdef1234567890abcdef123456"),
            ("Anthropic", "sk-ant-test1234567890abcdef1234567890abcdef123456789"),
            ("Google", "AIzaSyTest1234567890abcdef1234567890"),
            ("Cohere", "test1234567890abcdef1234567890abcdef123456")
        ]
        
        for provider, key in valid_tests:
            is_valid, message = self.api_key_manager.validate_api_key_format(provider, key)
            self.assertTrue(is_valid, f"Key for {provider} should be valid: {message}")
        
        # בדיקות אי-תקינות
        invalid_tests = [
            ("OpenAI", "invalid-key"),  # לא מתחיל ב-sk-
            ("OpenAI", "sk-short"),     # קצר מדי
            ("Anthropic", "sk-wrong-prefix"),  # לא מתחיל ב-sk-ant-
            ("", "sk-test123"),         # ספק ריק
            ("OpenAI", ""),             # מפתח ריק
        ]
        
        for provider, key in invalid_tests:
            is_valid, message = self.api_key_manager.validate_api_key_format(provider, key)
            self.assertFalse(is_valid, f"Key '{key}' for '{provider}' should be invalid")
    
    def test_key_rotation(self):
        """בדיקת רוטציה של מפתח"""
        provider = "OpenAI"
        old_key = self.test_keys[provider]
        new_key = "sk-rotated1234567890abcdef1234567890abcdef"
        
        # שמירת מפתח ראשון
        self.api_key_manager.store_api_key(provider, old_key)
        
        # רוטציה
        success = self.api_key_manager.rotate_api_key(provider, new_key)
        self.assertTrue(success)
        
        # בדיקה שהמפתח החדש פעיל
        retrieved_key = self.api_key_manager.retrieve_api_key(provider)
        self.assertEqual(retrieved_key, new_key)
    
    def test_connection_test_recording(self):
        """בדיקת רישום תוצאות בדיקת חיבור"""
        provider = "OpenAI"
        api_key = self.test_keys[provider]
        
        # שמירת מפתח
        self.api_key_manager.store_api_key(provider, api_key)
        
        # בדיקת חיבור
        success, message, response_time = self.api_key_manager.test_api_key_connection(provider)
        
        # בדיקה שהתוצאה נרשמה
        history = self.api_key_manager.get_connection_test_history(provider, 1)
        self.assertEqual(len(history), 1)
        
        test_record = history[0]
        self.assertEqual(test_record["success"], success)
        self.assertIsNotNone(test_record["test_time"])
        self.assertIsNotNone(test_record["response_time"])
    
    def test_security_status(self):
        """בדיקת סטטוס אבטחה"""
        # שמירת מספר מפתחות
        for provider, key in list(self.test_keys.items())[:2]:
            self.api_key_manager.store_api_key(provider, key)
        
        # קבלת סטטוס אבטחה
        status = self.api_key_manager.get_security_status()
        
        # בדיקות
        self.assertIn("active_keys_count", status)
        self.assertIn("encryption_enabled", status)
        self.assertIn("database_path", status)
        
        self.assertEqual(status["active_keys_count"], 2)
        self.assertTrue(status["encryption_enabled"])
    
    def test_export_settings(self):
        """בדיקת יצוא הגדרות"""
        # שמירת מפתח
        provider = "OpenAI"
        api_key = self.test_keys[provider]
        self.api_key_manager.store_api_key(provider, api_key)
        
        # יצוא ללא מפתחות
        settings_without_keys = self.api_key_manager.export_settings(include_keys=False)
        
        self.assertIn("providers", settings_without_keys)
        self.assertIn("export_time", settings_without_keys)
        self.assertFalse(settings_without_keys["include_keys"])
        self.assertNotIn("encrypted_keys", settings_without_keys)
        
        # יצוא עם מפתחות
        settings_with_keys = self.api_key_manager.export_settings(include_keys=True)
        
        self.assertTrue(settings_with_keys["include_keys"])
        self.assertIn("encrypted_keys", settings_with_keys)
    
    def test_cleanup_old_data(self):
        """בדיקת ניקוי נתונים ישנים"""
        provider = "OpenAI"
        api_key = self.test_keys[provider]
        
        # שמירת מפתח
        self.api_key_manager.store_api_key(provider, api_key)
        
        # בדיקת חיבור (ליצירת רשומה)
        self.api_key_manager.test_api_key_connection(provider)
        
        # בדיקה שיש נתונים
        history_before = self.api_key_manager.get_connection_test_history(provider)
        self.assertGreater(len(history_before), 0)
        
        # ניקוי (עם 0 ימים - ינקה הכל)
        self.api_key_manager.cleanup_old_data(days_to_keep=0)
        
        # בדיקה שהנתונים נוקו
        history_after = self.api_key_manager.get_connection_test_history(provider)
        self.assertEqual(len(history_after), 0)
    
    def test_hash_key_consistency(self):
        """בדיקת עקביות hash של מפתחות"""
        test_key = "sk-test1234567890abcdef"
        
        # יצירת hash פעמיים
        hash1 = self.api_key_manager._hash_key(test_key)
        hash2 = self.api_key_manager._hash_key(test_key)
        
        # בדיקה שה-hash עקבי
        self.assertEqual(hash1, hash2)
        
        # בדיקה שה-hash שונה למפתחות שונים
        different_key = "sk-different1234567890abcdef"
        hash3 = self.api_key_manager._hash_key(different_key)
        self.assertNotEqual(hash1, hash3)


if __name__ == '__main__':
    unittest.main()
