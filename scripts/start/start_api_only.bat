@echo off
chcp 65001 >nul
title Audio Chat Studio - שרת API בלבד

echo.
echo ========================================
echo    🔵 Audio Chat Studio API 🔵
echo    הפעלת שרת API ראשי בלבד
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
echo 🚀 מפעיל שרת API...

REM Create logs directory
if not exist "logs" mkdir logs

REM Start FastAPI server
echo 🔵 שרת API פועל על פורט 5000...
echo 📋 לוג נשמר ב-logs\api_server.log
echo.
echo 📱 ממשקים זמינים:
echo    • API:           http://127.0.0.1:5000
echo    • Swagger UI:    http://127.0.0.1:5000/docs
echo    • ReDoc:         http://127.0.0.1:5000/redoc
echo.
echo לעצירה: Ctrl+C
echo.

python fastapi_server.py

pause