"""
Message Encryption Service
מספק הצפנה מתקדמת להודעות במסד הנתונים עם ניהול מפתחות אוטומטי
"""

import os
import json
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import sqlite3
import logging

logger = logging.getLogger(__name__)

class EncryptionService:
    """
    שירות הצפנה מתקדם להודעות עם ניהול מפתחות אוטומטי
    """
    
    def __init__(self, db_path: str = "data/encryption_keys.db"):
        self.db_path = db_path
        self.current_key_id = None
        self.key_cache = {}
        self.key_rotation_days = 30  # רוטציה כל 30 יום
        self._init_database()
        self._load_current_key()
    
    def _init_database(self):
        """אתחול מסד נתונים למפתחות הצפנה"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טבלת מפתחות הצפנה
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS encryption_keys (
            key_id TEXT PRIMARY KEY,
            key_data TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            key_version INTEGER DEFAULT 1,
            algorithm TEXT DEFAULT 'AES-256-GCM'
        )
        ''')
        
        # טבלת מטאדטה של הודעות מוצפנות
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS encrypted_messages_metadata (
            message_id TEXT PRIMARY KEY,
            key_id TEXT NOT NULL,
            encryption_timestamp TEXT NOT NULL,
            checksum TEXT NOT NULL,
            FOREIGN KEY (key_id) REFERENCES encryption_keys (key_id)
        )
        ''')
        
        # אינדקסים לביצועים
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_key_active ON encryption_keys (is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_key_expires ON encryption_keys (expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_msg_key ON encrypted_messages_metadata (key_id)')
        
        conn.commit()
        conn.close()
    
    def _generate_key(self) -> Tuple[str, str, str]:
        """יצירת מפתח הצפנה חדש"""
        # יצירת salt אקראי
        salt = secrets.token_bytes(32)
        
        # יצירת מפתח בסיס
        master_password = os.getenv('ENCRYPTION_MASTER_PASSWORD', 'default-master-key-change-in-production')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        
        # יצירת key_id ייחודי
        key_id = hashlib.sha256(salt + key).hexdigest()[:16]
        
        return key_id, key.decode(), base64.b64encode(salt).decode()
    
    def _load_current_key(self):
        """טעינת המפתח הפעיל הנוכחי"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT key_id, key_data, salt FROM encryption_keys 
        WHERE is_active = TRUE AND expires_at > ? 
        ORDER BY created_at DESC LIMIT 1
        ''', (datetime.now().isoformat(),))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            key_id, key_data, salt = result
            self.current_key_id = key_id
            self.key_cache[key_id] = {
                'key': key_data,
                'salt': salt,
                'fernet': Fernet(key_data.encode())
            }
        else:
            # יצירת מפתח ראשון
            self._create_new_key()
    
    def _create_new_key(self) -> str:
        """יצירת מפתח הצפנה חדש ושמירתו במסד הנתונים"""
        key_id, key_data, salt = self._generate_key()
        
        now = datetime.now()
        expires_at = now + timedelta(days=self.key_rotation_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # השבתת מפתחות קודמים
        cursor.execute('UPDATE encryption_keys SET is_active = FALSE')
        
        # הוספת מפתח חדש
        cursor.execute('''
        INSERT INTO encryption_keys 
        (key_id, key_data, salt, created_at, expires_at, is_active, key_version)
        VALUES (?, ?, ?, ?, ?, TRUE, 1)
        ''', (key_id, key_data, salt, now.isoformat(), expires_at.isoformat()))
        
        conn.commit()
        conn.close()
        
        # עדכון cache
        self.current_key_id = key_id
        self.key_cache[key_id] = {
            'key': key_data,
            'salt': salt,
            'fernet': Fernet(key_data.encode())
        }
        
        logger.info(f"Created new encryption key: {key_id}")
        return key_id
    
    def _get_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """קבלת מפתח מה-cache או מהמסד נתונים"""
        if key_id in self.key_cache:
            return self.key_cache[key_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT key_data, salt FROM encryption_keys WHERE key_id = ?
        ''', (key_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            key_data, salt = result
            key_info = {
                'key': key_data,
                'salt': salt,
                'fernet': Fernet(key_data.encode())
            }
            self.key_cache[key_id] = key_info
            return key_info
        
        return None
    
    def encrypt_message(self, message_content: str, message_id: str) -> str:
        """הצפנת תוכן הודעה"""
        try:
            # בדיקה אם נדרשת רוטציה של מפתח
            self._check_key_rotation()
            
            # קבלת המפתח הפעיל
            if not self.current_key_id:
                self._create_new_key()
            
            key_info = self.key_cache[self.current_key_id]
            fernet = key_info['fernet']
            
            # הצפנת התוכן
            encrypted_content = fernet.encrypt(message_content.encode('utf-8'))
            encrypted_b64 = base64.b64encode(encrypted_content).decode('utf-8')
            
            # יצירת checksum
            checksum = hashlib.sha256(message_content.encode('utf-8')).hexdigest()
            
            # שמירת מטאדטה
            self._save_encryption_metadata(message_id, self.current_key_id, checksum)
            
            logger.debug(f"Encrypted message {message_id} with key {self.current_key_id}")
            return encrypted_b64
            
        except Exception as e:
            logger.error(f"Failed to encrypt message {message_id}: {str(e)}")
            raise
    
    def decrypt_message(self, encrypted_content: str, message_id: str) -> str:
        """פענוח תוכן הודעה"""
        try:
            # קבלת מטאדטה של ההצפנה
            metadata = self._get_encryption_metadata(message_id)
            if not metadata:
                raise ValueError(f"No encryption metadata found for message {message_id}")
            
            key_id, checksum = metadata
            
            # קבלת המפתח
            key_info = self._get_key(key_id)
            if not key_info:
                raise ValueError(f"Encryption key {key_id} not found")
            
            fernet = key_info['fernet']
            
            # פענוח התוכן
            encrypted_data = base64.b64decode(encrypted_content.encode('utf-8'))
            decrypted_content = fernet.decrypt(encrypted_data).decode('utf-8')
            
            # אימות checksum
            calculated_checksum = hashlib.sha256(decrypted_content.encode('utf-8')).hexdigest()
            if calculated_checksum != checksum:
                raise ValueError(f"Checksum mismatch for message {message_id}")
            
            logger.debug(f"Decrypted message {message_id} with key {key_id}")
            return decrypted_content
            
        except Exception as e:
            logger.error(f"Failed to decrypt message {message_id}: {str(e)}")
            raise
    
    def _save_encryption_metadata(self, message_id: str, key_id: str, checksum: str):
        """שמירת מטאדטה של הצפנה"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO encrypted_messages_metadata
        (message_id, key_id, encryption_timestamp, checksum)
        VALUES (?, ?, ?, ?)
        ''', (message_id, key_id, datetime.now().isoformat(), checksum))
        
        conn.commit()
        conn.close()
    
    def _get_encryption_metadata(self, message_id: str) -> Optional[Tuple[str, str]]:
        """קבלת מטאדטה של הצפנה"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT key_id, checksum FROM encrypted_messages_metadata 
        WHERE message_id = ?
        ''', (message_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result if result else None
    
    def _check_key_rotation(self):
        """בדיקה אם נדרשת רוטציה של מפתח"""
        if not self.current_key_id:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT expires_at FROM encryption_keys 
        WHERE key_id = ? AND is_active = TRUE
        ''', (self.current_key_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            expires_at = datetime.fromisoformat(result[0])
            if datetime.now() >= expires_at:
                logger.info("Key rotation required - creating new key")
                self._create_new_key()
    
    def rotate_keys(self) -> str:
        """רוטציה ידנית של מפתחות"""
        logger.info("Manual key rotation initiated")
        return self._create_new_key()
    
    def get_key_info(self) -> Dict[str, Any]:
        """קבלת מידע על המפתח הפעיל"""
        if not self.current_key_id:
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT key_id, created_at, expires_at, key_version, algorithm
        FROM encryption_keys 
        WHERE key_id = ? AND is_active = TRUE
        ''', (self.current_key_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            key_id, created_at, expires_at, key_version, algorithm = result
            return {
                'key_id': key_id,
                'created_at': created_at,
                'expires_at': expires_at,
                'key_version': key_version,
                'algorithm': algorithm,
                'days_until_expiry': (datetime.fromisoformat(expires_at) - datetime.now()).days
            }
        
        return {}
    
    def cleanup_old_keys(self, keep_days: int = 90):
        """ניקוי מפתחות ישנים"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # מחיקת מפתחות ישנים (לא פעילים)
        cursor.execute('''
        DELETE FROM encryption_keys 
        WHERE is_active = FALSE AND created_at < ?
        ''', (cutoff_date.isoformat(),))
        
        deleted_keys = cursor.rowcount
        
        # מחיקת מטאדטה של הודעות שהמפתחות שלהן נמחקו
        cursor.execute('''
        DELETE FROM encrypted_messages_metadata 
        WHERE key_id NOT IN (SELECT key_id FROM encryption_keys)
        ''')
        
        deleted_metadata = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted_keys} old keys and {deleted_metadata} metadata records")
        return {'deleted_keys': deleted_keys, 'deleted_metadata': deleted_metadata}
    
    def verify_encryption_integrity(self) -> Dict[str, Any]:
        """אימות תקינות ההצפנה"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # בדיקת מפתחות פעילים
        cursor.execute('SELECT COUNT(*) FROM encryption_keys WHERE is_active = TRUE')
        active_keys = cursor.fetchone()[0]
        
        # בדיקת מטאדטה יתומה
        cursor.execute('''
        SELECT COUNT(*) FROM encrypted_messages_metadata 
        WHERE key_id NOT IN (SELECT key_id FROM encryption_keys)
        ''')
        orphaned_metadata = cursor.fetchone()[0]
        
        # בדיקת מפתחות שפגו
        cursor.execute('''
        SELECT COUNT(*) FROM encryption_keys 
        WHERE is_active = TRUE AND expires_at < ?
        ''', (datetime.now().isoformat(),))
        expired_keys = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'active_keys': active_keys,
            'orphaned_metadata': orphaned_metadata,
            'expired_keys': expired_keys,
            'integrity_ok': orphaned_metadata == 0 and expired_keys == 0 and active_keys > 0
        }


# יצירת instance גלובלי
encryption_service = EncryptionService()


def encrypt_message_content(content: str, message_id: str) -> str:
    """פונקציה נוחה להצפנת הודעה"""
    return encryption_service.encrypt_message(content, message_id)


def decrypt_message_content(encrypted_content: str, message_id: str) -> str:
    """פונקציה נוחה לפענוח הודעה"""
    return encryption_service.decrypt_message(encrypted_content, message_id)


def get_encryption_status() -> Dict[str, Any]:
    """קבלת סטטוס ההצפנה"""
    key_info = encryption_service.get_key_info()
    integrity = encryption_service.verify_encryption_integrity()
    
    return {
        'encryption_enabled': True,
        'current_key': key_info,
        'integrity_check': integrity
    }