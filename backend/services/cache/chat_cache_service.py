"""
Chat Cache Service
שירות cache מתקדם למערכת השיחות עם תמיכה ב-in-memory ו-Redis
"""

import os
import json
import time
import hashlib
import threading
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import weakref
from collections import OrderedDict

logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T')
CacheKey = Union[str, tuple]

class CacheStrategy(Enum):
    """אסטרטגיות cache שונות"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out

class CacheBackend(Enum):
    """סוגי backend לcache"""
    MEMORY = "memory"
    REDIS = "redis"
    HYBRID = "hybrid"  # Memory + Redis

@dataclass
class CacheEntry:
    """רשומת cache בודדת"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """בדיקה אם הרשומה פגה"""
        if self.ttl_seconds is None:
            return False
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """גיל הרשומה בשניות"""
        return (datetime.utcnow() - self.created_at).total_seconds()
    
    def touch(self):
        """עדכון זמן גישה אחרון"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1

@dataclass
class CacheStats:
    """סטטיסטיקות cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    hit_rate: float = 0.0
    
    def update_hit_rate(self):
        """עדכון אחוז הצלחה"""
        total = self.hits + self.misses
        self.hit_rate = (self.hits / total * 100) if total > 0 else 0.0

class LRUCache(Generic[T]):
    """
    LRU Cache implementation מותאם לביצועים
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = None):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()
    
    def get(self, key: str) -> Optional[T]:
        """קבלת ערך מה-cache"""
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                self._stats.update_hit_rate()
                return None
            
            entry = self._cache[key]
            
            # בדיקת תפוגה
            if entry.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                self._stats.entry_count -= 1
                self._stats.total_size_bytes -= entry.size_bytes
                self._stats.update_hit_rate()
                return None
            
            # עדכון LRU - העברה לסוף
            entry.touch()
            self._cache.move_to_end(key)
            
            self._stats.hits += 1
            self._stats.update_hit_rate()
            return entry.value
    
    def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> None:
        """הגדרת ערך ב-cache"""
        with self._lock:
            # חישוב גודל
            size_bytes = self._calculate_size(value)
            
            # יצירת entry חדש
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                ttl_seconds=ttl_seconds or self.ttl_seconds,
                size_bytes=size_bytes
            )
            
            # אם המפתח כבר קיים, עדכון
            if key in self._cache:
                old_entry = self._cache[key]
                self._stats.total_size_bytes -= old_entry.size_bytes
            else:
                self._stats.entry_count += 1
            
            self._cache[key] = entry
            self._cache.move_to_end(key)
            self._stats.total_size_bytes += size_bytes
            
            # בדיקת גבול גודל ופינוי אם נדרש
            self._evict_if_needed()
    
    def delete(self, key: str) -> bool:
        """מחיקת ערך מה-cache"""
        with self._lock:
            if key in self._cache:
                entry = self._cache.pop(key)
                self._stats.entry_count -= 1
                self._stats.total_size_bytes -= entry.size_bytes
                return True
            return False
    
    def clear(self) -> None:
        """ניקוי כל ה-cache"""
        with self._lock:
            self._cache.clear()
            self._stats = CacheStats()
    
    def _evict_if_needed(self) -> None:
        """פינוי entries אם נדרש"""
        while len(self._cache) > self.max_size:
            # הסרת הישן ביותר (LRU)
            oldest_key, oldest_entry = self._cache.popitem(last=False)
            self._stats.evictions += 1
            self._stats.entry_count -= 1
            self._stats.total_size_bytes -= oldest_entry.size_bytes
            logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def _calculate_size(self, value: Any) -> int:
        """חישוב גודל ערך בבתים (הערכה)"""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (list, dict)):
                return len(json.dumps(value, ensure_ascii=False).encode('utf-8'))
            else:
                return len(str(value).encode('utf-8'))
        except:
            return 100  # הערכה ברירת מחדל
    
    def get_stats(self) -> CacheStats:
        """קבלת סטטיסטיקות cache"""
        with self._lock:
            return self._stats
    
    def cleanup_expired(self) -> int:
        """ניקוי entries שפגו"""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired:
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self._cache.pop(key)
                self._stats.evictions += 1
                self._stats.entry_count -= 1
                self._stats.total_size_bytes -= entry.size_bytes
            
            return len(expired_keys)

