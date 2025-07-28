# 🎵 Audio Chat Studio - מדריך הפעלה

## 🚀 הפעלה מהירה

### אופציה 1: הפעלה אוטומטית (מומלץ)
```bash
# Windows
start_all.bat

# או דרך npm
cd electron-app
npm start
```

### אופציה 2: הפעלה ידנית
```bash
# 1. הפעלת שרת API (פורט 5000)
python fastapi_server.py

# 2. הפעלת ממשק ניהול (פורט 5001) - בטרמינל נפרד
python admin_server.py

# 3. הפעלת האפליקציה - בטרמינל נפרד
cd electron-app
npm run dev
```

## 📍 נקודות גישה

| שירות | כתובת | תיאור |
|--------|--------|--------|
| **API עיקרי** | http://127.0.0.1:5000 | שרת עיבוד האודיו |
| **תיעוד API** | http://127.0.0.1:5000/docs | Swagger UI |
| **ממשק ניהול** | http://127.0.0.1:5001 | מוניטורינג ובקרה |
| **אפליקציה** | אוטומטי | חלון Electron |

## 🛑 עצירת השירותים

### אופציה 1: עצירה אוטומטית
```bash
stop_all.bat
```

### אופציה 2: עצירה ידנית
- סגור את חלונות הטרמינל
- או לחץ `Ctrl+C` בכל טרמינל

## 🧪 בדיקת תקינות

### בדיקת API
```bash
curl http://127.0.0.1:5000/health
```

### בדיקת ממשק ניהול
```bash
curl http://127.0.0.1:5001/health
```

## 📊 תכונות ממשק הניהול

- **מוניטורינג בזמן אמת**: CPU, זיכרון, דיסק
- **ניהול קבצים**: צפייה, מחיקה, סטטיסטיקות
- **לוגים**: מעקב אחר פעילות השרת
- **בדיקות**: בדיקת תקינות API
- **גרפים**: ביצועי מערכת בזמן אמת

## 🔧 פתרון בעיות

### שגיאת "Port already in use"
```bash
# בדיקת תהליכים על הפורט
netstat -ano | findstr :5000
netstat -ano | findstr :5001

# עצירת תהליך ספציפי
taskkill /PID [PID_NUMBER] /F
```

### שגיאות Python
```bash
# וידוא התקנת חבילות
pip install -r requirements.txt

# בדיקת גרסת Python
python --version
```

### שגיאות Node.js
```bash
# התקנת dependencies
cd electron-app
npm install

# ניקוי cache
npm run clean
```

## 📝 הערות פיתוח

- השרתים מתחילים במצב `reload=True` לפיתוח
- הלוגים מוצגים בטרמינל ובממשק הניהול
- קבצי אודיו נשמרים בתיקיית `uploads/`
- קבצים זמניים נשמרים בתיקיית `temp/`

## 🎯 שלבים הבאים

1. **העלה קובץ אודיו** דרך האפליקציה
2. **עבור לדף Testing** ובחר "Interactive Editor"
3. **נסה פעולות עריכה** מהירות
4. **עקב אחר הביצועים** בממשק הניהול

---

**נוצר עבור Audio Chat Studio v1.0.0**