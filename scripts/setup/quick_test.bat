@echo off
chcp 65001 >nul
title Audio Chat Studio - Simple Test

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    בדיקה פשוטה של המערכת
echo ========================================
echo.

REM Activate virtual environment
if exist ".venv" (
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment לא נמצא!
    echo הרץ: scripts\setup\install_dependencies.bat
    pause
    exit /b 1
)

echo 🔵 מפעיל שרת API פשוט (פורט 5000)...
start "Simple API Server" cmd /k "call .venv\Scripts\activate.bat && cd backend\api && python simple_main.py"

timeout /t 3 /nobreak >nul

echo 🟢 מפעיל ממשק ניהול פשוט (פורט 5001)...
start "Simple Admin Interface" cmd /k "call .venv\Scripts\activate.bat && cd backend\admin && python simple_main.py"

timeout /t 5 /nobreak >nul

echo 🌐 פותח דפדפנים...
start http://127.0.0.1:5000/docs
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5001

echo.
echo ✅ המערכת הפשוטה הופעלה!
echo.
echo 📱 ממשקים זמינים:
echo    • API פשוט:      http://127.0.0.1:5000
echo    • Swagger UI:    http://127.0.0.1:5000/docs
echo    • ממשק ניהול:    http://127.0.0.1:5001
echo.
echo 🎯 זוהי גרסה פשוטה ללא תלויות מורכבות
echo    לגרסה המלאה, תקן את בעיות ה-imports
echo.
pause