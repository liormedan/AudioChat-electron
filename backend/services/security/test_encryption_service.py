"""
בדיקות אבטחה לשירות ההצפנה
"""

import unittest
import tempfile
import os
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.services.security.encryption_service import EncryptionService, encrypt_message_content, decrypt_message_content


class TestEncryptionService(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_encryption.db")
        self.service = EncryptionService(db_path=self.db_path)
        
    def tearDown(self):
        """ניקוי אחרי בדיקות"""
        shutil.rmtree(self.temp_dir)
    
    def test_encryption_decryption_basic(self):
        """בדיקת הצפנה ופענוח בסיסי"""
        message_id = "test_msg_001"
        original_content = "זהו תוכן הודעה סודי בעברית"
        
        # הצפנה
        encrypted = self.service.encrypt_message(original_content, message_id)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, original_content)
        
        # פענוח
        decrypted = self.service.decrypt_message(encrypted, message_id)
        self.assertEqual(decrypted, original_content)
    
    def test_encryption_with_special_characters(self):
        """בדיקת הצפנה עם תווים מיוחדים"""
        message_id = "test_msg_002"
        original_content = "הודעה עם תווים מיוחדים: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        encrypted = self.service.encrypt_message(original_content, message_id)
        decrypted = self.service.decrypt_message(encrypted, message_id)
        
        self.assertEqual(decrypted, original_content)
    
    def test_encryption_with_unicode(self):
        """בדיקת הצפנה עם Unicode"""
        message_id = "test_msg_003"
        original_content = "הודעה עם אמוג'י 😀🎉 וסמלים מיוחדים ∑∆∏"
        
        encrypted = self.service.encrypt_message(original_content, message_id)
        decrypted = self.service.decrypt_message(encrypted, message_id)
        
        self.assertEqual(decrypted, original_content)
    
    def test_encryption_with_long_content(self):
        """בדיקת הצפנה עם תוכן ארוך"""
        message_id = "test_msg_004"
        original_content = "הודעה ארוכה מאוד " * 1000  # 20,000 תווים
        
        encrypted = self.service.encrypt_message(original_content, message_id)
        decrypted = self.service.decrypt_message(encrypted, message_id)
        
        self.assertEqual(decrypted, original_content)
    
    def test_different_messages_different_encryption(self):
        """בדיקה שהודעות זהות מוצפנות באופן שונה"""
        content = "תוכן זהה"
        
        encrypted1 = self.service.encrypt_message(content, "msg1")
        encrypted2 = self.service.encrypt_message(content, "msg2")
        
        # ההצפנות צריכות להיות שונות (בגלל salt/nonce)
        self.assertNotEqual(encrypted1, encrypted2)
        
        # אבל הפענוח צריך להחזיר את אותו תוכן
        decrypted1 = self.service.decrypt_message(encrypted1, "msg1")
        decrypted2 = self.service.decrypt_message(encrypted2, "msg2")
        
        self.assertEqual(decrypted1, content)
        self.assertEqual(decrypted2, content)
    
    def test_key_rotation(self):
        """בדיקת רוטציה של מפתחות"""
        message_id = "test_msg_005"
        original_content = "הודעה לפני רוטציה"
        
        # הצפנה עם המפתח הראשון
        old_key_id = self.service.current_key_id
        encrypted1 = self.service.encrypt_message(original_content, message_id)
        
        # רוטציה ידנית
        new_key_id = self.service.rotate_keys()
        self.assertNotEqual(old_key_id, new_key_id)
        
        # הצפנה עם המפתח החדש
        message_id2 = "test_msg_006"
        encrypted2 = self.service.encrypt_message("הודעה אחרי רוטציה", message_id2)
        
        # פענוח של שתי ההודעות צריך לעבוד
        decrypted1 = self.service.decrypt_message(encrypted1, message_id)
        decrypted2 = self.service.decrypt_message(encrypted2, message_id2)
        
        self.assertEqual(decrypted1, original_content)
        self.assertEqual(decrypted2, "הודעה אחרי רוטציה")
    
    def test_invalid_message_id_decryption(self):
        """בדיקת פענוח עם message_id לא תקין"""
        message_id = "test_msg_007"
        original_content = "תוכן הודעה"
        
        encrypted = self.service.encrypt_message(original_content, message_id)
        
        # ניסיון פענוח עם message_id שונה
        with self.assertRaises(ValueError):
            self.service.decrypt_message(encrypted, "wrong_message_id")
    
    def test_corrupted_encrypted_content(self):
        """בדיקת פענוח של תוכן מושחת"""
        message_id = "test_msg_008"
        original_content = "תוכן הודעה"
        
        encrypted = self.service.encrypt_message(original_content, message_id)
        
        # השחתת התוכן המוצפן
        corrupted_encrypted = encrypted[:-5] + "XXXXX"
        
        with self.assertRaises(Exception):
            self.service.decrypt_message(corrupted_encrypted, message_id)
    
    def test_key_info_retrieval(self):
        """בדיקת קבלת מידע על המפתח"""
        key_info = self.service.get_key_info()
        
        self.assertIn('key_id', key_info)
        self.assertIn('created_at', key_info)
        self.assertIn('expires_at', key_info)
        self.assertIn('algorithm', key_info)
        self.assertEqual(key_info['algorithm'], 'AES-256-GCM')
    
    def test_encryption_integrity_verification(self):
        """בדיקת אימות תקינות ההצפנה"""
        integrity = self.service.verify_encryption_integrity()
        
        self.assertIn('active_keys', integrity)
        self.assertIn('orphaned_metadata', integrity)
        self.assertIn('expired_keys', integrity)
        self.assertIn('integrity_ok', integrity)
        self.assertTrue(integrity['integrity_ok'])
    
    def test_cleanup_old_keys(self):
        """בדיקת ניקוי מפתחות ישנים"""
        # יצירת מפתח נוסף
        self.service.rotate_keys()
        
        # ניקוי (עם 0 ימים כדי לנקות הכל)
        result = self.service.cleanup_old_keys(keep_days=0)
        
        self.assertIn('deleted_keys', result)
        self.assertIn('deleted_metadata', result)
    
    def test_checksum_validation(self):
        """בדיקת ולידציה של checksum"""
        message_id = "test_msg_009"
        original_content = "תוכן לבדיקת checksum"
        
        # הצפנה
        encrypted = self.service.encrypt_message(original_content, message_id)
        
        # שינוי ידני של checksum במטאדטה
        import sqlite3
        conn = sqlite3.connect(self.service.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE encrypted_messages_metadata 
        SET checksum = 'invalid_checksum' 
        WHERE message_id = ?
        ''', (message_id,))
        conn.commit()
        conn.close()
        
        # פענוח צריך להיכשל בגלל checksum לא תקין
        with self.assertRaises(ValueError) as context:
            self.service.decrypt_message(encrypted, message_id)
        
        self.assertIn("Checksum mismatch", str(context.exception))
    
    @patch.dict(os.environ, {'ENCRYPTION_MASTER_PASSWORD': 'test-master-password'})
    def test_master_password_usage(self):
        """בדיקת שימוש ב-master password"""
        # יצירת שירות חדש עם master password מותאם
        temp_db = os.path.join(self.temp_dir, "test_master_pwd.db")
        service = EncryptionService(db_path=temp_db)
        
        message_id = "test_msg_010"
        original_content = "תוכן עם master password מותאם"
        
        encrypted = service.encrypt_message(original_content, message_id)
        decrypted = service.decrypt_message(encrypted, message_id)
        
        self.assertEqual(decrypted, original_content)
    
    def test_concurrent_encryption(self):
        """בדיקת הצפנה במקביל"""
        import threading
        import time
        
        results = {}
        errors = []
        
        def encrypt_message(msg_id, content):
            try:
                encrypted = self.service.encrypt_message(content, msg_id)
                decrypted = self.service.decrypt_message(encrypted, msg_id)
                results[msg_id] = (content == decrypted)
            except Exception as e:
                errors.append(str(e))
        
        # יצירת 10 threads להצפנה במקביל
        threads = []
        for i in range(10):
            msg_id = f"concurrent_msg_{i}"
            content = f"תוכן הודעה מספר {i}"
            thread = threading.Thread(target=encrypt_message, args=(msg_id, content))
            threads.append(thread)
            thread.start()
        
        # המתנה לסיום כל ה-threads
        for thread in threads:
            thread.join()
        
        # בדיקת תוצאות
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results.values()))


class TestEncryptionServiceHelpers(unittest.TestCase):
    """בדיקות לפונקציות העזר"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_helpers.db")
        
        # יצירת instance חדש לבדיקות
        global encryption_service
        from backend.services.security.encryption_service import EncryptionService
        encryption_service = EncryptionService(db_path=self.db_path)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_helper_functions(self):
        """בדיקת פונקציות העזר"""
        message_id = "helper_test_001"
        original_content = "תוכן לבדיקת פונקציות עזר"
        
        # בדיקת פונקציית הצפנה
        encrypted = encrypt_message_content(original_content, message_id)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, original_content)
        
        # בדיקת פונקציית פענוח
        decrypted = decrypt_message_content(encrypted, message_id)
        self.assertEqual(decrypted, original_content)
    
    def test_encryption_status(self):
        """בדיקת פונקציית סטטוס ההצפנה"""
        from backend.services.security.encryption_service import get_encryption_status
        
        status = get_encryption_status()
        
        self.assertIn('encryption_enabled', status)
        self.assertIn('current_key', status)
        self.assertIn('integrity_check', status)
        self.assertTrue(status['encryption_enabled'])


if __name__ == '__main__':
    unittest.main()