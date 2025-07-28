@echo off
chcp 65001 >nul
title Audio Chat Studio - התקנת תלויות

echo.
echo ========================================
echo    📦 Audio Chat Studio Setup 📦
echo    התקנת כל התלויות הנדרשות
echo ========================================
echo.

echo 🔍 בודק Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא מותקן!
    echo אנא התקן Python 3.8+ מ-https://python.org
    pause
    exit /b 1
) else (
    echo ✅ Python מותקן
)

echo.
echo 🔍 בודק Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js לא מותקן!
    echo אנא התקן Node.js מ-https://nodejs.org
    pause
    exit /b 1
) else (
    echo ✅ Node.js מותקן
)

echo.
echo 🐍 יוצר Python Virtual Environment...
if exist ".venv" (
    echo Virtual environment כבר קיים
) else (
    python -m venv .venv
    echo ✅ Virtual environment נוצר
)

echo.
echo 🔄 מפעיל Virtual Environment...
call .venv\Scripts\activate.bat

echo.
echo 📦 מתקין Python packages...
pip install --upgrade pip
pip install fastapi uvicorn python-multipart psutil jinja2
pip install librosa soundfile pydub mutagen noisereduce
pip install flask flask-cors werkzeug

echo.
echo 📦 מתקין Node.js dependencies...
cd electron-app
if exist "package.json" (
    npm install
    echo ✅ Node.js dependencies הותקנו
) else (
    echo ❌ package.json לא נמצא באפליקציית Electron
)
cd ..

echo.
echo 📁 יוצר תיקיות נדרשות...
if not exist "uploads" mkdir uploads
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "templates" mkdir templates

echo.
echo ✅ כל התלויות הותקנו בהצלחה!
echo.
echo 🚀 כעת תוכל להריץ:
echo    • start_all.bat - להפעלת כל המערכת
echo    • start_api_only.bat - לשרת API בלבד
echo    • start_admin_only.bat - לממשק ניהול בלבד
echo    • start_electron_only.bat - לאפליקציה בלבד
echo.
pause