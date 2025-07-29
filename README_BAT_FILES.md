# 🎵 Audio Chat Studio - קבצי הפעלה

מדריך לשימוש בקבצי ה-BAT להפעלה מהירה של המערכת.

## 📁 קבצי הפעלה זמינים

### 🚀 הפעלה ראשונית
```bash
install_dependencies.bat    # התקנת כל התלויות הנדרשות
quick_test.bat              # בדיקה מהירה של המערכת
```

### 🎯 הפעלת המערכת
```bash
start_all.bat              # הפעלת כל השרתים והאפליקציה
start_api_only.bat         # שרת API בלבד (פורט 5000)
start_admin_only.bat       # ממשק ניהול בלבד (פורט 5001)
start_electron_only.bat    # אפליקציית Electron בלבד (פורט 3000)
```

### 🛠️ ניהול ומעקב
```bash
check_status.bat           # בדיקת סטטוס כל השרתים
stop_all.bat              # עצירת כל השרתים
```

---

## 🎯 הפעלה מהירה - צעד אחר צעד

> **שים לב**: קבצי ה-`BAT` מיועדים להרצה מ-`cmd.exe`. בהרצה דרך PowerShell ייתכן שהפקודות לא יעבדו כמצופה.

### שלב 1: התקנה ראשונית
```bash
# הרץ פעם אחת בלבד
install_dependencies.bat
```

### שלב 2: בדיקה
```bash
# וודא שהכל תקין
quick_test.bat
```

### שלב 3: הפעלה
```bash
# הפעל את כל המערכת
start_all.bat
```

---

## 📱 ממשקים זמינים

לאחר הפעלת `start_all.bat`:

| שירות | כתובת | תיאור |
|--------|--------|--------|
| **API ראשי** | http://127.0.0.1:5000 | שרת עיבוד האודיו |
| **Swagger UI** | http://127.0.0.1:5000/docs | תיעוד API אינטראקטיבי |
| **ממשק ניהול** | http://127.0.0.1:5001 | מוניטורינג ובקרה |
| **אפליקציה** | http://127.0.0.1:3000 | ממשק המשתמש |

---

## 🔧 פתרון בעיות נפוצות

### ❌ "Python לא מותקן"
```bash
# התקן Python 3.8+ מ:
https://python.org
```

### ❌ "Node.js לא מותקן"
```bash
# התקן Node.js מ:
https://nodejs.org
```

### ❌ "Virtual environment לא נמצא"
```bash
# הרץ:
install_dependencies.bat
```

### ❌ "פורט תפוס"
```bash
# עצור את כל השרתים:
stop_all.bat

# ואז הפעל מחדש:
start_all.bat
```

### ❌ "Node modules לא נמצאו"
```bash
cd electron-app
npm install
cd ..
```

---

## 📋 לוגים ומעקב

### מיקום לוגים
```
logs/
├── api_server.log      # לוגי שרת API
├── admin_server.log    # לוגי ממשק ניהול
└── electron_app.log    # לוגי אפליקציה
```

### צפייה בלוגים בזמן אמת
```bash
# Windows PowerShell
Get-Content logs\api_server.log -Wait

# או בממשק הניהול:
http://127.0.0.1:5001
```

---

## 🎯 תרחישי שימוש נפוצים

### פיתוח - API בלבד
```bash
start_api_only.bat
# פותח: http://127.0.0.1:5000/docs
```

### ניהול מערכת
```bash
start_admin_only.bat
# פותח: http://127.0.0.1:5001
```

### בדיקת אפליקציה
```bash
start_electron_only.bat
# פותח: http://127.0.0.1:3000
```

### הפעלה מלאה לדמו
```bash
start_all.bat
# פותח את כל הממשקים אוטומטית
```

---

## 🛡️ אבטחה והגדרות

### פורטים בשימוש
- **5000**: API ראשי (FastAPI)
- **5001**: ממשק ניהול (Admin)
- **3000**: אפליקציית Electron

### תיקיות חשובות
```
uploads/        # קבצי אודיו שהועלו
temp/          # קבצים זמניים
logs/          # לוגי המערכת
.venv/         # Python virtual environment
templates/     # תבניות HTML
```

---

## 🚀 טיפים לביצועים

### הפעלה מהירה
1. השתמש ב-`start_api_only.bat` לפיתוח
2. השתמש ב-`check_status.bat` לבדיקות מהירות
3. השתמש ב-`stop_all.bat` לפני סגירת המחשב

### ניטור ביצועים
1. פתח את ממשק הניהול: http://127.0.0.1:5001
2. עקב אחר שימוש CPU וזיכרון
3. בדוק לוגים בזמן אמת

---

## 📞 תמיכה

אם נתקלת בבעיות:

1. **הרץ בדיקה**: `quick_test.bat`
2. **בדוק סטטוס**: `check_status.bat`
3. **עצור והפעל מחדש**: `stop_all.bat` ואז `start_all.bat`
4. **התקן מחדש**: `install_dependencies.bat`
5. `start.bat` בודק כעת את `%ERRORLEVEL%` כדי לוודא ש-Node.js מותקן

---

**🎉 המערכת מוכנה לשימוש!**