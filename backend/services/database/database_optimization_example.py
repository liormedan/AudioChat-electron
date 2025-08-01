"""
דוגמה מקיפה לאופטימיזציות מסד הנתונים
"""

import time
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from backend.services.database.optimized_db_service import (
    OptimizedDatabaseService, BatchOperation, QueryType
)
from backend.services.database.chat_db_integration import (
    optimized_chat_history, optimized_session_service, 
    get_database_performance_summary, perform_maintenance
)
from backend.models.chat import ChatSession, Message, MessageRole

# הגדרת logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_connection_pooling():
    """הדגמת connection pooling"""
    print("\n=== Connection Pooling Demo ===")
    
    # יצירת שירות עם הגדרות pool מותאמות
    db_service = OptimizedDatabaseService(
        pool_config={
            'min_connections': 3,
            'max_connections': 8,
            'max_idle_time': 60,
            'cleanup_interval': 30
        }
    )
    
    print("Created database service with optimized connection pool")
    
    # הצגת סטטיסטיקות pool ראשוניות
    pool_stats = db_service.connection_pool.get_stats()
    print(f"Initial pool stats:")
    print(f"  Total connections: {pool_stats.total_connections}")
    print(f"  Idle connections: {pool_stats.idle_connections}")
    print(f"  Active connections: {pool_stats.active_connections}")
    
    # ביצוע queries במקביל לבדיקת pool
    import threading
    
    def worker(worker_id: int, num_queries: int):
        for i in range(num_queries):
            try:
                cursor = db_service.execute_query(
                    "SELECT COUNT(*) FROM chat_sessions",
                    query_type=QueryType.SELECT
                )
                result = cursor.fetchone()[0]
                time.sleep(0.01)  # סימולציה של עבודה
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
    
    # יצירת threads מרובים
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker, args=(i, 10))
        threads.append(thread)
        thread.start()
    
    # המתנה לסיום
    for thread in threads:
        thread.join()
    
    # הצגת סטטיסטיקות סופיות
    final_stats = db_service.connection_pool.get_stats()
    print(f"\nFinal pool stats:")
    print(f"  Pool hits: {final_stats.pool_hits}")
    print(f"  Pool misses: {final_stats.pool_misses}")
    print(f"  Max wait time: {final_stats.max_wait_time:.4f}s")
    print(f"  Average wait time: {final_stats.wait_time_total / (final_stats.pool_hits + final_stats.pool_misses):.4f}s")
    
    db_service.close()

