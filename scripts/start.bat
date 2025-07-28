@echo off
chcp 65001 >nul
title Audio Chat Studio - Quick Start

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    מערכת עריכת אודיו מבוססת AI
echo ========================================
echo.

echo 🚀 מפעיל את המערכת...
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment לא נמצא!
    echo הרץ: scripts\setup\install_dependencies.bat
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo 🔵 מפעיל שרת API ראשי (פורט 5000)...
start "API Server" cmd /k "call .venv\Scripts\activate.bat && python backend\api\main.py"

timeout /t 3 /nobreak >nul

echo 🟢 מפעיל ממשק ניהול (פורט 5001)...
start "Admin Interface" cmd /k "call .venv\Scripts\activate.bat && python backend\admin\main.py"

timeout /t 3 /nobreak >nul

echo 🟡 מפעיל אפליקציית Electron...
start "Electron App" cmd /k "cd electron-app && npm start"

echo.
echo ✅ המערכת הופעלה!
echo.
echo 📱 ממשקים זמינים:
echo    • API ראשי:      http://127.0.0.1:5000
echo    • Swagger UI:    http://127.0.0.1:5000/docs
echo    • ממשק ניהול:    http://127.0.0.1:5001
echo    • אפליקציה:      http://127.0.0.1:3000
echo.

timeout /t 5 /nobreak >nul

echo 🌐 פותח דפדפנים...
start http://127.0.0.1:5001
start http://127.0.0.1:5000/docs

echo.
echo 🎉 המערכת פועלת!
echo.
echo לעצירה: scripts\stop\stop_all.bat
pause