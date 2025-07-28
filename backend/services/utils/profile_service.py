import os
import sqlite3
from datetime import datetime
from typing import Optional



from models.user_profile import UserProfile


class ProfileService:
    """Service for storing and retrieving :class:`UserProfile`."""

    def __init__(self, db_path: str = None):
        
        if db_path is None:
            app_data_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, "profiles.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                email TEXT NOT NULL,
                avatar_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def save_profile(self, profile: UserProfile) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_profiles
                (id, display_name, email, avatar_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                profile.id,
                profile.display_name,
                profile.email,
                profile.avatar_path,
                profile.created_at.isoformat(),
                profile.updated_at.isoformat(),
            ),
        )
        conn.commit()
        conn.close()
        

    def get_profile(self, profile_id: str) -> Optional[UserProfile]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, display_name, email, avatar_path, created_at, updated_at FROM user_profiles WHERE id = ?",
            (profile_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return UserProfile(
            id=row[0],
            display_name=row[1],
            email=row[2],
            avatar_path=row[3],
            created_at=datetime.fromisoformat(row[4]),
            updated_at=datetime.fromisoformat(row[5]),
        )
