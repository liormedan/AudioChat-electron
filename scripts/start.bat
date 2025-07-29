@echo off
chcp 65001 >nul
title Audio Chat Studio - הפעלה מלאה

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    הפעלה מלאה של המערכת
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

REM Check Python dependencies
echo 🔍 בודק תלויות Python...
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

REM Check if backend can be imported
echo 🔍 בודק תקינות Backend...
python -c "from backend.api.main import create_app; print('Backend ready')" 2>nul
if errorlevel 1 (
    echo ⚠️ Backend יש בעיות, מנסה להתקין תלויות נוספות...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ⚠️ חלק מהתלויות לא הותקנו - המערכת תעבוד במצב מוגבל
    )
)

REM Check Node.js dependencies for frontend
echo 🔍 בודק תלויות Node.js...
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
echo 🚀 מפעיל שירותים...
echo.

REM Start backend server
echo 🔵 מפעיל שרת Backend (FastAPI)...
start "Backend Server" cmd /k "title Backend Server && call .venv\Scripts\activate.bat && python backend\main.py --reload"

REM Wait for backend to start
echo ⏳ ממתין לשרת Backend...
timeout /t 5 /nobreak >nul

REM Check if backend is running
echo 🔍 בודק שהשרת Backend מוכן...
python -c "import requests; r = requests.get('http://127.0.0.1:5000', timeout=3); print('✅ Backend server is responding')" 2>nul
if errorlevel 1 (
    echo ⚠️ שרת Backend עדיין לא מוכן, ממתין עוד...
    timeout /t 5 /nobreak >nul
    python -c "import requests; r = requests.get('http://127.0.0.1:5000', timeout=3); print('✅ Backend server is now ready')" 2>nul
    if errorlevel 1 (
        echo ⚠️ שרת Backend לא מגיב - בדוק את החלון של Backend Server
    )
)

REM Start frontend
echo 🟢 מפעיל Frontend (Electron)...
cd frontend\electron-app
start "Frontend" cmd /k "title Frontend && npm run dev"
cd ..\..

REM Wait for frontend to start
echo ⏳ ממתין ל-Frontend...
timeout /t 8 /nobreak >nul

echo.
echo ✅ המערכת הופעלה בהצלחה!
echo.
echo 📱 ממשקים זמינים:
echo    • API Server:     http://127.0.0.1:5000
echo    • Swagger UI:     http://127.0.0.1:5000/docs
echo    • Frontend App:   Electron Window
echo.
echo 🔧 פקודות שימושיות:
echo    • עצירת המערכת:   scripts\stop.bat
echo    • הפעלת פיתוח:    scripts\start-dev.bat
echo    • התקנה מחדש:     scripts\setup.bat
echo.
echo לחץ כל מקש לסגירת החלון הזה...
pause >nul