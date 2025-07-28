@echo off
chcp 65001 >nul
title Audio Chat Studio - ממשק ניהול בלבד

echo.
echo ========================================
echo    🟢 Audio Chat Studio Admin 🟢
echo    הפעלת ממשק ניהול בלבד
echo ========================================
echo.

REM Activate virtual environment
if exist ".venv" (
    echo 🔄 מפעיל virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment לא נמצא!
    echo יוצר virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment נוצר ומופעל
)

echo.
echo 🚀 מפעיל ממשק ניהול...

REM Create logs directory
if not exist "logs" mkdir logs

REM Start Admin server
echo 🟢 ממשק ניהול פועל על פורט 5001...
echo 📋 לוג נשמר ב-logs\admin_server.log
echo.
echo 📱 ממשק זמין:
echo    • ממשק ניהול:    http://127.0.0.1:5001
echo.
echo לעצירה: Ctrl+C
echo.

timeout /t 3 /nobreak >nul
start http://127.0.0.1:5001

python admin_server.py

pause