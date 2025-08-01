"""
בדיקות לשירות מסד הנתונים המותאם לביצועים
"""

import unittest
import tempfile
import os
import shutil
import time
import threading
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.services.database.optimized_db_service import (
    OptimizedDatabaseService, ConnectionPool, DatabaseConnection, BatchOperation,
    QueryType, QueryStats, ConnectionPoolStats,
    optimized_db, get_db_performance_info, cleanup_database, optimize_database
)


class TestDatabaseConnection(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.connection = DatabaseConnection(self.db_path, "test_conn_1")
    
    def tearDown(self):
        """ניקוי אחרי בדיקות"""
        self.connection.close()
        shutil.rmtree(self.temp_dir)
    
    def test_connection_creation(self):
        """בדיקת יצירת חיבור"""
        conn = self.connection.connect()
        self.assertIsNotNone(conn)
        self.assertEqual(self.connection.connection_id, "test_conn_1")
        self.assertFalse(self.connection.is_active)
    
    def test_query_execution(self):
        """בדיקת ביצוע query"""
        # יצירת טבלה פשוטה
        cursor = self.connection.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        self.assertIsNotNone(cursor)
        
        # הכנסת נתונים
        cursor = self.connection.execute("INSERT INTO test VALUES (?, ?)", (1, "test"))
        self.assertEqual(cursor.rowcount, 1)
        
        # קבלת נתונים
        cursor = self.connection.execute("SELECT * FROM test WHERE id = ?", (1,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], "test")
    
    def test_batch_execution(self):
        """בדיקת ביצוע batch queries"""
        # יצירת טבלה
        self.connection.execute("CREATE TABLE test_batch (id INTEGER, value TEXT)")
        
        # הכנסת נתונים ב-batch
        data = [(i, f"value_{i}") for i in range(10)]
        cursor = self.connection.executemany("INSERT INTO test_batch VALUES (?, ?)", data)
        
        # בדיקת תוצאות
        cursor = self.connection.execute("SELECT COUNT(*) FROM test_batch")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 10)
    
    def test_connection_stats(self):
        """בדיקת סטטיסטיקות חיבור"""
        initial_query_count = self.connection.query_count
        
        # ביצוע מספר queries
        self.connection.execute("SELECT 1")
        self.connection.execute("SELECT 2")
        
        self.assertEqual(self.connection.query_count, initial_query_count + 2)
        self.assertGreater(self.connection.age_seconds, 0)
        self.assertGreaterEqual(self.connection.idle_seconds, 0)


