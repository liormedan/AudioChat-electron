@echo off
chcp 65001 >nul
title Audio Chat Studio - מצב פיתוח

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    מצב פיתוח (Development Mode)
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment לא נמצא!
    echo 🔧 מריץ התקנה ראשונית...
    call scripts\setup.bat
    if errorlevel 1 (
        echo ❌ ההתקנה נכשלה!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔵 מפעיל סביבת Python...
call .venv\Scripts\activate.bat

REM Quick dependency check
echo 🔍 בדיקה מהירה של תלויות...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo ⚠️ FastAPI לא מותקן, מתקין...
    pip install fastapi uvicorn
)

REM Check Node.js dependencies
if not exist "frontend\electron-app\node_modules" (
    echo ⚠️ מתקין תלויות Node.js...
    cd frontend\electron-app
    npm install
    cd ..\..
)

REM Clean up any existing processes
echo 🧹 מנקה תהליכים קיימים...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
taskkill /f /im electron.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 🚀 מפעיל במצב פיתוח...
echo.

REM Start backend with hot reload
echo 🔵 מפעיל Backend עם Hot Reload...
start "Backend Dev" cmd /k "title Backend Dev Server && call .venv\Scripts\activate.bat && python backend\main.py --reload --log-level DEBUG"

REM Wait for backend
echo ⏳ ממתין לשרת Backend...
timeout /t 3 /nobreak >nul

REM Start frontend with hot reload
echo 🟢 מפעיל Frontend עם Hot Reload...
cd frontend\electron-app
start "Frontend Dev" cmd /k "title Frontend Dev Server && npm run dev"
cd ..\..

REM Wait for frontend
echo ⏳ ממתין ל-Frontend...
timeout /t 5 /nobreak >nul

echo.
echo ✅ מצב פיתוח הופעל!
echo.
echo 🔧 תכונות מצב פיתוח:
echo    • Hot Reload - שינויים בקוד יתעדכנו אוטומטית
echo    • Debug Logging - לוגים מפורטים
echo    • Development Tools - כלי פיתוח זמינים
echo.
echo 📱 ממשקים זמינים:
echo    • API Server:     http://127.0.0.1:5000
echo    • Swagger UI:     http://127.0.0.1:5000/docs
echo    • Frontend Dev:   http://127.0.0.1:5174
echo    • Electron App:   יפתח אוטומטית
echo.
echo 🔧 פקודות שימושיות:
echo    • עצירת המערכת:   scripts\stop.bat
echo    • מצב ייצור:      scripts\start.bat
echo    • בדיקת מצב:      scripts\utils\health-check.bat
echo.
echo 💡 טיפים לפיתוח:
echo    • שינויים בקוד Python יתעדכנו אוטומטית
echo    • שינויים בקוד React יתעדכנו אוטומטית
echo    • לוגים מפורטים זמינים בחלונות הפקודה
echo    • השתמש ב-Ctrl+C בחלונות הפקודה לעצירה
echo.
echo לחץ כל מקש לסגירת החלון הזה...
pause >nul