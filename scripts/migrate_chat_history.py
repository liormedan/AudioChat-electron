import os
import json
import sqlite3
from datetime import datetime


def migrate_db(old_db: str, new_db: str):
    if not os.path.exists(old_db):
        print(f"Old database {old_db} not found")
        return

    if os.path.exists(new_db):
        print(f"New database {new_db} already exists")
        return

    conn_old = sqlite3.connect(old_db)
    cur_old = conn_old.cursor()

    cur_old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_sessions'")
    if not cur_old.fetchone():
        print("Old database does not contain chat_sessions table")
        conn_old.close()
        return

    cur_old.execute("PRAGMA table_info(chat_sessions)")
    columns = [row[1] for row in cur_old.fetchall()]
    if 'data' not in columns:
        print("Database already in new format")
        conn_old.close()
        return

    conn_new = sqlite3.connect(new_db)
    cur_new = conn_new.cursor()

    # create new schema
    cur_new.execute('''
        CREATE TABLE chat_sessions (
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

    cur_new.execute('''
        CREATE TABLE chat_messages (
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

    cur_new.execute('CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id)')
    cur_new.execute('CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at)')
    cur_new.execute('CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id)')
    cur_new.execute('CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp)')

    conn_new.commit()

    cur_old.execute('SELECT session_id, title, created_at, updated_at, data FROM chat_sessions')
    sessions = cur_old.fetchall()
    for sess_id, title, created_at, updated_at, data in sessions:
        session_data = json.loads(data)
        messages = session_data.get('messages', [])
        cur_new.execute(
            'INSERT INTO chat_sessions (id, title, model_id, created_at, updated_at, message_count) VALUES (?, ?, ?, ?, ?, ?)',
            (sess_id, title, 'default', created_at, updated_at, len(messages))
        )
        for msg in messages:
            cur_new.execute(
                'INSERT INTO chat_messages (id, session_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)',
                (
                    msg.get('message_id') or f"{int(datetime.now().timestamp()*1000)}",
                    sess_id,
                    msg.get('sender', 'user'),
                    msg.get('text', ''),
                    msg.get('timestamp'),
                )
            )

    conn_new.commit()
    conn_old.close()
    conn_new.close()
    print(f"Migration complete. New DB: {new_db}")


if __name__ == '__main__':
    default_old = os.path.join(os.path.expanduser('~'), '.audio_chat_qt', 'chat_history.db')
    default_new = os.path.join(os.path.expanduser('~'), '.audio_chat_qt', 'chat_history_v2.db')
    migrate_db(default_old, default_new)
