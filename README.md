# 🎵 Audio Chat Studio

מערכת מתקדמת לעיבוד אודיו ובינה מלאכותית עם ממשק Electron מודרני.

## 🚀 התקנה מהירה

```bash
# הורד את הפרויקט
git clone <repository-url>
cd Audio-Chat-Studio

# הפעל התקנה אוטומטית
scripts\setup.bat

# הפעל את המערכת
scripts\start.bat
```

> **שים לב**: קבצי ה-`BAT` נבנו עבור `cmd.exe`. ייתכן שתיתקלו בבעיות אם תריצו אותם דרך PowerShell.

## 📋 דרישות מערכת

- **Python 3.8+** - לבקאנד
- **Node.js 16+** - לפרונטאנד (אופציונלי)
- **Windows 10+** - מערכת הפעלה נתמכת

## 🏗️ ארכיטקטורה

```
Audio-Chat-Studio/
├── 🖥️ Backend (FastAPI)
│   ├── backend/main.py          # נקודת כניסה ראשית
│   ├── backend/api/main.py      # FastAPI application
│   └── backend/services/        # שירותי עסק
├── 🌐 Frontend (Electron + React)
│   └── frontend/electron-app/   # אפליקציית Electron
├── 🚀 Scripts
│   ├── scripts/start.bat        # הפעלה רגילה
│   ├── scripts/start-dev.bat    # מצב פיתוח
│   ├── scripts/start-prod.bat   # מצב ייצור
│   └── scripts/setup.bat        # התקנה ראשונית
└── 📊 Data & Logs
    ├── data/                    # קבצי נתונים
    └── logs/                    # קבצי לוג
```

## 🎯 תכונות עיקריות

### 🎵 עיבוד אודיו
- העלאת קבצי אודיו במגוון פורמטים
- חילוץ metadata מתקדם
- ניתוח ספקטרלי וטמפורלי
- עיבוד אודיו בזמן אמת

### 🤖 בינה מלאכותית וצ'אט
- מערכת צ'אט מתקדמת עם AI מקומי (Gemma)
- ניהול סשנים והיסטוריית שיחות
- תמיכה בהזרמת תגובות (streaming)
- שירותי LLM מתקדמים
- עיבוד פקודות בשפה טבעית
- תמיכה במודלים מקומיים וענן
- חיפוש והעברת שיחות
- הגדרות מודל מתקדמות

### 🖥️ ממשק משתמש
- אפליקציית Electron מודרנית
- ממשק React עם TypeScript
- עיצוב רספונסיבי עם Tailwind CSS

## 📖 מדריך שימוש

### הפעלה בסיסית

```bash
# התקנה ראשונית (פעם אחת)
scripts\setup.bat

# הפעלה רגילה
scripts\start.bat

# בדיקת מצב המערכת
scripts\utils\health-check.bat

# עצירת המערכת
scripts\stop.bat
```

### מצבי הפעלה

| מצב | פקודה | תיאור |
|-----|-------|-------|
| **רגיל** | `scripts\start.bat` | הפעלה סטנדרטית |
| **פיתוח** | `scripts\start-dev.bat` | Hot reload + debug logs |
| **ייצור** | `scripts\start-prod.bat` | קבצים בנויים + ביצועים |

### בנייה לייצור

```bash
# בנייה מלאה
scripts\build.bat

# בנייה של Frontend בלבד
cd frontend\electron-app
npm run build

# בנייה של Backend בלבד
python -m PyInstaller backend\main.py
```

## 🔧 פיתוח

### הגדרת סביבת פיתוח

```bash
# התקנת dependencies
scripts\setup.bat

# הפעלה במצב פיתוח
scripts\start-dev.bat

# בדיקת TypeScript
cd frontend\electron-app
npm run type-check

# בדיקת Python
python -c "from backend.api.main import create_app; print('OK')"
```

### מבנה הקוד

#### Backend (Python)
```
backend/
├── main.py                 # נקודת כניסה + הגדרות שרת
├── api/main.py            # FastAPI app + routes
├── services/              # שירותי עסק
│   ├── audio/            # עיבוד אודיו
│   ├── ai/               # בינה מלאכותית
│   └── storage/          # ניהול קבצים
└── models/               # מודלי נתונים
```

#### Frontend (TypeScript + React)
```
frontend/electron-app/src/
├── main/                 # Electron main process
├── renderer/             # React application
│   ├── components/       # רכיבי UI
│   ├── pages/           # דפי האפליקציה
│   ├── services/        # שירותי API
│   └── stores/          # ניהול מצב
└── preload/             # Preload scripts
```

## 🌐 API Documentation

כשהמערכת רצה, הממשקים הבאים זמינים:

- **Swagger UI**: http://127.0.0.1:5000/docs
- **API Endpoints**: http://127.0.0.1:5000/api/
- **Health Check**: http://127.0.0.1:5000/

