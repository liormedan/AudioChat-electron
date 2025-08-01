# Chat Cache Service Documentation

מערכת Cache מתקדמת למערכת השיחות עם תמיכה ב-in-memory ו-Redis caching.

## תכונות עיקריות

### 1. In-Memory Caching
- **LRU (Least Recently Used)** eviction strategy
- Thread-safe operations
- TTL (Time To Live) support
- Real-time statistics
- Automatic cleanup של entries שפגו

### 2. Redis Support (אופציונלי)
- Distributed caching
- Persistence across restarts
- Scalable for multiple instances
- JSON serialization/deserialization
- Connection pooling

### 3. Hybrid Mode
- Memory cache כ-L1 cache (מהיר)
- Redis כ-L2 cache (persistent)
- Automatic fallback mechanisms
- Optimal performance

### 4. Cache Invalidation Strategies
- Single key invalidation
- Pattern-based invalidation
- Callback-based invalidation
- Automatic cleanup threads

## שימוש בסיסי

### אתחול Cache Service

```python
from backend.services.cache.chat_cache_service import ChatCacheService, CacheBackend

# Memory-only cache
cache = ChatCacheService(
    backend=CacheBackend.MEMORY,
    max_memory_size=1000,
    default_ttl=3600
)

# Redis cache
cache = ChatCacheService(
    backend=CacheBackend.REDIS,
    redis_config={
        'host': 'localhost',
        'port': 6379,
        'password': 'your_password'
    }
)

# Hybrid cache (מומלץ לproduction)
cache = ChatCacheService(
    backend=CacheBackend.HYBRID,
    max_memory_size=1000,
    redis_config={'host': 'localhost', 'port': 6379}
)
```

### פעולות בסיסיות

```python
# Set value
cache.set("user:123", {"name": "John", "email": "john@example.com"}, ttl_seconds=1800)

# Get value
user_data = cache.get("user:123")
if user_data:
    print(f"User: {user_data['name']}")

# Get with default
user_data = cache.get("user:456", {"name": "Unknown"})

# Delete
cache.delete("user:123")

# Pattern invalidation
cache.invalidate_pattern("user:*")

# Clear all
cache.clear()
```

## Chat-Specific Caching

### שימוש ב-ChatCacheManager

```python
from backend.services.cache.chat_cache_service import chat_cache

# Session caching
session_data = {"id": "sess_123", "title": "My Chat", "user_id": "user_456"}
chat_cache.set_session("sess_123", session_data)
cached_session = chat_cache.get_session("sess_123")

# Messages caching
messages = [
    {"id": "msg1", "content": "Hello", "role": "user"},
    {"id": "msg2", "content": "Hi there!", "role": "assistant"}
]
chat_cache.set_session_messages("sess_123", messages, limit=50)
cached_messages = chat_cache.get_session_messages("sess_123", limit=50)

# User sessions caching
user_sessions = [{"id": "sess1", "title": "Chat 1"}, {"id": "sess2", "title": "Chat 2"}]
chat_cache.set_user_sessions("user_456", user_sessions, limit=20)
cached_sessions = chat_cache.get_user_sessions("user_456", limit=20)

# Search results caching
query = "machine learning"
filters = {"date_from": "2024-01-01", "user_id": "user_456"}
results = [{"id": "msg1", "content": "ML intro", "score": 0.95}]
chat_cache.set_search_results(query, filters, results)
cached_results = chat_cache.get_search_results(query, filters)
```

## Function Caching Decorator

```python
from backend.services.cache.chat_cache_service import cached

@cached(ttl_seconds=1800, key_prefix="expensive_calc")
def expensive_calculation(x, y, model_type="default"):
    # Expensive computation here
    time.sleep(2)  # Simulate work
    return x * y + hash(model_type)

# First call - computes and caches
result1 = expensive_calculation(10, 20, model_type="gpt-4")

# Second call with same params - returns from cache
result2 = expensive_calculation(10, 20, model_type="gpt-4")

# Different params - computes again
result3 = expensive_calculation(15, 25, model_type="claude")
```

## Cache Invalidation Strategies

### 1. Manual Invalidation

```python
# Single key
chat_cache.invalidate_session("session_123")

# Pattern-based
cache.invalidate_pattern("user:123:*")
cache.invalidate_pattern("session:*")
```

### 2. Callback-based Invalidation

```python
def on_user_update(key):
    print(f"User data updated: {key}")
    # Additional cleanup logic here

# Register callback
cache.register_invalidation_callback("user:*", on_user_update)

# When user data is deleted, callback will be triggered
cache.delete("user:123")  # Triggers on_user_update("user:123")
```

### 3. Automatic Cleanup

```python
# Cleanup expired entries (runs automatically every 5 minutes)
expired_count = cache.memory_cache.cleanup_expired()
print(f"Cleaned up {expired_count} expired entries")
```

## Performance Monitoring

### Statistics

```python
# Get cache statistics
stats = cache.get_stats()

for backend_name, backend_stats in stats.items():
    print(f"{backend_name} Cache:")
    print(f"  Hit Rate: {backend_stats.hit_rate:.2f}%")
    print(f"  Hits: {backend_stats.hits}")
    print(f"  Misses: {backend_stats.misses}")
    print(f"  Entries: {backend_stats.entry_count}")
    print(f"  Size: {backend_stats.total_size_bytes} bytes")
    print(f"  Evictions: {backend_stats.evictions}")
```

