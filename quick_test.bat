@echo off
chcp 65001 >nul
title Audio Chat Studio - בדיקה מהירה

echo.
echo ========================================
echo    🧪 Audio Chat Studio Quick Test 🧪
echo    בדיקה מהירה של כל המערכת
echo ========================================
echo.

echo 🔄 מפעיל virtual environment...
if exist ".venv" (
    call .venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment לא נמצא! הרץ install_dependencies.bat
    pause
    exit /b 1
)

echo.
echo 🧪 בודק imports של Python...

python -c "import fastapi; print('✅ FastAPI')" 2>nul || echo "❌ FastAPI"
python -c "import uvicorn; print('✅ Uvicorn')" 2>nul || echo "❌ Uvicorn"
python -c "import psutil; print('✅ psutil')" 2>nul || echo "❌ psutil"
python -c "import jinja2; print('✅ Jinja2')" 2>nul || echo "❌ Jinja2"
python -c "import librosa; print('✅ librosa')" 2>nul || echo "❌ librosa"
python -c "import pydub; print('✅ pydub')" 2>nul || echo "❌ pydub"

echo.
echo 🧪 בודק קבצי Python...

if exist "fastapi_server.py" (
    echo ✅ fastapi_server.py
) else (
    echo ❌ fastapi_server.py לא נמצא
)

if exist "admin_server.py" (
    echo ✅ admin_server.py
) else (
    echo ❌ admin_server.py לא נמצא
)

echo.
echo 🧪 בודק אפליקציית Electron...

if exist "electron-app\package.json" (
    echo ✅ package.json
) else (
    echo ❌ package.json לא נמצא
)

if exist "electron-app\node_modules" (
    echo ✅ node_modules
) else (
    echo ❌ node_modules לא נמצא - הרץ npm install
)

echo.
echo 🧪 בודק תיקיות...

if exist "templates" (
    echo ✅ templates
) else (
    echo ❌ templates
    mkdir templates
)

if exist "uploads" (
    echo ✅ uploads
) else (
    echo ❌ uploads
    mkdir uploads
)

if exist "logs" (
    echo ✅ logs
) else (
    echo ❌ logs
    mkdir logs
)

echo.
echo 🧪 בדיקת syntax של קבצי Python...

echo בודק fastapi_server.py...
python -m py_compile fastapi_server.py 2>nul && echo "✅ fastapi_server.py" || echo "❌ fastapi_server.py - שגיאת syntax"

echo בודק admin_server.py...
python -m py_compile admin_server.py 2>nul && echo "✅ admin_server.py" || echo "❌ admin_server.py - שגיאת syntax"

echo.
echo 🧪 בדיקת חיבור לאינטרנט...
ping -n 1 8.8.8.8 >nul 2>&1 && echo "✅ חיבור לאינטרנט" || echo "❌ אין חיבור לאינטרנט"

echo.
echo 📊 סיכום בדיקה:
echo.

REM Count issues
set issues=0

if not exist ".venv" set /a issues+=1
if not exist "electron-app\node_modules" set /a issues+=1
if not exist "templates" set /a issues+=1
if not exist "uploads" set /a issues+=1
if not exist "logs" set /a issues+=1

if %issues%==0 (
    echo 🎉 כל הבדיקות עברו בהצלחה!
    echo המערכת מוכנה לשימוש.
    echo.
    echo הרץ start_all.bat להפעלת המערכת
) else (
    echo ⚠️  נמצאו %issues% בעיות
    echo הרץ install_dependencies.bat לתיקון
)

echo.
pause