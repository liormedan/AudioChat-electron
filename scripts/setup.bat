@echo off
chcp 65001 >nul
title Audio Chat Studio - התקנה ראשונית

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    התקנה ראשונית של המערכת
echo ========================================
echo.

REM Check if Python is installed
echo 🔍 בודק התקנת Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא מותקן במערכת!
    echo.
    echo 📥 אנא התקן Python מ: https://www.python.org/downloads/
    echo    ✅ וודא שסימנת "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python מותקן

REM Check if Node.js is installed
echo 🔍 בודק התקנת Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js לא מותקן במערכת!
    echo.
    echo 📥 אנא התקן Node.js מ: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

node --version
npm --version
echo ✅ Node.js ו-npm מותקנים

REM Create virtual environment
echo.
echo 🔧 יוצר סביבת Python וירטואלית...
if exist ".venv" (
    echo ⚠️ סביבה וירטואלית כבר קיימת, מדלג...
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ יצירת סביבה וירטואלית נכשלה!
        pause
        exit /b 1
    )
    echo ✅ סביבה וירטואלית נוצרה
)

REM Activate virtual environment
echo 🔵 מפעיל סביבה וירטואלית...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ הפעלת סביבה וירטואלית נכשלה!
    pause
    exit /b 1
)

REM Upgrade pip
echo 🔄 מעדכן pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo 📦 מתקין תלויות Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ התקנת תלויות Python נכשלה!
    echo.
    echo 🔧 מנסה התקנה חלקית...
    pip install fastapi uvicorn pydantic python-multipart
    if errorlevel 1 (
        echo ❌ התקנה חלקית נכשלה!
        pause
        exit /b 1
    )
    echo ⚠️ התקנה חלקית הושלמה - חלק מהתכונות עלולות לא לעבוד
)

REM Install Node.js dependencies
echo 📦 מתקין תלויות Node.js...
cd frontend\electron-app
npm install
if errorlevel 1 (
    echo ❌ התקנת תלויות Node.js נכשלה!
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

REM Create necessary directories
echo 📁 יוצר תיקיות נדרשות...
if not exist "data\uploads" mkdir data\uploads
if not exist "data\processed" mkdir data\processed
if not exist "data\temp" mkdir data\temp
if not exist "data\cache" mkdir data\cache
if not exist "logs\api" mkdir logs\api
if not exist "logs\system" mkdir logs\system
if not exist "logs\frontend" mkdir logs\frontend

REM Test installation
echo 🧪 בודק התקנה...
python -c "import fastapi; print('✅ FastAPI מותקן')" 2>nul
if errorlevel 1 (
    echo ❌ FastAPI לא מותקן כראוי
) else (
    echo ✅ FastAPI מותקן כראוי
)

python -c "from backend.api.main import create_app; print('✅ Backend מוכן')" 2>nul
if errorlevel 1 (
    echo ⚠️ Backend יש בעיות - חלק מהתכונות עלולות לא לעבוד
) else (
    echo ✅ Backend מוכן לשימוש
)

echo.
echo ✅ ההתקנה הושלמה בהצלחה!
echo.
echo 🚀 להפעלת המערכת הרץ: scripts\start.bat
echo 🔧 לפיתוח הרץ: scripts\start-dev.bat
echo.
pause