class RedisCache:
    """
    Redis Cache implementation (אופציונלי)
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, 
                 password: Optional[str] = None, prefix: str = 'chat_cache:'):
        self.prefix = prefix
        self._redis = None
        self._connection_params = {
            'host': host,
            'port': port,
            'db': db,
            'password': password,
            'decode_responses': True
        }
        self._stats = CacheStats()
        self._lock = threading.RLock()
        
        # ניסיון חיבור
        self._connect()
    
    def _connect(self) -> bool:
        """חיבור ל-Redis"""
        try:
            import redis
            self._redis = redis.Redis(**self._connection_params)
            self._redis.ping()  # בדיקת חיבור
            logger.info("Connected to Redis successfully")
            return True
        except ImportError:
            logger.warning("Redis library not installed. Install with: pip install redis")
            return False
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            return False
    
    def is_available(self) -> bool:
        """בדיקה אם Redis זמין"""
        return self._redis is not None
    
    def get(self, key: str) -> Optional[Any]:
        """קבלת ערך מ-Redis"""
        if not self.is_available():
            return None
        
        try:
            with self._lock:
                full_key = f"{self.prefix}{key}"
                data = self._redis.get(full_key)
                
                if data is None:
                    self._stats.misses += 1
                    self._stats.update_hit_rate()
                    return None
                
                # פענוח JSON
                value = json.loads(data)
                self._stats.hits += 1
                self._stats.update_hit_rate()
                return value
                
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            self._stats.misses += 1
            self._stats.update_hit_rate()
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """הגדרת ערך ב-Redis"""
        if not self.is_available():
            return False
        
        try:
            with self._lock:
                full_key = f"{self.prefix}{key}"
                data = json.dumps(value, ensure_ascii=False, default=str)
                
                if ttl_seconds:
                    result = self._redis.setex(full_key, ttl_seconds, data)
                else:
                    result = self._redis.set(full_key, data)
                
                if result:
                    self._stats.entry_count += 1
                    self._stats.total_size_bytes += len(data.encode('utf-8'))
                
                return bool(result)
                
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """מחיקת ערך מ-Redis"""
        if not self.is_available():
            return False
        
        try:
            with self._lock:
                full_key = f"{self.prefix}{key}"
                result = self._redis.delete(full_key)
                
                if result:
                    self._stats.entry_count -= 1
                
                return bool(result)
                
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """ניקוי כל המפתחות עם הprefix"""
        if not self.is_available():
            return False
        
        try:
            with self._lock:
                pattern = f"{self.prefix}*"
                keys = self._redis.keys(pattern)
                
                if keys:
                    result = self._redis.delete(*keys)
                    self._stats.entry_count = 0
                    self._stats.total_size_bytes = 0
                    return bool(result)
                
                return True
                
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def get_stats(self) -> CacheStats:
        """קבלת סטטיסטיקות Redis cache"""
        return self._stats

class ChatCacheService:
    """
    שירות cache מתקדם למערכת השיחות
    """
    
    def __init__(self, 
                 backend: CacheBackend = CacheBackend.MEMORY,
                 max_memory_size: int = 1000,
                 default_ttl: int = 3600,  # שעה
                 redis_config: Optional[Dict[str, Any]] = None):
        
        self.backend = backend
        self.default_ttl = default_ttl
        self._lock = threading.RLock()
        
        # אתחול cache backends
        self.memory_cache = LRUCache(max_size=max_memory_size, ttl_seconds=default_ttl)
        
        self.redis_cache = None
        if backend in [CacheBackend.REDIS, CacheBackend.HYBRID]:
            redis_config = redis_config or {}
            self.redis_cache = RedisCache(**redis_config)
            
            if not self.redis_cache.is_available():
                logger.warning("Redis not available, falling back to memory cache")
                self.backend = CacheBackend.MEMORY
        
        # Cache invalidation callbacks
        self._invalidation_callbacks: Dict[str, List[Callable]] = {}
        
        # Background cleanup thread
        self._cleanup_thread = None
        self._start_cleanup_thread()
        
        logger.info(f"ChatCacheService initialized with backend: {self.backend.value}")
    
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """קבלת ערך מה-cache"""
        try:
            if self.backend == CacheBackend.MEMORY:
                return self.memory_cache.get(key) or default
            
            elif self.backend == CacheBackend.REDIS:
                return self.redis_cache.get(key) or default
            
            elif self.backend == CacheBackend.HYBRID:
                # נסה memory cache קודם
                value = self.memory_cache.get(key)
                if value is not None:
                    return value
                
                # אם לא נמצא, נסה Redis
                value = self.redis_cache.get(key)
                if value is not None:
                    # שמור ב-memory cache לפעם הבאה
                    self.memory_cache.set(key, value)
                    return value
                
                return default
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> bool:
        """הגדרת ערך ב-cache"""
        try:
            ttl = ttl_seconds or self.default_ttl
            success = True
            
            if self.backend in [CacheBackend.MEMORY, CacheBackend.HYBRID]:
                self.memory_cache.set(key, value, ttl)
            
            if self.backend in [CacheBackend.REDIS, CacheBackend.HYBRID]:
                success = self.redis_cache.set(key, value, ttl)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """מחיקת ערך מה-cache"""
        try:
            success = True
            
            if self.backend in [CacheBackend.MEMORY, CacheBackend.HYBRID]:
                self.memory_cache.delete(key)
            
            if self.backend in [CacheBackend.REDIS, CacheBackend.HYBRID]:
                success = self.redis_cache.delete(key)
            
            # הפעלת callbacks של invalidation
            self._trigger_invalidation_callbacks(key)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """ניקוי כל ה-cache"""
        try:
            success = True
            
            if self.backend in [CacheBackend.MEMORY, CacheBackend.HYBRID]:
                self.memory_cache.clear()
            
            if self.backend in [CacheBackend.REDIS, CacheBackend.HYBRID]:
                success = self.redis_cache.clear()
            
            return success
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """ביטול cache לפי pattern"""
        try:
            invalidated = 0
            
            if self.backend in [CacheBackend.MEMORY, CacheBackend.HYBRID]:
                # Memory cache - iterate through keys
                keys_to_delete = []
                for key in self.memory_cache._cache.keys():
                    if self._match_pattern(key, pattern):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    if self.memory_cache.delete(key):
                        invalidated += 1
            
            if self.backend in [CacheBackend.REDIS, CacheBackend.HYBRID] and self.redis_cache.is_available():
                # Redis - use keys pattern matching
                try:
                    import redis
                    full_pattern = f"{self.redis_cache.prefix}{pattern}"
                    keys = self.redis_cache._redis.keys(full_pattern)
                    
                    for key in keys:
                        clean_key = key.replace(self.redis_cache.prefix, '')
                        if self.redis_cache.delete(clean_key):
                            invalidated += 1
                            
                except Exception as e:
                    logger.error(f"Redis pattern invalidation error: {e}")
            
            return invalidated
            
        except Exception as e:
            logger.error(f"Pattern invalidation error for pattern {pattern}: {e}")
            return 0
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """בדיקה אם מפתח תואם לpattern"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
    
    def get_stats(self) -> Dict[str, CacheStats]:
        """קבלת סטטיסטיקות cache"""
        stats = {}
        
        if self.backend in [CacheBackend.MEMORY, CacheBackend.HYBRID]:
            stats['memory'] = self.memory_cache.get_stats()
        
        if self.backend in [CacheBackend.REDIS, CacheBackend.HYBRID] and self.redis_cache:
            stats['redis'] = self.redis_cache.get_stats()
        
        return stats
    
    def register_invalidation_callback(self, pattern: str, callback: Callable[[str], None]):
        """רישום callback לביטול cache"""
        if pattern not in self._invalidation_callbacks:
            self._invalidation_callbacks[pattern] = []
        self._invalidation_callbacks[pattern].append(callback)
    
    def _trigger_invalidation_callbacks(self, key: str):
        """הפעלת callbacks של invalidation"""
        for pattern, callbacks in self._invalidation_callbacks.items():
            if self._match_pattern(key, pattern):
                for callback in callbacks:
                    try:
                        callback(key)
                    except Exception as e:
                        logger.error(f"Invalidation callback error: {e}")
    
    def _start_cleanup_thread(self):
        """התחלת thread לניקוי תקופתי"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # כל 5 דקות
                    
                    if self.backend in [CacheBackend.MEMORY, CacheBackend.HYBRID]:
                        expired_count = self.memory_cache.cleanup_expired()
                        if expired_count > 0:
                            logger.debug(f"Cleaned up {expired_count} expired cache entries")
                            
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

# Decorator לcaching פונקציות
def cached(ttl_seconds: int = 3600, key_prefix: str = "func"):
    """
    Decorator לcaching תוצאות פונקציות
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # יצירת מפתח cache
            key_parts = [key_prefix, func.__name__]
            
            # הוספת args
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))
                else:
                    key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
            
            # הוספת kwargs
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (str, int, float, bool)):
                    key_parts.append(f"{k}:{v}")
                else:
                    key_parts.append(f"{k}:{hashlib.md5(str(v).encode()).hexdigest()[:8]}")
            
            cache_key = ":".join(key_parts)
            
            # ניסיון קבלה מ-cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # חישוב התוצאה
            result = func(*args, **kwargs)
            
            # שמירה ב-cache
            cache_service.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator

