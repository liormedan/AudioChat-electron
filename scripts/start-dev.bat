@echo off
chcp 65001 >nul
title Audio Chat Studio - Development Mode

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    מצב פיתוח (Development Mode)
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

REM Clean up any existing processes
echo 🧹 מנקה תהליכים קיימים...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo 🚀 מפעיל במצב פיתוח עם Hot Reload...
echo.

REM Start Backend API Server with reload
echo 🔵 מפעיל שרת API עם Hot Reload (פורט 5000)...
start "Audio Chat Studio - API Server (DEV)" cmd /k "title Audio Chat Studio - API Server (DEV) && call .venv\Scripts\activate.bat && python backend\main.py --host 127.0.0.1 --port 5000 --reload --log-level DEBUG"

REM Wait for backend to start
echo ⏳ ממתין לאתחול שרת API...
timeout /t 8 /nobreak >nul

REM Check if backend started successfully
python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=3)" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ שרת API לא הגיב, בודק שוב...
    timeout /t 3 /nobreak >nul
    python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=3)" >nul 2>&1
    if errorlevel 1 (
        echo ❌ שרת API לא מגיב! בדוק את החלון של השרת
        echo ממשיך בכל זאת...
    ) else (
        echo ✅ שרת API פעיל!
    )
) else (
    echo ✅ שרת API פעיל!
)

REM Start Frontend Development Server (if exists)
if exist "frontend\electron-app\package.json" (
    echo 🌐 בודק אם Node.js זמין...
    node --version >nul 2>&1
    if not errorlevel 1 (
        echo 🎨 מפעיל Vite Development Server...
        cd frontend\electron-app
        
        REM Check if node_modules exists
        if not exist "node_modules" (
            echo 📦 מתקין dependencies של Frontend...
            npm install
            if errorlevel 1 (
                echo ❌ התקנת dependencies נכשלה!
                cd ..\..
                pause
                exit /b 1
            )
        )
        
        REM Start Vite dev server
        start "Audio Chat Studio - Vite Dev Server" cmd /k "title Audio Chat Studio - Vite Dev Server && npm run dev:vite"
        
        REM Wait for Vite to start
        timeout /t 5 /nobreak >nul
        
        REM Start Electron in development mode
        echo 🖥️ מפעיל Electron Development Mode...
        start "Audio Chat Studio - Electron Dev" cmd /k "title Audio Chat Studio - Electron Dev && npm run dev:electron"
        
        cd ..\..
        timeout /t 3 /nobreak >nul
    ) else (
        echo ⚠️ Node.js לא נמצא, מדלג על Frontend
        echo 💡 להתקנת Node.js: https://nodejs.org/
    )
) else (
    echo ⚠️ Frontend לא נמצא, מדלג...
)

echo.
echo 🌐 פותח כלי פיתוח...
timeout /t 2 /nobreak >nul

REM Open development interfaces
start http://127.0.0.1:5000/docs
if exist "frontend\electron-app\package.json" (
    start http://127.0.0.1:5174
)

echo.
echo ✅ מצב פיתוח הופעל בהצלחה!
echo.
echo 🛠️ כלי פיתוח זמינים:
echo    • API Server (Hot Reload):  http://127.0.0.1:5000
echo    • Swagger UI:               http://127.0.0.1:5000/docs
if exist "frontend\electron-app\package.json" (
    echo    • Vite Dev Server:          http://127.0.0.1:5174
    echo    • Electron App:             יפתח אוטומטית
)
echo.
echo 🔥 Hot Reload פעיל - שינויים בקוד יתעדכנו אוטומטית!
echo.
echo 📝 טיפים לפיתוח:
echo    • שינויים בקוד Python יפעילו restart אוטומטי
echo    • שינויים בקוד React יתעדכנו מיידית
echo    • לוגים מפורטים זמינים בחלונות השרת
echo.
echo 🛑 לעצירת המערכת: הרץ scripts\stop.bat
echo.
pause