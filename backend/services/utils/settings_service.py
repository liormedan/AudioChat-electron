import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet

import base64
import hashlib
from services.api_key_manager import APIKeyManager


class SettingsService:
    
    def __init__(self, db_path: str = None):
        """
        יוצר שירות הגדרות חדש
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים
        """
        
        
        # נתיב למסד הנתונים
        if db_path is None:
            app_data_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, "settings.db")
        
        self.db_path = db_path
        
        # יצירת מסד נתונים אם לא קיים
        self._init_db()
        
        # יצירת מפתח הצפנה
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _init_db(self) -> None:
        """יצירת מסד נתונים אם לא קיים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טבלת הגדרות כלליות
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            data_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            description TEXT
        )
        ''')
        
        # טבלת API keys מוצפנים
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            provider TEXT PRIMARY KEY,
            encrypted_key TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_used TEXT,
            is_valid BOOLEAN DEFAULT TRUE
        )
        ''')
        
        # טבלת מפתחות הצפנה
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS encryption_keys (
            id INTEGER PRIMARY KEY,
            key_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """קבלת או יצירת מפתח הצפנה"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # בדיקה אם יש מפתח קיים
        cursor.execute('SELECT key_data FROM encryption_keys WHERE id = 1')
        row = cursor.fetchone()
        
        if row:
            # מפתח קיים
            key_data = row[0]
            conn.close()
            return base64.b64decode(key_data.encode())
        else:
            # יצירת מפתח חדש
            key = Fernet.generate_key()
            key_data = base64.b64encode(key).decode()
            
            cursor.execute('''
            INSERT INTO encryption_keys (id, key_data, created_at)
            VALUES (1, ?, ?)
            ''', (key_data, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return key
    
    # General Settings Management
    def set_setting(self, key: str, value: Any, description: str = None) -> None:
        """
        שמירת הגדרה
        
        Args:
            key (str): מפתח ההגדרה
            value (Any): ערך ההגדרה
            description (str, optional): תיאור ההגדרה
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # קביעת סוג הנתונים
        data_type = type(value).__name__
        
        # המרת הערך למחרוזת JSON
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        elif isinstance(value, bool):
            value_str = str(value).lower()
        else:
            value_str = str(value)
        
        # בדיקה אם ההגדרה קיימת
        cursor.execute('SELECT key FROM settings WHERE key = ?', (key,))
        exists = cursor.fetchone() is not None
        
        now = datetime.now().isoformat()
        
        if exists:
            # עדכון הגדרה קיימת
            cursor.execute('''
            UPDATE settings 
            SET value = ?, data_type = ?, updated_at = ?, description = ?
            WHERE key = ?
            ''', (value_str, data_type, now, description, key))
        else:
            # יצירת הגדרה חדשה
            cursor.execute('''
            INSERT INTO settings (key, value, data_type, created_at, updated_at, description)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (key, value_str, data_type, now, now, description))
        
        conn.commit()
        conn.close()
        
        # שליחת אות
        
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        קבלת הגדרה
        
        Args:
            key (str): מפתח ההגדרה
            default (Any, optional): ערך ברירת מחדל
        
        Returns:
            Any: ערך ההגדרה או ערך ברירת המחדל
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value, data_type FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return default
        
        value_str, data_type = row
        
        # המרת הערך לסוג המקורי
        try:
            if data_type == 'dict' or data_type == 'list':
                return json.loads(value_str)
            elif data_type == 'bool':
                return value_str.lower() == 'true'
            elif data_type == 'int':
                return int(value_str)
            elif data_type == 'float':
                return float(value_str)
            else:
                return value_str
        except:
            return default
    
    def get_all_settings(self) -> Dict[str, Any]:
        """קבלת כל ההגדרות"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value, data_type FROM settings')
        rows = cursor.fetchall()
        conn.close()
        
        settings = {}
        for key, value_str, data_type in rows:
            try:
                if data_type == 'dict' or data_type == 'list':
                    settings[key] = json.loads(value_str)
                elif data_type == 'bool':
                    settings[key] = value_str.lower() == 'true'
                elif data_type == 'int':
                    settings[key] = int(value_str)
                elif data_type == 'float':
                    settings[key] = float(value_str)
                else:
                    settings[key] = value_str
            except:
                settings[key] = value_str
        
        return settings
    
    def delete_setting(self, key: str) -> bool:
        """
        מחיקת הגדרה
        
        Args:
            key (str): מפתח ההגדרה
        
        Returns:
            bool: האם המחיקה הצליחה
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM settings WHERE key = ?', (key,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if success:
            
        
        return success
    
    # API Keys Management
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """
        שמירת API key מוצפן
        
        Args:
            provider (str): שם הספק
            api_key (str): API key
        
        Returns:
            bool: האם השמירה הצליחה
        """
        try:
            # הצפנת ה-API key
            encrypted_key = self.cipher.encrypt(api_key.encode()).decode()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # בדיקה אם הספק קיים
            cursor.execute('SELECT provider FROM api_keys WHERE provider = ?', (provider,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # עדכון מפתח קיים
                cursor.execute('''
                UPDATE api_keys 
                SET encrypted_key = ?, updated_at = ?, is_valid = TRUE
                WHERE provider = ?
                ''', (encrypted_key, now, provider))
            else:
                # יצירת מפתח חדש
                cursor.execute('''
                INSERT INTO api_keys (provider, encrypted_key, created_at, updated_at, is_valid)
                VALUES (?, ?, ?, ?, TRUE)
                ''', (provider, encrypted_key, now, now))
            
            conn.commit()
            conn.close()
            
            # שליחת אות
            
            
            return True
        except Exception as e:
            print(f"Error saving API key for {provider}: {e}")
            return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        קבלת API key מפוענח
        
        Args:
            provider (str): שם הספק
        
        Returns:
            Optional[str]: API key או None אם לא נמצא
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT encrypted_key FROM api_keys WHERE provider = ?', (provider,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        try:
            # פענוח ה-API key
            encrypted_key = row[0]
            decrypted_key = self.cipher.decrypt(encrypted_key.encode()).decode()
            
            # עדכון זמן שימוש אחרון
            self._update_last_used(provider)
            
            return decrypted_key
        except Exception as e:
            print(f"Error decrypting API key for {provider}: {e}")
            return None
    
    def get_api_key_masked(self, provider: str) -> Optional[str]:
        """
        קבלת API key מוסתר (עם כוכביות)
        
        Args:
            provider (str): שם הספק
        
        Returns:
            Optional[str]: API key מוסתר או None אם לא נמצא
        """
        api_key = self.get_api_key(provider)
        if not api_key:
            return None
        
        # הסתרת רוב התווים
        if len(api_key) <= 8:
            return "*" * len(api_key)
        else:
            return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    
    def has_api_key(self, provider: str) -> bool:
        """
        בדיקה האם יש API key לספק
        
        Args:
            provider (str): שם הספק
        
        Returns:
            bool: האם יש API key
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT provider FROM api_keys WHERE provider = ?', (provider,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def delete_api_key(self, provider: str) -> bool:
        """
        מחיקת API key
        
        Args:
            provider (str): שם הספק
        
        Returns:
            bool: האם המחיקה הצליחה
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM api_keys WHERE provider = ?', (provider,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if success:
            
        
        return success
    
    def get_all_api_key_providers(self) -> List[str]:
        """קבלת רשימת כל הספקים עם API keys"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT provider FROM api_keys ORDER BY provider')
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def validate_api_key(self, provider: str) -> bool:
        """
        בדיקת תקינות API key (placeholder)
        
        Args:
            provider (str): שם הספק
        
        Returns:
            bool: האם המפתח תקין
        """
        api_key = self.get_api_key(provider)
        if not api_key:
            self._update_key_validity(provider, False)
            return False

        # השתמש ב‑APIKeyManager כדי לבצע בדיקת חיבור אמיתית
        api_key_manager = APIKeyManager(self.db_path.replace("settings.db", "api_keys.db"))
        success, _msg, _time = api_key_manager.test_api_key_connection(provider, api_key)

        # עדכון סטטוס התקינות במסד הנתונים
        self._update_key_validity(provider, success)

        return success
    
    def _update_last_used(self, provider: str) -> None:
        """עדכון זמן שימוש אחרון"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE api_keys SET last_used = ? WHERE provider = ?
        ''', (datetime.now().isoformat(), provider))
        
        conn.commit()
        conn.close()
    
    def _update_key_validity(self, provider: str, is_valid: bool) -> None:
        """עדכון תקינות מפתח"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE api_keys SET is_valid = ? WHERE provider = ?
        ''', (is_valid, provider))
        
        conn.commit()
        conn.close()
    
    # Export/Import Settings
    def export_settings(self, file_path: str, include_api_keys: bool = False) -> bool:
        """
        ייצוא הגדרות לקובץ
        
        Args:
            file_path (str): נתיב הקובץ
            include_api_keys (bool): האם לכלול API keys
        
        Returns:
            bool: האם הייצוא הצליח
        """
        try:
            settings = self.get_all_settings()
            
            export_data = {
                "settings": settings,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            if include_api_keys:
                # הוספת API keys (מוסתרים)
                providers = self.get_all_api_key_providers()
                api_keys = {}
                for provider in providers:
                    api_keys[provider] = self.get_api_key_masked(provider)
                export_data["api_keys_masked"] = api_keys
                export_data["warning"] = "API keys are masked for security. You'll need to re-enter them after import."
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        ייבוא הגדרות מקובץ
        
        Args:
            file_path (str): נתיב הקובץ
        
        Returns:
            bool: האם הייבוא הצליח
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # ייבוא הגדרות
            if "settings" in import_data:
                for key, value in import_data["settings"].items():
                    self.set_setting(key, value)
            
            return True
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
