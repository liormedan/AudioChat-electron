"""
בדיקות לשירות Cache של מערכת השיחות
"""

import unittest
import tempfile
import os
import shutil
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.services.cache.chat_cache_service import (
    ChatCacheService, LRUCache, RedisCache, ChatCacheManager,
    CacheBackend, CacheStrategy, CacheEntry, CacheStats,
    cached, cache_service, chat_cache, get_cache_info, clear_all_cache
)


class TestCacheEntry(unittest.TestCase):
    
    def test_cache_entry_creation(self):
        """בדיקת יצירת cache entry"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            ttl_seconds=3600
        )
        
        self.assertEqual(entry.key, "test_key")
        self.assertEqual(entry.value, "test_value")
        self.assertEqual(entry.access_count, 0)
        self.assertFalse(entry.is_expired)
    
    def test_cache_entry_expiration(self):
        """בדיקת תפוגת cache entry"""
        # Entry שפג
        old_time = datetime.utcnow() - timedelta(hours=2)
        expired_entry = CacheEntry(
            key="expired",
            value="value",
            created_at=old_time,
            last_accessed=old_time,
            ttl_seconds=3600  # שעה
        )
        
        self.assertTrue(expired_entry.is_expired)
        
        # Entry שלא פג
        fresh_entry = CacheEntry(
            key="fresh",
            value="value",
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            ttl_seconds=3600
        )
        
        self.assertFalse(fresh_entry.is_expired)
    
    def test_cache_entry_touch(self):
        """בדיקת עדכון זמן גישה"""
        entry = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow()
        )
        
        original_access_count = entry.access_count
        original_last_accessed = entry.last_accessed
        
        time.sleep(0.01)  # המתנה קצרה
        entry.touch()
        
        self.assertEqual(entry.access_count, original_access_count + 1)
        self.assertGreater(entry.last_accessed, original_last_accessed)


class TestLRUCache(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.cache = LRUCache(max_size=3, ttl_seconds=3600)
    
    def test_basic_get_set(self):
        """בדיקת get ו-set בסיסיים"""
        # Set value
        self.cache.set("key1", "value1")
        
        # Get value
        result = self.cache.get("key1")
        self.assertEqual(result, "value1")
        
        # Get non-existent key
        result = self.cache.get("nonexistent")
        self.assertIsNone(result)
    
    def test_lru_eviction(self):
        """בדיקת פינוי LRU"""
        # מילוי cache עד הגבול
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # גישה ל-key1 כדי להפוך אותו לrecently used
        self.cache.get("key1")
        
        # הוספת key חדש - צריך לפנות את key2 (הכי פחות used)
        self.cache.set("key4", "value4")
        
        # key2 צריך להיות מפונה
        self.assertIsNone(self.cache.get("key2"))
        
        # key1, key3, key4 צריכים להיות קיימים
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key3"), "value3")
        self.assertEqual(self.cache.get("key4"), "value4")
    
    def test_ttl_expiration(self):
        """בדיקת תפוגת TTL"""
        # יצירת cache עם TTL קצר
        short_cache = LRUCache(max_size=10, ttl_seconds=1)
        
        short_cache.set("key1", "value1")
        
        # מיד אחרי הגדרה - צריך להיות זמין
        self.assertEqual(short_cache.get("key1"), "value1")
        
        # המתנה לתפוגה
        time.sleep(1.1)
        
        # אחרי תפוגה - צריך להחזיר None
        self.assertIsNone(short_cache.get("key1"))
    
    def test_update_existing_key(self):
        """בדיקת עדכון מפתח קיים"""
        self.cache.set("key1", "value1")
        self.cache.set("key1", "updated_value")
        
        result = self.cache.get("key1")
        self.assertEqual(result, "updated_value")
    
    def test_delete(self):
        """בדיקת מחיקה"""
        self.cache.set("key1", "value1")
        
        # מחיקה מוצלחת
        result = self.cache.delete("key1")
        self.assertTrue(result)
        
        # המפתח לא צריך להיות קיים יותר
        self.assertIsNone(self.cache.get("key1"))
        
        # מחיקת מפתח לא קיים
        result = self.cache.delete("nonexistent")
        self.assertFalse(result)
    
    def test_clear(self):
        """בדיקת ניקוי cache"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
        
        stats = self.cache.get_stats()
        self.assertEqual(stats.entry_count, 0)
    
    def test_stats(self):
        """בדיקת סטטיסטיקות"""
        # התחלה עם stats ריקים
        stats = self.cache.get_stats()
        self.assertEqual(stats.hits, 0)
        self.assertEqual(stats.misses, 0)
        
        # Set ו-get מוצלח
        self.cache.set("key1", "value1")
        result = self.cache.get("key1")
        
        stats = self.cache.get_stats()
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.misses, 0)
        self.assertEqual(stats.entry_count, 1)
        
        # Get לא מוצלח
        self.cache.get("nonexistent")
        
        stats = self.cache.get_stats()
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.misses, 1)
        self.assertEqual(stats.hit_rate, 50.0)
    
    def test_cleanup_expired(self):
        """בדיקת ניקוי entries שפגו"""
        # יצירת cache עם TTL קצר
        short_cache = LRUCache(max_size=10, ttl_seconds=1)
        
        short_cache.set("key1", "value1")
        short_cache.set("key2", "value2")
        
        # המתנה לתפוגה
        time.sleep(1.1)
        
        # הוספת entry חדש שלא פג
        short_cache.set("key3", "value3")
        
        # ניקוי entries שפגו
        expired_count = short_cache.cleanup_expired()
        
        self.assertEqual(expired_count, 2)  # key1 ו-key2 פגו
        self.assertIsNone(short_cache.get("key1"))
        self.assertIsNone(short_cache.get("key2"))
        self.assertEqual(short_cache.get("key3"), "value3")


