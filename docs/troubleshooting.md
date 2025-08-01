# Chat System Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### 1. Chat Service Not Available (503 Error)

**Symptoms:**
- API returns "Chat service is not available"
- `/api/chat/*` endpoints return 503 status

**Causes:**
- LLM service failed to initialize
- Missing model files
- Insufficient system resources

**Solutions:**

1. **Check LLM Service Status:**
```bash
curl http://127.0.0.1:5000/health
```

2. **Verify Model Availability:**
```bash
curl http://127.0.0.1:5000/api/llm/models
```

3. **Check System Resources:**
```bash
# Windows
tasklist /fi "imagename eq python.exe"
wmic process where name="python.exe" get processid,workingsetsize

# Check available memory
systeminfo | findstr "Available Physical Memory"
```

4. **Restart Services:**
```bash
scripts\stop.bat
scripts\start-dev.bat
```

5. **Check Logs:**
```bash
type logs\backend.log | findstr "ERROR"
```

#### 2. Database Connection Issues

**Symptoms:**
- "Database is locked" errors
- Session/message operations fail
- Slow query performance

**Solutions:**

1. **Check Database File Permissions:**
```bash
# Ensure database files are writable
dir data\*.db
```

2. **Close Existing Connections:**
```python
# In Python console
import sqlite3
conn = sqlite3.connect('data/chat_history.db')
conn.execute('PRAGMA journal_mode=WAL;')
conn.close()
```

3. **Database Integrity Check:**
```sql
-- Connect to database and run
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

4. **Optimize Database:**
```sql
VACUUM;
ANALYZE;
```

#### 3. Rate Limiting Issues (429 Error)

**Symptoms:**
- "Too Many Requests" errors
- Chat requests being blocked

**Solutions:**

1. **Check Rate Limit Status:**
```bash
curl -I http://127.0.0.1:5000/api/chat/send
# Look for X-RateLimit-* headers
```

2. **Adjust Rate Limits:**
```python
# In backend/services/ai/chat_security_service.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"]  # Increase from 5/minute
)
```

3. **Clear Rate Limit Cache:**
```bash
# Restart the service to clear in-memory rate limits
scripts\stop.bat
scripts\start-dev.bat
```

#### 4. Model Loading Failures

**Symptoms:**
- "Model not available" errors
- Long loading times
- Memory errors during model initialization

**Solutions:**

1. **Check Available Models:**
```bash
curl http://127.0.0.1:5000/api/llm/providers
```

2. **Verify Model Files:**
```bash
dir models\*.gguf
# Ensure model files exist and are not corrupted
```

3. **Check System Memory:**
```bash
# Ensure sufficient RAM for model loading
# Gemma 4B requires ~8GB RAM
systeminfo | findstr "Total Physical Memory"
```

4. **Try Different Model:**
```bash
curl -X POST http://127.0.0.1:5000/api/llm/active-model \
  -H "Content-Type: application/json" \
  -d '{"model_id": "alternative-model-id"}'
```

### Frontend Issues

#### 1. Chat Interface Not Loading

**Symptoms:**
- Blank chat interface
- JavaScript errors in console
- Components not rendering

**Solutions:**

1. **Check Console Errors:**
```javascript
// Open DevTools (F12) and check Console tab
// Look for React/TypeScript errors
```

2. **Verify API Connection:**
```javascript
// In browser console
fetch('/api/health')
  .then(r => r.json())
  .then(console.log)
```

3. **Clear Browser Cache:**
```bash
# Hard refresh
Ctrl + Shift + R

# Or clear all data
# DevTools > Application > Storage > Clear storage
```

4. **Check Network Tab:**
```javascript
// DevTools > Network tab
// Look for failed API requests
// Check for CORS errors
```

#### 2. Messages Not Displaying

**Symptoms:**
- Messages sent but not visible
- Empty message list
- Loading indicators stuck

**Solutions:**

1. **Check Store State:**
```javascript
// In React DevTools
// Look for chat store state
// Verify messages array is populated
```

2. **Verify Session ID:**
```javascript
// Check if valid session is selected
console.log('Current session:', currentSessionId);
```

3. **Check API Response:**
```javascript
// Network tab in DevTools
// Verify /api/chat/sessions/{id}/messages returns data
```

4. **Clear Component State:**
```javascript
// Force component re-render
// Or restart the application
```

#### 3. Streaming Not Working

**Symptoms:**
- No real-time message updates
- Messages appear all at once
- EventSource errors

**Solutions:**

1. **Check EventSource Support:**
```javascript
if (typeof EventSource !== 'undefined') {
  console.log('EventSource supported');
} else {
  console.log('EventSource not supported');
}
```

2. **Verify Streaming Endpoint:**
```bash
curl -N http://127.0.0.1:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"hello"}'
```

3. **Check Network Configuration:**
```javascript
// Ensure no proxy blocking SSE
// Check for firewall issues
```

4. **Fallback to Regular Requests:**
```javascript
// Disable streaming temporarily
const useStreaming = false;
```

#### 4. Performance Issues

**Symptoms:**
- Slow message rendering
- UI freezing during large conversations
- High memory usage

**Solutions:**

1. **Enable Virtual Scrolling:**
```typescript
<MessageList 
  virtualScrolling={true}
  itemHeight={80}
  maxHeight="600px"
