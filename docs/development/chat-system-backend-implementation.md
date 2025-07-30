# מסמך פיתוח - תשתית Backend למערכת שיחות AI

## סקירה כללית

מסמך זה מתעד את היישום של תשתית Backend למערכת שיחות AI ב-Audio Chat Studio. התשתית כוללת מודלי נתונים, שירותי ניהול, וטבלאות מסד נתונים לשמירת היסטוריית שיחות.

## מה יושם

### 1. מודלי נתונים חדשים 📊

**קובץ:** `backend/models/chat.py`

#### מודלים שנוצרו:
- **`ChatSession`** - מודל לניהול sessions של שיחות
- **`Message`** - מודל להודעות בודדות
- **`ChatResponse`** - מודל לתשובות מהמודל
- **`MessageRole`** - Enum לתפקידי הודעות (user, assistant, system)
- **`SessionStatus`** - Enum לסטטוס sessions (active, archived, deleted)

#### תכונות עיקריות:
- תמיכה בהמרה ל/מ-dictionary
- תמיכה בהמרה מ-database rows
- Metadata גמיש לכל מודל
- Type safety עם enums

### 2. טבלאות מסד נתונים 🗄️

**קובץ:** `backend/services/ai/llm_service.py` (עודכן)
**Migration:** `backend/migrations/add_chat_tables.py`

#### טבלאות שנוצרו:
```sql
-- טבלת sessions
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
);

-- טבלת הודעות
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
);
```

#### אינדקסים לביצועים:
- `idx_chat_sessions_user_id`
- `idx_chat_sessions_updated_at`
- `idx_chat_messages_session_id`
- `idx_chat_messages_timestamp`

### 3. שירותי ניהול 🔧

#### Chat Service
**קובץ:** `backend/services/ai/chat_service.py`

**פונקציונליות:**
- `send_message()` - שליחת הודעה וקבלת תשובה
- `stream_message()` - שליחת הודעה עם streaming response
- `get_conversation_context()` - קבלת הקשר השיחה
- אינטגרציה עם LLM Service הקיים

#### Session Service
**קובץ:** `backend/services/ai/session_service.py`

**פונקציונליות:**
- `create_session()` - יצירת session חדש
- `get_session()` - קבלת session לפי ID
- `list_user_sessions()` - רשימת sessions של משתמש
- `update_session()` - עדכון session
- `delete_session()` - מחיקת session
- `archive_session()` / `unarchive_session()` - ארכיון sessions
- `search_sessions()` - חיפוש sessions
- `get_session_stats()` - סטטיסטיקות session
- `cleanup_old_sessions()` - ניקוי sessions ישנים

#### Chat History Service
**קובץ:** `backend/services/ai/chat_history_service.py`

**פונקציונליות:**
- `save_message()` - שמירת הודעה
- `get_session_messages()` - קבלת הודעות session
- `search_messages()` - חיפוש בהודעות
- `export_session()` - ייצוא session (JSON, Markdown, Text)
- `delete_message()` - מחיקת הודעה
- `update_message()` - עדכון הודעה
- `get_session_statistics()` - סטטיסטיקות מפורטות

### 4. בדיקות יחידה 🧪

#### בדיקות שנוצרו:
- `tests/unit/test_chat_models.py` - בדיקות למודלי הנתונים
- `tests/unit/test_chat_service.py` - בדיקות ל-Chat Service
- `tests/unit/test_session_service.py` - בדיקות ל-Session Service
- `tests/unit/test_chat_history_service.py` - בדיקות ל-Chat History Service

#### כיסוי בדיקות:
- ✅ יצירה ועדכון של מודלים
- ✅ המרות to_dict/from_dict
- ✅ פונקציונליות CRUD מלאה
- ✅ טיפול בשגיאות
- ✅ Edge cases
- ✅ Streaming functionality
- ✅ Export/Import capabilities

## אינטגרציה עם המערכת הקיימת

### עדכונים ב-Services Registry
**קובץ:** `backend/services/__init__.py`

```python
# הוספת imports חדשים
from .utils.chat_service import ChatService, ChatMessage, ChatSession

# הוספת ל-__all__
__all__ = [
    'ChatService',
    'ChatMessage', 
    'ChatSession',
    # ... existing services
]
```

### חיבור ל-LLM Service
השירותים החדשים משתמשים ב-LLM Service הקיים:
- שימוש באותו מסד נתונים
- אינטגרציה עם מנהל מפתחות API
- תמיכה במודלים מקומיים ו-cloud

## תכונות מתקדמות

### 1. Streaming Support
```python
async def stream_message(self, session_id: str, message: str) -> AsyncGenerator[str, None]:
    # תמיכה ב-streaming responses
    async for chunk in self.llm_service.stream_chat_response(context):
        yield chunk
```

### 2. Export Formats
```python
# תמיכה בפורמטים שונים
json_export = history_service.export_session(session_id, format="json")
markdown_export = history_service.export_session(session_id, format="markdown")
text_export = history_service.export_session(session_id, format="txt")
```

### 3. Advanced Search
```python
# חיפוש מתקדם בהודעות
results = history_service.search_messages(
    query="Python programming",
    user_id="user123",
    session_id="session456"
)
```

### 4. Session Management
```python
# ניהול מתקדם של sessions
stats = session_service.get_session_stats(session_id)
archived_count = session_service.cleanup_old_sessions(days_old=30, dry_run=False)
```

## ביצועים ואופטימיזציה

### אינדקסים במסד הנתונים
- אינדקס על `user_id` לחיפוש מהיר של sessions
- אינדקס על `updated_at` למיון כרונולוגי
- אינדקס על `session_id` לקישור הודעות
- אינדקס על `timestamp` למיון הודעות

### Connection Management
- שימוש ב-connection pooling (עתידי)
- סגירה נכונה של connections
- טיפול בשגיאות מסד נתונים

### Memory Management
- Lazy loading של הודעות
- Pagination support
- Cleanup של sessions ישנים

## אבטחה

### Input Validation
- בדיקת תקינות של IDs
- Sanitization של תוכן הודעות
- Type checking עם dataclasses

### Data Protection
- Foreign key constraints
- Transaction safety
- Error handling מקיף

## שימוש בתשתית

### יצירת Chat Service
```python
from backend.services.ai.llm_service import LLMService
from backend.services.ai.session_service import SessionService
from backend.services.ai.chat_history_service import ChatHistoryService
from backend.services.ai.chat_service import ChatService

# יצירת שירותים
llm_service = LLMService()
session_service = SessionService()
history_service = ChatHistoryService()
chat_service = ChatService(llm_service, session_service, history_service)

# יצירת session חדש
session = session_service.create_session(title="My Chat", model_id="local-gemma-3-4b-it")

# שליחת הודעה
response = chat_service.send_message(session.id, "Hello, AI!")
print(response.content)
```

### Streaming Chat
```python
async def chat_with_streaming():
    async for chunk in chat_service.stream_message(session.id, "Tell me a story"):
        print(chunk, end='', flush=True)
```

## מה הלאה

התשתית מוכנה לשלב הבא - יצירת API endpoints ו-Frontend components. השירותים מספקים את כל הפונקציונליות הנדרשת למערכת שיחות מתקדמת.

### משימות הבאות:
1. ✅ **הושלם** - תשתית Backend
2. 🔄 **הבא** - API Endpoints
3. 🔄 **הבא** - Frontend Components
4. 🔄 **הבא** - Integration Testing

---

**תאריך עדכון:** $(date)
**מפתח:** AI Assistant
**סטטוס:** הושלם בהצלחה ✅