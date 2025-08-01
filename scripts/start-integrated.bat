@echo off
chcp 65001 >nul
title Audio Chat Studio - Integrated Startup

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    הפעלה משולבת עם טרמינל מובנה
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

REM Change to project root directory
cd /d "%~dp0.."

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

REM Check if required packages are installed
echo 🔍 בודק dependencies...
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ חבילות חסרות, מתקין...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ התקנת החבילות נכשלה!
        pause
        exit /b 1
    )
)

REM Check if Node.js is available for frontend
echo 🔍 בודק זמינות Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js לא נמצא!
    echo אנא התקן Node.js מ: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if frontend dependencies are installed
if exist "frontend\electron-app\package.json" (
    cd frontend\electron-app
    if not exist "node_modules" (
        echo 📦 מתקין Frontend dependencies...
        npm install
        if errorlevel 1 (
            echo ❌ התקנת Frontend dependencies נכשלה!
            pause
            exit /b 1
        )
    )
    
    echo.
    echo 🚀 מפעיל Audio Chat Studio עם טרמינל מובנה...
    echo.
    echo 📱 האפליקציה תפתח עם טרמינל מובנה שמציג:
    echo    • לוגים של Backend Server
    echo    • לוגים של Frontend Dev Server  
    echo    • סטטוס כל השירותים
    echo    • פקדי שליטה על השירותים
    echo.
    
    REM Start the integrated Electron app
    npm run dev:integrated
    
    cd ..\..
) else (
    echo ❌ Frontend לא נמצא!
    pause
    exit /b 1
)

echo.
echo ✅ Audio Chat Studio הופעל בהצלחה!
echo 🛑 לעצירת המערכת: סגור את האפליקציה או הרץ scripts\stop.bat
echo.