/>
```

2. **Limit Message History:**
```typescript
const messages = allMessages.slice(-100); // Show last 100 messages
```

3. **Optimize Re-renders:**
```typescript
const MessageBubble = React.memo(({ message }) => {
  // Component implementation
});
```

4. **Check Memory Usage:**
```javascript
// DevTools > Performance tab
// Look for memory leaks
// Check component mount/unmount cycles
```

### Integration Issues

#### 1. Session Management Problems

**Symptoms:**
- Sessions not persisting
- Duplicate sessions created
- Session data corruption

**Solutions:**

1. **Check Session Storage:**
```bash
# Verify database tables
sqlite3 data/chat_history.db ".tables"
sqlite3 data/chat_history.db "SELECT * FROM chat_sessions LIMIT 5;"
```

2. **Validate Session Creation:**
```bash
curl -X POST http://127.0.0.1:5000/api/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Session"}'
```

3. **Clear Corrupted Sessions:**
```sql
-- Connect to database
DELETE FROM chat_sessions WHERE title IS NULL OR title = '';
```

#### 2. Message History Issues

**Symptoms:**
- Messages not saving
- Incomplete message history
- Search not working

**Solutions:**

1. **Check Message Storage:**
```sql
SELECT COUNT(*) FROM chat_messages;
SELECT * FROM chat_messages ORDER BY timestamp DESC LIMIT 5;
```

2. **Verify Message Format:**
```bash
curl -X POST http://127.0.0.1:5000/api/chat/sessions/test/messages \
  -H "Content-Type: application/json" \
  -d '{"role":"user","content":"test message"}'
```

3. **Rebuild Search Index:**
```sql
-- If using FTS
DROP TABLE IF EXISTS messages_fts;
CREATE VIRTUAL TABLE messages_fts USING fts5(content, session_id);
INSERT INTO messages_fts SELECT content, session_id FROM chat_messages;
```

### Security Issues

#### 1. Authentication Problems

**Symptoms:**
- Unauthorized access to sessions
- User ID validation failures
- Permission denied errors

**Solutions:**

1. **Check User ID Validation:**
```python
# In chat_security_service.py
def validate_session_access(session_id: str, user_id: str) -> bool:
    # Add logging to debug
    logger.debug(f"Validating access: session={session_id}, user={user_id}")
    return True  # Temporarily allow all access for debugging
```

2. **Verify Session Ownership:**
```sql
SELECT user_id FROM chat_sessions WHERE id = 'session_id';
```

#### 2. Input Sanitization Issues

**Symptoms:**
- XSS vulnerabilities
- Script injection
- Malformed content

**Solutions:**

1. **Check Sanitization Function:**
```python
def test_sanitization():
    test_input = "<script>alert('xss')</script>Hello"
    result = sanitize_input(test_input)
    print(f"Sanitized: {result}")
```

2. **Update Sanitization Rules:**
```python
import re
import html

def sanitize_input(input_text: str) -> str:
    # Remove script tags
    input_text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', input_text, flags=re.IGNORECASE)
    # Escape HTML
    input_text = html.escape(input_text)
    return input_text.strip()
```

### Performance Issues

#### 1. Slow Response Times

**Symptoms:**
- Long delays in chat responses
- Timeout errors
- High CPU usage

**Solutions:**

1. **Check Model Performance:**
```bash
curl -w "@curl-format.txt" -X POST http://127.0.0.1:5000/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"hello"}'

# Create curl-format.txt:
# time_total: %{time_total}s
# time_connect: %{time_connect}s
# time_starttransfer: %{time_starttransfer}s
```

2. **Monitor System Resources:**
```bash
# CPU usage
wmic cpu get loadpercentage /value