### Cache Info

```python
from backend.services.cache.chat_cache_service import get_cache_info

info = get_cache_info()
print(f"Backend: {info['backend']}")
print(f"Redis Available: {info['redis_available']}")
print(f"Stats: {info['stats']}")
```

## Redis Setup

### Installation

```bash
# Install Redis server
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Windows:
# Download from https://redis.io/download
```

### Configuration

```python
# Initialize Redis cache
from backend.services.cache.chat_cache_service import init_redis_cache

init_redis_cache(
    host='localhost',
    port=6379,
    password='your_password'  # Optional
)
```

### Docker Redis

```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass your_password
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## Best Practices

### 1. Cache Key Design

```python
# Good - hierarchical and descriptive
"user:123:profile"
"session:abc123:messages:50"
"search:query_hash:filters_hash"

# Bad - flat and unclear
"u123"
"data"
"temp"
```

### 2. TTL Strategy

```python
# Short-lived data (5-10 minutes)
chat_cache.set_session_messages(session_id, messages, ttl=600)

# Medium-lived data (30 minutes)
chat_cache.set_session(session_id, session_data, ttl=1800)

# Long-lived data (1-2 hours)
chat_cache.set_user_sessions(user_id, sessions, ttl=7200)
```

### 3. Error Handling

```python
try:
    cached_data = cache.get("key")
    if cached_data is None:
        # Cache miss - fetch from database
        data = fetch_from_database()
        cache.set("key", data, ttl=3600)
        return data
    return cached_data
except Exception as e:
    logger.warning(f"Cache error: {e}")
    # Fallback to database
    return fetch_from_database()
```

### 4. Memory Management

```python
# Monitor cache size
stats = cache.get_stats()
if stats['memory'].total_size_bytes > 100_000_000:  # 100MB
    logger.warning("Cache size is getting large")
    
# Periodic cleanup
cache.memory_cache.cleanup_expired()
```

## Testing

### Running Tests

```bash
# Run all cache tests
python -m pytest backend/services/cache/test_chat_cache_service.py -v

# Run specific test class
python -m pytest backend/services/cache/test_chat_cache_service.py::TestLRUCache -v

# Run with coverage
python -m pytest backend/services/cache/test_chat_cache_service.py --cov=backend.services.cache
```

### Integration Testing

```python
# Run integration example
python backend/services/cache/cache_integration_example.py
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```python
   # Check Redis status
   redis-cli ping
   # Should return PONG
   ```

2. **High Memory Usage**
   ```python
   # Reduce cache size
   cache = ChatCacheService(max_memory_size=500)
   
   # Lower TTL values
   cache.set("key", value, ttl_seconds=300)  # 5 minutes
   ```

3. **Cache Misses**
   ```python
   # Check cache statistics
   stats = cache.get_stats()
   print(f"Hit rate: {stats['memory'].hit_rate}%")
   
   # Verify key patterns
   print(f"Looking for key: {key}")
   ```

4. **Performance Issues**
   ```python
   # Use hybrid mode for better performance
   cache = ChatCacheService(backend=CacheBackend.HYBRID)
   
   # Implement proper key patterns
   # Avoid frequent pattern invalidations
   ```

## Configuration

### Environment Variables

```bash
# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0

# Cache configuration
CACHE_BACKEND=hybrid  # memory, redis, hybrid
CACHE_DEFAULT_TTL=3600
CACHE_MAX_MEMORY_SIZE=1000
```

### Production Settings

```python
# Production cache configuration
cache = ChatCacheService(
    backend=CacheBackend.HYBRID,
    max_memory_size=5000,  # Larger memory cache
    default_ttl=1800,      # 30 minutes default
    redis_config={
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'password': os.getenv('REDIS_PASSWORD'),
        'db': int(os.getenv('REDIS_DB', 0)),
        'socket_keepalive': True,
        'socket_keepalive_options': {},
        'health_check_interval': 30
    }
)
```

## API Reference

### ChatCacheService

- `get(key, default=None)` - Get value from cache
- `set(key, value, ttl_seconds=None)` - Set value in cache
- `delete(key)` - Delete key from cache
- `clear()` - Clear all cache
- `invalidate_pattern(pattern)` - Invalidate keys matching pattern
- `get_stats()` - Get cache statistics

### ChatCacheManager

- `get_session(session_id)` - Get session from cache
- `set_session(session_id, data, ttl=1800)` - Cache session
- `get_session_messages(session_id, limit=50)` - Get cached messages
- `set_session_messages(session_id, messages, limit=50)` - Cache messages
- `get_user_sessions(user_id, limit=20)` - Get user's sessions
- `set_user_sessions(user_id, sessions, limit=20)` - Cache user sessions
- `get_search_results(query, filters)` - Get cached search results
- `set_search_results(query, filters, results)` - Cache search results

### Utility Functions

- `get_cache_info()` - Get cache system information
- `clear_all_cache()` - Clear all caches
- `init_redis_cache(host, port, password)` - Initialize Redis cache