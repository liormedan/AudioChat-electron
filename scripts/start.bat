@echo off
chcp 65001 >nul
title Audio Chat Studio - Main Startup

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    הפעלה מלאה של המערכת
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא נמצא במערכת!
    echo אנא התקן Python 3.8 או גרסה חדשה יותר
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment לא נמצא!
    echo.
    echo 🔧 מפעיל התקנה אוטומטית...
    call scripts\setup.bat
    if errorlevel 1 (
        echo ❌ ההתקנה נכשלה!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 מפעיל סביבת Python...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ לא ניתן להפעיל את סביבת Python!
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 🔍 בודק dependencies...
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ חבילות חסרות, מתקין...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ התקנת החבילות נכשלה!
        pause
        exit /b 1
    )
)

REM Check if ports are available
echo 🔍 בודק זמינות פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if not errorlevel 1 (
    echo ⚠️ פורט 5000 תפוס! מנסה לסגור תהליכים קיימים...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

netstat -an | find "127.0.0.1:5001" >nul
if not errorlevel 1 (
    echo ⚠️ פורט 5001 תפוס! מנסה לסגור תהליכים קיימים...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo.
echo 🚀 מפעיל שירותי המערכת...
echo.

REM Start Backend API Server
echo 🔵 מפעיל שרת API ראשי (פורט 5000)...
start "Audio Chat Studio - API Server" cmd /k "title Audio Chat Studio - API Server && call .venv\Scripts\activate.bat && python backend\main.py --host 127.0.0.1 --port 5000"

REM Wait for backend to start
echo ⏳ ממתין לאתחול שרת API...
timeout /t 5 /nobreak >nul

REM Check if backend started successfully
python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=2)" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ שרת API לא הגיב, ממשיך בכל זאת...
) else (
    echo ✅ שרת API פעיל!
)

REM Start Admin Interface (if exists)
if exist "backend\admin\main.py" (
    echo 🟢 מפעיל ממשק ניהול (פורט 5001)...
    start "Audio Chat Studio - Admin Interface" cmd /k "title Audio Chat Studio - Admin Interface && call .venv\Scripts\activate.bat && cd backend\admin && python main.py"
    timeout /t 3 /nobreak >nul
) else (
    echo ⚠️ ממשק ניהול לא נמצא, מדלג...
)

REM Start Frontend (if exists)
if exist "frontend\electron-app\package.json" (
    echo 🌐 בודק אם Node.js זמין...
    node --version >nul 2>&1
    if not errorlevel 1 (
        echo 🎨 מפעיל Electron Frontend...
        cd frontend\electron-app
        start "Audio Chat Studio - Frontend" cmd /k "title Audio Chat Studio - Frontend && npm run dev"
        cd ..\..
        timeout /t 3 /nobreak >nul
    ) else (
        echo ⚠️ Node.js לא נמצא, מדלג על Frontend
    )
) else (
    echo ⚠️ Frontend לא נמצא, מדלג...
)

echo.
echo 🌐 פותח דפדפנים...
timeout /t 2 /nobreak >nul

REM Open browser interfaces
start http://127.0.0.1:5000/docs
if exist "backend\admin\main.py" (
    start http://127.0.0.1:5001
)

echo.
echo ✅ המערכת הופעלה בהצלחה!
echo.
echo 📱 ממשקים זמינים:
echo    • API Server:     http://127.0.0.1:5000
echo    • Swagger UI:     http://127.0.0.1:5000/docs
if exist "backend\admin\main.py" (
    echo    • ממשק ניהול:     http://127.0.0.1:5001
)
if exist "frontend\electron-app\package.json" (
    echo    • Electron App:   יפתח אוטומטית
)
echo.
echo 🛑 לעצירת המערכת: הרץ scripts\stop.bat
echo 📊 לבדיקת מצב: הרץ scripts\utils\health-check.bat
echo.
pause