### עיקרי Endpoints

| Method | Endpoint | תיאור |
|--------|----------|-------|
| `POST` | `/api/audio/upload` | העלאת קובץ אודיו |
| `GET` | `/api/audio/files` | רשימת קבצים |
| `GET` | `/api/audio/metadata/{id}` | metadata של קובץ |
| `POST` | `/api/audio/command/execute` | ביצוע פקודה |

### Chat API Endpoints

| Method | Endpoint | תיאור |
|--------|----------|-------|
| `POST` | `/api/chat/send` | שליחת הודעה לצ'אט |
| `POST` | `/api/chat/stream` | הזרמת תגובות בזמן אמת |
| `GET` | `/api/chat/sessions` | רשימת סשני צ'אט |
| `POST` | `/api/chat/sessions` | יצירת סשן חדש |
| `GET` | `/api/chat/sessions/{id}/messages` | הודעות סשן |
| `GET` | `/api/chat/search` | חיפוש בהודעות |
| `POST` | `/api/chat/export/{id}` | ייצוא שיחה |

למידע מפורט על Chat API ראו `docs/api/chat-api.md`.
המסמך כולל דוגמאות קוד, SDK examples ו-streaming עם Server-Sent Events.

## 🛠️ פתרון בעיות

### בעיות נפוצות

#### "Python לא נמצא"
```bash
# התקן Python מ: https://python.org
# וודא שהוא ב-PATH
python --version
```

#### "Virtual environment לא נמצא"
```bash
# הפעל התקנה מחדש
scripts\setup.bat
```

#### "Backend לא מגיב"
```bash
# בדוק מצב המערכת
scripts\utils\health-check.bat

# הפעל מחדש
scripts\stop.bat
scripts\start.bat
```

#### "Frontend לא נטען"
```bash
# התקן Node.js מ: https://nodejs.org
# התקן dependencies
cd frontend\electron-app
npm install
```

### לוגים ודיבוג

- **Backend logs**: `logs/backend.log`
- **API logs**: `logs/api/`
- **System logs**: `logs/system/`

```bash
# הפעלה עם לוגים מפורטים
scripts\start-dev.bat

# בדיקת לוגים
type logs\backend.log
```

## 🧪 בדיקות

### בדיקות בסיסיות
```bash
# בדיקת בריאות כללית
scripts\utils\health-check.bat

# בדיקת Backend
python -c "from backend.api.main import create_app; print('OK')"

# בדיקת Frontend
cd frontend\electron-app
npm run test:backend
npm run type-check
```

### בדיקות מתקדמות
```bash
# בדיקת אינטגרציה מלאה
scripts\final-integration-test.bat

# בדיקות ביצועים
python tests\performance\run_performance_tests.py

# בדיקות E2E
cd frontend\electron-app
npm run test:e2e

# בדיקות נגישות
npm run test:accessibility
```

### בדיקות צ'אט ספציפיות
```bash
# בדיקת Chat API
curl -X POST http://127.0.0.1:5000/api/chat/sessions -H "Content-Type: application/json" -d "{\"title\":\"Test\"}"

# בדיקת Streaming
curl -N http://127.0.0.1:5000/api/chat/stream -H "Content-Type: application/json" -d "{\"session_id\":\"test\",\"message\":\"Hello\"}"

# בדיקת בסיס נתונים
python -c "from backend.services.database.connection import get_db_connection; print('DB OK' if get_db_connection() else 'DB Failed')"
```

## 📦 פריסה

### בנייה לייצור
```bash
# בנייה מלאה עם executable
scripts\build.bat

# הקבצים יהיו ב:
# - py_build/dist/audio-chat-studio-backend.exe
# - frontend/electron-app/dist/
# - frontend/electron-app/release/ (אם נבחר)
```

### הפעלה בייצור
```bash
# הפעלה עם קבצים בנויים
scripts\start-prod.bat

# או ישירות
frontend\electron-app\py_build\dist\audio-chat-studio-backend.exe
```

## 🤝 תרומה

1. Fork את הפרויקט
2. צור branch חדש (`git checkout -b feature/amazing-feature`)
3. Commit השינויים (`git commit -m 'Add amazing feature'`)
4. Push ל-branch (`git push origin feature/amazing-feature`)
5. פתח Pull Request

## 📄 רישיון

פרויקט זה מופץ תחת רישיון MIT. ראה `LICENSE` לפרטים נוספים.

## 🆘 תמיכה

- **Issues**: פתח issue ב-GitHub
- **Documentation**: `docs/` directory
- **Health Check**: `scripts\utils\health-check.bat`

---

**Audio Chat Studio** - מערכת מתקדמת לעיבוד אודיו ובינה מלאכותית 🎵🤖