# Memory usage
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value
```

3. **Optimize Model Parameters:**
```json
{
  "temperature": 0.7,
  "max_tokens": 512,  // Reduce for faster responses
  "top_p": 0.9
}
```

4. **Enable Caching:**
```python
# In chat_cache_service.py
cache_enabled = True
cache_ttl = 300  # 5 minutes
```

#### 2. Memory Leaks

**Symptoms:**
- Increasing memory usage over time
- Application crashes
- System slowdown

**Solutions:**

1. **Monitor Memory Usage:**
```python
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
```

2. **Check for Unclosed Connections:**
```python
# Ensure database connections are closed
try:
    # Database operations
    pass
finally:
    if conn:
        conn.close()
```

3. **Clear Caches Periodically:**
```python
# In cache service
def cleanup_expired_cache():
    # Remove old cache entries
    pass
```

### Development Issues

#### 1. Hot Reload Not Working

**Symptoms:**
- Changes not reflected in browser
- Manual refresh required
- Build errors

**Solutions:**

1. **Check Vite Configuration:**
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    hmr: {
      port: 5173
    }
  }
});
```

2. **Verify File Watching:**
```bash
# Check if files are being watched
# Look for file system events in terminal
```

3. **Clear Build Cache:**
```bash
cd frontend/electron-app
rm -rf node_modules/.vite
npm run dev
```

#### 2. TypeScript Errors

**Symptoms:**
- Type checking failures
- Build errors
- IDE warnings

**Solutions:**

1. **Check TypeScript Configuration:**
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true
  }
}
```

2. **Update Type Definitions:**
```bash
npm install --save-dev @types/node @types/react
```

3. **Fix Common Type Issues:**
```typescript
// Use proper typing
interface Props {
  onAction?: (id: string, action: string) => void;
}

// Handle optional props
const { onAction = () => {} } = props;
```

## Diagnostic Tools

### Health Check Script

```bash
# Create health-check.bat
@echo off
echo Checking Audio Chat Studio Health...

echo.
echo 1. Backend Service:
curl -s http://127.0.0.1:5000/health || echo "Backend not responding"

echo.
echo 2. LLM Models:
curl -s http://127.0.0.1:5000/api/llm/models || echo "LLM service unavailable"

echo.
echo 3. Database:
sqlite3 data/chat_history.db "SELECT COUNT(*) as session_count FROM chat_sessions;"

echo.
echo 4. System Resources:
wmic cpu get loadpercentage /value | findstr "LoadPercentage"
wmic OS get FreePhysicalMemory /value | findstr "FreePhysicalMemory"

echo.
echo Health check complete.
pause
```

### Debug Mode

Enable comprehensive logging:

```python
# backend/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/debug.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Profiling

```python
# Add to chat service methods
import time
import functools

def profile_performance(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@profile_performance
def send_message(self, session_id: str, message: str):
    # Method implementation
    pass
```

## Getting Help

### Log Collection

When reporting issues, collect these logs:

```bash
# Backend logs
type logs\backend.log > debug_info.txt

# System info
systeminfo >> debug_info.txt

# Process info
tasklist | findstr python >> debug_info.txt

# Database info
sqlite3 data/chat_history.db ".schema" >> debug_info.txt
```

### Issue Reporting Template

```markdown
## Issue Description
Brief description of the problem

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 10/11
- Python Version: 3.x
- Node Version: 18.x
- Browser: Chrome/Firefox/Edge

## Logs
```
[Paste relevant logs here]
```

## Additional Context
Any other relevant information
```

### Community Resources

- GitHub Issues: Report bugs and feature requests
- Documentation: Check latest docs for updates
- Discord/Forum: Community support and discussions

## Prevention

### Regular Maintenance

```bash
# Weekly maintenance script
@echo off
echo Running maintenance...

echo Cleaning temporary files...
del /q data\temp\*.*

echo Optimizing database...
sqlite3 data/chat_history.db "VACUUM; ANALYZE;"

echo Checking disk space...
dir data\ | findstr "bytes free"

echo Maintenance complete.
```

### Monitoring

Set up basic monitoring:

```python
# monitor.py
import requests
import time
import logging

def check_health():
    try:
        response = requests.get('http://127.0.0.1:5000/health', timeout=5)
        if response.status_code == 200:
            logging.info("Health check passed")
        else:
            logging.warning(f"Health check failed: {response.status_code}")
    except Exception as e:
        logging.error(f"Health check error: {e}")

if __name__ == "__main__":
    while True:
        check_health()
        time.sleep(60)  # Check every minute
```

This troubleshooting guide should help developers and users quickly identify and resolve common issues with the AI Chat System.