@echo off
chcp 65001 >nul
title Audio Chat Studio - Production Mode

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    מצב ייצור (Production Mode)
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

REM Check if production build exists
if not exist "frontend\electron-app\dist" (
    echo ⚠️ Production build לא נמצא!
    echo.
    echo 🔧 בונה את האפליקציה לייצור...
    call scripts\build.bat
    if errorlevel 1 (
        echo ❌ הבנייה נכשלה!
        pause
        exit /b 1
    )
)

REM Clean up any existing processes
echo 🧹 מנקה תהליכים קיימים...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Check if ports are available
echo 🔍 בודק זמינות פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if not errorlevel 1 (
    echo ⚠️ פורט 5000 תפוס! מנסה לסגור תהליכים קיימים...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo.
echo 🚀 מפעיל במצב ייצור...
echo.

REM Start Backend API Server in production mode
echo 🔵 מפעיל שרת API בייצור (פורט 5000)...
start "Audio Chat Studio - API Server (PROD)" cmd /k "title Audio Chat Studio - API Server (PROD) && call .venv\Scripts\activate.bat && python backend\main.py --host 127.0.0.1 --port 5000 --log-level INFO"

REM Wait for backend to start
echo ⏳ ממתין לאתחול שרת API...
timeout /t 8 /nobreak >nul

REM Check if backend started successfully
python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=5)" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ שרת API לא הגיב, בודק שוב...
    timeout /t 5 /nobreak >nul
    python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=5)" >nul 2>&1
    if errorlevel 1 (
        echo ❌ שרת API לא מגיב! בדוק את החלון של השרת
        echo ממשיך בכל זאת...
    ) else (
        echo ✅ שרת API פעיל!
    )
) else (
    echo ✅ שרת API פעיל!
)

REM Start Electron App in production mode (if built)
if exist "frontend\electron-app\dist" (
    echo 🖥️ מפעיל Electron App בייצור...
    cd frontend\electron-app
    
    REM Check if node_modules exists
    if not exist "node_modules" (
        echo 📦 מתקין dependencies של Frontend...
        npm install --production
        if errorlevel 1 (
            echo ❌ התקנת dependencies נכשלה!
            cd ..\..
            pause
            exit /b 1
        )
    )
    
    REM Start Electron with built files
    start "Audio Chat Studio - Electron (PROD)" cmd /k "title Audio Chat Studio - Electron (PROD) && electron ."
    
    cd ..\..
    timeout /t 3 /nobreak >nul
) else (
    echo ⚠️ Electron build לא נמצא, מדלג...
    echo 💡 הרץ scripts\build.bat לבניית האפליקציה
)

REM Start Admin Interface (if exists)
if exist "backend\admin\main.py" (
    echo 🟢 מפעיל ממשק ניהול (פורט 5001)...
    start "Audio Chat Studio - Admin Interface (PROD)" cmd /k "title Audio Chat Studio - Admin Interface (PROD) && call .venv\Scripts\activate.bat && cd backend\admin && python main.py"
    timeout /t 3 /nobreak >nul
) else (
    echo ⚠️ ממשק ניהול לא נמצא, מדלג...
)

echo.
echo 🌐 פותח ממשקי ייצור...
timeout /t 2 /nobreak >nul

REM Open production interfaces
start http://127.0.0.1:5000/docs
if exist "backend\admin\main.py" (
    start http://127.0.0.1:5001
)

echo.
echo ✅ מצב ייצור הופעל בהצלחה!
echo.
echo 🏭 ממשקי ייצור זמינים:
echo    • API Server:         http://127.0.0.1:5000
echo    • Swagger UI:         http://127.0.0.1:5000/docs
if exist "backend\admin\main.py" (
    echo    • ממשק ניהול:         http://127.0.0.1:5001
)
if exist "frontend\electron-app\dist" (
    echo    • Electron App:       יפתח אוטומטית
)
echo.
echo 📊 מאפייני ייצור:
echo    • ללא Hot Reload
echo    • לוגים ברמת INFO
echo    • קבצים סטטיים בנויים
echo    • ביצועים מיטביים
echo.
echo 🛑 לעצירת המערכת: הרץ scripts\stop.bat
echo 📊 לבדיקת מצב: הרץ scripts\utils\health-check.bat
echo.
pause