"""
Optimized Database Service
שירות מסד נתונים מותאם לביצועים עם connection pooling, batch operations ואופטימיזציות
"""

import os
import sqlite3
import threading
import logging
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
import weakref

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """סוגי queries שונים"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    BATCH = "BATCH"

@dataclass
class QueryStats:
    """סטטיסטיקות query"""
    query_type: QueryType
    execution_time: float
    rows_affected: int
    timestamp: datetime
    query_hash: str
    error: Optional[str] = None

@dataclass
class ConnectionPoolStats:
    """סטטיסטיקות connection pool"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    created_connections: int = 0
    closed_connections: int = 0
    pool_hits: int = 0
    pool_misses: int = 0
    wait_time_total: float = 0.0
    max_wait_time: float = 0.0

class DatabaseConnection:
    """מחלקה לניהול חיבור בודד למסד הנתונים"""
    
    def __init__(self, db_path: str, connection_id: str):
        self.db_path = db_path
        self.connection_id = connection_id
        self.connection: Optional[sqlite3.Connection] = None
        self.created_at = datetime.utcnow()
        self.last_used = datetime.utcnow()
        self.query_count = 0
        self.is_active = False
        self.thread_id = None
        self._lock = threading.Lock()
    
    def connect(self) -> sqlite3.Connection:
        """יצירת חיבור למסד הנתונים"""
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0,
                isolation_level=None  # Autocommit mode
            )
            
            # הגדרות אופטימיזציה
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA synchronous=NORMAL")
            self.connection.execute("PRAGMA cache_size=10000")
            self.connection.execute("PRAGMA temp_store=MEMORY")
            self.connection.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            # Row factory לתוצאות נוחות יותר
            self.connection.row_factory = sqlite3.Row
            
        return self.connection
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """ביצוע query"""
        with self._lock:
            self.last_used = datetime.utcnow()
            self.query_count += 1
            self.is_active = True
            self.thread_id = threading.current_thread().ident
            
            try:
                conn = self.connect()
                cursor = conn.execute(query, params)
                return cursor
            finally:
                self.is_active = False
    
    def executemany(self, query: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """ביצוע batch query"""
        with self._lock:
            self.last_used = datetime.utcnow()
            self.query_count += len(params_list)
            self.is_active = True
            self.thread_id = threading.current_thread().ident
            
            try:
                conn = self.connect()
                cursor = conn.executemany(query, params_list)
                return cursor
            finally:
                self.is_active = False
    
    def close(self):
        """סגירת החיבור"""
        with self._lock:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.is_active = False
    
    @property
    def age_seconds(self) -> float:
        """גיל החיבור בשניות"""
        return (datetime.utcnow() - self.created_at).total_seconds()
    
    @property
    def idle_seconds(self) -> float:
        """זמן חוסר פעילות בשניות"""
        return (datetime.utcnow() - self.last_used).total_seconds()

class ConnectionPool:
    """Connection pool למסד הנתונים"""
    
    def __init__(self, db_path: str, min_connections: int = 2, max_connections: int = 10, 
                 max_idle_time: int = 300, cleanup_interval: int = 60):
        self.db_path = db_path
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.cleanup_interval = cleanup_interval
        
        self._connections: Dict[str, DatabaseConnection] = {}
        self._available_connections: Queue = Queue()
        self._lock = threading.RLock()
        self._stats = ConnectionPoolStats()
        
        # Cleanup thread
        self._cleanup_thread = None
        self._shutdown = False
        
        # אתחול pool
        self._initialize_pool()
        self._start_cleanup_thread()
    
    def _initialize_pool(self):
        """אתחול connection pool עם מספר חיבורים מינימלי"""
        for i in range(self.min_connections):
            conn_id = f"conn_{i}_{int(time.time())}"
            db_conn = DatabaseConnection(self.db_path, conn_id)
            
            with self._lock:
                self._connections[conn_id] = db_conn
                self._available_connections.put(conn_id)
                self._stats.total_connections += 1
                self._stats.created_connections += 1
                self._stats.idle_connections += 1
    
    @contextmanager
    def get_connection(self, timeout: float = 30.0):
        """קבלת חיבור מה-pool"""
        start_time = time.time()
        connection_id = None
        
        try:
            # ניסיון קבלת חיבור זמין
            try:
                connection_id = self._available_connections.get(timeout=timeout)
                wait_time = time.time() - start_time
                
                with self._lock:
                    self._stats.pool_hits += 1
                    self._stats.wait_time_total += wait_time
                    self._stats.max_wait_time = max(self._stats.max_wait_time, wait_time)
                    self._stats.active_connections += 1
                    self._stats.idle_connections -= 1
                
            except Empty:
                # אין חיבורים זמינים - ניסיון יצירת חיבור חדש
                if len(self._connections) < self.max_connections:
                    connection_id = self._create_new_connection()
                    wait_time = time.time() - start_time
                    
                    with self._lock:
                        self._stats.pool_misses += 1
                        self._stats.wait_time_total += wait_time
                        self._stats.active_connections += 1
                else:
                    raise TimeoutError(f"No database connections available within {timeout}s")
            
            # החזרת החיבור
            db_connection = self._connections[connection_id]
            yield db_connection
            
        finally:
            # החזרת החיבור ל-pool
            if connection_id:
                with self._lock:
                    self._stats.active_connections -= 1
                    self._stats.idle_connections += 1
                
                self._available_connections.put(connection_id)
    
    def _create_new_connection(self) -> str:
        """יצירת חיבור חדש"""
        conn_id = f"conn_{len(self._connections)}_{int(time.time())}"
        db_conn = DatabaseConnection(self.db_path, conn_id)
        
        with self._lock:
            self._connections[conn_id] = db_conn
            self._stats.total_connections += 1
            self._stats.created_connections += 1
        
        return conn_id
    
    def _start_cleanup_thread(self):
        """התחלת thread לניקוי חיבורים ישנים"""
        def cleanup_worker():
            while not self._shutdown:
                try:
                    time.sleep(self.cleanup_interval)
                    self._cleanup_idle_connections()
                except Exception as e:
                    logger.error(f"Connection pool cleanup error: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_idle_connections(self):
        """ניקוי חיבורים שלא בשימוש"""
        with self._lock:
            connections_to_remove = []
            
            for conn_id, db_conn in self._connections.items():
                if (not db_conn.is_active and 
                    db_conn.idle_seconds > self.max_idle_time and
                    len(self._connections) > self.min_connections):
                    connections_to_remove.append(conn_id)
            
            for conn_id in connections_to_remove:
                try:
                    # הסרה מהqueue אם קיים
                    temp_queue = Queue()
                    while not self._available_connections.empty():
                        try:
                            item = self._available_connections.get_nowait()
                            if item != conn_id:
                                temp_queue.put(item)
                        except Empty:
                            break
                    
                    # החזרת הפריטים לqueue
                    while not temp_queue.empty():
                        self._available_connections.put(temp_queue.get_nowait())
                    
                    # סגירת החיבור
                    db_conn = self._connections.pop(conn_id)
                    db_conn.close()
                    
                    self._stats.total_connections -= 1
                    self._stats.closed_connections += 1
                    self._stats.idle_connections -= 1
                    
                    logger.debug(f"Cleaned up idle connection: {conn_id}")
                    
                except Exception as e:
                    logger.error(f"Error cleaning up connection {conn_id}: {e}")
    
    def get_stats(self) -> ConnectionPoolStats:
        """קבלת סטטיסטיקות pool"""
        with self._lock:
            return ConnectionPoolStats(
                total_connections=self._stats.total_connections,
                active_connections=self._stats.active_connections,
                idle_connections=self._stats.idle_connections,
                created_connections=self._stats.created_connections,
                closed_connections=self._stats.closed_connections,
                pool_hits=self._stats.pool_hits,
                pool_misses=self._stats.pool_misses,
                wait_time_total=self._stats.wait_time_total,
                max_wait_time=self._stats.max_wait_time
            )
    
    def close_all(self):
        """סגירת כל החיבורים"""
        self._shutdown = True
        
        with self._lock:
            for db_conn in self._connections.values():
                db_conn.close()
            
            self._connections.clear()
            
            # ניקוי queue
            while not self._available_connections.empty():
                try:
                    self._available_connections.get_nowait()
                except Empty:
                    break
            
            self._stats = ConnectionPoolStats()

class BatchOperation:
    """מחלקה לביצוע batch operations"""
    
    def __init__(self, operation_type: str, table_name: str):
        self.operation_type = operation_type
        self.table_name = table_name
        self.operations: List[Tuple[str, tuple]] = []
        self.batch_size = 1000
    
    def add_operation(self, query: str, params: tuple):
        """הוספת פעולה ל-batch"""
        self.operations.append((query, params))
    
    def execute(self, db_connection: DatabaseConnection) -> int:
        """ביצוע כל הפעולות ב-batch"""
        if not self.operations:
            return 0
        
        total_affected = 0
        
        # קיבוץ פעולות לפי query
        query_groups = {}
        for query, params in self.operations:
            if query not in query_groups:
                query_groups[query] = []
            query_groups[query].append(params)
        
        # ביצוע כל קבוצה
        for query, params_list in query_groups.items():
            # חלוקה ל-batches קטנים יותר
            for i in range(0, len(params_list), self.batch_size):
                batch_params = params_list[i:i + self.batch_size]
                cursor = db_connection.executemany(query, batch_params)
                total_affected += cursor.rowcount
        
        return total_affected

class OptimizedDatabaseService:
    """
    שירות מסד נתונים מותאם לביצועים
    """
    
    def __init__(self, db_path: str = None, pool_config: Dict[str, Any] = None):
        if db_path is None:
            app_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "llm_data.db")
        
        self.db_path = db_path
        
        # הגדרות connection pool
        pool_config = pool_config or {}
        self.connection_pool = ConnectionPool(
            db_path=db_path,
            min_connections=pool_config.get('min_connections', 2),
            max_connections=pool_config.get('max_connections', 10),
            max_idle_time=pool_config.get('max_idle_time', 300),
            cleanup_interval=pool_config.get('cleanup_interval', 60)
        )
        
        # סטטיסטיקות queries
        self.query_stats: List[QueryStats] = []
        self.stats_lock = threading.Lock()
        self.max_stats_history = 10000
        
        # אתחול מסד הנתונים
        self._initialize_database()
        
        logger.info(f"OptimizedDatabaseService initialized with pool: {pool_config}")
    
    def _initialize_database(self):
        """אתחול מסד הנתונים עם אופטימיזציות"""
        with self.connection_pool.get_connection() as db_conn:
            # יצירת טבלאות
            self._create_tables(db_conn)
            
            # יצירת אינדקסים מותאמים
            self._create_optimized_indexes(db_conn)
            
            # הגדרות אופטימיזציה גלובליות
            self._apply_global_optimizations(db_conn)
    
    def _create_tables(self, db_conn: DatabaseConnection):
        """יצירת טבלאות מסד הנתונים"""
        
        # טבלת sessions
        db_conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            model_id TEXT NOT NULL,
            user_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            message_count INTEGER DEFAULT 0,
            is_archived BOOLEAN DEFAULT FALSE,
            metadata TEXT DEFAULT '{}',
            -- אופטימיזציות נוספות
            last_message_at TEXT,
            total_tokens INTEGER DEFAULT 0,
            avg_response_time REAL DEFAULT 0.0
        )
        ''')
        
        # טבלת messages
        db_conn.execute('''
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
            -- אופטימיזציות נוספות
            content_hash TEXT,
            content_length INTEGER,
            is_encrypted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
        ''')
        
        # טבלת סטטיסטיקות (לביצועים)
        db_conn.execute('''
        CREATE TABLE IF NOT EXISTS query_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_type TEXT NOT NULL,
            query_hash TEXT NOT NULL,
            execution_time REAL NOT NULL,
            rows_affected INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            error_message TEXT
        )
        ''')
        
        # טבלת cache metadata
        db_conn.execute('''
        CREATE TABLE IF NOT EXISTS cache_metadata (
            cache_key TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT NOT NULL,
            data_size INTEGER DEFAULT 0
        )
        ''')
    
    def _create_optimized_indexes(self, db_conn: DatabaseConnection):
        """יצירת אינדקסים מותאמים לביצועים"""
        
        # אינדקסים בסיסיים
        indexes = [
            # Chat sessions indexes
            "CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_chat_sessions_archived ON chat_sessions(is_archived, updated_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_updated ON chat_sessions(user_id, updated_at DESC)",
            
            # Chat messages indexes
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_timestamp ON chat_messages(session_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_model_id ON chat_messages(model_id)",
            
            # Performance indexes
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_tokens ON chat_messages(tokens_used) WHERE tokens_used IS NOT NULL",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_response_time ON chat_messages(response_time) WHERE response_time IS NOT NULL",
            
            # Search indexes
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_content_length ON chat_messages(content_length)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_content_hash ON chat_messages(content_hash)",
            
            # Query performance indexes
            "CREATE INDEX IF NOT EXISTS idx_query_performance_timestamp ON query_performance(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_query_performance_type ON query_performance(query_type, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_query_performance_hash ON query_performance(query_hash)",
            
            # Cache metadata indexes
            "CREATE INDEX IF NOT EXISTS idx_cache_metadata_expires ON cache_metadata(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_cache_metadata_accessed ON cache_metadata(last_accessed DESC)"
        ]
        
        for index_sql in indexes:
            try:
                db_conn.execute(index_sql)
                logger.debug(f"Created index: {index_sql}")
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")
    
    def _apply_global_optimizations(self, db_conn: DatabaseConnection):
        """הגדרות אופטימיזציה גלובליות"""
        optimizations = [
            "PRAGMA journal_mode=WAL",
            "PRAGMA synchronous=NORMAL", 
            "PRAGMA cache_size=10000",
            "PRAGMA temp_store=MEMORY",
            "PRAGMA mmap_size=268435456",  # 256MB
            "PRAGMA page_size=4096",
            "PRAGMA auto_vacuum=INCREMENTAL",
            "PRAGMA optimize"
        ]
        
        for pragma in optimizations:
            try:
                db_conn.execute(pragma)
                logger.debug(f"Applied optimization: {pragma}")
            except Exception as e:
                logger.warning(f"Failed to apply optimization {pragma}: {e}")
    
    def execute_query(self, query: str, params: tuple = (), 
                     query_type: QueryType = QueryType.SELECT) -> sqlite3.Cursor:
        """ביצוע query בודד עם מעקב ביצועים"""
        start_time = time.time()
        query_hash = str(hash(query))
        error = None
        rows_affected = 0
        
        try:
            with self.connection_pool.get_connection() as db_conn:
                cursor = db_conn.execute(query, params)
                rows_affected = cursor.rowcount
                return cursor
                
        except Exception as e:
            error = str(e)
            logger.error(f"Query execution failed: {e}")
            raise
        
        finally:
            execution_time = time.time() - start_time
            
            # שמירת סטטיסטיקות
            self._record_query_stats(
                query_type=query_type,
                execution_time=execution_time,
                rows_affected=rows_affected,
                query_hash=query_hash,
                error=error
            )
    
    def execute_batch(self, batch_operation: BatchOperation) -> int:
        """ביצוע batch operations"""
        start_time = time.time()
        
        try:
            with self.connection_pool.get_connection() as db_conn:
                total_affected = batch_operation.execute(db_conn)
                
                execution_time = time.time() - start_time
                self._record_query_stats(
                    query_type=QueryType.BATCH,
                    execution_time=execution_time,
                    rows_affected=total_affected,
                    query_hash=f"batch_{batch_operation.operation_type}_{batch_operation.table_name}"
                )
                
                return total_affected
                
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_query_stats(
                query_type=QueryType.BATCH,
                execution_time=execution_time,
                rows_affected=0,
                query_hash=f"batch_{batch_operation.operation_type}_{batch_operation.table_name}",
                error=str(e)
            )
            raise
    
    def _record_query_stats(self, query_type: QueryType, execution_time: float,
                           rows_affected: int, query_hash: str, error: str = None):
        """רישום סטטיסטיקות query"""
        with self.stats_lock:
            stat = QueryStats(
                query_type=query_type,
                execution_time=execution_time,
                rows_affected=rows_affected,
                timestamp=datetime.utcnow(),
                query_hash=query_hash,
                error=error
            )
            
            self.query_stats.append(stat)
            
            # ניקוי סטטיסטיקות ישנות
            if len(self.query_stats) > self.max_stats_history:
                self.query_stats = self.query_stats[-self.max_stats_history//2:]
    
    # Session operations with optimizations
    def get_session_with_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """קבלת session עם סטטיסטיקות מותאמות"""
        query = '''
        SELECT s.*,
               COUNT(m.id) as actual_message_count,
               MAX(m.timestamp) as last_message_timestamp,
               SUM(m.tokens_used) as total_tokens_used,
               AVG(m.response_time) as avg_response_time
        FROM chat_sessions s
        LEFT JOIN chat_messages m ON s.id = m.session_id
        WHERE s.id = ?
        GROUP BY s.id
        '''
        
        cursor = self.execute_query(query, (session_id,), QueryType.SELECT)
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_user_sessions_paginated(self, user_id: str = None, limit: int = 50, 
                                   offset: int = 0, include_archived: bool = False) -> Dict[str, Any]:
        """קבלת sessions של משתמש עם pagination מותאם"""
        
        # בניית query דינמי
        base_query = '''
        SELECT s.*,
               COUNT(m.id) as message_count,
               MAX(m.timestamp) as last_message_at
        FROM chat_sessions s
        LEFT JOIN chat_messages m ON s.id = m.session_id
        '''
        
        conditions = []
        params = []
        
        if user_id:
            conditions.append("s.user_id = ?")
            params.append(user_id)
        
        if not include_archived:
            conditions.append("s.is_archived = FALSE")
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " GROUP BY s.id ORDER BY s.updated_at DESC"
        
        # Count query לסך הכל
        count_query = base_query.replace(
            "SELECT s.*, COUNT(m.id) as message_count, MAX(m.timestamp) as last_message_at",
            "SELECT COUNT(DISTINCT s.id)"
        ).replace("GROUP BY s.id ORDER BY s.updated_at DESC", "")
        
        # ביצוע queries
        count_cursor = self.execute_query(count_query, tuple(params), QueryType.SELECT)
        total_count = int(count_cursor.fetchone()[0])
        
        # הוספת pagination
        paginated_query = base_query + " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = self.execute_query(paginated_query, tuple(params), QueryType.SELECT)
        sessions = [dict(row) for row in cursor.fetchall()]
        
        return {
            "sessions": sessions,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(sessions) < total_count
        }
    
    def save_messages_batch(self, messages_data: List[Dict[str, Any]]) -> int:
        """שמירת הודעות מרובות ב-batch"""
        if not messages_data:
            return 0
        
        batch = BatchOperation("INSERT", "chat_messages")
        
        insert_query = '''
        INSERT INTO chat_messages 
        (id, session_id, role, content, timestamp, model_id, tokens_used, 
         response_time, metadata, content_hash, content_length, is_encrypted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        for msg_data in messages_data:
            # חישוב metadata נוספים
            content = msg_data.get('content', '')
            content_hash = str(hash(content))
            content_length = len(content)
            
            params = (
                msg_data.get('id', str(uuid.uuid4())),
                msg_data['session_id'],
                msg_data['role'],
                content,
                msg_data.get('timestamp', datetime.utcnow().isoformat()),
                msg_data.get('model_id'),
                msg_data.get('tokens_used'),
                msg_data.get('response_time'),
                json.dumps(msg_data.get('metadata', {})),
                content_hash,
                content_length,
                msg_data.get('is_encrypted', False)
            )
            
            batch.add_operation(insert_query, params)
        
        return self.execute_batch(batch)
    
    def get_session_messages_paginated(self, session_id: str, limit: int = 50, 
                                     offset: int = 0, order: str = 'ASC') -> Dict[str, Any]:
        """קבלת הודעות session עם pagination מותאם"""
        
        # Count query
        count_query = "SELECT COUNT(*) FROM chat_messages WHERE session_id = ?"
        count_cursor = self.execute_query(count_query, (session_id,), QueryType.SELECT)
        total_count = count_cursor.fetchone()[0]
        
        # Messages query
        order_clause = "ASC" if order.upper() == "ASC" else "DESC"
        messages_query = f'''
        SELECT id, session_id, role, content, timestamp, model_id, 
               tokens_used, response_time, metadata, content_length, is_encrypted
        FROM chat_messages 
        WHERE session_id = ? 
        ORDER BY timestamp {order_clause}
        LIMIT ? OFFSET ?
        '''
        
        cursor = self.execute_query(messages_query, (session_id, limit, offset), QueryType.SELECT)
        messages = [dict(row) for row in cursor.fetchall()]
        
        return {
            "messages": messages,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(messages) < total_count,
            "order": order
        }
    
    def search_messages_optimized(self, query: str, user_id: str = None, 
                                session_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """חיפוש הודעות מותאם לביצועים"""
        
        # בניית query עם FTS אם זמין, אחרת LIKE
        search_query = '''
        SELECT m.id, m.session_id, m.role, m.content, m.timestamp, 
               m.model_id, m.tokens_used, m.response_time, m.content_length,
               s.title as session_title, s.user_id
        FROM chat_messages m
        JOIN chat_sessions s ON m.session_id = s.id
        WHERE m.content LIKE ?
        '''
        
        params = [f"%{query}%"]
        
        if user_id:
            search_query += " AND s.user_id = ?"
            params.append(user_id)
        
        if session_id:
            search_query += " AND m.session_id = ?"
            params.append(session_id)
        
        search_query += " ORDER BY m.timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.execute_query(search_query, tuple(params), QueryType.SELECT)
        return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_data(self, days_old: int = 30, dry_run: bool = True) -> Dict[str, int]:
        """ניקוי נתונים ישנים"""
        cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()
        
        cleanup_stats = {
            "old_sessions": 0,
            "old_messages": 0,
            "query_stats": 0,
            "cache_entries": 0
        }
        
        if dry_run:
            # ספירה בלבד
            queries = [
                ("SELECT COUNT(*) FROM chat_sessions WHERE is_archived = 1 AND updated_at < ?", "old_sessions"),
                ("SELECT COUNT(*) FROM chat_messages WHERE timestamp < ?", "old_messages"),
                ("SELECT COUNT(*) FROM query_performance WHERE timestamp < ?", "query_stats"),
                ("SELECT COUNT(*) FROM cache_metadata WHERE expires_at < ?", "cache_entries")
            ]
            
            for query, key in queries:
                cursor = self.execute_query(query, (cutoff_date,), QueryType.SELECT)
                cleanup_stats[key] = cursor.fetchone()[0]
        
        else:
            # מחיקה בפועל
            with self.connection_pool.get_connection() as db_conn:
                # מחיקת sessions ישנים וארכיוניים
                cursor = db_conn.execute(
                    "DELETE FROM chat_sessions WHERE is_archived = 1 AND updated_at < ?",
                    (cutoff_date,)
                )
                cleanup_stats["old_sessions"] = cursor.rowcount
                
                # מחיקת הודעות ישנות (orphaned)
                cursor = db_conn.execute(
                    "DELETE FROM chat_messages WHERE timestamp < ? AND session_id NOT IN (SELECT id FROM chat_sessions)",
                    (cutoff_date,)
                )
                cleanup_stats["old_messages"] = cursor.rowcount
                
                # מחיקת סטטיסטיקות ישנות
                cursor = db_conn.execute(
                    "DELETE FROM query_performance WHERE timestamp < ?",
                    (cutoff_date,)
                )
                cleanup_stats["query_stats"] = cursor.rowcount
                
                # מחיקת cache entries שפגו
                cursor = db_conn.execute(
                    "DELETE FROM cache_metadata WHERE expires_at < ?",
                    (datetime.utcnow().isoformat(),)
                )
                cleanup_stats["cache_entries"] = cursor.rowcount
        
        return cleanup_stats
    
    def optimize_database(self) -> Dict[str, Any]:
        """אופטימיזציה של מסד הנתונים"""
        optimization_results = {}
        
        with self.connection_pool.get_connection() as db_conn:
            # VACUUM לדחיסת מסד הנתונים
            start_time = time.time()
            db_conn.execute("VACUUM")
            optimization_results["vacuum_time"] = time.time() - start_time
            
            # ANALYZE לעדכון סטטיסטיקות
            start_time = time.time()
            db_conn.execute("ANALYZE")
            optimization_results["analyze_time"] = time.time() - start_time
            
            # PRAGMA optimize
            start_time = time.time()
            db_conn.execute("PRAGMA optimize")
            optimization_results["optimize_time"] = time.time() - start_time
            
            # בדיקת גודל מסד הנתונים
            cursor = db_conn.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor = db_conn.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            optimization_results["database_size_bytes"] = page_count * page_size
            
            # בדיקת fragmentation
            cursor = db_conn.execute("PRAGMA freelist_count")
            freelist_count = cursor.fetchone()[0]
            optimization_results["fragmentation_pages"] = freelist_count
        
        return optimization_results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות ביצועים"""
        with self.stats_lock:
            if not self.query_stats:
                return {"message": "No query statistics available"}
            
            # חישוב סטטיסטיקות
            total_queries = len(self.query_stats)
            avg_execution_time = sum(s.execution_time for s in self.query_stats) / total_queries
            max_execution_time = max(s.execution_time for s in self.query_stats)
            min_execution_time = min(s.execution_time for s in self.query_stats)
            
            # סטטיסטיקות לפי סוג
            type_stats = {}
            for stat in self.query_stats:
                query_type = stat.query_type.value
                if query_type not in type_stats:
                    type_stats[query_type] = {
                        "count": 0,
                        "total_time": 0,
                        "avg_time": 0,
                        "errors": 0
                    }
                
                type_stats[query_type]["count"] += 1
                type_stats[query_type]["total_time"] += stat.execution_time
                if stat.error:
                    type_stats[query_type]["errors"] += 1
            
            # חישוב ממוצעים
            for stats in type_stats.values():
                if stats["count"] > 0:
                    stats["avg_time"] = stats["total_time"] / stats["count"]
            
            return {
                "total_queries": total_queries,
                "avg_execution_time": avg_execution_time,
                "max_execution_time": max_execution_time,
                "min_execution_time": min_execution_time,
                "query_type_stats": type_stats,
                "connection_pool_stats": self.connection_pool.get_stats().__dict__,
                "recent_errors": [
                    {"query_hash": s.query_hash, "error": s.error, "timestamp": s.timestamp.isoformat()}
                    for s in self.query_stats[-50:] if s.error
                ]
            }
    
    def close(self):
        """סגירת השירות"""
        self.connection_pool.close_all()
        logger.info("OptimizedDatabaseService closed")

# Global instance
optimized_db = OptimizedDatabaseService()

# Utility functions
def get_db_performance_info() -> Dict[str, Any]:
    """קבלת מידע ביצועים של מסד הנתונים"""
    return optimized_db.get_performance_stats()

def cleanup_database(days_old: int = 30, dry_run: bool = True) -> Dict[str, int]:
    """ניקוי מסד הנתונים"""
    return optimized_db.cleanup_old_data(days_old, dry_run)

def optimize_database() -> Dict[str, Any]:
    """אופטימיזציה של מסד הנתונים"""
    return optimized_db.optimize_database()