"""
Migration script to add chat tables to existing database
"""
import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def migrate_chat_tables(db_path: str = None) -> bool:
    """
    Add chat tables to existing database
    
    Args:
        db_path (str, optional): Path to database file
        
    Returns:
        bool: True if migration successful
    """
    if db_path is None:
        app_data_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
        os.makedirs(app_data_dir, exist_ok=True)
        db_path = os.path.join(app_data_dir, "llm_data.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_sessions'")
        if cursor.fetchone():
            logger.info("Chat tables already exist, skipping migration")
            conn.close()
            return True
        
        logger.info("Creating chat tables...")
        
        # Create chat_sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            model_id TEXT NOT NULL,
            user_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            message_count INTEGER DEFAULT 0,
            is_archived BOOLEAN DEFAULT FALSE,
            metadata TEXT DEFAULT '{}'
        )
        ''')
        
        # Create chat_messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            model_id TEXT,
            tokens_used INTEGER,
            response_time REAL,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp)')
        
        # Create migration record
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        ''')
        
        cursor.execute(
            'INSERT INTO migrations (name, applied_at) VALUES (?, ?)',
            ('add_chat_tables', datetime.utcnow().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        logger.info("Chat tables migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def rollback_chat_tables(db_path: str = None) -> bool:
    """
    Rollback chat tables migration
    
    Args:
        db_path (str, optional): Path to database file
        
    Returns:
        bool: True if rollback successful
    """
    if db_path is None:
        app_data_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
        db_path = os.path.join(app_data_dir, "llm_data.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Rolling back chat tables...")
        
        # Drop tables
        cursor.execute('DROP TABLE IF EXISTS chat_messages')
        cursor.execute('DROP TABLE IF EXISTS chat_sessions')
        
        # Remove migration record
        cursor.execute('DELETE FROM migrations WHERE name = ?', ('add_chat_tables',))
        
        conn.commit()
        conn.close()
        
        logger.info("Chat tables rollback completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        return False


if __name__ == "__main__":
    # Run migration
    success = migrate_chat_tables()
    if success:
        print("✅ Chat tables migration completed")
    else:
        print("❌ Chat tables migration failed")