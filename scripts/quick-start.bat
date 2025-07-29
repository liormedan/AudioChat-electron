@echo off
chcp 65001 >nul
title Audio Chat Studio - Quick Start

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    הפעלה מהירה
echo ========================================
echo.

REM Activate virtual environment
if not exist ".venv" (
    echo ❌ Virtual environment לא נמצא! הרץ scripts\setup.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo 🚀 מפעיל Backend ו-Frontend יחד...
echo.

REM Start Backend in background
echo 🔵 מפעיל Backend API (פורט 5000)...
start /min "Backend API" cmd /c "call .venv\Scripts\activate.bat && python backend\main.py --port 5000"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start Frontend if Node.js is available
where node >nul 2>&1
if not errorlevel 1 (
    if exist "frontend\electron-app\package.json" (
        echo 🌐 מפעיל Frontend...
        cd frontend\electron-app
        start /min "Frontend Dev" cmd /c "npm run dev"
        cd ..\..
    )
) else (
    echo ⚠️ Node.js לא נמצא, מפעיל רק Backend
)

REM Wait for services to start
echo ⏳ ממתין לאתחול השירותים...
timeout /t 8 /nobreak >nul

REM Open browser
echo 🌐 פותח דפדפן...
start http://127.0.0.1:5000/docs

echo.
echo ✅ המערכת הופעלה!
echo.
echo 📱 ממשקים זמינים:
echo    • API Server:    http://127.0.0.1:5000
echo    • Swagger UI:    http://127.0.0.1:5000/docs
echo    • Frontend:      http://127.0.0.1:5174 (אם זמין)
echo.
echo 🛑 לעצירה: הרץ scripts\stop.bat
echo.
pause