"""
דוגמה לשימוש במערכת Cache עם Session Service
"""

import time
import logging
from backend.services.cache.chat_cache_service import (
    ChatCacheService, CacheBackend, chat_cache, init_redis_cache, get_cache_info
)
from backend.services.ai.session_service import SessionService

# הגדרת logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_memory_caching():
    """הדגמת in-memory caching"""
    print("\n=== Memory Caching Demo ===")
    
    # יצירת session service
    session_service = SessionService()
    
    # יצירת session חדש
    session = session_service.create_session(
        title="Test Session",
        model_id="gpt-4",
        user_id="user123"
    )
    
    print(f"Created session: {session.id}")
    
    # קבלת session - צריך להיות מ-cache
    start_time = time.time()
    cached_session = session_service.get_session(session.id)
    cache_time = time.time() - start_time
    
    print(f"Retrieved from cache in {cache_time:.4f}s")
    print(f"Session title: {cached_session.title}")
    
    # הצגת סטטיסטיקות cache
    cache_info = get_cache_info()
    print(f"Cache stats: {cache_info['stats']}")

def demonstrate_redis_caching():
    """הדגמת Redis caching (אם זמין)"""
    print("\n=== Redis Caching Demo ===")
    
    try:
        # אתחול Redis cache
        init_redis_cache()
        
        # בדיקת זמינות Redis
        cache_info = get_cache_info()
        if not cache_info['redis_available']:
            print("Redis not available - skipping Redis demo")
            return
        
        print("Redis cache initialized successfully")
        
        # שימוש ב-cache manager
        test_data = {
            "user_id": "user123",
            "preferences": {"theme": "dark", "language": "he"},
            "last_activity": "2024-01-01T12:00:00Z"
        }
        
        # שמירה ב-cache
        chat_cache.set_session("redis_test_session", test_data)
        print("Data saved to Redis cache")
        
        # קבלה מ-cache
        cached_data = chat_cache.get_session("redis_test_session")
        print(f"Retrieved from Redis: {cached_data}")
        
        # הצגת סטטיסטיקות
        cache_info = get_cache_info()
        print(f"Redis stats: {cache_info['stats'].get('redis', 'N/A')}")
        
    except Exception as e:
        print(f"Redis demo failed: {e}")

def demonstrate_cache_invalidation():
    """הדגמת cache invalidation strategies"""
    print("\n=== Cache Invalidation Demo ===")
    
    # הוספת נתונים לcache
    chat_cache.set_session("session1", {"title": "Session 1"})
    chat_cache.set_session("session2", {"title": "Session 2"})
    chat_cache.set_user_sessions("user123", [{"id": "session1"}, {"id": "session2"}])
    
    print("Added test data to cache")
    
    # ביטול session בודד
    chat_cache.invalidate_session("session1")
    print("Invalidated session1")
    
    # בדיקה שנמחק
    result = chat_cache.get_session("session1")
    print(f"session1 after invalidation: {result}")
    
    # ביטול לפי pattern
    invalidated_count = chat_cache.cache.invalidate_pattern("user:*")
    print(f"Invalidated {invalidated_count} entries matching 'user:*'")

def demonstrate_performance_monitoring():
    """הדגמת ניטור ביצועים"""
    print("\n=== Performance Monitoring Demo ===")
    
    # ביצוע פעולות cache מרובות
    for i in range(100):
        key = f"perf_test_{i}"
        value = f"value_{i}"
        chat_cache.cache.set(key, value)
    
    # קבלת חלק מהערכים
    for i in range(0, 100, 10):
        key = f"perf_test_{i}"
        chat_cache.cache.get(key)
    
    # ניסיון קבלת ערכים לא קיימים
    for i in range(200, 210):
        key = f"nonexistent_{i}"
        chat_cache.cache.get(key)
    
    # הצגת סטטיסטיקות ביצועים
    stats = chat_cache.cache.get_stats()
    for backend_name, backend_stats in stats.items():
        print(f"\n{backend_name.upper()} Cache Stats:")
        print(f"  Hits: {backend_stats.hits}")
        print(f"  Misses: {backend_stats.misses}")
        print(f"  Hit Rate: {backend_stats.hit_rate:.2f}%")
        print(f"  Entries: {backend_stats.entry_count}")
        print(f"  Total Size: {backend_stats.total_size_bytes} bytes")
        print(f"  Evictions: {backend_stats.evictions}")

def demonstrate_search_caching():
    """הדגמת caching של תוצאות חיפוש"""
    print("\n=== Search Results Caching Demo ===")
    
    # סימולציה של תוצאות חיפוש
    query = "machine learning"
    filters = {"date_from": "2024-01-01", "user_id": "user123"}
    
    # תוצאות חיפוש מדומות
    search_results = [
        {"id": "msg1", "content": "Introduction to machine learning", "score": 0.95},
        {"id": "msg2", "content": "Advanced machine learning techniques", "score": 0.87},
        {"id": "msg3", "content": "Machine learning in practice", "score": 0.82}
    ]
    
    # שמירת תוצאות ב-cache
    start_time = time.time()
    chat_cache.set_search_results(query, filters, search_results)
    save_time = time.time() - start_time
    print(f"Saved search results to cache in {save_time:.4f}s")
    
    # קבלת תוצאות מ-cache
    start_time = time.time()
    cached_results = chat_cache.get_search_results(query, filters)
    retrieve_time = time.time() - start_time
    print(f"Retrieved search results from cache in {retrieve_time:.4f}s")
    print(f"Found {len(cached_results)} cached results")
    
    # בדיקה עם filters שונים - צריך להחזיר None
    different_filters = {"date_from": "2024-02-01", "user_id": "user456"}
    cached_results = chat_cache.get_search_results(query, different_filters)
    print(f"Results with different filters: {cached_results}")

if __name__ == "__main__":
    print("Chat Cache Service Integration Demo")
    print("=" * 50)
    
    # הרצת הדגמות
    demonstrate_memory_caching()
    demonstrate_redis_caching()
    demonstrate_cache_invalidation()
    demonstrate_performance_monitoring()
    demonstrate_search_caching()
    
    print("\n" + "=" * 50)
    print("Demo completed successfully!")