# Chat-specific cache functions
class ChatCacheManager:
    """
    מנהל cache ספציפי למערכת השיחות
    """
    
    def __init__(self, cache_service: ChatCacheService):
        self.cache = cache_service
    
    # Session caching
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """קבלת session מ-cache"""
        return self.cache.get(f"session:{session_id}")
    
    def set_session(self, session_id: str, session_data: Dict[str, Any], ttl: int = 1800):
        """שמירת session ב-cache (30 דקות)"""
        return self.cache.set(f"session:{session_id}", session_data, ttl)
    
    def invalidate_session(self, session_id: str):
        """ביטול cache של session"""
        return self.cache.delete(f"session:{session_id}")
    
    # Messages caching
    def get_session_messages(self, session_id: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """קבלת הודעות session מ-cache"""
        return self.cache.get(f"messages:{session_id}:{limit}")
    
    def set_session_messages(self, session_id: str, messages: List[Dict[str, Any]], limit: int = 50):
        """שמירת הודעות session ב-cache"""
        return self.cache.set(f"messages:{session_id}:{limit}", messages, 600)  # 10 דקות
    
    def invalidate_session_messages(self, session_id: str):
        """ביטול cache של הודעות session"""
        return self.cache.invalidate_pattern(f"messages:{session_id}:*")
    
    # User sessions caching
    def get_user_sessions(self, user_id: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """קבלת sessions של משתמש מ-cache"""
        return self.cache.get(f"user_sessions:{user_id}:{limit}")
    
    def set_user_sessions(self, user_id: str, sessions: List[Dict[str, Any]], limit: int = 20):
        """שמירת sessions של משתמש ב-cache"""
        return self.cache.set(f"user_sessions:{user_id}:{limit}", sessions, 900)  # 15 דקות
    
    def invalidate_user_sessions(self, user_id: str):
        """ביטול cache של sessions משתמש"""
        return self.cache.invalidate_pattern(f"user_sessions:{user_id}:*")
    
    # Search results caching
    def get_search_results(self, query: str, filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """קבלת תוצאות חיפוש מ-cache"""
        search_key = self._generate_search_key(query, filters)
        return self.cache.get(f"search:{search_key}")
    
    def set_search_results(self, query: str, filters: Dict[str, Any], results: List[Dict[str, Any]]):
        """שמירת תוצאות חיפוש ב-cache"""
        search_key = self._generate_search_key(query, filters)
        return self.cache.set(f"search:{search_key}", results, 300)  # 5 דקות
    
    def _generate_search_key(self, query: str, filters: Dict[str, Any]) -> str:
        """יצירת מפתח לחיפוש"""
        filter_str = json.dumps(filters, sort_keys=True, ensure_ascii=False)
        combined = f"{query}:{filter_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    # Statistics caching
    def get_stats(self, stat_type: str, period: str = "daily") -> Optional[Dict[str, Any]]:
        """קבלת סטטיסטיקות מ-cache"""
        return self.cache.get(f"stats:{stat_type}:{period}")
    
    def set_stats(self, stat_type: str, stats_data: Dict[str, Any], period: str = "daily"):
        """שמירת סטטיסטיקות ב-cache"""
        ttl = 3600 if period == "hourly" else 86400  # שעה או יום
        return self.cache.set(f"stats:{stat_type}:{period}", stats_data, ttl)

# Global cache service instance
cache_service = ChatCacheService(
    backend=CacheBackend.MEMORY,  # ברירת מחדל
    max_memory_size=1000,
    default_ttl=3600
)

# Global chat cache manager
chat_cache = ChatCacheManager(cache_service)

# Initialize Redis if available
def init_redis_cache(host: str = 'localhost', port: int = 6379, password: Optional[str] = None):
    """אתחול Redis cache"""
    global cache_service, chat_cache
    
    redis_config = {
        'host': host,
        'port': port,
        'password': password
    }
    
    cache_service = ChatCacheService(
        backend=CacheBackend.HYBRID,
        redis_config=redis_config
    )
    
    chat_cache = ChatCacheManager(cache_service)
    logger.info("Redis cache initialized")

# Utility functions
def get_cache_info() -> Dict[str, Any]:
    """קבלת מידע על מצב ה-cache"""
    stats = cache_service.get_stats()
    
    info = {
        'backend': cache_service.backend.value,
        'stats': stats,
        'redis_available': cache_service.redis_cache.is_available() if cache_service.redis_cache else False
    }
    
    return info

def clear_all_cache():
    """ניקוי כל ה-cache"""
    return cache_service.clear()