class TestRedisCache(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        # ניסיון יצירת Redis cache (יכשל אם Redis לא זמין)
        self.redis_cache = RedisCache(prefix="test_cache:")
    
    def test_redis_availability(self):
        """בדיקת זמינות Redis"""
        # הבדיקה תעבור גם אם Redis לא זמין
        is_available = self.redis_cache.is_available()
        self.assertIsInstance(is_available, bool)
    
    @unittest.skipUnless(
        RedisCache().is_available(), 
        "Redis not available"
    )
    def test_redis_basic_operations(self):
        """בדיקת פעולות בסיסיות ב-Redis"""
        # Clear any existing test data
        self.redis_cache.clear()
        
        # Set value
        result = self.redis_cache.set("test_key", {"data": "test_value"})
        self.assertTrue(result)
        
        # Get value
        result = self.redis_cache.get("test_key")
        self.assertEqual(result, {"data": "test_value"})
        
        # Delete value
        result = self.redis_cache.delete("test_key")
        self.assertTrue(result)
        
        # Get deleted value
        result = self.redis_cache.get("test_key")
        self.assertIsNone(result)
    
    @unittest.skipUnless(
        RedisCache().is_available(), 
        "Redis not available"
    )
    def test_redis_ttl(self):
        """בדיקת TTL ב-Redis"""
        # Set value with short TTL
        result = self.redis_cache.set("ttl_key", "ttl_value", ttl_seconds=1)
        self.assertTrue(result)
        
        # Immediately get - should exist
        result = self.redis_cache.get("ttl_key")
        self.assertEqual(result, "ttl_value")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Get after expiration - should be None
        result = self.redis_cache.get("ttl_key")
        self.assertIsNone(result)


class TestChatCacheService(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.cache_service = ChatCacheService(
            backend=CacheBackend.MEMORY,
            max_memory_size=10,
            default_ttl=3600
        )
    
    def test_memory_backend(self):
        """בדיקת memory backend"""
        # Set and get
        result = self.cache_service.set("test_key", "test_value")
        self.assertTrue(result)
        
        value = self.cache_service.get("test_key")
        self.assertEqual(value, "test_value")
        
        # Delete
        result = self.cache_service.delete("test_key")
        self.assertTrue(result)
        
        value = self.cache_service.get("test_key")
        self.assertIsNone(value)
    
    def test_default_value(self):
        """בדיקת ערך ברירת מחדל"""
        value = self.cache_service.get("nonexistent", "default")
        self.assertEqual(value, "default")
    
    def test_pattern_invalidation(self):
        """בדיקת ביטול לפי pattern"""
        # הגדרת מספר מפתחות
        self.cache_service.set("user:123:profile", {"name": "John"})
        self.cache_service.set("user:123:settings", {"theme": "dark"})
        self.cache_service.set("user:456:profile", {"name": "Jane"})
        self.cache_service.set("session:abc", {"data": "test"})
        
        # ביטול כל המפתחות של user:123
        invalidated = self.cache_service.invalidate_pattern("user:123:*")
        self.assertEqual(invalidated, 2)
        
        # בדיקה שהמפתחות נמחקו
        self.assertIsNone(self.cache_service.get("user:123:profile"))
        self.assertIsNone(self.cache_service.get("user:123:settings"))
        
        # בדיקה שמפתחות אחרים נשארו
        self.assertIsNotNone(self.cache_service.get("user:456:profile"))
        self.assertIsNotNone(self.cache_service.get("session:abc"))
    
    def test_stats(self):
        """בדיקת סטטיסטיקות"""
        stats = self.cache_service.get_stats()
        self.assertIn('memory', stats)
        
        memory_stats = stats['memory']
        self.assertIsInstance(memory_stats, CacheStats)
    
    def test_clear_all(self):
        """בדיקת ניקוי כל ה-cache"""
        self.cache_service.set("key1", "value1")
        self.cache_service.set("key2", "value2")
        
        result = self.cache_service.clear()
        self.assertTrue(result)
        
        self.assertIsNone(self.cache_service.get("key1"))
        self.assertIsNone(self.cache_service.get("key2"))
    
    def test_invalidation_callbacks(self):
        """בדיקת callbacks של invalidation"""
        callback_called = []
        
        def test_callback(key):
            callback_called.append(key)
        
        # רישום callback
        self.cache_service.register_invalidation_callback("user:*", test_callback)
        
        # הגדרה ומחיקה של מפתח
        self.cache_service.set("user:123", "data")
        self.cache_service.delete("user:123")
        
        # בדיקה שה-callback נקרא
        self.assertIn("user:123", callback_called)


class TestChatCacheManager(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        cache_service = ChatCacheService(backend=CacheBackend.MEMORY)
        self.cache_manager = ChatCacheManager(cache_service)
    
    def test_session_caching(self):
        """בדיקת caching של sessions"""
        session_data = {
            "id": "session_123",
            "title": "Test Session",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # שמירה
        result = self.cache_manager.set_session("session_123", session_data)
        self.assertTrue(result)
        
        # קבלה
        cached_session = self.cache_manager.get_session("session_123")
        self.assertEqual(cached_session, session_data)
        
        # ביטול
        result = self.cache_manager.invalidate_session("session_123")
        self.assertTrue(result)
        
        # בדיקה שנמחק
        cached_session = self.cache_manager.get_session("session_123")
        self.assertIsNone(cached_session)
    
    def test_messages_caching(self):
        """בדיקת caching של הודעות"""
        messages = [
            {"id": "msg1", "content": "Hello", "role": "user"},
            {"id": "msg2", "content": "Hi there!", "role": "assistant"}
        ]
        
        # שמירה
        result = self.cache_manager.set_session_messages("session_123", messages, 50)
        self.assertTrue(result)
        
        # קבלה
        cached_messages = self.cache_manager.get_session_messages("session_123", 50)
        self.assertEqual(cached_messages, messages)
        
        # ביטול
        invalidated = self.cache_manager.invalidate_session_messages("session_123")
        self.assertGreaterEqual(invalidated, 0)
    
    def test_user_sessions_caching(self):
        """בדיקת caching של sessions משתמש"""
        user_sessions = [
            {"id": "session1", "title": "Chat 1"},
            {"id": "session2", "title": "Chat 2"}
        ]
        
        # שמירה
        result = self.cache_manager.set_user_sessions("user_123", user_sessions, 20)
        self.assertTrue(result)
        
        # קבלה
        cached_sessions = self.cache_manager.get_user_sessions("user_123", 20)
        self.assertEqual(cached_sessions, user_sessions)
        
        # ביטול
        invalidated = self.cache_manager.invalidate_user_sessions("user_123")
        self.assertGreaterEqual(invalidated, 0)
    
    def test_search_results_caching(self):
        """בדיקת caching של תוצאות חיפוש"""
        query = "test query"
        filters = {"date_from": "2024-01-01", "user_id": "123"}
        results = [
            {"id": "msg1", "content": "test message 1"},
            {"id": "msg2", "content": "test message 2"}
        ]
        
        # שמירה
        result = self.cache_manager.set_search_results(query, filters, results)
        self.assertTrue(result)
        
        # קבלה
        cached_results = self.cache_manager.get_search_results(query, filters)
        self.assertEqual(cached_results, results)
        
        # בדיקה עם filters שונים - צריך להחזיר None
        different_filters = {"date_from": "2024-01-02", "user_id": "456"}
        cached_results = self.cache_manager.get_search_results(query, different_filters)
        self.assertIsNone(cached_results)
    
    def test_stats_caching(self):
        """בדיקת caching של סטטיסטיקות"""
        stats_data = {
            "total_messages": 1000,
            "total_sessions": 50,
            "active_users": 25
        }
        
        # שמירה
        result = self.cache_manager.set_stats("general", stats_data, "daily")
        self.assertTrue(result)
        
        # קבלה
        cached_stats = self.cache_manager.get_stats("general", "daily")
        self.assertEqual(cached_stats, stats_data)


class TestCachedDecorator(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        # ניקוי cache לפני כל בדיקה
        cache_service.clear()
    
    def test_function_caching(self):
        """בדיקת caching של פונקציות"""
        call_count = 0
        
        @cached(ttl_seconds=3600, key_prefix="test_func")
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # קריאה ראשונה - צריכה לחשב
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # קריאה שנייה עם אותם פרמטרים - צריכה לחזור מ-cache
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # לא צריך לחשב שוב
        
        # קריאה עם פרמטרים שונים - צריכה לחשב
        result3 = expensive_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count, 2)
    
    def test_function_caching_with_kwargs(self):
        """בדיקת caching עם kwargs"""
        call_count = 0
        
        @cached(ttl_seconds=3600, key_prefix="test_kwargs")
        def function_with_kwargs(a, b=10, c=20):
            nonlocal call_count
            call_count += 1
            return a + b + c
        
        # קריאות עם kwargs שונים
        result1 = function_with_kwargs(1, b=5, c=10)
        result2 = function_with_kwargs(1, b=5, c=10)  # אותם פרמטרים
        result3 = function_with_kwargs(1, b=6, c=10)  # פרמטרים שונים
        
        self.assertEqual(result1, 16)
        self.assertEqual(result2, 16)
        self.assertEqual(result3, 17)
        self.assertEqual(call_count, 2)  # רק 2 חישובים


class TestUtilityFunctions(unittest.TestCase):
    
    def test_get_cache_info(self):
        """בדיקת פונקציית מידע cache"""
        info = get_cache_info()
        
        self.assertIn('backend', info)
        self.assertIn('stats', info)
        self.assertIn('redis_available', info)
        
        self.assertEqual(info['backend'], 'memory')
        self.assertIsInstance(info['redis_available'], bool)
    
    def test_clear_all_cache_function(self):
        """בדיקת פונקציית ניקוי כל ה-cache"""
        # הוספת נתונים ל-cache
        cache_service.set("test_key", "test_value")
        
        # ניקוי
        result = clear_all_cache()
        self.assertTrue(result)
        
        # בדיקה שנוקה
        value = cache_service.get("test_key")
        self.assertIsNone(value)


class TestConcurrency(unittest.TestCase):
    
    def test_concurrent_access(self):
        """בדיקת גישה במקביל ל-cache"""
        cache = LRUCache(max_size=100)
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(10):
                    key = f"worker_{worker_id}_key_{i}"
                    value = f"worker_{worker_id}_value_{i}"
                    
                    # Set
                    cache.set(key, value)
                    
                    # Get
                    retrieved = cache.get(key)
                    if retrieved == value:
                        results.append(f"{worker_id}_{i}")
                    
                    time.sleep(0.001)  # המתנה קצרה
                    
            except Exception as e:
                errors.append(str(e))
        
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
        self.assertEqual(len(results), 50)  # 5 workers * 10 operations


if __name__ == '__main__':
    unittest.main()