def demonstrate_batch_operations():
    """הדגמת batch operations"""
    print("\n=== Batch Operations Demo ===")
    
    # יצירת sessions ב-batch
    print("Creating sessions in batch...")
    
    sessions_data = []
    for i in range(100):
        session_data = {
            'id': f'batch_session_{i}',
            'title': f'Batch Session {i}',
            'model_id': 'gpt-4',
            'user_id': f'user_{i % 10}',  # 10 משתמשים שונים
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'message_count': 0,
            'is_archived': False,
            'metadata': '{}'
        }
        sessions_data.append(session_data)
    
    # מדידת זמן batch insert
    start_time = time.time()
    
    batch = BatchOperation("INSERT", "chat_sessions")
    for session_data in sessions_data:
        batch.add_operation(
            """INSERT INTO chat_sessions 
               (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(session_data.values())
        )
    
    from backend.services.database.optimized_db_service import optimized_db
    affected_rows = optimized_db.execute_batch(batch)
    batch_time = time.time() - start_time
    
    print(f"Batch insert: {affected_rows} sessions in {batch_time:.4f}s")
    print(f"Rate: {affected_rows / batch_time:.0f} sessions/second")
    
    # השוואה עם insert בודד
    print("\nComparing with individual inserts...")
    
    start_time = time.time()
    for i in range(10):  # רק 10 לדוגמה
        optimized_db.execute_query(
            """INSERT INTO chat_sessions 
               (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (f'single_session_{i}', f'Single Session {i}', 'gpt-4', 'user_single',
             datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 0, False, '{}'),
            QueryType.INSERT
        )
    
    single_time = time.time() - start_time
    print(f"Individual inserts: 10 sessions in {single_time:.4f}s")
    print(f"Rate: {10 / single_time:.0f} sessions/second")
    print(f"Batch is {(single_time / 10) / (batch_time / 100):.1f}x faster")

def demonstrate_pagination():
    """הדגמת pagination מותאם"""
    print("\n=== Pagination Demo ===")
    
    # קבלת sessions עם pagination
    page_size = 20
    total_pages = 0
    total_sessions = 0
    
    print(f"Fetching sessions with page size: {page_size}")
    
    page = 0
    while True:
        start_time = time.time()
        
        result = optimized_db.get_user_sessions_paginated(
            user_id=None,  # כל המשתמשים
            limit=page_size,
            offset=page * page_size,
            include_archived=False
        )
        
        fetch_time = time.time() - start_time
        
        sessions = result['sessions']
        if not sessions:
            break
        
        total_sessions += len(sessions)
        total_pages += 1
        
        print(f"Page {page + 1}: {len(sessions)} sessions in {fetch_time:.4f}s")
        
        if not result['has_more']:
            break
        
        page += 1
        
        # הגבלה למניעת לולאה אינסופית
        if page >= 10:
            break
    
    print(f"\nTotal: {total_sessions} sessions across {total_pages} pages")

def demonstrate_optimized_queries():
    """הדגמת queries מותאמים"""
    print("\n=== Optimized Queries Demo ===")
    
    # יצירת הודעות לדוגמה
    print("Creating sample messages...")
    
    # בחירת session קיים
    cursor = optimized_db.execute_query(
        "SELECT id FROM chat_sessions LIMIT 1",
        query_type=QueryType.SELECT
    )
    session_row = cursor.fetchone()
    
    if not session_row:
        print("No sessions found, skipping messages demo")
        return
    
    session_id = session_row[0]
    
    # יצירת הודעות ב-batch
    messages_data = []
    for i in range(50):
        message_data = {
            'id': f'opt_msg_{i}',
            'session_id': session_id,
            'role': 'user' if i % 2 == 0 else 'assistant',
            'content': f'Optimized message content {i} with some searchable text about AI and machine learning',
            'timestamp': (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
            'model_id': 'gpt-4',
            'tokens_used': random.randint(10, 100),
            'response_time': random.uniform(0.1, 2.0),
            'metadata': {},
            'is_encrypted': False
        }
        messages_data.append(message_data)
    
    optimized_db.save_messages_batch(messages_data)
    print(f"Created {len(messages_data)} sample messages")
    
    # בדיקת query עם אינדקסים
    print("\nTesting optimized queries...")
    
    # Query 1: הודעות לפי session (משתמש באינדקס)
    start_time = time.time()
    result = optimized_db.get_session_messages_paginated(
        session_id=session_id,
        limit=20,
        offset=0,
        order='DESC'
    )
    query1_time = time.time() - start_time
    print(f"Session messages query: {len(result['messages'])} messages in {query1_time:.4f}s")
    
    # Query 2: חיפוש בתוכן (משתמש באינדקס LIKE)
    start_time = time.time()
    search_results = optimized_db.search_messages_optimized(
        query='machine learning',
        limit=10
    )
    query2_time = time.time() - start_time
    print(f"Content search query: {len(search_results)} results in {query2_time:.4f}s")
    
    # Query 3: סטטיסטיקות session (משתמש באינדקסים מרובים)
    start_time = time.time()
    session_stats = optimized_db.get_session_with_stats(session_id)
    query3_time = time.time() - start_time
    print(f"Session stats query: completed in {query3_time:.4f}s")
    
    if session_stats:
        print(f"  Messages: {session_stats.get('actual_message_count', 0)}")
        print(f"  Total tokens: {session_stats.get('total_tokens_used', 0)}")
        print(f"  Avg response time: {session_stats.get('avg_response_time', 0):.3f}s")

def demonstrate_database_maintenance():
    """הדגמת תחזוקת מסד נתונים"""
    print("\n=== Database Maintenance Demo ===")
    
    # יצירת נתונים ישנים לדוגמה
    print("Creating old data for cleanup demo...")
    
    old_date = (datetime.utcnow() - timedelta(days=35)).isoformat()
    
    # יצירת sessions ישנים וארכיוניים
    old_sessions = []
    for i in range(5):
        session_data = {
            'id': f'old_session_{i}',
            'title': f'Old Session {i}',
            'model_id': 'gpt-3.5',
            'user_id': 'old_user',
            'created_at': old_date,
            'updated_at': old_date,
            'message_count': 0,
            'is_archived': True,  # ארכיוני
            'metadata': '{}'
        }
        old_sessions.append(session_data)
    
    batch = BatchOperation("INSERT", "chat_sessions")
    for session_data in old_sessions:
        batch.add_operation(
            """INSERT INTO chat_sessions 
               (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(session_data.values())
        )
    
    optimized_db.execute_batch(batch)
    print(f"Created {len(old_sessions)} old archived sessions")
    
    # בדיקת cleanup (dry run)
    print("\nTesting cleanup (dry run)...")
    cleanup_stats = optimized_db.cleanup_old_data(days_old=30, dry_run=True)
    print(f"Would clean up:")
    for key, count in cleanup_stats.items():
        if count > 0:
            print(f"  {key}: {count}")
    
    # ביצוע cleanup בפועל
    print("\nPerforming actual cleanup...")
    cleanup_stats = optimized_db.cleanup_old_data(days_old=30, dry_run=False)
    print(f"Cleaned up:")
    for key, count in cleanup_stats.items():
        if count > 0:
            print(f"  {key}: {count}")
    
    # אופטימיזציה של מסד הנתונים
    print("\nOptimizing database...")
    start_time = time.time()
    optimization_results = optimized_db.optimize_database()
    optimization_time = time.time() - start_time
    
    print(f"Database optimization completed in {optimization_time:.4f}s:")
    print(f"  VACUUM time: {optimization_results['vacuum_time']:.4f}s")
    print(f"  ANALYZE time: {optimization_results['analyze_time']:.4f}s")
    print(f"  Database size: {optimization_results['database_size_bytes'] / (1024*1024):.2f} MB")
    print(f"  Fragmentation pages: {optimization_results['fragmentation_pages']}")

def demonstrate_performance_monitoring():
    """הדגמת ניטור ביצועים"""
    print("\n=== Performance Monitoring Demo ===")
    
    # ביצוע queries מגוונים לסטטיסטיקות
    print("Generating query statistics...")
    
    # SELECT queries
    for i in range(20):
        optimized_db.execute_query(
            "SELECT COUNT(*) FROM chat_sessions WHERE user_id = ?",
            (f'user_{i % 5}',),
            QueryType.SELECT
        )
    
    # INSERT queries
    for i in range(5):
        optimized_db.execute_query(
            """INSERT INTO chat_sessions 
               (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (f'perf_session_{i}', f'Performance Session {i}', 'gpt-4', 'perf_user',
             datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 0, False, '{}'),
            QueryType.INSERT
        )
    
    # UPDATE queries
    for i in range(3):
        optimized_db.execute_query(
            "UPDATE chat_sessions SET title = ? WHERE id = ?",
            (f'Updated Performance Session {i}', f'perf_session_{i}'),
            QueryType.UPDATE
        )
    
    # קבלת סטטיסטיקות ביצועים
    perf_stats = optimized_db.get_performance_stats()
    
    print(f"\nPerformance Statistics:")
    print(f"  Total queries: {perf_stats['total_queries']}")
    print(f"  Average execution time: {perf_stats['avg_execution_time']:.4f}s")
    print(f"  Max execution time: {perf_stats['max_execution_time']:.4f}s")
    print(f"  Min execution time: {perf_stats['min_execution_time']:.4f}s")
    
    print(f"\nQuery Type Statistics:")
    for query_type, stats in perf_stats['query_type_stats'].items():
        print(f"  {query_type}:")
        print(f"    Count: {stats['count']}")
        print(f"    Average time: {stats['avg_time']:.4f}s")
        print(f"    Errors: {stats['errors']}")
    
    print(f"\nConnection Pool Statistics:")
    pool_stats = perf_stats['connection_pool_stats']
    print(f"  Total connections: {pool_stats['total_connections']}")
    print(f"  Active connections: {pool_stats['active_connections']}")
    print(f"  Pool hits: {pool_stats['pool_hits']}")
    print(f"  Pool misses: {pool_stats['pool_misses']}")
    
    if pool_stats['pool_hits'] + pool_stats['pool_misses'] > 0:
        hit_rate = pool_stats['pool_hits'] / (pool_stats['pool_hits'] + pool_stats['pool_misses']) * 100
        print(f"  Pool hit rate: {hit_rate:.1f}%")

def demonstrate_integration_services():
    """הדגמת שירותי האינטגרציה"""
    print("\n=== Integration Services Demo ===")
    
    # יצירת session עם השירות המותאם
    print("Creating session with optimized service...")
    
    session = optimized_session_service.create_session(
        title="Integration Demo Session",
        model_id="gpt-4",
        user_id="integration_user"
    )
    
    print(f"Created session: {session.id}")
    
    # הוספת הודעות עם השירות המותאם
    print("Adding messages with optimized service...")
    
    messages = []
    for i in range(10):
        message = Message(
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"Integration demo message {i} about artificial intelligence and natural language processing",
            model_id="gpt-4",
            tokens_used=random.randint(20, 80),
            response_time=random.uniform(0.2, 1.5)
        )
        messages.append(message)
    
    # שמירה ב-batch
    message_ids = optimized_chat_history.save_messages_batch(session.id, messages)
    print(f"Saved {len(message_ids)} messages in batch")
    
    # קבלת הודעות עם pagination
    print("Retrieving messages with pagination...")
    
    retrieved_messages = optimized_chat_history.get_session_messages(
        session_id=session.id,
        limit=5,
        offset=0,
        order='ASC'
    )
    
    print(f"Retrieved {len(retrieved_messages)} messages (first page)")
    
    # חיפוש הודעות
    print("Searching messages...")
    
    search_results = optimized_chat_history.search_messages(
        query="artificial intelligence",
        session_id=session.id,
        limit=5
    )
    
    print(f"Found {len(search_results)} messages matching search")
    
    # קבלת סטטיסטיקות session
    print("Getting session statistics...")
    
    session_stats = optimized_chat_history.get_session_statistics(session.id)
    print(f"Session statistics:")
    print(f"  Message count: {session_stats.get('message_count', 0)}")
    print(f"  Total tokens: {session_stats.get('total_tokens', 0)}")
    print(f"  Average response time: {session_stats.get('avg_response_time', 0):.3f}s")
    
    # קבלת sessions של משתמש
    print("Getting user sessions...")
    
    user_sessions_result = optimized_session_service.list_user_sessions(
        user_id="integration_user",
        limit=10,
        offset=0
    )
    
    print(f"User has {len(user_sessions_result['sessions'])} sessions")
    print(f"Total sessions: {user_sessions_result['total_count']}")

def demonstrate_performance_summary():
    """הדגמת סיכום ביצועים"""
    print("\n=== Performance Summary ===")
    
    summary = get_database_performance_summary()
    
    print("Database Performance Summary:")
    print(f"  Total queries: {summary['database']['total_queries']}")
    print(f"  Average execution time: {summary['database']['avg_execution_time']:.4f}s")
    print(f"  Recent errors: {summary['database']['recent_errors']}")
    
    print("\nCache Performance:")
    for backend, stats in summary['cache'].items():
        print(f"  {backend.upper()}:")
        print(f"    Hit rate: {stats['hit_rate']:.1f}%")
        print(f"    Entries: {stats['total_entries']}")
        print(f"    Size: {stats['total_size_mb']:.2f} MB")
    
    print(f"\nSummary generated at: {summary['timestamp']}")

if __name__ == "__main__":
    print("Database Optimization Comprehensive Demo")
    print("=" * 60)
    
    try:
        # הרצת כל ההדגמות
        demonstrate_connection_pooling()
        demonstrate_batch_operations()
        demonstrate_pagination()
        demonstrate_optimized_queries()
        demonstrate_database_maintenance()
        demonstrate_performance_monitoring()
        demonstrate_integration_services()
        demonstrate_performance_summary()
        
        print("\n" + "=" * 60)
        print("All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # ניקוי
        try:
            optimized_db.close()
        except:
            pass