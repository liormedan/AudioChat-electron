@echo off
chcp 65001 >nul
title Audio Chat Studio - מצב פיתוח

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    מצב פיתוח (Development Mode)
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment לא נמצא!
    echo.
    echo 🔧 מריץ התקנה אוטומטית...
    call scripts\setup.bat
    if errorlevel 1 (
        echo ❌ ההתקנה נכשלה!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔵 מפעיל סביבת Python...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ שגיאה בהפעלת סביבת Python!
    pause
    exit /b 1
)

REM Check Python dependencies with development packages
echo 🔍 בודק תלויות Python לפיתוח...
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo ⚠️ חסרות תלויות Python בסיסיות, מתקין...
    pip install fastapi uvicorn pydantic python-multipart
    if errorlevel 1 (
        echo ❌ התקנת תלויות בסיסיות נכשלה!
        pause
        exit /b 1
    )
)

REM Install development dependencies if needed
echo 🔍 בודק תלויות פיתוח...
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo ⚠️ מתקין תלויות פיתוח...
    pip install pytest pytest-asyncio httpx
)

REM Check if backend can be imported
echo 🔍 בודק תקינות Backend...
python -c "from backend.api.main import create_app; print('Backend ready for development')" 2>nul
if errorlevel 1 (
    echo ⚠️ Backend יש בעיות, מנסה להתקין תלויות נוספות...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ⚠️ חלק מהתלויות לא הותקנו - המערכת תעבוד במצב מוגבל
    )
)

REM Check Node.js dependencies for frontend development
echo 🔍 בודק תלויות Node.js לפיתוח...
if exist "frontend\electron-app\node_modules" (
    echo ✅ תלויות Node.js קיימות
) else (
    echo ⚠️ מתקין תלויות Node.js...
    cd frontend\electron-app
    npm install
    if errorlevel 1 (
        echo ❌ התקנת תלויות Node.js נכשלה!
        cd ..\..
        pause
        exit /b 1
    )
    cd ..\..
)

REM Check if ports are available
echo 🔍 בודק זמינות פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if not errorlevel 1 (
    echo ⚠️ פורט 5000 תפוס, מנסה לסגור תהליכים קיימים...
    taskkill /f /im python.exe 2>nul
    timeout /t 2 /nobreak >nul
)

netstat -an | find "127.0.0.1:5174" >nul
if not errorlevel 1 (
    echo ⚠️ פורט 5174 תפוס, מנסה לסגור תהליכים קיימים...
    taskkill /f /im node.exe 2>nul
    timeout /t 2 /nobreak >nul
)

echo.
echo 🚀 מפעיל שירותים במצב פיתוח...
echo.

REM Start backend server with development settings
echo 🔵 מפעיל שרת Backend עם Hot Reload...
start "Backend Dev Server" cmd /k "title Backend Dev Server && call .venv\Scripts\activate.bat && python backend\main.py --reload --log-level DEBUG"

REM Wait for backend to start
echo ⏳ ממתין לשרת Backend...
timeout /t 5 /nobreak >nul

REM Check if backend is running
echo 🔍 בודק שהשרת Backend מוכן...
python -c "import requests; r = requests.get('http://127.0.0.1:5000', timeout=3); print('✅ Backend dev server is responding')" 2>nul
if errorlevel 1 (
    echo ⚠️ שרת Backend עדיין לא מוכן, ממתין עוד...
    timeout /t 5 /nobreak >nul
    python -c "import requests; r = requests.get('http://127.0.0.1:5000', timeout=3); print('✅ Backend dev server is now ready')" 2>nul
    if errorlevel 1 (
        echo ⚠️ שרת Backend לא מגיב - בדוק את החלון של Backend Dev Server
    )
)

REM Start frontend in development mode
echo 🟢 מפעיל Frontend במצב פיתוח...
cd frontend\electron-app
start "Frontend Dev" cmd /k "title Frontend Dev && npm run dev"
cd ..\..

REM Wait for frontend to start
echo ⏳ ממתין ל-Frontend...
timeout /t 8 /nobreak >nul

REM Open development tools
echo 🛠️ פותח כלי פיתוח...
timeout /t 3 /nobreak >nul
start http://127.0.0.1:5000/docs

echo.
echo ✅ מצב פיתוח הופעל בהצלחה!
echo.
echo 📱 ממשקים זמינים:
echo    • API Server:     http://127.0.0.1:5000
echo    • Swagger UI:     http://127.0.0.1:5000/docs (נפתח אוטומטית)
echo    • Frontend App:   Electron Window (עם DevTools)
echo.
echo 🛠️ תכונות פיתוח:
echo    • Hot Reload:     מופעל לבקאנד ופרונטאנד
echo    • Debug Logs:     רמת לוג DEBUG
echo    • Auto Restart:   שרת מתחיל מחדש בשינויים
echo.
echo 🔧 פקודות שימושיות:
echo    • עצירת המערכת:   scripts\stop.bat
echo    • הפעלה רגילה:    scripts\start.bat
echo    • בדיקת בריאות:   curl http://127.0.0.1:5000
echo.
echo 💡 טיפים לפיתוח:
echo    • שמור קבצים ב-backend/ לרענון אוטומטי
echo    • שמור קבצים ב-frontend/ לרענון אוטומטי
echo    • בדוק לוגים בחלונות הנפרדים
echo.
echo לחץ כל מקש לסגירת החלון הזה...
pause >nul