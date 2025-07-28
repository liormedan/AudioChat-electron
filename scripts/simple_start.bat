@echo off
chcp 65001 >nul
title Audio Chat Studio - Simple Start

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    הפעלה פשוטה
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

echo 🔵 מפעיל שרת API ראשי...
start "API Server" cmd /k "call .venv\Scripts\activate.bat && cd backend\api && python main.py"

timeout /t 3 /nobreak >nul

echo 🟢 מפעיל ממשק ניהול...
start "Admin Interface" cmd /k "call .venv\Scripts\activate.bat && cd backend\admin && python main.py"

timeout /t 5 /nobreak >nul

echo 🌐 פותח דפדפנים...
start http://127.0.0.1:5000/docs
start http://127.0.0.1:5001

echo.
echo ✅ המערכת הופעלה!
echo.
echo 📱 ממשקים זמינים:
echo    • Swagger UI:    http://127.0.0.1:5000/docs
echo    • ממשק ניהול:    http://127.0.0.1:5001
echo.
pause