class TestConnectionPool(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_pool.db")
        self.pool = ConnectionPool(
            db_path=self.db_path,
            min_connections=2,
            max_connections=5,
            max_idle_time=10,
            cleanup_interval=5
        )
    
    def tearDown(self):
        """ניקוי אחרי בדיקות"""
        self.pool.close_all()
        shutil.rmtree(self.temp_dir)
    
    def test_pool_initialization(self):
        """בדיקת אתחול pool"""
        stats = self.pool.get_stats()
        self.assertEqual(stats.total_connections, 2)  # min_connections
        self.assertEqual(stats.idle_connections, 2)
        self.assertEqual(stats.active_connections, 0)
    
    def test_connection_acquisition(self):
        """בדיקת קבלת חיבור מה-pool"""
        with self.pool.get_connection() as conn:
            self.assertIsInstance(conn, DatabaseConnection)
            
            # בדיקת סטטיסטיקות במהלך השימוש
            stats = self.pool.get_stats()
            self.assertEqual(stats.active_connections, 1)
            self.assertEqual(stats.idle_connections, 1)
        
        # בדיקת סטטיסטיקות אחרי השחרור
        stats = self.pool.get_stats()
        self.assertEqual(stats.active_connections, 0)
        self.assertEqual(stats.idle_connections, 2)
    
    def test_concurrent_connections(self):
        """בדיקת חיבורים במקביל"""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                with self.pool.get_connection() as conn:
                    # יצירת טבלה אם לא קיימת
                    conn.execute("CREATE TABLE IF NOT EXISTS concurrent_test (id INTEGER, worker_id INTEGER)")
                    
                    # הכנסת נתונים
                    conn.execute("INSERT INTO concurrent_test VALUES (?, ?)", (worker_id, worker_id))
                    
                    # קצת עבודה
                    time.sleep(0.1)
                    
                    # קבלת נתונים
                    cursor = conn.execute("SELECT COUNT(*) FROM concurrent_test WHERE worker_id = ?", (worker_id,))
                    count = cursor.fetchone()[0]
                    results.append((worker_id, count))
                    
            except Exception as e:
                errors.append(str(e))
        
        # יצירת 3 threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # המתנה לסיום
        for thread in threads:
            thread.join()
        
        # בדיקת תוצאות
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 3)
        
        # כל worker צריך לראות את הנתונים שלו
        for worker_id, count in results:
            self.assertEqual(count, 1)
    
    def test_pool_expansion(self):
        """בדיקת הרחבת pool כשנדרש"""
        connections = []
        
        try:
            # קבלת כל החיבורים הזמינים ועוד
            for i in range(4):  # יותר מ-min_connections
                conn_context = self.pool.get_connection()
                conn = conn_context.__enter__()
                connections.append((conn_context, conn))
            
            # בדיקה שה-pool התרחב
            stats = self.pool.get_stats()
            self.assertEqual(stats.active_connections, 4)
            self.assertGreaterEqual(stats.total_connections, 4)
            
        finally:
            # שחרור כל החיבורים
            for conn_context, conn in connections:
                conn_context.__exit__(None, None, None)
    
    def test_connection_timeout(self):
        """בדיקת timeout כשאין חיבורים זמינים"""
        connections = []
        
        try:
            # תפיסת כל החיבורים המקסימליים
            for i in range(5):  # max_connections
                conn_context = self.pool.get_connection()
                conn = conn_context.__enter__()
                connections.append((conn_context, conn))
            
            # ניסיון קבלת חיבור נוסף צריך להיכשל
            with self.assertRaises((TimeoutError, Exception)):
                with self.pool.get_connection(timeout=0.1):
                    pass
                    
        finally:
            # שחרור החיבורים
            for conn_context, conn in connections:
                conn_context.__exit__(None, None, None)


class TestBatchOperation(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_batch.db")
        self.db_conn = DatabaseConnection(self.db_path, "batch_test")
        
        # יצירת טבלה לבדיקות
        self.db_conn.execute("CREATE TABLE test_batch (id INTEGER, name TEXT, value INTEGER)")
    
    def tearDown(self):
        """ניקוי אחרי בדיקות"""
        self.db_conn.close()
        shutil.rmtree(self.temp_dir)
    
    def test_batch_insert(self):
        """בדיקת batch insert"""
        batch = BatchOperation("INSERT", "test_batch")
        
        # הוספת פעולות
        for i in range(100):
            batch.add_operation(
                "INSERT INTO test_batch VALUES (?, ?, ?)",
                (i, f"name_{i}", i * 10)
            )
        
        # ביצוע batch
        affected_rows = batch.execute(self.db_conn)
        self.assertEqual(affected_rows, 100)
        
        # בדיקת תוצאות
        cursor = self.db_conn.execute("SELECT COUNT(*) FROM test_batch")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 100)
    
    def test_mixed_batch_operations(self):
        """בדיקת batch עם פעולות מעורבות"""
        # הכנסת נתונים ראשוניים
        for i in range(10):
            self.db_conn.execute("INSERT INTO test_batch VALUES (?, ?, ?)", (i, f"name_{i}", i))
        
        batch = BatchOperation("MIXED", "test_batch")
        
        # הוספת עדכונים
        for i in range(5):
            batch.add_operation(
                "UPDATE test_batch SET value = ? WHERE id = ?",
                (i * 100, i)
            )
        
        # הוספת הכנסות חדשות
        for i in range(10, 15):
            batch.add_operation(
                "INSERT INTO test_batch VALUES (?, ?, ?)",
                (i, f"new_name_{i}", i * 10)
            )
        
        # ביצוע batch
        affected_rows = batch.execute(self.db_conn)
        self.assertEqual(affected_rows, 10)  # 5 updates + 5 inserts
        
        # בדיקת תוצאות
        cursor = self.db_conn.execute("SELECT COUNT(*) FROM test_batch")
        total_count = cursor.fetchone()[0]
        self.assertEqual(total_count, 15)
        
        # בדיקת עדכונים
        cursor = self.db_conn.execute("SELECT value FROM test_batch WHERE id = 0")
        updated_value = cursor.fetchone()[0]
        self.assertEqual(updated_value, 0)  # 0 * 100


