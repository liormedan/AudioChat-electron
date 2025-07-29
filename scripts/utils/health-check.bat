@echo off
chcp 65001 >nul
title Audio Chat Studio - Health Check

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    בדיקת בריאות המערכת
echo ========================================
echo.

set "all_healthy=true"

REM Check Python installation
echo 🐍 בודק Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא נמצא במערכת
    set "all_healthy=false"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python זמין: גרסה !PYTHON_VERSION!
)

REM Check Virtual Environment
echo 🔧 בודק Virtual Environment...
if exist ".venv" (
    echo ✅ Virtual Environment קיים
    
    REM Try to activate and check packages
    call .venv\Scripts\activate.bat >nul 2>&1
    if errorlevel 1 (
        echo ❌ לא ניתן להפעיל Virtual Environment
        set "all_healthy=false"
    ) else (
        echo ✅ Virtual Environment פעיל
        
        REM Check critical packages
        echo 📦 בודק חבילות קריטיות...
        python -c "import fastapi" >nul 2>&1
        if errorlevel 1 (
            echo ❌ FastAPI לא מותקן
            set "all_healthy=false"
        ) else (
            echo ✅ FastAPI מותקן
        )
        
        python -c "import uvicorn" >nul 2>&1
        if errorlevel 1 (
            echo ❌ Uvicorn לא מותקן
            set "all_healthy=false"
        ) else (
            echo ✅ Uvicorn מותקן
        )
        
        python -c "import librosa" >nul 2>&1
        if errorlevel 1 (
            echo ⚠️ Librosa לא מותקן (אופציונלי)
        ) else (
            echo ✅ Librosa מותקן
        )
    )
) else (
    echo ❌ Virtual Environment לא קיים
    set "all_healthy=false"
)

REM Check Node.js (optional for frontend)
echo 🌐 בודק Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Node.js לא נמצא (נדרש לפרונטאנד)
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo ✅ Node.js זמין: גרסה !NODE_VERSION!
    
    REM Check frontend dependencies
    if exist "frontend\electron-app\node_modules" (
        echo ✅ Frontend dependencies מותקנים
    ) else (
        echo ⚠️ Frontend dependencies לא מותקנים
    )
)

REM Check Backend API
echo 🔍 בודק Backend API...
python -c "from backend.api.main import create_app; print('Backend importable')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend לא ניתן לייבוא
    set "all_healthy=false"
) else (
    echo ✅ Backend ניתן לייבוא
)

REM Check if Backend is running
echo 🌐 בודק אם Backend רץ...
python -c "import requests; r=requests.get('http://127.0.0.1:5000/', timeout=3); print('Backend responding')" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Backend לא רץ כרגע (פורט 5000)
) else (
    echo ✅ Backend רץ ומגיב (פורט 5000)
)

REM Check ports availability
echo 🔌 בודק זמינות פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if not errorlevel 1 (
    echo ✅ פורט 5000 בשימוש (Backend)
) else (
    echo ⚠️ פורט 5000 פנוי
)

netstat -an | find "127.0.0.1:5001" >nul
if not errorlevel 1 (
    echo ✅ פורט 5001 בשימוש (Admin)
) else (
    echo ⚠️ פורט 5001 פנוי
)

netstat -an | find "127.0.0.1:5174" >nul
if not errorlevel 1 (
    echo ✅ פורט 5174 בשימוש (Vite Dev)
) else (
    echo ⚠️ פורט 5174 פנוי
)

REM Check directories
echo 📁 בודק תיקיות נדרשות...
if exist "data" (
    echo ✅ תיקיית data קיימת
) else (
    echo ❌ תיקיית data לא קיימת
    set "all_healthy=false"
)

if exist "logs" (
    echo ✅ תיקיית logs קיימת
) else (
    echo ❌ תיקיית logs לא קיימת
    set "all_healthy=false"
)

REM Check running processes
echo 🔄 בודק תהליכים פעילים...
tasklist | find "python.exe" >nul
if not errorlevel 1 (
    echo ✅ תהליכי Python פעילים
) else (
    echo ⚠️ אין תהליכי Python פעילים
)

tasklist | find "node.exe" >nul
if not errorlevel 1 (
    echo ✅ תהליכי Node.js פעילים
) else (
    echo ⚠️ אין תהליכי Node.js פעילים
)

tasklist | find "electron.exe" >nul
if not errorlevel 1 (
    echo ✅ Electron פעיל
) else (
    echo ⚠️ Electron לא פעיל
)

echo.
echo ========================================
if "%all_healthy%"=="true" (
    echo    ✅ המערכת תקינה! ✅
    echo ========================================
    echo.
    echo 🎉 כל הרכיבים הקריטיים פועלים כמו שצריך
) else (
    echo    ⚠️ נמצאו בעיות במערכת ⚠️
    echo ========================================
    echo.
    echo 🔧 פתרונות מומלצים:
    echo    • הרץ scripts\setup.bat לתיקון בעיות התקנה
    echo    • בדוק שכל התלויות מותקנות
    echo    • וודא שהפורטים פנויים
)

echo.
echo 📊 מידע נוסף:
echo    • להפעלת המערכת: scripts\start.bat
echo    • למצב פיתוח: scripts\start-dev.bat
echo    • לעצירת המערכת: scripts\stop.bat
echo.
pause