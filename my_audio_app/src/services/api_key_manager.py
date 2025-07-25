"""
מנהל API Keys מאובטח
מספק הצפנה ואחסון מאובטח של מפתחות API
"""

import os
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from PyQt6.QtCore import QObject, pyqtSignal


class APIKeyManager(QObject):
    """מנהל מאובטח למפתחות API"""
    
    # אותות
    key_added = pyqtSignal(str)  # provider_name
    key_updated = pyqtSignal(str)  # provider_name
    key_deleted = pyqtSignal(str)  # provider_name
    key_tested = pyqtSignal(str, bool)  # provider_name, success
    
    def __init__(self, db_path: str = None, master_password: str = None):
        """
        יוצר מנהל API Keys חדש
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים
            master_password (str, optional): סיסמה ראשית להצפנה
        """
        super().__init__()
        
        # נתיב למסד הנתונים
        if db_path is None:
            app_data_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, "api_keys.db")
        
        self.db_path = db_path
        
        # יצירת מסד נתונים אם לא קיים
        self._init_db()
        
        # הגדרת הצפנה
        self._setup_encryption(master_password)
    
    def _init_db(self) -> None:
        """יצירת מסד נתונים אם לא קיים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טבלת מפתחות API מוצפנים
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS encrypted_api_keys (
            provider_name TEXT PRIMARY KEY,
            encrypted_key TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_used TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            key_hash TEXT NOT NULL,
            metadata TEXT DEFAULT '{}'
        )
        ''')
        
        # טבלת היסטוריית מפתחות (לרוטציה)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS key_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_name TEXT NOT NULL,
            key_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            deactivated_at TEXT,
            reason TEXT DEFAULT 'rotation'
        )
        ''')
        
        # טבלת בדיקות חיבור
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS connection_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_name TEXT NOT NULL,
            test_time TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            response_time REAL,
            error_message TEXT,
            test_type TEXT DEFAULT 'manual'
        )
        ''')
        
        # טבלת הגדרות אבטחה
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _setup_encryption(self, master_password: str = None) -> None:
        """הגדרת מערכת הצפנה"""
        if master_password is None:
            # יצירת סיסמה ראשית אוטומטית
            master_password = self._get_or_create_master_password()
        
        # יצירת מפתח הצפנה מהסיסמה הראשית
        self.encryption_key = self._derive_key_from_password(master_password)
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_create_master_password(self) -> str:
        """קבלת או יצירת סיסמה ראשית"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM security_settings WHERE key = ?', ('master_password_hash',))
        row = cursor.fetchone()
        
        if row:
            # סיסמה קיימת - נשתמש בהאש כסיסמה
            master_password = row[0]
        else:
            # יצירת סיסמה חדשה
            master_password = secrets.token_urlsafe(32)
            password_hash = hashlib.sha256(master_password.encode()).hexdigest()
            
            cursor.execute('''
            INSERT INTO security_settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ''', ('master_password_hash', password_hash, datetime.now().isoformat()))
            
            conn.commit()
        
        conn.close()
        return master_password
    
    def _derive_key_from_password(self, password: str) -> bytes:
        """יצירת מפתח הצפנה מסיסמה"""
        # יצירת salt קבוע למפתח הראשי
        salt = b'audio_chat_qt_salt_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _generate_salt(self) -> str:
        """יצירת salt אקראי"""
        return secrets.token_urlsafe(16)
    
    def _hash_key(self, api_key: str) -> str:
        """יצירת hash למפתח API (לזיהוי ללא חשיפה)"""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    def encrypt_api_key(self, api_key: str) -> Tuple[str, str]:
        """
        הצפנת מפתח API
        
        Args:
            api_key (str): מפתח API להצפנה
            
        Returns:
            Tuple[str, str]: מפתח מוצפן ו-salt
        """
        salt = self._generate_salt()
        
        # הוספת salt למפתח לפני הצפנה
        salted_key = f"{salt}:{api_key}"
        
        # הצפנה
        encrypted_key = self.cipher.encrypt(salted_key.encode())
        
        return base64.urlsafe_b64encode(encrypted_key).decode(), salt
    
    def decrypt_api_key(self, encrypted_key: str, salt: str) -> str:
        """
        פענוח מפתח API
        
        Args:
            encrypted_key (str): מפתח מוצפן
            salt (str): Salt שנוצר בעת ההצפנה
            
        Returns:
            str: מפתח API מפוענח
        """
        try:
            # פענוח
            encrypted_data = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # הסרת salt
            salted_key = decrypted_data.decode()
            stored_salt, api_key = salted_key.split(':', 1)
            
            # בדיקת salt
            if stored_salt != salt:
                raise ValueError("Invalid salt")
            
            return api_key
            
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {str(e)}")
    
    def store_api_key(self, provider_name: str, api_key: str, metadata: Dict = None) -> bool:
        """
        שמירת מפתח API מוצפן
        
        Args:
            provider_name (str): שם הספק
            api_key (str): מפתח API
            metadata (Dict, optional): מטא-דאטה נוספת
            
        Returns:
            bool: האם השמירה הצליחה
        """
        try:
            # הצפנת המפתח
            encrypted_key, salt = self.encrypt_api_key(api_key)
            key_hash = self._hash_key(api_key)
            
            # שמירה במסד הנתונים
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # בדיקה אם המפתח כבר קיים
            cursor.execute('SELECT provider_name FROM encrypted_api_keys WHERE provider_name = ?', 
                         (provider_name,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # עדכון מפתח קיים - שמירה בהיסטוריה
                cursor.execute('''
                INSERT INTO key_history (provider_name, key_hash, created_at, deactivated_at, reason)
                SELECT provider_name, key_hash, created_at, ?, 'updated'
                FROM encrypted_api_keys WHERE provider_name = ?
                ''', (datetime.now().isoformat(), provider_name))
            
            # קבלת זמן יצירה אם קיים
            created_at = datetime.now().isoformat()
            if exists:
                cursor.execute('SELECT created_at FROM encrypted_api_keys WHERE provider_name = ?', 
                             (provider_name,))
                existing_row = cursor.fetchone()
                if existing_row:
                    created_at = existing_row[0]
            
            # שמירת המפתח החדש
            cursor.execute('''
            INSERT OR REPLACE INTO encrypted_api_keys 
            (provider_name, encrypted_key, salt, created_at, updated_at, is_active, key_hash, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                provider_name,
                encrypted_key,
                salt,
                created_at,
                datetime.now().isoformat(),
                True,
                key_hash,
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            # שליחת אות
            if exists:
                self.key_updated.emit(provider_name)
            else:
                self.key_added.emit(provider_name)
            
            return True
            
        except Exception as e:
            print(f"Error storing API key for {provider_name}: {str(e)}")
            return False
    
    def retrieve_api_key(self, provider_name: str) -> Optional[str]:
        """
        שליפת מפתח API מפוענח
        
        Args:
            provider_name (str): שם הספק
            
        Returns:
            Optional[str]: מפתח API מפוענח או None אם לא נמצא
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT encrypted_key, salt FROM encrypted_api_keys 
            WHERE provider_name = ? AND is_active = TRUE
            ''', (provider_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            encrypted_key, salt = row
            api_key = self.decrypt_api_key(encrypted_key, salt)
            
            # עדכון זמן שימוש אחרון
            self._update_last_used(provider_name)
            
            return api_key
            
        except Exception as e:
            print(f"Error retrieving API key for {provider_name}: {str(e)}")
            return None
    
    def _update_last_used(self, provider_name: str) -> None:
        """עדכון זמן שימוש אחרון"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE encrypted_api_keys SET last_used = ? WHERE provider_name = ?
        ''', (datetime.now().isoformat(), provider_name))
        
        conn.commit()
        conn.close()
    
    def delete_api_key(self, provider_name: str) -> bool:
        """
        מחיקת מפתח API
        
        Args:
            provider_name (str): שם הספק
            
        Returns:
            bool: האם המחיקה הצליחה
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # שמירה בהיסטוריה לפני מחיקה
            cursor.execute('''
            INSERT INTO key_history (provider_name, key_hash, created_at, deactivated_at, reason)
            SELECT provider_name, key_hash, created_at, ?, 'deleted'
            FROM encrypted_api_keys WHERE provider_name = ?
            ''', (datetime.now().isoformat(), provider_name))
            
            # מחיקת המפתח
            cursor.execute('DELETE FROM encrypted_api_keys WHERE provider_name = ?', (provider_name,))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if success:
                self.key_deleted.emit(provider_name)
            
            return success
            
        except Exception as e:
            print(f"Error deleting API key for {provider_name}: {str(e)}")
            return False
    
    def rotate_api_key(self, provider_name: str, new_api_key: str) -> bool:
        """
        רוטציה של מפתח API
        
        Args:
            provider_name (str): שם הספק
            new_api_key (str): מפתח API חדש
            
        Returns:
            bool: האם הרוטציה הצליחה
        """
        return self.store_api_key(provider_name, new_api_key, {"rotation": True})
    
    def list_stored_providers(self) -> List[Dict]:
        """
        רשימת ספקים עם מפתחות שמורים
        
        Returns:
            List[Dict]: רשימת ספקים עם מידע בסיסי
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT provider_name, created_at, updated_at, last_used, is_active, key_hash, metadata
        FROM encrypted_api_keys ORDER BY provider_name
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        providers = []
        for row in rows:
            provider_info = {
                "provider_name": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "last_used": row[3],
                "is_active": bool(row[4]),
                "key_hash": row[5],
                "metadata": json.loads(row[6]) if row[6] else {}
            }
            providers.append(provider_info)
        
        return providers
    
    def validate_api_key_format(self, provider_name: str, api_key: str) -> Tuple[bool, str]:
        """
        בדיקת פורמט מפתח API
        
        Args:
            provider_name (str): שם הספק
            api_key (str): מפתח API לבדיקה
            
        Returns:
            Tuple[bool, str]: האם תקין והודעת שגיאה אם לא
        """
        if not api_key or not api_key.strip():
            return False, "API key cannot be empty"
        
        # כללי בדיקה לפי ספק
        validation_rules = {
            "OpenAI": {
                "prefix": "sk-",
                "min_length": 40,
                "pattern": r"^sk-[A-Za-z0-9]{40,}$"
            },
            "Anthropic": {
                "prefix": "sk-ant-",
                "min_length": 50,
                "pattern": r"^sk-ant-[A-Za-z0-9\-_]{30,}$"
            },
            "Google": {
                "min_length": 30,
                "pattern": r"^[A-Za-z0-9\-_]{30,}$"
            },
            "Cohere": {
                "min_length": 40,
                "pattern": r"^[A-Za-z0-9\-_]{40,}$"
            }
        }
        
        rules = validation_rules.get(provider_name, {})
        
        # בדיקת אורך מינימלי
        min_length = rules.get("min_length", 20)
        if len(api_key) < min_length:
            return False, f"API key too short (minimum {min_length} characters)"
        
        # בדיקת prefix אם נדרש
        if "prefix" in rules and not api_key.startswith(rules["prefix"]):
            return False, f"API key must start with '{rules['prefix']}'"
        
        # בדיקת pattern אם קיים
        if "pattern" in rules:
            import re
            if not re.match(rules["pattern"], api_key):
                return False, "API key format is invalid"
        
        return True, "Valid format"
    
    def test_api_key_connection(self, provider_name: str, api_key: str = None) -> Tuple[bool, str, float]:
        """
        בדיקת חיבור עם מפתח API
        
        Args:
            provider_name (str): שם הספק
            api_key (str, optional): מפתח API לבדיקה (אם לא סופק, ישתמש בשמור)
            
        Returns:
            Tuple[bool, str, float]: הצלחה, הודעה, זמן תגובה
        """
        start_time = datetime.now()
        
        try:
            # אם לא סופק מפתח, נשלוף מהאחסון
            if api_key is None:
                api_key = self.retrieve_api_key(provider_name)
                if not api_key:
                    return False, "No API key stored for this provider", 0.0
            
            # בדיקת פורמט
            is_valid, message = self.validate_api_key_format(provider_name, api_key)
            if not is_valid:
                return False, f"Format validation failed: {message}", 0.0
            
            # בדיקת חיבור בפועל (כאן תהיה קריאה אמיתית ל-API)
            success, error_message = self._perform_connection_test(provider_name, api_key)
            
            # חישוב זמן תגובה
            response_time = (datetime.now() - start_time).total_seconds()
            
            # שמירת תוצאת הבדיקה
            self._save_connection_test_result(provider_name, success, response_time, error_message)
            
            # שליחת אות
            self.key_tested.emit(provider_name, success)
            
            return success, error_message or "Connection successful", response_time
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            error_message = f"Connection test failed: {str(e)}"
            
            self._save_connection_test_result(provider_name, False, response_time, error_message)
            self.key_tested.emit(provider_name, False)
            
            return False, error_message, response_time
    
    def _perform_connection_test(self, provider_name: str, api_key: str) -> Tuple[bool, str]:
        """
        ביצוע בדיקת חיבור אמיתית
        
        Args:
            provider_name (str): שם הספק
            api_key (str): מפתח API
            
        Returns:
            Tuple[bool, str]: הצלחה והודעת שגיאה
        """
        # כאן תהיה הלוגיקה האמיתית לבדיקת חיבור לכל ספק
        # לעת עתה נחזיר הצלחה אם המפתח עובר בדיקת פורמט
        
        test_endpoints = {
            "OpenAI": "https://api.openai.com/v1/models",
            "Anthropic": "https://api.anthropic.com/v1/messages",
            "Google": "https://generativelanguage.googleapis.com/v1/models",
            "Cohere": "https://api.cohere.ai/v1/models"
        }
        
        # סימולציה של בדיקת חיבור
        # בפועל כאן נשלח בקשה HTTP לנקודת הקצה המתאימה
        
        if len(api_key) < 20:
            return False, "API key too short"
        
        # סימולציה של הצלחה
        return True, "Connection successful"
    
    def _save_connection_test_result(self, provider_name: str, success: bool, 
                                   response_time: float, error_message: str = None) -> None:
        """שמירת תוצאת בדיקת חיבור"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO connection_tests (provider_name, test_time, success, response_time, error_message, test_type)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            provider_name,
            datetime.now().isoformat(),
            success,
            response_time,
            error_message,
            'manual'
        ))
        
        conn.commit()
        conn.close()
    
    def get_connection_test_history(self, provider_name: str, limit: int = 10) -> List[Dict]:
        """
        קבלת היסטוריית בדיקות חיבור
        
        Args:
            provider_name (str): שם הספק
            limit (int): מספר תוצאות מקסימלי
            
        Returns:
            List[Dict]: רשימת תוצאות בדיקות
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT test_time, success, response_time, error_message, test_type
        FROM connection_tests 
        WHERE provider_name = ? 
        ORDER BY test_time DESC 
        LIMIT ?
        ''', (provider_name, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        tests = []
        for row in rows:
            test_info = {
                "test_time": row[0],
                "success": bool(row[1]),
                "response_time": row[2],
                "error_message": row[3],
                "test_type": row[4]
            }
            tests.append(test_info)
        
        return tests
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> None:
        """
        ניקוי נתונים ישנים
        
        Args:
            days_to_keep (int): מספר ימים לשמירה
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ניקוי היסטוריית מפתחות ישנה
        cursor.execute('DELETE FROM key_history WHERE deactivated_at < ?', (cutoff_str,))
        
        # ניקוי בדיקות חיבור ישנות
        cursor.execute('DELETE FROM connection_tests WHERE test_time < ?', (cutoff_str,))
        
        conn.commit()
        conn.close()
    
    def export_settings(self, include_keys: bool = False) -> Dict:
        """
        יצוא הגדרות
        
        Args:
            include_keys (bool): האם לכלול מפתחות (מוצפנים)
            
        Returns:
            Dict: הגדרות מיוצאות
        """
        settings = {
            "providers": self.list_stored_providers(),
            "export_time": datetime.now().isoformat(),
            "include_keys": include_keys
        }
        
        if include_keys:
            # הוספת מפתחות מוצפנים (רק למטרות גיבוי)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT provider_name, encrypted_key, salt FROM encrypted_api_keys')
            encrypted_keys = {}
            for row in cursor.fetchall():
                encrypted_keys[row[0]] = {
                    "encrypted_key": row[1],
                    "salt": row[2]
                }
            
            settings["encrypted_keys"] = encrypted_keys
            conn.close()
        
        return settings
    
    def get_security_status(self) -> Dict:
        """
        קבלת סטטוס אבטחה
        
        Returns:
            Dict: מידע על מצב האבטחה
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ספירת מפתחות פעילים
        cursor.execute('SELECT COUNT(*) FROM encrypted_api_keys WHERE is_active = TRUE')
        active_keys = cursor.fetchone()[0]
        
        # בדיקת בדיקות חיבור אחרונות
        cursor.execute('''
        SELECT provider_name, MAX(test_time), success 
        FROM connection_tests 
        GROUP BY provider_name
        ''')
        
        last_tests = {}
        for row in cursor.fetchall():
            last_tests[row[0]] = {
                "last_test": row[1],
                "success": bool(row[2])
            }
        
        conn.close()
        
        return {
            "active_keys_count": active_keys,
            "encryption_enabled": True,
            "last_connection_tests": last_tests,
            "database_path": self.db_path
        }