class TestOptimizedDatabaseService(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_optimized.db")
        
        self.db_service = OptimizedDatabaseService(
            db_path=self.db_path,
            pool_config={
                'min_connections': 1,
                'max_connections': 3,
                'max_idle_time': 10
            }
        )
    
    def tearDown(self):
        """ניקוי אחרי בדיקות"""
        self.db_service.close()
        shutil.rmtree(self.temp_dir)
    
    def test_database_initialization(self):
        """בדיקת אתחול מסד הנתונים"""
        # בדיקה שהטבלאות נוצרו
        cursor = self.db_service.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'",
            query_type=QueryType.SELECT
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['chat_sessions', 'chat_messages', 'query_performance', 'cache_metadata']
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_session_operations(self):
        """בדיקת פעולות session"""
        # יצירת session
        session_data = {
            'id': 'test_session_1',
            'title': 'Test Session',
            'model_id': 'gpt-4',
            'user_id': 'user_123',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'message_count': 0,
            'is_archived': False,
            'metadata': '{}'
        }
        
        # הכנסת session
        cursor = self.db_service.execute_query(
            """INSERT INTO chat_sessions 
               (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(session_data.values()),
            QueryType.INSERT
        )
        
        # קבלת session עם סטטיסטיקות
        session_with_stats = self.db_service.get_session_with_stats('test_session_1')
        self.assertIsNotNone(session_with_stats)
        self.assertEqual(session_with_stats['title'], 'Test Session')
        self.assertEqual(session_with_stats['actual_message_count'], 0)
    
    def test_paginated_sessions(self):
        """בדיקת קבלת sessions עם pagination"""
        # יצירת מספר sessions
        sessions_data = []
        for i in range(25):
            session_data = {
                'id': f'session_{i}',
                'title': f'Session {i}',
                'model_id': 'gpt-4',
                'user_id': 'user_123',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'message_count': 0,
                'is_archived': False,
                'metadata': '{}'
            }
            sessions_data.append(session_data)
        
        # הכנסה ב-batch
        batch = BatchOperation("INSERT", "chat_sessions")
        for session_data in sessions_data:
            batch.add_operation(
                """INSERT INTO chat_sessions 
                   (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tuple(session_data.values())
            )
        
        affected = self.db_service.execute_batch(batch)
        self.assertEqual(affected, 25)
        
        # בדיקת pagination
        result = self.db_service.get_user_sessions_paginated(
            user_id='user_123',
            limit=10,
            offset=0
        )
        
        self.assertEqual(len(result['sessions']), 10)
        self.assertEqual(result['total_count'], 25)
        self.assertTrue(result['has_more'])
        
        # עמוד שני
        result_page2 = self.db_service.get_user_sessions_paginated(
            user_id='user_123',
            limit=10,
            offset=10
        )
        
        self.assertEqual(len(result_page2['sessions']), 10)
        self.assertTrue(result_page2['has_more'])
        
        # עמוד אחרון
        result_page3 = self.db_service.get_user_sessions_paginated(
            user_id='user_123',
            limit=10,
            offset=20
        )
        
        self.assertEqual(len(result_page3['sessions']), 5)
        self.assertFalse(result_page3['has_more'])
    
    def test_batch_message_operations(self):
        """בדיקת פעולות הודעות ב-batch"""
        # יצירת session קודם
        self.db_service.execute_query(
            """INSERT INTO chat_sessions 
               (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ('batch_session', 'Batch Test', 'gpt-4', 'user_123', 
             datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 0, False, '{}'),
            QueryType.INSERT
        )
        
        # יצירת הודעות
        messages_data = []
        for i in range(50):
            message_data = {
                'id': f'msg_{i}',
                'session_id': 'batch_session',
                'role': 'user' if i % 2 == 0 else 'assistant',
                'content': f'Message content {i}',
                'timestamp': datetime.utcnow().isoformat(),
                'model_id': 'gpt-4',
                'tokens_used': 10 + i,
                'response_time': 0.5 + (i * 0.1),
                'metadata': {},
                'is_encrypted': False
            }
            messages_data.append(message_data)
        
        # שמירה ב-batch
        affected = self.db_service.save_messages_batch(messages_data)
        self.assertEqual(affected, 50)
        
        # בדיקת תוצאות עם pagination
        result = self.db_service.get_session_messages_paginated(
            session_id='batch_session',
            limit=20,
            offset=0
        )
        
        self.assertEqual(len(result['messages']), 20)
        self.assertEqual(result['total_count'], 50)
        self.assertTrue(result['has_more'])
    
    def test_search_optimization(self):
        """בדיקת חיפוש מותאם"""
        # הכנת נתונים לחיפוש
        self.db_service.execute_query(
            """INSERT INTO chat_sessions 
               (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ('search_session', 'Search Test', 'gpt-4', 'user_search', 
             datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 0, False, '{}'),
            QueryType.INSERT
        )
        
        # הוספת הודעות עם תוכן לחיפוש
        search_messages = [
            {'content': 'This is about machine learning algorithms', 'role': 'user'},
            {'content': 'Machine learning is fascinating', 'role': 'assistant'},
            {'content': 'Tell me about deep learning', 'role': 'user'},
            {'content': 'Deep learning uses neural networks', 'role': 'assistant'},
            {'content': 'What about natural language processing?', 'role': 'user'}
        ]
        
        messages_data = []
        for i, msg in enumerate(search_messages):
            message_data = {
                'id': f'search_msg_{i}',
                'session_id': 'search_session',
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': datetime.utcnow().isoformat(),
                'model_id': 'gpt-4',
                'tokens_used': 10,
                'response_time': 0.5,
                'metadata': {},
                'is_encrypted': False
            }
            messages_data.append(message_data)
        
        self.db_service.save_messages_batch(messages_data)
        
        # חיפוש
        results = self.db_service.search_messages_optimized(
            query='machine learning',
            user_id='user_search',
            limit=10
        )
        
        self.assertEqual(len(results), 2)  # שתי הודעות עם "machine learning"
        
        # חיפוש ספציפי יותר
        results = self.db_service.search_messages_optimized(
            query='deep learning',
            session_id='search_session',
            limit=10
        )
        
        self.assertEqual(len(results), 2)  # שתי הודעות עם "deep learning"
    
    def test_performance_monitoring(self):
        """בדיקת ניטור ביצועים"""
        # ביצוע מספר queries
        for i in range(10):
            self.db_service.execute_query(
                "SELECT COUNT(*) FROM chat_sessions",
                query_type=QueryType.SELECT
            )
        
        # קבלת סטטיסטיקות
        stats = self.db_service.get_performance_stats()
        
        self.assertIn('total_queries', stats)
        self.assertIn('avg_execution_time', stats)
        self.assertIn('query_type_stats', stats)
        self.assertIn('connection_pool_stats', stats)
        
        # בדיקה שיש סטטיסטיקות SELECT
        self.assertIn('SELECT', stats['query_type_stats'])
        self.assertGreaterEqual(stats['query_type_stats']['SELECT']['count'], 10)
    
    def test_database_cleanup(self):
        """בדיקת ניקוי מסד הנתונים"""
        # יצירת נתונים ישנים
        old_date = (datetime.utcnow() - timedelta(days=35)).isoformat()
        
        # session ישן
        self.db_service.execute_query(
            """INSERT INTO chat_sessions 
               (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ('old_session', 'Old Session', 'gpt-4', 'user_old', 
             old_date, old_date, 0, True, '{}'),
            QueryType.INSERT
        )
        
        # בדיקת dry run
        cleanup_stats = self.db_service.cleanup_old_data(days_old=30, dry_run=True)
        self.assertEqual(cleanup_stats['old_sessions'], 1)
        
        # ביצוע ניקוי בפועל
        cleanup_stats = self.db_service.cleanup_old_data(days_old=30, dry_run=False)
        self.assertEqual(cleanup_stats['old_sessions'], 1)
        
        # בדיקה שהנתונים נמחקו
        cursor = self.db_service.execute_query(
            "SELECT COUNT(*) FROM chat_sessions WHERE id = ?",
            ('old_session',),
            QueryType.SELECT
        )
        count = cursor.fetchone()[0]
        self.assertEqual(count, 0)
    
    def test_database_optimization(self):
        """בדיקת אופטימיזציה של מסד הנתונים"""
        # הוספת נתונים
        for i in range(100):
            self.db_service.execute_query(
                """INSERT INTO chat_sessions 
                   (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (f'opt_session_{i}', f'Session {i}', 'gpt-4', 'user_opt', 
                 datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 0, False, '{}'),
                QueryType.INSERT
            )
        
        # ביצוע אופטימיזציה
        optimization_results = self.db_service.optimize_database()
        
        self.assertIn('vacuum_time', optimization_results)
        self.assertIn('analyze_time', optimization_results)
        self.assertIn('optimize_time', optimization_results)
        self.assertIn('database_size_bytes', optimization_results)
        self.assertIn('fragmentation_pages', optimization_results)
        
        # בדיקה שהזמנים סבירים
        self.assertGreater(optimization_results['vacuum_time'], 0)
        self.assertGreater(optimization_results['analyze_time'], 0)
        self.assertGreater(optimization_results['database_size_bytes'], 0)


class TestUtilityFunctions(unittest.TestCase):
    
    def test_get_db_performance_info(self):
        """בדיקת פונקציית מידע ביצועים"""
        # ביצוע כמה queries כדי ליצור סטטיסטיקות
        optimized_db.execute_query("SELECT 1", query_type=QueryType.SELECT)
        
        info = get_db_performance_info()
        self.assertIsInstance(info, dict)
        
        if 'total_queries' in info:  # אם יש סטטיסטיקות
            self.assertIn('avg_execution_time', info)
            self.assertIn('connection_pool_stats', info)
    
    def test_cleanup_database_function(self):
        """בדיקת פונקציית ניקוי"""
        result = cleanup_database(days_old=30, dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertIn('old_sessions', result)
        self.assertIn('old_messages', result)
    
    def test_optimize_database_function(self):
        """בדיקת פונקציית אופטימיזציה"""
        result = optimize_database()
        self.assertIsInstance(result, dict)
        self.assertIn('vacuum_time', result)
        self.assertIn('database_size_bytes', result)


class TestConcurrency(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_concurrent.db")
        
        self.db_service = OptimizedDatabaseService(
            db_path=self.db_path,
            pool_config={
                'min_connections': 2,
                'max_connections': 5
            }
        )
    
    def tearDown(self):
        """ניקוי אחרי בדיקות"""
        self.db_service.close()
        shutil.rmtree(self.temp_dir)
    
    def test_concurrent_database_operations(self):
        """בדיקת פעולות מסד נתונים במקביל"""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # יצירת session
                session_id = f'concurrent_session_{worker_id}'
                self.db_service.execute_query(
                    """INSERT INTO chat_sessions 
                       (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (session_id, f'Concurrent Session {worker_id}', 'gpt-4', f'user_{worker_id}',
                     datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 0, False, '{}'),
                    QueryType.INSERT
                )
                
                # הוספת הודעות
                messages_data = []
                for i in range(10):
                    message_data = {
                        'id': f'concurrent_msg_{worker_id}_{i}',
                        'session_id': session_id,
                        'role': 'user' if i % 2 == 0 else 'assistant',
                        'content': f'Concurrent message {worker_id}_{i}',
                        'timestamp': datetime.utcnow().isoformat(),
                        'model_id': 'gpt-4',
                        'tokens_used': 10,
                        'response_time': 0.5,
                        'metadata': {},
                        'is_encrypted': False
                    }
                    messages_data.append(message_data)
                
                affected = self.db_service.save_messages_batch(messages_data)
                results.append((worker_id, affected))
                
            except Exception as e:
                errors.append(f"Worker {worker_id}: {str(e)}")
        
        # יצירת 5 threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # המתנה לסיום
        for thread in threads:
            thread.join()
        
        # בדיקת תוצאות
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)
        
        # כל worker צריך להצליח להכניס 10 הודעות
        for worker_id, affected in results:
            self.assertEqual(affected, 10)
        
        # בדיקת סך הנתונים
        cursor = self.db_service.execute_query(
            "SELECT COUNT(*) FROM chat_sessions",
            query_type=QueryType.SELECT
        )
        session_count = cursor.fetchone()[0]
        self.assertEqual(session_count, 5)
        
        cursor = self.db_service.execute_query(
            "SELECT COUNT(*) FROM chat_messages",
            query_type=QueryType.SELECT
        )
        message_count = cursor.fetchone()[0]
        self.assertEqual(message_count, 50)  # 5 workers * 10 messages


if __name__ == '__main__':
    unittest.main()