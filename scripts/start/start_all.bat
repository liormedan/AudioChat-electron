@echo off
chcp 65001 >nul
title Audio Chat Studio - הפעלת כל השרתים

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    הפעלת כל השרתים והאפליקציה
echo ========================================
echo.

echo 📋 בודק תלויות...

REM Check if virtual environment exists
if not exist "..\.venv" (
    echo ❌ Virtual environment לא נמצא!
    echo יוצר virtual environment...
    cd ..
    python -m venv .venv
    cd scripts\start
    echo ✅ Virtual environment נוצר
)

REM Activate virtual environment
echo 🔄 מפעיל virtual environment...
call ..\.venv\Scripts\activate.bat

REM Check if node_modules exists
if not exist "..\frontend\electron-app\node_modules" (
    echo ❌ Node modules לא נמצאו!
    echo מתקין dependencies...
    cd ..\frontend\electron-app
    npm install
    cd ..\..\scripts\start
    echo ✅ Dependencies הותקנו
)

echo.
echo 🚀 מפעיל שרתים...
echo.

REM Create logs directory
if not exist "..\..\logs" mkdir ..\..\logs
if not exist "..\..\logs\api" mkdir ..\..\logs\api
if not exist "..\..\logs\admin" mkdir ..\..\logs\admin
if not exist "..\..\logs\frontend" mkdir ..\..\logs\frontend

REM Start FastAPI server (main API)
echo 🔵 מפעיל שרת API ראשי (פורט 5000)...
start "API Server" cmd /k "cd /d %~dp0..\.. && call .venv\Scripts\activate.bat && python backend\api\main.py > logs\api\server.log 2>&1"

REM Wait a bit for the server to start
timeout /t 3 /nobreak >nul

REM Start Admin server
echo 🟢 מפעיל ממשק ניהול (פורט 5001)...
start "Admin Interface" cmd /k "cd /d %~dp0..\.. && call .venv\Scripts\activate.bat && python backend\admin\main.py > logs\admin\server.log 2>&1"

REM Wait a bit for the admin server to start
timeout /t 3 /nobreak >nul

REM Start Electron app
echo 🟡 מפעיל אפליקציית Electron (פורט 3000)...
start "Electron App" cmd /k "cd /d %~dp0..\..\frontend\electron-app && npm start > ..\..\logs\frontend\app.log 2>&1"

echo.
echo ✅ כל השרתים הופעלו!
echo.
echo 📱 ממשקים זמינים:
echo    • API ראשי:      http://127.0.0.1:5000
echo    • Swagger UI:    http://127.0.0.1:5000/docs
echo    • ממשק ניהול:    http://127.0.0.1:5001
echo    • אפליקציה:      http://127.0.0.1:3000
echo.
echo 📋 לוגים נשמרים בתיקיית logs\
echo.
echo ⏳ ממתין 10 שניות ואז פותח את הממשקים...

timeout /t 10 /nobreak >nul

REM Open browsers
echo 🌐 פותח דפדפנים...
start http://127.0.0.1:5001
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000/docs
timeout /t 2 /nobreak >nul
start http://127.0.0.1:3000

echo.
echo 🎉 המערכת פועלת!
echo.
echo לעצירת כל השרתים, הרץ: ..\stop\stop_all.bat
echo.
pause